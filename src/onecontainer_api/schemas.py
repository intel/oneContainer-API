# SPDX-License-Identifier: BSD-3-Clause
#  Copyright (c) 2020 Intel Corporation
from enum import Enum
from typing import List, Optional, Dict, Any

from pydantic import utils, BaseModel


class Scopes(str, Enum):
    """Enum str class for scopes of service api functions of onecontainer-api

    ai means artificial intelligence functions
    db means database functions
    media means media transcoding functions
    hpc means high performance computing functions
    """
    ai = 'ai'
    db = 'db'
    media = 'media'
    hpc = 'hpc'


class SourceTypes(str, Enum):
    """Types of drivers

    native means driver source code is hosted as part of onecontainer-api code and driver.location
    should be empty.
    plugin means driver source code is hosted as a git repository and driver.location
    should be a git repository.
    """
    native = "native"
    plugin = "plugin"


class DriverBase(BaseModel):
    name: str
    version: str
    app: str
    app_version_match: str
    scope: Scopes
    source_type: SourceTypes
    location: Optional[str]
    meta: Optional[Dict[str, Any]]


class DriverCreate(BaseModel):
    name: str
    source_type: SourceTypes = SourceTypes.native.value
    location: Optional[str]


class ServiceBase(BaseModel):
    description: Optional[str] = None
    driver: Optional[str] = None


class ServiceCreate(ServiceBase):
    name: str
    version: str
    app: str
    app_version: str
    locations: Dict[str, str]
    meta: Dict[str, Any]


class ServiceUpdate(ServiceBase):
    name: Optional[str]
    version: Optional[str]
    app: Optional[str]
    app_version: Optional[str]
    locations: Optional[Dict[str, str]]
    meta: Optional[Dict[str, Any]]


class Service(ServiceCreate):
    id: str

    class Config:
        orm_mode = True


class Column(BaseModel):
    name: str
    datatype: str


class Table(BaseModel):
    name: str
    columns: List[Column]
    primary_key: Optional[List[str]]


class DMLExistCondition(str, Enum):
    if_exist = "if_exist"
    if_not_exist = "if_not_exist"


class RecordDMLOptions(BaseModel):
    field_values: Optional[Dict[str, Any]]
    where: Optional[Dict[str, Any]]
    ttl: Optional[int]
    timestamp: Optional[int]
    field_conditions: Optional[Dict[str, Any]]
    exist_condition: Optional[DMLExistCondition]


class AIModelMeta(BaseModel):
    name: str
    path: str
    kwargs: Optional[Dict[str, Any]]
