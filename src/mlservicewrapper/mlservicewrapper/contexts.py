import re
import asyncio
import os
import types
import typing

import pandas as pd

from . import errors

class NameValidator:
    __valid_name_regex = re.compile(r'^[A-Z][\w\d]*$')

    @classmethod
    def raise_if_invalid(cls, name: str):
        if not cls.__valid_name_regex.match(name):
            raise ValueError("Name is not valid: '{}'!".format(name))

        pass
    


class ServiceContext:
    def get_parameter_value(self, name: str, required: bool = True, default: str = None) -> str:
        raise NotImplementedError()

class ProcessContext:
    def get_parameter_value(self, name: str, required: bool = True, default: str = None) -> str:
        raise NotImplementedError()
    
    def get_input_dataframe(self, name: str, required: bool = True) -> types.CoroutineType:
        raise NotImplementedError()

    def set_output_dataframe(self, name: str, df: pd.DataFrame) -> types.CoroutineType:
        raise NotImplementedError()

class CollectingProcessContext(ProcessContext):
    def __init__(self):
        super()
        self.__output_dataframes = dict()

    async def set_output_dataframe(self, name: str, df: pd.DataFrame):
        NameValidator.raise_if_invalid(name)

        self.__output_dataframes[name] = df
    
    def get_output_dataframe(self, name: str):
        NameValidator.raise_if_invalid(name)

        return self.__output_dataframes.get(name)

    def output_dataframes(self):
        return self.__output_dataframes.items()


class EnvironmentVariableServiceContext(ServiceContext):
    def __init__(self, prefix: str, default_values: dict = None):
        self.__prefix = prefix
        self.__default_values = default_values or dict()
    
    def get_parameter_value(self, name: str, required: bool = True, default: str = None) -> str:
        NameValidator.raise_if_invalid(name)

        ev = os.environ.get(self.__prefix + name)
        if ev:
            return ev

        if name in self.__default_values:
            return self.__default_values[name]

        if required and default is None:
            raise errors.MissingParameterError(name)

        return default
