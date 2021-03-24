"""REST inteface to model_runner."""
import io
import pickle
import time
from logging import exception

import ffmpeg
import sanic
from sanic import response
from sqlalchemy.orm import sessionmaker

from logger import logger

from pipeline import Input, Pipeline


app = sanic.Sanic("mers-ffmpeg")


@app.route("/")
async def index(request):
    """index"""
    return response.json(
        {
            "info": "ffmpeg server on mers",
            "urls": ["/", "/ping", "/probe", "/pipeline"],
        }
    )


@app.route("/ping")
async def ping(request):
    """heartbeat."""
    return response.json({"status": "ok"})


@app.route("/probe", methods=["POST"])
async def probe(request):
    """probe."""
    input_file = Input.get_input_from_data(request.json)
    try:
        res = input_file.probe()
    except ffmpeg._run.Error as e:
        logger.error(e)
        logger.error(e.stderr)
        return response.json({
                "status":"error",
                "description":e.stderr.decode('utf-8').strip().split('\n')[11:]
            }, status=400)
    return response.json(res)


@app.route("/pipeline", methods=["POST"])
async def create_pipeline(request):
    """Create pipeline."""
    pipeline = Pipeline.parse_data(request.json)
    if not pipeline.outputs:
        return response.json({
                "status":"error",
                "description": "No outputs specified"
            }, status=400)
    try:
        pipeline.transcode()
    except ffmpeg._run.Error as e:
        logger.error(e)
        logger.error(e.stderr)
        return response.json({
                "status":"error",
                "description":e.stderr.decode('utf-8').strip().split('\n')[11:]
            }, status=400)
    return response.json({
            "id": pipeline.id,
            "outputs": list(pipeline.get_outputs_data())
        })


@app.route("/pipeline/<pipeline_id:string>")
async def get_pipeline(request, pipeline_id):
    """Get pipeline."""
    pipeline = Pipeline.get_from_db(pipeline_id)
    if pipeline is None:
        return response.json({
                "status":"error",
                "description": f"Pipeline {pipeline_id} doesn't exist"
            }, status=400)
    return response.json(list(pipeline.get_outputs_data()))


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5552, debug=True, auto_reload=True)
