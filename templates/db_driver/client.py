# SPDX-License-Identifier: BSD-3-Clause
#  Copyright (c) 2020 Intel Corporation
#!/usr/bin/env python3

class Client:

    def __init__(self, hosts, metadata):
        ### Instantiate connection
        raise NotImplementedError

    def list_tables(self, **kwargs):
        ### List tables code
        raise NotImplementedError

    def create_table(self, data):
        ### create table
        raise NotImplementedError
