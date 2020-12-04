# Getting started

This section documents the first steps on how to use oneContainer API. It is required that the oneContainer API frontend server is up and running; for installation instructions go to the [Installation section](../Readme.md#Installation)

## Verifying services are running

The oneContainer API installation creates a frontend web server, a queuing service and some optional default backend services with docker containers.

This containers will be created within a bridged virtual network named `oca_network` which has the subnet `10.5.0.0/16` and the names will start with the prefix `oca_`.

### The queuing service

To see the queuing service containers that are running, execute the following command:

```bash
docker ps --filter "label=com.docker.compose.project=async_queue"
```

There you can see the queue API, the queue dashboard which can be accessed via http by a web browser, and a Redis* server to manage queue data.

### Default backend services

By default, oneContainer API installs and registers 2 backend services.  The definition of those services are described in the `INITIAL_SERVICES` variable at the end of `config.py` file.

To see the default backend services created after oneContainer API launch, execute the following command:

```bash
docker ps --filter "label=oca_service=default_backend"
```

In this case there is a custom dlrs-pytorch-torchub service built within the oneContainer API source code, and an Apache Cassandra* service from Docker Hub*.

**Note: If you don't want to install the default backend services, run oneContainer API with the `SVC_CREATE_ON_START=0` environment variable**

**Note: The services will remain live even if oneContainer API is torn down. This will keep data persistency when you raise oneContainer API again.**

### The frontend API

oneContainer API follows the standard OpenAPI* version 3 and by default, FastAPI* uses Swagger* UI to interact with the API reference. This application can be accessed with the following URL:

`http://localhost:8000/docs`

There you can interact with the frontend API using a web browser.

If you want to use cURL to ineract with the API, we have provided a set of scripts used in this demonstration in the `demo` directory and the usage is described in the following sections.

## The management API endpoints

The management API is used to configure and read oneContainer API database to prepare it for service requests. Here is a list of useful commands you can use for the management API:

### List available services

To list the available services that can be consumed using oneContainer-api, use a `GET` call to `/service/`:

```bash
curl -X GET localhost:8000/service/ | python3 -m json.tool
```

The output looks like:

```bash
[
    {
        "description": "Builtin backend service",
        "driver": "datastax-cassandra-driver-3.24.0",
        "name": "oca_cassandra",
        "version": "v1",
        "app": "cassandra:latest",
        "app_version": "3.11.9",
        "locations": {
            "node1": "10.5.0.1:5551"
        },
        "meta": {},
        "id": "qulezawi"
    },
    {
        "description": "Builtin backend service",
        "driver": "dlrs-torchub-driver-0.1.0",
        "name": "oca_dlrs-pytorch-torchub",
        "version": "v1",
        "app": "dlrs-pytorch-torchub",
        "app_version": "0.1.0",
        "locations": {
            "node1": "10.5.0.1:5550"
        },
        "meta": {},
        "id": "sufiyopa"
    }
]
```

As seen above, the default services enabled are a single Deep Learning Inference backend (dlrs-pytorch-torchub) and a backend for Cassandra DB (cassandra). Both of the services have been launched at startup and are running at ip `10.5.0.1` on ports 5550 and 5551 respectively. Each of the services have unique ids, that need to be used with all the other calls below.

### Check service

Let's check the health status of the service `sufiyopa`

```bash
curl -X GET localhost:8000/service/sufiyopa/heartbeat | python3 -m json.tool
```

Output:

```bash
{
    "status": "ok"
}
```

The service seems to be working!

## Deep Learning API functions

This service API will use the service `sufiyopa` listed in the available services above.

### Classification models from torchub

A default backend for serving torchub models is shipped along with oneContainer-API. To interact with the model server, oneContainer-API can be used as shown below.

### Load  model

Using the `/serve` API we can load and serve the models, to load a model a payload description file is required, the format of which looks like:

```bash
{
    "path": <model_path>,
    "name": <model_name>,
    "kwargs": <{any meta args that has to be passed}>
}
```

Let's use the API to load a `resnet18` model:

```bash
curl -X POST -d @model.json localhost:8000/ai/sufiyopa/serve | python3 -m json.tool
```

Where `model.json` payload looks like:

```bash
{
    "path": "pytorch/vision:v0.6.0",
    "name": "resnet18",
    "kwargs": {"pretrained": true}
}
```

This will generate an output like:

```bash
{
    "id": "6ad1fd81-3f7e-4579-bf4a-5a7e4e249095",
    "status": "queued",
    "queue": "oca_dlrs-pytorch-torchub",
    "position": 0
}
```

This output contains an `id` field for the job which has been queued, this value can be used to query the result:

```bash
curl -X GET localhost:8000/job/6ad1fd81-3f7e-4579-bf4a-5a7e4e249095 | python3 -m json.tool
```

Output:

```bash
{
    "status": "finished",
    "queue": "oca_dlrs-pytorch-torchub",
    "position": null,
    "result": {
        "status": "ok",
        "result": "model resnet18 loading in progress"
    }
}
```

After some minutes, the model will load in the dlrs-pytorch-torchub service, then you can execute image inference as shown in the following section.

### Test model

Let's predict using the loaded model:

```bash
curl -X POST -F image_file=@cat.jpg localhost:8000/ai/sufiyopa/predict | python3 -m json.tool
```

Output:

```bash
{
    "id": "572c0648-fdef-49d9-8bdf-8546f042f8cb",
    "status": "queued",
    "queue": "oca_dlrs-pytorch-torchub",
    "position": null
}
```

Using the job id:

```bash
curl -X GET localhost:8000/job/572c0648-fdef-49d9-8bdf-8546f042f8cb | python3 -m json.tool
```

Output:

```bash
{
    "status": "finished",
    "queue": "oca_dlrs-pytorch-torchub",
    "position": null,
    "result": {
        "results": [
            {
                "status": "ok",
                "result": "indri"
            }
        ]
    }
}
```
