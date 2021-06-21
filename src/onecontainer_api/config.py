# SPDX-License-Identifier: BSD-3-Clause
#  Copyright (c) 2020 Intel Corporation
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

import onecontainer_api

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(BASE_DIR, onecontainer_api.ENV_FILE))
sys.path.append(BASE_DIR)

# cache time to expire
cache_tte = int(os.environ.get("CACHE_TTE", 3600)) 

# General config

ID_SIZE = 8

# Docker management config

BUILTIN_BACKEND_PATH = "backends"

NETWORK_NAME = os.environ.get("DOCKER_NETWORK", "oca_network")
NETWORK_GATEWAY = os.environ.get("DOCKER_NETWORK_GATEWAY", "10.5.0.1")

# Driver related config

PLUGIN_PATH = f"{Path.home()}/.onecontainer-api/drivers"
NATIVE_PATH = f"{BASE_DIR}/drivers"

if not os.path.exists(PLUGIN_PATH):
    os.makedirs(PLUGIN_PATH)

DRIVER_PORT = 5055

# Queue Service config

QUEUE_API_URL = "http://127.0.0.1:5057"

# Database related config

SQLITE_PROTOCOL = "sqlite"
DB_NAME = os.environ.get("DB_NAME", "oca_db")

DATABASE_PROTOCOL = SQLITE_PROTOCOL
DATABASE_URL = f"{DATABASE_PROTOCOL}:///./{DB_NAME}.db"



# Service related config

JSON = 'json'
YAML = 'yaml'
RAW = 'raw'

INPUT_FORMATS = [
    JSON,
    YAML,
    RAW,
]

DEFAULT_INPUT_FORMAT = JSON

DEFAULT_META = {
    'db': {
        'cassandra': {
            'keyspace': 'oca_ks',
            'replication': {'class': 'SimpleStrategy', 'replication_factor': 1}
        }
    }
}


# Startup config
BACKEND_CREATE_ON_START = bool(os.environ.get("BACKEND_CREATE_ON_START", True))
QUEUE_CREATE_ON_START = bool(os.environ.get("QUEUE_CREATE_ON_START", True))
BACKEND_NETWORK_GATEWAY = os.environ.get("DOCKER_BACKEND_GATEWAY", "172.17.0.1")

# We want to keep using the services created
SVC_DELETE_ON_STOP = False

INITIAL_SERVICES = [
    {
        "image": "cassandra:latest",
        "version": "3.11.9",
        "source": "dockerhub",
        "port": {
            "9042/tcp": 5551
        },
        "scope": "db",
        "driver": "datastax-cassandra-driver-3.24.0"
    }, {
        "image": "dlrs-pytorch-torchub",
        "version": "0.1.0",
        "source": "native",
        "port": {
            "5550/tcp": 5550
        },
        "scope": "ai",
        "driver": "dlrs-torchub-driver-0.1.0"
    }, {
        "image": "mers-ffmpeg",
        "version": "0.1.0",
        "source": "native",
        "port": {
            "5552/tcp": 5552
        },
        "scope": "media",
        "driver": "mers-ffmpeg-driver-0.1.0"
    }, {
        "image": "web-rtmp",
        "version": "0.1.0",
        "source": "native",
        "port": {
            "80/tcp": 5553,
            "1935/tcp": 5554
        }
    }
]
