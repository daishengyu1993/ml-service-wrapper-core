
from pandas import DataFrame

from .job_run_context import JobRunContext
from .service_context import ServiceContext


class JobService:
    def load(self, ctx: ServiceContext) -> None:
        """Initialize variables and load models."""

        pass

    def dispose(self) -> None:
        """Clean up any resources (file handles, temporary files, etc.) to gracefully shut down."""

        pass

    def get_results(self, ctx: JobRunContext) -> DataFrame:
        """Run a prediction or processing job, and return results as a DataFrame."""
        """Result records must mirror the DataFrame Index from any data they receive, but there is no requirement that all input Indexes will have output."""
        """Implementations may make in-place modifications to any data they receive."""

        raise NotImplementedError()

    def __enter__(self):
        return self

    def __exit__(self, ctx_type, ctx_value, ctx_traceback):
        self.dispose()
