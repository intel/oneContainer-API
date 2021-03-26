# SPDX-License-Identifier: BSD-3-Clause
#  Copyright (c) 2020 Intel Corporation
import os

import docker
import pytest
import requests

from onecontainer_api import startup_svc, config


class TestStartup():

    def setup_method(self):
        startup_svc.start_queue()

    def teardown_method(self):
        startup_svc.delete_queue()

    def test_network_created(self):
        client = docker.client.from_env()
        try:
            client.networks.get(config.NETWORK_NAME)
        except docker.errors.NotFound:
            pytest.fail(f"Network was not created: {config.NETWORK_NAME}")

    def test_queue_is_running(self):
        resp = requests.get(config.QUEUE_API_URL+"/ping")
        assert resp.status_code == 200
        assert resp.text == '"Ok"'

    def test_redis_is_running(self):
        client = docker.client.from_env()
        cont = client.containers.get("oca_redis")
        resp = cont.exec_run('bash -c "redis-cli info | grep used_memory:"')
        assert resp.exit_code == 0
        assert resp.output.decode().split(":")[0] == "used_memory"

    def test_backend_services(self):
        client = docker.client.from_env()
        for svc in config.INITIAL_SERVICES:
            svc["name"] = f"oca_{svc['image']}"
            if ":" in svc["name"]:
                svc["name"] = svc["name"].split(":")[0]
            cont = client.containers.get(svc["name"])
            assert cont.status == 'running'
