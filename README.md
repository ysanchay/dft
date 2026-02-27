# DFT — Document & File Tools Platform

This repository includes product documentation and a backend code scaffold for all core document tools.

## Implemented Tool Handlers (Backend)

The backend includes code paths for:

- PDF Compressor
- PDF Merge
- PDF Split
- PDF → Word
- Word → PDF
- Image → PDF
- PDF Form Filler

> Current implementations are **MVP placeholders** to prove API flow and tool-specific routing; production-grade PDF/DOC/image engines can be swapped in behind the same interfaces.

## API Scaffold

`backend/main.py` exposes:

- `GET /health`
- `POST /api/files/validate`
- `POST /api/files/upload`
- `POST /api/jobs`
- `GET /api/jobs/{id}`
- `GET /api/jobs/{id}/result`
- `GET /api/downloads/{id}`

## Run locally

```bash
python -m pip install -r requirements.txt
uvicorn backend.main:app --reload
```

Open `http://127.0.0.1:8000/docs` for Swagger UI.

## Test

```bash
python -m pytest -q
```
