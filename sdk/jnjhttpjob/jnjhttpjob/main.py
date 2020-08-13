
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

from jnjjobwrapper import (EnvironmentVariableServiceContext, JobRunContext,
                           JobService)

# from flask import Flask

# app = Flask(__name__)

# @app.route("/")
# def hello():
#     return "Hello World from Flask"

# if __name__ == "__main__":
#     # Only for debugging while developing
#     app.run(host='0.0.0.0', debug=True, port=80)


# from job.sample_job import SampleJob

# print("http__main__")


class HttpRunContext(JobRunContext):
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
    def __init__(self, job: JobService):
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

        resp = self.job.get_results(req_ctx)

        resp_dict = [{"id": k, "result": v} for (k, v) in resp.to_dict("index").items()]

        return JSONResponse(resp_dict)

    def get_status(self, request: Request):
        if self.is_loading:
            return JSONResponse({"status": "Loading...", "ready": False}, 200)

        return JSONResponse({"status": "Ready", "ready": True}, 200)

    def load(self):
        context = EnvironmentVariableServiceContext("JOB_")

        self.job.load(context)

        self.is_loading = False

    def begin_loading(self):
        load_run = Thread(target=self.load, args=())
        load_run.start()


config_path = os.environ.get("JOB_CONFIG_PATH", "./job/config.json")

with open(config_path, "r") as config_file:
    config = json.loads(config_file.read())

job_script_path = config["modulePath"]
job_class_name = config["className"]

if job_script_path is None:
    raise "The modulePath couldn't be determined!"

config_directory_path = os.path.dirname(config_path)

job_script_path = os.path.realpath(
    os.path.join(config_directory_path, job_script_path))

print("Loading from script {}".format(job_script_path))

job_script_directory_path = os.path.dirname(job_script_path)
job_script_basename = os.path.basename(job_script_path)

os.sys.path.insert(0, "/app/job")

#cwd_original = os.getcwd()
#print("Moving from {} to {} to import {}".format(cwd_original, job_script_directory_path, job_script_basename))
# os.chdir(job_script_directory_path)

job_script_module_name = os.path.splitext(job_script_basename)[0]

job_module = importlib.import_module(job_script_module_name)

# job_script_globals = {
#     "__name__": job_script_module_name,
#     "__file__": job_script_basename
# }

# with open(job_script_basename, "r") as job_script_file:
#     job_script = job_script_file.open()

# exec(job_script, job_script_globals)
# job_module = job_script_globals

# spec = importlib.util.spec_from_file_location(job_script_module_name, job_script_basename)
# job_module = importlib.util.module_from_spec(spec)
# spec.loader.exec_module(job_module)
# os.chdir(cwd_original)

job_type = getattr(job_module, job_class_name)

job = job_type()

api = ApiInstance(job)

api.begin_loading()

routes = [
    Route("/api/process", endpoint=api.process, methods=["POST"]),
    Route("/api/status", endpoint=api.get_status, methods=["GET"])
]

app = Starlette(debug=True, routes=routes)
