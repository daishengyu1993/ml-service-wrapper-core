import asyncio
import concurrent
import concurrent.futures
import importlib
import json
import os
import time
# from multiprocessing import Manager, Value
from threading import Thread

import pandas as pd
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import JSONResponse, Response
from starlette.routing import Route

import mlservicewrapper
import mlservicewrapper.contexts
import mlservicewrapper.errors
import mlservicewrapper.services
import mlservicewrapper.server


def error_response(status_code: int, message: str):
    return JSONResponse({"error": message}, status_code)

def bad_request_response(message: str, input_type: str = None, name: str = None, additional_details: dict = None):
    return JSONResponse({
        "error": "An invalid value was provided to {}.".format(name),
        "inputType": input_type,
        "name": name,
        "details": message,
        "additionalInformation": additional_details
    }, 400)

class HttpJsonRunContext(mlservicewrapper.contexts.CollectingProcessContext):
    def __init__(self, parameters: dict, inputs: dict):
        super().__init__()
        self.__parameters = parameters or dict()
        self.__inputs = inputs or dict()

    def get_parameter_value(self, name: str, required: bool = True, default: str = None) -> str:
        if name in self.__parameters:
            return self.__parameters[name]

        if required and not default:
            raise mlservicewrapper.errors.MissingParameterError(name)

        return default
    

    async def get_input_dataframe(self, name: str, required: bool = True):
        if name in self.__inputs:
            return pd.DataFrame.from_records(self.__inputs[name])

        if required:
            raise mlservicewrapper.errors.MissingDatasetError(name)

        return None


class ApiInstance:
    def __init__(self):
        self.__is_loading = True

    async def process(self, request: Request) -> Response:
        content_type = "application/json"
        # request.headers.get("Content-Type", "application/json")

        if content_type.lower() == "application/json":
            req_dict = await request.json()

            req_ctx = HttpJsonRunContext(req_dict.get("parameters", dict()), req_dict.get("inputs", dict()))
        else:
            return error_response(405, "This endpoint does not accept {}!".format(content_type))

        if self.__is_loading:
            return error_response(409, "The model is still loading!")

        try:
            await self.__service.process(req_ctx)
        except mlservicewrapper.errors.BadParameterError as err:
            return bad_request_response(err.message, "parameter", err.name)
        except mlservicewrapper.errors.DatasetFieldError as err:
            return bad_request_response(err.message, "dataset", err.name, { "field": err.field_name })
        except mlservicewrapper.errors.BadDatasetError as err:
            return bad_request_response(err.message, "dataset", err.name)
        except mlservicewrapper.errors.BadRequestError as err:
            return bad_request_response(err.message)

        outputs_dict = dict(((k, v.to_dict("records")) for k, v in req_ctx.output_dataframes()))
        
        return JSONResponse({
            "outputs": outputs_dict
        })

    def get_status(self, request: Request):
        if self.__is_loading:
            return JSONResponse({"status": "Loading...", "ready": False}, 200)

        return JSONResponse({"status": "Ready", "ready": True}, 200)

    def stop(self):
        if not self.__is_loading:
            self.__service.dispose()
        
    async def __do_load(self):
        print("load")
        service, config_parameters = mlservicewrapper.server.get_service_instance()

        context = mlservicewrapper.contexts.EnvironmentVariableServiceContext("SERVICE_", config_parameters)

        print("service.load")
        await service.load(context)

        self.__service = service

        self.__is_loading = False
        print("done load")

    def begin_loading(self):
        loop = asyncio.new_event_loop()

        asyncio.run_coroutine_threadsafe(self.__do_load(), loop)

        thr = Thread(target=loop.run_forever)
        thr.daemon = True
        thr.start()

        print("Done begin_loading")

        #asyncio.to_thread()

    # async def __load(self):
    #     context = mlservicewrapper.contexts.EnvironmentVariableServiceContext("SERVICE_", self.__config_parameters)

    #     await self.__service.load(context)

    #     self.__is_loading = False
        
    # def __start_background_loop(self, loop: asyncio.AbstractEventLoop) -> None:
    #     asyncio.set_event_loop(loop)
    #     loop.run_forever()

    # def begin_loading(self):
    #     loop = asyncio.new_event_loop()

    #     t = Thread(target=self.__start_background_loop, args=(loop,), daemon=True)
    #     t.start()

        # def do_load():
        #     asyncio.run_coroutine_threadsafe(self.__load(), loop)
        #     #loop.create_task(self.__load())

        # loop.call_soon_threadsafe(do_load)
        
        # load_run = Thread(target=run, args=())
        # load_run.start()

# def add_routes(routes: list, service: mlservicewrapper.services.Service, route_name: str = None):
#     route_prefix = "/api"

api = ApiInstance()

routes = [
    Route("/api/process", endpoint=api.process, methods=["POST"]),
    Route("/api/status", endpoint=api.get_status, methods=["GET"])
]

app = Starlette(debug=True, routes=routes, on_startup=[api.begin_loading], on_shutdown=[api.stop])

# print("begin_loading")
# api.begin_loading()

# print("done begin_loading!")

# time.sleep(60)

# print("done sleep")
