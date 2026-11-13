#!/usr/bin/env python3
"""news-image-01 entry: copy the front-page image to /output/entry.png.

The image (news.png) is a one-page newspaper front page summing up
Friday 13 November 2026, rendered by render.py (PIL, deterministic).
This program only copies the file the repository holds.

Standard library only — no third-party imports — so it runs in a bare
python:3.13 container.
"""
import hashlib
import os
import shutil
import struct

SRC = os.path.join(os.path.dirname(os.path.abspath(__file__)), "news.png")
DST = "/output/entry.png"
MAX_BYTES = 1024 * 1024
MAX_DIM = 1024
PNG_MAGIC = b"\x89PNG\r\n\x1a\n"


def png_dimensions(data):
    """Read (width, height) from the PNG IHDR chunk without any image lib."""
    if len(data) < 24 or data[:8] != PNG_MAGIC:
        raise SystemExit("entry.png is not a PNG file (bad magic)")
    if data[12:16] != b"IHDR":
        raise SystemExit("entry.png is not a PNG file (no IHDR chunk)")
    width, height = struct.unpack(">II", data[16:24])
    return width, height


def main():
    if not os.path.exists(SRC):
        raise SystemExit("news.png not found next to main.py")
    os.makedirs("/output", exist_ok=True)
    shutil.copyfile(SRC, DST)
    if not os.path.exists(DST):
        raise SystemExit("copy failed: %s was not created" % DST)
    with open(SRC, "rb") as f:
        src_data = f.read()
    with open(DST, "rb") as f:
        data = f.read()
    if hashlib.sha256(data).hexdigest() != hashlib.sha256(src_data).hexdigest():
        raise SystemExit("entry.png does not match news.png (copy failed)")
    if len(data) > MAX_BYTES:
        raise SystemExit("entry.png over the 1 MiB limit: %d bytes" % len(data))
    width, height = png_dimensions(data)
    if width > MAX_DIM or height > MAX_DIM:
        raise SystemExit(
            "entry.png over the 1024x1024 limit: %dx%d" % (width, height)
        )
    print("wrote", DST, len(data), "bytes,", (width, height), "sha256",
          hashlib.sha256(data).hexdigest())


if __name__ == "__main__":
    main()
