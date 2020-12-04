"""REST inteface to model_runner."""
import io
from logging import exception

import sanic
from sanic import response

from logger import logger
from model_hub import ModelLoader
from model_hub import ImageProcessor
from model_hub import ModelRunner


app = sanic.Sanic("dlrs-torchub")
model_loader = ModelLoader()


@app.route("/")
async def index(request):
    """index"""
    return response.json(
        {
            "info": "torch hub server on dlrs",
            "urls": ["/", "/ping", "/serve", "/predict"],
        }
    )


@app.route("/ping")
async def ping(request):
    """heartbeat."""
    return response.json({"status": "ok"})


@app.route("/serve", methods=["POST"])
async def load_model(request):
    """load model using process pool."""
    global model_loader
    req = request.json
    if req is None:
        return response.json(
            {"status": "fail", "result": "model param json not provided"}
        )
    if req.get("path", None) and req.get("name", None):
        if not model_loader:
            model_loader = ModelLoader()
        model_loader.init_model(req)
        if model_loader.loaded:
            return response.json(
                {"status": "ok", "result": f"model {req['name']} loaded"}
            )
        try:
            request.app.loop.run_in_executor(None, model_loader.load_model)
        except RuntimeError:
            return response.json(
                {"status": "fail", "result": "model or path not retievable"}
            )
        return response.json(
            {"status": "ok", "result": f"model {req['name']} loading in progress"}
        )
    else:
        model_loader = None
        raise sanic.exceptions.SanicException(
            "model_path/model_name not given", status_code=401
        )


@app.route("/predict", methods=["POST"])
async def predict(request):
    """return output of the model."""
    img_str = request.files["img"]
    image = io.BytesIO(img_str[0].body)
    img_processor = ImageProcessor(image)
    img_tensor = img_processor.transform()
    try:
        model_runner = ModelRunner(model_loader.model, img_tensor)
    except AttributeError:
        return response.json(
            {"status": "failed", "result": "model not initiated, use serve model API"}
        )
    return response.json({"status": "ok", "result": model_runner.predict()})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5550)
