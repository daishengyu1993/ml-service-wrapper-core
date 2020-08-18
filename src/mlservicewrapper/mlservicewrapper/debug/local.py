import statistics
import asyncio
import json
import os
import re
import typing
import time

import pandas as pd

from .. import contexts, errors, services


class _LocalLoadContext(contexts.ServiceContext):
    def __init__(self, parameters: dict = None):
        self.__parameters = parameters or dict()

        print("Loaded service parameters:")
        print(self.__parameters)
        print()
            
    def get_parameter_value(self, name: str, required: bool = True, default: str = None) -> str:
        contexts.NameValidator.raise_if_invalid(name)
        
        if name in self.__parameters:
            return self.__parameters[name]
        
        if required and default is None:
            raise errors.MissingParameterError(name)

        print("Could not find optional parameter {}".format(name))

        return default

def get_input_path(dir_path: str, name: str):
    name_regex = re.escape(name) + r"\.\w+"
    
    file_path: str = None
    for f in os.scandir(dir_path):
        if not re.match(name_regex, f.name):
            continue

        if file_path:
            raise ValueError("Multiple files matched input dataset {}".format(name))

        file_path = f.path

    return file_path

class _LocalRunContext(contexts.CollectingProcessContext):
    def __init__(self, input_files_dir: str, output_files_dir: str = None, parameters: dict = None):
        super().__init__()
        self.__parameters = parameters or dict()

        self.__input_files_dir = input_files_dir
        self.__output_files_dir = output_files_dir

    def get_parameter_value(self, name: str, required: bool = True, default: str = None) -> str:
        contexts.NameValidator.raise_if_invalid(name)
        
        if name in self.__parameters:
            return self.__parameters[name]
        
        if required and default is None:
            raise errors.MissingParameterError(name)
            
        print("Could not find optional parameter {}".format(name))

        return default

    async def get_input_dataframe(self, name: str, required: bool = True):
        contexts.NameValidator.raise_if_invalid(name)
        
        file_path = get_input_path(self.__input_files_dir, name)

        if file_path:
            return pd.read_csv(file_path)

        if required:
            raise errors.MissingDatasetError(name)

        return None

    async def set_output_dataframe(self, name: str, df: pd.DataFrame):
        contexts.NameValidator.raise_if_invalid(name)
        
        await super().set_output_dataframe(name, df)
        
        print("Got results for {}".format(name))
        print(df)
        print()

        if self.__output_files_dir:
            os.makedirs(self.__output_files_dir, exist_ok=True)

            df.to_csv(os.path.join(self.__output_files_dir, name + ".csv"), index=False)

class _LocalDataFrameRunContext(contexts.ProcessContext):
    def __init__(self, df: pd.DataFrame, name: str, base_ctx: contexts.ProcessContext):
        self.__base_ctx = base_ctx
        self.__name = name
        self.__df = df

    def get_parameter_value(self, name: str, required: bool = True, default: str = None) -> str:
        return self.__base_ctx.get_parameter_value(name, required, default)

    def set_output_dataframe(self, name: str, df: pd.DataFrame):
        return self.__base_ctx.set_output_dataframe(name, df)

    async def get_input_dataframe(self, name: str, required: bool = True):
        contexts.NameValidator.raise_if_invalid(name)
        
        if name == self.__name:
            return self.__df

        return await self.__base_ctx.get_input_dataframe(name, required)

    def output_dataframes(self):
        return self.__base_ctx.output_dataframes()

    

def run(service: services.Service, input_file_directory: str, output_file_directory: str = None, split_dataset_name: str = None, load_parameters: dict = None, runtime_parameters: dict = None):
    load_context = _LocalLoadContext(load_parameters)

    loop = asyncio.get_event_loop()

    print("Loading...")
    s = time.perf_counter()
    loop.run_until_complete(service.load(load_context))
    e = time.perf_counter()

    load_time = e - s
    
    print("Running...")

    run_context = _LocalRunContext(input_file_directory, output_file_directory, runtime_parameters)

    times = list()

    if split_dataset_name:
        split_dataset_path = get_input_path(input_file_directory, split_dataset_name)
        
        df = pd.read_csv(split_dataset_path)

        for r in df.itertuples(index=False):
            rdf = pd.DataFrame([r])
        
            row_run_context = _LocalDataFrameRunContext(rdf, split_dataset_name, run_context)

            s = time.perf_counter()
            loop.run_until_complete(service.process(row_run_context))
            e = time.perf_counter()

            times.append(e - s)
    else:

        s = time.perf_counter()
        loop.run_until_complete(service.process(run_context))
        e = time.perf_counter()

        times.append(e - s)

    print("Load time: {}s".format(load_time))
    print()
    print("Min process time: {}s".format(min(times)))
    print("Mean process time: {}s".format(statistics.mean(times)))
    print("Median process time: {}s".format(statistics.median(times)))
    print("Max process time: {}s".format(max(times)))
    
    return dict(run_context.output_dataframes())
