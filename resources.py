from pathlib import Path
import hashlib, io, json, lzma, os, shutil, struct, subprocess, tempfile
from patchlib import ROOT, apply_delta, digest, dialogue

PATCH=ROOT/"patch"
def manifest(name):
    return json.loads((PATCH/name).read_text("utf8"))

def require_hash(path, expected):
    if not path.is_file() or digest(path)!=expected:
        raise ValueError(f"Missing or unsupported file: {path}")

def unpack(tool, package, directory):
    local=directory/package.name.upper()
    shutil.copyfile(package,local)
    with (directory/"unpack.log").open("wb") as log:
        subprocess.run([str(tool),local.name],cwd=directory,stdout=log,stderr=subprocess.STDOUT,check=True)
    return local

def archive(package, target, donor, tool):
    with tempfile.TemporaryDirectory(dir=target.parent) as folder:
        d=Path(folder)
        local=unpack(tool,package,d)
        if package.stem.upper()=="PACK01":
            from field_text import CHOICES
            (d/CHOICES).write_bytes(apply_delta(donor.read(CHOICES),(PATCH/"choices.adp").read_bytes()))
            edits=json.loads(lzma.decompress((PATCH/"lines.json.xz").read_bytes()))
            for rel,(original,rules) in edits.items():
                src=donor.read("event/event/"+rel) if original else None
                if original and hashlib.sha256(src).hexdigest()!=original:
                    raise ValueError(f"Incorrect Vita dialogue: {rel}")
                f=d/"event/event"/rel
                f.write_bytes(dialogue(f.read_bytes(),src,rules,rel))
        else:
            from third_party.gust_xml import descramble,unglaze,encode_file,detect_text_encoding
            def xml(data,rel):
                if rel.endswith(".e"):data=unglaze(descramble(data))
                return data.decode(detect_text_encoding(data)).encode("utf8")
            for rel,encoding,original,patch in manifest("ui.json"):
                f=d/"saves"/rel
                base=xml(f.read_bytes(),rel)
                if original:
                    src=donor.read("saves/"+rel)
                    if hashlib.sha256(src).hexdigest()!=original:
                        raise ValueError(f"Incorrect Vita menu: {rel}")
                    base+=xml(src,rel)
                result=apply_delta(base,(PATCH/patch).read_bytes()).decode("utf8").encode(encoding)
                f.write_bytes(encode_file(result) if f.suffix==".e" else result)
        index=local.with_suffix(".json")
        # Gust Tools chooses the output name from the archive manifest.
        local.unlink()
        with (d/"pack.log").open("wb") as log:
            subprocess.run([str(tool),index.name],cwd=d,stdout=log,stderr=subprocess.STDOUT,check=True)
        shutil.move(local,target)

def picture(asset,height):
    from PIL import Image
    header=bytearray(128)
    header[:4]=b"DDS "
    struct.pack_into("<7I",header,4,124,0xa1007,height,2048,height*1024,0,1)
    struct.pack_into("<II4s",header,76,32,4,b"DXT1")
    struct.pack_into("<I",header,108,0x401008)
    if len(asset)!=56+height*1024:
        raise ValueError("Unexpected tutorial size")
    im=Image.open(io.BytesIO(header+asset[56:])).convert("RGBA")
    return im.crop(im.getchannel("A").getbbox())

def graphics(original,target,donor,texture_tool):
    from tutorials import exclusive,shared
    shutil.copyfile(original,target)
    with tempfile.TemporaryDirectory(dir=target.parent) as temp, target.open("r+b") as output:
        for name,offset,size,mode,donor_hash in manifest("graphics.json"):
            output.seek(offset)
            if mode=="atlas":
                data=bytearray(output.read(size))
                changes=lzma.decompress((PATCH/(name+".blocks.xz")).read_bytes())
                for pos,mask in struct.iter_unpack("<I16s",changes):
                    for i,b in enumerate(mask[:len(data)-pos]):
                        data[pos+i]^=b
                output.seek(offset);output.write(data)
                continue
            asset=output.read(size)
            image=picture(asset,2048).convert("RGB")
            if mode=="shared":
                from PIL import Image
                source=Path(temp)/(name+".g1t")
                source.write_bytes(donor.read("data/psvita/ipu/"+source.name))
                require_hash(source,donor_hash)
                subprocess.run([str(texture_tool),str(source)],cwd=temp,stdout=subprocess.DEVNULL,check=True)
                with Image.open(source.with_suffix("")/"000.dds") as decoded:
                    native=decoded.convert("RGBA")
                native=native.crop(native.getchannel("A").getbbox())
                if native.size!=(960,544):raise ValueError(f"Unexpected Vita tutorial dimensions: {name}")
                shared(name,image,native)
            else:exclusive(name,image)
            if image.size!=(1920,1080):raise ValueError("Unexpected DX image size")
            packed=io.BytesIO()
            image.save(packed,format="DDS",pixel_format="DXT1")
            blocks=packed.getvalue()[128:]
            if len(blocks)!=1920*1080//2:raise ValueError("Unexpected DXT encoding")
            for row in range(270):
                output.seek(offset+56+row*4096)
                output.write(blocks[row*3840:(row+1)*3840])

def launcher(target):
    bundled = ROOT / "tools" / "EnglishLauncher.exe"
    if bundled.is_file():
        shutil.copyfile(bundled, target)
        return
    csc=Path(os.environ["WINDIR"])/"Microsoft.NET/Framework64/v4.0.30319/csc.exe"
    subprocess.run([str(csc),"/nologo","/target:winexe","/optimize+","/utf8output",
                    "/r:System.Windows.Forms.dll","/r:System.Drawing.dll","/r:System.Core.dll",
                    "/out:"+str(target),str(ROOT/"tools/Launcher.cs")],check=True)
