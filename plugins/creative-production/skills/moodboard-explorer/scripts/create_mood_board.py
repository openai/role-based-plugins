#!/usr/bin/env python3
"""Create a local image-only mood board app from a JSON spec."""

from __future__ import annotations

import argparse
import json
import re
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PLUGIN_ROOT = ROOT.parents[1]
TEMPLATE = ROOT / "assets" / "mood-board-app"
CODEX_EXEC_RUNNER = PLUGIN_ROOT / "runtime" / "codex_exec_image_batch.py"
SINGLE_IMAGE_GUARD = (
    "Single coherent frame, one composed scene or object detail, not a collage, "
    "not a grid, not a contact sheet, not a scrapbook, not a mood board layout."
)
REMIX_SLOT_ORDER = ("style", "palette", "scene", "props", "character", "format")
STOP_WORDS = {
    "a",
    "an",
    "and",
    "around",
    "as",
    "beside",
    "for",
    "from",
    "in",
    "into",
    "of",
    "on",
    "or",
    "the",
    "to",
    "with",
}


def slugify(value: str) -> str:
    slug = re.sub(r"[^a-zA-Z0-9]+", "-", value.strip().lower()).strip("-")
    return slug or "mood-board"


def normalize_image_prompt(prompt: str) -> str:
    cleaned = str(prompt)
    replacements = [
        (r"image-only editorial mood board tile", "single editorial photograph"),
        (r"image-only mood board tile", "single editorial photograph"),
        (r"moodboard tile", "visual reference image"),
        (r"mood board tile", "visual reference image"),
        (r"mood board image", "visual reference image"),
    ]
    for pattern, replacement in replacements:
        cleaned = re.sub(pattern, replacement, cleaned, flags=re.IGNORECASE)
    if "not a collage" not in cleaned.lower():
        cleaned = f"{cleaned} {SINGLE_IMAGE_GUARD}"
    return cleaned


def compact_text(value: object, limit: int = 140) -> str:
    text = re.sub(r"\s+", " ", str(value or "")).strip(" .")
    if len(text) <= limit:
        return text
    return text[: limit - 3].rsplit(" ", 1)[0].strip(" ,.;") + "..."


def title_words(value: object) -> list[str]:
    return re.findall(r"[A-Za-z0-9]+", str(value or ""))


def focus_label(item: dict) -> str:
    title = compact_text(item.get("title"), 42)
    if title and not re.fullmatch(r"image[-\s]*\d*", title, flags=re.IGNORECASE):
        return title

    candidates = title_words(
        " ".join(str(item.get(key, "")) for key in ("motif", "caption", "prompt"))
    )
    meaningful = [word for word in candidates if word.lower() not in STOP_WORDS and len(word) > 2]
    return " ".join(meaningful[:3]).title() or "Selected Image"


def focus_noun(item: dict) -> str:
    words = [
        word
        for word in title_words(focus_label(item))
        if word.lower() not in STOP_WORDS and not word.isdigit()
    ]
    if not words:
        return "Image"
    if words[-1].lower() in {"study", "route", "frame", "image"} and len(words) > 1:
        return words[-2].title()
    return words[-1].title()


def visual_cue(item: dict) -> str:
    for key in ("caption", "prompt", "motif", "tone"):
        cue = compact_text(item.get(key), 120)
        if cue:
            return cue
    return focus_label(item)


def suggestion(label: str, description: str, prompt_hint: str) -> dict[str, str]:
    return {
        "label": compact_text(label, 34),
        "description": compact_text(description, 118),
        "promptHint": compact_text(prompt_hint, 180),
    }


