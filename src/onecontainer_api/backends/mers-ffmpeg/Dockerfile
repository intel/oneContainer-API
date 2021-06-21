FROM sysstacks/mers-ubuntu:latest

EXPOSE 49152-65535/udp
COPY --chown=mers-user:video . /home/mers-user/ffmpeg_server
WORKDIR /home/mers-user/ffmpeg_server/
RUN pip3 install --no-cache-dir -U -r /home/mers-user/ffmpeg_server/requirements.txt
ENTRYPOINT ["python3"]
CMD ["runner.py"]
