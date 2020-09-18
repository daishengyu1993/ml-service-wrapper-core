import importlib.util
import json
import os
import sys
import typing
from types import SimpleNamespace
import inspect

from .contexts import ServiceContext, EnvironmentVariableServiceContext, ProcessContext
from .services import Service

__all__ = ["ServerInstance"]

class ServerInstance:
    def __init__(self, config_path: str = None):

        if not config_path:
            config_path = os.environ.get("SERVICE_CONFIG_PATH", "./service/config.json")

        with open(config_path, "r") as config_file:
            config = json.load(config_file)

        config_directory_path = os.path.dirname(config_path)
        service_module_path = config.get("modulePath")

        if service_module_path is None:
            raise ValueError("The modulePath couldn't be determined!")

        self.__service_module_path = os.path.realpath(os.path.join(config_directory_path, service_module_path))

        self.__class_name = config.get("className")
        self.__service_instance_name = config.get("serviceInstanceName")

        if self.__class_name is None and self.__service_instance_name is None:
            raise ValueError("Either className or serviceInstanceName must be specified in the configuration file!")

        self.__parameters = config.get("parameters")
        self.__host_configs = config.get("host")
        
        self.__service: Service = None

    def get_host_config_section(self, name: str) -> dict:
        return self.__host_configs.get(name)

    def get_parameters(self) -> dict or None:
        return self.__parameters
    
    def __get_service_instance(self) -> Service:

        print("Loading from script {}".format(self.__service_module_path))

        service_module_dirname = os.path.dirname(self.__service_module_path)
        service_module_basename = os.path.basename(self.__service_module_path)

        os.sys.path.insert(0, service_module_dirname)

        service_module_name = os.path.splitext(service_module_basename)[0]

        print("Importing module {} from {}...".format(service_module_name, service_module_dirname))

        service_module = importlib.import_module(service_module_name)

        print("Imported module")

        if self.__class_name is not None:
            service_type = getattr(service_module, self.__class_name)

            print("Identified service type: {}".format(str(service_type)))

            service = service_type()
        else:
            service = getattr(service_module, self.__service_instance_name)

        print("Got service: {}".format(service))

        return service

    def is_loaded(self):
        return self.__service is not None

    async def load(self, ctx: ServiceContext = None):
        service = self.__get_service_instance()
        
        if hasattr(service, 'load'):
            config_parameters = self.get_parameters()

            if ctx is None:
                ctx = EnvironmentVariableServiceContext("SERVICE_", config_parameters)

            print("service.load")
            load_result = service.load(ctx)

            if inspect.iscoroutine(load_result):
                await load_result

        self.__service = service

    async def process(self, ctx: ProcessContext):
        if not self.is_loaded():
            raise ValueError("Be sure to call load before process!")
        
        process_result = self.__service.process(ctx)

        if inspect.iscoroutine(process_result):
            await process_result

    def dispose(self):
        if self.__service is None or not hasattr(self.__service, 'dispose'):
            return
        
        self.__service.dispose()
