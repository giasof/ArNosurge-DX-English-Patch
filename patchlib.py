"""Read patch instructions. COPY addresses refer to local game data."""
from pathlib import Path
import hashlib
import re
import struct
import lzma

ROOT = Path(__file__).resolve().parent

def digest(path):
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()

def apply_delta(base, patch):
    source = memoryview(lzma.decompress(patch))
    magic, size = struct.unpack_from("<4sI", source)
    if magic != b"ADP1":
        raise ValueError("Invalid patch header")
    answer = bytearray()
    pos = 8
    while pos < len(source):
        length, = struct.unpack_from("<i", source, pos)
        pos += 4
        if length < 0:
            end = pos - length
            if end > len(source):
                raise ValueError("Truncated patch data")
            answer.extend(source[pos:end])
            pos = end
        elif length:
            offset, = struct.unpack_from("<I", source, pos)
            pos += 4
            if offset + length > len(base):
                raise ValueError("Patch source does not match")
            answer.extend(base[offset:offset+length])
        else:
            raise ValueError("Empty patch instruction")
    if len(answer) != size:
        raise ValueError("Patch length mismatch")
    return bytes(answer)

def ebm_rows(data):
    count, = struct.unpack_from("<I", data)
    pos = 4
    rows = []
    for _ in range(count):
        length, = struct.unpack_from("<I", data, pos+32)
        end = pos+36+length
        if not length or end > len(data) or data[end-1] != 0:
            raise ValueError("Invalid EBM record")
        rows.append((data[pos:pos+32], data[pos+36:end-1]))
        pos = end
    if pos != len(data):
        raise ValueError("Unrecognized EBM trailer")
    return rows

def gaps(text):
    pieces = re.split(rb"((?:<CR>|[ \t\r\n])+)", text)
    clean = bytearray()
    breaks = {}
    for i, piece in enumerate(pieces):
        if i % 2:
            breaks[len(clean)] = piece
        else:
            clean.extend(piece)
    return bytes(clean), breaks

def dialogue(dx, us, edits):
    original = ebm_rows(dx)
    donor = ebm_rows(us) if us is not None else []
    result = bytearray(struct.pack("<I", len(original)))
    for i, (header, text) in enumerate(original):
        if str(i) in edits:
            use_donor, changes = edits[str(i)]
            base = donor[i][1] if use_donor else text
            if changes:
                chars, marks = gaps(base)
                marks.update((p, v.encode("ascii")) for p,v in changes)
                last = 0
                pieces = []
                for p, v in sorted(marks.items()):
                    pieces.extend((chars[last:p], v))
                    last = p
                text = b"".join(pieces) + chars[last:]
            else:
                text = base
        result.extend(header + struct.pack("<I", len(text)+1) + text + b"\0")
    return bytes(result)
