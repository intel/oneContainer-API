# SPDX-License-Identifier: BSD-3-Clause
#  Copyright (c) 2020 Intel Corporation
#!/bin/env python
# a stub service to use for testing queue.

import time

import flask
from flask import request

app = flask.Flask("service_stub")


def _leibniz_pi(acc=100_00_000):
    pi = 0
    for n in range(0, acc):
        pi += 4.0 * (-1) ** n / (2 * n + 1)
    return pi


@app.route("/fast", methods=["GET", "POST"])
def fast():
    "fast pi approx, takes about 40 sec on an i9"
    args = request.args
    method = request.method
    data = {}
    data["type"] = "fast"
    data["msg"] = "success: f{request.method} with no args/kwargs!"
    stime = time.time()
    data["pi"] = _leibniz_pi(acc=100_000)
    data["time_taken"] = time.time() - stime
    data["args"] = args
    data["json"] = request.get_json(force=True)
    data["msg"] = "success: {} with args service success!".format(method)
    return flask.jsonify(data)


@app.route("/slow", methods=["GET", "POST"])
def slow():
    "slow pi approx, takes about 4 sec on an i9"
    args = request.args
    method = request.method
    data = {}
    data["type"] = "slow"
    data["msg"] = "success: {} with args service success!".format(method)
    data["json"] = request.get_json(force=True)
    stime = time.time()
    data["pi"] = _leibniz_pi()
    data["time_taken"] = time.time() - stime
    data["args"] = args
    data["msg"] = "success: f{request.method} with args service success"
    return flask.jsonify(data)


@app.route("/really_slow", methods=["GET", "POST"])
def really_slow():
    "really slow pi approx, takes about 40 sec on an i9"
    args = request.args
    method = request.method
    data = {}
    data["type"] = "slow"
    data["msg"] = "success: {} with args service success!".format(method)
    stime = time.time()
    data["pi"] = _leibniz_pi(acc=100_00_000_0)
    data["time_taken"] = time.time() - stime
    data["args"] = args
    data["json"] = request.get_json(force=True)
    data["msg"] = "success: f{request.method} with args service success!"
    return flask.jsonify(data)


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5055)
