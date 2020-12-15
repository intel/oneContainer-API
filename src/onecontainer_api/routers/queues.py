# SPDX-License-Identifier: BSD-3-Clause
#  Copyright (c) 2020 Intel Corporation
import json
import requests

from fastapi import APIRouter
from starlette.datastructures import UploadFile
import docker

from onecontainer_api import config, errors
from onecontainer_api.logger import logger

router = APIRouter()


def raise_worker(service_name: str):
    logger.debug(f"Rising a worker for queue {service_name}")
    client = docker.from_env()
    img_name = "oca_worker"
    cont_name = f"oca_worker_{service_name}"
    cont = None
    try:
        client.images.get(img_name)
        cont = client.containers.get(cont_name)
    except docker.errors.ImageNotFound:
        logger.debug(f"Building worker image {img_name}")
        client.images.build(path="async_queue", tag=img_name, rm=True)
    except docker.errors.NotFound:
        logger.debug(f"Container {cont_name} not found")

    if cont:
        logger.debug("Worker container already up")
    else:
        logger.debug(f"Creating worker container {cont_name}")
        client.containers.run(img_name, detach=True, network=config.NETWORK_NAME, working_dir="/workspace", name=cont_name, command=f"rq worker --url redis://oca_redis:6379 {service_name}")
    # TODO: Implement queue monitoring system to remove workers on empty queues


def check_api_status():
    try:
        resp = requests.get(f'{config.QUEUE_API_URL}/ping')
        if resp.status_code != 200:
            raise errors.ServiceException(config.QUEUE_API_URL, errors.QAPI_UNREACH_ERROR, "Check service or network")
    except requests.exceptions.ConnectionError:
        raise errors.ServiceException(config.QUEUE_API_URL, errors.QAPI_UNREACH_ERROR, "Check service or network")
    return True


def queue_service(name, url, req_type, headers, data, ttl):
    req_data = {
        "name": name,
        "url": url,
        "req_type": req_type,
        "headers": headers,
        "ttl": ttl
    }
    if isinstance(data, UploadFile):
        files = {'data': (data.filename, data.file.read())}
        req_data["headers"] = json.dumps(headers)
        resp = requests.post(f"{config.QUEUE_API_URL}/queue", files=files, data=req_data)
    else:
        req_data["data"] = data
        resp = requests.post(f"{config.QUEUE_API_URL}/queue", json=req_data)
    # TODO: Execute this in a separate thread to avoid waiting
    raise_worker(name)
    return resp


# Get a job response
@router.get("/job/{job_id}",
    description="Query a job execution result")
async def get_job(job_id: str):
    try:
        resp = requests.get(f"{config.QUEUE_API_URL}/queue/{job_id}")
        if resp.status_code == 200:
            output = json.loads(resp.text)
        else:
            raise errors.ServiceException(job_id, errors.QAPI_JOB_ERROR, "Job not found")
    except requests.exceptions.ConnectionError:
        raise errors.ServiceException(config.QUEUE_API_URL, errors.QAPI_UNREACH_ERROR, "Check service or network")
    return output
