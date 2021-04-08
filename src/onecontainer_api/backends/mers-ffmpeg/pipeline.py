# SPDX-License-Identifier: BSD-3-Clause
#  Copyright (c) 2020 Intel Corporation
import pickle
import os
import threading
import time
import random
import subprocess
from typing import List

import ffmpeg
from sqlalchemy.orm import sessionmaker
from cloudstore import store

from logger import logger
from models import Base, engine, PipelineModel

Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
session = Session()

VIDEO_TYPE = 1
AUDIO_TYPE = 2
SUBTITLE_TYPE = 3

CHANNEL_TYPES = {
    "video":VIDEO_TYPE, 
    "audio": AUDIO_TYPE,
    "subtitle": SUBTITLE_TYPE
}


def gen_id(size):
    return ''.join(random.choice('aeiou' if x % 2 else 'bcdfghklmnpqrstvwxyz')
                   for x in range(size))


class Channel:
    def __init__(self, stream_type: int, codec: str, params: dict = None, codec_params: dict = None, filters: dict = None):
        self.stream_type = stream_type
        self.codec = codec
        self.params = params
        self.codec_params = codec_params
        self.filters = filters

class Input:

    @staticmethod
    def get_input_from_data(data: dict):
        return Input(data.get("source"), data.get("start_time"), data.get("duration"))

    def __init__(self, source: str, start_time: int = None, duration: int = None):
        self.source = source
        self.start_time = start_time
        self.duration = duration

    def probe(self) -> dict:
        return ffmpeg.probe(self.source)

class Output:

    CREATED_STATE = "created"
    RUNNING_STATE = "running"
    FINISHED_STATE = "finished"
    ERROR_STATE = "error"

    @staticmethod
    def get_outputs_from_data(data: dict):
        outputs = []
        for output_data in data:
            output_channels = output_data.pop("channels", []) or []
            output_data["channels"] = []
            for channel_data in output_channels:
                channel_type = channel_data.pop("stream_type")
                output_data["channels"].append(Channel(CHANNEL_TYPES.get(channel_type, 0), **channel_data))
            outputs.append(Output(**output_data))    
        return outputs

    def __init__(self, container: str, params: dict = None, channels: List[Channel] = None, storage: dict = None, **kwargs):
        self.container = container
        self.params = params
        self.channels = channels
        self.id = f"{gen_id(8)}.{self.container}"
        self.storage = storage
        self.command = None
        self.ffmpeg_job = None

    def get_status(self):
        if self.command is None:
            return Output.CREATED_STATE
        if not os.path.exists(f"{self.id}.err"):
            return Output.RUNNING_STATE
        if self.get_cmd_rc() == 0:
            return Output.FINISHED_STATE
        return Output.ERROR_STATE

    def get_cmd_output(self):
        if os.path.exists(f"{self.id}.err"):
            with open(f"{self.id}.err", 'r') as logfile:
                return logfile.readlines()[11:]

    def get_cmd_rc(self):
        if os.path.exists(f"{self.id}.ret"):
            with open(f"{self.id}.ret", 'r') as rcfile:
                return int(rcfile.read())

