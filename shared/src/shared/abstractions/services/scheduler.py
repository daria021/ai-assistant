from abc import ABC, abstractmethod
from collections.abc import Callable
from datetime import datetime
from typing import Coroutine, Any


class SchedulerInterface(ABC):
    @abstractmethod
    def schedule_once(
            self,
            callback: Callable[[Any], Coroutine[Any, Any, None]],
            runs_on: datetime,
            args: tuple[Any, ...] = (),
            job_id: str = None,
            misfire_grace_time: int = 60,
    ) -> None:
        ...

    @abstractmethod
    def initialize(self) -> None:
        ...
