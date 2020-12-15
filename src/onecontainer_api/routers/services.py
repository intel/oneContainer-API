# SPDX-License-Identifier: BSD-3-Clause
#  Copyright (c) 2020 Intel Corporation
"""Services entrypoint."""

from typing import List

from fastapi import APIRouter, Depends
import databases
import sqlite3

from onecontainer_api import crud, models, schemas, errors
from onecontainer_api.logger import logger
from onecontainer_api.routers import drivers

import re

router = APIRouter()


@router.get("/service/", response_model=List[schemas.Service],
    description="List backend services available")
async def list_services(skip: int = 0, limit: int = 100,
                        db: databases.Database = Depends(models.get_db)):
    resp = await crud.db_list(db=db, table=models.get_table("service"), skip=skip, limit=limit)
    return resp


@router.post("/service/",
    description="Register a backend service")
async def post_service(service: schemas.ServiceCreate,
                       db: databases.Database = Depends(models.get_db)):
    logger.debug(f"Create serivce with data: {service}")
    created = None
    try:
        logger.debug("Looking for available drivers for backend service")
        drivers_avail = await drivers.match_drivers(service)
        if drivers_avail:
            service.driver = f"{drivers_avail[0].name}-{drivers_avail[0].version}"
            logger.debug(f"Driver match: {service.driver}")
        created = await crud.db_create(db=db, table=models.get_table("service"),
                                       values=service.dict())
        if created and drivers_avail:
            if not drivers.is_driver_deployed(drivers_avail[0]):
                driver_deployed = drivers.deploy_driver(drivers_avail[0])
                if not driver_deployed:
                    created["driver"] = None
                    await put_service(created["id"], schemas.ServiceCreate(**created), db)
    except sqlite3.IntegrityError as exc:
        raise errors.DataException(service, getattr(service, exc.args[0].split('.')[-1]),
                                   errors.CONFLICT_ERROR)
    return created


@router.get("/service/{service_id}", response_model=schemas.Service,
    description="Get information about a backend service")
async def get_service(service_id: str, db: databases.Database = Depends(models.get_db)):
    queried = await crud.db_get(db=db, table=models.get_table("service"), obj_id=service_id)
    if queried is None:
        raise errors.DataException(schemas.Service, service_id, errors.NOTFOUND_ERROR)
    return queried


@router.get("/service/{service_id}/heartbeat",
    description="Test connection to a backend service")
async def ping_service(service_id: str, db: databases.Database = Depends(models.get_db)):
    service = await get_service(service_id, db)
    if service.driver:
        driver = await drivers.get_driver(service.driver)
        return drivers.service_stack(driver, service, "get", "/ping", sync=True)
    raise errors.ServiceException(service.id, errors.NO_DRV_ERROR, "Service has no driver assigned")


@router.put("/service/{service_id}",
    description="Update information of a backend service")
async def put_service(service_id: str, service: schemas.ServiceUpdate,
                      db: databases.Database = Depends(models.get_db)):
    updated = None
    try:
        updated = await crud.db_update(db=db, table=models.get_table("service"),
                                       values=service.dict(exclude_unset=True),
                                       obj_id=service_id)
    except sqlite3.IntegrityError as exc:
        raise errors.DataException(service, getattr(service, exc.args[0].split('.')[-1]),
                                   errors.CONFLICT_ERROR)
    if not updated:
        raise errors.DataException(service, service_id, errors.NOTFOUND_ERROR)
    return updated


@router.delete("/service/{service_id}",
    description="Remove the record of a backend service")
async def delete_service(service_id: str, db: databases.Database = Depends(models.get_db)):
    table = models.get_table('service')
    deleted = await crud.db_delete(db=db, table=table, obj_id=service_id)
    if not deleted:
        raise errors.DataException(schemas.Service, service_id, errors.NOTFOUND_ERROR)
    return deleted


@router.get("/service/{service_id}/driver", response_model=List[schemas.DriverBase],
    description="Get the driver assigned to a backend service")
async def avail_drivers(service_id: str, db: databases.Database = Depends(models.get_db)):
    """ List available drivers for a service stack

    An driver is available for a backend service by matching the driver.app with
    service.app and if driver.app_version_match applies to service.app_version.

    These drivers are identified by name and version.

    To get the driver assigned to the service, use call to GET /service/
    """
    service = await get_service(service_id, db)
    return await drivers.match_drivers(service)


@router.post("/service/{service_id}/driver", response_model=schemas.DriverBase,
    description="Assign a driver to a service")
async def assign_driver(service_id: str, driver: schemas.DriverCreate,
                        db: databases.Database = Depends(models.get_db)):
    """ Assign a driver to a service

    Stacks by default may be assigned to a driver if they have one available natively,
    this can be changes in this function.

    To get a list of available drivers for a service, execute a GET call to
    /service/{service_id}/driver
    """
    await get_service(service_id, db)
    if driver.source_type == schemas.SourceTypes.native.value:
        driver_list = await drivers.list_drivers()
        for avail_driver in driver_list:
            if avail_driver.name == driver.name:
                driver = avail_driver
                break
    if isinstance(driver, schemas.DriverCreate):
        raise errors.ServiceException(driver.name, errors.NO_DRV_ERROR, "Execute a GET to /driver for a list of native drivers")
    drivers.deploy_driver(driver)
    return driver
