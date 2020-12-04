"""queue implementation."""
import os
from types import SimpleNamespace as SN

from starlette.datastructures import UploadFile

import requests
from redis import Redis
from rq import Queue
from rq.job import Job
from rq.job import Retry

from logger import logger


REDIS_HOST = os.environ.get("REDISHOST", "oca_redis")
REDIS_PORT = int(os.environ.get("REDISPORT", "6379"))
CONN = Redis(host=REDIS_HOST, port=REDIS_PORT)


def fetch_job(job_id):
    """given an id, fetch the job."""
    job = Job.fetch(job_id, connection=CONN)
    resp = {
        "status": job.get_status(),
        "queue": job.origin,
        "position": job.get_position(),
        "result": job.result,
    }
    return resp


def worker(**kwargs):
    """post job to queue, all drivers behind url and port."""
    logger.debug("kwargs passed to worker: {}".format(kwargs))
    kwargs.update({
        "proxies": {"http": None},
        "json": None,
        "params": None,
        "files": None
    })
    data = kwargs.pop("data")
    if kwargs["method"] == "get":
        kwargs["params"] = data
    else:
        if isinstance(data, UploadFile):
            kwargs["files"] = {'img': (data.filename, data.file.read())}
        else:
            kwargs["json"] = data
    return requests.request(**kwargs).json()


def enqueue_job(item):
    """add job to queue."""
    logger.debug("job enqueued with worker req type: {}".format(item.req_type))
    sq = Queue(item.name, connection=CONN)
    job = sq.enqueue(
        worker,
        kwargs={
            "data": item.data,
            "method": item.req_type,
            "url": item.url,
            "headers": item.headers,
        },
        result_ttl=item.ttl if item.ttl else 18600,  # a day
        retry=Retry(max=3),
    )
    return {
        "id": job.get_id(),
        "status": job.get_status(),
        "queue": item.name,
        "position": job.get_position(),
    }


def delete_jobs():
    """delete all jobs."""
    # TODO: delete from all queues
    sq = Queue("", connection=CONN)
    return sq.delete(delete_jobs=True)


def get_info():
    """queue info - size, job ids."""
    # TODO: use a specific queue
    info = SN()
    info.name = "queue_info"
    sq = Queue("", connection=CONN)
    info.size = len(sq)
    info.job_ids = sq.job_ids
    return vars(info)
