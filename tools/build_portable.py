"""Build the offline Windows x64 release from the tagged patch and pinned upstream files."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import zipfile

ROOT = Path(__file__).resolve().parents[1]
PINNED = {
    "python.zip": "97dae5274cc54867065e8d5a3226e48c35017ed332a0fdb0e27d5b5821961297",
    "pillow.whl": "9dda0788a9932776a75d8bcc020076edc308ce2508b51f6739a45e3158b3fc42",
    "gust_tools.zip": "49a850357b4aa4399a9fc4a1be5ed331d6456d585213792e89527daf75a183ad",
    "ffmpeg.zip": "f7697c270197c04bf72759c65ada64fcaea663bcb80767c390752d2412ea2dcf",
}

def pinned(folder, name):
    path = folder / name
    with path.open("rb") as stream:
        if hashlib.file_digest(stream, "sha256").hexdigest() != PINNED[name]:
            raise ValueError(f"Incorrect upstream archive: {name}")
    return zipfile.ZipFile(path)

def write_entry(archive, entry, destination):
    destination.parent.mkdir(parents=True, exist_ok=True)
    with archive.open(entry) as source, destination.open("wb") as target:
        shutil.copyfileobj(source, target)

def patch_files():
    files = ["install.py", "patchlib.py", "resources.py", "tutorials.py", "movies.py",
             "Setup.cmd", "README.md", "README.fr.md", "third_party/gust_xml.py",
             "third_party/LICENSE-gust-xml.txt", "third_party/PORTABLE.md",
             "tools/Launcher.cs", "tools/Setup.cs", "tools/write_movie.cpp", "tools/write_movie.exe",
             "patch/files.json", "patch/ui.json", "patch/graphics.json", "patch/lines.json.xz", "patch/program.adp",
             "subtitles/timings.json"]
    files += ["patch/" + row[3] for row in json.loads((ROOT / "patch/ui.json").read_text())]
    files += [f"patch/{name}.blocks.xz" for name in ("mainmenu", "common", "system", "window")]
    files += [f"subtitles/{name}.ass" for name in ("opening","prologue","seq02","seq03","seq04","seq05","tm_felion_D")]
    times = json.loads((ROOT / "subtitles/timings.json").read_text())
    files += [f"subtitles/mask-{name}-{i}.png" for name, spans in times.items() for i in range(len(spans))]
    return files

def build(inputs, output):
    with tempfile.TemporaryDirectory(dir=output.parent) as temp:
        stage = Path(temp) / output.stem
        for relative in patch_files():
            target = stage / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT / relative, target)
        runtime = stage / "runtime"
        runtime.mkdir()
        with pinned(inputs, "python.zip") as archive:
            for entry in archive.namelist():
                if entry == Path(entry).name:
                    write_entry(archive, entry, runtime / entry)
        # Isolate the interpreter from PYTHONPATH, site packages and the registry.
        (runtime / "python313._pth").write_text("python313.zip\n.\n..\n", encoding="ascii")
        with pinned(inputs, "pillow.whl") as archive:
            for entry in archive.namelist():
                if not entry.endswith("/") and entry.startswith(("PIL/", "pillow-13.0.0.dist-info/")):
                    write_entry(archive, entry, runtime / entry)
        with pinned(inputs, "gust_tools.zip") as archive:
            for entry in ("gust_pak.exe", "LICENSE.txt"):
                write_entry(archive, entry, stage / "tools/gust" / entry)
        with pinned(inputs, "ffmpeg.zip") as archive:
            for entry in archive.namelist():
                path = Path(entry)
                if path.name == "LICENSE.txt" or (path.parent.name == "bin" and
                        (path.name in ("ffmpeg.exe", "ffprobe.exe") or path.suffix == ".dll")):
                    write_entry(archive, entry, stage / "tools/ffmpeg" / path.name)
        compiler = Path(os.environ["WINDIR"]) / "Microsoft.NET/Framework64/v4.0.30319/csc.exe"
        for source, target in [("Setup.cs", stage / "Setup.exe"),
                               ("Launcher.cs", stage / "tools/EnglishLauncher.exe")]:
            subprocess.run([str(compiler), "/nologo", "/target:winexe", "/platform:x64", "/optimize+",
                            "/codepage:65001", "/r:System.Windows.Forms.dll", "/r:System.Drawing.dll",
                            "/out:" + str(target), str(ROOT / "tools" / source)], check=True)
        # A sibling temporary file keeps an existing verified release usable on failure.
        pending = Path(temp) / "release.zip"
        with zipfile.ZipFile(pending, "w", zipfile.ZIP_DEFLATED, compresslevel=6) as z:
            for path in sorted(stage.rglob("*")):
                if path.is_file():
                    z.write(path, path.relative_to(stage.parent))
        pending.replace(output)

if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("inputs", type=Path, help="Directory containing the four pinned upstream archives")
    p.add_argument("output", type=Path, help="Output ZIP filename")
    args = p.parse_args()
    build(args.inputs.resolve(), args.output.resolve())
