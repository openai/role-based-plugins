#!/usr/bin/env python3
"""Initialize local Data Analytics source-routing and onboarding state files."""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

SKILL_ROOT = Path(__file__).resolve().parents[1]
USER_CONTEXT_TEMPLATE = SKILL_ROOT / "plugin-author-config/user-context-config.md"
ONBOARDING_STATE_TEMPLATE = SKILL_ROOT / "references/onboarding-state-template.json"

USER_CONTEXT_NOTE = """<!--
Data Analytics user-context scaffold. This file is user-editable.
Store only durable source-routing choices explicitly selected for future use
plus semantic-layer registry entries. Do not store general memory, output
preferences, onboarding state, or connector readiness here.
-->

"""

DEFAULT_USER_CONTEXT_MARKER = "## Default User Context"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Create missing Data Analytics local state files from bundled templates. "
            "Existing files are preserved unless --overwrite is passed."
        )
    )
    parser.add_argument("--codex-home", type=Path, default=None)
    parser.add_argument("--state-dir", type=Path, default=None)
    parser.add_argument("--overwrite", action="store_true")
    return parser.parse_args()


def default_codex_home() -> Path:
    env_home = os.environ.get("CODEX_HOME")
    if env_home:
        return Path(env_home).expanduser()
    return Path.home() / ".codex"


def validate_json(path: Path) -> None:
    with path.open("r", encoding="utf-8") as handle:
        json.load(handle)


def build_user_context_scaffold() -> str:
    template_text = USER_CONTEXT_TEMPLATE.read_text(encoding="utf-8")
    if DEFAULT_USER_CONTEXT_MARKER not in template_text:
        raise ValueError("user-context-config.md must include a Default User Context section")
    user_context_text = template_text.rsplit(DEFAULT_USER_CONTEXT_MARKER, 1)[1].strip()
    if not user_context_text.startswith("# Data Analytics Source Routing Preferences"):
        raise ValueError(
            "user-context-config.md default user context must start with source routing"
        )
    if "# Semantic Layers" not in user_context_text:
        raise ValueError("user-context-config.md default user context must include Semantic Layers")
    if "## Saved Links And Context" in user_context_text:
        raise ValueError("user-context-config.md must not include saved-context sections")
    return user_context_text + "\n"


def write_text_if_needed(path: Path, text: str, overwrite: bool) -> str:
    existed = path.exists()
    if existed and not overwrite:
        return "preserved"
    path.write_text(text, encoding="utf-8")
    return "overwritten" if existed else "created"


def main() -> int:
    args = parse_args()
    codex_home = args.codex_home.expanduser() if args.codex_home else default_codex_home()
    state_dir = (
        args.state_dir.expanduser()
        if args.state_dir
        else codex_home / "state/plugins/data-analytics"
    )

    missing_templates = [
        str(path.relative_to(SKILL_ROOT))
        for path in (USER_CONTEXT_TEMPLATE, ONBOARDING_STATE_TEMPLATE)
        if not path.exists()
    ]
    if missing_templates:
        print("Missing Data Analytics bundled state source(s):", file=sys.stderr)
        for missing in missing_templates:
            print(f"- {missing}", file=sys.stderr)
        return 1

    try:
        user_context_scaffold = build_user_context_scaffold()
        validate_json(ONBOARDING_STATE_TEMPLATE)
    except (json.JSONDecodeError, ValueError) as exc:
        print(f"Invalid Data Analytics bundled state source: {exc}", file=sys.stderr)
        return 1

    state_dir.mkdir(parents=True, exist_ok=True)
    user_context_path = state_dir / "user-context.md"
    onboarding_state_path = state_dir / "onboarding-state.json"

    user_context_result = write_text_if_needed(
        user_context_path,
        USER_CONTEXT_NOTE + user_context_scaffold,
        args.overwrite,
    )
    onboarding_state = json.loads(ONBOARDING_STATE_TEMPLATE.read_text(encoding="utf-8"))
    onboarding_state_result = write_text_if_needed(
        onboarding_state_path,
        json.dumps(onboarding_state, indent=2) + "\n",
        args.overwrite,
    )
    validate_json(onboarding_state_path)

    print(f"Data Analytics state directory: {state_dir}")
    print(f"user-context.md: {user_context_result}")
    print(f"onboarding-state.json: {onboarding_state_result}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
