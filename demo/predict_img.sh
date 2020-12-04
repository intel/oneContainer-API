#!/bin/bash

curl -X POST -F image_file=@cat.jpg localhost:8000/ai/$1/predict | python3 -m json.tool
