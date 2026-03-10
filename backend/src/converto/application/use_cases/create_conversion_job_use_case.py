from converto.application.commands.create_conversion_job_command import CreateConversionJobCommand
from converto.application.ports.job_dispatcher_port import JobDispatcherPort
from converto.domain.entities.conversion_job import ConversionJob
from converto.domain.repositories.conversion_job_repository import ConversionJobRepository


class CreateConversionJobUseCase:
    def __init__(
        self,
        repository: ConversionJobRepository,
        job_dispatcher: JobDispatcherPort,
    ) -> None:
        self._repository = repository
        self._job_dispatcher = job_dispatcher

    def execute(self, command: CreateConversionJobCommand) -> ConversionJob:
        job = ConversionJob.create(
            source_filename=command.source_filename,
            source_format=command.source_format,
            target_format=command.target_format,
            source_key=command.source_key,
        )
        saved = self._repository.save(job)
        self._job_dispatcher.dispatch_conversion(saved.id)
        return saved

