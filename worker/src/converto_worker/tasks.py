from converto_worker.bootstrap import celery_app, process_conversion_use_case


@celery_app.task(name="converto_worker.tasks.process_conversion")
def process_conversion(job_id: str) -> dict[str, str]:
    # TODO: Replace hardcoded values once API persists full job payload for workers.
    result_key = process_conversion_use_case.execute(
        source_key=f"inbox/{job_id}.source",
        source_format="source",
        target_format="target",
    )
    return {"job_id": job_id, "result_key": result_key}

