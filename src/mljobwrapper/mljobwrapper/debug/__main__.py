import argparse
import os

from .. import server
from . import local


#https://stackoverflow.com/a/42355279/1270504
class StoreDictKeyPair(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        my_dict = {}
        for kv in values.split(","):
            k,v = kv.split("=")
            my_dict[k] = v
        setattr(namespace, self.dest, my_dict)

parser = argparse.ArgumentParser(description='Locally debug.', prog = "mljobwrapper.debug")
parser.add_argument(
    '--config', help='Path to job configuration file', required=True)
parser.add_argument('--input-dir', dest='input_dir',
                    help='Path to input directory', required=True)
parser.add_argument('--output-dir', dest='output_dir',
                    help='Path to input directory')
parser.add_argument("--load-params", dest="load_params", action=StoreDictKeyPair, metavar="KEY1=VAL1,KEY2=VAL2...")
parser.add_argument("--run-params", dest="runtime_parameters", action=StoreDictKeyPair, metavar="KEY1=VAL1,KEY2=VAL2...")

args = parser.parse_args()

job, params = server.get_job_instance(args.config)

local.run(job, args.input_dir, load_parameters=args.load_params, runtime_parameters=args.runtime_parameters, output_file_directory=args.output_dir)
