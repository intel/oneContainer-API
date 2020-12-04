## Fast image recognition

A backend service for image recognition using [Efficient Net](https://github.com/lukemelas/EfficientNet-PyTorch).


To run the server:

```bash
›$ docker run -d -p 5059:5059 dlrs-pytorch-classify
```

Once the docker instance is up, on the client, you can run these:

Basic info about the API:

```bash

›$ curl -i   'http://localhost:5059/usage'
```

```bash
{
  "info": {
    "usage": {
      "client": "curl -i  -X POST -F img=@data/cat.jpg 'http://localhost:5059/recog'",
      "server": "docker run -d -p 5059:5059 stacks_img_recog"
    },
    "what": "image recognition api"
  }
}
```

Classify the sample image in the `data` directory:

![cat](./data/cat.jpg)

photo credit: Kerri Lee Smith <a href=http://www.flickr.com/photos/77654186@N07/48470874687>Ellie Belly Ladybug</a> via <a href=http://photopin.com>photopin</a> <a href=https://creativecommons.org/licenses/by-nc-sa/2.0/>(license)</a>

```bash
›$ curl -i  -X POST -F img=@data/cat.jpg 'http://localhost:5059/recog'
```

output:

```bash
{
  "class": "Egyptian cat",
  "prob": 0.2503426969051361
}

```
