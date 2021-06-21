# SPDX-License-Identifier: BSD-3-Clause
#  Copyright (c) 2020 Intel Corporation
try:
    from importlib.metadata import version, PackageNotFoundError  # type: ignore
except ImportError:  # pragma: no cover
    from importlib_metadata import version, PackageNotFoundError  # type: ignore


try:
    __version__ = version(__name__)
except PackageNotFoundError:  # pragma: no cover
    __version__ = "unknown"

from onecontainer_api.logger import logger

ENV_FILE = ".env"
logger.debug("default CACHE TTE set to: 3600")
logger.debug("set environment variable CACHE_TTE=<seconds> to set cache ttl")
logger.debug("use 0 or None if you want to disable it")