def generated_remix_suggestions(item: dict) -> dict[str, list[dict[str, str]]]:
    focus = focus_label(item)
    noun = focus_noun(item)
    cue = visual_cue(item)
    return {
        "style": [
            suggestion(
                f"Editorial {noun}",
                f"Cleaner light and hierarchy around {focus}.",
                f"Apply a polished editorial treatment to {focus}; preserve {cue}.",
            ),
            suggestion(
                f"Documentary {noun}",
                f"More natural texture and believable lived-in detail for {focus}.",
                f"Shift {focus} toward documentary realism while preserving {cue}.",
            ),
            suggestion(
                f"Dramatic {noun}",
                "Richer blacks, sharper highlights, and more cinematic emphasis.",
                f"Apply high-contrast cinematic treatment to {focus}; keep {cue} recognizable.",
            ),
        ],
        "palette": [
            suggestion(
                f"Warm {noun}",
                f"Warmer neutrals and tactile highlights around {focus}.",
                f"Shift the palette warmer while preserving the subject and composition of {focus}.",
            ),
            suggestion(
                f"Cool {noun}",
                "Crisper whites, cooler shadows, and restrained technical contrast.",
                f"Use cooler minimal accents around {focus}; keep {cue} intact.",
            ),
            suggestion(
                f"Accent {noun}",
                "A stronger accent color against quieter supporting surfaces.",
                f"Add a controlled accent palette to {focus} without changing the main subject.",
            ),
        ],
        "scene": [
            suggestion(
                f"{noun} Studio",
                f"A cleaner controlled studio setting that keeps {focus} dominant.",
                f"Move {focus} into a cleaner studio-hero setting while preserving {cue}.",
            ),
            suggestion(
                f"{noun} In Use",
                f"A more believable real-world context for {focus}.",
                f"Place {focus} into a realistic usage context; preserve the source image's core cue: {cue}.",
            ),
            suggestion(
                f"{noun} Detail",
                "A tighter scene focused on material, craft, or product detail.",
                f"Create a close-detail scene for {focus}, keeping the most important source cue visible.",
            ),
        ],
        "props": [
            suggestion(
                "Minimal Support",
                f"Reduce surrounding objects so {focus} carries more weight.",
                f"Remove nonessential props and keep {focus} as the dominant read.",
            ),
            suggestion(
                f"{noun} Cues",
                f"Add restrained supporting objects that clarify the context of {focus}.",
                f"Add a few contextual props that reinforce {cue} without distracting from {focus}.",
            ),
            suggestion(
                "Premium Finish",
                "Sharper materials, cleaner surfaces, and more elevated detail.",
                f"Add premium material cues around {focus}; preserve the source image's composition.",
            ),
        ],
        "character": [
            suggestion(
                "Expert Hands",
                f"More credible craft, authority, and purposeful interaction with {focus}.",
                f"If a person appears, make them an expert operator interacting naturally with {focus}.",
            ),
            suggestion(
                "Everyday Use",
                "More approachable human presence while preserving the mood.",
                f"Show {focus} in an everyday user context without losing {cue}.",
            ),
            suggestion(
                "No Human",
                "Let the object, place, or composition carry the frame.",
                f"Remove visible people and let {focus} carry the image.",
            ),
        ],
        "format": [
            suggestion(
                f"Portrait {noun}",
                "Tighter vertical crop for social or story placement.",
                f"Adapt {focus} to a portrait social crop while preserving the key visual read.",
            ),
            suggestion(
                f"Wide {noun}",
                "Broader horizontal composition for landing-page or banner use.",
                f"Adapt {focus} to a wide hero composition with room for layout.",
            ),
            suggestion(
                f"{noun} Crop",
                "Closer inspection of the material, surface, or focal subject.",
                f"Create a closer detail crop of {focus}; keep {cue} legible.",
            ),
        ],
    }


def normalize_remix_option(option: object) -> dict[str, str] | None:
    if isinstance(option, str):
        label = compact_text(option, 34)
        return suggestion(label, label, label)
    if not isinstance(option, dict):
        return None
    label = compact_text(option.get("label") or option.get("title") or option.get("direction"), 34)
    if not label:
        return None
    description = compact_text(
        option.get("description") or option.get("summary") or option.get("detail") or label,
        118,
    )
    prompt_hint = compact_text(option.get("promptHint") or option.get("prompt") or description, 180)
    return suggestion(label, description, prompt_hint)


