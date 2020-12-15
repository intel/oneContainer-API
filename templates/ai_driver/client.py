# SPDX-License-Identifier: BSD-3-Clause
#  Copyright (c) 2020 Intel Corporation
#!/usr/bin/env python3

import asyncio


class Client:
    def __init__(self):
        raise NotImplementedError

    async def ping(self):
        """health check."""
        raise NotImplementedError

    async def usage(self):
        """usage banner"""
        raise NotImplementedError

    async def serve(self, model_meta):
        """load and init model."""
        raise NotImplementedError

    async def predict(self, img):
        """takes in an input and returns the response."""
        raise NotImplementedError


async def main():
    raise NotImplementedError


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
