# Product Strategy: Document & File Tools

## Website Structure

Each tool has:
1. **SEO Landing Page**
2. **Processing Page**

```text
/tools
  ├── pdf-compressor
  ├── pdf-merge
  ├── pdf-split
  ├── pdf-to-word
  ├── word-to-pdf
  ├── image-to-pdf
  ├── pdf-form-filler
```

---

## Highest-Traffic Priority Tools

### 1) PDF Compressor (Top Priority)

**Why this tool leads traffic:**
- Government form size restrictions
- Email attachment limits
- Heavy student and office usage

**Core features:**
- Compression levels: Low / Medium / High
- Before/after file-size preview
- One-click compressed PDF download

**SEO variants sharing same engine:**
- `/pdf-compressor-for-ssc`
- `/pdf-compressor-for-passport`
- `/pdf-compressor-under-200kb`

### 2) PDF Merge Tool

- Drag and reorder PDFs
- Merge multiple PDFs (size-limited)
- Download final merged PDF

### 3) PDF Split Tool

- Split by page range
- Extract specific pages

### 4) PDF → Word Converter

- Preserve text structure and paragraph flow
- Optional image exclusion
- High CPC potential

### 5) Word → PDF Converter

- Clean export
- Font normalization
- No watermark

### 6) Image → PDF Converter

- JPG/PNG to PDF
- Bulk images to one PDF

### 7) Online PDF Form Filler (Differentiator)

- Upload PDF
- Fill fields online
- Download filled PDF

---

## Shared System Architecture

### Frontend (Next.js)

- Upload component
- Tool selector/navigation
- Progress bar
- Download CTA

### Backend (FastAPI or Node)

- File validator
- File processor
- Tool-specific engine
- Temporary storage abstraction

### Cleanup Worker

- Automatic deletion after 10–15 minutes

---

## Core Shared Modules

### 1) Upload & Validation

Rules:
- Max upload size (10–25 MB, configurable)
- Allowed formats only
- Optional anti-malware scan

Validation response contract:

```json
{
  "filename": "document.pdf",
  "size_mb": 4.2,
  "mime_type": "application/pdf",
  "valid": true
}
```

### 2) Temporary Storage

- Store in `/tmp` or object storage with TTL
- Cron/worker-based auto-deletion
- No long-term user retention

Trust message for SEO/conversion:
> Files are auto-deleted after 15 minutes.

### 3) Job Queue / Processing Engine

- Async processing pipeline
- Progress updates for frontend polling/SSE
- Improves reliability and UX during spikes

---

## Tool Engines: Functional Specs

### PDF Compressor

Compression techniques:
- Image optimization
- Remove unused objects
- Downscale render resolution

Output response example:

```json
{
  "original_size_kb": 1240,
  "compressed_size_kb": 310,
  "reduction_percent": 75
}
```

UX essentials:
- Before/after sizes
- Download button
- Compress another file flow

### PDF Merge

- Accept multiple PDFs
- Respect frontend sort order
- Sequentially merge pages

### PDF Split

Supports:
- Page ranges (e.g., `1-3`)
- Extract list (e.g., `2,5,7`)

### PDF → Word

- Extract text layer
- Preserve paragraphs
- Basic formatting only

**Safety statement:** avoid claiming perfect formatting.

### Word → PDF

- Normalize fonts
- Flatten layout to stable PDF
- Produce ATS-friendly output

### Image → PDF

- Resize/compress inputs when needed
- Center alignment
- Multi-page PDF assembly

### PDF Form Filler

- Detect fillable fields
- Render web form overlay
- Inject submitted values back into PDF

---

## Optional LLM Add-ons (Not Required)

- Smart file naming from content cues
- Headline extraction and lightweight summary metadata

---

## SEO Strategy

### URL model

One tool = one primary page + focused variants:
- `/pdf-compressor`
- `/pdf-compressor-for-passport`
- `/pdf-merge-online`

### Content blocks per SEO page

- What it does
- When to use
- FAQ (schema-enabled)
- Internal links to sibling tools
