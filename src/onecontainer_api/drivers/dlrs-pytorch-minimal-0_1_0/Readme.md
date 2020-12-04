## DLRS REST client plugin

## build client

```bash
make
```

To test the client, once the default classify backend for pytorch is setup:

```bash
docker run --rm dlrs-rest-driver --ip 172.17.0.2 --port 5055 --operation usage  --debug
```

To classify an image:

```bash
docker run --rm dlrs-rest-driver --ip 172.17.0.2 --port 5055 --operation classify --img tests/data/cat.jpg  --debug
```



