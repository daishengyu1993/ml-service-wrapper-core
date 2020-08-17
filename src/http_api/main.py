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
from requests.structures import CaseInsensitiveDict

import jnjjobwrapper
import jnjjobwrapper.contexts
import jnjjobwrapper.errors
import jnjjobwrapper.job_service
import jnjjobwrapper.server
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import JSONResponse, Response
from starlette.routing import Route


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

class HttpResponseError(RuntimeError):
    def __init__(self, response: Response):
        super().__init__()
        self.response = response

class HttpJsonRunContext(jnjjobwrapper.contexts.CollectingJobRunContext):
    def __init__(self, parameters: dict, inputs: dict):
        super().__init__()
        self.__parameters = CaseInsensitiveDict(parameters or dict())
        self.__inputs = CaseInsensitiveDict(inputs or dict())

    def get_parameter_value(self, name: str, required: bool = True, default: str = None) -> str:
        if name not in self.__parameters:
            if required:
                raise HttpResponseError(error_response(400, "Required parameter '{}' was not found!".format(required)))
            else:
                return default
        
        return self.__parameters[name]

    async def get_input_dataframe(self, name: str, required: bool = True):
        if name not in self.__inputs:
            if required:
                raise HttpResponseError(error_response(400, "Required input data '{}' was not found!".format(required)))
            else:
                return None

        return pd.DataFrame.from_records(self.__inputs[name])

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
            await self.__job.process(req_ctx)
        except HttpResponseError as err:
            return err.response
        except jnjjobwrapper.errors.BadParameterError as err:
            return bad_request_response(err.message, "parameter", err.name)
        except jnjjobwrapper.errors.DatasetFieldError as err:
            return bad_request_response(err.message, "dataset", err.name, { "field": err.field_name })
        except jnjjobwrapper.errors.BadDatasetError as err:
            return bad_request_response(err.message, "dataset", err.name)
        except jnjjobwrapper.errors.BadRequestError as err:
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
            self.__job.dispose()
        
    async def __do_load(self):
        print("load")
        job, config_parameters = jnjjobwrapper.server.get_job_instance()

        context = jnjjobwrapper.contexts.EnvironmentVariableServiceContext("JOB_", config_parameters)

        print("job.load")
        await job.load(context)

        self.__job = job

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
    #     context = jnjjobwrapper.contexts.EnvironmentVariableServiceContext("JOB_", self.__config_parameters)

    #     await self.__job.load(context)

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

# def add_routes(routes: list, job: jnjjobwrapper.job_service.JobService, route_name: str = None):
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
