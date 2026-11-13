#!/usr/bin/env python3
"""news-image-01 v3 entry: copy the red tabloid front-page image to /output/entry.png.

The image (news.png) is a bold tabloid front page for 13 November 2026:
a red masthead reading THE WORLD, the giant headline HORMUZ ON FIRE, a
drawn lead scene of four tankers in the Strait of Hormuz with two burning,
and six more stories plus an ALSO strip below. This program only copies the
file the repository holds.

Standard library only: no third-party imports, so it runs in a bare
python:3.13 image. Dimensions are read from the PNG IHDR header.
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


def fail(message):
    """Abort with a clear one-line reason."""
    raise SystemExit(message)


ALLOWED_DEPTHS = {0: (1, 2, 4, 8, 16), 2: (8, 16), 3: (1, 2, 4, 8),
                  4: (8, 16), 6: (8, 16)}


def check_colour(data):
    """Reject PNGs whose IHDR colour type or bit depth we do not expect:
    the renderer writes 8-bit truecolour (type 2), so anything else means
    the image was swapped or corrupted."""
    if len(data) < 29:
        fail("entry.png too short for an IHDR chunk")
    depth = data[24]
    colour = data[25]
    if colour not in ALLOWED_DEPTHS or depth not in ALLOWED_DEPTHS[colour]:
        fail("entry.png has an unexpected colour type %d / bit depth %d"
             % (colour, depth))
    if colour != 2 or depth != 8:
        fail("entry.png is not 8-bit truecolour: type %d, depth %d"
             % (colour, depth))


def read_header(data):
    """Return (width, height) from a PNG's IHDR chunk, or fail."""
    if len(data) < 24 or data[:8] != MAGIC or data[12:16] != b"IHDR":
        fail("entry.png is not a valid PNG file")
    width, height = struct.unpack(">II", data[16:24])
    return width, height


def check_size(size):
    if size > LIMIT_BYTES:
        fail("entry.png over the 1 MiB limit: %d bytes" % size)


def check_sides(width, height):
    if width > LIMIT_SIDE or height > LIMIT_SIDE:
        fail("entry.png over the 1024x1024 limit: %dx%d" % (width, height))


def check_match(first, second):
    if first != second:
        fail("copy mismatch: entry.png differs from news.png")


def publish():
    if not os.path.exists(CARD):
        fail("news.png not found next to main.py")
    os.makedirs("/output", exist_ok=True)
    shutil.copyfile(CARD, OUT)
    if not os.path.isfile(OUT):
        fail("copy failed: %s was not created" % OUT)
    with open(OUT, "rb") as f:
        data = f.read()
    check_size(len(data))
    width, height = read_header(data)
    check_colour(data)
    check_sides(width, height)
    src_digest = hashlib.sha256(open(CARD, "rb").read()).hexdigest()
    dst_digest = hashlib.sha256(data).hexdigest()
    check_match(src_digest, dst_digest)
    print("wrote", OUT, len(data), "bytes,", (width, height),
          "sha256", dst_digest)


if __name__ == "__main__":
    publish()
