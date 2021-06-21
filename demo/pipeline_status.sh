#!/bin/bash

curl localhost:8000/media/$1/pipeline/$2?sync=true | python3 -m json.tool
