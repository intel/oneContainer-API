#!usr/bin/env python

import io

import quart
from quart_cors import cors

from client import Client as DLRS_Client
from logger import logger

app = quart.Quart(__name__)
cors(app)


@app.route("/ping", method=["GET"])
def ping():
    """driver health check."""
    client = DLRS_Client(
        files["ip"].read().decode("utf-8"), files["port"].read().decode("utf-8")
    )
    return client.ping()


@app.route("/usage", methods=["GET"])
async def usage():
    """usage banner."""
    logger.debug("client api - usage")
    files = await quart.request.files
    client = DLRS_Client(
        files["ip"].read().decode("utf-8"), files["port"].read().decode("utf-8")
    )
    return quart.jsonify(await client.usage())


@app.route("/predict", methods=["POST"])
async def predict():
    """predict - classify image sent."""
    logger.debug("client api - predict")
    files = await quart.request.files
    if files.get("img", None):
        client = DLRS_Client(
            files["ip"].read().decode("utf-8"), files["port"].read().decode("utf-8")
        )
        y_hat = client.classify(files["img"].read())
        return quart.jsonify(await y_hat), 201
    return quart.jsonify({"status": "not image file in request data with key `img`"})


@app.errorhandler(404)
async def not_found(error):
    return quart.make_response(quart.jsonify({"error": "Not found"}), 404)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5055)
