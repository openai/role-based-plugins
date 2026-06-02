#!/usr/bin/env python3
"""Initialize local Sales user-context and onboarding-state files."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from state_paths import STATE_DIR_HELP, resolve_state_dir

SKILL_ROOT = Path(__file__).resolve().parents[1]
USER_CONTEXT_TEMPLATE = SKILL_ROOT / "plugin-author-config/user-context-config.md"
AUTOMATION_CONFIG = SKILL_ROOT / "plugin-author-config/automation-config.md"
ONBOARDING_STATE_TEMPLATE = SKILL_ROOT / "references/onboarding-state-template.json"

USER_CONTEXT_NOTE = """<!--
Sales user-context scaffold. This file is user-editable.
Unresolved `status: not provided` entries are setup prompts, not saved facts.
Agents may create or revise categories when helpful. Saved links, docs, and
user-provided context should include Date Added, Useful Context, and Future Use
when available.
-->

"""

DEFAULT_CATEGORIES_MARKER = "## Default Categories"
SAVED_CONTEXT_HEADING = "## Saved Links And Context"
SAVED_CONTEXT_PLACEHOLDER = "status: not provided"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Create missing Sales local state files from bundled config/templates. "
            "Existing files are preserved unless --overwrite is passed."
        )
    )
    parser.add_argument(
        "--codex-home",
        type=Path,
        default=None,
        help="Codex home directory. Defaults to $CODEX_HOME or ~/.codex.",
    )
    parser.add_argument(
        "--state-dir",
        type=Path,
        default=None,
        help=STATE_DIR_HELP,
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Overwrite existing user-context.md and onboarding-state.json.",
    )
    return parser.parse_args()


def validate_json(path: Path) -> None:
    with path.open("r", encoding="utf-8") as handle:
        json.load(handle)


def build_user_context_scaffold() -> str:
    template_text = USER_CONTEXT_TEMPLATE.read_text(encoding="utf-8")
    if DEFAULT_CATEGORIES_MARKER not in template_text:
        raise ValueError("user-context-config.md must include a Default Categories section")
    category_text = template_text.split(DEFAULT_CATEGORIES_MARKER, 1)[1].strip()
    sections = [
        section.strip() for section in re.split(r"(?m)(?=^# .+$)", category_text) if section.strip()
    ]
    if not sections:
        raise ValueError("user-context-config.md must define at least one category")

    rendered_sections: list[str] = []
    for section in sections:
        if not section.startswith("# "):
            raise ValueError("user-context-config.md category entries must start with H1 headings")
        if "- Priority:" in section:
            raise ValueError("user-context-config.md must not define Priority fields")
        if "## User Resources" in section or SAVED_CONTEXT_HEADING in section:
            raise ValueError(
                "user-context-config.md must not include saved-context subsections; "
                "the initializer adds them"
            )
        rendered_sections.append(
            f"{section.rstrip()}\n\n{SAVED_CONTEXT_HEADING}\n\n{SAVED_CONTEXT_PLACEHOLDER}"
        )

    return "\n\n".join(rendered_sections) + "\n"


def load_automation_config() -> dict[str, dict[str, object]]:
    text = AUTOMATION_CONFIG.read_text(encoding="utf-8")
    if "## Default Automations" in text:
        text = text.split("## Default Automations", 1)[1]
    if "## Later Journey Automations" in text:
        text = text.split("## Later Journey Automations", 1)[0]
    matches = list(re.finditer(r"(?m)^`([a-z0-9_]+)`\s*$", text))
    automations: dict[str, dict[str, object]] = {}
    for index, match in enumerate(matches):
        automation_id = match.group(1)
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        block = text[match.end() : end]
        metadata: dict[str, object] = {}
        for field, key in (
            ("Name", "name"),
            ("Frequency", "frequency"),
            ("Instructions", "instructions"),
        ):
            field_match = re.search(rf"(?m)^- {re.escape(field)}:\s*(.+?)\s*$", block)
            if not field_match:
                raise ValueError(
                    f"automation-config.md entry {automation_id} missing field: {field}"
                )
            value = field_match.group(1).strip()
            if key in {"name", "target_thread_title", "frequency"}:
                value = value.rstrip(".")
            metadata[key] = value
        metadata["target_thread_title"] = metadata["name"]
        automations[automation_id] = metadata
    if not automations:
        raise ValueError("automation-config.md must define at least one automation entry")
    return automations


def build_automation_state_entry(metadata: dict[str, object]) -> dict[str, object]:
    return {
        "status": None,
        "canonical_id": None,
        "target_thread_id": None,
        "target_thread_title": metadata["target_thread_title"],
        "target_thread_status": None,
        "last_installed": None,
        "frequency": metadata["frequency"],
        "name": metadata["name"],
        "instructions": metadata["instructions"],
    }


def build_onboarding_state(automations: dict[str, dict[str, object]]) -> dict[str, object]:
    with ONBOARDING_STATE_TEMPLATE.open("r", encoding="utf-8") as handle:
        state = json.load(handle)
    state["automations"] = {
        automation_id: build_automation_state_entry(metadata)
        for automation_id, metadata in automations.items()
    }
    return state


def write_text_if_needed(path: Path, text: str, overwrite: bool) -> str:
    existed = path.exists()
    if existed and not overwrite:
        return "preserved"
    path.write_text(text, encoding="utf-8")
    return "overwritten" if existed else "created"


def main() -> int:
    args = parse_args()

    state_dir = resolve_state_dir(args.codex_home, args.state_dir)

    missing_templates = [
        str(path.relative_to(SKILL_ROOT))
        for path in (
            USER_CONTEXT_TEMPLATE,
            AUTOMATION_CONFIG,
            ONBOARDING_STATE_TEMPLATE,
        )
        if not path.exists()
    ]
    if missing_templates:
        print("Missing Sales bundled state source(s):", file=sys.stderr)
        for missing in missing_templates:
            print(f"- {missing}", file=sys.stderr)
        return 1

    try:
        user_context_scaffold = build_user_context_scaffold()
        automations = load_automation_config()
        validate_json(ONBOARDING_STATE_TEMPLATE)
    except (json.JSONDecodeError, ValueError) as exc:
        print(
            f"Invalid Sales bundled state source: {exc}",
            file=sys.stderr,
        )
        return 1

    state_dir.mkdir(parents=True, exist_ok=True)

    user_context_path = state_dir / "user-context.md"
    onboarding_state_path = state_dir / "onboarding-state.json"

    user_context_text = USER_CONTEXT_NOTE + user_context_scaffold
    user_context_result = write_text_if_needed(
        user_context_path,
        user_context_text,
        args.overwrite,
    )

    onboarding_state_text = json.dumps(build_onboarding_state(automations), indent=2) + "\n"
    onboarding_state_result = write_text_if_needed(
        onboarding_state_path,
        onboarding_state_text,
        args.overwrite,
    )

    try:
        validate_json(onboarding_state_path)
    except json.JSONDecodeError as exc:
        print(
            f"Invalid written Sales state JSON: {exc}",
            file=sys.stderr,
        )
        return 1

    print(f"Sales state directory: {state_dir}")
    print(f"user-context.md: {user_context_result}")
    print(f"onboarding-state.json: {onboarding_state_result}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
