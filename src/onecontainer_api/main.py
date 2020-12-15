# SPDX-License-Identifier: BSD-3-Clause
#  Copyright (c) 2020 Intel Corporation
"""vertical onecontainer api, cli entrypoint."""

import argparse

import uvicorn

from onecontainer_api.frontend import app


def cli():
    parser = argparse.ArgumentParser("one container api.")
    parser.add_argument("launch", help="launch one_container_api")
    args = parser.parse_args()
    if args.launch:
        uvicorn.run(app)
