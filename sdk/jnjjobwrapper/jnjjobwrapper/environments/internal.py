import importlib.util
import json
import os
import sys
from types import SimpleNamespace

from ..job_service import JobService
from ..contexts import ServiceContext


class EnvironmentVariableServiceContext(ServiceContext):
    def __init__(self, prefix: str):
        self.prefix = prefix
    
    def get_parameter_value(self, name: str, default: str = None) -> str:
        return os.environ.get(self.prefix + name, default)

def get_job_type():
    print("not yet in sys modules")

    config_path = os.environ.get("JOB_CONFIG_PATH")

    with open(config_path, "r") as config_file:
        config = json.loads(config_file.read())

    job_script_path = config["modulePath"]
    job_class_name = config["className"]

    if job_script_path is None:
        raise "The modulePath couldn't be determined!"

    job_script_path = os.path.join(os.path.dirname(config_path), job_script_path)

    print("Loading from script {}".format(job_script_path))

    spec = importlib.util.spec_from_file_location("jnjjobwrapper_caller", job_script_path)
    caller_module = importlib.util.module_from_spec(spec)

    if "jnjjobwrapper_caller" not in sys.modules:
        sys.modules["jnjjobwrapper_caller"] = caller_module

    spec.loader.exec_module(caller_module)
    #importlib.reload(caller_module)

    return getattr(caller_module, job_class_name)

def load_job() -> JobService:
    job_type = get_job_type()
    job = job_type()

    ctx = EnvironmentVariableServiceContext("JNJ_JOB_")

    job.load(ctx)
    
    return job
