## Client API examples

To see what all APIs are available, a test script has been provided.

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

Note: A model has to be `served` before `prediction`.
