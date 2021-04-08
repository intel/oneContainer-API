#!/bin/bash

curl -X POST -d @pipeline.json localhost:8000/media/$1/pipeline?sync=true | python3 -m json.tool
