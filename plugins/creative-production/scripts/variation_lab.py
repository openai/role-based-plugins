#!/usr/bin/env python3
"""Build universal Variation Lab manifests and static review surfaces."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
from html import escape
from pathlib import Path
from typing import Any
from urllib.parse import unquote, urlparse

COMMON_LOCKS = [
    {
        "id": "approved-facts",
        "label": "Approved facts",
        "description": "Do not invent claims, prices, dates, specs, certifications, endorsements, or source evidence.",
    },
    {
        "id": "brand-safety",
        "label": "Brand safety",
        "description": "Preserve brand constraints, avoid competitor marks, and keep provenance reviewable.",
    },
]

LOCAL_ASSET_DIR = "variation-assets"

SLOT_LIBRARY: dict[str, dict[str, Any]] = {
    "subject": {
        "label": "Subject / Product",
        "description": "Swap or preserve the main product, object, venue, chart, page, or hero subject.",
        "sources": ["upload", "asset-library", "brief"],
        "action": "Change subject",
        "promptHint": "Replace only the subject slot while preserving the selected composition and locked facts.",
    },
    "character": {
        "label": "Character",
        "description": "Change the person, persona, role, age range, wardrobe, expression, or pose.",
        "sources": ["character-library", "brief"],
        "action": "Change character",
        "promptHint": "Replace or refine the human character while preserving the subject and approved copy.",
    },
    "scene": {
        "label": "Scene / Location",
        "description": "Change environment, location, time of day, occasion, usage moment, or setting.",
        "sources": ["scene-library", "brief"],
        "action": "Change scene",
        "promptHint": "Move the asset into a new scene while preserving locked subject facts and composition intent.",
    },
    "style": {
        "label": "Style",
        "description": "Change polish treatment, lighting, rendering style, material finish, or visual system.",
        "sources": ["style-library", "selected-route", "brief"],
        "action": "Change style",
        "promptHint": "Apply a different visual treatment while preserving content, subject identity, and layout intent.",
    },
    "copy": {
        "label": "Copy",
        "description": "Change headline, callouts, CTA, labels, section titles, or narrative emphasis.",
        "sources": ["approved-copy", "brief"],
        "action": "Change copy",
        "promptHint": "Update copy only from approved text and keep generated text reviewable.",
    },
    "format": {
        "label": "Format",
        "description": "Change aspect ratio, channel, crop, export size, or placement surface.",
        "sources": ["channel-preset", "brief"],
        "action": "Change format",
        "promptHint": "Adapt the asset to another format while preserving safe zones and locked content.",
    },
    "camera": {
        "label": "Camera / Shot",
        "description": "Change angle, crop, lens feel, zoom, pan, or detail emphasis.",
        "sources": ["shot-library", "brief"],
        "action": "Change camera",
        "promptHint": "Generate camera or composition variants while preserving the selected subject and facts.",
    },
    "palette": {
        "label": "Palette / Materials",
        "description": "Change color palette, material surfaces, texture, or finish cues.",
        "sources": ["style-library", "brand-palette", "brief"],
        "action": "Change palette",
        "promptHint": "Vary palette and materials without changing approved content or source meaning.",
    },
    "props": {
        "label": "Props / Context",
        "description": "Change supporting objects, environmental cues, fixtures, accessories, or contextual signals.",
        "sources": ["scene-library", "brief"],
        "action": "Change props",
        "promptHint": "Change supporting context only; do not introduce unsupported claims or new brands.",
    },
    "layout": {
        "label": "Layout",
        "description": "Change hierarchy, card structure, spacing, callout placement, or module arrangement.",
        "sources": ["template-library", "brief"],
        "action": "Change layout",
        "promptHint": "Recompose layout while preserving exact facts, data, copy, and source constraints.",
    },
    "proof_data": {
        "label": "Proof / Data",
        "description": "Change cited proof, data view, evidence module, quote, or source-backed support.",
        "sources": ["approved-source", "data", "brief"],
        "action": "Change proof",
        "promptHint": "Change proof only from supplied source material and preserve source traceability.",
    },
}

OPTION_LIBRARY: dict[str, list[dict[str, str]]] = {
    "style": [
        {
            "id": "alpine-weather-editorial",
            "label": "Alpine Weather Editorial",
            "description": "Cold air, mist, technical outdoor campaign polish, restrained but premium.",
            "promptHint": "Apply an alpine weather editorial treatment with mist, cold daylight, and technical outdoor polish.",
        },
        {
            "id": "rain-slick-realism",
            "label": "Rain-Slick Realism",
            "description": "Wet surfaces, believable weather, high contrast droplets, grounded product realism.",
            "promptHint": "Use rainy realistic lighting and wet surface detail while preserving the selected asset.",
        },
        {
            "id": "technical-blueprint-overlay",
            "label": "Technical Blueprint Overlay",
            "description": "Precise diagrams, measurement marks, blueprint energy, controlled product clarity.",
            "promptHint": "Add a technical blueprint-style treatment using exact supplied copy only.",
        },
        {
            "id": "product-lab-test-bench",
            "label": "Product Lab Test Bench",
            "description": "Testing bench, material proof cues, precise lights, performance validation mood.",
            "promptHint": "Move the style toward a controlled product test bench without inventing proof claims.",
        },
        {
            "id": "museum-plinth-sport",
            "label": "Museum Plinth Sport",
            "description": "Gallery plinth, premium sport object, quiet white space, product-as-icon.",
            "promptHint": "Treat the asset like a premium sport object on a gallery plinth.",
        },
    ],
    "palette": [
        {
            "id": "volt-charcoal",
            "label": "Volt Green + Charcoal",
            "description": "Sharper performance contrast with electric green accents and dark neutrals.",
            "promptHint": "Shift accents toward volt green and charcoal while preserving product colors.",
        },
        {
            "id": "red-clay-sand",
            "label": "Red Clay + Sand",
            "description": "Warm trail earth, desert dust, clay-red shadows, sun-faded neutrals.",
            "promptHint": "Use a red clay and sand palette around the asset without recoloring the product inaccurately.",
        },
        {
            "id": "ice-blue-silver",
            "label": "Ice Blue + Silver",
            "description": "Cool technical freshness, icy highlights, clean metallic restraint.",
            "promptHint": "Use ice blue and silver environmental accents for a crisp technical feel.",
        },
        {
            "id": "black-yellow-technical",
            "label": "Black + Safety Yellow",
            "description": "High-contrast technical signage, performance gear, sharper callout energy.",
            "promptHint": "Use black and safety-yellow graphic accents while keeping approved copy exact.",
        },
    ],
    "character": [
        {
            "id": "older-trail-coach",
            "label": "Older Trail Coach",
            "description": "Experienced, credible, warm, practical outdoor authority.",
            "promptHint": "Change the character to an older trail coach while preserving pose and product focus.",
        },
        {
            "id": "weekend-hiker",
            "label": "Weekend Hiker",
            "description": "Approachable recreational user, real trail-prep energy, less influencer polish.",
            "promptHint": "Change the character to a weekend hiker with believable gear and expression.",
        },
        {
            "id": "elite-runner",
            "label": "Elite Runner",
            "description": "Lean performance feel, confident pre-run energy, more athletic styling.",
            "promptHint": "Change the character to an elite trail runner without adding fake endorsements.",
        },
        {
            "id": "retail-associate",
            "label": "Retail Associate",
            "description": "Helpful in-store expert presenting the product clearly.",
            "promptHint": "Change the character to a running-store associate in a retail fitting context.",
        },
        {
            "id": "product-only",
            "label": "No Human",
            "description": "Remove the person and make the object carry the entire ad.",
            "promptHint": "Remove the character and convert the asset into a product-only composition.",
        },
    ],
    "scene": [
        {
            "id": "forest-trailhead",
            "label": "Forest Trailhead",
            "description": "Morning trees, trail sign, damp ground, real pre-run setting.",
            "promptHint": "Move the asset into a forest trailhead scene with morning light.",
        },
        {
            "id": "rainy-city-to-trail",
            "label": "Rainy City-to-Trail",
            "description": "Urban wet pavement, transit-to-trail energy, reflective highlights.",
            "promptHint": "Move the asset into a rainy city-to-trail commute scene.",
        },
        {
            "id": "running-store-wall",
            "label": "Running Store Wall",
            "description": "Retail shoe wall, fitting bench, expert recommendation context.",
            "promptHint": "Move the asset into a running-store wall scene without adding fake prices.",
        },
        {
            "id": "gym-recovery-bench",
            "label": "Gym Recovery Bench",
            "description": "Locker-room bench, post-run gear, practical training context.",
            "promptHint": "Move the asset into a gym recovery bench scene.",
        },
        {
            "id": "mountain-ridge",
            "label": "Mountain Ridge",
            "description": "Open elevation, rugged horizon, aspirational outdoor scale.",
            "promptHint": "Move the asset into a mountain ridge overlook while preserving product fidelity.",
        },
    ],
    "copy": [
        {
            "id": "remove-callouts",
            "label": "Remove Callouts",
            "description": "Keep the main headline only; remove small arrows and tags.",
            "promptHint": "Remove small callouts and keep only approved main headline copy.",
        },
        {
            "id": "feature-tags-only",
            "label": "Feature Tags Only",
            "description": "Use only the approved short feature tags, no large headline.",
            "promptHint": "Use only approved short feature tags and no extra body text.",
        },
        {
            "id": "copy-safe-space",
            "label": "More Copy Space",
            "description": "Create clean space for deterministic text overlay later.",
            "promptHint": "Create clean negative space for later deterministic copy overlays.",
        },
        {
            "id": "no-text",
            "label": "No Text",
            "description": "Remove all readable text for a product-only visual layer.",
            "promptHint": "Remove all readable text and leave no generated copy.",
        },
    ],
    "format": [
        {
            "id": "vertical-reels",
            "label": "Vertical Reels Cover",
            "description": "Tall crop, phone-first composition, product still large.",
            "promptHint": "Adapt to a vertical social cover composition with safe top and bottom margins.",
        },
        {
            "id": "landscape-display",
            "label": "Landscape Display",
            "description": "Wider composition for web, display, or presentation use.",
            "promptHint": "Adapt to a landscape display composition with clear product visibility.",
        },
        {
            "id": "square-feed",
            "label": "Square Feed",
            "description": "Balanced square crop for dense review and paid social.",
            "promptHint": "Adapt to a square feed composition without cropping important content.",
        },
        {
            "id": "web-hero-strip",
            "label": "Web Hero Strip",
            "description": "Wide shallow hero with room for deterministic copy.",
            "promptHint": "Adapt to a wide web hero strip with clean copy-safe space.",
        },
    ],
    "camera": [
        {
            "id": "outsole-macro",
            "label": "Outsole Macro",
            "description": "Extreme grip detail, tactile rubber and mud texture.",
            "promptHint": "Change camera emphasis to an outsole macro detail.",
        },
        {
            "id": "overhead-gear-flatlay",
            "label": "Overhead Gear Flatlay",
            "description": "Product with trail gear, clear layout, inspection-friendly.",
            "promptHint": "Change to an overhead gear flatlay composition.",
        },
        {
            "id": "low-angle-hero",
            "label": "Low Angle Hero",
            "description": "More scale and drama, shoe feels monumental.",
            "promptHint": "Use a low-angle hero camera while preserving the product.",
        },
        {
            "id": "handoff-closeup",
            "label": "Handoff Closeup",
            "description": "Human handoff moment, product fills frame, clear social energy.",
            "promptHint": "Use a handoff closeup with natural hands and strong product focus.",
        },
    ],
    "subject": [
        {
            "id": "new-uploaded-product",
            "label": "Use New Uploaded Product",
            "description": "Keep the route, replace the product reference.",
            "promptHint": "Replace the subject with a new uploaded product while preserving the selected route.",
        },
        {
            "id": "product-family",
            "label": "Product Family",
            "description": "Show multiple related variants as one family system.",
            "promptHint": "Expand the subject into a product family without inventing details.",
        },
        {
            "id": "product-only-packshot",
            "label": "Product-Only Packshot",
            "description": "Reduce narrative and make the product the only subject.",
            "promptHint": "Make the subject a product-only packshot in the selected style.",
        },
    ],
    "props": [
        {
            "id": "mud-splashes",
            "label": "Mud Splashes",
            "description": "Adds trail-use texture without hiding the product.",
            "promptHint": "Add controlled mud and trail texture as supporting context only.",
        },
        {
            "id": "trail-map",
            "label": "Trail Map",
            "description": "Adds planning, route, and outdoor-use context.",
            "promptHint": "Add trail map context without adding fake location claims.",
        },
        {
            "id": "hydration-vest",
            "label": "Hydration Vest",
            "description": "Adds runner gear context and credible use cues.",
            "promptHint": "Add hydration vest and trail gear as supporting props.",
        },
        {
            "id": "retail-tags",
            "label": "Retail Shelf Tags",
            "description": "Adds retail context without prices or fake discounts.",
            "promptHint": "Add retail shelf tag context without prices or fake promos.",
        },
    ],
    "layout": [
        {
            "id": "split-product-copy",
            "label": "Split Product + Copy",
            "description": "Product side, clean text side, deterministic overlay ready.",
            "promptHint": "Recompose into a split product and copy layout with clean safe space.",
        },
        {
            "id": "badge-corners",
            "label": "Badge Corners",
            "description": "Small corner badges, central product hero, sparse copy.",
            "promptHint": "Use sparse corner badges without adding unsupported claims.",
        },
        {
            "id": "full-bleed-hero",
            "label": "Full-Bleed Hero",
            "description": "Edge-to-edge image with product and scene carrying the message.",
            "promptHint": "Use a full-bleed hero layout with minimal generated text.",
        },
    ],
    "proof_data": [
        {
            "id": "source-card",
            "label": "Source Card",
            "description": "Add a deterministic source/proof card area for later overlay.",
            "promptHint": "Reserve space for a deterministic proof card; do not invent evidence.",
        },
        {
            "id": "spec-placeholder",
            "label": "Spec Placeholder",
            "description": "Create a blank spec area, to be filled by approved data later.",
            "promptHint": "Reserve a blank spec area for approved data; do not generate fake specs.",
        },
    ],
}

ASSET_PROFILES: dict[str, dict[str, Any]] = {
    "image_ad": {
        "label": "Image Ad",
        "slots": [
            "subject",
            "character",
            "scene",
            "style",
            "copy",
            "format",
            "camera",
            "palette",
            "props",
        ],
        "locks": [
            {
                "id": "product-fidelity",
                "label": "Product fidelity",
                "description": "Preserve visible shape, markings, labels, proportions, and material truth unless subject is intentionally changed.",
            },
            {
                "id": "approved-copy",
                "label": "Approved copy",
                "description": "Use exact supplied ad copy only; do not add subtitles or unsupported body text.",
            },
        ],
        "suggested": [
            "change-character",
            "change-scene",
            "change-style",
            "change-copy",
            "change-format",
            "more-like-this",
        ],
    },
    "style_route": {
        "label": "Style Route",
        "slots": ["style", "palette", "scene", "character", "subject", "copy", "format"],
        "locks": [
            {
                "id": "anchor-integrity",
                "label": "Anchor integrity",
                "description": "Preserve the selected anchor asset, approved copy, and route intent unless a slot explicitly changes them.",
            },
        ],
        "suggested": [
            "change-style",
            "change-scene",
            "change-character",
            "change-subject",
            "more-like-this",
        ],
    },
    "scene": {
        "label": "Scene",
        "slots": ["scene", "props", "character", "camera", "style", "subject", "format"],
        "locks": [
            {
                "id": "scene-truth",
                "label": "Scene truth",
                "description": "Keep the usage moment plausible and preserve safety, service, or venue constraints.",
            },
        ],
        "suggested": [
            "change-scene",
            "change-props",
            "change-character",
            "change-camera",
            "more-like-this",
        ],
    },
    "moodboard": {
        "label": "Moodboard",
        "slots": ["style", "palette", "scene", "props", "character", "format"],
        "locks": [
            {
                "id": "territory",
                "label": "Territory",
                "description": "Preserve the selected mood territory and audience feel unless the territory slot changes.",
            },
        ],
        "suggested": ["change-style", "change-palette", "change-scene", "more-like-this"],
    },
    "chart": {
        "label": "Chart",
        "slots": ["style", "palette", "layout", "format", "copy"],
        "locks": [
            {
                "id": "data-integrity",
                "label": "Data integrity",
                "description": "Chart values, axes, units, and source notes must remain exact and deterministic.",
            },
            {
                "id": "source-traceability",
                "label": "Source traceability",
                "description": "Do not alter cited sources or evidence without approved replacement data.",
            },
        ],
        "suggested": ["change-style", "change-palette", "change-layout", "change-format"],
    },
    "document": {
        "label": "Document / Page",
        "slots": ["layout", "style", "palette", "copy", "proof_data", "format"],
        "locks": [
            {
                "id": "source-claims",
                "label": "Source claims",
                "description": "Preserve claims, citations, proof, and review status unless supplied source material changes.",
            },
        ],
        "suggested": ["change-layout", "change-style", "change-copy", "change-proof"],
    },
    "video": {
        "label": "Video",
        "slots": ["scene", "character", "style", "copy", "format", "camera", "props"],
        "locks": [
            {
                "id": "story-continuity",
                "label": "Story continuity",
                "description": "Preserve selected narrative, product truth, and approved voice/copy constraints.",
            },
        ],
        "suggested": [
            "change-scene",
            "change-character",
            "change-style",
            "change-format",
            "change-camera",
        ],
    },
    "generic_visual": {
        "label": "Generic Visual",
        "slots": [
            "subject",
            "scene",
            "style",
            "copy",
            "format",
            "camera",
            "palette",
            "props",
            "layout",
        ],
        "locks": [],
        "suggested": [
            "change-subject",
            "change-scene",
            "change-style",
            "change-format",
            "more-like-this",
        ],
    },
}


def normalize_asset_type(value: str | None) -> str:
    asset_type = (value or "generic_visual").strip().lower().replace("-", "_")
    aliases = {
        "ad": "image_ad",
        "image-ad": "image_ad",
        "style": "style_route",
        "white_paper": "document",
        "page": "document",
        "object": "generic_visual",
    }
    asset_type = aliases.get(asset_type, asset_type)
    if asset_type not in ASSET_PROFILES:
        asset_type = "generic_visual"
    return asset_type


def default_slots(asset_type: str) -> list[dict[str, Any]]:
    profile = ASSET_PROFILES[normalize_asset_type(asset_type)]
    return [{**SLOT_LIBRARY[slot_id], "id": slot_id} for slot_id in profile["slots"]]


def default_locks(asset_type: str) -> list[dict[str, Any]]:
    profile = ASSET_PROFILES[normalize_asset_type(asset_type)]
    return COMMON_LOCKS + profile.get("locks", [])


def normalize_asset(
    item: dict[str, Any], index: int, *, asset_type: str, source_skill: str | None = None
) -> dict[str, Any]:
    src = item.get("src") or item.get("image") or item.get("imageUrl") or item.get("output")
    href = item.get("href") or src
    label = item.get("label") or item.get("title") or f"Asset {index}"
    asset_id = item.get("asset_id") or item.get("id") or f"asset-{index:02d}"
    return {
        "asset_id": str(asset_id),
        "asset_type": normalize_asset_type(str(item.get("asset_type") or asset_type)),
        "label": str(label),
        "image": str(src) if src else "",
        "href": str(href) if href else "",
        "source": {
            "skill": item.get("skill") or source_skill,
            "route": item.get("route") or item.get("family") or item.get("routeName"),
            "prompt": item.get("prompt"),
            "index": item.get("index", index),
        },
        "slots": item.get("slots") or default_slots(str(item.get("asset_type") or asset_type)),
        "locks": item.get("locks") or default_locks(str(item.get("asset_type") or asset_type)),
        "suggested_variations": item.get("suggested_variations")
        or ASSET_PROFILES[normalize_asset_type(str(item.get("asset_type") or asset_type))][
            "suggested"
        ],
    }


def build_variation_manifest(
    review_items: list[dict[str, Any]],
    *,
    title: str,
    asset_type: str,
    source_skill: str | None = None,
    summary: str | None = None,
) -> dict[str, Any]:
    normalized_type = normalize_asset_type(asset_type)
    return {
        "version": 1,
        "meta": {
            "title": title,
            "summary": summary
            or "Choose an output, then decide which slots to change while keeping the right locks in place.",
            "default_asset_type": normalized_type,
            "source_skill": source_skill,
        },
        "slot_library": SLOT_LIBRARY,
        "option_library": OPTION_LIBRARY,
        "asset_profiles": ASSET_PROFILES,
        "assets": [
            normalize_asset(item, index, asset_type=normalized_type, source_skill=source_skill)
            for index, item in enumerate(review_items, start=1)
        ],
    }


def _image_source_path(value: str | None) -> Path | None:
    if not value:
        return None
    src = str(value)
    if src.startswith(("http://", "https://", "data:")):
        return None
    if src.startswith("file://"):
        parsed = urlparse(src)
        if parsed.netloc not in {"", "localhost"}:
            return None
        return Path(unquote(parsed.path)).expanduser()
    path = Path(src).expanduser()
    if not path.is_absolute():
        return None
    return path


def _relative_to_out_dir(path: Path, out_dir: Path) -> str | None:
    try:
        return path.resolve().relative_to(out_dir.resolve()).as_posix()
    except ValueError:
        return None


def _portable_asset_name(index: int, source_path: Path) -> str:
    stem = re.sub(r"[^a-zA-Z0-9]+", "-", source_path.stem.lower()).strip("-") or "asset"
    suffix = source_path.suffix.lower()
    if suffix not in {".png", ".jpg", ".jpeg", ".webp", ".svg"}:
        suffix = ".png"
    digest = hashlib.sha256(str(source_path.resolve()).encode("utf-8")).hexdigest()[:10]
    return f"{index:02d}-{stem}-{digest}{suffix}"


def localize_asset_images(out_dir: Path, manifest: dict[str, Any]) -> int:
    """Make absolute local image references portable inside the served lab folder."""
    localized = 0
    asset_dir = out_dir / LOCAL_ASSET_DIR
    for index, asset in enumerate(manifest.get("assets") or [], start=1):
        image = asset.get("image")
        source_path = _image_source_path(image)
        if source_path is None:
            continue
        if not source_path.exists() or not source_path.is_file():
            continue

        existing_relative = _relative_to_out_dir(source_path, out_dir)
        if existing_relative:
            portable_image = existing_relative
        else:
            asset_dir.mkdir(parents=True, exist_ok=True)
            target_path = asset_dir / _portable_asset_name(index, source_path)
            if source_path.resolve() != target_path.resolve():
                shutil.copy2(source_path, target_path)
            portable_image = target_path.relative_to(out_dir).as_posix()

        if asset.get("href") == image:
            asset["href"] = portable_image
        asset["image"] = portable_image
        localized += 1
    return localized


def render_variation_lab_html(
    out_dir: Path, manifest: dict[str, Any], output_name: str = "variation-lab.html"
) -> Path:
    localize_asset_images(out_dir, manifest)
    assets_json = json_for_script_tag(manifest)
    first_asset = (manifest.get("assets") or [{}])[0]
    first_image = first_asset.get("image") or ""
    title = manifest.get("meta", {}).get("title") or "Variation Lab"
    cards = []
    for index, asset in enumerate(manifest.get("assets", []), start=1):
        image = escape(str(asset.get("image") or ""), quote=True)
        label = escape(str(asset.get("label") or f"Asset {index}"))
        asset_id = escape(str(asset.get("asset_id") or f"asset-{index:02d}"), quote=True)
        selected = " selected" if index == 1 else ""
        image_html = (
            f'<img src="{image}" alt="">' if image else '<div class="missing-image">No image</div>'
        )
        cards.append(
            f'<div class="asset-tile{selected}" data-asset-id="{asset_id}">'
            f'<button class="asset-card" type="button" aria-label="{label}">{image_html}</button>'
            f'<button class="reject-thumb" type="button" aria-label="Reject {label}">×</button>'
            f"</div>"
        )

    html = f"""<!doctype html>
