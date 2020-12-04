## DLRS torchub driver

Build and instantiate the driver

```bash
make && make run
```

To classify an image using models deployed using torchub:

Instantiate the backend torchub serving service:

```bash
cd ../backends/dlrs-pytorch/torchub/
make && make run
```

## client API examples

A test script in `api-request.py` is provided in the `tests` directory of the driver.


First let's see what usage API:

```bash
python api-request.py --usage
```

Health check

```bash
python api-request.py --health
```

Serve a model, it accepts a metadata json file

A sample `model_meta.json` file is:

```bash
model_meta = {
    "type" = "classify",  # at this stage 
    "path" = "pytorch/vision:v0.6.0",  # path to get the model
    "name" = "resnet18",  # model name, this can be resnet50, alexnet etc
    "kwargs" = {"pretrained": True},  # any kwargs, that has to be passed to to the model server
}
```

```bash
python api-request.py --serve
```

Finally to see a prediction example, run

```bash
python api-request.py --predict
```

Note: A model has to be `served` before calling `predict`.
