import importlib.util

import pytest

fastapi = pytest.importorskip("fastapi")
from fastapi.testclient import TestClient

from backend.main import app


def test_fastapi_app_module_exists() -> None:
    # Environment-safe check: package availability may vary in sandbox.
    assert importlib.util.find_spec("backend.main") is not None


def test_upload_generates_unique_names() -> None:
    client = TestClient(app)

    first = client.post(
        "/api/files/upload",
        files={"file": ("same-name.pdf", b"file-one", "application/pdf")},
    )
    second = client.post(
        "/api/files/upload",
        files={"file": ("same-name.pdf", b"file-two", "application/pdf")},
    )

    assert first.status_code == 200
    assert second.status_code == 200
    assert first.json()["upload_id"] != second.json()["upload_id"]


def test_job_rejects_non_uploaded_path_reference() -> None:
    client = TestClient(app)

    response = client.post(
        "/api/jobs",
        json={
            "tool": "pdf-compressor",
            "input_files": ["/etc/passwd"],
            "options": {},
        },
    )

    assert response.status_code == 400
    assert "Invalid input file reference" in response.json()["detail"]
