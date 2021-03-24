import os
import signal
import time

import docker

from onecontainer_api.routers import queues, services
from onecontainer_api.logger import logger
from onecontainer_api import crud, config, models, errors, schemas


def create_service(svc: dict):
    logger.debug(f"Starting service {svc['image']}")
    client = docker.from_env()
    if svc["source"] == "native":
        logger.debug("Building image locally")
        path = f"{config.BASE_DIR}/{config.BUILTIN_BACKEND_PATH}/{svc['image']}"
        client.images.build(path=path, tag=svc['image'], rm=True)
    else:
        logger.debug("Pulling image")
        client.images.pull(svc['image'])
    gpu_args = {}
    if os.path.exists("/dev/dri/renderD128"):
        gpu_args["devices"] = ["/dev/dri"]
        gpu_args["environment"] = ["QSV_DEVICE=/dev/dri/renderD128"]
    cont = client.containers.run(svc['image'], detach=True, name=svc['name'], ports=svc.get("port", None), labels={"oca_service": "default_backend"}, **gpu_args)
    logger.debug("Service started")
    return cont


async def register_service(svc: dict):
    if svc.get("driver"):
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
        svc = schemas.ServiceCreate(**data)
        id_ = await services.post_service(svc, models.get_db())
        logger.debug(f"Service registered {id_}")


def delete_queue():
    logger.debug("Stoping Queuing service")
    ret = os.system(f"cd {config.BASE_DIR}/async_queue && docker-compose kill && docker-compose rm -f")
    if ret:
        raise errors.ServiceException("Queue API", errors.QAPI_EXEC_ERROR, "Can't delete Queue API containers")
    logger.debug("Queue service down")


def delete_queue_event(sig, frame):
    delete_queue()


def start_queue():
    try:
        queues.check_api_status()
        logger.debug("Queuing service already up")
    except errors.ServiceException:
        logger.debug("Starting Queuing service")
        # TODO: Move .env.test to ./async_queue for testing environment
        ret = os.system(f"cd {config.BASE_DIR}/async_queue && docker-compose up --build --force-recreate --detach")
        if ret:
            raise errors.ServiceException("Queue API", errors.QAPI_EXEC_ERROR, "Can't create Queue API containers")
        # Wait for network to be created and avoid race conditions in testing, they have several setup/teardown calls
        time.sleep(3)
        logger.debug("Queue service up")


async def start_backends():
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
            cont = create_service(svc)
        if not list(filter(lambda x: x["name"] == svc["name"], services)):
            # TODO: check if there is an ip:port change
            await register_service(svc)
    # Allow some time for services to start
    time.sleep(5)


async def startup():
    if config.QUEUE_CREATE_ON_START:
        start_queue()
        signal.signal(signal.SIGINT, delete_queue_event)
    if config.BACKEND_CREATE_ON_START:
        await start_backends()
        # TODO: Support BACKENDS_DELETE_ON_STOP?
    logger.debug("Frontend Gateway API ready")
