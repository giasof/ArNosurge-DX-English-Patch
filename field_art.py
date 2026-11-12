"""Rebuild the field, encyclopedia and map artwork from the local editions."""
import io
import lzma
import os
import struct
import subprocess
import tempfile
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw, ImageFont
from resources import PATCH, manifest, picture, unpack

GUIDES = {"131": "tu_battle14", "132": "tu_battle15", "141a": "tu_combination2a",
          "142a": "tu_combination3a", "143a": "tu_combination4a"}
INSTRUCTIONS = {
    "008": ("Battle commands", [("Y  /  Top", "Impulse"), ("X  /  Left", "Alpha Strike"),
            ("A  /  Bottom", "Stampede"), ("B  /  Enemy turn", "Guard")]),
    "036": ("Skill sets", [("Set", "Top / Left / Bottom"), ("Base", "Impulse / Alpha Strike / Stampede"),
            ("Enhanced", "Double Charge / Beta Strike / Grand Slam"),
            ("Expanded", "Slam Charge / Zero Divide / Impact Blow")]),
    "076": ("Genomi-Link", [("1", "World Link"), ("2", "GP Fusion"), ("3", "Rankings")]),
}


def font(size):
    return ImageFont.truetype(str(Path(os.environ["WINDIR"]) / "Fonts/segoeuib.ttf"), size)


def card(title, rows):
    canvas = Image.new("RGBA", (512,288), "#172831")
    pen = ImageDraw.Draw(canvas)
    pen.rectangle((0,0,511,54), fill="#253e49")
    pen.text((16,10), title, font=font(25), fill="white")
    for i, (label, value) in enumerate(rows):
        y = 61 + 47*i
        pen.text((17,y), label, font=font(19), fill="#83ddd8")
        size = 19
        while pen.textlength(value, font=font(size)) > 328:
            size -= 1
        pen.text((173,y), value, font=font(size), fill="white")
    return canvas


def extract_texture(tool, path):
    subprocess.run([str(tool), str(path)], cwd=path.parent, input=b"\n",
                   stdout=subprocess.DEVNULL, check=True)


def read_image(stem, index):
    with Image.open(stem / f"{index:03d}.dds") as source:
        return source.convert("RGBA")


def resize(image, size):
    return image.resize(size, Image.Resampling.LANCZOS)


def map_sheet(name, index, original, source, vita, sprites):
    canvas = resize(source, original.size)
    used = set()
    for idx, rect, source_idx, source_rect in sprites:
        if idx != index or tuple(rect) in used:
            continue
        used.add(tuple(rect))
        sheet = source if source_idx == index else read_image(vita, source_idx)
        x,y,r,b = rect
        canvas.paste(resize(sheet.crop(source_rect), (r-x,b-y)), (x,y))
    if name == "worldtown" and index == 4:
        for row, (col, src_row) in [(11,(0,11)), (13,(0,13)), (14,(0,14)), (15,(1,10))]:
            tile = canvas.crop((384*col,48*src_row,384*col+384,48*src_row+48))
            canvas.paste(tile, (384,48*row))
        ImageDraw.Draw(canvas).text((385,578), 'Curio Shop "Kururinten"', font=font(28),
                                    fill="white", stroke_width=2, stroke_fill="#524b48")
    return canvas


