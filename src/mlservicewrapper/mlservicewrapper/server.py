import importlib.util
import json
import os
import sys
from types import SimpleNamespace

from .contexts import EnvironmentVariableServiceContext
from .services import Service


def get_service_instance(config_path: str = None) -> (Service, dict):
    if not config_path:
        config_path = os.environ.get("SERVICE_CONFIG_PATH", "./service/config.json")

    with open(config_path, "r") as config_file:
        config = json.loads(config_file.read())

    service_script_path = config["modulePath"]

    if service_script_path is None:
        raise ValueError("The modulePath couldn't be determined!")

    config_directory_path = os.path.dirname(config_path)

    service_script_path = os.path.realpath(
        os.path.join(config_directory_path, service_script_path))

    print("Loading from script {}".format(service_script_path))

    service_script_dirname = os.path.dirname(service_script_path)
    service_script_basename = os.path.basename(service_script_path)

    os.sys.path.insert(0, service_script_dirname)

    service_script_module_name = os.path.splitext(service_script_basename)[0]

    print("Importing module {} from {}...".format(service_script_module_name, service_script_dirname))

    service_module = importlib.import_module(service_script_module_name)

    print("Imported module")

    if "className" in config:
        service_class_name = config["className"]
        service_type = getattr(service_module, service_class_name)

        print("Identified service type: {}".format(str(service_type)))

        service = service_type()
    else:
        service_instance_name = config["serviceInstanceName"]
        service = getattr(service_module, service_instance_name)

    print("Got service: {}".format(service))

    return (service, config.get("parameters", dict()))
