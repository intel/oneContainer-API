import os

from fastapi.testclient import TestClient

from onecontainer_api import models, schemas, config, startup_svc
from onecontainer_api.frontend import app

class TestAI():

    def setup_method(self):
        models.Base.metadata.create_all(bind=models.engine)

    def teardown_method(self):
        os.remove(config.DATABASE_URL.split("///")[1])

    def test_usage(self):
        with TestClient(app) as client:
            response = client.get("/service")
            data = list(filter(lambda x: x['app'] == 'dlrs-pytorch-torchub', response.json()))[0]
            svc_id = data.pop("id")
            response = client.get(f"/ai/{svc_id}/usage")
            assert response.status_code == 200, response.text

    def test_serve_missing_body(self):
        with TestClient(app) as client:
            response = client.get("/service")
            data = list(filter(lambda x: x['app'] == 'dlrs-pytorch-torchub', response.json()))[0]
            svc_id = data.pop("id")
            response = client.post(f"/ai/{svc_id}/serve")
            assert response.status_code == 400, response.text
            assert response.json() == {"endpoint": f"/ai/{svc_id}/serve", "status": "Bad Request"}