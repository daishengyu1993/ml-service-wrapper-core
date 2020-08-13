
from pandas import DataFrame

from .contexts import JobRunContext
from .contexts import ServiceContext


class JobService:
    def load(self, ctx: ServiceContext) -> None:
        """Initialize variables and load models."""

        return self.load_internal(ctx)

    def dispose(self) -> None:
        """Clean up any resources (file handles, temporary files, etc.) to gracefully shut down."""

        return self.dispose_internal()

    def get_results(self, ctx: JobRunContext) -> DataFrame:
        """Run a prediction or processing job, and return results as a DataFrame."""

        return self.get_results_internal(ctx)

    def __enter__(self):
        return self

    def __exit__(self, ctx_type, ctx_value, ctx_traceback):
        self.dispose()

    def load_internal(self, ctx: ServiceContext) -> None:
        """Initialize variables and load models."""

        pass

    def dispose_internal(self) -> None:
        """Clean up any resources (file handles, temporary files, etc.) to gracefully shut down."""

        pass

    def get_results_internal(self, ctx: JobRunContext) -> DataFrame:
        """Run a prediction or processing job, and return results as a DataFrame."""
        """Result records must mirror the DataFrame Index from any data they receive, but there is no requirement that all input Indexes will have output."""
        """Implementations may make in-place modifications to any data they receive."""

        raise NotImplementedError()
