"""Entry point for the news-image-20261119 entry.

Stdlib only. Copies entry.png byte-for-byte into MAKEFUN_OUTPUT_DIR
(or the directory given as argv[1]) and verifies the copy:
PNG magic bytes plus identical byte count.
"""
import hashlib
import os
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "entry.png")
PNG_MAGIC = b"\x89PNG\r\n\x1a\n"


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR")
    if not out_dir and len(sys.argv) > 1:
        out_dir = sys.argv[1]
    if not out_dir:
        print("error: set MAKEFUN_OUTPUT_DIR or pass an output directory",
              file=sys.stderr)
        return 1

    with open(SRC, "rb") as f:
        data = f.read()
    if data[:8] != PNG_MAGIC:
        print("error: entry.png is not a PNG (bad magic bytes)",
              file=sys.stderr)
        return 1
    if len(data) == 0:
        print("error: entry.png is empty", file=sys.stderr)
        return 1

    os.makedirs(out_dir, exist_ok=True)
    dst = os.path.join(out_dir, "entry.png")
    shutil.copyfile(SRC, dst)

    with open(dst, "rb") as f:
        copied = f.read()
    if copied != data:
        print("error: copied file differs from entry.png", file=sys.stderr)
        return 1

    print("ok: entry.png %d bytes sha256=%s -> %s"
          % (len(data), hashlib.sha256(data).hexdigest(), dst))
    return 0


if __name__ == "__main__":
    sys.exit(main())
