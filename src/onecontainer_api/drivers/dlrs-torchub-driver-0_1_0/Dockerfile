FROM python:3.8-slim-buster

WORKDIR /workspace

COPY requirements.txt .
RUN pip --use-feature=2020-resolver install --no-cache-dir -U  -r requirements.txt
COPY . .

EXPOSE 5055
ENTRYPOINT [ "python3", "api.py" ]
