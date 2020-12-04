#!/bin/bash

curl -X GET localhost:8000/job/$1 | python3 -m json.tool
