import os

import docker

from fastapi.testclient import TestClient

from onecontainer_api import models, schemas, config, startup_svc
from onecontainer_api.frontend import app
from onecontainer_api.routers import drivers


class TestServices():

    def setup_method(self):
        models.Base.metadata.create_all(bind=models.engine)

    def teardown_method(self):
        os.remove(config.DATABASE_URL.split("///")[1])

    def test_list_service(self):
        with TestClient(app) as client:
            response = client.get("/service")
            assert response.status_code == 200
            assert len(response.json()) == len([x for x in config.INITIAL_SERVICES if "driver" in x])

    def test_get_service(self):
        with TestClient(app) as client:
            response = client.get("/service")
            assert response.status_code == 200
            data = response.json()[0]
            svc = schemas.Service(**data)
            response = client.get(f"/service/{data['id']}")
            assert response.status_code == 200, response.text
            assert response.json() == svc.dict()

    def test_post_service(self):
        with TestClient(app) as client:
            response = client.get("/service")
            data = response.json()[1]
            data.pop("id")
            data["name"] = data["name"]+"_test"
            svc = schemas.ServiceCreate(**data)
            response = client.post("/service/",
                json=svc.dict()
            )
            assert response.status_code == 200, response.text
            data["id"] = response.json()
            assert len(data["id"]) == config.ID_SIZE

            response = client.get(f"/service/{data['id']}")
            assert response.status_code == 200, response.text
            assert response.json() == data
    
    def test_update_service(self):
        with TestClient(app) as client:
            response = client.get("/service")
            data = response.json()[1]
            svc_id = data.pop("id")
            data["name"] = data["name"]+"_test"
            svc = schemas.ServiceUpdate(name=data["name"])
            response = client.put(f"/service/{svc_id}",
                json=svc.dict(exclude_unset=True)
            )
            assert response.status_code == 200, response.json()

            response = client.get(f"/service/{svc_id}")
            assert response.status_code == 200, response.text
            data["id"] = svc_id
            assert response.json() == data
    
    def test_delete_service(self):
        with TestClient(app) as client:
            response = client.get("/service")
            data = response.json()[1]
            svc_id = data.pop("id")
            response = client.delete(f"/service/{svc_id}")
            assert response.status_code == 200, response.json()

            response = client.get(f"/service/{svc_id}")
            assert response.status_code == 400, response.text
            assert response.json() == {"endpoint": f"/service/{svc_id}", "status": f"Service not found: {svc_id}"}

    def test_service_driver_deploy(self):
        with TestClient(app) as client:
            response = client.get("/service")
            data = response.json()[1]
            data.pop("id")
            data["name"] = data["name"]+"_test"
            svc = schemas.ServiceCreate(**data)
            response = client.post("/service/",
                json=svc.dict()
            )
            assert response.status_code == 200, response.text
            data["id"] = response.json()
            response = client.get(f"/service/{data['id']}/driver")
            assert response.status_code == 200, response.text
            driver = schemas.DriverBase(**response.json()[0])
            cont_name = f"{driver.name}-{driver.version}"
            docker_client = docker.from_env()
            cont = docker_client.containers.get(cont_name)
            assert cont.status == "running"
            cont.kill()
    
    def test_service_driver_redeploy(self):
        with TestClient(app) as client:
            response = client.get("/service")
            data = response.json()[1]
            data.pop("id")
            data["name"] = data["name"]+"_test"
            svc = schemas.ServiceCreate(**data)
            response = client.post("/service/",
                json=svc.dict()
            )
            assert response.status_code == 200, response.text
            data["id"] = response.json()
            response = client.get(f"/service/{data['id']}/driver")
            assert response.status_code == 200, response.text
            driver = schemas.DriverBase(**response.json()[0])
            cont_name = f"{driver.name}-{driver.version}"
            docker_client = docker.from_env()
            cont = docker_client.containers.get(cont_name)
            assert cont.status == "running"
            cont.kill()
            cont = docker_client.containers.get(cont_name)
            assert cont.status == "exited"
            response = client.post(f"/service/{data['id']}/driver",
                json={
                    "name": driver.name,
                    "source_type": schemas.SourceTypes.native.value
                }
            )
            cont = docker_client.containers.get(cont_name)
            assert cont.status == "running"
