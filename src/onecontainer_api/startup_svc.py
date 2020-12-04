import os
import signal

import docker

from onecontainer_api.routers import queues, services
from onecontainer_api.logger import logger
from onecontainer_api import crud, config, models, errors, schemas


def create_service(svc: dict):
    logger.debug(f"Starting service {svc['image']}")
    client = docker.from_env()
    if svc["source"] == "native":
        logger.debug("Building image locally")
        path = f"{config.BUILTIN_BACKEND_PATH}/{svc['image']}"
        client.images.build(path=path, tag=svc['image'], rm=True)
    else:
        logger.debug("Pulling image")
        client.images.pull(svc['image'])
    cont = client.containers.run(svc['image'], detach=True, name=svc['name'], ports=svc["port"], labels={"oca_service": "default_backend"})
    logger.debug("Service started")
    return cont


async def register_service(svc: dict):
    logger.debug(f"Registering service {svc['image']}")
    data = {
        "name": svc["name"],
        "description": "Builtin backend service",
        "version": "v1",
        "app": svc["image"],
        "app_version": svc["version"],
        "driver": svc["driver"],
        "scope": svc["scope"],
        "locations": {
            "node1": f"{config.NETWORK_GATEWAY}:{list(svc['port'].values())[0]}"
        },
        "meta": svc.get("meta", {})
    }
    # id_ = await crud.db_create(models.get_db(), models.get_table("service"), data)
    svc = schemas.ServiceCreate(**data)
    id_ = await services.post_service(svc, models.get_db())
    logger.debug(f"Service registered {id_}")


def teardown():
    logger.debug("Stoping Queuing service")
    os.system("cd async_queue && docker-compose kill && docker-compose rm -f")
    logger.debug("Queue service down")
    # TODO: check init_services.DELETE_ON_STOP


def sigint_event(sig, frame):
    teardown()


async def startup():
    try:
        queues.check_api_status()
        logger.debug("Queuing service already up")
    except errors.ServiceException:
        logger.debug("Starting Queuing service")
        # TODO: Move .env.test to ./async_queue for testing environment
        os.system("cd async_queue && docker-compose up --build --force-recreate --detach")
        logger.debug("Queue service up")
    if config.SVC_CREATE_ON_START:
        services = await crud.db_list(models.get_db(), models.get_table("service"))
        client = docker.from_env()
        for svc in config.INITIAL_SERVICES:
            logger.debug(f"Checking service {svc['image']}")
            svc["name"] = f"oca_{svc['image']}"
            if ":" in svc["name"]:
                svc["name"] = svc["name"].split(":")[0]
            try:
                cont = client.containers.get(svc["name"])
                if cont.status == 'exited':
                    cont.start()
            except docker.errors.NotFound:
                create_service(svc)
            if not list(filter(lambda x: x["name"] == svc["name"], services)):
                # TODO: check if there is an ip:port change
                await register_service(svc)
    signal.signal(signal.SIGINT, sigint_event)
    logger.debug("Frontend Gateway API ready")
