FROM nginx:1.19.6

RUN apt update && \
    apt install -y git && \
    cd /usr/share/nginx/html && \
    git clone https://github.com/intel-iot-devkit/sample-videos.git