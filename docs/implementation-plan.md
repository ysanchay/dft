# Implementation Plan

## Phase 1 — Foundation (Week 1)

1. Scaffold frontend and backend repos/services.
2. Implement shared upload validation module.
3. Add temporary storage with TTL cleanup worker.
4. Add async job execution model + progress API.

## Phase 2 — Launch High-Intent Tools (Weeks 2–3)

1. PDF Compressor (priority)
2. PDF Merge
3. PDF Split

### Deliverables

- SEO page + processing page for each tool
- Shared UI upload + progress + download flow
- Basic analytics events (upload, success, fail)

## Phase 3 — Conversion Suite (Weeks 4–5)

1. PDF → Word
2. Word → PDF
3. Image → PDF

## Phase 4 — Differentiator (Week 6)

1. Online PDF Form Filler
2. Field detection + renderer + value injection

## Common API Contracts

### Upload Validation

`POST /api/files/validate`

```json
{
  "filename": "x.pdf",
  "size_mb": 4.2,
  "mime_type": "application/pdf",
  "valid": true,
  "errors": []
}
```

### Job Submission

`POST /api/jobs`

```json
{
  "tool": "pdf-compressor",
  "input_files": ["tmp/file-1.pdf"],
  "options": { "level": "medium" }
}
```

### Job Status

`GET /api/jobs/{id}`

```json
{
  "id": "job_123",
  "status": "processing",
  "progress": 65,
  "eta_seconds": 8
}
```

### Job Result

```json
{
  "id": "job_123",
  "status": "completed",
  "download_url": "/api/downloads/job_123/output.pdf",
  "meta": {
    "original_size_kb": 1240,
    "output_size_kb": 310
  }
}
```

## Non-Functional Requirements

- Max upload: configurable by tool (default 25 MB)
- Data retention: 15-minute auto-delete
- Throughput target: 95th percentile completion under 20s for standard PDFs
- Observability: structured logs + tool-level metrics
- Security: MIME/extension checks, filename sanitization, request rate limiting
