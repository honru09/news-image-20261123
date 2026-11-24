#!/usr/bin/env python3
"""Copy the bundled news image to the output directory.

Reads entry.png from this repository, checks it is a complete
1024x1024 PNG, then copies it to $MAKEFUN_OUTPUT_DIR (or /output).
Standard library only; no network, no other files.
"""

import os
import shutil
import struct
import sys
import zlib

PNG_MAGIC = b"\x89PNG\r\n\x1a\n"
EXPECTED_WIDTH = 1024
EXPECTED_HEIGHT = 1024
SOURCE_NAME = "entry.png"


def fail(message):
    """Print a named error and exit non-zero."""
    print(f"error: {message}", file=sys.stderr)
    raise SystemExit(1)


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    source = os.path.join(here, SOURCE_NAME)
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR") or "/output"
    target = os.path.join(out_dir, SOURCE_NAME)

    with open(source, "rb") as handle:
        data = handle.read()

    if data[:8] != PNG_MAGIC:
        fail("bad magic: file does not start with the PNG signature")
    if len(data) < 33:
        fail("truncated file: too short to hold a PNG header")
    if data[12:16] != b"IHDR":
        fail("bad PNG: first chunk is not IHDR")
    width, height = struct.unpack(">II", data[16:24])
    if (width, height) != (EXPECTED_WIDTH, EXPECTED_HEIGHT):
        fail(f"wrong size: image is {width}x{height}, expected 1024x1024")
    # Walk every chunk: each length must stay inside the file, and the
    # last chunk must be a well-formed IEND (zero length, correct CRC).
    offset = 8
    last_type = None
    while offset + 8 <= len(data):
        length, chunk_type = struct.unpack(">I4s", data[offset:offset + 8])
        if offset + 12 + length > len(data):
            fail("truncated file: a chunk runs past the end of the file")
        last_type = chunk_type
        offset += 12 + length
    if offset != len(data):
        fail("truncated file: trailing bytes after the last chunk")
    if last_type != b"IEND":
        fail("missing or truncated IEND: last chunk is not IEND")
    iend_crc = struct.unpack(">I", data[offset - 4:offset])[0]
    if iend_crc != (zlib.crc32(b"IEND") & 0xFFFFFFFF):
        fail("missing or truncated IEND: IEND checksum is wrong")

    os.makedirs(out_dir, exist_ok=True)
    shutil.copyfile(source, target)
    os.chmod(target, 0o644)
    print(f"wrote {target}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
