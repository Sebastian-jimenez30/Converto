from abc import ABC, abstractmethod
from uuid import UUID


class JobDispatcherPort(ABC):
    @abstractmethod
    def dispatch_conversion(self, job_id: UUID) -> None:
        raise NotImplementedError

