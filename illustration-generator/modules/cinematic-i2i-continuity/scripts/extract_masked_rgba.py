#!/usr/bin/env python3
"""Extract a reusable RGBA overlay from an image and a grayscale semantic mask."""

from __future__ import annotations

import argparse
from pathlib import Path

from PIL import Image


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--image", required=True)
    parser.add_argument("--mask", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--padding", type=int, default=0)
    parser.add_argument("--opacity", type=float, default=1.0)
    parser.add_argument("--preserve-canvas", action="store_true")
    args = parser.parse_args()

    image = Image.open(args.image).convert("RGBA")
    mask = Image.open(args.mask).convert("L")
    if image.size != mask.size:
        raise SystemExit(f"image and mask sizes differ: {image.size} != {mask.size}")
    if not 0 <= args.opacity <= 1:
        raise SystemExit("--opacity must be between 0 and 1")

    if args.opacity < 1:
        mask = mask.point(lambda value: round(value * args.opacity))
    image.putalpha(mask)

    if not args.preserve_canvas:
        box = mask.getbbox()
        if not box:
            raise SystemExit("mask contains no visible pixels")
        left, top, right, bottom = box
        padding = max(0, args.padding)
        image = image.crop((
            max(0, left - padding),
            max(0, top - padding),
            min(image.width, right + padding),
            min(image.height, bottom + padding),
        ))

    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    image.save(output)


if __name__ == "__main__":
    main()
