"""Install, check or restore the Ar nosurge DX localization on Windows."""
import argparse
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
from contextlib import contextmanager, ExitStack
from patchlib import ROOT, apply_delta, digest
from resources import PATCH, archive, graphics, launcher, manifest, require_hash

FILES = manifest("files.json")
BACKUP = "ArnosurgeDX-patch-backup"
GRAPHICS = "Data/PACK00_01.PAK"
GRAPHICS_RECEIPT = "vita-graphics-v140.json"

def needs_update(folder, rel, installed_hash):
    if rel == GRAPHICS:
        marker = folder / GRAPHICS_RECEIPT
        return not marker.exists() or json.loads(marker.read_text("utf8")) != installed_hash
    return installed_hash in FILES[rel].get("previous", [])

def write_json(path, value):
    temp=path.with_suffix(".new")
    temp.write_text(json.dumps(value,indent=2)+"\n","utf8")
    os.replace(temp,path)

def read_state(path):
    if not path.exists():return {}
    value=json.loads(path.read_text("utf8"))
    if not isinstance(value,dict) or not value.keys()<=FILES.keys():
        raise ValueError(f"Unexpected patch state: {path}")
    return value

@contextmanager
def lock(folder):
    import msvcrt
    folder.mkdir(exist_ok=True)
    with (folder/"lock").open("a+b") as f:
        if not f.tell():f.write(b"0");f.flush()
        f.seek(0)
        msvcrt.locking(f.fileno(),msvcrt.LK_NBLCK,1)
        try:yield
        finally:
            f.seek(0);msvcrt.locking(f.fileno(),msvcrt.LK_UNLCK,1)

def safepath(base,rel):
    p=base/rel
    if p.resolve()!=p or not p.is_relative_to(base):
        raise ValueError(f"Unexpected redirected path: {p}")
    return p

def require_closed():
    powershell=Path(os.environ["SystemRoot"])/"System32/WindowsPowerShell/v1.0/powershell.exe"
    query="@(Get-Process -Name ArnosurgeDX,ArnosurgeDX_Launcher,ArnosurgeDX_Env -ErrorAction SilentlyContinue).Count"
    count=subprocess.check_output([str(powershell),"-NoProfile","-NonInteractive","-Command",query])
    if int(count.strip()):
        raise ValueError("Close the game and its launcher first.")

def copy_checked(src,dst,expected):
    dst.parent.mkdir(parents=True,exist_ok=True)
    with tempfile.NamedTemporaryFile(dir=dst.parent,delete=False) as f:tmp=Path(f.name)
    try:
        shutil.copyfile(src,tmp);require_hash(tmp,expected);os.replace(tmp,dst)
    finally:tmp.unlink(missing_ok=True)

def restore(game,folder,active,items):
    # Validate the whole set before changing any file. A pending restore
    # can be resumed if Windows or the installer stops between replacements.
    for rel,new in items.items():
        original=FILES[rel]["original"]
        require_hash(safepath(folder,rel),original)
        # During an interrupted upgrade, an entry not yet replaced can
        # still contain the prior release recorded in installed.json.
        if digest(safepath(game,rel)) not in (new,original,active.get(rel)):
            raise ValueError(f"File changed outside this installer: {rel}")
    write_json(folder/"pending.json",items)
    for rel in items:
        expected=FILES[rel]["original"];target=safepath(game,rel)
        if digest(target)!=expected:copy_checked(safepath(folder,rel),target,expected)
        active.pop(rel,None)
    write_json(folder/"installed.json",active)
    (folder/"pending.json").unlink()

def program(arg,name):
    resolved=Path(arg).expanduser().resolve() if arg else None
    if not resolved:
        bundled = ROOT / "tools" / ("ffmpeg" if name == "ffmpeg.exe" else "gust") / name
        found = bundled if bundled.is_file() else shutil.which(name)
        if found:resolved=Path(found).resolve()
    if not resolved or not resolved.is_file():raise ValueError(f"Required tool: {name}. See README.")
    return resolved

def prepare(a,rel,original,target,root,stage):
    if rel=="ArnosurgeDX.exe":
        from field_text import program_source
        program = apply_delta(original.read_bytes(), (PATCH/"program.adp").read_bytes())
        target.write_bytes(apply_delta(program_source(program, root), (PATCH/"field-program.adp").read_bytes()))
    elif rel.endswith("_Launcher.exe"):
        launcher(target)
    elif rel.endswith("_Env.exe"):
        launch=stage/"ArnosurgeDX_Launcher.exe"
        if launch.exists():shutil.copyfile(launch,target)
        else:launcher(target)
    elif rel==GRAPHICS:
        from field_art import field_graphics
        graphics(original,target,root,a.texture_tool)
        field_graphics(original,target,root,a.texture_tool)
    elif rel.endswith(".PAK"):archive(original,target,root,a.gust)
    else:
        from movies import render
        render(original,target,a.ffmpeg)
    # Windows fonts, the local compiler and WMV encoder can change output
    # bytes across machines. The two data PAKs and the game EXE are exact.
    if rel in ("ArnosurgeDX.exe","Data/PACK01.PAK","Data/PACK02.PAK"):
        require_hash(target,FILES[rel]["reference"])
    return digest(target)

