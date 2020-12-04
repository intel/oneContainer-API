"""utilities."""

import os
from os import listdir
from os.path import isfile
from os.path import isdir
from os.path import join

from logger import logger

def is_model_cached(model_repo: str = "", model_name: str = "", cache_dir : str= "/root/.cache/torch/hub"):
    """check if the model(pretrained) is cached locally."""
    if not (model_repo and model_name):
        raise ValueError("model_repo or model_name not provided")
    chk_point_files = None
    model_repo_str = "_".join(model_repo.split("/"))
    if ":" in model_repo_str:
        model_repo_str = "_".join(model_repo_str.split(":"))
    else:
        model_repo_str = f"{model_repo_str}_master"
    model_dir = isdir(os.path.join(cache_dir, model_repo_str))
    chk_point_dir = join(cache_dir, "checkpoints")
    try:
        chk_point_files = any([
            f.startswith(model_name)
            for f in listdir(chk_point_dir)
            if isfile(join(chk_point_dir, f))
        ])
    except FileNotFoundError as e:
        logger.error(e)
    if model_dir and chk_point_files:
        return True
    else:
        return False


if __name__ == "__main__":
    from torch import hub
    hub.load("pytorch/vision:v0.6.0", "resnet18", pretrained=True)
    two = is_model_cached("pytorch/vision:v0.6.0", "resnet18")
    print("checking if resnet18 v0.6.0 is cached: ", two)
    hub.load("pytorch/vision", "resnet18", pretrained=True)
    two = is_model_cached("pytorch/vision", "resnet18")
    print("checking if resnet18 master is cached: ", two)
