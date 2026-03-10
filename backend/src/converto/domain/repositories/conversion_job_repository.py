from abc import ABC, abstractmethod
from uuid import UUID

from converto.domain.entities.conversion_job import ConversionJob


class ConversionJobRepository(ABC):
    @abstractmethod
    def save(self, job: ConversionJob) -> ConversionJob:
        raise NotImplementedError

    @abstractmethod
    def get_by_id(self, job_id: UUID) -> ConversionJob | None:
        raise NotImplementedError

