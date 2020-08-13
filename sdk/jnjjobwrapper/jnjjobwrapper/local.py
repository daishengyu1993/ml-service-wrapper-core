import json
import os
import typing

import pandas as pd

from .contexts import JobRunContext, ServiceContext
from .job_service import JobService


class LocalLoadContext(ServiceContext):
    def __init__(self, parameters: dict = None):
        self.parameters = parameters if parameters is not None else dict()

        print("Loaded service parameters:")
        print(self.parameters)
        print()
            
    def get_parameter_value(self, name: str, default: str = None) -> str:
        return self.parameters.get(name, default)


class LocalRunContext(JobRunContext):
    def __init__(self, input_files_dir: str, output_files_dir: str, index_field_names: typing.Dict[str, str] = None, parameters: dict = None):
        self.parameters = parameters if parameters is not None else dict()
        self.input_files_dir = input_files_dir
        self.index_field_names = index_field_names if index_field_names is not None else dict()

        print("Loaded execution parameters:")
        print(self.parameters)
        print()

        self.output_dataframes = dict()

    def get_parameter_value(self, name: str, default: str = None) -> str:
        return self.parameters.get(name, default)

    async def get_input_dataframe(self, name: str):
        path = os.path.join(self.input_files_dir, name)

        index_name = self.index_field_names.get(name)

        self.df = pd.read_csv(path, index_col = index_name)

        print("Loaded data:")
        print(self.df)
        print()

    async def set_output_dataframe(self, name: str, df: pd.DataFrame):
        self.output_dataframes[name] = df

    def get_output_dataframe_names(self):
        return self.output_dataframes.keys()
    
    def get_output_dataframe(self, name: str):
        return self.output_dataframes.get(name)

async def run(job: JobService, input_file_directory: str, index_field_name: str = None, load_parameters: dict = None, runtime_parameters: dict = None, output_file_path: str = None):
    load_context = LocalLoadContext(load_parameters)

    run_context = LocalRunContext(input_file_directory, index_field_name, runtime_parameters)

    job.load(load_context)

    results = await job.process(run_context)

    print("Got results:")
    print(results)
    print()

    if output_file_path != None:
        results.to_csv(output_file_path)

    return results
