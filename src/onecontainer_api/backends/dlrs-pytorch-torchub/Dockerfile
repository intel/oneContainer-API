FROM sysstacks/dlrs-pytorch-ubuntu:latest

WORKDIR /hub_server/
COPY requirements.txt .
RUN pip install --no-cache-dir -U -r requirements.txt
COPY . /hub_server/
ENTRYPOINT ["python"]
CMD ["runner.py"]
