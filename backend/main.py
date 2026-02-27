from __future__ import annotations

from pathlib import Path
from uuid import uuid4

from fastapi import BackgroundTasks, FastAPI, File, HTTPException, UploadFile
from fastapi.responses import FileResponse

from .jobs import job_store
from .models import JobCreateRequest, JobResultResponse, JobStatusResponse, ValidationResult
from .tools import TEMP_DIR, cleanup_files, run_job
from .validators import validate_file

app = FastAPI(title="DFT API", version="0.1.0")


def _is_in_temp_dir(path: Path) -> bool:
    temp_root = TEMP_DIR.resolve()
    resolved = path.resolve(strict=False)
    return resolved == temp_root or temp_root in resolved.parents


def _resolve_uploaded_input(upload_id: str) -> Path:
    candidate = Path(upload_id)
    if candidate.is_absolute() or len(candidate.parts) != 1 or candidate.name != upload_id:
        raise HTTPException(status_code=400, detail=f"Invalid input file reference: {upload_id}")

    resolved = (TEMP_DIR / upload_id).resolve(strict=False)
    if not _is_in_temp_dir(resolved):
        raise HTTPException(status_code=400, detail=f"Input file must be within temp storage: {upload_id}")
    if not resolved.exists() or not resolved.is_file():
        raise HTTPException(status_code=400, detail=f"Input file not found: {upload_id}")
    return resolved


@app.get("/health")
def health() -> dict:
    return {"ok": True}


@app.post("/api/files/validate", response_model=ValidationResult)
async def api_validate(file: UploadFile = File(...)) -> ValidationResult:
    content = await file.read()
    result = validate_file(file.filename or "unknown", len(content), file.content_type or "application/octet-stream")
    return result


@app.post("/api/files/upload")
async def api_upload(file: UploadFile = File(...)) -> dict:
    cleanup_files()
    content = await file.read()
    validation = validate_file(file.filename or "unknown", len(content), file.content_type or "application/octet-stream")
    if not validation.valid:
        raise HTTPException(status_code=400, detail=validation.errors)

    suffix = Path(file.filename or "upload.bin").suffix
    dst = TEMP_DIR / f"{uuid4().hex}{suffix}"
    dst.write_bytes(content)
    return {
        "upload_id": dst.name,
        "stored_path": str(dst),
        "size_mb": validation.size_mb,
        "original_filename": file.filename,
    }


@app.post("/api/jobs", response_model=JobStatusResponse)
def create_job(payload: JobCreateRequest, background_tasks: BackgroundTasks) -> JobStatusResponse:
    cleanup_files()
    if not payload.input_files:
        raise HTTPException(status_code=400, detail="input_files must not be empty")

    safe_inputs: list[str] = []
    for input_file in payload.input_files:
        resolved = _resolve_uploaded_input(input_file)
        safe_inputs.append(str(resolved))

    job = job_store.create(tool=payload.tool.value, input_files=safe_inputs, options=payload.options)
    background_tasks.add_task(run_job, job)
    return JobStatusResponse(id=job.id, status=job.status, progress=job.progress, eta_seconds=job.eta_seconds)


@app.get("/api/jobs/{job_id}", response_model=JobStatusResponse)
def get_job_status(job_id: str) -> JobStatusResponse:
    job = job_store.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return JobStatusResponse(id=job.id, status=job.status, progress=job.progress, eta_seconds=job.eta_seconds)


@app.get("/api/jobs/{job_id}/result", response_model=JobResultResponse)
def get_job_result(job_id: str) -> JobResultResponse:
    job = job_store.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    if job.status != "completed" or not job.output_file:
        raise HTTPException(status_code=409, detail="Job is not completed")

    return JobResultResponse(
        id=job.id,
        status=job.status,
        download_url=f"/api/downloads/{job.id}",
        meta=job.meta,
    )


@app.get("/api/downloads/{job_id}")
def download(job_id: str) -> FileResponse:
    job = job_store.get(job_id)
    if not job or not job.output_file:
        raise HTTPException(status_code=404, detail="Download not found")
    return FileResponse(job.output_file, media_type="application/octet-stream", filename=f"{job_id}-output.bin")
