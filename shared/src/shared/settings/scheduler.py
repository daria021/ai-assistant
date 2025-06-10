from pydantic import Field

from shared.settings import AbstractSettings


class SchedulerSettings(AbstractSettings):
    job_store_sqlite_path: str = Field(default='/app/jobs.sqlite')
