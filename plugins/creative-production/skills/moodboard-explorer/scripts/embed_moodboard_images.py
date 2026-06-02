#!/usr/bin/env python3
"""Embed generated image files into a Moodboard Explorer app."""

from __future__ import annotations

import argparse
import json
import re
import shutil
from pathlib import Path


def safe_filename(value: str, suffix: str) -> str:
    stem = re.sub(r"[^a-zA-Z0-9._-]+", "-", value.strip()).strip("-")
    return f"{stem or 'image'}{suffix.lower() or '.png'}"


def parse_image_mapping(value: str) -> tuple[str, Path]:
    if "=" not in value:
        raise argparse.ArgumentTypeError("--image must look like item-id=/path/to/image.png")
    item_id, file_path = value.split("=", 1)
    item_id = item_id.strip()
    if not item_id:
        raise argparse.ArgumentTypeError("--image item id cannot be empty")
    return item_id, Path(file_path).expanduser()


def to_static_stream(stream: dict) -> dict:
    return {
        **stream,
        "items": [
            {**item, "imageUrl": item["imageUrl"][1:]}
            if isinstance(item.get("imageUrl"), str) and item["imageUrl"].startswith("/")
            else item
            for item in stream.get("items", [])
        ],
    }


def write_static_artifacts(app_dir: Path, stream: dict) -> None:
    static_stream = to_static_stream(stream)
    data_dir = app_dir / "data"
    (data_dir / "stream-static.json").write_text(
        json.dumps(static_stream, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    embedded_json = json.dumps(static_stream, ensure_ascii=False).replace("<", "\\u003c")
    index_html = (app_dir / "index.html").read_text(encoding="utf-8")
    app_script_tag = '  <script src="app.js"></script>'
    if app_script_tag not in index_html:
        raise SystemExit("Could not find app.js script tag in moodboard index.html")
    static_html = index_html.replace(
        app_script_tag,
        f"  <script>window.MOODBOARD_STREAM = {embedded_json};</script>\n{app_script_tag}",
    )
    (app_dir / "mood-board.html").write_text(static_html, encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--app", required=True, type=Path, help="Moodboard app output directory.")
    parser.add_argument(
        "--image",
        action="append",
        default=[],
        type=parse_image_mapping,
        help="Mapping from moodboard item id to image file, e.g. tile-1=/tmp/tile.png.",
    )
    args = parser.parse_args()

    if not args.image:
        raise SystemExit("Provide at least one --image mapping.")

    app_dir = args.app.expanduser().resolve()
    stream_path = app_dir / "data" / "stream.json"
    generated_dir = app_dir / "generated"
    if not stream_path.exists():
        raise SystemExit(f"Could not find moodboard stream: {stream_path}")

    stream = json.loads(stream_path.read_text(encoding="utf-8"))
    items = {str(item.get("id")): item for item in stream.get("items", [])}
    generated_dir.mkdir(exist_ok=True)

    embedded: list[dict[str, str]] = []
    for item_id, source_path in args.image:
        if item_id not in items:
            raise SystemExit(f"Unknown moodboard item id: {item_id}")
        source_path = source_path.expanduser().resolve()
        if not source_path.exists():
            raise SystemExit(f"Image file does not exist: {source_path}")

        filename = safe_filename(item_id, source_path.suffix)
        target_path = generated_dir / filename
        if source_path != target_path.resolve():
            shutil.copy2(source_path, target_path)
        items[item_id]["imageUrl"] = f"/generated/{filename}"
        embedded.append({"id": item_id, "path": str(target_path)})

    stream_path.write_text(
        json.dumps(stream, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    write_static_artifacts(app_dir, stream)

    print(
        json.dumps(
            {
                "app": str(app_dir),
                "runDirectory": str(app_dir),
                "streamPath": str(stream_path),
                "reviewSurface": "render_moodboard_board_widget",
                "embedded": embedded,
                "handoff": (
                    "Render the inline MCP mood board with runDirectory. "
                    "Do not show the local HTML/server surface unless the user asks to debug it."
                ),
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
