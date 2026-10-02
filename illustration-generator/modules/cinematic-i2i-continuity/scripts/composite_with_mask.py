#!/usr/bin/env python3
"""Composite one full-canvas layer through one full-canvas mask."""

from __future__ import annotations

import argparse
from pathlib import Path

from PIL import Image


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base", required=True)
    parser.add_argument("--layer", required=True)
    parser.add_argument("--mask", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    base = Image.open(args.base).convert("RGBA")
    layer = Image.open(args.layer).convert("RGBA")
    mask = Image.open(args.mask).convert("L")
    if base.size != layer.size or base.size != mask.size:
        raise SystemExit(f"base/layer/mask must share one canvas: {base.size}, {layer.size}, {mask.size}")
    output = Image.composite(layer, base, mask)
    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    output.convert("RGB").save(args.output)


if __name__ == "__main__":
    main()
