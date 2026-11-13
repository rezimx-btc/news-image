#!/usr/bin/env python3
"""news-image-01 entry: copy the front-page image to /output/entry.png.

The image (news.png) is a one-page newspaper front page summing up
Friday 13 November 2026, rendered by render.py (PIL, deterministic).
This program only copies the file the repository holds.
"""
import hashlib
import os
import shutil

SRC = os.path.join(os.path.dirname(os.path.abspath(__file__)), "news.png")
DST = "/output/entry.png"


def main():
    if not os.path.exists(SRC):
        raise SystemExit("news.png not found next to main.py")
    os.makedirs("/output", exist_ok=True)
    shutil.copyfile(SRC, DST)
    with open(SRC, "rb") as f:
        src_data = f.read()
    with open(DST, "rb") as f:
        data = f.read()
    if hashlib.sha256(data).hexdigest() != hashlib.sha256(src_data).hexdigest():
        raise SystemExit("entry.png does not match news.png (copy failed)")
    if len(data) > 1024 * 1024:
        raise SystemExit("entry.png over the 1 MiB limit: %d bytes" % len(data))
    from PIL import Image
    im = Image.open(DST)
    if im.width > 1024 or im.height > 1024:
        raise SystemExit("entry.png over the 1024x1024 limit: %s" % (im.size,))
    print("wrote", DST, len(data), "bytes,", im.size, "sha256",
          hashlib.sha256(data).hexdigest())


if __name__ == "__main__":
    main()
