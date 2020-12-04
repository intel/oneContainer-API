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
            async with sess.get(f"{self.url}/usage") as resp:
                return await resp.json()

    async def classify(self, img):
        """classify method, takes in an image and returns the response."""
        async with self.session as sess:
            async with sess.post(
                f"{self.url}/recog",
                data={"img": img, "content_type": "application/octet-stream"},
            ) as resp:
                return await resp.text()

    def ping(self):
        """health check."""
        return "Ok"


async def main():
    parser = argparse.ArgumentParser(description="REST driver client for DLRS")
    parser.add_argument("--debug", dest="debug", action="store_true", help="debug mode")
    parser.add_argument("--ip", dest="ip", required=True, help="host ip")
    parser.add_argument("--port", dest="port", required=True, help="host port")
    parser.add_argument(
        "--operation", dest="operation", required=True, help="method to execute"
    )
    parser.add_argument("--img", dest="img", required=False, help="image to classify")
    args = parser.parse_args()
    client = Client(args.ip, args.port, args.debug)
    if args.operation == "usage":
        result = await client.usage()
    if args.operation == "classify":
        # TODO: this img is obtained from the queue
        async with aiofiles.open(args.img, mode="rb") as img:
            img = await img.read()
            result = await client.classify(img)
    print(result)


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
