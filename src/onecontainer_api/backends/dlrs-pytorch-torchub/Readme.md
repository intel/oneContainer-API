## Load model from torch-hub

### Run model server

```bash
python runner.py
```

### Models tested

- ResNet18
- ResNet34
- ResNet50

### Implementation details

- load model based on json data from `/serve` url using a background task
- predict using `/predict` url and input image
