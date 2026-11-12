"""Source data for the field dialogue and conversation choice differences."""
from patchlib import ebm_rows

CHOICES = "event/balloonsel/balloonseldata.bsb"


def program_source(program, donor):
    """Use local DX bytes, choice strings and English wording from the Vita edition."""
    source = bytearray(program)
    source.extend(donor.read(CHOICES))
    for name in sorted(donor.index):
        if name.startswith("event/event/") and name.endswith(".ebm"):
            for _, text in ebm_rows(donor.read(name)):
                source.extend(text.replace(b"<CR>", b" ") + b"\0")
    return bytes(source)
