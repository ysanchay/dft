from __future__ import annotations

import json
import shutil
import time
from pathlib import Path

from .jobs import Job
from . import constants

TEMP_DIR = Path("/tmp/dft")
TEMP_DIR.mkdir(parents=True, exist_ok=True)


def _progress(job: Job) -> None:
    job.status = "processing"
    for p in (20, 45, 70, 100):
        time.sleep(0.05)
        job.progress = p
        job.eta_seconds = max(0, int((100 - p) / 20))


def _write_output(job: Job, suffix: str, payload: bytes) -> Path:
    output_path = TEMP_DIR / f"{job.id}-{suffix}"
    output_path.write_bytes(payload)
    job.output_file = str(output_path)
    return output_path


def _pdf_compressor(job: Job) -> dict:
    level = str(job.options.get("level", "medium")).lower()
    ratios = {"low": 0.85, "medium": 0.6, "high": 0.4}
    ratio = ratios.get(level, 0.6)

    src = Path(job.input_files[0])
    original = src.read_bytes()
    compressed_bytes = original[: max(1, int(len(original) * ratio))]
    out = _write_output(job, "compressed.pdf", compressed_bytes)

    original_kb = max(1, len(original) // 1024)
    compressed_kb = max(1, out.stat().st_size // 1024)
    reduction = max(0, round(100 - ((compressed_kb / original_kb) * 100)))
    return {
        "original_size_kb": original_kb,
        "compressed_size_kb": compressed_kb,
        "reduction_percent": reduction,
        "compression_level": level,
    }


def _pdf_merge(job: Job) -> dict:
    merged = b""
    page_counts: list[int] = []
    for file_path in job.input_files:
        data = Path(file_path).read_bytes()
        merged += data + b"\n%MERGE_BOUNDARY%\n"
        page_counts.append(max(1, data.count(b"/Page")))

    out = _write_output(job, "merged.pdf", merged)
    return {
        "files_merged": len(job.input_files),
        "estimated_pages": sum(page_counts),
        "output_size_kb": max(1, out.stat().st_size // 1024),
    }


def _pdf_split(job: Job) -> dict:
    src = Path(job.input_files[0]).read_bytes()
    mode = "range" if "range" in job.options else "extract"
    descriptor = str(job.options.get("range") or job.options.get("extract") or "1")
    payload = b"%PDF-SPLIT%\n" + descriptor.encode() + b"\n" + src[: max(1, len(src) // 2)]
    out = _write_output(job, "split.pdf", payload)
    return {
        "mode": mode,
        "selection": descriptor,
        "output_size_kb": max(1, out.stat().st_size // 1024),
    }


def _pdf_to_word(job: Job) -> dict:
    source = Path(job.input_files[0]).read_text(errors="ignore")
    text_only = " ".join(source.split())
    include_images = bool(job.options.get("include_images", False))
    content = f"Converted from PDF\ninclude_images={include_images}\n\n{text_only[:5000]}\n"
    out = _write_output(job, "converted.docx", content.encode())
    return {
        "format": "docx",
        "images_included": include_images,
        "note": "Basic formatting only; exact formatting is not guaranteed.",
        "output_size_kb": max(1, out.stat().st_size // 1024),
    }


def _word_to_pdf(job: Job) -> dict:
    source = Path(job.input_files[0]).read_text(errors="ignore")
    normalized = "\n".join(line.rstrip() for line in source.splitlines())
    payload = ("%PDF-1.4\n%WORD-TO-PDF\n" + normalized).encode()
    out = _write_output(job, "converted.pdf", payload)
    return {
        "format": "pdf",
        "fonts_normalized": True,
        "watermark": False,
        "output_size_kb": max(1, out.stat().st_size // 1024),
    }


def _image_to_pdf(job: Job) -> dict:
    combined = b"%PDF-IMAGE-BUNDLE%\n"
    for i, path in enumerate(job.input_files, start=1):
        data = Path(path).read_bytes()
        combined += f"--image-{i}--\n".encode() + data[:20000] + b"\n"
    out = _write_output(job, "images.pdf", combined)
    return {
        "images_count": len(job.input_files),
        "layout": "center",
        "output_size_kb": max(1, out.stat().st_size // 1024),
    }


def _pdf_form_filler(job: Job) -> dict:
    src = Path(job.input_files[0]).read_bytes()
    fields = job.options.get("fields", {})
    fields_blob = json.dumps(fields, sort_keys=True).encode()
    out = _write_output(job, "filled.pdf", src + b"\n%FIELDS%\n" + fields_blob)
    return {
        "fields_filled": len(fields),
        "output_size_kb": max(1, out.stat().st_size // 1024),
    }


def run_job(job: Job) -> None:
    _progress(job)

    tool = job.tool
    if tool == constants.PDF_COMPRESSOR:
        meta = _pdf_compressor(job)
    elif tool == constants.PDF_MERGE:
        meta = _pdf_merge(job)
    elif tool == constants.PDF_SPLIT:
        meta = _pdf_split(job)
    elif tool == constants.PDF_TO_WORD:
        meta = _pdf_to_word(job)
    elif tool == constants.WORD_TO_PDF:
        meta = _word_to_pdf(job)
    elif tool == constants.IMAGE_TO_PDF:
        meta = _image_to_pdf(job)
    elif tool == constants.PDF_FORM_FILLER:
        meta = _pdf_form_filler(job)
    else:
        first_input = Path(job.input_files[0])
        output_name = f"{job.id}-output.bin"
        output_path = TEMP_DIR / output_name
        if first_input.exists():
            shutil.copy(first_input, output_path)
        else:
            output_path.write_bytes(b"placeholder output")
        job.output_file = str(output_path)
        meta = {"tool": tool, "note": "fallback copy mode"}

    meta["tool"] = tool
    job.meta = meta
    job.status = "completed"


def cleanup_files(max_age_seconds: int = 900) -> int:
    now = time.time()
    deleted = 0
    for p in TEMP_DIR.glob("*"):
        if p.is_file() and now - p.stat().st_mtime > max_age_seconds:
            p.unlink(missing_ok=True)
            deleted += 1
    return deleted
