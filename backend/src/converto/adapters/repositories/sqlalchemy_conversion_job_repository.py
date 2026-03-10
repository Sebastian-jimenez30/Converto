from uuid import UUID

from sqlalchemy.orm import sessionmaker

from converto.adapters.db.models import ConversionJobModel
from converto.domain.entities.conversion_job import ConversionJob, JobStatus
from converto.domain.repositories.conversion_job_repository import ConversionJobRepository


class SqlAlchemyConversionJobRepository(ConversionJobRepository):
    def __init__(self, session_factory: sessionmaker) -> None:
        self._session_factory = session_factory

    def save(self, job: ConversionJob) -> ConversionJob:
        with self._session_factory() as session:
            model = ConversionJobModel(
                id=job.id,
                source_filename=job.source_filename,
                source_format=job.source_format,
                target_format=job.target_format,
                status=job.status.value,
                source_key=job.source_key,
                result_key=job.result_key,
                error_message=job.error_message,
                created_at=job.created_at,
                updated_at=job.updated_at,
            )
            session.add(model)
            session.commit()
            session.refresh(model)
            return self._to_domain(model)

    def get_by_id(self, job_id: UUID) -> ConversionJob | None:
        with self._session_factory() as session:
            model = session.get(ConversionJobModel, job_id)
            if model is None:
                return None
            return self._to_domain(model)

    @staticmethod
    def _to_domain(model: ConversionJobModel) -> ConversionJob:
        return ConversionJob(
            id=model.id,
            source_filename=model.source_filename,
            source_format=model.source_format,
            target_format=model.target_format,
            status=JobStatus(model.status),
            source_key=model.source_key,
            result_key=model.result_key,
            error_message=model.error_message,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )
