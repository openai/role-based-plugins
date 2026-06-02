#!/usr/bin/env python3
"""Build an Ads Explorer run using the Creative Production image-ad library."""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
SKILL_DIR = SCRIPT_DIR.parent
PLUGIN_ROOT = SKILL_DIR.parents[1]
OFFER_SCRIPT = PLUGIN_ROOT / "skills" / "offer-explorer" / "scripts" / "build_offer_explorer.py"
AD_LIBRARY = (
    PLUGIN_ROOT / "assets" / "image-ad-library" / "packs" / "diverse-image-ad-archetypes.json"
)


def main() -> int:
    parser = argparse.ArgumentParser(description="Build a Creative Production Ads Explorer run.")
    parser.add_argument("--ad-name", "--offer-name", dest="ad_name", required=True)
    parser.add_argument("--ad-brief", "--offer-brief", dest="ad_brief")
    parser.add_argument("--ad-brief-file", "--offer-brief-file", dest="ad_brief_file")
    parser.add_argument(
        "--subject-kind",
        choices=["product", "service", "venue", "experience"],
        default="product",
    )
    parser.add_argument("--out-dir")
    parser.add_argument(
        "--reference-image", help="Optional source image to mention in job context."
    )
    parser.add_argument("--generate", action="store_true")
    parser.add_argument("--review-only", action="store_true")
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--quality", default="medium")
    parser.add_argument("--codex-exec-runner", type=Path)
    parser.add_argument("--workspace", type=Path)
    parser.add_argument("--codex-bin", default="codex")
    parser.add_argument("--sandbox", default="workspace-write")
    parser.add_argument("--max-concurrency", type=int, default=64)
    parser.add_argument("--max-attempts", type=int, default=2)
    parser.add_argument("--timeout-seconds", type=float, default=600)
    args = parser.parse_args()

    ad_brief = args.ad_brief or ""
    if args.reference_image:
        reference_image = Path(args.reference_image).expanduser().resolve()
        if not reference_image.exists():
            raise SystemExit(f"Reference image not found: {reference_image}")
        ad_brief = (
            f"{ad_brief}\n\nSource image reference: {reference_image}. Preserve visible subject "
            "identity, silhouette, proportions, materials, colors, labels, logos, markings, and category."
        ).strip()

    cmd = [
        sys.executable,
        str(OFFER_SCRIPT),
        "--offer-name",
        args.ad_name,
        "--subject-kind",
        args.subject_kind,
        "--expansion-map",
        str(AD_LIBRARY),
        "--pack",
        "diverse-image-ad-archetypes",
        "--scale",
        "family",
        "--quality",
        args.quality,
        "--max-concurrency",
        str(args.max_concurrency),
        "--max-attempts",
        str(args.max_attempts),
        "--timeout-seconds",
        str(args.timeout_seconds),
        "--codex-bin",
        args.codex_bin,
        "--sandbox",
        args.sandbox,
    ]
    if args.codex_exec_runner:
        cmd.extend(["--codex-exec-runner", str(args.codex_exec_runner)])
    if args.workspace:
        cmd.extend(["--workspace", str(args.workspace)])
    if ad_brief:
        cmd.extend(["--offer-brief", ad_brief])
    if args.ad_brief_file:
        cmd.extend(["--offer-brief-file", args.ad_brief_file])
    if args.out_dir:
        cmd.extend(["--out-dir", args.out_dir])
    if args.generate:
        cmd.append("--generate")
    if args.review_only:
        cmd.append("--review-only")
    if args.force:
        cmd.append("--force")

    return subprocess.run(cmd, check=False).returncode


if __name__ == "__main__":
    raise SystemExit(main())
