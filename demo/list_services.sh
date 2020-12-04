#!/bin/bash

curl -X GET localhost:8000/service/ | python3 -m json.tool
