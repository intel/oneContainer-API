# SPDX-License-Identifier: BSD-3-Clause
#  Copyright (c) 2020 Intel Corporation
#!/usr/bin/env python3

import asyncio
import argparse
import base64
import json

import aiohttp
import aiofiles

from logger import logger


class Client:
    def __init__(self, ip, port, debug=None):
        self.url = f"http://{ip}:{port}"
        self.session = aiohttp.ClientSession()
        if debug:
            logger.debug(f"Connecting to hosts: {self.url}")

    async def usage(self):
        """usage banner"""
        async with self.session as sess:
            async with sess.get(f"{self.url}/") as resp:
                return await resp.text()

    #async def serve(self):
    #    """init and load model."""
    #    async with self.session as sess:
    #        async with sess.get(f"{self.url}/serve") as resp:
    #            return await resp.json()

    async def predict(self, img):
        """takes in an image and returns the response."""
        async with self.session as sess:
            async with sess.post(
                f"{self.url}/predict",
                data={"img": img, "content_type": "application/octet-stream"},
            ) as resp:
                return await resp.text()

    async def ping(self):
        """health check."""
        async with self.session as sess:
            async with sess.get(f"{self.url}/ping") as resp:
                return await resp.json()

    async def serve(self, model_meta):
        """load and init model."""
        async with self.session as sess:
            async with sess.post(f"{self.url}/serve", json=model_meta) as resp:
                return await resp.text()


async def main():
    parser = argparse.ArgumentParser(
        description="driver client for DLRS torchub classifier"
    )
    parser.add_argument("--debug", dest="debug", action="store_true", help="debug mode")
    parser.add_argument("--ip", dest="ip", required=True, help="host ip")
    parser.add_argument("--port", dest="port", required=True, help="host port")
    parser.add_argument(
        "--operation", dest="operation", required=True, help="method to execute"
    )
    result = None
    parser.add_argument("--img", dest="img", required=False, help="image to classify")
    parser.add_argument(
        "--model_meta", dest="img", required=False, help="image to classify"
    )
    args = parser.parse_args()
    client = Client(args.ip, args.port, args.debug)
    if args.operation == "usage":
        result = await client.usage()
    elif args.operation == "ping":
        result = await client.ping()
    elif args.operation == "predict":
        # TODO: this img is obtained from the queue
        async with aiofiles.open(args.img, mode="rb") as img:
            img = await img.read()
            result = await client.predict(img)
    elif args.operation == "serve":
        # TODO: this img is obtained from the queue
        async with aiofiles.open(args.img, mode="rb") as json_fl:
            json = await json_fl.read()
            result = await client.serve(json)
    else:
        print("operation not available")
    print(result)


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
