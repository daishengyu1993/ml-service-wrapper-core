import asyncio
import os
import types
import typing

import pandas as pd


class ServiceContext:
    def get_parameter_value(self, name: str, default: str = None) -> str:
        raise NotImplementedError()

class JobRunContext:
    def get_parameter_value(self, name: str, required: bool = True, default: str = None) -> str:
        raise NotImplementedError()
    
    def get_input_dataframe(self, name: str, required: bool = True) -> types.CoroutineType:
        raise NotImplementedError()

    def set_output_dataframe(self, name: str, df: pd.DataFrame) -> types.CoroutineType:
        raise NotImplementedError()

class CollectingJobRunContext(JobRunContext):
    def __init__(self):
        super()
        self.__output_dataframes = dict()

    async def set_output_dataframe(self, name: str, df: pd.DataFrame):
        self.__output_dataframes[name] = df
    
    def get_output_dataframe(self, name: str):
        return self.__output_dataframes.get(name)

    def output_dataframes(self):
        return self.__output_dataframes.items()


class EnvironmentVariableServiceContext(ServiceContext):
    def __init__(self, prefix: str, default_values: dict = None):
        self.__prefix = prefix
        self.__default_values = default_values or dict()
    
    def get_parameter_value(self, name: str, default: str = None) -> str:
        return os.environ.get(self.__prefix + name, self.__default_values.get(name, default))
