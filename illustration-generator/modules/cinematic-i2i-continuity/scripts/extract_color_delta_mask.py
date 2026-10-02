#!/usr/bin/env python3
"""Build a soft matte for a colored VFX layer while freezing the base frame."""

from __future__ import annotations

import argparse
import math
from pathlib import Path

from PIL import Image, ImageChops, ImageFilter


def odd_filter_size(radius: int) -> int:
    return max(3, radius * 2 + 1)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base", required=True)
    parser.add_argument("--layer", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--include-mask")
    parser.add_argument("--min-delta", type=float, default=24.0)
    parser.add_argument("--min-warmth", type=float, default=18.0)
    parser.add_argument("--grow", type=int, default=2)
    parser.add_argument("--feather", type=float, default=5.0)
    args = parser.parse_args()

    base = Image.open(args.base).convert("RGB")
    layer = Image.open(args.layer).convert("RGB")
    if base.size != layer.size:
        raise SystemExit(f"base/layer must share one canvas: {base.size}, {layer.size}")

    include = None
    if args.include_mask:
        include = Image.open(args.include_mask).convert("L")
        if include.size != base.size:
            raise SystemExit(f"include-mask must match the canvas: {include.size} != {base.size}")

    base_pixels = base.load()
    layer_pixels = layer.load()
    include_pixels = include.load() if include else None
    matte = Image.new("L", base.size, 0)
    matte_pixels = matte.load()

    for y in range(base.height):
        for x in range(base.width):
            if include_pixels is not None and include_pixels[x, y] == 0:
                continue
            br, bg, bb = base_pixels[x, y]
            lr, lg, lb = layer_pixels[x, y]
            delta = math.sqrt((lr - br) ** 2 + (lg - bg) ** 2 + (lb - bb) ** 2)
            warmth = ((lr + lg) / 2.0) - lb
            if delta < args.min_delta or warmth < args.min_warmth or lr < lb:
                continue
            delta_alpha = (delta - args.min_delta) * 3.0
            warmth_alpha = (warmth - args.min_warmth) * 4.0
            matte_pixels[x, y] = int(max(0, min(255, max(delta_alpha, warmth_alpha))))

    if include:
        matte = ImageChops.multiply(matte, include)
    if args.grow > 0:
        matte = matte.filter(ImageFilter.MaxFilter(odd_filter_size(args.grow)))
    if args.feather > 0:
        matte = matte.filter(ImageFilter.GaussianBlur(args.feather))

    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    matte.save(args.output)


if __name__ == "__main__":
    main()
