# SPDX-License-Identifier: BSD-3-Clause
#  Copyright (c) 2020 Intel Corporation
import json
import os

import onecontainer_api

onecontainer_api.ENV_FILE = ".env.test"

from onecontainer_api import config, schemas
from onecontainer_api.routers import drivers

DRIVERS = []

for name_ver in ["datastax-cassandra-driver-3_24_0", "dlrs-torchub-driver-0_1_0"]:
    with open(f"{config.NATIVE_PATH}/{name_ver}/metadata.json", "r") as driver_file:
        driver_info = json.load(driver_file)
        driver_info["source_type"] = schemas.SourceTypes.native.value
        DRIVERS.append(schemas.DriverBase(**driver_info))


class TestDrivers():

    def setup_method(self):
        for driver in DRIVERS:
            drivers.deploy_driver(driver)

    def teardown_method(self):
        for driver in DRIVERS:
            cont = drivers.get_driver_container(driver)
            if cont.status == 'running':
                cont.kill()

    def test_drivers_deployment(self):
        for driver in DRIVERS[1:]:
            assert drivers.is_driver_deployed(driver)
            cont = drivers.get_driver_container(driver)
            assert cont.status == 'running'

    def test_drivers_deployment_port(self):
        for driver in DRIVERS[1:]:
            assert drivers.is_driver_deployed(driver)
            cont = drivers.get_driver_container(driver)
            assert cont.attrs['NetworkSettings']['Ports'] == {f'{config.DRIVER_PORT}/tcp': None}

    def test_drivers_deployment_network(self):
        for driver in DRIVERS[1:]:
            assert drivers.is_driver_deployed(driver)
            cont = drivers.get_driver_container(driver)
            assert list(cont.attrs['NetworkSettings']['Networks'].keys())[0] == config.NETWORK_NAME

    def test_driver_redeploy(self):
        driver = DRIVERS[-1]
        cont = drivers.get_driver_container(driver)
        cont.kill()
        assert drivers.is_driver_deployed(driver)
