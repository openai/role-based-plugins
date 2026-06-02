#!/usr/bin/env python3
"""Validate persisted Sales automation setup against onboarding requirements."""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import tomllib
from pathlib import Path
from typing import Any

MARKETPLACE_ID = "role-based-plugins"
PLUGIN_ID = "sales"
SKILL_ROOT = Path(__file__).resolve().parents[1]
AUTOMATION_CONFIG = SKILL_ROOT / "plugin-author-config/automation-config.md"
DEFAULT_AUTOMATION_IDS = ("weekly_sales_company_research", "daily_sales_tips")
LATER_AUTOMATION_IDS = ("daily_meeting_prep",)
READY_READBACK_STATUSES = {"clean", "confirmed", "read", "read_back", "readback_verified", "ready", "verified"}
READY_TARGET_THREAD_STATUSES = {"pinned", "ready", "verified"}
RESOLVED_SKIP_STATUSES = {
    "declined",
    "deferred",
    "deferred_environment_api_limitations",
    "not_applicable",
    "skipped",
    "skipped_for_now",
}
WORKSPACE_ONLY_TOML_KEYS = {
    "cwds",
    "execution_environment",
    "executionEnvironment",
    "local_environment_config_path",
    "localEnvironmentConfigPath",
}


def default_codex_home() -> Path:
    return Path(os.environ.get("CODEX_HOME", Path.home() / ".codex")).expanduser()


def default_state_dir() -> Path:
    return default_codex_home() / "state/plugins" / MARKETPLACE_ID / PLUGIN_ID


def default_automations_dir() -> Path:
    return default_codex_home() / "automations"


def parse_automation_config() -> dict[str, dict[str, str]]:
    text = AUTOMATION_CONFIG.read_text(encoding="utf-8")
    entries: dict[str, dict[str, str]] = {}
    for match in re.finditer(r"^`([^`]+)`\n\n(?P<body>(?:- .+(?:\n|$))+)", text, re.M):
        automation_id = match.group(1)
        body = match.group("body")
        entry: dict[str, str] = {"id": automation_id}
        for line in body.splitlines():
            field_match = re.match(r"^- ([^:]+):\s*(.*)$", line)
            if field_match:
                key = field_match.group(1).casefold()
                value = field_match.group(2).strip()
                if key in {"name", "frequency"}:
                    value = value.rstrip(".")
                entry[key] = value
        entries[automation_id] = entry
    return entries


def slugify_name(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.casefold()).strip("-")


def expected_rrule(frequency: str) -> str | None:
    if frequency == "weekdays at 9:00 AM local time":
        return "FREQ=WEEKLY;BYDAY=MO,TU,WE,TH,FR;BYHOUR=9;BYMINUTE=0;BYSECOND=0"
    if frequency == "weekly on Mondays at 9:00 AM local time":
        return "FREQ=WEEKLY;BYDAY=MO;BYHOUR=9;BYMINUTE=0;BYSECOND=0"
    return None


def read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    payload = json.loads(path.read_text(encoding="utf-8"))
    return payload if isinstance(payload, dict) else {}


