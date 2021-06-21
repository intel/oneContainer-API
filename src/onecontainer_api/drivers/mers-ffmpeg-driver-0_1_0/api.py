# SPDX-License-Identifier: BSD-3-Clause
#  Copyright (c) 2020 Intel Corporation
#!usr/bin/env python

import base64
import io
import json

import sanic
from sanic import response

from client import Client as MERS_Client
from logger import logger

app = sanic.Sanic("mers-ffmpeg-client")


def decode_headers(req):
    metadata = json.loads(req.headers.get('Metadata', '{}'))
    hosts = req.headers.get('Hosts', '').split(",")
    return metadata, hosts


def get_client(req):
    try:
        metadata, hosts = decode_headers(req)
    except json.decoder.JSONDecodeError:
        return None, "Metadata is not JSON object"
    if hosts[0] == '':
        return None, "Missing hosts"
    if not ":" in hosts[0]:
        return None, f"Missing port in host {hosts[0]}"
    ip = hosts[0].split(":")[0]
    port = hosts[0].split(":")[1]
    client = MERS_Client(ip, port)
    return client, None


@app.route("/ping", methods=["GET"])
async def ping(request):
    """driver health check."""
    client, error = get_client(request)
    if error:
        return error, 400
    resp, status = await client.ping()
    if status == 500:
        status = 400
    return response.json(resp, status=status)


@app.route("/probe", methods=["POST"])
async def probe(request):
    """probes media file"""
    logger.debug("client api - probe")
    client, error = get_client(request)
    if error:
        return error, 400
    resp, status = await client.probe(request.json)
    if status == 500:
        status = 400
    return response.json(resp, status=status)

@app.route("/pipeline", methods=["POST"])
async def transcode(request):
    """executes a transcoding pipeline job."""
    logger.debug("client api - transcode")
    client, error = get_client(request)
    if error:
        return error, 400
    resp, status = await client.transcode(request.json)
    if status == 500:
        status = 400
    return response.json(resp, status=status)


@app.route("/pipeline/<pipeline_id:string>", methods=["GET"])
async def get_outputs(request, pipeline_id):
    """gets the outputs a transcoding pipeline job."""
    client, error = get_client(request)
    if error:
        return error, 400
    resp, status = await client.get_outputs(pipeline_id)
    if status == 500:
        status = 400
    return response.json(resp, status=status)


@app.route("/pipeline/<pipeline_id:string>", methods=["DELETE"])
async def stop_pipeline(request, pipeline_id):
    """stops a transcoding pipeline job."""
    client, error = get_client(request)
    if error:
        return error, 400
    resp, status = await client.stop_pipeline(pipeline_id)
    if status == 500:
        status = 400
    return response.json(resp, status=status)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5055, workers=4)
