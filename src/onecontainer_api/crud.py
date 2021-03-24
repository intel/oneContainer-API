import sqlalchemy
import databases

from onecontainer_api import config

import random


def gen_id(size):
    """Generate random Ids for model creation
    """
    return ''.join(random.choice('aeiou' if x % 2 else 'bcdfghklmnpqrstvwxyz')
                   for x in range(size))


async def db_get(db: databases.Database, table: sqlalchemy.sql.schema.Table, obj_id: str):
    query = table.select()
    query = query.where(table.c.id == obj_id)
    try:
        result = await db.fetch_one(query)
    except RuntimeError:
        return None
    return result


async def db_list(db: databases.Database, table: sqlalchemy.sql.schema.Table,
                  skip: int = 0, limit: int = 100):
    query = table.select()
    query = query.offset(skip)
    query = query.limit(limit)
    try:
        result = await db.fetch_all(query)
    except RuntimeError as e:
        return None
    return result


async def db_create(db: databases.Database, table: sqlalchemy.sql.schema.Table, values: dict):
    """create a db record and return the id if successful."""
    values["id"] = gen_id(config.ID_SIZE)
    query = table.insert()
    query = query.values(**values)
    try:
        await db.execute(query)
    except RuntimeError:
        return None
    return values["id"]


async def db_update(db: databases.Database, table: sqlalchemy.sql.schema.Table,
                    values: dict, obj_id: str):
    query = table.update()
    query = query.where(table.c.id == obj_id)
    query = query.values(**values)
    try:
        await db.execute(query)
    except RuntimeError:
        return None
    return True


async def db_delete(db: databases.Database, table, obj_id: str):
    query = table.delete()
    query = query.where(table.c.id == obj_id)
    try:
        await db.execute(query)
    except RuntimeError:
        return None
    return True
