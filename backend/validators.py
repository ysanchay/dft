from __future__ import annotations

from pathlib import Path

from .models import ValidationResult

MAX_MB_DEFAULT = 25
ALLOWED_MIME = {
    "application/pdf",
    "application/msword",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "image/jpeg",
    "image/png",
}


def validate_file(filename: str, size_bytes: int, mime_type: str, max_mb: int = MAX_MB_DEFAULT) -> ValidationResult:
    errors: list[str] = []
    size_mb = round(size_bytes / (1024 * 1024), 2)

    if size_mb > max_mb:
        errors.append(f"File exceeds max size of {max_mb} MB")

    if mime_type not in ALLOWED_MIME:
        errors.append("Unsupported mime type")

    if not Path(filename).name == filename:
        errors.append("Invalid filename")

    return ValidationResult(
        filename=filename,
        size_mb=size_mb,
        mime_type=mime_type,
        valid=len(errors) == 0,
        errors=errors,
    )
