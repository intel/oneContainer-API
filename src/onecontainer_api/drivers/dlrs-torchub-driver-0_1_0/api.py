#!usr/bin/env python

import base64
import io
import json

import sanic

from client import Client as DLRS_Client
from logger import logger

app = sanic.Sanic("dlrs-torchub-classify-client")


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
    client = DLRS_Client(ip, port)
    return client, None


@app.route("/ping", methods=["GET"])
async def ping(request):
    """driver health check."""
    client, error = get_client(request)
    if error:
        return error, 400
    return sanic.response.text(json.dumps(await client.ping()))


@app.route("/usage", methods=["GET"])
async def usage(request):
    """usage banner."""
    logger.debug("client api - usage")
    client, error = get_client(request)
    if error:
        return error, 400
    return sanic.response.text(await client.usage())


@app.route("/predict", methods=["POST"])
async def predict(request):
    """predict - classify image sent."""
    data = request.files
    results = []
    logger.debug("client api - predict")
    logger.debug(f"files: {data}")
    client, error = get_client(request)
    if error:
        return error, 400
    if data.get("img", None):
        for img in data["img"]:
            b64_img = img.body
            # img_bytes = base64.b64decode(b64_img)
            results.append(json.loads(await client.predict(b64_img)))
        return sanic.response.json({"results": results})
    return sanic.response.json(
        {"status": "not image file in request data with key `img`"}
    )


@app.route("/serve", methods=["POST"])
async def serve(request):
    """load and init model"""
    logger.debug("client api - serve")
    client, error = get_client(request)
    if error:
        return error, 400
    y_hat = client.serve(request.json)
    return sanic.response.text(await y_hat)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5055, workers=4)
