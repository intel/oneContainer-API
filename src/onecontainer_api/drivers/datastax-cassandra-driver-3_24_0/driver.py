# SPDX-License-Identifier: BSD-3-Clause
#  Copyright (c) 2020 Intel Corporation
#!/usr/bin/env python3

from cassandra.cluster import Cluster, NoHostAvailable

from logger import logger


class Client:

    def __init__(self, hosts, metadata):
        self.port = 9042
        self.hosts = []
        for host in hosts:
            if ":" in host:
                self.port = host.split(":")[-1]
                self.hosts.append(host.split(":")[0])
            else:
                self.hosts.append(host)
        logger.debug(f"Connecting to hosts: {hosts}")
        self.ks = metadata["keyspace"]
        self.repl = metadata["replication"]
        self.cluster = Cluster(self.hosts, port=self.port)
        try:
            self.session = self.cluster.connect(self.ks)
        except NoHostAvailable:
            self.cluster.shutdown()
            self.cluster = Cluster(self.hosts, port=self.port)
            query = f"CREATE KEYSPACE IF NOT EXISTS {self.ks} WITH REPLICATION = {self.repl}"
            logger.debug(f"Keyspace not found: {self.ks}")
            logger.debug(f"Executing query: {query}")
            self.session = self.cluster.connect()
            self.session.execute(query)
            self.session.set_keyspace(self.ks)

    def heartbeat(self):
        return bool(self.cluster.metadata.keyspaces)

    def _format_table(self, table):
        columns = []
        for column_name, column in table.columns.items():
            columns.append({
                "name": column_name,
                "datatype": column.cql_type
            })
        return {
            "name": table.name,
            "columns": columns,
            "primary_key": [x.name for x in table.primary_key]
        }

    def list_tables(self, **kwargs):
        tables = []
        for _, table in self.cluster.metadata.keyspaces[self.ks].tables.items():
            tables.append(self._format_table(table))
        return tables

    def create_table(self, data):
        logger.debug(f"Creating table {data}")
        fields = []
        for i in data["columns"]:
            fields.append(f'{i["name"]} {i["datatype"]}')
        query = f'CREATE TABLE {data["name"]}({",".join(fields)}, PRIMARY KEY({",".join(data["primary_key"])}))'
        logger.debug(f"Executing query: {query}")
        self.session.execute(query)
        return True

    def describe_table(self, table_name):
        table = self.cluster.metadata.keyspaces[self.ks].tables[table_name]
        return self._format_table(table)

    def insert_into(self, table_name, data):
        logger.debug(f"Insert into {table_name}: {data}")
        fields = []
        values = []
        for k, v in data["field_values"].items():
            fields.append(k)
            if isinstance(v, str):
                v = f"'{v}'"
            values.append(str(v))
        query = f'INSERT INTO {table_name}({",".join(fields)}) VALUES({",".join(values)})'
        logger.debug(f"Executing query: {query}")
        self.session.execute(query)
        return True

    def select_from(self, table_name, data):
        logger.debug(f"Select from {table_name}: {data}")
        query = f'SELECT * FROM {table_name}'
        logger.debug(f"Executing query: {query}")
        rows = self.session.execute(query)
        return rows.all()

    def update_from(self, table_name, data):
        logger.debug(f"Update from {table_name}: {data}")
        updates = []
        filters = []
        for k, v in data["field_values"].items():
            if isinstance(v, str):
                v = f"'{v}'"
            updates.append(f"{k} = {v}")
        for k, v in data["where"].items():
            if isinstance(v, str):
                v = f"'{v}'"
            filters.append(f"{k} = {v}")
        query = f'UPDATE {table_name} SET {",".join(updates)} WHERE {",".join(filters)}'
        logger.debug(f"Executing query: {query}")
        self.session.execute(query)
        return True

    def delete_from(self, table_name, data):
        logger.debug(f"Delete from {table_name}: {data}")
        filters = []
        for k, v in data["where"].items():
            if isinstance(v, str):
                v = f"'{v}'"
            filters.append(f"{k} = {v}")
        query = f'DELETE FROM {table_name} WHERE {",".join(filters)}'
        logger.debug(f"Executing query: {query}")
        self.session.execute(query)
        return True
