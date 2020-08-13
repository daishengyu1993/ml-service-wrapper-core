
import json

import pandas as pd

from ..contexts import JobRunContext
from ..job_service import JobService
from ..contexts import ServiceContext


class LocalLoadContext(ServiceContext):
    def __init__(self, parameters: dict = None):
        self.parameters = parameters if parameters is not None else dict()

        print("Loaded service parameters:")
        print(self.parameters)
        print()
            
    def get_parameter_value(self, name: str, default: str = None) -> str:
        return self.parameters.get(name, default)


class LocalRunContext(JobRunContext):
    def __init__(self, input_file_path: str, index_field_name: str = None, parameters: dict = None):
        self.parameters = parameters if parameters is not None else dict()

        print("Loaded execution parameters:")
        print(self.parameters)
        print()

        self.df = pd.read_csv(input_file_path, index_col = index_field_name)

        print("Loaded data:")
        print(self.df)
        print()

    def get_parameter_value(self, name: str, default: str = None) -> str:
        return self.parameters.get(name, default)
    
    def get_data(self) -> pd.DataFrame:
        return self.df.copy()
    

def run(job: JobService, input_file_path: str, index_field_name: str = None, load_parameters: dict = None, runtime_parameters: dict = None, output_file_path: str = None):
    load_context = LocalLoadContext(load_parameters)

    run_context = LocalRunContext(input_file_path, index_field_name, runtime_parameters)

    job.load(load_context)

    results = job.get_results(run_context)

    print("Got results:")
    print(results)
    print()

    if output_file_path != None:
        results.to_csv(output_file_path)

    return results
