# SPDX-License-Identifier: BSD-3-Clause
#  Copyright (c) 2020 Intel Corporation

"""drivers entrypoint."""

from typing import List

from fastapi import APIRouter, Depends
from starlette.datastructures import UploadFile
import databases
import docker
import requests

from onecontainer_api import models, schemas, config, errors
from onecontainer_api.routers import queues
from onecontainer_api.logger import logger

import json
import os
import time
from packaging import version

router = APIRouter()


def match_version(ver: str, match: str):
    operator = match[:2]
    target = match[2:]
    if operator == "==" and ver == target:
        return True
    elif operator == "<=" and version.parse(ver) <= version.parse(target):
        return True
    elif operator == ">=" and version.parse(ver) >= version.parse(target):
        return True
    return False


async def match_drivers(service: schemas.ServiceBase):
    matched_drivers = []
    drivers = await list_drivers()
    logger.debug(f"Found {len(drivers)} drivers installed")
    logger.debug(f"Matching driver for {service.app} {service.app_version}")
    for driver in drivers:
        if driver.app == service.app and match_version(service.app_version,
                                                       driver.app_version_match):
            matched_drivers.append(driver)
    return matched_drivers


def service_stack(driver: schemas.DriverBase, service: schemas.Service, method: str,
                  path: str, data: dict = {}, sync: bool = False, ttl: int = 3600):
    output = ""
    hosts = list(service.locations.values())
    meta = service.meta
    if not meta:
        meta = config.DEFAULT_META.get(driver.scope, {}).get(driver.app)
    headers = {"Metadata": json.dumps(meta), "Hosts": ",".join(hosts)}
    try:
        ip = get_driver_ip(driver)
    except errors.ServiceException as exc:
        drv_create = {
            "name": driver.name,
            "source_type": driver.source_type,
            "location": driver.location
        }
        exc.detail += f"Redeploy driver by executing a POST call to /service/{service.id}/driver with data: {json.dumps(drv_create)}"
        raise exc
    url = f"http://{ip}:{config.DRIVER_PORT}{path}"
    if sync:
        logger.debug(f"Executing {method.upper()} {url} with headers: {headers} and data: {data}")
        try:
            kwargs = {
                "headers": headers,
                "proxies": {"http": None},
                "json": None,
                "params": None,
                "files": None
            }
            if method == "get":
                kwargs["params"] = data
            else:
                if isinstance(data, dict):
                    kwargs["json"] = data
                if isinstance(data, UploadFile):
                    kwargs["files"] = {'img': (data.filename, data.file.read())}
            resp = requests.request(method.upper(), url, **kwargs)
        except requests.exceptions.ConnectionError:
            raise errors.ServiceException(driver.name, errors.DRV_UNREACH_ERROR, f"No route to {url}")
        if resp.status_code == 200:
            try:
                output = json.loads(resp.text)
            except json.decoder.JSONDecodeError:
                raise errors.ServiceException(url, errors.DRV_IMPL_ERROR, f'Ouptut is not JSON deserializable: "{resp.text}"')
        else:
            raise errors.ServiceException(url, errors.DRV_EXEC_ERROR, resp.text)
    else:
        queues.check_api_status()
        resp = queues.queue_service(service.name, url, method, headers, data, ttl)
        if resp.status_code == 200:
            output = json.loads(resp.text)
        else:
            raise errors.ServiceException("", errors.QAPI_EXEC_ERROR, resp.text)
    return output


def get_driver_container(driver: schemas.DriverBase):
    cont = None
    cont_name = f"{driver.name}-{driver.version}"
    client = docker.from_env()
    try:
        client.images.get(f"{driver.name}:{driver.version}")
        cont = client.containers.get(cont_name)
    except docker.errors.ImageNotFound:
        raise errors.ServiceException(cont_name, errors.NO_DRV_ERROR, "Image doesn't exist.")
    except docker.errors.NotFound:
        raise errors.ServiceException(cont_name, errors.NO_DRV_ERROR, "Container doesn't exist.")
    if cont.status == 'exited':
        logger.debug(f"Container {cont_name} is not running. Running starting command")
        cont.start()
        time.sleep(3)
        cont = client.containers.get(cont_name)
    return cont


