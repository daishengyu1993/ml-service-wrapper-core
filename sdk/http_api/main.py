import asyncio
import concurrent
import concurrent.futures
import importlib
import json
import os
# from multiprocessing import Manager, Value
from threading import Thread

import pandas as pd
from requests.structures import CaseInsensitiveDict
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import JSONResponse, Response
from starlette.routing import Route

import jnjjobwrapper
import jnjjobwrapper.contexts
import jnjjobwrapper.errors
import jnjjobwrapper.job_service
import jnjjobwrapper.server


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
        self.parameters = CaseInsensitiveDict(parameters or dict())
        self.inputs = CaseInsensitiveDict(inputs or dict())

    def get_parameter_value(self, name: str, required: bool = True, default: str = None) -> str:
        if name not in self.parameters:
            if required:
                raise HttpResponseError(error_response(400, "Required parameter '{}' was not found!".format(required)))
            else:
                return default
        
        return self.parameters[name]

    async def get_input_dataframe(self, name: str, required: bool = True):
        if name not in self.inputs:
            if required:
                raise HttpResponseError(error_response(400, "Required input data '{}' was not found!".format(required)))
            else:
                return None

        return pd.DataFrame.from_records(self.inputs[name])

class ApiInstance:
    def __init__(self, job: jnjjobwrapper.job_service.JobService):
        self.is_loading = True
        self.job = job

    async def process(self, request: Request) -> Response:
        content_type = "application/json"
        # request.headers.get("Content-Type", "application/json")

        if content_type.lower() == "application/json":
            req_dict = await request.json()

            req_ctx = HttpJsonRunContext(req_dict.get("parameters", dict()), req_dict.get("inputs", dict()))
        else:
            return error_response(405, "This endpoint does not accept {}!".format(content_type))

        if self.is_loading:
            return error_response(409, "The model is still loading!")

        try:
            await self.job.process(req_ctx)
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
        if self.is_loading:
            return JSONResponse({"status": "Loading...", "ready": False}, 200)

        return JSONResponse({"status": "Ready", "ready": True}, 200)

    async def load(self):
        context = jnjjobwrapper.contexts.EnvironmentVariableServiceContext("JOB_")

        await self.job.load(context)

        self.is_loading = False

    def begin_loading(self):
        loop = asyncio.get_event_loop()

        def do_load():
            loop.create_task(self.load())

        loop.call_soon_threadsafe(do_load)
        
        # load_run = Thread(target=run, args=())
        # load_run.start()


job = jnjjobwrapper.server.get_job_instance()

api = ApiInstance(job)

api.begin_loading()

routes = [
    Route("/api/process", endpoint=api.process, methods=["POST"]),
    Route("/api/status", endpoint=api.get_status, methods=["GET"])
]

app = Starlette(debug=True, routes=routes)
