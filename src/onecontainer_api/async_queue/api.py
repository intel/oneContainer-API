# SPDX-License-Identifier: BSD-3-Clause
#  Copyright (c) 2020 Intel Corporation
"""interface to redis-queue."""
from enum import Enum
from typing import Optional
from typing import Union
from typing import Dict
from typing import Any

from fastapi import FastAPI, Request
from pydantic import BaseModel

from logger import logger
from job_queue import fetch_job
from job_queue import enqueue_job
from job_queue import delete_jobs
from job_queue import get_info

import json

app = FastAPI()


class RequestType(str, Enum):
    get = "get"
    post = "post"
    delete = "delete"
    put = "put"


class QueueData(BaseModel):
    """json blob with all information that has to be sent to the driver."""

    description: Optional[str]
    data: Optional[Any]
    headers: Optional[Dict[str, str]]
    url: str
    name: str
    req_type: Union[RequestType, str] = "post"
    ttl: Optional[int]


@app.get("/ping")
async def get_heartbeat():
    logger.debug("Heartbeat check")
    return "Ok"


@app.options("/queue")
async def queue_info():
    """get information on the current queue."""
    info = get_info()
    logger.debug("queue info: {}".format(vars(info)))
    return info


@app.post("/queue")
async def post_job(request: Request):
    """enqueue a new job to the queue."""
    if request.headers['content-type'].startswith('application/json'):
        item = QueueData(**await request.json())
    elif request.headers['content-type'].startswith('multipart/form-data'):
        form = await request.form()
        item = QueueData(
            headers=json.loads(form.get('headers', "")),
            url=form["url"],
            name=form["name"],
            req_type=form.get("req_type"),
            ttl=int(form.get("ttl", "0")) or None,
            data=form.get("data")
        )
    logger.debug(f"queue job: {item}")
    return enqueue_job(item)


@app.get("/queue/{job_id}")
async def get_result(job_id):
    logger.debug("getting status of queue job: {}".format(job_id))
    result = fetch_job(job_id)
    return result


@app.delete("/queue")
async def delete_queue():
    logger.debug("deleting all jobs.")
    return delete_jobs()
