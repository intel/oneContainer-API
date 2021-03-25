# SPDX-License-Identifier: BSD-3-Clause
#  Copyright (c) 2020 Intel Corporation
import requests
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--health", action="store_true")
parser.add_argument("--usage", action="store_true")
parser.add_argument("--serve", action="store_true")
parser.add_argument("--predict", action="store_true")
args = parser.parse_args()


if args.health:
    # usage banner
    print("run health check")
    url = "http://10.5.0.3:5055/ping"
    headers = {
        "Hosts": "10.5.0.1:5550"
    }
    print(f"driver URL: {url}")
    print(f"headers passed to backend: {headers}")
    req = requests.get(url, headers=headers, proxies={"http": None})
    print("resp: ", req.text)
    print("-" * 50)

if args.usage:
    # usage check
    print("run usage check")
    url = "http://10.5.0.3:5055/usage"
    headers = {
        "Hosts": "10.5.0.1:5550"
    }
    print(f"driver URL: {url}")
    print(f"headers passed to backend: {headers}")
    req = requests.get(url, headers=headers, proxies={"http": None})
    print("resp: ", req.text)
    print("-" * 50)

if args.serve:
    # serve model
    url = "http://10.5.0.3:5055/serve"
    data = {
        "path": "pytorch/vision:v0.6.0",
        "name": "resnet18",
        "kwargs": {"pretrained": True},
    }
    headers = {
        "Hosts": "10.5.0.1:5550"
    }
    print(f"driver URL: {url}")
    print(f"headers passed to backend: {headers}")
    print(f"data passed to backend: {data}")
    req = requests.post(url, json=data, headers=headers, proxies={"http": None})
    print("resp: ", req.text)
    print("-" * 50)

if args.predict:
    # classify sample image
    print("classify sample image")
    url = "http://10.5.0.3:5055/predict"
    data = {"img": open("data/cat.jpg", "rb")}
    headers = {
        "Hosts": "10.5.0.1:5550"
    }
    print(f"driver URL: {url}")
    print(f"headers passed to backend: {headers}")
    print(f"data passed to backend: {data}")
    req = requests.post(url, files=data, headers=headers, proxies={"http": None})
    print("resp: ", req.text)
    print("-" * 50)
