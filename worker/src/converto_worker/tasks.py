from uuid import UUID
import mimetypes

from converto_worker.adapters.db.models import ConversionJobModel
from converto_worker.bootstrap import celery_app, process_conversion_use_case, s3_storage, session_factory


@celery_app.task(name="converto_worker.tasks.process_conversion")
def process_conversion(job_id: str) -> dict[str, str]:
    job_uuid = UUID(job_id)
    with session_factory() as session:
        job = session.get(ConversionJobModel, job_uuid)
        if job is None:
            return {"job_id": job_id, "status": "not_found"}

        try:
            job.status = "processing"
            job.error_message = None
            session.commit()
            session.refresh(job)

            source_bytes = s3_storage.download_bytes(job.source_key)
            converted_bytes = process_conversion_use_case.execute(
                source_content=source_bytes,
                source_format=job.source_format,
                target_format=job.target_format,
            )

            output_key = f"outputs/{job.id}/result.{job.target_format}"
            output_mime, _ = mimetypes.guess_type(output_key)
            s3_storage.upload_bytes(
                output_key,
                converted_bytes,
                content_type=output_mime or "application/octet-stream",
            )

            job.status = "done"
            job.result_key = output_key
            job.error_message = None
            session.commit()

            return {"job_id": job_id, "status": "done", "result_key": output_key}
        except Exception as exc:  # noqa: BLE001
            session.rollback()
            job = session.get(ConversionJobModel, job_uuid)
            if job is not None:
                job.status = "failed"
                job.error_message = str(exc)[:1000]
                session.commit()
            return {"job_id": job_id, "status": "failed", "error": str(exc)}
