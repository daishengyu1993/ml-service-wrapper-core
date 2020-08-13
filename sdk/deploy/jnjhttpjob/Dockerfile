FROM tiangolo/uvicorn-gunicorn-starlette:python3.8 as base

COPY ./jnjjobwrapper /lib/jnjjobwrapper

RUN pip install /lib/jnjjobwrapper

FROM base as final

ENV JOB_CONFIG_PATH=/app/job/config.json

COPY ./jnjhttpjob/jnjhttpjob /app/

COPY ./sample_job /app/job

