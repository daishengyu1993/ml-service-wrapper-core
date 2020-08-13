import asyncio
import os
import types
import typing

from pandas import DataFrame


class ServiceContext:
    def get_parameter_value(self, name: str, default: str = None) -> str:
        raise NotImplementedError()

class JobRunContext:
    def get_parameter_value(self, name: str, default: str = None) -> str:
        raise NotImplementedError()
    
    def get_input_dataframe(self, name: str) -> types.CoroutineType:
        raise NotImplementedError()

    def set_output_dataframe(self, name: str, df: DataFrame) -> types.CoroutineType:
        raise NotImplementedError()

class EnvironmentVariableServiceContext(ServiceContext):
    def __init__(self, prefix: str):
        self.prefix = prefix
    
    def get_parameter_value(self, name: str, default: str = None) -> str:
        return os.environ.get(self.prefix + name, default)
