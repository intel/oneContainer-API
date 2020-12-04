FROM python:slim

WORKDIR /workspace
COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt
COPY service.py service.py

ENTRYPOINT [ "python3" ]
CMD [ "service.py" ]