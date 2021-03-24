"""Media vertical entrypoint."""

from typing import List

from fastapi import APIRouter, Depends, File, UploadFile
import databases

from onecontainer_api import models, schemas, errors
from onecontainer_api.routers import services, drivers

import re

router = APIRouter()


@router.post("/media/{service_id}/probe",
    description="Probe a media file")
async def probe(service_id: str, input_file: schemas.InputFile, sync: bool = False, ttl: int = 3600, db: databases.Database = Depends(models.get_db)):
    service = await services.get_service(service_id, db)
    if service.driver:
        driver = await drivers.get_driver(service.driver)
        return drivers.service_stack(driver, service, "post", "/probe", data=input_file.dict(), sync=sync, ttl=ttl)
    raise errors.ServiceException(service.id, errors.NO_DRV_ERROR, "Service has no driver assigned")


@router.post("/media/{service_id}/pipeline",
    description="Create an ffmpeg pipeline")
async def transcode(service_id: str, pipeline: schemas.Pipeline, sync: bool = False, ttl: int = 3600, db: databases.Database = Depends(models.get_db)):
    service = await services.get_service(service_id, db)
    if service.driver:
        driver = await drivers.get_driver(service.driver)
        return drivers.service_stack(driver, service, "post", "/pipeline", data=pipeline.dict(), sync=sync, ttl=ttl)
    raise errors.ServiceException(service.id, errors.NO_DRV_ERROR, "Service has no driver assigned")


@router.get("/media/{service_id}/pipeline/{pipeline_id}",
    description="Get the outputs of a pipeline")
async def get_outputs(service_id: str, pipeline_id: str, sync: bool = False, ttl: int = 3600, db: databases.Database = Depends(models.get_db)):
    service = await services.get_service(service_id, db)
    if service.driver:
        driver = await drivers.get_driver(service.driver)
        return drivers.service_stack(driver, service, "get", f"/pipeline/{pipeline_id}", sync=sync, ttl=ttl)
    raise errors.ServiceException(service.id, errors.NO_DRV_ERROR, "Service has no driver assigned")