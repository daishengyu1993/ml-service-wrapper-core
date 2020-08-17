import asyncio
import json
import os
import re
import typing

import pandas as pd

from .. import contexts, errors, services


class LocalLoadContext(contexts.ServiceContext):
    def __init__(self, parameters: dict = None):
        self.__parameters = parameters or dict()

        print("Loaded service parameters:")
        print(self.__parameters)
        print()
            
    def get_parameter_value(self, name: str, required: bool = True, default: str = None) -> str:
        if name in self.__parameters:
            return self.__parameters[name]
        
        if not required:
            print("Could not find optional parameter {}".format(name))

            return default

        raise errors.MissingParameterError(name)

class LocalRunContext(contexts.CollectingServiceRunContext):
    def __init__(self, input_files_dir: str, output_files_dir: str, parameters: dict = None):
        super().__init__()
        self.__parameters = parameters or dict()

        self.__input_files_dir = input_files_dir
        self.__output_files_dir = output_files_dir

    def get_parameter_value(self, name: str, required: bool = True, default: str = None) -> str:
        if name in self.__parameters:
            return self.__parameters[name]
        
        if required:
            raise errors.MissingParameterError(name)
            
        print("Could not find optional parameter {}".format(name))

        return default

    async def get_input_dataframe(self, name: str, required: bool = True):
        name_regex = re.escape(name) + r"\.\w+"
        
        file_path: str = None
        for f in os.scandir(self.__input_files_dir):
            if not re.match(name_regex, f.name):
                continue
 
            if file_path:
                raise "Multiple files matched input dataset {}".format(name)

            file_path = f.path

        if file_path:
            return pd.read_csv(file_path)

        if required:
            raise errors.MissingDatasetError(name)

        return None

    async def set_output_dataframe(self, name: str, df: pd.DataFrame):
        await super().set_output_dataframe(name, df)
        
        print("Got results for {}".format(name))
        print(df)
        print()

        if self.__output_files_dir:
            df.to_csv(os.path.join(self.__output_files_dir, name + ".csv"), index=False)

def run(service: services.Service, input_file_directory: str, load_parameters: dict = None, runtime_parameters: dict = None, output_file_directory: str = None):
    load_context = LocalLoadContext(load_parameters)

    run_context = LocalRunContext(input_file_directory, output_file_directory, runtime_parameters)

    print("Loading...")
    asyncio.run(service.load(load_context))

    print("Running...")
    asyncio.run(service.process(run_context))

    return dict(run_context.output_dataframes())
