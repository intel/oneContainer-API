"""tochhub model backend for dlrs."""
import json
import os

from PIL import Image
import psutil
import torch
from torchvision import transforms
from torchvision.transforms.transforms import CenterCrop

from logger import logger
from utils import is_model_cached


class InitServer:
    """init with default best config for CPUs."""

    def __init__(self, kmp_bt="0", kmp_aff=None):
        self.intra_op = str(psutil.cpu_count(logical=False))
        self.inter_op = "2"
        self.kmp_bt = kmp_bt
        self.kmp_aff = kmp_aff if kmp_aff else "granularity=fine,verbose,compact,1,0"

    def set_vars(self):
        os.environ["OMP_BLOCK_TIME"] = self.kmp_bt
        os.environ["KMP_AFFINITY"] = self.kmp_aff
        os.environ["OMP_NUM_THREADS"] = self.intra_op
        os.environ["inter_op_parallelism_threads"] = self.inter_op
        os.environ["intra_op_parallelism_threads"] = self.intra_op


class ModelLoader:
    """load a model given metadata from torchub."""

    def __init__(self, model_meta: dict = None):
        InitServer().set_vars()
        self.loaded = False

    def init_model(self, model_meta: dict):
        try:
            self.m_name = model_meta["name"]
            self.m_path = model_meta["path"]
            self.m_kwargs = model_meta.get("kwargs", None)
            if not self.m_kwargs.get("pretrained", None):
                self.m_kwargs["pretrained"] = True
            if is_model_cached(self.m_path, self.m_name):
                self.model = torch.hub.load(self.m_path, self.m_name, **self.m_kwargs)
                self.model.eval()
                self.loaded = True
        except TypeError as e:
            logger.error(e)

    def load_model(self):
        """load model artifacts from model_hub."""
        try:
            self.model = torch.hub.load(self.m_path, self.m_name, **self.m_kwargs)
            self.model.eval()
            self.loaded = True
        except AttributeError as e:
            logger.error(e)
        except FileNotFoundError as e:
            logger.error(e)
        except RuntimeError as e:
            logger.error(e)
            raise RuntimeError
        return True


class ImageProcessor:
    """transorform image to tensor."""

    def __init__(self, img):
        self.image = Image.open(img)

    def transform(self, size=None, crop=None, mean=None, std=None):
        # todo: load preprocess based on self.model_name
        self.preprocess = transforms.Compose(
            [
                transforms.Resize(size if size else 256),
                transforms.CenterCrop(crop if crop else 224),
                transforms.ToTensor(),
                transforms.Normalize(
                    mean=mean if mean else [0.485, 0.486, 0.406],
                    std=std if std else [0.229, 0.224, 0.225],
                ),
            ]
        )
        self.t_image = self.preprocess(self.image).unsqueeze(0)
        return self.t_image


class ModelRunner:
    """Run model using LoadedModel and ImageProcessor."""

    def __init__(self, model, t_image):
        self.model = model
        self.t_image = t_image

    def run(self):
        """excute forward pass."""
        with torch.no_grad():
            output = self.model(self.t_image)
            # todo: max 3
            _, pred = output.max(1)
            return pred

    def predict(self):
        """get class of object."""
        # todo: use class_idx based on model
        class_idx = json.load(open("./data/imagenet_class_index.json"))
        prediction = self.run()
        prediction_idx = str(prediction.item())
        return class_idx[prediction_idx][1]


if __name__ == "__main__":
    model_meta = {
        "path": "pytorch/vision:v0.6.0",
        "name": "resnet50",
        "kwargs": {"pretrained": True},
        "class_idx": "",  # url
        "img_meta": {"size": 0, "crop": 0},
    }
    m_loader = ModelLoader(model_meta)
    m_loader.load_model()
    img_prep = ImageProcessor(open("./data/cat.jpg", "rb"))
    img_prep.transform()
    m_runr = ModelRunner(m_loader.model, img_prep.t_image)
    print(m_runr.predict())
