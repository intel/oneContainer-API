#!/bin/bash

curl -X POST -d @video_source.json localhost:8000/media/$1/probe?sync=true | python3 -m json.tool