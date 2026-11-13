#!/usr/bin/env python3
"""news-image-01 entry: publish the newspaper image as the entry.

Copies news.png (rendered by render.py in this same repository) to
/output/entry.png and proves the copy is exact: same bytes, same sha256,
within the 1 MiB size cap and the 1024x1024 dimension cap. The PNG
dimensions are read straight from the IHDR header with struct, so this
runs in a bare python:3.13 image with no third-party packages at all.
"""
import hashlib
import os
import shutil
import struct

HERE = os.path.dirname(os.path.abspath(__file__))
CARD = os.path.join(HERE, "news.png")
OUT = "/output/entry.png"
MAGIC = b"\x89PNG\r\n\x1a\n"
LIMIT_BYTES = 1024 * 1024
LIMIT_SIDE = 1024


def fail(msg):
    raise SystemExit(msg)


def read_header(data):
    """Return (width, height) from a PNG's IHDR chunk, or fail."""
    if len(data) < 24 or data[:8] != MAGIC or data[12:16] != b"IHDR":
        fail("news.png is not a valid PNG file")
    width, height = struct.unpack(">II", data[16:24])
    return width, height


def check_size(data):
    if len(data) > LIMIT_BYTES:
        fail("entry.png over the 1 MiB limit: %d bytes" % len(data))


def check_sides(width, height):
    if width > LIMIT_SIDE or height > LIMIT_SIDE:
        fail("entry.png over the 1024x1024 limit: %dx%d"
             % (width, height))
    if width == 0 or height == 0:
        fail("entry.png has a zero side: %dx%d" % (width, height))


def check_match(src, dst):
    if src != dst:
        fail("copy mismatch: entry.png differs from news.png")


def publish():
    if not os.path.exists(CARD):
        fail("news.png not found next to main.py")
    with open(CARD, "rb") as f:
        src_data = f.read()
    src_width, src_height = read_header(src_data)
    check_size(src_data)
    check_sides(src_width, src_height)
    os.makedirs("/output", exist_ok=True)
    shutil.copyfile(CARD, OUT)
    if not os.path.isfile(OUT):
        fail("copy failed: %s was not created" % OUT)
    with open(OUT, "rb") as f:
        data = f.read()
    src_digest = hashlib.sha256(open(CARD, "rb").read()).hexdigest()
    dst_digest = hashlib.sha256(data).hexdigest()
    check_match(src_digest, dst_digest)
    print("wrote %s %d bytes, (%d, %d) sha256 %s"
          % (OUT, len(data), src_width, src_height, dst_digest))


if __name__ == "__main__":
    publish()
