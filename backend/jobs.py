from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field


@dataclass
class Job:
    id: str
    tool: str
    input_files: list[str]
    options: dict
    status: str = "queued"
    progress: int = 0
    eta_seconds: int = 10
    output_file: str | None = None
    meta: dict = field(default_factory=dict)
    created_at: float = field(default_factory=time.time)


class InMemoryJobStore:
    def __init__(self) -> None:
        self.jobs: dict[str, Job] = {}

    def create(self, tool: str, input_files: list[str], options: dict) -> Job:
        job = Job(id=f"job_{uuid.uuid4().hex[:8]}", tool=tool, input_files=input_files, options=options)
        self.jobs[job.id] = job
        return job

    def get(self, job_id: str) -> Job | None:
        return self.jobs.get(job_id)


job_store = InMemoryJobStore()
