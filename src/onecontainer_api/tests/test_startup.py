import os

import docker
import pytest
import requests

import onecontainer_api

onecontainer_api.ENV_FILE = ".env.test"

from onecontainer_api import startup_svc, models, config


class TestStartup():

    @pytest.fixture
    async def setup(self):
        models.Base.metadata.create_all(bind=models.engine)
        await startup_svc.startup()

    def teardown_method(self):
        startup_svc.teardown()
        os.remove(config.DATABASE_URL.split("///")[1])

    def test_network_created(self, setup):
        client = docker.client.from_env()
        try:
            client.networks.get(config.NETWORK_NAME)
        except docker.errors.NotFound:
            pytest.fail(f"Network was not created: {config.NETWORK_NAME}")

    def test_queue_is_running(self, setup):
        resp = requests.get(config.QUEUE_API_URL+"/ping")
        assert resp.status_code == 200
        assert resp.text == '"Ok"'

    def test_redis_is_running(self, setup):
        client = docker.client.from_env()
        cont = client.containers.get("oca_redis")
        resp = cont.exec_run('bash -c "redis-cli info | grep used_memory:"')
        assert resp.exit_code == 0
        assert resp.output.decode().split(":")[0] == "used_memory"

    def test_backend_services(self, setup):
        client = docker.client.from_env()
        for svc in config.INITIAL_SERVICES:
            svc["name"] = f"oca_{svc['image']}"
            if ":" in svc["name"]:
                svc["name"] = svc["name"].split(":")[0]
            cont = client.containers.get(svc["name"])
            assert cont.status == 'running'