<html>
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{escape(str(title))}</title>
<style>
:root {{
  color-scheme: light;
  --bg: #fff;
  --ink: #181818;
  --muted: #666;
  --line: #e5e5e5;
  --soft: #fafafa;
  --accent: #245f4c;
}}
* {{ box-sizing: border-box; }}
body {{ margin: 0; background: var(--bg); color: var(--ink); font-family: Arial, sans-serif; }}
button, select {{ font: inherit; }}
main {{ display: grid; grid-template-columns: minmax(340px, 0.92fr) minmax(360px, 1.08fr); gap: 22px; align-items: start; min-height: 100vh; max-width: 1240px; margin: 0 auto; padding: 24px; }}
.hero {{ display: grid; gap: 10px; }}
.asset-list {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(56px, 1fr)); gap: 8px; }}
.asset-tile {{ position: relative; aspect-ratio: 1; border-radius: 6px; overflow: hidden; }}
.asset-card {{ width: 100%; border: 0; border-radius: 6px; background: #fff; padding: 0; overflow: hidden; cursor: pointer; aspect-ratio: 1; }}
.asset-tile.selected .asset-card {{ box-shadow: 0 0 0 3px rgba(36, 95, 76, 0.18); }}
.asset-card img, .missing-image {{ width: 100%; height: 100%; object-fit: cover; display: block; background: var(--soft); }}
.missing-image {{ display: grid; place-items: center; color: var(--muted); font-size: 12px; }}
.asset-tile.rejected img {{ opacity: .28; filter: grayscale(1); }}
.asset-tile.rejected::after {{ content: ""; position: absolute; left: -12%; top: 50%; width: 124%; border-top: 2px solid rgba(24, 24, 24, .72); transform: rotate(-28deg); pointer-events: none; }}
.reject-thumb {{ position: absolute; top: 4px; right: 4px; width: 18px; height: 18px; border: 0; border-radius: 999px; background: rgba(255, 255, 255, .9); color: #333; font-size: 13px; line-height: 17px; padding: 0; cursor: pointer; opacity: .88; }}
.reject-thumb:hover {{ background: #181818; color: #fff; }}
.preview {{ position: relative; border: 0; border-radius: 8px; overflow: hidden; background: var(--soft); }}
.preview img {{ width: 100%; height: auto; display: block; }}
.preview.rejected img {{ opacity: .32; filter: grayscale(1); }}
.preview.rejected::after {{ content: ""; position: absolute; left: -8%; top: 50%; width: 116%; border-top: 3px solid rgba(24, 24, 24, .72); transform: rotate(-25deg); pointer-events: none; }}
.reject-active {{ position: absolute; top: 10px; right: 10px; z-index: 2; width: 30px; height: 30px; border: 0; border-radius: 999px; background: rgba(255, 255, 255, .92); color: #222; font-size: 20px; line-height: 28px; cursor: pointer; box-shadow: 0 1px 6px rgba(0, 0, 0, .16); }}
.reject-active:hover {{ background: #181818; color: #fff; }}
.panel {{ border: 1px solid var(--line); border-radius: 8px; background: #fff; overflow: hidden; }}
.section {{ padding: 16px; border-bottom: 1px solid var(--line); }}
.section:last-child {{ border-bottom: 0; }}
.section h3 {{ margin: 0 0 10px; font-size: 13px; letter-spacing: .04em; text-transform: uppercase; color: #444; }}
.control-row {{ display: grid; grid-template-columns: 76px 1fr; gap: 10px; align-items: center; margin-bottom: 12px; }}
.control-row label {{ font-size: 13px; color: var(--muted); }}
select {{ width: 100%; border: 1px solid var(--line); border-radius: 8px; background: #fff; padding: 9px 10px; color: var(--ink); }}
.option-menu {{ display: grid; gap: 8px; }}
.option {{ display: grid; grid-template-columns: 34px 1fr; gap: 10px; align-items: start; border: 1px solid var(--line); border-radius: 8px; background: var(--soft); padding: 9px; cursor: pointer; }}
.option.selected {{ border-color: var(--accent); background: #f4faf7; }}
.plus {{ width: 28px; height: 28px; border: 1px solid var(--line); border-radius: 999px; background: #fff; cursor: pointer; font-weight: 700; line-height: 1; }}
.plus:hover {{ border-color: var(--accent); color: var(--accent); }}
.option strong {{ display: block; font-size: 13px; margin: 1px 0 4px; }}
.option p {{ margin: 0; color: var(--muted); font-size: 12px; line-height: 1.35; }}
.selected-tray {{ display: flex; flex-wrap: wrap; gap: 8px; min-height: 34px; }}
.chip {{ display: inline-flex; align-items: center; gap: 8px; border: 1px solid var(--line); border-radius: 999px; background: var(--soft); padding: 7px 9px; font-size: 12px; }}
.chip button {{ border: 0; background: transparent; color: var(--muted); cursor: pointer; padding: 0; }}
.empty {{ color: var(--muted); font-size: 13px; }}
.composer-actions {{ display: flex; flex-wrap: wrap; gap: 8px; margin-top: 12px; }}
.composer-actions button {{ border: 1px solid var(--line); border-radius: 8px; background: #fff; padding: 9px 11px; cursor: pointer; }}
.composer-actions .primary {{ border-color: var(--accent); background: var(--accent); color: #fff; }}
.handoff-status {{ margin-top: 9px; min-height: 18px; color: var(--muted); font-size: 12px; line-height: 1.4; }}
.handoff-output {{ margin-top: 12px; border: 1px solid var(--line); border-radius: 8px; background: var(--soft); overflow: hidden; }}
.handoff-output[hidden] {{ display: none; }}
.handoff-head {{ display: flex; justify-content: space-between; gap: 10px; align-items: center; padding: 9px; border-bottom: 1px solid var(--line); }}
.handoff-head strong {{ font-size: 13px; }}
.handoff-head button {{ border: 1px solid var(--line); border-radius: 8px; background: #fff; padding: 7px 9px; cursor: pointer; font-size: 12px; }}
.handoff-output details {{ background: #fff; }}
.handoff-output summary {{ cursor: pointer; padding: 9px 10px; color: var(--muted); font-size: 12px; }}
.handoff-output textarea {{ width: 100%; min-height: 148px; border: 0; resize: vertical; padding: 10px; background: #fff; color: var(--ink); font: 12px/1.45 ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace; }}
@media (max-width: 980px) {{
  main {{ grid-template-columns: 1fr; }}
  .asset-list {{ grid-template-columns: repeat(auto-fill, minmax(52px, 1fr)); }}
}}
</style>
</head>
<body>
<main>
  <section class="hero">
    <div class="preview" id="previewFrame">
      <button class="reject-active" type="button" id="rejectActive" aria-label="Reject selected image">×</button>
      <img id="previewImage" src="{escape(str(first_image), quote=True)}" alt="">
    </div>
    <div class="asset-list" id="assetList">{"".join(cards)}</div>
  </section>
  <section>
    <div class="panel">
      <div class="section">
        <h3>Create More Variations</h3>
        <div class="control-row">
          <label for="slotSelect">Change</label>
          <select id="slotSelect"></select>
        </div>
        <div class="option-menu" id="optionMenu"></div>
      </div>
      <div class="section">
        <h3>Selected Variations</h3>
        <div class="selected-tray" id="selectedTray"></div>
        <div class="composer-actions">
          <button class="primary" type="button" id="buildBatch">Remix</button>
          <button type="button" id="clearBatch">Clear</button>
        </div>
        <div class="handoff-status" id="handoffStatus" role="status">Click recommendations, then build a request to send back into the conversation.</div>
        <div class="handoff-output" id="handoffOutput" hidden>
          <div class="handoff-head">
            <strong id="handoffTitle">Remix request ready</strong>
            <button type="button" id="copyRequest">Copy request</button>
          </div>
          <details id="requestDetails">
            <summary>View request</summary>
            <textarea id="handoffText" readonly></textarea>
          </details>
        </div>
      </div>
    </div>
  </section>
</main>
<script type="application/json" id="variationData">{assets_json}</script>
<script>
const data = JSON.parse(document.getElementById("variationData").textContent);
const assets = data.assets || [];
const byId = new Map(assets.map((asset) => [asset.asset_id, asset]));
const preview = document.getElementById("previewImage");
const previewFrame = document.getElementById("previewFrame");
const slotSelect = document.getElementById("slotSelect");
const optionMenu = document.getElementById("optionMenu");
const selectedTray = document.getElementById("selectedTray");
const handoffStatus = document.getElementById("handoffStatus");
const handoffOutput = document.getElementById("handoffOutput");
const handoffTitle = document.getElementById("handoffTitle");
const handoffText = document.getElementById("handoffText");
const requestDetails = document.getElementById("requestDetails");
const copyRequestButton = document.getElementById("copyRequest");
const optionLibrary = data.option_library || {{}};
const maxRemixRecipes = Number(data.meta?.max_remix_recipes || 24);
const remixRequestFilename = "variation-remix-request.json";
let activeAsset = assets[0] || null;
let selectedVariations = [];
let batchItems = [];
let rejectedAssets = new Set();
let saveTimer = null;

function setHandoffStatus(message) {{
  handoffStatus.textContent = message || "";
}}

function hasLocalSaveBridge() {{
  return window.location.protocol === "http:" || window.location.protocol === "https:";
}}

async function saveRemixRequest(payload) {{
  if (!hasLocalSaveBridge()) return false;
  const response = await fetch("/api/remix-request", {{
    method: "POST",
    headers: {{
      "content-type": "application/json",
      "x-bv-run-token": window.VARIATION_LAB_RUN_TOKEN || ""
    }},
    body: JSON.stringify(payload)
  }});
  return response.ok;
}}

function draftRemixRequestPayload() {{
  const recipes = selectedVariations.length ? buildRemixRecipes(selectedVariations) : [];
  const items = selectedVariations.length ? remixItemsFromRecipes(recipes) : [];
  return buildRemixBatchPayload(
    {{
      type: "autosave",
      label: "Saved selections",
      action: "save_selected_variations"
    }},
    items,
    selectedVariations.length ? "draft" : "empty"
  );
}}

function scheduleRemixRequestSave() {{
  if (saveTimer) clearTimeout(saveTimer);
  saveTimer = setTimeout(async () => {{
    try {{
      const saved = await saveRemixRequest(draftRemixRequestPayload());
      if (saved && selectedVariations.length) {{
        setHandoffStatus(`Saved selections to ${{remixRequestFilename}}. Send any follow-up and Codex can continue from them.`);
      }}
    }} catch (_error) {{
      // Keep the local lab usable even if it was opened as file:// or the server stopped.
    }}
  }}, 350);
}}

function notifyHostHeight() {{
  if (window.openai && typeof window.openai.notifyResize === "function") {{
    window.openai.notifyResize();
  }}
  if (window.openai && typeof window.openai.notifyIntrinsicHeight === "function") {{
    window.openai.notifyIntrinsicHeight();
  }}
}}

function actionLabel(value) {{
  return String(value || "")
    .replace(/-/g, " ")
    .replace(/\\b\\w/g, (match) => match.toUpperCase());
}}

function activeSlot() {{
  if (!activeAsset) return null;
  return (activeAsset.slots || []).find((slot) => slot.id === slotSelect.value) || (activeAsset.slots || [])[0] || null;
}}

function slotLabel(slot) {{
  return (slot?.label || actionLabel(slot?.id || "")).replace(/\\s*\\/\\s*/g, " / ");
}}

function syncReviewState() {{
  document.querySelectorAll(".asset-tile").forEach((tile) => {{
    const id = tile.dataset.assetId;
    tile.classList.toggle("selected", Boolean(activeAsset && id === activeAsset.asset_id));
    tile.classList.toggle("rejected", rejectedAssets.has(id));
  }});
  previewFrame.classList.toggle("rejected", Boolean(activeAsset && rejectedAssets.has(activeAsset.asset_id)));
}}

function nextReviewAsset(afterId) {{
  if (!assets.length) return null;
  const start = Math.max(0, assets.findIndex((asset) => asset.asset_id === afterId));
  for (let offset = 1; offset <= assets.length; offset += 1) {{
    const candidate = assets[(start + offset) % assets.length];
    if (!rejectedAssets.has(candidate.asset_id)) return candidate;
  }}
  return byId.get(afterId) || assets[0] || null;
}}

function rejectAsset(assetId) {{
  if (!assetId) return;
  rejectedAssets.add(assetId);
  if (activeAsset && activeAsset.asset_id === assetId) {{
    renderAsset(nextReviewAsset(assetId));
  }} else {{
    syncReviewState();
  }}
  scheduleRemixRequestSave();
}}

function renderedLabels() {{
  return new Set((data.assets || []).map((asset) => String(asset.label || "").toLowerCase()));
}}

function availableOptions(slot) {{
  if (!slot) return [];
  const options = optionLibrary[slot.id] || [];
  const rendered = renderedLabels();
  if (slot.id !== "style") return options;
  return options.filter((option) => !rendered.has(String(option.label || "").toLowerCase()));
}}

function variationKey(asset, slot, option) {{
  return [asset?.asset_id, slot?.id, option?.id].join("::");
}}

function variationRecord(asset, slot, option) {{
  return {{
    key: variationKey(asset, slot, option),
    assetId: asset.asset_id,
    assetLabel: asset.label,
    image: asset.image,
    slotId: slot.id,
    slotLabel: slotLabel(slot),
    slotPromptHint: slot.promptHint || "",
    option
  }};
}}

function isVariationSelected(asset, slot, option) {{
  const key = variationKey(asset, slot, option);
  return selectedVariations.some((item) => item.key === key);
}}

function toggleVariation(slot, option) {{
  if (!activeAsset || !slot || !option) return;
  const record = variationRecord(activeAsset, slot, option);
  if (selectedVariations.some((item) => item.key === record.key)) {{
    selectedVariations = selectedVariations.filter((item) => item.key !== record.key);
  }} else {{
    selectedVariations.push(record);
  }}
  renderSelectedVariations();
  renderOptions();
  scheduleRemixRequestSave();
}}

function removeVariation(key) {{
  selectedVariations = selectedVariations.filter((item) => item.key !== key);
  renderSelectedVariations();
  renderOptions();
  scheduleRemixRequestSave();
}}

function renderSlotSelect(asset) {{
  slotSelect.innerHTML = "";
  for (const slot of asset.slots || []) {{
    const option = document.createElement("option");
    option.value = slot.id;
    option.textContent = slotLabel(slot);
    slotSelect.append(option);
  }}
  const preferred = (asset.slots || []).find((slot) => slot.id === "style") || (asset.slots || [])[0];
  if (preferred) slotSelect.value = preferred.id;
  renderOptions();
}}

function renderOptions() {{
  const slot = activeSlot();
  optionMenu.innerHTML = "";
  const options = availableOptions(slot);
  if (!slot || !options.length) {{
    const empty = document.createElement("div");
    empty.className = "empty";
    empty.textContent = "No recommendations for this slot yet.";
    optionMenu.append(empty);
    return;
  }}
  for (const option of options) {{
    const selected = isVariationSelected(activeAsset, slot, option);
    const row = document.createElement("div");
    row.className = "option";
    row.classList.toggle("selected", selected);
    row.setAttribute("role", "button");
    row.tabIndex = 0;
    row.addEventListener("click", (event) => {{
      if (event.target.closest("button")) return;
      toggleVariation(slot, option);
    }});
    row.addEventListener("keydown", (event) => {{
      if (event.key !== "Enter" && event.key !== " ") return;
      event.preventDefault();
      toggleVariation(slot, option);
    }});
    const plus = document.createElement("button");
    plus.className = "plus";
    plus.type = "button";
    plus.textContent = selected ? "✓" : "+";
    plus.title = selected ? "Variation selected" : "Add variation";
    plus.addEventListener("click", (event) => {{
      event.stopPropagation();
      toggleVariation(slot, option);
    }});
    const copy = document.createElement("div");
    const strong = document.createElement("strong");
    strong.textContent = option.label || option.id;
    const desc = document.createElement("p");
    desc.textContent = option.description || option.promptHint || "";
    copy.append(strong, desc);
    row.append(plus, copy);
    optionMenu.append(row);
  }}
}}

function renderSelectedVariations() {{
  selectedTray.innerHTML = "";
  if (!selectedVariations.length) {{
    const empty = document.createElement("div");
    empty.className = "empty";
    empty.textContent = "Click recommendations to queue remix ideas.";
    selectedTray.append(empty);
    return;
  }}
  for (const item of selectedVariations) {{
    const chip = document.createElement("span");
    chip.className = "chip";
    const label = document.createElement("span");
    label.textContent = `${{item.slotLabel}}: ${{item.option.label}}`;
    const remove = document.createElement("button");
    remove.type = "button";
    remove.textContent = "x";
    remove.addEventListener("click", () => removeVariation(item.key));
    chip.append(label, remove);
    selectedTray.append(chip);
  }}
  const recipes = buildRemixRecipes(selectedVariations);
  const suffix = recipes.truncated ? ` Showing first ${{recipes.length}}.` : "";
  setHandoffStatus(`${{selectedVariations.length}} change${{selectedVariations.length === 1 ? "" : "s"}} selected. Remix will create ${{recipes.length}} image${{recipes.length === 1 ? "" : "s"}}.${{suffix}}`);
}}

function lockSummary(asset) {{
  return (asset.locks || []).map((lock) => lock.label || lock.id).filter(Boolean).join(", ");
}}

function groupVariationsByAsset(variations) {{
  const grouped = new Map();
  for (const item of variations) {{
    const asset = byId.get(item.assetId) || activeAsset;
    if (!asset) continue;
    if (!grouped.has(item.assetId)) grouped.set(item.assetId, {{ asset, slots: new Map() }});
    const group = grouped.get(item.assetId);
    if (!group.slots.has(item.slotId)) group.slots.set(item.slotId, []);
    group.slots.get(item.slotId).push(item);
  }}
  return Array.from(grouped.values());
}}

function cartesian(lists) {{
  return lists.reduce(
    (acc, list) => acc.flatMap((prefix) => list.map((item) => [...prefix, item])),
    [[]]
  );
}}

function buildRemixRecipes(variations) {{
  const recipes = [];
  let total = 0;
  for (const group of groupVariationsByAsset(variations)) {{
    const slotLists = Array.from(group.slots.values());
    const combos = cartesian(slotLists);
    total += combos.length;
    for (const changes of combos) {{
      if (recipes.length < maxRemixRecipes) recipes.push({{ asset: group.asset, changes }});
    }}
  }}
  recipes.total = total;
  recipes.truncated = total > recipes.length;
  return recipes;
}}

function buildPromptFromRecipe(recipe) {{
  const asset = recipe.asset;
  const sourcePrompt = asset?.source?.prompt || "";
  const changes = recipe.changes || [];
  const changeText = changes.map((item) => `${{item.slotLabel}}: ${{item.option.label}}`).join("; ");
  const hints = changes
    .map((item) => item.option.promptHint || item.slotPromptHint || "")
    .filter(Boolean)
    .map((hint) => `- ${{hint}}`)
    .join(" ");
  const parts = [
    `Source asset: ${{asset?.label || changes[0]?.assetLabel || "Selected asset"}}.`,
    `Apply these changes together: ${{changeText}}.`,
    hints,
    `Preserve locks: ${{lockSummary(asset)}}.`
  ].filter(Boolean);
  if (sourcePrompt) parts.push(`Source prompt context: ${{sourcePrompt}}`);
  return parts.join(" ");
}}

function buildRemixBatchPayload(widgetAction = null, items = batchItems, remixStatus = "ready") {{
  return {{
    version: 1,
    source: "variation-lab",
    status: remixStatus,
    triggered_by: widgetAction ? "widget_action" : "manual",
    widget_action: widgetAction,
    title: data.meta?.title || "Variation Lab",
    source_page: window.location.href,
    source_asset: activeAsset?.asset_id || null,
    combination_strategy: "cartesian_by_asset_across_slots",
    max_remix_recipes: maxRemixRecipes,
    update_target: {{
      action: "prepend_generated_assets_to_same_variation_lab",
      source_page: window.location.href
    }},
    rejected_assets: Array.from(rejectedAssets),
    created_at: new Date().toISOString(),
    items
  }};
}}

function buildConversationPrompt(payload) {{
  const lines = [
    "Create these Variation Lab remixes from my selected options.",
    "Generate one new image for each remix item, then prepend the generated images to the same Variation Lab so the set keeps compiling.",
    "",
    `Source: ${{payload.title}}`,
    payload.source_page ? `Source page: ${{payload.source_page}}` : "",
    "",
    "Selections:",
    ...payload.items.map((item, index) => `${{index + 1}}. ${{item.asset_label}} — ${{item.instruction}}`)
  ].filter(Boolean);
  return `${{lines.join("\\n")}}\\n\\nRemix batch JSON:\\n\\`\\`\\`json\\n${{JSON.stringify(payload, null, 2)}}\\n\\`\\`\\``;
}}

async function writeClipboard(text) {{
  if (navigator.clipboard && typeof navigator.clipboard.writeText === "function") {{
    await navigator.clipboard.writeText(text);
    return true;
  }}
  return false;
}}

async function sendConversationRequest(payload, prompt) {{
  const openai = window.openai || {{}};
  if (typeof openai.uploadFile === "function" && typeof openai.sendFollowUpMessage === "function") {{
    try {{
      const file = new File(
        [JSON.stringify(payload, null, 2)],
        "variation-remix-batch.json",
        {{ type: "application/json" }}
      );
      const upload = await openai.uploadFile(file);
      const fileId = upload?.fileId || upload?.id || upload?.file_id || "";
      const attachmentLine = fileId
        ? `Attached remix batch JSON file ID: ${{fileId}}`
        : "The remix batch JSON was uploaded by Variation Lab.";
      await openai.sendFollowUpMessage({{ prompt: `${{prompt}}\\n\\n${{attachmentLine}}` }});
      handoffOutput.hidden = true;
      setHandoffStatus("Sent the remix request to the conversation.");
      return;
    }} catch (_error) {{
      // Continue to the local fallback below.
    }}
  }}

  if (typeof openai.sendFollowUpMessage === "function") {{
    try {{
      await openai.sendFollowUpMessage({{ prompt }});
      handoffOutput.hidden = true;
      setHandoffStatus("Sent the remix request to the conversation.");
      return;
    }} catch (_error) {{
      // Continue to the local fallback below.
    }}
  }}

  handoffOutput.hidden = false;
  handoffTitle.textContent = "Remix request ready";
  handoffText.value = prompt;
  requestDetails.open = false;
  notifyHostHeight();

  try {{
    if (await writeClipboard(prompt)) {{
      setHandoffStatus("Copied the remix request. Paste it into chat to render these selections.");
      return;
    }}
  }} catch (_error) {{
    // Clipboard may be blocked for local file previews.
  }}

  setHandoffStatus("Remix request is ready. Use Copy request when you want to paste it into chat.");
}}

function selectedOrActiveVariations() {{
  if (selectedVariations.length) return selectedVariations;
  const slot = activeSlot();
  const options = availableOptions(slot);
  if (!activeAsset || !slot || !options.length) return [];
  return [variationRecord(activeAsset, slot, options[0])];
}}

function remixItemsFromRecipes(recipes) {{
  return recipes.map((recipe, index) => {{
    const asset = recipe.asset;
    const changes = recipe.changes || [];
    const first = changes[0] || {{}};
    const instruction = changes.map((item) => `${{item.slotLabel}} -> ${{item.option.label}}`).join(" + ");
    return {{
      id: `remix-${{String(index + 1).padStart(2, "0")}}`,
      asset_id: asset?.asset_id || first.assetId,
      asset_label: asset?.label || first.assetLabel,
      image: asset?.image || first.image,
      slot: first.slotId || null,
      slot_label: first.slotLabel || null,
      option_id: first.option?.id || null,
      option_label: first.option?.label || null,
      changes: changes.map((item) => ({{
        slot: item.slotId,
        slot_label: item.slotLabel,
        option_id: item.option.id,
        option_label: item.option.label,
        prompt_hint: item.option.promptHint || item.slotPromptHint || ""
      }})),
      instruction,
      prompt: buildPromptFromRecipe(recipe),
      locks: asset?.locks || []
    }};
  }});
}}

async function buildRemixBatch() {{
  const remixVariations = selectedOrActiveVariations();
  if (!remixVariations.length) {{
    setHandoffStatus("Choose a variation to remix first.");
    handoffOutput.hidden = true;
    handoffText.value = "";
    notifyHostHeight();
    return;
  }}
  const recipes = buildRemixRecipes(remixVariations);
  batchItems = remixItemsFromRecipes(recipes);
  const payload = buildRemixBatchPayload({{
    type: "handoff_cta",
    label: "Remix",
    action: "send_selected_variations"
  }}, batchItems, "ready");
  const prompt = buildConversationPrompt(payload);
  setHandoffStatus("Preparing remix request...");
  try {{
    await saveRemixRequest(payload);
    await sendConversationRequest(payload, prompt);
  }} catch (error) {{
    handoffOutput.hidden = false;
    handoffTitle.textContent = "Remix request ready";
    handoffText.value = prompt;
    requestDetails.open = false;
    try {{
      if (await writeClipboard(prompt)) {{
        setHandoffStatus("Copied the remix request. Paste it into chat to render these selections.");
      }} else {{
        setHandoffStatus("Remix request is ready. Use Copy request when you want to paste it into chat.");
      }}
    }} catch (_clipboardError) {{
      setHandoffStatus("Remix request is ready. Use Copy request when you want to paste it into chat.");
    }}
    notifyHostHeight();
  }}
}}

function renderAsset(asset) {{
  if (!asset) return;
  activeAsset = asset;
  preview.src = asset.image || "";
  renderSlotSelect(asset);
  syncReviewState();
}}

document.getElementById("assetList").addEventListener("click", (event) => {{
  const rejectButton = event.target.closest(".reject-thumb");
  if (rejectButton) {{
    const tile = rejectButton.closest("[data-asset-id]");
    rejectAsset(tile?.dataset.assetId);
    return;
  }}
  const tile = event.target.closest("[data-asset-id]");
  if (!tile) return;
  renderAsset(byId.get(tile.dataset.assetId));
}});

document.getElementById("rejectActive").addEventListener("click", () => {{
  rejectAsset(activeAsset?.asset_id);
}});

slotSelect.addEventListener("change", renderOptions);
document.getElementById("buildBatch").addEventListener("click", buildRemixBatch);
copyRequestButton.addEventListener("click", async () => {{
  if (!handoffText.value) {{
    setHandoffStatus("Build a remix request first.");
    return;
  }}
  try {{
    if (await writeClipboard(handoffText.value)) {{
      setHandoffStatus("Copied the remix request.");
    }} else {{
      setHandoffStatus("Clipboard is unavailable. Select and copy the request text.");
    }}
  }} catch (_error) {{
    setHandoffStatus("Clipboard is unavailable. Select and copy the request text.");
  }}
}});
document.getElementById("clearBatch").addEventListener("click", () => {{
  selectedVariations = [];
  batchItems = [];
  renderSelectedVariations();
  handoffOutput.hidden = true;
  handoffText.value = "";
  setHandoffStatus("Click recommendations, then build a request to send back into the conversation.");
  scheduleRemixRequestSave();
  notifyHostHeight();
}});

renderSelectedVariations();
renderAsset((data.assets || [])[0]);
</script>
</body>
</html>
"""
    target = out_dir / output_name
    target.write_text(html, encoding="utf-8")
    return target


def json_for_script_tag(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False).replace("<", "\\u003c")


def render_variation_lab_server(
    out_dir: Path,
    html_output: str = "variation-lab.html",
    output_name: str = "server.mjs",
) -> Path:
    server = f"""import {{ randomBytes }} from "node:crypto";
import {{ createReadStream }} from "node:fs";
import fs from "node:fs/promises";
import http from "node:http";
import path from "node:path";
import {{ fileURLToPath }} from "node:url";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const requestedPort = Number(process.env.PORT || 8799);
const maxPortAttempts = Number(process.env.CREATIVE_PRODUCTION_PORT_ATTEMPTS || 20);
let port = requestedPort;
const runToken = process.env.BV_RUN_TOKEN || randomBytes(24).toString("base64url");
const remixRequestPath = path.join(__dirname, "variation-remix-request.json");
const htmlFile = {json.dumps(html_output)};

const mimeTypes = new Map([
  [".html", "text/html; charset=utf-8"],
  [".css", "text/css; charset=utf-8"],
  [".js", "text/javascript; charset=utf-8"],
  [".json", "application/json; charset=utf-8"],
  [".png", "image/png"],
  [".jpg", "image/jpeg"],
  [".jpeg", "image/jpeg"],
  [".webp", "image/webp"],
  [".svg", "image/svg+xml; charset=utf-8"],
]);

function corsHeaders(req) {{
  const origin = req.headers.origin;
  const allowedOrigins = new Set([
    `http://127.0.0.1:${{port}}`,
    `http://localhost:${{port}}`,
  ]);
  if (!origin || !allowedOrigins.has(origin)) return {{}};
  return {{
    "Access-Control-Allow-Origin": origin,
    "Access-Control-Allow-Headers": "content-type,x-bv-run-token",
    "Access-Control-Allow-Methods": "GET,POST,OPTIONS",
    "Vary": "Origin",
  }};
}}

function hostIsAllowed(req) {{
  const host = req.headers.host;
  return !host || host === `127.0.0.1:${{port}}` || host === `localhost:${{port}}`;
}}

function originIsAllowed(req) {{
  const origin = req.headers.origin;
  return !origin || origin === `http://127.0.0.1:${{port}}` || origin === `http://localhost:${{port}}`;
}}

function send(req, res, status, body, contentType = "text/plain; charset=utf-8") {{
  res.writeHead(status, {{
    "Content-Type": contentType,
    ...corsHeaders(req),
  }});
  res.end(body);
}}

function sendJson(req, res, status, body) {{
  send(req, res, status, JSON.stringify(body), "application/json; charset=utf-8");
}}

function rejectUnsafeRequest(req, res) {{
  if (!hostIsAllowed(req) || !originIsAllowed(req)) {{
    sendJson(req, res, 403, {{ error: "Request origin is not allowed." }});
    return true;
  }}
  return false;
}}

function requireRunToken(req, res) {{
  if (req.headers["x-bv-run-token"] !== runToken) {{
    sendJson(req, res, 403, {{ error: "Missing or invalid Creative Production run token." }});
    return false;
  }}
  return true;
}}

async function readJson(req) {{
  let body = "";
  for await (const chunk of req) body += chunk;
  return JSON.parse(body || "{{}}");
}}

async function fileExists(filePath) {{
  try {{
    await fs.access(filePath);
    return true;
  }} catch {{
    return false;
  }}
}}

function injectRunToken(html) {{
  const script = `<script>window.VARIATION_LAB_RUN_TOKEN=${{JSON.stringify(runToken)}};</script>`;
  if (html.includes("</head>")) return html.replace("</head>", `  ${{script}}\\n</head>`);
  return `${{script}}\\n${{html}}`;
}}

async function serveFile(req, res, pathname) {{
  const normalized = pathname === "/" ? `/${{htmlFile}}` : pathname;
  const safePath = path.normalize(normalized).replace(/^(\\.\\.[/\\\\])+/, "");
  const filePath = path.join(__dirname, safePath);

  if (!filePath.startsWith(__dirname) || !(await fileExists(filePath))) {{
    send(req, res, 404, "Not found");
    return;
  }}

  const ext = path.extname(filePath);
  if (ext === ".html") {{
    send(req, res, 200, injectRunToken(await fs.readFile(filePath, "utf8")), mimeTypes.get(ext));
    return;
  }}

  res.writeHead(200, {{
    "Content-Type": mimeTypes.get(ext) || "application/octet-stream",
    "Cache-Control": "no-cache",
    ...corsHeaders(req),
  }});
  createReadStream(filePath).pipe(res);
}}

const server = http.createServer(async (req, res) => {{
  try {{
    if (req.method === "OPTIONS") {{
      if (rejectUnsafeRequest(req, res)) return;
      sendJson(req, res, 204, {{}});
      return;
    }}

    const url = new URL(req.url, `http://127.0.0.1:${{port}}`);
    if (rejectUnsafeRequest(req, res)) return;

    if (req.method === "GET" && url.pathname === "/api/session") {{
      sendJson(req, res, 200, {{ runToken, remixRequestPath }});
      return;
    }}

    if (req.method === "GET" && url.pathname === "/api/remix-request") {{
      if (!(await fileExists(remixRequestPath))) {{
        sendJson(req, res, 404, {{ error: "No saved remix request yet." }});
        return;
      }}
      send(req, res, 200, await fs.readFile(remixRequestPath, "utf8"), "application/json; charset=utf-8");
      return;
    }}

    if (req.method === "POST" && url.pathname === "/api/remix-request") {{
      if (!requireRunToken(req, res)) return;
      const payload = await readJson(req);
      const saved = {{
        ...payload,
        saved_at: new Date().toISOString(),
        saved_by: "variation-lab-server",
      }};
      await fs.writeFile(remixRequestPath, `${{JSON.stringify(saved, null, 2)}}\\n`, "utf8");
      sendJson(req, res, 200, {{ ok: true, path: remixRequestPath, status: saved.status || "draft" }});
      return;
    }}

    if (req.method === "GET") {{
      await serveFile(req, res, url.pathname);
      return;
    }}

    send(req, res, 405, "Method not allowed");
  }} catch (error) {{
    sendJson(req, res, 500, {{ error: error.message || "Unknown server error." }});
  }}
}});

function logReady() {{
  console.log(`Variation Lab: http://127.0.0.1:${{port}}`);
  console.log(`Saved remix request: ${{remixRequestPath}}`);
}}

function listenWithFallback(nextPort = requestedPort, remaining = maxPortAttempts) {{
  port = nextPort;
  server.once("error", (error) => {{
    if (error.code === "EADDRINUSE" && !process.env.PORT && remaining > 0) {{
      console.log(`Port ${{port}} is occupied; trying ${{port + 1}}.`);
      listenWithFallback(port + 1, remaining - 1);
      return;
    }}
    console.error(error);
    process.exitCode = 1;
  }});
  server.listen(port, "127.0.0.1", logReady);
}}

listenWithFallback();
"""
    target = out_dir / output_name
    target.write_text(server, encoding="utf-8")
    return target


def _read_review_items(path: Path) -> list[dict[str, Any]]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(payload, list):
        return payload
    if isinstance(payload, dict) and isinstance(payload.get("assets"), list):
        return payload["assets"]
    raise ValueError("Review manifest must be a list or an object with an assets array.")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Build a universal Creative Production Variation Lab."
    )
    parser.add_argument("--out-dir", required=True, type=Path)
    parser.add_argument("--review-manifest", required=True, type=Path)
    parser.add_argument("--title", default="Variation Lab")
    parser.add_argument("--summary")
    parser.add_argument("--asset-type", default="generic_visual")
    parser.add_argument("--source-skill")
    parser.add_argument("--manifest-output", default="variation-manifest.json")
    parser.add_argument("--html-output", default="variation-lab.html")
    args = parser.parse_args()

    args.out_dir.mkdir(parents=True, exist_ok=True)
    review_items = _read_review_items(args.review_manifest)
    manifest = build_variation_manifest(
        review_items,
        title=args.title,
        summary=args.summary,
        asset_type=args.asset_type,
        source_skill=args.source_skill,
    )
    html_path = render_variation_lab_html(args.out_dir, manifest, args.html_output)
    manifest_path = args.out_dir / args.manifest_output
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    server_path = render_variation_lab_server(args.out_dir, args.html_output)
    print(
        json.dumps(
            {
                "variation_manifest": str(manifest_path.resolve()),
                "variation_lab": str(html_path.resolve()),
                "variation_server": str(server_path.resolve()),
                "saved_remix_request": str(
                    (args.out_dir / "variation-remix-request.json").resolve()
                ),
                "assets": len(manifest["assets"]),
                "asset_type": normalize_asset_type(args.asset_type),
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
