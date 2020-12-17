FROM python:slim

WORKDIR /workspace

RUN pip install --no-cache-dir pip --upgrade
COPY requirements.txt .
RUN pip install --no-cache-dir -U -r requirements.txt
COPY . .

#ENTRYPOINT [ "python", "./client.py" ]
