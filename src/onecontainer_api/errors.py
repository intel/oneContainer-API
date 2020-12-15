# SPDX-License-Identifier: BSD-3-Clause
#  Copyright (c) 2020 Intel Corporation
"""custom onecontainer-api errors."""
from pydantic import BaseModel


CONFLICT_ERROR = 100
NOTFOUND_ERROR = 101
REQMISSIG_ERROR = 102

DATA_ERROR_MSG = {
    NOTFOUND_ERROR: "not found",
    CONFLICT_ERROR: "already exists",
    REQMISSIG_ERROR: "field required"
}

NO_DRV_ERROR = 200
DRV_UNREACH_ERROR = 201
DRV_EXEC_ERROR = 202
DRV_IMPL_ERROR = 203
QAPI_UNREACH_ERROR = 204
QAPI_EXEC_ERROR = 205
QAPI_JOB_ERROR = 206
DATA_ERROR = 207

SVC_ERROR_MSG = {
    NO_DRV_ERROR: "Driver is not available",
    DRV_UNREACH_ERROR: "Driver is unreachable",
    DRV_EXEC_ERROR: "Driver execution failed",
    DRV_IMPL_ERROR: "Driver might be successful but wrongly implemented",
    QAPI_UNREACH_ERROR: "Queue API is unreachable",
    QAPI_EXEC_ERROR: "Queue API call failed",
    QAPI_JOB_ERROR: "Queue API failed to process job",
    DATA_ERROR: "Data error"
}


class OneContainerAPIException(Exception):
    """default onecontainer api exception."""
    pass


class DataException(OneContainerAPIException):
    def __init__(self, model: BaseModel, obj_id: str, msg_type: int):
        self.model = model
        self.obj_id = obj_id
        self.msg = DATA_ERROR_MSG[msg_type]


class ServiceException(OneContainerAPIException):
    def __init__(self, obj_ref: str, msg_type: int, detail: str = ""):
        self.obj_ref = obj_ref

        self.detail = detail
        self.msg = SVC_ERROR_MSG[msg_type]

