# SPDX-License-Identifier: BSD-3-Clause
#  Copyright (c) 2020 Intel Corporation
#!/bin/env python

import json
import time

import diver

import flask
from flask import request

app = flask.Flask("<driver_name>")

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
    client = driver.Client(hosts, metadata)
    return client, None


@app.route("/table", methods=["GET", "POST"])
def table():
    client, error = get_client(request)
    if error:
        return error, 400
    if request.method == 'POST':
        resp = client.create_table(request.data)
    else:
        resp = client.list_tables()
    return flask.jsonify(resp)


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5055)
