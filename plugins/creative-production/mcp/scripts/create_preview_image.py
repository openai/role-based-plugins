#!/usr/bin/env python3
"""Create a deterministic JPEG preview for MCP inline mood-board review."""

from __future__ import annotations

import argparse
from pathlib import Path

from PIL import Image, ImageOps


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path)
    parser.add_argument("target", type=Path)
    parser.add_argument("--max-edge", type=int, default=720)
    parser.add_argument("--quality", type=int, default=72)
    return parser.parse_args()


def flatten_to_rgb(image: Image.Image) -> Image.Image:
    image = ImageOps.exif_transpose(image)
    if image.mode in {"RGBA", "LA"} or (image.mode == "P" and "transparency" in image.info):
        canvas = Image.new("RGB", image.size, (255, 255, 255))
        alpha = image.convert("RGBA").getchannel("A")
        canvas.paste(image.convert("RGB"), mask=alpha)
        return canvas
    return image.convert("RGB")


def main() -> None:
    args = parse_args()
    args.target.parent.mkdir(parents=True, exist_ok=True)
    with Image.open(args.source) as image:
        preview = flatten_to_rgb(image)
        preview.thumbnail((args.max_edge, args.max_edge), Image.Resampling.LANCZOS)
        preview.save(
            args.target,
            "JPEG",
            quality=args.quality,
            optimize=True,
            progressive=True,
        )


if __name__ == "__main__":
    main()
