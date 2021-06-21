# SPDX-License-Identifier: BSD-3-Clause
#  Copyright (c) 2020 Intel Corporation
import os
import time

from fastapi.testclient import TestClient

from onecontainer_api import models, schemas, config, startup_svc
from onecontainer_api.frontend import app

web_server_port = 80
rtmp_server_port = 1935
for svc in config.INITIAL_SERVICES:
    if svc["image"] == "web-rtmp":
        web_server_port = svc["port"]["80/tcp"]
        rtmp_server_port = svc["port"]["1935/tcp"]
        break

video_0 = f"http://{config.BACKEND_NETWORK_GATEWAY}:{web_server_port}/sample-videos/fruit-and-vegetable-detection.mp4"
video_1 = f"http://{config.BACKEND_NETWORK_GATEWAY}:{web_server_port}/sample-videos/bottle-detection.mp4"
video_2 = f"http://{config.BACKEND_NETWORK_GATEWAY}:{web_server_port}/sample-videos/face-demographics-walking.mp4"

rtmp_ip = f"{config.BACKEND_NETWORK_GATEWAY}:{rtmp_server_port}"

input_data = {
    "source": video_0
}

probe_input = {'streams': [{'index': 0, 'codec_name': 'h264', 'codec_long_name': 'H.264 / AVC / MPEG-4 AVC / MPEG-4 part 10', 'profile': 'High', 'codec_type': 'video', 'codec_time_base': '1001/120000', 'codec_tag_string': 'avc1', 'codec_tag': '0x31637661', 'width': 960, 'height': 540, 'coded_width': 960, 'coded_height': 544, 'closed_captions': 0, 'has_b_frames': 0, 'sample_aspect_ratio': '1:1', 'display_aspect_ratio': '16:9', 'pix_fmt': 'yuv420p', 'level': 32, 'color_range': 'tv', 'color_space': 'bt709', 'color_transfer': 'bt709', 'color_primaries': 'bt709', 'chroma_location': 'left', 'field_order': 'progressive', 'refs': 1, 'is_avc': 'true', 'nal_length_size': '4', 'r_frame_rate': '60000/1001', 'avg_frame_rate': '60000/1001', 'time_base': '1/60000', 'start_pts': 0, 'start_time': '0.000000', 'duration_ts': 3636633, 'duration': '60.610550', 'bit_rate': '2335818', 'bits_per_raw_sample': '8', 'nb_frames': '3633', 'disposition': {'default': 1, 'dub': 0, 'original': 0, 'comment': 0, 'lyrics': 0, 'karaoke': 0, 'forced': 0, 'hearing_impaired': 0, 'visual_impaired': 0, 'clean_effects': 0, 'attached_pic': 0, 'timed_thumbnails': 0}, 'tags': {'creation_time': '2018-06-15T21:05:12.000000Z', 'language': 'und', 'handler_name': 'Core Media Video'}}], 'format': {'filename': 'http://172.17.0.1:5553/sample-videos/fruit-and-vegetable-detection.mp4', 'nb_streams': 1, 'nb_programs': 0, 'format_name': 'mov,mp4,m4a,3gp,3g2,mj2', 'format_long_name': 'QuickTime / MOV', 'start_time': '0.000000', 'duration': '60.610550', 'size': '17760065', 'bit_rate': '2344154', 'probe_score': 100, 'tags': {'major_brand': 'mp42', 'minor_version': '1', 'compatible_brands': 'mp41mp42isom', 'creation_time': '2018-06-15T21:05:12.000000Z'}}}

supported_containers = ["mkv", "mp4", "mov", "m4a", "avi", "webm", "wmv", "vob"]

supported_audio_codecs = {
  "aac": "aac",
  "ogg": "libvorbis",
  "wav": "pcm_s16le",
  "flac": "flac",
  "ac3": "ac3",
  "wma": "wmav2",
}

supported_gpu_codecs = {
  "mp4": "h264_vaapi",
  "mkv": "hevc_vaapi",
  "mov": "mjpeg_vaapi",
  "webm": "vp8_vaapi"
}