def get_driver_ip(driver: schemas.DriverBase):
    cont = get_driver_container(driver)
    return cont.attrs["NetworkSettings"]["Networks"][config.NETWORK_NAME]["IPAddress"]


def is_driver_deployed(driver: schemas.DriverBase):
    try:
        get_driver_container(driver)
    except errors.ServiceException:
        return False
    return True


def deploy_driver(driver: schemas.DriverBase):
    client = docker.from_env()
    cont_name = f"{driver.name}-{driver.version}"
    img_name = f"{driver.name}:{driver.version}"
    logger.debug(f"Deploying driver: {cont_name}")
    if driver.source_type == schemas.SourceTypes.native.value:
        path = f"{config.NATIVE_PATH}/{cont_name}".replace(".", "_")
    else:
        # TODO: Download plugin first
        path = f"{config.PLUGIN_PATH}/{cont_name}".replace(".", "_")
    client.images.build(path=path, tag=img_name, rm=True)
    try:
        cont = get_driver_container(driver)
        logger.debug(f"Previuos driver {cont_name} found. Deleting old one")
        cont.stop()
        cont.remove()
    except errors.ServiceException:
        logger.debug(f"No previuos driver {cont_name} found")
    client.containers.run(img_name, detach=True, network=config.NETWORK_NAME, name=cont_name)
    return True


@router.get("/driver/", response_model=List[schemas.DriverBase],
    description="Get drivers available")
async def list_drivers():
    """List drivers

    A backend stack service may be accessed through different clients,
    this function lists available drivers, including native drivers (The
    ones that comes with onecontainer-api source code) and plugin drivers.

    Plugin drivers are manually created using the call to POST /driver

    The `drivers/` directory is used to store onecontainer-api native drivers,
    bellow this path, directories are named with the following format:
    {driver.name}-{driver.version}

    The `~/.onecontainer-api/drivers/` directory is used to store plugin drivers.

    Inside of each driver folder, there should be a metadata.json file which
    will be used to deserialize data and create a schemas.DriverBase object.
    """
    drivers = []
    for source_type, path in zip([schemas.SourceTypes.native.value,
                                  schemas.SourceTypes.plugin.value],
                                 [config.NATIVE_PATH, config.PLUGIN_PATH]):
        for name_ver in os.listdir(path):
            if "metadata.json" in os.listdir(f"{path}/{name_ver}"):
                with open(f"{path}/{name_ver}/metadata.json", "r") as driver_file:
                    driver_info = json.load(driver_file)
                    driver_info["source_type"] = source_type
                    drivers.append(schemas.DriverBase(**driver_info))
    return drivers


@router.get("/driver/{drv_name_ver}", response_model=schemas.DriverBase,
    description="Get driver information")
async def get_driver(drv_name_ver: str):
    """Get driver by name-version

    Since this objects are not stored in DB, they don't have an Id, they are
    referenced by name and version using the following format:
    {driver.name}-{driver.version}
    """
    ver = drv_name_ver.split("-")[-1]
    name = drv_name_ver[:-len(ver)-1]
    drivers = await list_drivers()
    for driver in drivers:
        if driver.name == name and driver.version == ver:
            return driver
    return None


@router.post("/driver/", response_model=schemas.DriverBase,
    description="Add a plugin driver")
async def post_driver(driver: schemas.DriverCreate,
                      db: databases.Database = Depends(models.get_db)):
    """Create a plugin driver

    Use this function add a driver to onecontainer-api to be used to comunicate with a
    backend service. Go to API reference for understanding the input model.
    """
    # TODO: Implement this
    return driver
