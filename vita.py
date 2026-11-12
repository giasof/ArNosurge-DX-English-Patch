"""Read the English resources of the US Vita Plus release from a local copy."""
import hashlib
import struct
import zlib
from pathlib import Path

ARCHIVE_HASH = "40c0080bd8dfe6f22f097021367a5d822c3bc823e70b4ba6196e565db33251f8"


class VitaArchive:
    def __init__(self, source):
        source = Path(source).expanduser().resolve()
        locations = (source, source / "resources1.psarc", source / "PSVita/resources1.psarc",
                     source / "Data/PSVita/resources1.psarc")
        path = next((candidate for candidate in locations if candidate.is_file()), None)
        if path is None:
            raise ValueError("Select the extracted US Vita Plus folder containing Data/PSVita/resources1.psarc (PCSE00707).")
        self.stream = path.open("rb")
        try:
            if self.stream.read(4) != b"PSAR":
                raise ValueError("The Vita archive is encrypted or invalid. Select a readable copy of PCSE00707, such as the installed app folder in Vita3K.")
            self.stream.seek(0)
            if hashlib.file_digest(self.stream, "sha256").hexdigest() != ARCHIVE_HASH:
                raise ValueError("Unsupported Vita archive. This release supports US Plus PCSE00707.")
            self.stream.seek(0)
            header = self.stream.read(32)
            magic, version, codec, toc, stride, count, block, flags = struct.unpack(">4sI4s5I", header)
            if (magic, codec, stride, block, flags) != (b"PSAR", b"zlib", 30, 65536, 0):
                raise ValueError("Unsupported PSARC format.")
            self.entries = []
            for _ in range(count):
                row = self.stream.read(stride)
                self.entries.append(tuple(int.from_bytes(row[a:b], "big") for a, b in ((16,20),(20,25),(25,30))))
            self.sizes = [size for size, in struct.iter_unpack(">H", self.stream.read(toc - self.stream.tell()))]
            names = self._read(0).decode("utf8").splitlines()
            self.index = {name.lstrip("/").lower(): i for i, name in enumerate(names, 1)}
            if len(self.index) != count - 1:
                raise ValueError("Invalid Vita resource index.")
        except BaseException:
            self.stream.close()
            raise

    def _read(self, index):
        block, remaining, offset = self.entries[index]
        self.stream.seek(offset)
        output = bytearray()
        while remaining:
            size = self.sizes[block] or 65536
            chunk = self.stream.read(size)
            expected = min(65536, remaining)
            if len(chunk) != size:
                raise ValueError("Truncated Vita resource.")
            if size != expected:
                chunk = zlib.decompress(chunk)
            if len(chunk) != expected:
                raise ValueError("Incorrect Vita resource size.")
            output.extend(chunk)
            remaining -= expected
            block += 1
        return bytes(output)

    def read(self, name):
        return self._read(self.index[name.lower()])

    def close(self):
        self.stream.close()


def dx_line(scene, index, donor, original):
    """Adapt hardware-specific instructions to the actual DX prompt tokens."""
    text = donor.decode("utf8")
    scene = Path(scene).stem.removeprefix("event_message_")
    if scene == "c11_1_120" and index == 7:
        text = "Delta and Cass both have something to say. Use <IM11> and <IM15> to move the ring and listen."
    elif scene == "c11_1_120" and index == 8:
        text = "As more companions join you, you can hear different conversations between them."
    elif scene == "c32_1_270" and index == 66:
        text = "Press <IM24> and <IM06> at the same time. Does that make sense?"
    elif scene == "ms31_080" and index == 22:
        text = text.replace("the START Button", "<IM19>")
    elif scene in ("swc08_120", "swi08_080") and "○ button" in text:
        text = text.replace("the ○ button skill", "the <IM21> skill").replace("the ○ button", "<IM21>")
    elif scene == "xx01_160" and index == 0:
        text = "Delta learned Zero Divide! Hold <IM11> or <IM15> and press <IM04> to use it."
    return text.encode("utf8")
