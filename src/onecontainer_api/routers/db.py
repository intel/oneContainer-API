# SPDX-License-Identifier: BSD-3-Clause
#  Copyright (c) 2020 Intel Corporation
from aiocache import Cache
from aiocache import cached
from fastapi import APIRouter, Depends
import databases
try:
    import ujson as json
except ImportError:
    import json

from onecontainer_api import models, errors, schemas
from onecontainer_api.config import cache_tte
from onecontainer_api.routers import services, drivers

router = APIRouter()


@router.get("/db/{service_id}/table",
    description="List tables available")
@cached(ttl=cache_tte, cache=Cache.MEMORY)
async def list_table(service_id: str, sync: bool = False, ttl: int = 3600, db: databases.Database = Depends(models.get_db)):
    service = await services.get_service(service_id, db)
    if service.driver:
        driver = await drivers.get_driver(service.driver)
        return drivers.service_stack(driver, service, "get", "/table", sync=sync, ttl=ttl)
    raise errors.ServiceException(service.id, errors.NO_DRV_ERROR, "Service has no driver assigned")


@router.post("/db/{service_id}/table",
    description="Create a new table")
@cached(ttl=cache_tte, cache=Cache.MEMORY)
async def post_table(service_id: str, table: schemas.Table, sync: bool = False, ttl: int = 3600,
                     db: databases.Database = Depends(models.get_db)):
    service = await services.get_service(service_id, db)
    if service.driver:
        driver = await drivers.get_driver(service.driver)
        return drivers.service_stack(driver, service, "post", "/table", data=table.dict(), sync=sync, ttl=ttl)
    raise errors.ServiceException(service.id, errors.NO_DRV_ERROR, "Service has no driver assigned")


@router.get("/db/{service_id}/table/{table_name}",
    description="List records in a table")
@cached(ttl=cache_tte, cache=Cache.MEMORY)
async def describe_table(service_id: str, table_name: str, sync: bool = False, ttl: int = 3600,
                         db: databases.Database = Depends(models.get_db)):
    service = await services.get_service(service_id, db)
    if service.driver:
        driver = await drivers.get_driver(service.driver)
        return drivers.service_stack(driver, service, "get", f"/table/{table_name}", sync=sync, ttl=ttl)
    raise errors.ServiceException(service.id, errors.NO_DRV_ERROR, "Service has no driver assigned")


@router.get("/db/{service_id}/table/{table_name}/record",
    description="Select records of a table using DQL")
@cached(ttl=cache_tte, cache=Cache.MEMORY)
async def list_records(service_id: str, table_name: str, sync: bool = False, ttl: int = 3600,
                       dql_options: str = "", db: databases.Database = Depends(models.get_db)):
    service = await services.get_service(service_id, db)
    if service.driver:
        driver = await drivers.get_driver(service.driver)
        path = f"/table/{table_name}/record"
        if dql_options:
            try:
                json.loads(dql_options)
            except json.decoder.JSONDecodeError:
                raise errors.ServiceException(dql_options, errors.DATA_ERROR, "Value is not JSON decodable")
        return drivers.service_stack(driver, service, "get", path, data={"dql": dql_options}, sync=sync, ttl=ttl)
    raise errors.ServiceException(service.id, errors.NO_DRV_ERROR, "Service has no driver assigned")


@router.post("/db/{service_id}/table/{table_name}/record",
    description="Insert a record in a table using DML")
@cached(ttl=cache_tte, cache=Cache.MEMORY)
async def create_records(service_id: str, table_name: str, dml_options: schemas.RecordDMLOptions,
                       sync: bool = False, ttl: int = 3600, db: databases.Database = Depends(models.get_db)):
    service = await services.get_service(service_id, db)
    if service.driver:
        driver = await drivers.get_driver(service.driver)
        path = f"/table/{table_name}/record"
        return drivers.service_stack(driver, service, "post", path, data=dml_options.dict(), sync=sync, ttl=ttl)
    raise errors.ServiceException(service.id, errors.NO_DRV_ERROR, "Service has no driver assigned")


@router.put("/db/{service_id}/table/{table_name}/record",
    description="Update records in a table using DML filtering")
@cached(ttl=cache_tte, cache=Cache.MEMORY)
async def update_records(service_id: str, table_name: str, dml_options: schemas.RecordDMLOptions,
                       sync: bool = False, ttl: int = 3600, db: databases.Database = Depends(models.get_db)):
    service = await services.get_service(service_id, db)
    if service.driver:
        driver = await drivers.get_driver(service.driver)
        path = f"/table/{table_name}/record"
        return drivers.service_stack(driver, service, "put", path, data=dml_options.dict(), sync=sync, ttl=ttl)
    raise errors.ServiceException(service.id, errors.NO_DRV_ERROR, "Service has no driver assigned")


@router.delete("/db/{service_id}/table/{table_name}/record",
    description="Delete records from a table using DML filtering")
@cached(ttl=cache_tte, cache=Cache.MEMORY)
async def delete_records(service_id: str, table_name: str, dml_options: schemas.RecordDMLOptions,
                       sync: bool = False, ttl: int = 3600, db: databases.Database = Depends(models.get_db)):
    service = await services.get_service(service_id, db)
    if service.driver:
        driver = await drivers.get_driver(service.driver)
        path = f"/table/{table_name}/record"
        return drivers.service_stack(driver, service, "delete", path, data=dml_options.dict(), sync=sync, ttl=ttl)
    raise errors.ServiceException(service.id, errors.NO_DRV_ERROR, "Service has no driver assigned")
