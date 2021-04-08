# Getting started

This section documents the first steps on how to use oneContainer API. It is required that the oneContainer API frontend server is up and running; for installation instructions go to the [Installation section](../Readme.md#Installation)

## Verifying services are running

The oneContainer API installation creates a frontend web server, a queuing service and some optional default backend services with docker containers.

This containers will be created within a bridged virtual network named `oca_network` which has the subnet `10.5.0.0/16` and the names will start with the prefix `oca_`.

### The queuing service

To see the queuing service containers that are running, execute the following command:

```bash
docker ps --filter "label=com.docker.compose.project=async_queue"
```

There you can see the queue API, the queue dashboard which can be accessed via http by a web browser, and a Redis* server to manage queue data.

### Default backend services

By default, oneContainer API installs and registers 2 backend services.  The definition of those services are described in the `INITIAL_SERVICES` variable at the end of `config.py` file.

To see the default backend services created after oneContainer API launch, execute the following command:

```bash
docker ps --filter "label=oca_service=default_backend"
```

In this case there is a custom dlrs-pytorch-torchub service built within the oneContainer API source code, and an Apache Cassandra* service from Docker Hub*.

**Note: If you don't want to install the default backend services, run oneContainer API with the `BACKEND_CREATE_ON_START=0` environment variable**

**Note: The services will remain live even if oneContainer API is torn down. This will keep data persistency when you raise oneContainer API again.**

### The frontend API

oneContainer API follows the standard OpenAPI* version 3 and by default, FastAPI* uses Swagger* UI to interact with the API reference. This application can be accessed with the following URL:

`http://localhost:8000/docs`

There you can interact with the frontend API using a web browser.

If you want to use cURL to ineract with the API, we have provided a set of scripts used in this demonstration in the `demo` directory and the usage is described in the following sections.

## The management API endpoints

The management API is used to configure and read oneContainer API database to prepare it for service requests. Here is a list of useful commands you can use for the management API:

### List available services

To list the available services that can be consumed using oneContainer-api, use a `GET` call to `/service/`:

```bash
curl -X GET localhost:8000/service/ | python3 -m json.tool
```

The output looks like:

```bash
[
    {
        "description": "Builtin backend service",
        "driver": "datastax-cassandra-driver-3.24.0",
        "name": "oca_cassandra",
        "version": "v1",
        "app": "cassandra:latest",
        "app_version": "3.11.9",
        "locations": {
            "node1": "10.5.0.1:5551"
        },
        "meta": {},
        "id": "qulezawi"
    },
    {
        "description": "Builtin backend service",
        "driver": "dlrs-torchub-driver-0.1.0",
        "name": "oca_dlrs-pytorch-torchub",
        "version": "v1",
        "app": "dlrs-pytorch-torchub",
        "app_version": "0.1.0",
        "locations": {
            "node1": "10.5.0.1:5550"
        },
        "meta": {},
        "id": "sufiyopa"
    },
    {
        "description": "Builtin backend service",
        "driver": "mers-ffmpeg-driver-0.1.0",
        "name": "oca_mers-ffmpeg",
        "version": "v1",
        "app": "mers-ffmpeg",
        "app_version": "0.1.0",
        "locations": {
            "node1": "10.5.0.1:5552"
        },
        "meta": {},
        "id": "venomesi"
    }
]
```

As seen above, the default services enabled are a single Deep Learning Inference backend (dlrs-pytorch-torchub) and a backend for Cassandra DB (cassandra). Both of the services have been launched at startup and are running at ip `10.5.0.1` on ports 5550 and 5551 respectively. Each of the services have unique ids, that need to be used with all the other calls below.

### Check service

Let's check the health status of the service `sufiyopa`

```bash
curl -X GET localhost:8000/service/sufiyopa/heartbeat | python3 -m json.tool
```

Output:

```bash
{
    "status": "ok"
}
```

The service seems to be working!

## Deep Learning API functions

This service API will use the service `sufiyopa` listed in the available services above.

### Classification models from torchub

A default backend for serving torchub models is shipped along with oneContainer-API. To interact with the model server, oneContainer-API can be used as shown below.

### Load model

Using the `/serve` API we can load and serve the models, to load a model a payload description file is required, the format of which looks like:

```bash
{
    "path": <model_path>,
    "name": <model_name>,
    "kwargs": <{any meta args that has to be passed}>
}
```

Let's use the API to load a `resnet18` model:

```bash
curl -X POST -d @model.json localhost:8000/ai/sufiyopa/serve | python3 -m json.tool
```

Where `model.json` payload looks like:

```bash
{
    "path": "pytorch/vision:v0.6.0",
    "name": "resnet18",
    "kwargs": {"pretrained": true}
}
```

This will generate an output like:

```bash
{
    "id": "6ad1fd81-3f7e-4579-bf4a-5a7e4e249095",
    "status": "queued",
    "queue": "oca_dlrs-pytorch-torchub",
    "position": 0
}
```

This output contains an `id` field for the job which has been queued, this value can be used to query the result:

```bash
curl -X GET localhost:8000/job/6ad1fd81-3f7e-4579-bf4a-5a7e4e249095 | python3 -m json.tool
```

Output:

```bash
{
    "status": "finished",
    "queue": "oca_dlrs-pytorch-torchub",
    "position": null,
    "result": {
        "status": "ok",
        "result": "model resnet18 loading in progress"
    }
}
```

After some minutes, the model will load in the dlrs-pytorch-torchub service, then you can execute image inference as shown in the following section.

### Test model

Let's predict using the loaded model:

```bash
curl -X POST -F image_file=@cat.jpg localhost:8000/ai/sufiyopa/predict | python3 -m json.tool
```

Output:

```bash
{
    "id": "572c0648-fdef-49d9-8bdf-8546f042f8cb",
    "status": "queued",
    "queue": "oca_dlrs-pytorch-torchub",
    "position": null
}
```

Using the job id:

```bash
curl -X GET localhost:8000/job/572c0648-fdef-49d9-8bdf-8546f042f8cb | python3 -m json.tool
```

Output:

```bash
{
    "status": "finished",
    "queue": "oca_dlrs-pytorch-torchub",
    "position": null,
    "result": {
        "results": [
            {
                "status": "ok",
                "result": "indri"
            }
        ]
    }
}
```


## Media API functions

This service API will use the service `venomesi` listed in the available services above.

### Video/audio transcoding using ffmpeg pipelines

A default backend for transcoding ffmpeg pipelines is shipped along with oneContainer-API. To interact with the ffmpeg service, oneContainer-API can be used as described below. All calls to the mers-ffmpeg backend are asynchronous and there is no need to use the queuing service, for this reason we have included the parameter `sync=true` in all of the API calls.

For further reference of the mers-ffmpeg backend, please go to the [mers-ffmpeg Readme.md file](../src/onecontainer_api/backends/mers-ffmpeg/Readme.md)

### Read file metadata info

Using the `/probe` API we can read file metadata, this requires a file source description, the format of which looks like:

```bash
{
    "source": <file_source>
}
```

Let's use the API to get the info of a file in an Azure storage bucket:

```bash
curl -X POST -d @video_source.json localhost:8000/media/venomesi/probe?sync=true | python3 -m json.tool
```

Where `video_source.json` payload looks like:

```bash
{
    "source": "https://ocapimedia.blob.core.windows.net/videospublic/big_buck_bunny_720p_surround.mp4"
}
```

This will generate an output like:

```bash
{
    "streams": [
        {
            "index": 0,
            "codec_name": "h264",
            "codec_long_name": "H.264 / AVC / MPEG-4 AVC / MPEG-4 part 10",
            "profile": "Constrained Baseline",
            "codec_type": "video",
            "codec_time_base": "1/48",
            "codec_tag_string": "avc1",
            "codec_tag": "0x31637661",
            "width": 640,
            "height": 360,
            "coded_width": 640,
            "coded_height": 368,
            "closed_captions": 0,
            "has_b_frames": 0,
            "sample_aspect_ratio": "1:1",
            "display_aspect_ratio": "16:9",
            "pix_fmt": "yuv420p",
            "level": 30,
            "chroma_location": "left",
            "refs": 1,
            "is_avc": "true",
            "nal_length_size": "4",
            "r_frame_rate": "24/1",
            "avg_frame_rate": "24/1",
            "time_base": "1/12288",
            "start_pts": 0,
            "start_time": "0.000000",
            "duration_ts": 7329280,
            "duration": "596.458333",
            "bit_rate": "697070",
            "bits_per_raw_sample": "8",
            "nb_frames": "14315",
            "disposition": {
                "default": 1,
                "dub": 0,
                "original": 0,
                "comment": 0,
                "lyrics": 0,
                "karaoke": 0,
                "forced": 0,
                "hearing_impaired": 0,
                "visual_impaired": 0,
                "clean_effects": 0,
                "attached_pic": 0,
                "timed_thumbnails": 0
            },
            "tags": {
                "language": "und",
                "handler_name": "VideoHandler"
            }
        },
        {
            "index": 1,
            "codec_name": "aac",
            "codec_long_name": "AAC (Advanced Audio Coding)",
            "profile": "LC",
            "codec_type": "audio",
            "codec_time_base": "1/44100",
            "codec_tag_string": "mp4a",
            "codec_tag": "0x6134706d",
            "sample_fmt": "fltp",
            "sample_rate": "44100",
            "channels": 2,
            "channel_layout": "stereo",
            "bits_per_sample": 0,
            "r_frame_rate": "0/0",
            "avg_frame_rate": "0/0",
            "time_base": "1/44100",
            "start_pts": 0,
            "start_time": "0.000000",
            "duration_ts": 26304768,
            "duration": "596.480000",
            "bit_rate": "128209",
            "max_bit_rate": "128209",
            "nb_frames": "25690",
            "disposition": {
                "default": 1,
                "dub": 0,
                "original": 0,
                "comment": 0,
                "lyrics": 0,
                "karaoke": 0,
                "forced": 0,
                "hearing_impaired": 0,
                "visual_impaired": 0,
                "clean_effects": 0,
                "attached_pic": 0,
                "timed_thumbnails": 0
            },
            "tags": {
                "language": "und",
                "handler_name": "SoundHandler"
            }
        }
    ],
    "format": {
        "filename": "https://ocapimedia.blob.core.windows.net/videospublic/big_buck_bunny_720p_surround.mp4",
        "nb_streams": 2,
        "nb_programs": 0,
        "format_name": "mov,mp4,m4a,3gp,3g2,mj2",
        "format_long_name": "QuickTime / MOV",
        "start_time": "0.000000",
        "duration": "596.504000",
        "size": "61878609",
        "bit_rate": "829883",
        "probe_score": 100,
        "tags": {
            "major_brand": "isom",
            "minor_version": "512",
            "compatible_brands": "isomiso2avc1mp41",
            "title": "Big Buck Bunny - https://archive.org/details/BigBuckBunny_124",
            "encoder": "Lavf55.45.100",
            "comment": "license:http://creativecommons.org/licenses/by/3.0/"
        }
    }
}
```

### Execute a transcoding pipeline

We will be using the same file as input for transcoding. A pipeline is defined by the following fields:

```bash
{
  "input_file": {
    "source": <file_source>,
    "start_time": <{start_time}>,
    "duration": <{duration}>
  },
  "outputs": [
    {
      "container": <mkv|mp4|webm|...>,
      "channels": [
        {
          "stream_type": <video|audio|subtitle>,
          "codec": <codec_name>,
          "codec_params": {<param_name>: <param_value>},
          "filters": {filter_name>: <filter_value>}
        }
      ],
      "storage": [
        {
          "name": <gcp|aws|azure>,
          "bucket": <bucket_name>,
          "env": {<env_var_name>: <env_var_value>}
        }
      ]
    }
  ]
}
```

Let's create a pipeline to re-encode the video for 10 seconds starting on second 15th using a libx264 with a fast preset and a crf of 23, also let's reduce video size by the half and add a black and white effect:

```bash
curl -X POST -d @pipeline.json localhost:8000/media/venomesi/pipeline?sync=true | python3 -m json.tool
```

Where pipeline.json looks like this:

```bash
{
  "input_file": {
    "source": "https://ocapimedia.blob.core.windows.net/videospublic/big_buck_bunny_720p_surround.mp4",
    "start_time": 15,
    "duration": 10
  },
  "outputs": [
    {
      "container": "mkv",
      "channels": [
        {
          "stream_type": "video",
          "codec": "libx264",
          "codec_params": {
            "preset": "fast",
            "crf": "23"
          },
          "filters": {
            "scale": {
              "w": "iw/2",
              "h": -1
            },
            "hue": {
              "s": 0
            }
          }
        }
      ],
      "storage": [
        {
          "name": "azure",
          "bucket": "videospublic",
          "env": {
            "AZURE_STORAGE_CONNECTION_STRING": "Hidden for security purposes"
          }
        }
      ]
    }
  ]
}
```

The output should look like this:

```bash
{
    "id": "zasacodadu",
    "outputs": [
        {
            "id": "wacicebu.mkv",
            "command": "ffmpeg -ss 15 -t 10 -i https://ocapimedia.blob.core.windows.net/videospublic/big_buck_bunny_720p_surround.mp4 -filter_complex [0:v]scale=h=-1:w=iw/2[s0];[s0]hue=s=0[s1] -map [s1] -map 0:a -crf 23 -preset fast -vcodec libx264 wacicebu.mkv",
            "status": "running",
            "command_output": null,
            "command_retcode": null
        }
    ]
}
```

This output is the definition of a pipeline job, it's identified by an ID, in this case is `zasacodadu`, the pipeline output name will be randomly assigned, in this case is `wacicebu.mkv`

### Get the status of a pipeline job

To get the pipeline job, we will be executing:

```bash
curl localhost:8000/media/venomesi/pipeline/zasacodadu?sync=true | python3 -m json.tool
```

After job finishes, we will see an output like the following:

```bash
[
    {
        "id": "wacicebu.mkv",
        "command": "ffmpeg -ss 15 -t 10 -i https://ocapimedia.blob.core.windows.net/videospublic/big_buck_bunny_720p_surround.mp4 -filter_complex [0:v]scale=h=-1:w=iw/2[s0];[s0]hue=s=0[s1] -map [s1] -map 0:a -crf 23 -preset fast -vcodec libx264 wacicebu.mkv",
        "status": "finished",
        "command_output": [
            "Input #0, mov,mp4,m4a,3gp,3g2,mj2, from 'https://ocapimedia.blob.core.windows.net/videospublic/big_buck_bunny_720p_surround.mp4':\n",
            "  Metadata:\n",
            "    major_brand     : isom\n",
            "    minor_version   : 512\n",
            "    compatible_brands: isomiso2avc1mp41\n",
            "    title           : Big Buck Bunny - https://archive.org/details/BigBuckBunny_124\n",
            "    encoder         : Lavf55.45.100\n",
            "    comment         : license:http://creativecommons.org/licenses/by/3.0/\n",
            "  Duration: 00:09:56.50, start: 0.000000, bitrate: 829 kb/s\n",
            "    Stream #0:0(und): Video: h264 (Constrained Baseline) (avc1 / 0x31637661), yuv420p, 640x360 [SAR 1:1 DAR 16:9], 697 kb/s, 24 fps, 24 tbr, 12288 tbn, 48 tbc (default)\n",
            "    Metadata:\n",
            "      handler_name    : VideoHandler\n",
            "    Stream #0:1(und): Audio: aac (LC) (mp4a / 0x6134706D), 44100 Hz, stereo, fltp, 128 kb/s (default)\n",
            "    Metadata:\n",
            "      handler_name    : SoundHandler\n",
            "Stream mapping:\n",
            "  Stream #0:0 (h264) -> scale (graph 0)\n",
            "  hue (graph 0) -> Stream #0:0 (libx264)\n",
            "  Stream #0:1 -> #0:1 (aac (native) -> vorbis (libvorbis))\n",
            "Press [q] to stop, [?] for help\n",
            "[libx264 @ 0x5565c179c3a0] using SAR=1/1\n",
            "[libx264 @ 0x5565c179c3a0] using cpu capabilities: MMX2 SSE2Fast SSSE3 SSE4.2 AVX FMA3 BMI2 AVX2\n",
            "[libx264 @ 0x5565c179c3a0] profile High, level 1.2, 4:2:0, 8-bit\n",
            "[libx264 @ 0x5565c179c3a0] 264 - core 159 r2991 1771b55 - H.264/MPEG-4 AVC codec - Copyleft 2003-2019 - http://www.videolan.org/x264.html - options: cabac=1 ref=2 deblock=1:0:0 analyse=0x3:0x113 me=hex subme=6 psy=1 psy_rd=1.00:0.00 mixed_ref=1 me_range=16 chroma_me=1 trellis=1 8x8dct=1 cqm=0 deadzone=21,11 fast_pskip=1 chroma_qp_offset=-2 threads=6 lookahead_threads=1 sliced_threads=0 nr=0 decimate=1 interlaced=0 bluray_compat=0 constrained_intra=0 bframes=3 b_pyramid=2 b_adapt=1 b_bias=0 direct=1 weightb=1 open_gop=0 weightp=1 keyint=250 keyint_min=24 scenecut=40 intra_refresh=0 rc_lookahead=30 rc=crf mbtree=1 crf=23.0 qcomp=0.60 qpmin=0 qpmax=69 qpstep=4 ip_ratio=1.40 aq=1:1.00\n",
            "Output #0, matroska, to 'wacicebu.mkv':\n",
            "  Metadata:\n",
            "    major_brand     : isom\n",
            "    minor_version   : 512\n",
            "    compatible_brands: isomiso2avc1mp41\n",
            "    title           : Big Buck Bunny - https://archive.org/details/BigBuckBunny_124\n",
            "    comment         : license:http://creativecommons.org/licenses/by/3.0/\n",
            "    encoder         : Lavf58.62.100\n",
            "    Stream #0:0: Video: h264 (libx264) (H264 / 0x34363248), yuv420p, 320x180 [SAR 1:1 DAR 16:9], q=-1--1, 24 fps, 1k tbn, 24 tbc (default)\n",
            "    Metadata:\n",
            "      encoder         : Lavc58.111.100 libx264\n",
            "    Side data:\n",
            "      cpb: bitrate max/min/avg: 0/0/0 buffer size: 0 vbv_delay: N/A\n",
            "    Stream #0:1(und): Audio: vorbis (libvorbis) (oV[0][0] / 0x566F), 44100 Hz, stereo, fltp (default)\n",
            "    Metadata:\n",
            "      handler_name    : SoundHandler\n",
            "      encoder         : Lavc58.111.100 libvorbis\n",
            "frame=    0 fps=0.0 q=0.0 size=       5kB time=00:00:00.38 bitrate= 103.9kbits/s speed=0.776x    \n",
            "frame=  240 fps=0.0 q=-1.0 Lsize=     262kB time=00:00:09.98 bitrate= 215.1kbits/s speed=10.1x    \n",
            "video:125kB audio:128kB subtitle:0kB other streams:0kB global headers:4kB muxing overhead: 3.977955%\n",
            "[libx264 @ 0x5565c179c3a0] frame I:3     Avg QP:20.04  size: 10478\n",
            "[libx264 @ 0x5565c179c3a0] frame P:144   Avg QP:24.21  size:   556\n",
            "[libx264 @ 0x5565c179c3a0] frame B:93    Avg QP:30.31  size:   165\n",
            "[libx264 @ 0x5565c179c3a0] consecutive B-frames: 42.9% 13.3%  8.8% 35.0%\n",
            "[libx264 @ 0x5565c179c3a0] mb I  I16..4:  6.7% 47.2% 46.1%\n",
            "[libx264 @ 0x5565c179c3a0] mb P  I16..4:  0.1%  0.7%  0.5%  P16..4: 16.8% 10.9%  6.4%  0.0%  0.0%    skip:64.6%\n",
            "[libx264 @ 0x5565c179c3a0] mb B  I16..4:  0.1%  0.7%  0.6%  B16..8:  5.6%  3.0%  0.4%  direct: 1.0%  skip:88.5%  L0:45.7% L1:38.6% BI:15.6%\n",
            "[libx264 @ 0x5565c179c3a0] 8x8 transform intra:49.5% inter:54.0%\n",
            "[libx264 @ 0x5565c179c3a0] coded y,uvDC,uvAC intra: 82.5% 0.0% 0.0% inter: 8.8% 0.0% 0.0%\n",
            "[libx264 @ 0x5565c179c3a0] i16 v,h,dc,p: 13% 51% 11% 25%\n",
            "[libx264 @ 0x5565c179c3a0] i8 v,h,dc,ddl,ddr,vr,hd,vl,hu: 15% 20% 13%  5%  9%  8% 10%  9% 11%\n",
            "[libx264 @ 0x5565c179c3a0] i4 v,h,dc,ddl,ddr,vr,hd,vl,hu: 24% 19% 15%  5%  8%  7%  8%  6%  8%\n",
            "[libx264 @ 0x5565c179c3a0] i8c dc,h,v,p: 100%  0%  0%  0%\n",
            "[libx264 @ 0x5565c179c3a0] Weighted P-Frames: Y:0.0% UV:0.0%\n",
            "[libx264 @ 0x5565c179c3a0] ref P L0: 80.1% 19.9%\n",
            "[libx264 @ 0x5565c179c3a0] ref B L0: 86.7% 13.3%\n",
            "[libx264 @ 0x5565c179c3a0] ref B L1: 97.5%  2.5%\n",
            "[libx264 @ 0x5565c179c3a0] kb/s:101.47\n"
        ],
        "command_retcode": 0
    }
]
```

Then we can verify our Azure storage bucket and look for the `wacicebu.mkv` file.
