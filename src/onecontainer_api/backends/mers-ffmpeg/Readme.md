# mers-ffmpeg server

This backend service exposes some ffmpeg commands as RestAPI functions using a python web framework.

In order to use the MeRS features, this service needs to be created as a docker container.

The mers-ffmpeg features include:

- File probing: the same way ffprobe works
- File transcoding into new file: using the codecs, formats and features available in MeRS (for more reference go to the [MeRS documentation page](https://intel.github.io/stacks/mers/mers.html)).
- Single input, multiple output: Currently channel/file merging is not supported.
- Asynchronous transcoding: Even asynchronous calls are supported by oneContainer API frontend calls, there was no reason to execute ffmpeg synchronously, usually video transcoding processes take too much time and http communication is not appropriate.
- Cloud storage: Transcoded files are going to be locally stored and, if specified, uploaded to GCP, AWS and/or Azure bucket storage.

Currently mers-ffmpeg does not support live streaming.

This service has been tested using the following encoders:

- libx264
- aac
- libvorbis
- pcm_s16le
- flac
- ac3
- wmav2
- h264_vaapi
- hevc_vaapi
- mjpeg_vaapi
- vp8_vaapi

This service has been tested using the following formats:

- mkv
- mp4
- mov
- m4a
- avi
- webm
- wmv
- vob
- ogg

## Start service

This service can be deployed as part of the oneContainer API launch process, this configuration can be found in the `src/onecontainer-api/config.py` file. There you can find all backend services deployed.

Just launch the frontend API service and locate your backend services using `docker ps`, the backend services used by oneContainer API have a `oca_` prefix. This service will be named `oca_mers-ffmpeg`.

### Create service independently (Optional)

To create the image and run the service without launching oneContainer API backend deployments, execute following commands:

```bash
docker build -f Dockerfile -t mers-ffmpeg .
docker run -ti -d --name=oca_mers-ffmpeg mers-ffmpeg
```

## GPU device passthrough

MeRS supports GPU transcoding, by default oneContainer API launch deployments will automatically map the GPU device to the container, but if you are creating this service manually and want to include GPU capabilities in your container, then run the command as follows:

```bash
docker run -ti -d --name=oca_mers-ffmpeg --device=/dev/dri --env QSV_DEVICE=/dev/dri/renderD128 mers-ffmpeg
```

### Issues troubleshooting

- In some cases, the MeRS container won't have r/w access to the GPU device. As a workaround for safe environments you can change the permissions with the following command before starting the service: `sudo chmod 666 /dev/dri/renderD128`

## Kill service

```bash
docker stop oca_mers-ffmpeg
docker rm oca_mers-ffmpeg
```

## API Reference for Pipelines explained

This is a Pipeline definition as shown in the Swagger auto documentation. If you want to interact with this service, launch oneContainer API and go to the [documentation page](http://127.0.0.1:8000/docs#/service_api/transcode_media__service_id__pipeline_post)

```
Pipeline{
input_file*	InputFile{
            source* 	string
                        title: Source
            start_time	integer
                        title: Start Time
            duration	integer
                        title: Duration
            }
outputs*	Outputs[
            title: Outputs
            Output{
                container*	string
                            title: Container
                params	    Params{}
                channels	Channels[
                            title: Channels
                            Channel{
                            stream_type*	string
                                            title: Stream Type
                            codec	        string
                                            title: Codec
                            params	        Params{}
                            codec_params	Codec Params{}
                            filters	        Filters{< * >:	{}}
                            }]
                storage 	Storage[
                            title: Storage
                            CloudStore{
                            name*	string
                                    title: Name
                            bucket*	string
                                    title: Bucket
                            env*	Env{< * >:	string}
                            }]
            }]
ttl	        integer
            title: Ttl
            default: 300
}
```

The fields marked with an asterisk `*` are considered mandatory fields.

### Cloud Storage

For every output file, you can opt to upload result to the cloud using the field `storage`. This field is a list of `CloudStore` definitions, meaning that you can upload the same result file to multiple CSPs or buckets.

Valid names for `CloudStore.name` are `"gcp"`, `"aws"` and `"azure"`.

The `CouldStore.env` field is used for authenticating to the corresponding CSP in the format `{<name>:<value>}`, here is a list of the environment variable names required for each CSP:

- gcp: `""`
- aws: `""`
- azure: `"AZURE_STORAGE_CONNECTION_STRING"`

### Result retention period

Transcoding resulting media file and the CLI output are being locally stored in the container file system, by default these files will remain for 5 minutes after all outputs processes are finished, you can change this behavior by using the `ttl` field.

The value of `ttl` indicates the number of seconds to keep the references and files of the outputs, if you want the files to remain forever, use the value `null`. (Using the value `0` will delete files immediately).

This mechanism is only valid for locally stored files. Media files uploaded to the cloud won't be deleted regardless of the `ttl` value. If you upload the resulting file to the cloud you can look at it using your cloud management tool, however the CLI output will only be visible using mers-ffmpeg server before the `ttl` period is reached.

### Params and filters

Params can be used for channels, formats and codecs.

For information about ffmpeg format parameters go to the [FFmpeg Formats Documentation](https://ffmpeg.org/ffmpeg-formats.html), each container format has its own parameters.

For information about ffmpeg codec parameters, go to the [FFmpeg Codecs Documentation](https://ffmpeg.org/ffmpeg-codecs.html), each encoder has its own parameters.

For information about channel options, go to the [Options section in the ffmpeg Documentation](https://ffmpeg.org/ffmpeg.html#toc-Options).

The format for the `params` field is `key:value` where key is the name of the parameter and value can be a string or a number. In case there is a parameter that requires no value (a flag), just set the value as `null`.

Filters are used to modify the channel stream and require reencoding. For information about filters go to the [FFmpeg Filters Documentation](https://ffmpeg.org/ffmpeg-filters.html).

The format for `filters` field is `key:value` where key is the filter name and value can be one of the following:

- A string corresponding to the value of the filter
- An object in the format `key:value` where key is the name of a sub parameter for the filter, and value can be a string or a number.
- An empty object `{}` when the filter has no values (a flag).

## API Examples

### Check status

Let's check the health status of the service `venomesi`

```bash
curl -X GET localhost:8000/service/venomesi/heartbeat | python3 -m json.tool
```

Output:

```bash
{
    "status": "ok"
}
```

### File probing

```bash
curl -X POST -H "Content-Type: application/json" -d '{"source": "http://172.17.0.1:5553/sample-videos/fruit-and-vegetable-detection.mp4"}' localhost:8000/media/venomesi/probe?sync=true | python3 -m json.tool
```

Output:

```bash
{
    "streams": [
        {
            "index": 0,
            "codec_name": "h264",
            "codec_long_name": "H.264 / AVC / MPEG-4 AVC / MPEG-4 part 10",
            "profile": "High",
            "codec_type": "video",
            "codec_time_base": "1001/120000",
            "codec_tag_string": "avc1",
            "codec_tag": "0x31637661",
            "width": 960,
            "height": 540,
            "coded_width": 960,
            "coded_height": 544,
            "closed_captions": 0,
            "has_b_frames": 0,
            "sample_aspect_ratio": "1:1",
            "display_aspect_ratio": "16:9",
            "pix_fmt": "yuv420p",
            "level": 32,
            "color_range": "tv",
            "color_space": "bt709",
            "color_transfer": "bt709",
            "color_primaries": "bt709",
            "chroma_location": "left",
            "field_order": "progressive",
            "refs": 1,
            "is_avc": "true",
            "nal_length_size": "4",
            "r_frame_rate": "60000/1001",
            "avg_frame_rate": "60000/1001",
            "time_base": "1/60000",
            "start_pts": 0,
            "start_time": "0.000000",
            "duration_ts": 3636633,
            "duration": "60.610550",
            "bit_rate": "2335818",
            "bits_per_raw_sample": "8",
            "nb_frames": "3633",
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
                "creation_time": "2018-06-15T21:05:12.000000Z",
                "language": "und",
                "handler_name": "Core Media Video"
            }
        }
    ],
    "format": {
        "filename": "http://172.17.0.1:5553/sample-videos/fruit-and-vegetable-detection.mp4",
        "nb_streams": 1,
        "nb_programs": 0,
        "format_name": "mov,mp4,m4a,3gp,3g2,mj2",
        "format_long_name": "QuickTime / MOV",
        "start_time": "0.000000",
        "duration": "60.610550",
        "size": "17760065",
        "bit_rate": "2344154",
        "probe_score": 100,
        "tags": {
            "major_brand": "mp42",
            "minor_version": "1",
            "compatible_brands": "mp41mp42isom",
            "creation_time": "2018-06-15T21:05:12.000000Z"
        }
    }
}
```

### Video transcoding using libx264

```bash
curl -X POST -H "Content-Type: application/json" -d '{"input_file": {"source": "http://172.17.0.1:5553/sample-videos/bottle-detection.mp4"}, "outputs": [{"container": "mkv", "channels": [{"stream_type": "video", "codec": "libx264", "codec_params": {"preset": "ultrafast", "tune": "film", "crf": "30"}}]}]}' localhost:8000/media/venomesi/pipeline?sync=true | python3 -m json.tool
```

Output:

```bash
{
    "id": "tesavihoya",
    "outputs": [
        {
            "id": "naxemera.mkv",
            "command": "ffmpeg -i http://172.17.0.1:5553/sample-videos/bottle-detection.mp4 -map 0:v -crf 30 -preset ultrafast -tune film -vcodec libx264 naxemera.mkv",
            "status": "running",
            "command_output": null,
            "command_retcode": null
        }
    ]
}
```

### Get CLI output after transcoding finishes

```bash
curl -X GET localhost:8000/media/venomesi/pipeline/tesavihoya?sync=true | python3 -m json.tool
```

Output:

```bash
[
    {
        "id": "naxemera.mkv",
        "command": "ffmpeg -i http://172.17.0.1:5553/sample-videos/bottle-detection.mp4 -map 0:v -crf 30 -preset ultrafast -tune film -vcodec libx264 naxemera.mkv",
        "status": "finished",
        "command_output": [
            "Input #0, mov,mp4,m4a,3gp,3g2,mj2, from 'http://172.17.0.1:5553/sample-videos/bottle-detection.mp4':\n",
            "  Metadata:\n",
            "    major_brand     : isom\n",
            "    minor_version   : 512\n",
            "    compatible_brands: isomiso2avc1mp41\n",
            "    encoder         : Lavf57.77.100\n",
            "  Duration: 00:00:39.86, start: 0.000000, bitrate: 101 kb/s\n",
            "    Stream #0:0(eng): Video: h264 (High) (avc1 / 0x31637661), yuv420p, 640x360 [SAR 1:1 DAR 16:9], 98 kb/s, 29.83 fps, 29.83 tbr, 11456 tbn, 59.67 tbc (default)\n",
            "    Metadata:\n",
            "      handler_name    : VideoHandler\n",
            "Stream mapping:\n",
            "  Stream #0:0 -> #0:0 (h264 (native) -> h264 (libx264))\n",
            "Press [q] to stop, [?] for help\n",
            "[libx264 @ 0x56242a51f3b0] using SAR=1/1\n",
            "[libx264 @ 0x56242a51f3b0] using cpu capabilities: MMX2 SSE2Fast SSSE3 SSE4.2 AVX FMA3 BMI2 AVX2\n",
            "[libx264 @ 0x56242a51f3b0] profile Constrained Baseline, level 3.0, 4:2:0, 8-bit\n",
            "[libx264 @ 0x56242a51f3b0] 264 - core 159 r2991 1771b55 - H.264/MPEG-4 AVC codec - Copyleft 2003-2019 - http://www.videolan.org/x264.html - options: cabac=0 ref=1 deblock=0:-1:-1 analyse=0:0 me=dia subme=0 psy=1 psy_rd=1.00:0.15 mixed_ref=0 me_range=16 chroma_me=1 trellis=0 8x8dct=0 cqm=0 deadzone=21,11 fast_pskip=1 chroma_qp_offset=0 threads=11 lookahead_threads=1 sliced_threads=0 nr=0 decimate=1 interlaced=0 bluray_compat=0 constrained_intra=0 bframes=0 weightp=0 keyint=250 keyint_min=25 scenecut=0 intra_refresh=0 rc=crf mbtree=0 crf=30.0 qcomp=0.60 qpmin=0 qpmax=69 qpstep=4 ip_ratio=1.40 aq=0\n",
            "Output #0, matroska, to 'naxemera.mkv':\n",
            "  Metadata:\n",
            "    major_brand     : isom\n",
            "    minor_version   : 512\n",
            "    compatible_brands: isomiso2avc1mp41\n",
            "    encoder         : Lavf58.62.100\n",
            "    Stream #0:0(eng): Video: h264 (libx264) (H264 / 0x34363248), yuv420p, 640x360 [SAR 1:1 DAR 16:9], q=-1--1, 29.83 fps, 1k tbn, 29.83 tbc (default)\n",
            "    Metadata:\n",
            "      handler_name    : VideoHandler\n",
            "      encoder         : Lavc58.111.100 libx264\n",
            "    Side data:\n",
            "      cpb: bitrate max/min/avg: 0/0/0 buffer size: 0 vbv_delay: N/A\n",
            "frame= 1152 fps=0.0 q=25.0 size=     512kB time=00:00:38.18 bitrate= 109.9kbits/s speed=76.2x    \n",
            "frame= 1189 fps=0.0 q=-1.0 Lsize=     754kB time=00:00:39.82 bitrate= 155.2kbits/s speed=76.7x    \n",
            "video:745kB audio:0kB subtitle:0kB other streams:0kB global headers:0kB muxing overhead: 1.216693%\n",
            "[libx264 @ 0x56242a51f3b0] frame I:5     Avg QP:22.80  size:  6983\n",
            "[libx264 @ 0x56242a51f3b0] frame P:1184  Avg QP:24.66  size:   614\n",
            "[libx264 @ 0x56242a51f3b0] mb I  I16..4: 100.0%  0.0%  0.0%\n",
            "[libx264 @ 0x56242a51f3b0] mb P  I16..4:  6.5%  0.0%  0.0%  P16..4: 10.8%  0.0%  0.0%  0.0%  0.0%    skip:82.7%\n",
            "[libx264 @ 0x56242a51f3b0] coded y,uvDC,uvAC intra: 5.6% 13.7% 0.8% inter: 2.6% 1.7% 0.0%\n",
            "[libx264 @ 0x56242a51f3b0] i16 v,h,dc,p: 31% 36% 16% 16%\n",
            "[libx264 @ 0x56242a51f3b0] i8c dc,h,v,p: 58% 22% 18%  3%\n",
            "[libx264 @ 0x56242a51f3b0] kb/s:153.05\n"
        ],
        "command_retcode": 0
    }
]
```