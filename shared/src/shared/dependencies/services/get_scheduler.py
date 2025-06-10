from pathlib import Path

from shared.abstractions.services.scheduler import SchedulerInterface
from shared.services.scheduler import Scheduler


def get_scheduler(sqlite_path: str) -> SchedulerInterface:
    return Scheduler(
        job_store_sqlite_path=Path(sqlite_path),
    )
