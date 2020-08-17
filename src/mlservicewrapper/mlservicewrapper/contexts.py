import asyncio
import os
import types
import typing

import pandas as pd

from . import errors


class ServiceContext:
    def get_parameter_value(self, name: str, required: bool = True, default: str = None) -> str:
        raise NotImplementedError()

class ServiceRunContext:
    def get_parameter_value(self, name: str, required: bool = True, default: str = None) -> str:
        raise NotImplementedError()
    
    def get_input_dataframe(self, name: str, required: bool = True) -> types.CoroutineType:
        raise NotImplementedError()

    def set_output_dataframe(self, name: str, df: pd.DataFrame) -> types.CoroutineType:
        raise NotImplementedError()

class CollectingServiceRunContext(ServiceRunContext):
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
    
    def get_parameter_value(self, name: str, required: bool = True, default: str = None) -> str:
        ev = os.environ.get(self.__prefix + name)
        if ev:
            return ev

        if name in self.__default_values:
            return self.__default_values[name]

        if required:
            raise errors.MissingParameterError(name)

        return default
