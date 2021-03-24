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

    async def ping(self):
        """health check."""
        async with self.session as sess:
            async with sess.get(f"{self.url}/ping") as resp:
                return await resp.json(), resp.status

    async def probe(self, data):
        """probes a media file."""
        async with self.session as sess:
            async with sess.post(f"{self.url}/probe", json=data) as resp:
                return await resp.json(), resp.status

    async def transcode(self, data):
        """executes a transcoding pipeline job."""
        async with self.session as sess:
            async with sess.post(f"{self.url}/pipeline", json=data) as resp:
                return await resp.json(), resp.status

    async def get_outputs(self, pipeline_id):
        """gets the outputs a transcoding pipeline job."""
        async with self.session as sess:
            async with sess.get(f"{self.url}/pipeline/{pipeline_id}") as resp:
                return await resp.json(), resp.status
