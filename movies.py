import json
import struct
import subprocess
import tempfile
from pathlib import Path
from patchlib import ROOT

def probe(binary, movie):
    fields = "packet=stream_index,pts,data_hash:stream=index,codec_type,codec_name,width,height,profile,time_base:format=duration"
    return json.loads(subprocess.check_output([
        str(binary), "-v", "error", "-show_packets", "-show_data_hash", "sha256",
        "-show_entries", fields, "-of", "json", str(movie)]))

def render(original, target, ffmpeg):
    sub = ROOT/"subtitles"
    name = original.stem
    times = json.loads((sub/"timings.json").read_text())[name] if name in ("opening","prologue","tm_felion_D") else []
    filters = [f"removelogo=f=mask-{name}-{i}.png:enable='between(t,{max(0,a-.42):.3f},{b+.42:.3f})'"
               for i,(a,b) in enumerate(times)]
    filters.append(f"ass={name}.ass")
    ffprobe = ffmpeg.with_name("ffprobe.exe")
    before = probe(ffprobe, original)
    video = next(s for s in before["streams"] if s["codec_type"]=="video")
    if (video["width"],video["height"],video["time_base"]) != (1920,1080,"1/1000"):
        raise ValueError(f"Unsupported movie profile: {name}")
    with tempfile.TemporaryDirectory(dir=target.parent) as temp:
        stamps = Path(temp)/"pts.bin"
        stamps.write_bytes(b"".join(struct.pack("<Q", int(p["pts"])*10000)
                            for p in before["packets"] if p["stream_index"]==video["index"]))
        args = [str(ffmpeg), "-nostdin","-v","error","-threads","3","-i",str(original),
                "-map","0:v:0","-an","-vf",",".join(filters),"-filter_threads","2",
                "-pix_fmt","yuv420p","-fps_mode","passthrough","-threads","1","-f","rawvideo","-"]
        with subprocess.Popen(args,cwd=sub,stdout=subprocess.PIPE) as proc:
            try:
                subprocess.run([str(ROOT/"tools/write_movie.exe"),str(original),str(target),str(stamps)],
                               stdin=proc.stdout,check=True)
            finally:
                proc.stdout.close()
            if proc.wait():
                raise RuntimeError(f"FFmpeg failed: {name}")
    after = probe(ffprobe,target)
    if before["streams"]!=after["streams"]:
        raise ValueError(f"Movie stream layout changed: {name}")
    for stream in before["streams"]:
        def packets(info):
            return [p for p in info["packets"] if p["stream_index"]==stream["index"]]
        a,b=packets(before),packets(after)
        if len(a)!=len(b) or any(abs(x["pts"]-y["pts"])>2 for x,y in zip(a,b)):
            raise ValueError(f"Movie timing mismatch: {name}")
        if stream["codec_type"]=="audio" and any(x["data_hash"]!=y["data_hash"] for x,y in zip(a,b)):
            raise ValueError(f"Audio mismatch: {name}")
