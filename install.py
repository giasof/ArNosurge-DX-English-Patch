"""Install, check or restore the Ar nosurge DX localization on Windows."""
import argparse
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
from contextlib import contextmanager
from patchlib import ROOT, apply_delta, digest
from resources import PATCH, archive, graphics, launcher, manifest, require_hash

FILES = manifest("files.json")
BACKUP = "ArnosurgeDX-patch-backup"

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
        if digest(safepath(game,rel)) not in (new,original):
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

def prepare(a,rel,target,root,stage):
    original=a.game/rel
    if rel=="ArnosurgeDX.exe":
        target.write_bytes(apply_delta(original.read_bytes(),(PATCH/"program.adp").read_bytes()))
    elif rel.endswith("_Launcher.exe"):
        launcher(target)
    elif rel.endswith("_Env.exe"):
        launch=stage/"ArnosurgeDX_Launcher.exe"
        if launch.exists():shutil.copyfile(launch,target)
        else:launcher(target)
    elif rel.endswith("PACK00_01.PAK"):graphics(original,target,root)
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
                state="installed" if h==active[rel] else "modified after installation"
            elif h==meta["original"]:state="original"
            elif h==meta.get("reference"):state="previously patched"
            else:state="missing or unsupported version"
            print(f"{state:32} {rel}");ok &= state in ("installed","original","previously patched")
        return 0 if ok else 1
    require_closed()
    with lock(folder):
        active=read_state(folder/"installed.json")
        pending=read_state(folder/"pending.json")
        if pending:restore(a.game,folder,active,pending)
        if a.action=="restore":
            if active:restore(a.game,folder,active,active.copy())
            print("Original files restored.");return 0
        needed=[]
        for rel in relevant:
            target=safepath(a.game,rel)
            if rel in active:
                require_hash(target,active[rel]);require_hash(safepath(folder,rel),FILES[rel]["original"])
            else:
                require_hash(target,FILES[rel]["original"]);needed.append(rel)
        if not needed:
            print("Already installed.");return 0
        donor=None
        if a.action=="install":
            if not a.ps3:raise ValueError("Supply --ps3 with the US PS3 game folder.")
            base=a.ps3.expanduser().resolve()
            donor=next((p for p in (base,base/"USRDIR",base/"PS3_GAME/USRDIR")
                        if (p/"Event/event").is_dir()),None)
            if donor is None:raise ValueError("PS3_GAME/USRDIR/Event/event was not found.")
            a.gust=program(a.gust,"gust_pak.exe")
            from PIL import Image
        else:
            a.ffmpeg=program(a.ffmpeg,"ffmpeg.exe")
            program(a.ffmpeg.with_name("ffprobe.exe"),"ffprobe.exe")
        with tempfile.TemporaryDirectory(dir=folder) as directory:
            stage=Path(directory);changed={}
            for rel in needed:
                print(f"Building {rel}",flush=True)
                target=stage/rel;target.parent.mkdir(parents=True,exist_ok=True)
                changed[rel]=prepare(a,rel,target,donor,stage)
            for rel in needed:
                backup=safepath(folder,rel);expected=FILES[rel]["original"]
                if backup.exists():require_hash(backup,expected)
                else:copy_checked(safepath(a.game,rel),backup,expected)
            require_closed()
            write_json(folder/"pending.json",changed)
            try:
                for rel,new in changed.items():
                    target=safepath(a.game,rel)
                    require_hash(target,FILES[rel]["original"])
                    os.replace(stage/rel,target);require_hash(target,new)
                write_json(folder/"installed.json",dict(active,**changed))
                (folder/"pending.json").unlink()
            except BaseException:
                restore(a.game,folder,active,changed);raise
    print("Installation verified.");return 0

if __name__=="__main__":
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action",choices=["check","install","movies","restore"])
    parser.add_argument("--game",type=Path,required=True)
    parser.add_argument("--ps3",type=Path)
    parser.add_argument("--gust",help="Path to gust_pak.exe")
    parser.add_argument("--ffmpeg",help="Path to ffmpeg.exe")
    try:sys.exit(main(parser.parse_args()))
    except (OSError,ValueError,RuntimeError,ImportError,subprocess.SubprocessError) as exc:
        print(f"Error: {exc}",file=sys.stderr);sys.exit(1)
