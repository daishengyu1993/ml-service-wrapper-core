import inspect
import types
from typing import Union

from pandas import DataFrame

from .contexts import JobRunContext, ServiceContext


class JobService:
    async def load(self, ctx: ServiceContext) -> types.CoroutineType:
        """Initialize variables and load models."""

        resp = self.load_internal(ctx)

        if inspect.iscoroutine(resp):
            await resp

        return resp

    async def dispose(self) -> types.CoroutineType:
        """Clean up any resources (file handles, temporary files, etc.) to gracefully shut down."""

        resp = self.dispose_internal()

        if inspect.iscoroutine(resp):
            await resp

        return resp

    async def process(self, ctx: JobRunContext) -> types.CoroutineType:
        """Run a prediction or processing job."""

        resp = self.process_internal(ctx)

        if inspect.iscoroutine(resp):
            await resp

        return resp

    def __enter__(self):
        return self

    def __exit__(self, ctx_type, ctx_value, ctx_traceback):
        self.dispose()

    async def load_internal(self, ctx: ServiceContext) -> Union[types.CoroutineType, None]:
        """Initialize variables and load models."""

    async def dispose_internal(self) -> Union[types.CoroutineType, None]:
        """Clean up any resources (file handles, temporary files, etc.) to gracefully shut down."""

        pass

    async def process_internal(self, ctx: JobRunContext) -> Union[types.CoroutineType, None]:
        """Run a prediction or processing job."""
        """Implementations may make in-place modifications to any data they receive."""

        raise NotImplementedError()