pipeline_codecs = {
  "input_file": {
    "source": video_1
  },
  "outputs": [
    {
      "container": "mp4",
      "channels": [
        {
          "stream_type": "video",
          "codec": "libx264"
        }
      ]
    }
  ]
}

pipeline_h264 = {
  "input_file": {
    "source": video_1
  },
  "outputs": [
    {
      "container": "mkv",
      "channels": [
        {
          "stream_type": "video",
          "codec": "libx264",
          "codec_params": {
            "preset": "ultrafast",
            "tune": "film",
            "crf": "30"
          }
        }
      ]
    }
  ]
}

pipeline_mpegts = {
  "input_file": {
    "source": video_1,
    "params": {
      "re": None
    }
  },
  "outputs": [
    {
      "container": "mpegts",
      "channels": [
        {
          "stream_type": "video",
          "codec": "libx264",
          "codec_params": {
            "preset": "fast",
            "crf": "30"
          }
        }
      ]
    }
  ]
}

pipeline_rtmp = {
  "input_file": {
    "source": video_1,
    "params": {
      "re": None
    }
  },
  "outputs": [
    {
      "container": "flv",
      "rtmp_ip": rtmp_ip,
      "rtmp_path": "live",
      "channels": [
        {
          "stream_type": "video",
          "codec": "libx264",
          "codec_params": {
            "preset": "fast",
            "crf": "30"
          }
        }
      ]
    }
  ]
}

pipeline_filters = {
  "input_file": {
    "source": video_2
  },
  "outputs": [
    {
      "container": "mkv",
      "channels": [
        {
          "stream_type": "video",
          "filters": {
            "scale": {
              "w": "iw/2",
              "h": -1
            },
            "deflicker": {
              "mode": "pm",
              "size": 10
            },
            "reverse": {},
            "hue": {
              "s": 0
            }
          }
        },
        {
          "stream_type": "audio",
          "filters": {
            "atrim": {
              "start": 1
            },
            "asetpts": "PTS-STARTPTS",
            "volume": {
              "volume": 0.8
            },
            "areverse": {},
            "aphaser": {}
          }
        }
      ]
    }
  ]
}

pipeline_copy = {
  "input_file": {
    "source": video_2
  },
  "outputs": [
    {
      "container": "mp4",
      "channels": [
        {
          "stream_type": "video",
          "codec": "copy"
        },
        {
          "stream_type": "audio",
          "codec": "copy"
        }
      ]
    }
  ]
}

pipeline_empty = {
  "input_file": {
    "source": video_2
  },
  "outputs": [
    {
      "container": "mp4"
    }
  ]
}

pipeline_mkv = {
  "input_file": {
    "source": video_1
  },
  "outputs": [
    {
      "container": "mkv",
      "params": {
        "metadata": "stereo_mode=left_right",
        "default_mode": "infer_no_subs"
      }
    }
  ]
}

pipeline_mp4 = {
  "input_file": {
    "source":video_1
  },
  "outputs": [
    {
      "container": "mp4",
      "params": {
        "movflags": "isml+frag_keyframe"
      }
    }
  ]
}

pipeline_aac = {
  "input_file": {
    "source": video_2
  },
  "outputs": [
    {
      "container": "aac",
      "channels": [
        {
          "stream_type": "audio",
          "codec": "aac",
          "codec_params": {
            "ab": 192000,
            "profile": "aac_ltp",
            "strict": "-2",
          }
        },
        {
          "stream_type": "video",
          "params": {
            "vn": None
          }
        }
      ]
    }
  ]
}

