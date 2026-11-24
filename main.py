#!/usr/bin/env python3
"""news-image-20261123 entrypoint (round 4).

Copies the pre-built infographic entry.png (1024x1024, one page summing up
the world news of Monday 23 November 2026) to <output dir>/entry.png.

Deterministic: the output is a byte-for-byte copy of the committed image,
so repeated runs always produce identical bytes. No network, no randomness,
no clock reads. Standard library only.
"""

import os
import struct
import sys

PNG_MAGIC = b"\x89PNG\r\n\x1a\n"
EXPECTED_WIDTH = 1024
EXPECTED_HEIGHT = 1024


def fail(message):
    sys.stderr.write("error: %s\n" % message)
    return 1


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    source = os.path.join(here, "entry.png")
    target_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    target = os.path.join(target_dir, "entry.png")

    if not os.path.isfile(source):
        return fail("missing expected image file: %s" % source)

    with open(source, "rb") as handle:
        data = handle.read()

    # The file must be a real PNG: 8-byte signature followed by an IHDR
    # chunk declaring the expected 1024x1024 canvas. Anything else means
    # the committed entry.png is corrupt or was replaced by the wrong file.
    if len(data) < 24 or data[:8] != PNG_MAGIC:
        return fail("entry.png is not a valid PNG file "
                    "(bad or missing PNG signature)")

    if data[12:16] != b"IHDR":
        return fail("entry.png is not a valid PNG file "
                    "(first chunk is not IHDR)")

    width, height = struct.unpack(">II", data[16:24])
    if (width, height) != (EXPECTED_WIDTH, EXPECTED_HEIGHT):
        return fail("entry.png has wrong size %dx%d, expected %dx%d"
                    % (width, height, EXPECTED_WIDTH, EXPECTED_HEIGHT))

    # The file must be a whole PNG, not a truncated one: the last 12 bytes
    # must be the IEND chunk (4-byte zero length, "IEND", 4-byte CRC).
    if len(data) < 12 or data[-12:-8] != b"\x00\x00\x00\x00" \
            or data[-8:-4] != b"IEND":
        return fail("entry.png is not a complete PNG file "
                    "(missing IEND trailer chunk; file may be truncated)")

    os.makedirs(target_dir, exist_ok=True)

    with open(target, "wb") as handle:
        handle.write(data)
    os.chmod(target, 0o644)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
