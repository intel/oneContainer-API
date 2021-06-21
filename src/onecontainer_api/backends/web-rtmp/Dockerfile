FROM nginx:1.19.6

RUN apt update && \
    apt install -y git libnginx-mod-rtmp && \
    apt install -y nginx && \
	mv /etc/nginx/conf.d/default.conf /etc/nginx/sites-available/default && \
    cd /usr/share/nginx/html && \
    git clone https://github.com/intel-iot-devkit/sample-videos.git && \
    echo "\nrtmp {\n\
	server {\n\
		listen 1935;\n\
		chunk_size 4000;\n\
		application live {\n\
			live on;\n\
			hls on;\n\
			hls_path /mnt/hls/;\n\
			hls_fragment 3;\n\
			hls_playlist_length 60;\n\
		}\n\
	}\n\
}" >> /etc/nginx/nginx.conf
