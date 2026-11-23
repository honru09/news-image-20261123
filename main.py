#!/usr/bin/env python3
"""news-image-20261123 entrypoint.

Copies the pre-built infographic entry.png (1024x1024, one page summing up
the world news of Monday 23 November 2026) to /output/entry.png.

Deterministic: the output is a byte-for-byte copy of the committed image,
so repeated runs always produce identical bytes. No network, no randomness,
no clock reads.
"""

import os
import sys

PNG_MAGIC = b"\x89PNG\r\n\x1a\n"


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    source = os.path.join(here, "entry.png")
    target_dir = "/output"
    target = os.path.join(target_dir, "entry.png")

    with open(source, "rb") as handle:
        data = handle.read()

    if data[:8] != PNG_MAGIC:
        sys.stderr.write("entry.png is not a valid PNG file\n")
        return 1

    os.makedirs(target_dir, exist_ok=True)

    with open(target, "wb") as handle:
        handle.write(data)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