class Pipeline:

    @staticmethod
    def parse_data(data: dict):
        # Don't print storage secrets, use this line in secure envs
        # logger.debug(f"Creating pipeline with the following data {data}")
        input_file = Input.get_input_from_data(data.get("input_file"))
        outputs = Output.get_outputs_from_data(data.get("outputs"))
        kwargs = {}
        if "ttl" in data:
            kwargs["ttl"] = data["ttl"]
        return Pipeline(input_file, outputs, **kwargs)

    @staticmethod
    def get_from_db(pipeline_id: str):
        pipeline = session.query(PipelineModel).filter_by(id=pipeline_id).first()
        if not pipeline:
            return None
        return pickle.loads(pipeline.obj)
        
    def __init__(self, input_file: Input, outputs: list, ttl: int = 300):
        self.input_file = input_file
        self.outputs = outputs
        self.id = gen_id(10)
        self.ttl = ttl
        logger.debug(f"New pipeline created: {self.id}")

    def _save_in_db(self):
        pipeline = PipelineModel(
            id=self.id,
            obj=pickle.dumps(self),
        )
        session.add(pipeline)
        session.commit()

    def transcode(self):
        input_params = {"filename": self.input_file.source}
        if self.input_file.start_time:
            input_params["ss"] = self.input_file.start_time
        if self.input_file.duration:
            input_params["t"] = self.input_file.duration
        has_video = False
        has_audio = False
        for stream in self.input_file.probe()["streams"]:
            if stream["codec_type"] == 'video':
                has_video = True
            elif stream["codec_type"] == 'audio':
                has_audio = True
        pipeline_input = ffmpeg.input(**input_params)
        for output in self.outputs:
            output_params = output.params or {}
            video = pipeline_input.video
            audio = pipeline_input.audio
            for channel in output.channels:
                if channel.filters:
                    for filter_name, filter_value in channel.filters.items():
                        filter_args = []
                        filter_kwargs = {}
                        if isinstance(filter_value, dict):
                            filter_kwargs.update(filter_value)
                        elif isinstance(filter_value, list):
                            filter_args.extend(filter_value)
                        else:
                            filter_args.append(filter_value)
                        if channel.stream_type == VIDEO_TYPE:
                            video = video.filter(filter_name, *filter_args, **filter_kwargs)
                        elif channel.stream_type == AUDIO_TYPE:
                            audio = audio.filter(filter_name, *filter_args, **filter_kwargs)
                profile = channel.codec_params.pop("profile", None) if channel.codec_params else None
                if channel.codec:
                    if channel.stream_type == VIDEO_TYPE:
                        output_params["vcodec"] = channel.codec
                        if profile:
                            channel.codec_params["profile:v"] = profile
                    elif channel.stream_type == AUDIO_TYPE:
                        output_params["acodec"] = channel.codec
                        if profile:
                            channel.codec_params["profile:a"] = profile
                    elif channel.stream_type == SUBTITLE_TYPE:
                        output_params["scodec"] = channel.codec
                    # TODO: Evaluate if channel params match container format?
                output_params.update(channel.params or {})
                output_params.update(channel.codec_params or {})
            output_args = []
            if has_video:
                output_args.append(video)
            if has_audio:
                output_args.append(audio)
            output_args.append(output.id)
            output.ffmpeg_job = ffmpeg.output(*output_args, **output_params)
            output.command = f"ffmpeg {' '.join(output.ffmpeg_job.get_args())}"
        # Need to save in DB before executing threads because pickle don't support threads
        self._save_in_db()
        logger.debug(f"Starting jobs for pipeline: {self.id} with ttl of {self.ttl}")
        jobs = []
        for output in self.outputs:
            logger.debug(f"Running command: {output.command}")
            process = ffmpeg.run_async(output.ffmpeg_job, pipe_stdout=True, pipe_stderr=True)
            output_watcher = threading.Thread(target=watch_output_job, args=(process, output))
            output_watcher.start()
            jobs.append(process)
        pipeline_watcher = threading.Thread(target=watch_pipeline_jobs, args=(jobs, self))
        pipeline_watcher.start()

    def get_outputs_ids(self):
        for output in self.outputs:
            yield output.id

    def get_outputs_data(self):
        for output in self.outputs:
            yield {
                "id": output.id,
                "command": output.command,
                "status": output.get_status(),
                "command_output": output.get_cmd_output(),
                "command_retcode": output.get_cmd_rc(),
            }


def watch_output_job(process: subprocess.Popen, output: Output):
    logger.debug(f"Waiting for job to finish: {output.id}")
    _, err = process.communicate()
    with open(f"{output.id}.ret", 'w') as outfile:
        outfile.write(str(process.returncode))
    with open(f"{output.id}.err", 'w') as errfile:
        errfile.write(err.decode('utf-8'))
    if output.storage:
        for cloud_storage in output.storage:
            name = cloud_storage.get("name")
            bucket = cloud_storage.get("bucket")
            logger.debug(f"Uploading {output.id} to {name}/{bucket}")
            os.environ.update(cloud_storage.get("env", {}))
            st = store(name)
            st.upload(bucket, output.id)
    logger.debug(f"Finished job: {output.id}")

def watch_pipeline_jobs(jobs: list, pipeline: Pipeline):
    for job in jobs:
        job.wait()
    if pipeline.ttl:
        logger.debug(f"Deleting pipeline: {pipeline.id} in {pipeline.ttl} seconds")
        time.sleep(pipeline.ttl)
        session = Session()
        db_obj = session.query(PipelineModel).filter_by(id=pipeline.id).first()
        session.delete(db_obj)
        session.commit()
        logger.debug(f"Done deleting pipeline: {pipeline.id}")
        for output in pipeline.outputs:
            logger.debug(f"Deleting output: {output.id}")
            os.remove(f"{output.id}.ret")
            os.remove(f"{output.id}.err")
            os.remove(f"{output.id}")