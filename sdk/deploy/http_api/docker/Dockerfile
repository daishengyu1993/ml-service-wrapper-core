FROM tiangolo/uvicorn-gunicorn-starlette:python3.8 as base

# FROM tiangolo/uvicorn-gunicorn-machine-learning:python3.7 as base
#RUN pip install starlette

COPY ./src/jnjjobwrapper /lib/jnjjobwrapper

RUN pip install /lib/jnjjobwrapper

FROM base as final

ENV JOB_CONFIG_PATH=/app/job/config.json

COPY ./src/http_api /app/

COPY ./sample_job /app/job

