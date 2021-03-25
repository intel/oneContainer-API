# SPDX-License-Identifier: BSD-3-Clause
#  Copyright (c) 2020 Intel Corporation
"""vertical onecontainer api, definitions"""
import json

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError, ValidationError
from fastapi.responses import JSONResponse

from onecontainer_api.routers import ai, db, media, services, drivers, queues
from onecontainer_api import models, errors, startup_svc

models.Base.metadata.create_all(bind=models.engine)

app = FastAPI(
    title="One Container API",
    description="A platform to support serving multiple backend microservices over a unified API",
    version="0.1.0"
)
app.include_router(ai.router, tags=["service_api"])
app.include_router(db.router, tags=["service_api"])
app.include_router(media.router, tags=["service_api"])
app.include_router(services.router, tags=["management_api"])
app.include_router(drivers.router, tags=["management_api"])
app.include_router(queues.router, tags=["service_api"])


@app.on_event("startup")
async def startup():
    await models.db.connect()
    await startup_svc.startup()


@app.on_event("shutdown")
async def shutdown():
    await models.db.disconnect()


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Validation override for request body validation errors
    """
    child = exc.args[0][0].exc
    status_msg = "Bad Request"
    if type(child) == json.decoder.JSONDecodeError:
        target = f"{child.colno}:{child.lineno}"
        status_msg = f"Wrong JSON: {child.msg} at {target}"
    elif type(child) == ValidationError:
        model = child.model.schema()['title']
        msg = child.errors()[0]['msg']
        targets = ",".join(map(str, child.errors()[0]['loc']))
        status_msg = f"{model} {msg}: {targets}"
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"endpoint": request.url.path, "status": status_msg},
    )


@app.exception_handler(errors.DataException)
async def data_exception_handler(request: Request, exc: errors.DataException):
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={
            "endpoint": request.url.path,
            "status": f"{exc.model.schema()['title']} {exc.msg}: {exc.obj_id}".strip()
        },
    )


@app.exception_handler(errors.ServiceException)
async def service_exception_handler(request: Request, exc: errors.ServiceException):
    detail = ""
    try:
        detail = json.loads(exc.detail)
    except json.decoder.JSONDecodeError:
        detail = exc.detail
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={
            "endpoint": request.url.path,
            "status": {
                "resource": exc.obj_ref,
                "message": exc.msg,
                "detail": detail
            }
        },
    )


@app.get("/")
def index():
    return {"msg": "system onecontainer api"}

