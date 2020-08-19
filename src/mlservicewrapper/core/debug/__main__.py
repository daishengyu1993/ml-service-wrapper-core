import argparse
import os

from .. import server
from . import local


#https://stackoverflow.com/a/42355279/1270504
class _StoreDictKeyPair(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        my_dict = {}
        for kv in values.split(","):
            k,v = kv.split("=")
            my_dict[k] = v
        setattr(namespace, self.dest, my_dict)

parser = argparse.ArgumentParser(description='Locally debug.', prog = "mlservicewrapper.core.debug")
parser.add_argument(
    '--config', help='Path to service configuration file', required=True)
parser.add_argument('--input-dir', dest='input_dir',
                    help='Path to input directory', required=True)
parser.add_argument('--output-dir', dest='output_dir',
                    help='Path to input directory')
parser.add_argument("--load-params", dest="load_params", action=_StoreDictKeyPair, metavar="KEY1=VAL1,KEY2=VAL2...")
parser.add_argument("--run-params", dest="runtime_parameters", action=_StoreDictKeyPair, metavar="KEY1=VAL1,KEY2=VAL2...")

parser.add_argument('--split-dataset-for-perf', dest='split_dataset_name',
                    help='Input dataset to split for performance evaluation.')

parser.add_argument('--assess-accuracy', dest='assess_accuracy', action=_StoreDictKeyPair, metavar="INPUT_DATASET_1.FIELD=OUTPUT_DATASET_1.FIELD,INPUT_DATASET_2.FIELD=OUTPUT_DATASET_2.FIELD,...",
                    help='Perform accuracy assessment against the given fields.')

args = parser.parse_args()

service, config_params = server.get_service_instance(args.config)

load_params = dict()

if config_params:
    load_params.update(config_params)

if args.load_params:
    load_params.update(args.load_params)
    
local.run(
    service,
    args.input_dir,
    split_dataset_name=args.split_dataset_name,
    load_parameters=args.load_params,
    runtime_parameters=args.runtime_parameters,
    output_file_directory=args.output_dir,
    assess_accuracy=args.assess_accuracy
)
