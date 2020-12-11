import os

import mlservicewrapper
import mlservicewrapper.core.debug
from service import SampleService

root_dir = os.path.join(os.path.dirname(__file__), '..')

input_data_dir = os.path.join(root_dir, 'data', 'input')
output_data_dir = os.path.join(root_dir, 'data', 'output')

load_parameters = {
    "ModBy": "3"
}

split_dataset_name = "Data"

if __name__ == "__main__":

    results = mlservicewrapper.core.debug.run(
        SampleService,
        input_data_dir,
        split_dataset_name=split_dataset_name,
        load_parameters=load_parameters,
        output_file_directory=output_data_dir
    )

    predictions = results["Results"]
