#!/bin/bash

curl -X POST -d @model.json localhost:8000/ai/$1/serve | python3 -m json.tool
