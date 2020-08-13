import asyncio
import concurrent
import concurrent.futures
import importlib
import json
import os
# from multiprocessing import Manager, Value
from threading import Thread

import pandas as pd
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.routing import Route

import jnjjobwrapper
import jnjjobwrapper.contexts
import jnjjobwrapper.job_service
import jnjjobwrapper.server

# from jnjjobwrapper import (EnvironmentVariableServiceContext, JobRunContext,
#                            JobService, load_job)



class HttpRunContext(jnjjobwrapper.contexts.JobRunContext):
    def __init__(self, parameters: dict, df: pd.DataFrame):
        self.parameters = parameters if parameters is not None else dict()
        self.df = df

    def get_parameter_value(self, name: str) -> str:
        return self.parameters.get(name)

    def get_data(self) -> pd.DataFrame:
        return self.df


def error(status_code: int, message: str):
    return JSONResponse({"error": message}, status_code)


class ApiInstance:
    def __init__(self, job: jnjjobwrapper.job_service.JobService):
        self.is_loading = True
        self.job = job

    async def process(self, request: Request) -> JSONResponse:
        content_type = "application/json"
        # request.headers.get("Content-Type", "application/json")

        if content_type.lower() == "application/json":
            req_dict = await request.json()

            if "records" not in req_dict:
                return error(400, "Missing required field records!")

            parameters = req_dict["parameters"] if "parameters" in req_dict and req_dict["parameters"] is not None else dict(
            )

            req_df = pd.DataFrame.from_records(
                [record["document"] for record in req_dict["records"]])

            doc_ids = [record["id"] for record in req_dict["records"]]

            if len(set(doc_ids)) < len(doc_ids):
                return error(400, "A duplicate id was detected!")

            req_df.set_index(pd.Index(doc_ids), inplace=True)
        else:
            return error(405, "This endpoint does not accept {}!".format(content_type))

        if self.is_loading:
            return error(409, "The model is still loading!")

        req_ctx = HttpRunContext(parameters, req_df)

        resp = self.job.process(req_ctx)

        resp_dict = [{"id": k, "result": v} for (k, v) in resp.to_dict("index").items()]

        return JSONResponse(resp_dict)

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