def main(a):
    if os.name!="nt":raise ValueError("Windows is required.")
    a.game=a.game.expanduser().resolve(strict=True)
    if not (a.game/"ArnosurgeDX.exe").is_file():raise ValueError("Select the DX installation folder.")
    folder=safepath(a.game,BACKUP)
    core=[r for r in FILES if not r.endswith(".wmv")]
    relevant=[r for r in FILES if r.endswith(".wmv")] if a.action=="movies" else core
    if a.action=="check":
        active=read_state(folder/"installed.json")
        if (folder/"pending.json").exists():raise ValueError("Incomplete installation. Run restore.")
        ok=True
        for rel,meta in FILES.items():
            p=safepath(a.game,rel);h=digest(p) if p.is_file() else ""
            if rel in active:
                if h!=active[rel]:state="modified after installation"
                elif needs_update(folder,rel,h):state="update available"
                else:state="installed"
            elif h==meta["original"]:state="original"
            elif h==meta.get("reference"):state="previously patched"
            else:state="missing or unsupported version"
            print(f"{state:32} {rel}");ok &= state in ("installed","original","previously patched","update available")
        return 0 if ok else 1
    require_closed()
    with lock(folder), ExitStack() as opened:
        active=read_state(folder/"installed.json")
        pending=read_state(folder/"pending.json")
        if pending:restore(a.game,folder,active,pending)
        if a.action=="restore":
            if active:restore(a.game,folder,active,active.copy())
            (folder/"vita-graphics.json").unlink(missing_ok=True)
            (folder/GRAPHICS_RECEIPT).unlink(missing_ok=True)
            print("Original files restored.");return 0
        needed=[]
        for rel in relevant:
            target=safepath(a.game,rel)
            if rel in active:
                require_hash(target,active[rel]);require_hash(safepath(folder,rel),FILES[rel]["original"])
                if needs_update(folder,rel,active[rel]):needed.append(rel)
            else:
                require_hash(target,FILES[rel]["original"]);needed.append(rel)
        if not needed:
            print("Already installed.");return 0
        donor=None
        if a.action=="install":
            from vita import VitaArchive
            if not a.vita:raise ValueError("Supply --vita with the US Vita Plus folder (PCSE00707).")
            print("Checking US Vita Plus archive...",flush=True)
            donor=VitaArchive(a.vita)
            opened.callback(donor.close)
            a.gust=program(a.gust,"gust_pak.exe")
            if GRAPHICS in needed:a.texture_tool=program(a.gust.with_name("gust_g1t.exe"),"gust_g1t.exe")
            from PIL import Image
        else:
            a.ffmpeg=program(a.ffmpeg,"ffmpeg.exe")
            program(a.ffmpeg.with_name("ffprobe.exe"),"ffprobe.exe")
        with tempfile.TemporaryDirectory(dir=folder) as directory:
            stage=Path(directory);changed={}
            for rel in needed:
                print(f"Building {rel}",flush=True)
                target=stage/rel;target.parent.mkdir(parents=True,exist_ok=True)
                original=safepath(folder if rel in active else a.game,rel)
                changed[rel]=prepare(a,rel,original,target,donor,stage)
            for rel in needed:
                backup=safepath(folder,rel);expected=FILES[rel]["original"]
                if backup.exists():require_hash(backup,expected)
                else:copy_checked(safepath(a.game,rel),backup,expected)
            require_closed()
            write_json(folder/"pending.json",changed)
            try:
                for rel,new in changed.items():
                    target=safepath(a.game,rel)
                    require_hash(target,active.get(rel,FILES[rel]["original"]))
                    os.replace(stage/rel,target);require_hash(target,new)
                write_json(folder/"installed.json",dict(active,**changed))
                if GRAPHICS in changed:write_json(folder/GRAPHICS_RECEIPT,changed[GRAPHICS])
                (folder/"pending.json").unlink()
            except BaseException:
                restore(a.game,folder,active,changed);raise
    print("Installation verified.");return 0

if __name__=="__main__":
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action",choices=["check","install","movies","restore"])
    parser.add_argument("--game",type=Path,required=True)
    parser.add_argument("--vita",type=Path)
    parser.add_argument("--gust",help="Path to gust_pak.exe")
    parser.add_argument("--ffmpeg",help="Path to ffmpeg.exe")
    try:sys.exit(main(parser.parse_args()))
    except (OSError,ValueError,RuntimeError,ImportError,subprocess.SubprocessError) as exc:
        print(f"Error: {exc}",file=sys.stderr);sys.exit(1)
