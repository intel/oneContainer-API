# oneContainer API

A platform to enable unified APIs with service backends for multiple verticals.

<img src=images/oneca-arch0.2.0.jpg width=700 height=600/>


## Installation

The requirements for onecontainer-api are the following:

 * Python >= 3.7
 * poetry >= 0.12

### Development environment

To install the dependencies, run the following commands:

```bash
$ poetry install
```

Using the virtual environment created by poetry will make all dependencies available.  To start this virtual environment execute the following command:

```bash
$ poetry shell
```

To start onecontainer_api, from CLI (oca), run the following command:

```bash
$ cd oneContainer-API/src/onecontainer_api
$ poetry run oca launch
```

This will start a uvicorn web server on port 8000. Execute `uvicorn --help` for a full list of parameters available.

## Documentation

### Why?

A lot of services are built and deployed as docker containers, the question or difficulty
is how to connect the last mile, how to expose these services to the ISV or user.

<img src=images/scope1.png width=400 height=200/>

This is where `oneContainerAPI` comes in, by providing a unified interface for ISVs to deploy and consume services.

<img src=images/scope2.png width=400 height=200/>

### Features

- Microservice architecture
- Unified APIs for service backends from various segments like AI, Media and DB
- Async queuing for compute / IO intensive requests
- Backends - Cassandra DB, DLRS PyTorch with Torchub
- Self-documentation


### Architecture

A 10,000 ft view of the architecture of oneContainerAPI:

<img src=images/onecntrAPI.png width=600 height=400/>

Various components that form the architecture are described below:

### Frontend / External API with service Queue

An `ISV` uses the frontend API to deploy services for their users to consume. The API is
divided in 2 sections: Management API and Service API. The Management API is used to
enable backend services to be able to be consumed by the Service API. The Service APIs are used by end users.

#### M-API and S-API

The API is divided in 2 sections: Management API and Service API.

The **Management API** or M-API is used to enable the backend services to be able to be consumed by the **Service API** or S-API. The Service API is used to consume and access deployed backends.

##### Example of management APIs

* List `services` and `drivers`:

<img src=images/mgmt_api.png width=300 height=300//>

##### Example of service APIs

* List `service functions` for AI and DB:

<img src=images/svc_api.png width=300 height=300//>

### Backend and drivers

#### Register a backend stack service

A `backend` is any containerized service, for example dlrs_pytorch, dbrs_cassandra etc. A
`driver` is any client that is designed as a REST service, that is used to consume a
`backend` service.

<img src=images/dlrs-torch-backend.png width=200 height=300/>

Infrastructure management is not in the scope of onecontainer-api; this means that onecontainer-api app is not aware of any backend services unless they are manually recorded in a onecontainer-api database.

To create a record of every backend service you want to consume, you need to execute a POST call to /service/ endpoint with the data required.

To review the API reference, go to docs/api-reference

#### Register a plugin client driver

When creating a record for a backend service, it will assign a driver if there is one available that can be used to consume the stack.

There is a list of drivers available that is created with onecontainer-api installation, these are what we call `native` drivers.

Onecontainer-api also supports custom driver clients, these are what we call `plugin` drivers.

A supported plugin driver complies with the following specification:

* It must contain a `metadata.json` to deserialize a `DriverBase` object. (Please refer to API reference for object formats).
* It shall be deployed in a way supported by onecontainer-api, the only method available is using `Dockerfiles`.

If there is no driver available, you will need to create one and then assign it to a stack. The folder `templates/` contains the templates to create drivers for each function scope.

### Service workflow

How a `request` is sent to a queue and how the queue worker processes the `request` and returns it:

<img src=images/workfow2.png width=700 height=450/>

### Self documentation

Onecontainer-api uses the [OpenAPI](https://www.openapis.org/) standard to generate documentation for APIs defined using the [FastAPI](https://fastapi.tiangolo.com/) framework. The updated API docs can be found at `docs/api-reference` and  can be rendered using any OpenAPI frontends. When the application is running, the API docs can be viewed at `host:port/docs` as well.

## Getting started

For a *Getting started* tutorial, view the [Readme.md](demo/Readme.md) in the `demo` directory.
