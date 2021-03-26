# SPDX-License-Identifier: BSD-3-Clause
#  Copyright (c) 2020 Intel Corporation
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import String, LargeBinary, Column


engine = create_engine('sqlite:///ffmpeg.db', echo=True)
Base = declarative_base()

class PipelineModel(Base):
    __tablename__ = 'pipeline'
    id = Column(String, primary_key=True)
    obj = Column(LargeBinary)

