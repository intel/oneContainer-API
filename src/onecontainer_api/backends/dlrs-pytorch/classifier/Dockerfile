FROM sysstacks/dlrs-pytorch-ubuntu:latest

WORKDIR /classifier/
COPY requirements.txt .
RUN pip install -U -r requirements.txt
COPY . /classifier/
ENTRYPOINT ["hypercorn","-kuvloop", "-b0.0.0.0:5059", "--debug", "-w1", "--reload"]
CMD ["rest:app"]
