#!/usr/bin/env python3
"""Place transparent character cutouts on a locked world plate from a JSON layout."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter


def resolve(path: str, root: Path) -> Path:
    value = Path(path).expanduser()
    return value if value.is_absolute() else root / value


def transformed_cutout(source: Path, height: int, mirror: bool, rotation: float, opacity: float) -> Image.Image:
    image = Image.open(source).convert("RGBA")
    alpha_box = image.getchannel("A").getbbox()
    if not alpha_box:
        raise SystemExit(f"cutout has no visible alpha pixels: {source}")
    image = image.crop(alpha_box)
    width = max(1, round(image.width * height / image.height))
    image = image.resize((width, height), Image.Resampling.LANCZOS)
    if mirror:
        image = image.transpose(Image.Transpose.FLIP_LEFT_RIGHT)
    if rotation:
        image = image.rotate(rotation, resample=Image.Resampling.BICUBIC, expand=True)
    if opacity < 1:
        alpha = image.getchannel("A").point(lambda value: round(value * opacity))
        image.putalpha(alpha)
    return image


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--layout", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    layout_path = Path(args.layout).resolve()
    layout = json.loads(layout_path.read_text(encoding="utf-8"))
    root = Path(layout.get("root", ".")).expanduser()
    if not root.is_absolute():
        root = (layout_path.parent / root).resolve()
    base = Image.open(resolve(layout["base"], root)).convert("RGBA")

    layers: list[tuple[dict, Image.Image]] = []
    shadow_plane = Image.new("RGBA", base.size, (0, 0, 0, 0))
    for item in layout.get("layers", []):
        cutout = transformed_cutout(
            resolve(item["path"], root),
            int(item["height"]),
            bool(item.get("mirror", False)),
            float(item.get("rotation", 0)),
            float(item.get("opacity", 1)),
        )
        layers.append((item, cutout))
        shadow = item.get("shadow")
        if shadow:
            x, y = int(item["x"]), int(item["y"])
            width = int(cutout.width * float(shadow.get("width", 0.7)))
            height = max(4, int(cutout.height * float(shadow.get("height", 0.045))))
            center_x = x + cutout.width // 2 + int(shadow.get("offset_x", 0))
            center_y = y + cutout.height + int(shadow.get("offset_y", -height // 2))
            alpha = int(shadow.get("opacity", 80))
            ImageDraw.Draw(shadow_plane).ellipse(
                (center_x - width // 2, center_y - height // 2, center_x + width // 2, center_y + height // 2),
                fill=(0, 0, 0, alpha),
            )

    blur = float(layout.get("shadow_blur", 14))
    if blur > 0:
        shadow_plane = shadow_plane.filter(ImageFilter.GaussianBlur(blur))
    base.alpha_composite(shadow_plane)
    for item, cutout in layers:
        base.alpha_composite(cutout, (int(item["x"]), int(item["y"])))

    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    base.convert("RGB").save(output)


if __name__ == "__main__":
    main()
