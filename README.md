# Mat2Ansys

**MatWeb → ANSYS Engineering Data XML bridge.**
Paste raw MatWeb material data, download a ready-to-import `.xml` file in seconds — no manual data entry, no sign-in.

[![Deploy with Vercel](https://vercel.com/button)](https://vercel.com/new/clone?repository-url=https://github.com/Alphyn12/Mat2Ansys)
![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)
![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python&logoColor=white)
![Next.js](https://img.shields.io/badge/Next.js-16-black?logo=next.js)

---

## How It Works

```
1. Go to matweb.com → find your material → open "Printer Friendly Version"
2. Select All (Ctrl+A) and copy the entire page text
3. Paste into Mat2Ansys → enter a material name → click "Generate XML"
4. Download the .xml file → import into ANSYS Engineering Data
```

The backend uses regex-based extraction to pull out the relevant properties, converts every unit to SI (Pa, kg/m³), derives Bulk and Shear Modulus from Young's Modulus and Poisson's Ratio, then injects the values into a valid **MatML 3.1** XML template.

---

## Features

- **Smart Paste** — no structured input required; paste the entire page and the backend finds what it needs
- **Multi-unit support** — MPa, GPa, ksi, psi, g/cc, kg/m³, lb/in³, range values (e.g. `0.27 - 0.30` → averaged)
- **Derived properties** — Bulk Modulus and Shear Modulus are automatically calculated from E and ν
- **Steel fallback defaults** — if a property is missing or unparseable, industry-standard steel values are used (E = 200 GPa, ν = 0.3, ρ = 7850 kg/m³)
- **Transparency** — a warning banner lists every property that fell back to a default, so you know exactly what to verify
- **Serverless-ready** — designed for Vercel's read-only filesystem, with atomic writes and stale-lock cleanup
- **Zero friction** — no database, no accounts, no API keys

---

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | Next.js 16 (App Router) · TypeScript 5 · Tailwind CSS 4 |
| Backend | FastAPI · Python 3.10+ · Pydantic |
| XML | Python `xml.etree.ElementTree` · MatML 3.1 template |
| Deployment | Vercel (`@vercel/python` + `@vercel/next`) |

---

## Getting Started

### Prerequisites

- **Python 3.10+**
- **Node.js 20+**

### 1. Clone

```bash
git clone https://github.com/Alphyn12/Mat2Ansys.git
cd Mat2Ansys
```

### 2. Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

### 3. Frontend

```bash
cd frontend
npm install
npm run dev
```

Open [http://localhost:3000](http://localhost:3000).

---

## Environment Variables

### Backend (`backend/.env`)

| Variable | Default | Description |
|---|---|---|
| `ALLOWED_ORIGINS` | `http://localhost:3000,http://127.0.0.1:3000` | CORS allowed origins |
| `SEARCH_CACHE_TTL_SEC` | `86400` | Material cache TTL in seconds |
| `DISABLE_CACHE` | `0` | Set to `1` to skip disk caching entirely |

### Frontend (`frontend/.env.local`)

| Variable | Default | Description |
|---|---|---|
| `NEXT_PUBLIC_API_BASE` | auto-detected | Backend base URL (omit in Vercel production) |

---

## API Reference

### `POST /api/parse-and-generate`

Parses raw MatWeb text and returns an ANSYS-compatible XML file.

**Request body:**

```json
{
  "name": "AISI 4140 Steel",
  "raw_text": "<full MatWeb Printer Friendly page text>"
}
```

**Response:** `application/xml` file download

**Response headers:**

| Header | Type | Description |
|---|---|---|
| `X-Mat2Ansys-Used-Defaults` | `string` (CSV) | Properties that fell back to steel defaults |
| `X-Mat2Ansys-Defaults-Count` | `string` (int) | Number of defaulted properties |
| `X-Mat2Ansys-Missing-Or-Unparsed` | `string` (CSV) | Properties not found in the source text |

### `GET /api/health`

Returns `{"status": "ok", "version": "2.0.0"}`.

---

## Supported Properties

| MatWeb Property | ANSYS Parameter | Unit (SI) |
|---|---|---|
| Density | Density | kg/m³ |
| Tensile Strength, Yield | Yield Strength | Pa |
| Tensile Strength, Ultimate | Ultimate Tensile Strength | Pa |
| Modulus of Elasticity / Tensile Modulus | Young's Modulus | Pa |
| Poisson's Ratio / Poissons Ratio | Poisson's Ratio | — |
| *(derived)* | Bulk Modulus `K = E / 3(1−2ν)` | Pa |
| *(derived)* | Shear Modulus `G = E / 2(1+ν)` | Pa |

---

## Project Structure

```
Mat2Ansys/
├── backend/
│   ├── main.py              # FastAPI app — endpoints, CORS
│   ├── utils.py             # Regex extraction & unit conversion
│   ├── xml_generator.py     # MatML 3.1 XML template injection
│   ├── db_handler.py        # JSON cache with atomic writes & file locking
│   ├── security.py          # Request validation
│   ├── template.xml         # ANSYS Structural Steel baseline (MatML 3.1)
│   ├── requirements.txt
│   └── tests/               # pytest unit tests
│       ├── test_api.py
│       ├── test_utils.py
│       ├── test_xml_generator.py
│       ├── test_db_handler.py
│       └── test_security.py
├── frontend/
│   ├── app/
│   │   ├── layout.tsx       # Root layout — fonts, metadata
│   │   ├── page.tsx         # Main SPA — form, state, API call, download
│   │   └── globals.css      # Design tokens + component styles
│   ├── public/              # Static assets (logo, guide screenshots)
│   ├── package.json
│   └── README.md            # Frontend-specific docs
├── vercel.json              # Vercel monorepo config
└── README.md                # This file
```

---

## Deployment (Vercel)

The repository is a monorepo. `vercel.json` at the root handles everything:

- `/api/*` → Python backend (FastAPI via `@vercel/python`)
- `/*` → Next.js frontend

**Steps:**

1. Fork or clone the repo
2. Import it into [Vercel](https://vercel.com)
3. Set `ALLOWED_ORIGINS` to your Vercel domain (or leave empty to accept same-origin requests only)
4. Deploy — no extra configuration needed

> **Vercel free plan note:** Functions time out after 10 seconds. The cache layer automatically uses a 2-second lock timeout on Vercel so a stale lock file can never exhaust the function's time budget.

---

## Running Tests

```bash
cd backend
pytest
```

---

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feat/your-feature`
3. Commit your changes with a clear message
4. Open a pull request against `master`

---

## License

[MIT](LICENSE)
