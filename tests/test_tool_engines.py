from pathlib import Path

from backend import constants
from backend.jobs import Job
from backend.tools import run_job


def _write(path: Path, data: bytes) -> str:
    path.write_bytes(data)
    return str(path)


def test_pdf_compressor_engine(tmp_path: Path) -> None:
    src = _write(tmp_path / "in.pdf", b"a" * 5000)
    job = Job(id="job_c1", tool=constants.PDF_COMPRESSOR, input_files=[src], options={"level": "high"})
    run_job(job)
    assert job.status == "completed"
    assert job.output_file and job.output_file.endswith("compressed.pdf")
    assert "reduction_percent" in job.meta


def test_pdf_merge_engine(tmp_path: Path) -> None:
    a = _write(tmp_path / "a.pdf", b"%PDF /Page /Page")
    b = _write(tmp_path / "b.pdf", b"%PDF /Page")
    job = Job(id="job_m1", tool=constants.PDF_MERGE, input_files=[a, b], options={})
    run_job(job)
    assert job.status == "completed"
    assert job.meta["files_merged"] == 2


def test_all_requested_tools_have_handlers(tmp_path: Path) -> None:
    sample_pdf = _write(tmp_path / "sample.pdf", b"%PDF content /Page")
    sample_doc = _write(tmp_path / "sample.docx", b"word content")
    sample_img = _write(tmp_path / "sample.jpg", b"jpeg-bytes")

    cases = [
        (constants.PDF_COMPRESSOR, [sample_pdf], {"level": "medium"}),
        (constants.PDF_MERGE, [sample_pdf, sample_pdf], {}),
        (constants.IMAGE_TO_PDF, [sample_img, sample_img], {}),
        (constants.WORD_TO_PDF, [sample_doc], {}),
        (constants.PDF_TO_WORD, [sample_pdf], {"include_images": False}),
        (constants.PDF_SPLIT, [sample_pdf], {"range": "1-2"}),
        (constants.PDF_FORM_FILLER, [sample_pdf], {"fields": {"name": "Aman"}}),
    ]

    for index, (tool, files, options) in enumerate(cases, start=1):
        job = Job(id=f"job_{index}", tool=tool, input_files=files, options=options)
        run_job(job)
        assert job.status == "completed"
        assert job.output_file
        assert job.meta["tool"] == tool
