from __future__ import annotations

from pathlib import Path

from fastapi import BackgroundTasks, FastAPI, File, HTTPException, UploadFile
from fastapi.responses import FileResponse

from .jobs import job_store
from .models import JobCreateRequest, JobResultResponse, JobStatusResponse, ValidationResult
from .tools import TEMP_DIR, cleanup_files, run_job
from .validators import validate_file

app = FastAPI(title="DFT API", version="0.1.0")


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

    dst = TEMP_DIR / (file.filename or "upload.bin")
    dst.write_bytes(content)
    return {"stored_path": str(dst), "size_mb": validation.size_mb}


@app.post("/api/jobs", response_model=JobStatusResponse)
def create_job(payload: JobCreateRequest, background_tasks: BackgroundTasks) -> JobStatusResponse:
    cleanup_files()
    if not payload.input_files:
        raise HTTPException(status_code=400, detail="input_files must not be empty")

    for input_file in payload.input_files:
        if not Path(input_file).exists():
            raise HTTPException(status_code=400, detail=f"Input file not found: {input_file}")

    job = job_store.create(tool=payload.tool.value, input_files=payload.input_files, options=payload.options)
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
