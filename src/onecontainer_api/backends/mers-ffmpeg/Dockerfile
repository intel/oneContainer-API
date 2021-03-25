FROM sysstacks/mers-ubuntu:latest

COPY --chown=mers-user:video . /home/mers-user/ffmpeg_server
WORKDIR /home/mers-user/ffmpeg_server/
RUN pip3 install --no-cache-dir -U -r /home/mers-user/ffmpeg_server/requirements.txt
ENTRYPOINT ["python3"]
CMD ["runner.py"]
