# SPDX-License-Identifier: BSD-3-Clause
#  Copyright (c) 2020 Intel Corporation
#!usr/bin/env python

import base64
import io
import json

import sanic

from client import Client

app = sanic.Sanic("ai-client-driver")


def _decode_headers(req):
    metadata = json.loads(req.headers.get("Metadata", "{}"))
    hosts = req.headers.get("Hosts", "").split(",")
    return metadata, hosts


def _get_client(req):
    try:
        metadata, hosts = _decode_headers(req)
    except json.decoder.JSONDecodeError:
        return None, "Metadata is not JSON object"
    if hosts[0] == "":
        return None, "Missing hosts"
    if ":" not in hosts[0]:
        return None, f"Missing port in host {hosts[0]}"
    ip = hosts[0].split(":")[0]
    port = hosts[0].split(":")[1]
    client = Client(ip, port)
    return client, None


@app.route("/ping", methods=["GET"])
async def ping(request):
    """driver health check."""
    client, error = _get_client(request)
    raise NotImplementedError


@app.route("/usage", methods=["GET"])
async def usage(request):
    """usage banner."""
    client, error = _get_client(request)
    raise NotImplementedError


@app.route("/serve", methods=["POST"])
async def serve(request):
    """load and init model"""
    client, error = _get_client(request)
    raise NotImplementedError


@app.route("/predict", methods=["POST"])
async def predict(request):
    """predict - classify input sent."""
    client, error = _get_client(request)
    raise NotImplementedError


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5055)