def normalize_remix_suggestions(item: dict) -> None:
    generated = generated_remix_suggestions(item)
    existing = item.get("remixSuggestions")
    normalized: dict[str, list[dict[str, str]]] = {}

    for slot_id in REMIX_SLOT_ORDER:
        raw_options = existing.get(slot_id) if isinstance(existing, dict) else None
        options = [
            normalized_option
            for normalized_option in (
                normalize_remix_option(option) for option in (raw_options or [])
            )
            if normalized_option
        ]
        normalized[slot_id] = options[:4] if options else generated[slot_id]

    item["remixSuggestions"] = normalized


def validate_spec(spec: dict) -> None:
    items = spec.get("items")
    if not isinstance(items, list) or not items:
        raise ValueError("Spec must include a non-empty items array.")

    for index, item in enumerate(items, start=1):
        if not item.get("id"):
            item["id"] = slugify(item.get("title") or f"image-{index}")
        if not item.get("prompt"):
            raise ValueError(f"Item {index} ({item.get('id')}) is missing prompt.")
        item["prompt"] = normalize_image_prompt(item["prompt"])
        item.setdefault("title", item["id"].replace("-", " ").title())
        item.setdefault("caption", "")
        item.setdefault("source", "Generated mood-board spec.")
        item.setdefault("tone", "calm")
        item.setdefault("motif", "moodboard")
        item.setdefault("palette", ["#ffffff", "#edf4f0", "#b8cfc3", "#426554", "#f8fbf9"])
        normalize_remix_suggestions(item)


def write_static_artifacts(output: Path, spec: dict) -> None:
    data_dir = output / "data"
    (data_dir / "stream-static.json").write_text(
        json.dumps(spec, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    embedded_json = json.dumps(spec, ensure_ascii=False).replace("<", "\\u003c")
    index_html = (output / "index.html").read_text(encoding="utf-8")
    static_html = index_html.replace(
        '  <script src="app.js"></script>',
        f'  <script>window.MOODBOARD_STREAM = {embedded_json};</script>\n  <script src="app.js"></script>',
    )
    (output / "mood-board.html").write_text(static_html, encoding="utf-8")


def plugin_version_label() -> str:
    manifest_path = PLUGIN_ROOT / ".codex-plugin" / "plugin.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    return f"{manifest['name']}@{manifest['version']}"


def write_runtime_config(output: Path) -> None:
    (output / "data" / "runtime-config.json").write_text(
        json.dumps(
            {
                "codexExecRunner": str(CODEX_EXEC_RUNNER),
                "pluginRoot": str(PLUGIN_ROOT),
                "createdByPluginVersion": plugin_version_label(),
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--spec",
        required=True,
        type=Path,
        help="JSON file with meta, signals, and items.",
    )
    parser.add_argument("--output", required=True, type=Path, help="Output app directory.")
    parser.add_argument(
        "--force",
        action="store_true",
        help="Replace output directory if it already exists.",
    )
    args = parser.parse_args()

    spec = json.loads(args.spec.read_text(encoding="utf-8"))
    validate_spec(spec)

    if args.output.exists():
        if not args.force:
            raise FileExistsError(f"{args.output} already exists. Use --force to replace it.")
        shutil.rmtree(args.output)

    shutil.copytree(TEMPLATE, args.output)
    data_dir = args.output / "data"
    data_dir.mkdir(exist_ok=True)
    (data_dir / "stream.json").write_text(
        json.dumps(spec, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    write_runtime_config(args.output)
    write_static_artifacts(args.output, spec)
    generated_dir = args.output / "generated"
    generated_dir.mkdir(exist_ok=True)

    print(
        json.dumps(
            {
                "output": str(args.output),
                "items": len(spec["items"]),
                "runDirectory": str(args.output),
                "streamPath": str(data_dir / "stream.json"),
                "reviewSurface": "render_moodboard_board_widget",
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
