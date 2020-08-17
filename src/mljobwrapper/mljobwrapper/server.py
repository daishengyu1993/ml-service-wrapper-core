import importlib.util
import json
import os
import sys
from types import SimpleNamespace

from .contexts import EnvironmentVariableServiceContext
from .job_service import JobService


def get_job_instance(config_path: str = None) -> (JobService, dict):
    if not config_path:
        config_path = os.environ.get("JOB_CONFIG_PATH", "./job/config.json")

    with open(config_path, "r") as config_file:
        config = json.loads(config_file.read())

    job_script_path = config["modulePath"]

    if job_script_path is None:
        raise "The modulePath couldn't be determined!"

    config_directory_path = os.path.dirname(config_path)

    job_script_path = os.path.realpath(
        os.path.join(config_directory_path, job_script_path))

    print("Loading from script {}".format(job_script_path))

    job_script_dirname = os.path.dirname(job_script_path)
    job_script_basename = os.path.basename(job_script_path)

    os.sys.path.insert(0, job_script_dirname)

    job_script_module_name = os.path.splitext(job_script_basename)[0]

    print("Importing module {} from {}...".format(job_script_module_name, job_script_dirname))

    job_module = importlib.import_module(job_script_module_name)

    print("Imported module")

    if "className" in config:
        job_class_name = config["className"]
        job_type = getattr(job_module, job_class_name)

        print("Identified job type: {}".format(str(job_type)))

        job = job_type()
    else:
        service_instance_name = config["serviceInstanceName"]
        job = getattr(job_module, service_instance_name)

    print("Got job: {}".format(job))

    return (job, config.get("parameters", dict()))
