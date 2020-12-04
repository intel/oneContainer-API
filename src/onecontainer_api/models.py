"""data models for the routes."""

from sqlalchemy import Column, String, JSON

from sqlalchemy.ext.declarative import declarative_base

import databases
import sqlalchemy

from onecontainer_api import config
from onecontainer_api.logger import logger

engine = sqlalchemy.create_engine(config.DATABASE_URL)

Base = declarative_base()

db = databases.Database(config.DATABASE_URL)


def get_db():
    logger.debug(f"Using db {db.url}")
    return db


class Service(Base):
    __tablename__ = "service"
    id = Column(String, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    description = Column(String)
    version = Column(String)
    app = Column(String)
    app_version = Column(String)
    scope = Column(String)
    driver = Column(String)
    locations = Column(JSON)
    meta = Column(JSON)


class AIModel(Base):
    __tablename__ = "aimodel"
    id = Column(String, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    description = Column(String)
    framework = Column(String)
    url = Column(String)
    version = Column(String)


def get_table(tablename):
    return Base.metadata.tables[tablename]
