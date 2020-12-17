FROM python:slim

WORKDIR /workspace

COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY . ./