def read_toml(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    return tomllib.loads(path.read_text(encoding="utf-8"))


def state_entry_is_resolved_skip(entry: dict[str, Any]) -> bool:
    return str(entry.get("status") or "").casefold() in RESOLVED_SKIP_STATUSES


def validate_automation(
    *,
    automation_id: str,
    config: dict[str, str],
    onboarding_state: dict[str, Any],
    automations_dir: Path,
    require: bool,
    failures: list[str],
) -> bool:
    state_entry = (
        onboarding_state.get("automations", {}).get(automation_id)
        if isinstance(onboarding_state.get("automations"), dict)
        else None
    )
    if not isinstance(state_entry, dict):
        if require:
            failures.append(f"{automation_id}: missing onboarding-state automations entry")
        return False
    if state_entry_is_resolved_skip(state_entry):
        return False

    name = config.get("name")
    prompt = config.get("instructions")
    frequency = config.get("frequency")
    if not name or not prompt or not frequency:
        failures.append(f"{automation_id}: automation-config.md entry is missing Name, Frequency, or Instructions")
        return False

    canonical_id = state_entry.get("canonical_id") or slugify_name(name)
    automation_toml = automations_dir / str(canonical_id) / "automation.toml"
    persisted = read_toml(automation_toml)
    if not persisted:
        failures.append(f"{automation_id}: missing automation readback at {automation_toml}")
        return False

    expected_schedule = expected_rrule(frequency)
    persisted_target_thread_id = persisted.get("target_thread_id") or persisted.get("targetThreadId")

    checks = {
        "stored kind is heartbeat": str(persisted.get("kind") or "").casefold() == "heartbeat",
        "stored prompt matches automation-config.md Instructions": persisted.get("prompt") == prompt,
        "stored target_thread_id is present": bool(persisted_target_thread_id),
        "stored target_thread_id matches onboarding state": (
            not state_entry.get("target_thread_id")
            or persisted_target_thread_id == state_entry.get("target_thread_id")
        ),
        "onboarding state records canonical_id": bool(state_entry.get("canonical_id")),
        "onboarding state records kind heartbeat": str(state_entry.get("kind") or "").casefold() == "heartbeat",
        "onboarding state records readback": str(state_entry.get("readback_status") or "").casefold()
        in READY_READBACK_STATUSES,
        "onboarding state records target thread id": bool(state_entry.get("target_thread_id")),
        "onboarding state records exact target thread title": state_entry.get("target_thread_title") == name,
        "onboarding state records pinned target thread": (
            str(state_entry.get("target_thread_status") or "").casefold() in READY_TARGET_THREAD_STATUSES
            or state_entry.get("target_thread_pinned") is True
        ),
        "stored automation has no workspace-only fields": not (set(persisted) & WORKSPACE_ONLY_TOML_KEYS),
    }
    if expected_schedule:
        checks["stored rrule matches configured cadence"] = persisted.get("rrule") == expected_schedule
    for label, ok in checks.items():
        if not ok:
            failures.append(f"{automation_id}: {label}")

    if automation_id == "weekly_sales_company_research":
        discovery = onboarding_state.get("initial_resource_discovery")
        if not isinstance(discovery, dict) or not discovery.get("status"):
            failures.append("weekly_sales_company_research: missing initial_resource_discovery kickoff status")
        elif discovery.get("target_thread_id") and discovery.get("target_thread_id") != state_entry.get("target_thread_id"):
            failures.append(
                "weekly_sales_company_research: initial_resource_discovery target_thread_id does not match automation target"
            )

    return True


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--state-dir", type=Path, default=default_state_dir())
    parser.add_argument("--automations-dir", type=Path, default=default_automations_dir())
    parser.add_argument(
        "--require-onboarding-defaults",
        action="store_true",
        help="Require the default Sales onboarding automations to be installed and ready.",
    )
    parser.add_argument(
        "--include-daily-meeting-prep",
        action="store_true",
        help="Also validate the later Sales Daily Meeting Prep automation when it is recorded.",
    )
    args = parser.parse_args()

    failures: list[str] = []
    config = parse_automation_config()
    onboarding_state = read_json(args.state_dir / "onboarding-state.json")
    automation_ids = list(DEFAULT_AUTOMATION_IDS)
    if args.include_daily_meeting_prep or (
        isinstance(onboarding_state.get("automations"), dict)
        and "daily_meeting_prep" in onboarding_state["automations"]
    ):
        automation_ids.extend(LATER_AUTOMATION_IDS)

    validated: list[str] = []
    for automation_id in automation_ids:
        if automation_id not in config:
            failures.append(f"{automation_id}: missing automation-config.md entry")
            continue
        validated_current = validate_automation(
            automation_id=automation_id,
            config=config[automation_id],
            onboarding_state=onboarding_state,
            automations_dir=args.automations_dir,
            require=args.require_onboarding_defaults or automation_id not in LATER_AUTOMATION_IDS,
            failures=failures,
        )
        if validated_current:
            validated.append(automation_id)

    payload = {
        "ok": not failures,
        "validated": validated,
        "failures": failures,
        "state_dir": str(args.state_dir),
        "automations_dir": str(args.automations_dir),
    }
    print(json.dumps(payload, indent=2))
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
