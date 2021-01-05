FROM python:slim

WORKDIR /workspace

RUN pip install --no-cache-dir pip --upgrade
COPY requirements.txt .
RUN pip install --no-cache-dir -U -r requirements.txt
COPY . .

EXPOSE 5055
ENTRYPOINT [ "python3", "service.py" ]
