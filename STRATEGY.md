# IMPLEMENTATION PLAN: Mat2Ansys Web Scraper & XML Generator

## Overview
This document outlines the step-by-step coding tasks required to build the Mat2Ansys tool. The AI Assistant must complete these phases sequentially. Do not proceed to the next phase until the current phase is fully coded, tested, and approved by the user.

## PHASE 1: Backend Setup & Stealth Scraper Engine (Python)
**Goal:** Set up the FastAPI backend and create a stealthy Playwright bot that can bypass basic ASP.NET anti-bot mechanisms.

**Tasks:**
1.  **Initialize Project:** Create `requirements.txt` containing: `fastapi`, `uvicorn`, `playwright`, `beautifulsoup4`, `pydantic`.
2.  **Create `scraper.py` (The Core Engine):**
    * Initialize `async_playwright`.
    * **CRITICAL STEALTH TACTICS:** Configure the browser context to avoid detection:
        * Set a realistic `User-Agent` string.
        * Pass `args=["--disable-blink-features=AutomationControlled"]` to hide the automation flag.
        * Add random asynchronous delays (`asyncio.sleep`) between typing and clicking actions to mimic human behavior.
3.  **Implement `search_material(query)`:**
    * Navigate to MatWeb search.
    * Input the query into the search box and submit.
    * Wait for the ASP.NET `__VIEWSTATE` to resolve and the results table to load.
    * Extract a list of dictionaries: `[{"name": "Material Name", "url": "MatWeb Detail URL"}]`.
    * Return this list.

## PHASE 2: Detail Extraction & Data Cleaning
**Goal:** Navigate to a specific material URL, extract mechanical properties, and normalize the data for Ansys.

**Tasks:**
1.  **Implement `get_material_details(url)` in `scraper.py`:**
    * Navigate to the provided MatWeb URL.
    * Extract the following target properties using precise DOM selectors (handling table rows):
        * Density
        * Tensile Strength, Yield
        * Tensile Strength, Ultimate
        * Modulus of Elasticity
        * Poisson's Ratio
2.  **Create `utils.py` (Data Cleaner):**
    * Write regex/string manipulation functions to clean the extracted text (e.g., convert "7.85 g/cc" to `7850`, "200 GPa" to `200000000000`).
    * Format the output into a strict JSON object with standard SI units (Pa, kg/m³).

## PHASE 3: Local Caching System
**Goal:** Prevent redundant scraping by saving fetched data locally.

**Tasks:**
1.  **Create `db_handler.py`:**
    * Implement functions to read and write to `bizim_malzemeler.json`.
    * Before triggering `scraper.py` in Phase 2, the system must check if the requested material URL/Name already exists in this JSON file. If yes, return the cached data immediately.

## PHASE 4: Ansys XML Generation
**Goal:** Inject the cleaned data into the Ansys MatML format.

**Tasks:**
1.  **Create `xml_generator.py`:**
    * Use `xml.etree.ElementTree` to parse `template.xml`.
    * Find the relevant `<PropertyData>` and `<ParameterValue>` tags.
    * Update the `<Data>` tags with the variables from Phase 2 (Density, Yield, Ultimate, Elasticity, Poisson).
    * Update the main material `<Name>`.
    * Save the modified tree as a new temporary `.xml` file and return its path.

## PHASE 5: API Endpoints (FastAPI)
**Goal:** Expose the Python logic as a REST API.

**Tasks:**
1.  **Create `main.py`:**
    * Set up FastAPI app with CORS middleware enabled (to allow frontend requests).
    * Endpoint 1: `GET /api/search?q={query}` -> Calls Phase 1 logic.
    * Endpoint 2: `POST /api/generate` -> Takes the MatWeb URL, calls Phase 2, 3, and 4 logic, and returns the customized `.xml` file as a `FileResponse` for download.

## PHASE 6: Frontend (Next.js + 21st.dev UI)
**Goal:** Build the user interface.

**Tasks:**
1.  Initialize a Next.js (App Router) project with Tailwind CSS.
2.  Create a sleek, dark-themed search interface using components inspired by `21st.dev` (input fields, loading spinners, data tables).
3.  Connect the frontend to the FastAPI backend endpoints.
4.  Handle the file download process cleanly when the user clicks "Download Ansys Patch".

**AI INSTRUCTION:** Acknowledge this plan. Start executing **PHASE 1** immediately by generating `requirements.txt` and the initial `scraper.py` setup.