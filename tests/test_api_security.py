import pytest

fastapi = pytest.importorskip("fastapi")

from fastapi.testclient import TestClient

from backend.main import app
from backend.tools import TEMP_DIR


client = TestClient(app)


def test_upload_uses_unique_storage_name() -> None:
    files = {"file": ("same-name.pdf", b"sample payload", "application/pdf")}
    first = client.post("/api/files/upload", files=files)
    second = client.post("/api/files/upload", files=files)

    assert first.status_code == 200
    assert second.status_code == 200

    first_path = first.json()["stored_path"]
    second_path = second.json()["stored_path"]

    assert first_path != second_path
    assert first_path.startswith(str(TEMP_DIR))
    assert second_path.startswith(str(TEMP_DIR))


def test_job_creation_rejects_non_temp_input_files() -> None:
    payload = {
        "tool": "pdf-compressor",
        "input_files": ["/etc/passwd"],
        "options": {},
    }

    response = client.post("/api/jobs", json=payload)

    assert response.status_code == 400
    assert "within temp storage" in response.json()["detail"]
