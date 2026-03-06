# Mat2Ansys Frontend

Next.js (App Router) frontend for searching MatWeb materials and downloading ANSYS XML files.

## Prerequisites

- Node.js 20+
- Backend API running (default: `http://localhost:8000`)

## Environment

Create a `.env.local` file in `frontend/`:

```bash
NEXT_PUBLIC_API_BASE=http://localhost:8000
```

## Run

```bash
npm install
npm run dev
```

Open `http://localhost:3000`.

## Build

```bash
npm run build
npm run start
```

## Notes

- The UI surfaces backend validation/scraper errors.
- If backend falls back to steel defaults for missing properties, a warning is shown after download.
