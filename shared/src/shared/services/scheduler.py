from dataclasses import field, dataclass
from datetime import datetime
from pathlib import Path
from typing import Callable, Coroutine, Any

from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from shared.abstractions.services.scheduler import SchedulerInterface
from shared.abstractions.singleton import Singleton


@dataclass
class Scheduler(
    SchedulerInterface,
    Singleton,
):
    job_store_sqlite_path: Path

    scheduler: AsyncIOScheduler = field(default=None, init=False)

    def __post_init__(self):
        jobstores = {
            'default': SQLAlchemyJobStore(
                url=f"sqlite:///{self.job_store_sqlite_path.absolute()}",
                tablename='apscheduler_jobs',
            )
        }
        executors = {'default': {'type': 'asyncio'}}
        job_defaults = {'coalesce': False, 'max_instances': 1}

        self.scheduler = AsyncIOScheduler(
            jobstores=jobstores,
            executors=executors,
            job_defaults=job_defaults,
            timezone="Europe/Moscow",
        )
        self.scheduler.start()

    def initialize(self) -> None:
        pass

    def schedule_once(
            self,
            callback: Callable[[Any], Coroutine[Any, Any, None]],
            runs_on: datetime,
            args: tuple[Any, ...] = (),
            job_id: str = None,
            misfire_grace_time: int = 60,
    ) -> None:
        self.scheduler.add_job(
            callback,
            next_run_time=runs_on,
            args=args,
            id=job_id,
            replace_existing=True if job_id else False,
            misfire_grace_time=misfire_grace_time,
        )

    def schedule_daily(
            self,
            callback: Callable[[Any], Coroutine[Any, Any, None]],
            hour: int,
            minute: int,
            args: tuple[Any, ...] = (),
            job_id: str | None = None,
            misfire_grace_time: int = 3600,
    ) -> None:
        trigger = CronTrigger(hour=hour, minute=minute, timezone=self.scheduler.timezone)
        self.scheduler.add_job(
            callback,
            trigger=trigger,
            args=args,
            id=job_id,
            replace_existing=True if job_id else False,
            misfire_grace_time=misfire_grace_time,
        )

    def add_listener(self, callback: Callable[[Any], None], mask: int) -> None:
        self.scheduler.add_listener(callback, mask=mask)
