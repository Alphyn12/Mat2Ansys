"""
Mat2Ansys - FastAPI Backend
============================
REST API exposing material XML generation.

Endpoints:
    POST /api/parse-and-generate  → Generate ANSYS XML from raw MatWeb text
    GET  /api/health            → Health check
"""

import os
import sys

# Ensure backend/ directory is on sys.path so relative imports work
# both locally and on Vercel (where the working directory is the repo root).
_BACKEND_DIR = os.path.dirname(os.path.abspath(__file__))
if _BACKEND_DIR not in sys.path:
    sys.path.insert(0, _BACKEND_DIR)

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field

from utils import parse_raw_matweb_text
from xml_generator import generate_ansys_xml
from db_handler import get_material, save_material

def _parse_allowed_origins() -> list[str]:
    import os

    raw = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000,http://127.0.0.1:3000")
    return [origin.strip() for origin in raw.split(",") if origin.strip()]


# ---------------------------------------------------------------------------
# App Setup
# ---------------------------------------------------------------------------
app = FastAPI(
    title="Mat2Ansys API",
    description="Bridge between MatWeb material database and ANSYS Workbench via Smart Paste",
    version="2.0.0",
)

# CORS: Allow Next.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=_parse_allowed_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------------------------
# Request/Response Models
# ---------------------------------------------------------------------------
class ParseGenerateRequest(BaseModel):
    name: str = Field(min_length=1, max_length=200, description="Material Name")
    raw_text: str = Field(min_length=1, description="Raw MatWeb Printer Friendly Text")


class HealthResponse(BaseModel):
    status: str
    version: str


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------
@app.get("/api/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    return HealthResponse(status="ok", version="2.0.0")


@app.post("/api/parse-and-generate")
async def parse_and_generate_xml(req: ParseGenerateRequest):
    """
    Generate an ANSYS-compatible MatML 3.1 XML file by parsing raw MatWeb text.
    Returns the XML file as a download.
    """
    material_name = req.name.strip()
    if not material_name:
        raise HTTPException(
            status_code=422,
            detail={"error_code": "INVALID_NAME", "message": "Material name cannot be empty."},
        )

    # 1) Parse raw text and extract properties
    parsed_data = parse_raw_matweb_text(req.raw_text)
    properties = parsed_data["properties"]
    used_defaults = parsed_data["used_defaults"]
    missing_or_unparsed = parsed_data["missing_or_unparsed"]
    
    # Cache the result using db_handler
    save_material(
        name=material_name,
        url="smart_paste",
        properties=properties,
        used_defaults=used_defaults,
        missing_or_unparsed=missing_or_unparsed
    )

    # 2) Generate ANSYS XML
    try:
        xml_path = generate_ansys_xml(material_name, properties)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={"error_code": "XML_GENERATION_FAILED", "message": f"XML generation failed: {e}"},
        )

    # 3) Return as file download
    safe_name = "".join(
        c if c.isalnum() or c in " _-" else "_" for c in material_name
    )
    return FileResponse(
        path=xml_path,
        media_type="application/xml",
        filename=f"{safe_name}.xml",
        headers={
            "Content-Disposition": f'attachment; filename="{safe_name}.xml"',
            "X-Mat2Ansys-Used-Defaults": ",".join(used_defaults),
            "X-Mat2Ansys-Defaults-Count": str(len(used_defaults)),
            "X-Mat2Ansys-Missing-Or-Unparsed": ",".join(missing_or_unparsed),
        },
    )


# ---------------------------------------------------------------------------
# Run with: uvicorn main:app --reload --port 8000
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
