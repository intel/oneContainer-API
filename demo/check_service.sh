#!/bin/bash

curl -X GET localhost:8000/service/$1/heartbeat | python3 -m json.tool
