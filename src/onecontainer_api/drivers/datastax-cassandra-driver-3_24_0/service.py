# SPDX-License-Identifier: BSD-3-Clause
#  Copyright (c) 2020 Intel Corporation
#!/bin/env python

import json
import urllib.parse

import driver

import flask
from flask import request

app = flask.Flask("cassandra_driver")


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


@app.route("/ping", methods=["GET"])
def ping():
    client, error = get_client(request)
    if error or not client.heartbeat():
        return error, 400
    return flask.jsonify({"status": "Ok"})


@app.route("/table", methods=["GET", "POST"])
def tables():
    client, error = get_client(request)
    if error:
        return error, 400
    if request.method == 'POST':
        resp = client.create_table(json.loads(request.data))
    else:
        resp = client.list_tables()
    return flask.jsonify(resp)


@app.route("/table/<table_name>", methods=["GET"])
def table(table_name):
    client, error = get_client(request)
    if error:
        return error, 400
    resp = client.describe_table(table_name)
    return flask.jsonify(resp)


@app.route("/table/<table_name>/record", methods=["GET", "POST", "PUT", "DELETE"])
def records(table_name):
    client, error = get_client(request)
    if error:
        return error, 400
    # TODO: Need to add error handling
    if request.method == 'POST':
        resp = client.insert_into(table_name, json.loads(request.data))
    elif request.method == 'PUT':
        resp = client.update_from(table_name, json.loads(request.data))
    elif request.method == 'DELETE':
        resp = client.delete_from(table_name, json.loads(request.data))
    else:
        filters = urllib.parse.parse_qs(request.query_string.decode('utf-8'))
        resp = client.select_from(table_name, filters)
    return flask.jsonify(resp)


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5055)
