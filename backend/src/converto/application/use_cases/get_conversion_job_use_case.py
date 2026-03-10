from uuid import UUID

from converto.domain.entities.conversion_job import ConversionJob
from converto.domain.repositories.conversion_job_repository import ConversionJobRepository


class GetConversionJobUseCase:
    def __init__(self, repository: ConversionJobRepository) -> None:
        self._repository = repository

    def execute(self, job_id: UUID) -> ConversionJob | None:
        return self._repository.get_by_id(job_id)

