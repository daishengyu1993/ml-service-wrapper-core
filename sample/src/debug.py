import os

import mlservicewrapper
import mlservicewrapper.debug
from service import SampleService

root_dir = os.path.join(os.path.dirname(__file__), '..')

input_data_dir = os.path.join(root_dir, 'data', 'input')
output_data_dir = os.path.join(root_dir, 'data', 'output')

load_parameters = {
    "ModBy": "3"
}

if __name__ == "__main__":

    with SampleService() as service:
        results = mlservicewrapper.debug.run(service, input_data_dir, load_parameters=load_parameters, output_file_directory=output_data_dir)

    predictions = results["Results"]
