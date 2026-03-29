# Mat2Ansys — Frontend

> **MatWeb → Ansys Engineering Data XML bridge** built with Next.js 15 App Router.
> Paste a MatWeb "Printer Friendly" table, get a ready-to-import `.xml` file in seconds.

---

## Overview

Mat2Ansys eliminates the tedious manual data-entry workflow between [matweb.com](https://www.matweb.com/) and Ansys Workbench. The frontend provides a single-page interface where engineers paste raw MatWeb text and immediately download a fully compliant **MatML 3.1 XML** file — no scraping, no sign-in, no waiting.

```
MatWeb "Printer Friendly" text
        ↓  paste
   Mat2Ansys UI
        ↓  POST /api/parse-and-generate
   FastAPI backend (regex extraction + unit conversion)
        ↓  FileResponse
   .xml download → Ansys Engineering Data import
```

---

## Tech Stack

| Layer | Technology |
|---|---|
| Framework | Next.js 15 (App Router, Turbopack) |
| Language | TypeScript 5 |
| Styling | Tailwind CSS v4 |
| Fonts | Sora (display) · Manrope (body) |
| Runtime | Node.js 20+ |
| Deployment | Vercel |

---

## Features

- **Smart Paste** — paste the entire MatWeb page text; the backend extracts only what it needs
- **Multi-unit support** — automatically handles MPa, GPa, ksi, psi, g/cc, kg/m³, lb/in³
- **Defaults transparency** — if a property is missing from the source data, a yellow warning banner lists exactly which values fell back to steel industry standards
- **Instant download** — XML is streamed directly to the browser as a `Blob`, no server-side storage
- **Sticky form** — the action panel stays in view while the step-by-step guide scrolls

---

## Prerequisites

- **Node.js 20+**
- **Mat2Ansys backend** running (see [`/backend`](../backend/README.md))

---

## Environment

Create a `.env.local` file in the `frontend/` directory:

```bash
# Required only if backend runs on a non-default address
NEXT_PUBLIC_API_BASE=http://localhost:8000
```

> If the variable is unset, the app auto-detects `localhost:8000` in development and routes through Vercel rewrites (`/api/*`) in production.

---

## Development

```bash
# Install dependencies
npm install

# Start dev server (Turbopack)
npm run dev
```

Open [http://localhost:3000](http://localhost:3000).

---

## Production Build

```bash
npm run build
npm run start
```

---

## Project Structure

```
frontend/
├── app/
│   ├── layout.tsx       # Root layout — fonts, metadata
│   ├── page.tsx         # Main SPA — form, state, API call, download
│   └── globals.css      # Design tokens + component styles
├── public/
│   ├── logo.jpg
│   ├── guide_search.png
│   └── guide_printer.png
├── next.config.ts
└── package.json
```

---

## API Contract

The frontend calls a single backend endpoint:

```
POST /api/parse-and-generate
Content-Type: application/json

{
  "name": "SAE 8620 H",
  "raw_text": "<full MatWeb Printer Friendly page text>"
}
```

**Response:** `application/xml` file download
**Response headers used by the frontend:**

| Header | Type | Description |
|---|---|---|
| `X-Mat2Ansys-Used-Defaults` | `string` (CSV) | Property names that fell back to steel defaults |
| `X-Mat2Ansys-Defaults-Count` | `string` (int) | Count of defaulted properties |

---

## Deployment (Vercel)

The monorepo is deployed via [`vercel.json`](../vercel.json) at the repo root.
`/api/*` requests are rewritten to the Python backend; everything else is served by Next.js.

No additional configuration is needed beyond setting environment variables in the Vercel dashboard.

---

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feat/your-feature`
3. Commit with a clear message
4. Open a pull request against `master`