class TestMedia():

    def setup_method(self):
        models.Base.metadata.create_all(bind=models.engine)

    def teardown_method(self):
        os.remove(config.DATABASE_URL.split("///")[1])

    def test_probe(self):
        with TestClient(app) as client:
            response = client.get("/service")
            data = list(filter(lambda x: x['app'] == 'mers-ffmpeg', response.json()))[0]
            svc_id = data.pop("id")
            response = client.post(f"/media/{svc_id}/probe?sync=true", json=input_data)
            assert response.status_code == 200
            assert response.json() == probe_input

    def test_probe_missing_fields(self):
        with TestClient(app) as client:
            response = client.get("/service")
            data = list(filter(lambda x: x['app'] == 'mers-ffmpeg', response.json()))[0]
            svc_id = data.pop("id")
            response = client.post(f"/media/{svc_id}/probe?sync=true", json={})
            assert response.status_code == 400
            assert response.json().get("status") == "InputFile field required: source"

    def test_probe_wrong_data(self):
        with TestClient(app) as client:
            response = client.get("/service")
            data = list(filter(lambda x: x['app'] == 'mers-ffmpeg', response.json()))[0]
            svc_id = data.pop("id")
            response = client.post(f"/media/{svc_id}/probe?sync=true", json={"source": "wrong"})
            assert response.status_code == 400
            assert response.json().get("status", {}).get('detail', {}).get('description') == ["wrong: No such file or directory"]
            response = client.post(f"/media/{svc_id}/probe?sync=true", json={"source": ""})
            assert response.status_code == 400
            assert response.json().get("status", {}).get('detail', {}).get("description") == [": No such file or directory"]
            response = client.post(f"/media/{svc_id}/probe?sync=true", json={"source": None})
            assert response.status_code == 400
            assert response.json().get("status") == "InputFile none is not an allowed value: source"
            response = client.post(f"/media/{svc_id}/probe?sync=true", json={"source": 1})
            assert response.status_code == 400
            assert response.json().get("status", {}).get('detail', {}).get("description") == ["1: No such file or directory"]

    def test_pipeline_missing_fields(self):
        with TestClient(app) as client:
            response = client.get("/service")
            data = list(filter(lambda x: x['app'] == 'mers-ffmpeg', response.json()))[0]
            svc_id = data.pop("id")
            json_data = pipeline_codecs.copy()
            json_data["outputs"] = [{}]
            response = client.post(f"/media/{svc_id}/pipeline?sync=true", json=json_data)
            assert response.status_code == 400
            assert response.json().get("status") == "Pipeline field required: outputs,0,container"
            json_data["outputs"][0] = {"container": "test", "channels": [{}]}
            response = client.post(f"/media/{svc_id}/pipeline?sync=true", json=json_data)
            assert response.status_code == 400
            assert response.json().get("status") == "Pipeline field required: outputs,0,channels,0,stream_type"
            json_data["outputs"] = []
            response = client.post(f"/media/{svc_id}/pipeline?sync=true", json=json_data)
            assert response.status_code == 400
            assert response.json().get("status", {}).get('detail', {}).get('description') == "No outputs specified"
            json_data.pop("input_file")
            response = client.post(f"/media/{svc_id}/pipeline?sync=true", json=json_data)
            assert response.status_code == 400
            assert response.json().get("status") == "Pipeline field required: input_file"

    def test_pipeline_unsupported_data(self):
        with TestClient(app) as client:
            response = client.get("/service")
            data = list(filter(lambda x: x['app'] == 'mers-ffmpeg', response.json()))[0]
            svc_id = data.pop("id")
            json_data = pipeline_codecs.copy()
            json_data["outputs"][0]["container"] = "wrong"
            response = client.post(f"/media/{svc_id}/pipeline?sync=true", json=json_data)
            assert response.status_code == 200
            pipeline_id = response.json()['id']
            time.sleep(3)
            response = client.get(f"/media/{svc_id}/pipeline/{pipeline_id}?sync=true")
            assert response.status_code == 200
            for output in response.json():
                assert output['status'] == 'error'
                assert output['command_output'][-1].strip() == f"{output.get('id')}.wrong: Invalid argument"
            json_data["outputs"][0]["container"] = "mkv"
            json_data["outputs"][0]["channels"][0]["codec"] = "wrong"
            response = client.post(f"/media/{svc_id}/pipeline?sync=true", json=json_data)
            assert response.status_code == 200
            pipeline_id = response.json()['id']
            time.sleep(2)
            response = client.get(f"/media/{svc_id}/pipeline/{pipeline_id}?sync=true")
            assert response.status_code == 200
            for output in response.json():
                assert output['status'] == 'error'
                assert output['command_output'][-1].strip() == "Unknown encoder 'wrong'"
            json_data["outputs"][0]["channels"][0]["codec"] = "libx264"
            json_data["outputs"][0]["channels"][0]["stream_type"] = "wrong"
            response = client.post(f"/media/{svc_id}/pipeline?sync=true", json=json_data)
            assert response.status_code == 200
            pipeline_id = response.json()['id']
            outputs = response.json().get("outputs", [])
            response = client.get(f"/media/{svc_id}/pipeline/{pipeline_id}?sync=true")
            assert response.status_code == 200
            result = response.json()
            for index in range(len(result)):
                assert result[index]['status'] != 'error'
                assert result[index]['command'] == f"ffmpeg -i {video_1} -map 0:v {outputs[index]}"

    def test_pipeline_copy(self):
        with TestClient(app) as client:
            response = client.get("/service")
            data = list(filter(lambda x: x['app'] == 'mers-ffmpeg', response.json()))[0]
            svc_id = data.pop("id")
            response = client.post(f"/media/{svc_id}/pipeline?sync=true", json=pipeline_copy)
            assert response.status_code == 200
            pipeline_id = response.json()['id']
            outputs = response.json().get("outputs", [])
            response = client.get(f"/media/{svc_id}/pipeline/{pipeline_id}?sync=true")
            assert response.status_code == 200
            result = response.json()
            for index in range(len(result)):
                assert result[index]['status'] != 'error'
                assert result[index]['command'] == f"ffmpeg -i {video_2} -map 0:v -map 0:a -acodec copy -vcodec copy {outputs[index]}"

    def test_pipeline_empty(self):
        with TestClient(app) as client:
            response = client.get("/service")
            data = list(filter(lambda x: x['app'] == 'mers-ffmpeg', response.json()))[0]
            svc_id = data.pop("id")
            response = client.post(f"/media/{svc_id}/pipeline?sync=true", json=pipeline_empty)
            assert response.status_code == 200
            pipeline_id = response.json()['id']
            outputs = response.json().get("outputs", [])
            response = client.get(f"/media/{svc_id}/pipeline/{pipeline_id}?sync=true")
            assert response.status_code == 200
            result = response.json()
            for index in range(len(result)):
                assert result[index]['status'] != 'error'
                assert result[index]['command'] == f"ffmpeg -i {video_2} -map 0:v -map 0:a {outputs[index]}"

    def test_pipeline_mkv(self):
        with TestClient(app) as client:
            response = client.get("/service")
            data = list(filter(lambda x: x['app'] == 'mers-ffmpeg', response.json()))[0]
            svc_id = data.pop("id")
            response = client.post(f"/media/{svc_id}/pipeline?sync=true", json=pipeline_mkv)
            assert response.status_code == 200
            pipeline_id = response.json()['id']
            outputs = response.json().get("outputs", [])
            response = client.get(f"/media/{svc_id}/pipeline/{pipeline_id}?sync=true")
            assert response.status_code == 200
            result = response.json()
            for index in range(len(result)):
                assert result[index]['status'] != 'error'
                assert result[index]['command'] == f"ffmpeg -i {video_1} -map 0:v -default_mode infer_no_subs -metadata stereo_mode=left_right {outputs[index]}"

    def test_pipeline_mp4(self):
        with TestClient(app) as client:
            response = client.get("/service")
            data = list(filter(lambda x: x['app'] == 'mers-ffmpeg', response.json()))[0]
            svc_id = data.pop("id")
            response = client.post(f"/media/{svc_id}/pipeline?sync=true", json=pipeline_mp4)
            assert response.status_code == 200
            pipeline_id = response.json()['id']
            outputs = response.json().get("outputs", [])
            response = client.get(f"/media/{svc_id}/pipeline/{pipeline_id}?sync=true")
            assert response.status_code == 200
            result = response.json()
            for index in range(len(result)):
                assert result[index]['status'] != 'error'
                assert result[index]['command'] == f"ffmpeg -i {video_1} -map 0:v -movflags isml+frag_keyframe {outputs[index]}"

    def test_pipeline_aac(self):
        with TestClient(app) as client:
            response = client.get("/service")
            data = list(filter(lambda x: x['app'] == 'mers-ffmpeg', response.json()))[0]
            svc_id = data.pop("id")
            response = client.post(f"/media/{svc_id}/pipeline?sync=true", json=pipeline_aac)
            assert response.status_code == 200
            pipeline_id = response.json()['id']
            outputs = response.json().get("outputs", [])
            response = client.get(f"/media/{svc_id}/pipeline/{pipeline_id}?sync=true")
            assert response.status_code == 200
            result = response.json()
            for index in range(len(result)):
                assert result[index]['status'] != 'error'
                assert result[index]['command'] == f"ffmpeg -i {video_2} -map 0:v -map 0:a -ab 192000 -acodec aac -profile:a aac_ltp -strict -2 -vn {outputs[index]}"

    def test_pipeline_h264(self):
        with TestClient(app) as client:
            response = client.get("/service")
            data = list(filter(lambda x: x['app'] == 'mers-ffmpeg', response.json()))[0]
            svc_id = data.pop("id")
            response = client.post(f"/media/{svc_id}/pipeline?sync=true", json=pipeline_h264)
            assert response.status_code == 200
            pipeline_id = response.json()['id']
            outputs = response.json().get("outputs", [])
            time.sleep(2)
            response = client.get(f"/media/{svc_id}/pipeline/{pipeline_id}?sync=true")
            assert response.status_code == 200
            result = response.json()
            for index in range(len(result)):
                assert result[index]['status'] == 'finished'
                assert result[index]['command'] == f"ffmpeg -i {video_1} -map 0:v -crf 30 -preset ultrafast -tune film -vcodec libx264 {outputs[index]}"

    def test_pipeline_filters(self):
        with TestClient(app) as client:
            response = client.get("/service")
            data = list(filter(lambda x: x['app'] == 'mers-ffmpeg', response.json()))[0]
            svc_id = data.pop("id")
            response = client.post(f"/media/{svc_id}/pipeline?sync=true", json=pipeline_filters)
            assert response.status_code == 200
            pipeline_id = response.json()['id']
            outputs = response.json().get("outputs", [])
            time.sleep(5)
            response = client.get(f"/media/{svc_id}/pipeline/{pipeline_id}?sync=true")
            assert response.status_code == 200
            result = response.json()
            for index in range(len(result)):
                assert result[index]['status'] == 'finished'
                assert result[index]['command'] == f"ffmpeg -i {video_2} -filter_complex [0:v]scale=h=-1:w=iw/2[s0];[s0]deflicker=mode=pm:size=10[s1];[s1]reverse[s2];[s2]hue=s=0[s3];[0:a]atrim=start=1[s4];[s4]asetpts=PTS-STARTPTS[s5];[s5]volume=volume=0.8[s6];[s6]areverse[s7];[s7]aphaser[s8] -map [s3] -map [s8] {outputs[index]}"

    def test_pipeline_supported_containers(self):
        with TestClient(app) as client:
            response = client.get("/service")
            data = list(filter(lambda x: x['app'] == 'mers-ffmpeg', response.json()))[0]
            svc_id = data.pop("id")
            json_data = pipeline_empty.copy()
            for container in supported_containers:
                json_data["outputs"][0]["container"] = container
                response = client.post(f"/media/{svc_id}/pipeline?sync=true", json=json_data)
                assert response.status_code == 200
                pipeline_id = response.json()['id']
                outputs = response.json().get("outputs", [])
                timeout = 15
                finished = False
                while not finished and timeout:
                    time.sleep(3)
                    response = client.get(f"/media/{svc_id}/pipeline/{pipeline_id}?sync=true")
                    assert response.status_code == 200
                    result = response.json()
                    for index in range(len(result)):
                        assert result[index]['status'] != 'error'
                        if result[index]['status'] == 'finished':
                            assert result[index]['command_retcode'] == 0
                            assert result[index]['command'] == f"ffmpeg -i {video_2} -map 0:v -map 0:a {outputs[index]}"
                            finished = True
                    timeout -= 1
                if not finished:
                    assert False
    
    def test_pipeline_supported_audio_codecs(self):
        with TestClient(app) as client:
            response = client.get("/service")
            data = list(filter(lambda x: x['app'] == 'mers-ffmpeg', response.json()))[0]
            svc_id = data.pop("id")
            json_data = pipeline_empty.copy()
            for extension, codec in supported_audio_codecs.items():
                json_data["outputs"][0]["container"] = extension
                json_data["outputs"][0]["channels"] = [{"stream_type": "audio", "codec": codec}, {"stream_type": "video", "params": {"vn": None}}]
                response = client.post(f"/media/{svc_id}/pipeline?sync=true", json=json_data)
                assert response.status_code == 200
                pipeline_id = response.json()['id']
                outputs = response.json().get("outputs", [])
                timeout = 15
                finished = False
                while not finished and timeout:
                    time.sleep(3)
                    response = client.get(f"/media/{svc_id}/pipeline/{pipeline_id}?sync=true")
                    assert response.status_code == 200
                    result = response.json()
                    for index in range(len(result)):
                        assert result[index]['status'] != 'error'
                        if result[index]['status'] == 'finished':
                            assert result[index]['command_retcode'] == 0
                            assert result[index]['command'] == f"ffmpeg -i {video_2} -map 0:v -map 0:a -acodec {codec} -vn {outputs[index]}"
                            finished = True
                    timeout -= 1
                if not finished:
                    assert False
    
    def test_pipeline_supported_gpu_codecs(self):
        with TestClient(app) as client:
            response = client.get("/service")
            data = list(filter(lambda x: x['app'] == 'mers-ffmpeg', response.json()))[0]
            svc_id = data.pop("id")
            json_data = pipeline_empty.copy()
            for extension, codec in supported_gpu_codecs.items():
                json_data["outputs"][0]["container"] = extension
                json_data["outputs"][0]["params"] = {"vaapi_device": "/dev/dri/renderD128"}
                json_data["outputs"][0]["channels"] = [{"stream_type": "video", "codec": codec, "params": {"vf":"format=nv12,hwupload"}}]
                response = client.post(f"/media/{svc_id}/pipeline?sync=true", json=json_data)
                assert response.status_code == 200
                pipeline_id = response.json()['id']
                outputs = response.json().get("outputs", [])
                timeout = 15
                finished = False
                while not finished or timeout == 0:
                    time.sleep(3)
                    response = client.get(f"/media/{svc_id}/pipeline/{pipeline_id}?sync=true")
                    assert response.status_code == 200
                    result = response.json()
                    for index in range(len(result)):
                        assert result[index]['status'] != 'error'
                        if result[index]['status'] == 'finished':
                            assert result[index]['command_retcode'] == 0
                            assert result[index]['command'] == f"ffmpeg -i {video_2} -map 0:v -map 0:a -vaapi_device /dev/dri/renderD128 -vcodec {codec} -vf format=nv12,hwupload {outputs[index]}"
                            finished = True
                    timeout -= 1
                if not finished:
                    assert False

    def test_pipeline_ttl(self):
        with TestClient(app) as client:
            response = client.get("/service")
            data = list(filter(lambda x: x['app'] == 'mers-ffmpeg', response.json()))[0]
            svc_id = data.pop("id")
            json_data = pipeline_copy.copy()
            json_data["ttl"] = 5
            response = client.post(f"/media/{svc_id}/pipeline?sync=true", json=json_data)
            assert response.status_code == 200
            result = response.json()
            time.sleep(6)
            response = client.get(f"/media/{svc_id}/pipeline/{result['id']}?sync=true")
            assert response.status_code == 400
            assert response.json().get("status", {}).get('detail', {}).get("description") == f"Pipeline {result['id']} doesn't exist"

    def test_pipeline_azure_upload(self):
        ks = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
        bucket = os.getenv("CLOUD_STORAGE_BUCKET")
        if ks and bucket:
            with TestClient(app) as client:
                response = client.get("/service")
                data = list(filter(lambda x: x['app'] == 'mers-ffmpeg', response.json()))[0]
                svc_id = data.pop("id")
                json_data = pipeline_copy.copy()
                json_data["outputs"][0]["storage"] = [{
                    "name": "azure",
                    "bucket": bucket,
                    "env": {
                        "AZURE_STORAGE_CONNECTION_STRING": ks
                    }
                }]
                response = client.post(f"/media/{svc_id}/pipeline?sync=true", json=json_data)
                assert response.status_code == 200
                # response = client.get(f"/media/{svc_id}/pipeline/{result['id']}?sync=true")

    def test_pipeline_mpegts(self):
        with TestClient(app) as client:
            response = client.get("/service")
            data = list(filter(lambda x: x['app'] == 'mers-ffmpeg', response.json()))[0]
            svc_id = data.pop("id")
            response = client.post(f"/media/{svc_id}/pipeline?sync=true", json=pipeline_mpegts)
            assert response.status_code == 200
            pipeline_id = response.json()['id']
            outputs = response.json().get("outputs", [])
            time.sleep(30)
            response = client.get(f"/media/{svc_id}/pipeline/{pipeline_id}?sync=true")
            assert response.status_code == 200
            result = response.json()
            for index in range(len(result)):
                assert result[index]['status'] == 'running'
                assert result[index]['command'] == f"ffmpeg -re -i {video_1} -map 0:v -f mpegts -crf 30 -preset fast -vcodec libx264 {outputs[index]}"
            time.sleep(15)
            response = client.get(f"/media/{svc_id}/pipeline/{pipeline_id}?sync=true")
            assert response.status_code == 200
            result = response.json()
            for index in range(len(result)):
                assert result[index]['status'] == 'finished'

    def test_pipeline_stop(self):
        with TestClient(app) as client:
            response = client.get("/service")
            data = list(filter(lambda x: x['app'] == 'mers-ffmpeg', response.json()))[0]
            svc_id = data.pop("id")
            response = client.post(f"/media/{svc_id}/pipeline?sync=true", json=pipeline_mpegts)
            assert response.status_code == 200
            pipeline_id = response.json()['id']
            outputs = response.json().get("outputs", [])
            time.sleep(2)
            response = client.get(f"/media/{svc_id}/pipeline/{pipeline_id}?sync=true")
            assert response.status_code == 200
            result = response.json()
            for index in range(len(result)):
                assert result[index]['status'] == 'running'
                assert result[index]['command'] == f"ffmpeg -re -i {video_1} -map 0:v -f mpegts -crf 30 -preset fast -vcodec libx264 {outputs[index]}"
            time.sleep(2)
            response = client.delete(f"/media/{svc_id}/pipeline/{pipeline_id}?sync=true")
            assert response.status_code == 200
            result = response.json()
            for index in range(len(result)):
                assert result[index]['status'] == 'finished'
    
    def test_pipeline_rtmp(self):
        with TestClient(app) as client:
            response = client.get("/service")
            data = list(filter(lambda x: x['app'] == 'mers-ffmpeg', response.json()))[0]
            svc_id = data.pop("id")
            response = client.post(f"/media/{svc_id}/pipeline?sync=true", json=pipeline_rtmp)
            assert response.status_code == 200
            pipeline_id = response.json()['id']
            outputs = response.json().get("outputs", [])
            time.sleep(30)
            response = client.get(f"/media/{svc_id}/pipeline/{pipeline_id}?sync=true")
            assert response.status_code == 200
            result = response.json()
            for index in range(len(result)):
                assert outputs[index] == f"rtmp://{rtmp_ip}/live"
                assert result[index]['status'] == 'running'
                assert result[index]['command'] == f"ffmpeg -re -i {video_1} -map 0:v -f flv -crf 30 -preset fast -vcodec libx264 {outputs[index]}"
            time.sleep(15)
            response = client.get(f"/media/{svc_id}/pipeline/{pipeline_id}?sync=true")
            assert response.status_code == 200
            result = response.json()
            for index in range(len(result)):
                assert result[index]['status'] == 'finished'