def localized_image(name, index, original, source, vita, sprites, guides):
    if name in ("bios","worldtown"):
        return map_sheet(name, index, original, source, vita, sprites)
    canvas = original.copy()
    if name.startswith("acps3_bios"):
        _, (x,y,r,b), _, rect = sprites[0]
        canvas.paste((0,0,0,0), (0,0,*canvas.size))
        canvas.paste(resize(source.crop(rect), (r-x,b-y)), (x,y))
        return canvas
    if name.startswith("acps3_geno"):
        canvas.paste(resize(source.crop((0,0,472,40)), (944,80)), (0,0))
        return canvas
    x,y,r,b = canvas.getchannel("A").getbbox()
    if name in ("glossary_020","glossary_050"):
        sx,sy,sr,sb = source.getchannel("A").getbbox()
        top = round((b-y)*.79)
        tile = source.crop((sx,sy+round((sb-sy)*.79),sr,sb))
        canvas.paste(resize(tile, (r-x,b-y-top)), (x,y+top))
        return canvas
    if name == "glossary_023":
        pen = ImageDraw.Draw(canvas)
        for l, end, text, color in [(54,335,"Individual consciousness",(52,151,57)),
                                     (357,524,"Shared consciousness",(188,61,25))]:
            pen.rectangle((l,202,end,225), fill=color)
            pen.text(((l+end)//2,213), text, font=font(13), anchor="mm", fill="white")
        return canvas
    suffix = name.removeprefix("acps3_help")
    if suffix in GUIDES:
        tile = guides[GUIDES[suffix]].crop((276,153,1626,913))
    elif suffix in INSTRUCTIONS:
        tile = card(*INSTRUCTIONS[suffix])
    else:
        tile = source.crop(source.getchannel("A").getbbox())
        if name == "glossary_060" or suffix in ("061","062","151"):
            tile = resize(tile, (512,288))
            pen = ImageDraw.Draw(tile)
            pen.rectangle((0,269,511,287), fill="#172831")
            text = {"061":"X  Info     B  Back     A  Confirm",
                    "062":"Choose quantity     B  Back     A  Confirm"}.get(suffix,"Select     B  Back     A  Confirm")
            pen.text((503,278), text, anchor="rm", font=font(12), fill="white")
    canvas.paste(resize(tile,(r-x,b-y)), (x,y))
    return canvas


def update_blocks(blob, dds, original, localized):
    bounds = ImageChops.difference(original, localized).getbbox(alpha_only=False)
    if not bounds:
        return
    offset = blob.find(dds[128:])
    if offset < 0:
        raise ValueError("Could not locate source texture blocks.")
    x,y,r,b = bounds
    x,y,r,b = x//4*4, y//4*4, (r+3)//4*4, (b+3)//4*4
    kind = dds[84:88].decode("ascii")
    packed = io.BytesIO()
    localized.crop((x,y,r,b)).save(packed, format="DDS", pixel_format=kind)
    data = packed.getvalue()[128:]
    block = 8 if kind=="DXT1" else 16
    width = (r-x)//4*block
    for line in range((b-y)//4):
        pos = offset+((y//4+line)*(original.width//4)+x//4)*block
        blob[pos:pos+width] = data[line*width:(line+1)*width]


def xor_bytes(left, right):
    return (int.from_bytes(left,"little") ^ int.from_bytes(right,"little")).to_bytes(len(left),"little")


def apply_overlay(stream, entry):
    data = lzma.decompress((PATCH/entry["overlay"]).read_bytes())
    pos = 0
    while pos < len(data):
        start, size = struct.unpack_from("<II",data,pos)
        pos += 8
        if start+size > entry["size"] or pos+size > len(data):
            raise ValueError("Invalid graphic overlay.")
        addr = entry["offset"]+start
        stream.seek(addr)
        result = xor_bytes(stream.read(size), data[pos:pos+size])
        stream.seek(addr)
        stream.write(result)
        pos += size


def field_graphics(original, target, donor, texture_tool):
    entries = manifest("field-images.json")
    guide_names = set(GUIDES.values())
    with tempfile.TemporaryDirectory(dir=target.parent) as tmp, target.open("r+b") as stream:
        directory = Path(tmp)
        unpack(texture_tool.with_name("gust_pak.exe"), original, directory)
        source_dir = directory/"data/x64/ui"
        vita_dir = directory/"vita"
        vita_dir.mkdir()
        guides = {}
        for name, offset, size, _, _ in manifest("graphics.json"):
            if name in guide_names:
                stream.seek(offset)
                guides[name] = picture(stream.read(size),2048)
        for name, entry in entries.items():
            if "overlay" in entry:
                apply_overlay(stream, entry)
                continue
            dx = source_dir/(name+".g1t")
            vita = vita_dir/dx.name
            vita.write_bytes(donor.read("data/psvita/ui/"+dx.name))
            extract_texture(texture_tool, dx)
            extract_texture(texture_tool, vita)
            source = dx.read_bytes()
            if len(source) != entry["size"]:
                raise ValueError(f"Unexpected DX texture length: {name}")
            blob = bytearray(source)
            for index in entry["indices"]:
                dx_stem, vita_stem = dx.with_suffix(""), vita.with_suffix("")
                before = read_image(dx_stem,index)
                translated = localized_image(name,index,before,read_image(vita_stem,index),
                                             vita_stem,entry.get("sprites",[]),guides)
                update_blocks(blob,(dx_stem/f"{index:03d}.dds").read_bytes(),before,translated)
            stream.seek(entry["offset"])
            raw = stream.read(len(blob))
            stream.seek(entry["offset"])
            stream.write(xor_bytes(raw,xor_bytes(source,blob)))
