#!/usr/bin/env python3
"""Read Data Analytics local state and emit a deterministic preflight payload."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

PLUGIN_ROOT = Path(__file__).resolve().parents[3]
ONBOARDING_REFERENCE = PLUGIN_ROOT / "skills/user-context/references/onboarding.md"
SOURCE_CATEGORY_CONFIG_REFERENCE = (
    PLUGIN_ROOT / "skills/user-context/plugin-author-config/source-category-config.json"
)
APP_MANIFEST_REFERENCE = PLUGIN_ROOT / ".app.json"
DEFAULT_MAX_CONTEXT_BYTES = 200_000
CORE_CATEGORY_IDS = ("structured_data", "team_communication", "company_docs")
ONBOARDING_RESOLVED_SOURCE_STATUSES = {
    "declined",
    "deferred",
    "deferred_environment_api_limitations",
    "not_applicable",
    "skipped",
    "skipped_for_now",
    "unavailable",
}
SOURCE_CLASSIFIED_STATUSES = {
    "active",
    "needs_confirmation",
    "missing",
    *ONBOARDING_RESOLVED_SOURCE_STATUSES,
}
SOURCE_ACTION_REQUIRED_STATUSES = {"needs_confirmation", "missing"}
CORE_SOURCE_EXPLICIT_FALLBACK_RESOLUTIONS = {
    "user_continued_with_known_gap",
    "user_declined",
    "user_deferred",
    "user_marked_unavailable",
    "user_skipped",
    "user_confirmed_not_applicable",
}
SEMANTIC_SETUP_COMPLETE_STATUSES = {
    "created",
    "refreshed",
    "inspected",
    "repaired",
    "planned",
    "skipped",
    "deferred",
    "unavailable",
    "blocked",
}
SEMANTIC_SETUP_TARGET_STATUSES = {"created", "refreshed", "inspected", "repaired", "planned"}
SEMANTIC_REFRESH_COMPLETE_STATUSES = {
    "accepted",
    "declined",
    "deferred",
    "unavailable",
    "skipped",
    "blocked",
}
HERO_PROMPT_COMPLETE_STATUSES = {"tried", "skipped", "deferred", "completed"}
HERO_SKILLS = ("metric-diagnostics", "product-business-analysis", "kpi-reporting")
SOURCE_ROUTING_PREFERENCES_HEADING = "data analytics source routing preferences"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Read Data Analytics user-context and onboarding-state files and return "
            "context plus workflow control obligations as JSON."
        )
    )
    parser.add_argument("--workflow", default="ordinary")
    parser.add_argument(
        "--request-mode",
        choices=("ordinary_workflow", "direct_onboarding_status", "guided_onboarding_workflow"),
        default="ordinary_workflow",
    )
    parser.add_argument("--codex-home", type=Path, default=None)
    parser.add_argument("--state-dir", type=Path, default=None)
    parser.add_argument("--max-context-bytes", type=int, default=DEFAULT_MAX_CONTEXT_BYTES)
    parser.add_argument("--section", action="append", default=[])
    return parser.parse_args()


def default_codex_home() -> Path:
    env_home = os.environ.get("CODEX_HOME")
    if env_home:
        return Path(env_home).expanduser()
    return Path.home() / ".codex"


def state_dir_from_args(args: argparse.Namespace) -> Path:
    if args.state_dir:
        return args.state_dir.expanduser()
    codex_home = args.codex_home.expanduser() if args.codex_home else default_codex_home()
    return codex_home / "state/plugins/data-analytics"


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def file_mtime(path: Path) -> str | None:
    try:
        return datetime.fromtimestamp(path.stat().st_mtime, tz=timezone.utc).isoformat()
    except OSError:
        return None


def section_bounds(markdown: str) -> dict[str, tuple[int, int, str]]:
    matches = list(re.finditer(r"(?m)^(#{1,6})\s+(.+?)\s*$", markdown))
    bounds: dict[str, tuple[int, int, str]] = {}
    for index, match in enumerate(matches):
        start = match.start()
        level = len(match.group(1))
        end = len(markdown)
        for next_match in matches[index + 1 :]:
            if len(next_match.group(1)) <= level:
                end = next_match.start()
                break
        heading = match.group(2).strip()
        bounds[heading.casefold()] = (start, end, heading)
    return bounds


def extract_sections(markdown: str, requested: list[str]) -> list[dict[str, str]]:
    if not requested:
        return []
    bounds = section_bounds(markdown)
    sections: list[dict[str, str]] = []
    for heading in requested:
        bound = bounds.get(heading.casefold())
        if not bound:
            sections.append({"heading": heading, "status": "missing", "content": ""})
            continue
        start, end, canonical_heading = bound
        sections.append(
            {
                "heading": canonical_heading,
                "status": "present",
                "content": markdown[start:end].strip(),
            }
        )
    return sections


def normalize_source_name(value: Any) -> str:
    return re.sub(r"[^a-z0-9]+", "", str(value or "").casefold())


def parse_source_preference_values(raw_value: str) -> list[str]:
    return [value.strip() for value in raw_value.split(",") if value.strip()]


def extract_saved_source_preferences(
    markdown: str | None,
    source_category_config: dict[str, dict[str, Any]],
) -> dict[str, dict[str, list[str]]]:
    """Read durable Data Analytics source-routing choices from user-context.md."""
    if not markdown:
        return {}
    bounds = section_bounds(markdown)
    source_routing_section = bounds.get(SOURCE_ROUTING_PREFERENCES_HEADING)
    if not source_routing_section:
        return {}
    start, end, _ = source_routing_section
    section = markdown[start:end]
    preferences: dict[str, dict[str, list[str]]] = {}
    current_category: str | None = None
    for raw_line in section.splitlines():
        line = raw_line.strip()
        category_match = re.match(r"^##\s+([a-z0-9_]+)\s*$", line)
        if category_match:
            category_id = category_match.group(1)
            current_category = category_id if category_id in source_category_config else None
            continue
        if not current_category:
            continue
        preference_match = re.match(r"^-\s*(Prefer|Avoid):\s*(.*?)\s*$", line)
        if not preference_match:
            continue
        disposition = "preferred" if preference_match.group(1) == "Prefer" else "avoid"
        configured_sources = {
            normalize_source_name(str(source)): str(source)
            for source in preferred_source_routes(source_category_config[current_category])
        }
        for source_name in parse_source_preference_values(preference_match.group(2)):
            configured_source = configured_sources.get(normalize_source_name(source_name))
            if not configured_source:
                continue
            category_preferences = preferences.setdefault(current_category, {})
            values = category_preferences.setdefault(disposition, [])
            if configured_source not in values:
                values.append(configured_source)
    return preferences


def summarize_user_context(
    markdown: str | None,
    source_category_config: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    """Return the narrow normalized Data Analytics user-context surface."""
    return {
        "scope": "source_routing_preferences_and_semantic_layer_registry",
        "source_routing_preferences": extract_saved_source_preferences(
            markdown,
            source_category_config,
        ),
        "semantic_layer_count": len(semantic_layer_registry(markdown)),
        "normalization_complete": markdown is not None,
    }


def read_text_payload(path: Path, max_context_bytes: int, sections: list[str]) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "path": str(path),
        "status": "missing",
        "bytes": 0,
        "sha256": None,
        "mtime": None,
        "content": None,
        "sections": [],
        "omitted": False,
        "error": None,
    }
    if not path.exists():
        return payload
    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as exc:
        payload["status"] = "unreadable"
        payload["error"] = str(exc)
        return payload

    encoded_len = len(text.encode("utf-8"))
    payload.update(
        {
            "status": "present",
            "bytes": encoded_len,
            "sha256": sha256_text(text),
            "mtime": file_mtime(path),
            "sections": extract_sections(text, sections),
            "_content": text,
        }
    )
    if encoded_len <= max_context_bytes:
        payload["content"] = text
    else:
        payload["omitted"] = True
        payload["omission_reason"] = (
            f"file exceeds max_context_bytes ({encoded_len} > {max_context_bytes})"
        )
    return payload


def payload_text(payload: dict[str, Any]) -> str | None:
    text = payload.get("_content")
    if isinstance(text, str):
        return text
    content = payload.get("content")
    return content if isinstance(content, str) else None


def public_file_payload(
    payload: dict[str, Any],
    *,
    include_content: bool,
) -> dict[str, Any]:
    public = {
        key: value for key, value in payload.items() if key not in {"_content", "data"}
    }
    if not include_content:
        public.pop("content", None)
    return public


def read_json_payload(path: Path, max_context_bytes: int) -> dict[str, Any]:
    payload = read_text_payload(path, max_context_bytes=max_context_bytes, sections=[])
    payload["data"] = None
    if payload["status"] != "present":
        return payload
    try:
        payload["data"] = json.loads(payload_text(payload) or path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        payload["status"] = "unreadable"
        payload["error"] = f"invalid json: {exc}"
    return payload


def markdown_template_from_onboarding_reference(heading_name: str) -> str:
    text = ONBOARDING_REFERENCE.read_text(encoding="utf-8")
    heading = re.search(rf"(?m)^## {re.escape(heading_name)}\s*$", text)
    if not heading:
        raise RuntimeError(f"{heading_name} heading not found")
    following = text[heading.end() :]
    code_block = re.search(r"```md\n(.*?)\n```", following, flags=re.DOTALL)
    if not code_block:
        raise RuntimeError(f"{heading_name} markdown block not found")
    return code_block.group(1).strip()


def load_source_category_config() -> dict[str, Any]:
    return json.loads(SOURCE_CATEGORY_CONFIG_REFERENCE.read_text(encoding="utf-8"))["categories"]


def unique_strings(values: list[Any]) -> list[str]:
    return list(dict.fromkeys(str(value) for value in values if isinstance(value, str) and value))


def preferred_source_routes(metadata: dict[str, Any]) -> list[str]:
    return unique_strings(
        [
            *(metadata.get("preferred_plugins") or []),
            *(metadata.get("preferred_apps") or []),
        ]
    )


def normalize_source_kind(value: Any) -> str | None:
    source_kind = str(value or "").casefold()
    if source_kind in {"plugin", "app", "connector", "manual"}:
        return source_kind
    return None


PLUGIN_INSTALL_EVIDENCE = {
    "installed_plugin_skill_visible",
    "plugin_in_available_plugins",
    "plugin_owned_skill_visible",
    "request_plugin_install_completed",
    "user_confirmed_installed_plugin",
}

PLUGIN_SKILL_SURFACE_EVIDENCE = {
    "plugin_skills_visible",
    "plugin_owned_skill_visible",
    "plugin_owned_skills_visible",
}

PLUGIN_TOOL_SURFACE_EVIDENCE = {
    "callable_app_tools_visible",
    "callable_plugin_tools_visible",
    "plugin_tools_visible",
}

PLUGIN_FIRST_SETUP_STATUSES = {
    "active",
    "missing",
    "needs_confirmation",
    "unavailable",
    "deferred",
    "deferred_environment_api_limitations",
    "skipped_for_now",
}


def compact_mapping(value: Any) -> dict[str, Any] | None:
    if not isinstance(value, dict):
        return None
    compact = {
        str(key): item
        for key, item in value.items()
        if isinstance(key, str) and (isinstance(item, (str, int, float, bool)) or item is None)
    }
    return compact or None


def default_skill_surface(source_kind: str | None, metadata: dict[str, Any]) -> str | None:
    if source_kind == "plugin":
        return "plugin_owned"
    if source_kind in {"app", "connector"}:
        if metadata.get("relevant_skills"):
            return "data_analytics_vendored_helper"
        return "direct_tool"
    if source_kind == "manual":
        return "manual"
    return None


def default_runtime_action(source_kind: str | None, skill_surface: str | None) -> str | None:
    if source_kind == "plugin":
        return "use_plugin_owned_skill_or_tools"
    if source_kind in {"app", "connector"}:
        if skill_surface == "data_analytics_vendored_helper":
            return "use_connector_or_app_with_data_analytics_helper_guidance"
        return "use_direct_tool_when_workflow_needs_source"
    if source_kind == "manual":
        return "use_manual_or_exported_context"
    return None


def copy_configured_route_metadata(
    entry: dict[str, Any],
    raw_entry: dict[str, Any],
    metadata: dict[str, Any],
) -> None:
    source_kind = normalize_source_kind(raw_entry.get("source_kind"))
    if source_kind is None:
        if isinstance(raw_entry.get("plugin"), dict):
            source_kind = "plugin"
        elif isinstance(raw_entry.get("connector"), dict):
            source_kind = "connector"
        elif isinstance(raw_entry.get("app"), dict):
            source_kind = "app"
        elif isinstance(raw_entry.get("manual"), dict) or raw_entry.get("manual_source"):
            source_kind = "manual"
        elif entry.get("status") == "active" and entry.get("preferred"):
            source_kind = "connector"

    if source_kind:
        entry["source_kind"] = source_kind

    for key in ("plugin", "app", "connector", "manual"):
        compact = compact_mapping(raw_entry.get(key))
        if compact is not None:
            entry[key] = compact

    manual_source = raw_entry.get("manual_source")
    if isinstance(manual_source, str) and manual_source:
        entry["manual_source"] = manual_source

    skill_surface = str(raw_entry.get("skill_surface") or "") or default_skill_surface(
        source_kind,
        metadata,
    )
    if skill_surface:
        entry["skill_surface"] = skill_surface

    runtime_action = str(raw_entry.get("runtime_action") or "") or default_runtime_action(
        source_kind,
        skill_surface,
    )
    if runtime_action:
        entry["runtime_action"] = runtime_action

    for evidence_key in (
        "installed_evidence",
        "plugin_install_evidence",
        "app_surface_evidence",
        "connector_surface_evidence",
        "skill_surface_evidence",
        "tool_surface_evidence",
    ):
        evidence_value = raw_entry.get(evidence_key)
        if isinstance(evidence_value, str) and evidence_value:
            entry[evidence_key] = evidence_value


def copy_source_resolution_metadata(
    entry: dict[str, Any],
    raw_entry: dict[str, Any],
) -> None:
    for key in ("resolution", "resolved_at", "resolution_note"):
        value = raw_entry.get(key)
        if isinstance(value, str) and value:
            entry[key] = value


def core_source_fallback_is_explicit(entry: dict[str, Any]) -> bool:
    return (
        str(entry.get("resolution") or "").casefold()
        in CORE_SOURCE_EXPLICIT_FALLBACK_RESOLUTIONS
    )


def normalize_unacknowledged_core_source_fallback(
    category_id: str,
    entry: dict[str, Any],
    metadata: dict[str, Any],
) -> None:
    if category_id not in CORE_CATEGORY_IDS:
        return
    if entry.get("status") not in ONBOARDING_RESOLVED_SOURCE_STATUSES:
        return
    if core_source_fallback_is_explicit(entry):
        return

    recorded_status = str(entry["status"])
    previous_setup_action = str(
        entry.get("fallback_setup_action") or entry.get("setup_action") or ""
    )
    preferred_routes = preferred_source_routes(metadata)
    entry["recorded_status"] = recorded_status
    entry["status"] = "needs_confirmation"
    entry["candidates"] = preferred_routes
    entry["setup_action"] = "run_plugin_first_source_setup"
    if previous_setup_action and previous_setup_action != entry["setup_action"]:
        entry["fallback_setup_action"] = previous_setup_action
    entry["setup_note"] = "core_source_requires_explicit_user_resolution_before_fallback"
    entry["plugin_preference_order"] = preferred_routes
    entry["setup_recovery"] = plugin_first_setup_recovery(metadata, previous_setup_action)


def compact_source_route(raw_route: Any, metadata: dict[str, Any]) -> dict[str, Any] | None:
    if not isinstance(raw_route, dict):
        return None
    route: dict[str, Any] = {}
    for key in ("status", "preferred", "name", "label", "fallback", "setup_action"):
        value = raw_route.get(key)
        if isinstance(value, str) and value:
            route[key] = value
    copy_configured_route_metadata(route, raw_route, metadata)
    if "preferred" not in route:
        for route_key in ("plugin", "app", "connector", "manual"):
            raw_value = raw_route.get(route_key)
            if isinstance(raw_value, str) and raw_value:
                route["preferred"] = raw_value
                break
            if isinstance(raw_value, dict):
                for name_key in ("name", "display_name", "id"):
                    name_value = raw_value.get(name_key)
                    if isinstance(name_value, str) and name_value:
                        route["preferred"] = name_value
                        break
                if "preferred" in route:
                    break
    if "runtime_action" not in route and route.get("source_kind"):
        runtime_action = default_runtime_action(
            str(route.get("source_kind") or ""),
            str(route.get("skill_surface") or ""),
        )
        if runtime_action:
            route["runtime_action"] = runtime_action
    return route or None


def active_plugin_route_present(entry: dict[str, Any]) -> bool:
    if entry.get("source_kind") == "plugin":
        return True
    routes = entry.get("routes")
    if not isinstance(routes, list):
        return False
    return any(isinstance(route, dict) and route.get("source_kind") == "plugin" for route in routes)


def unproven_plugin_route(entry: dict[str, Any]) -> bool:
    if entry.get("source_kind") != "plugin":
        return False
    installed_evidence = str(entry.get("installed_evidence") or "")
    plugin_install_evidence = str(entry.get("plugin_install_evidence") or "")
    if installed_evidence in PLUGIN_INSTALL_EVIDENCE:
        return False
    if plugin_install_evidence not in PLUGIN_INSTALL_EVIDENCE:
        return True
    if entry.get("skill_surface") == "plugin_owned":
        skill_surface_evidence = str(entry.get("skill_surface_evidence") or "")
        if skill_surface_evidence not in PLUGIN_SKILL_SURFACE_EVIDENCE:
            return True
    surface_evidence = {
        str(entry.get("app_surface_evidence") or ""),
        str(entry.get("tool_surface_evidence") or ""),
        str(entry.get("skill_surface_evidence") or ""),
    }
    return not surface_evidence.intersection(
        PLUGIN_TOOL_SURFACE_EVIDENCE | PLUGIN_SKILL_SURFACE_EVIDENCE
    )


def list_from_inventory(inventory: dict[str, Any], *keys: str) -> list[str]:
    values: list[str] = []
    for key in keys:
        raw = inventory.get(key)
        if isinstance(raw, list):
            values.extend(str(item) for item in raw if isinstance(item, str) and item)
    return values


def matching_configured_sources(preferred_sources: list[str], candidates: set[str]) -> list[str]:
    return [
        source for source in preferred_sources if normalize_source_name(source) in candidates
    ]


def missing_source_it_options(preferred_sources: list[str]) -> list[str]:
    source_list = ", ".join(preferred_sources) if preferred_sources else "a matching source"
    return [
        f"Ask IT or a workspace admin to install or enable one of: {source_list}.",
        "Use exported, pasted, or manually supplied context for the current workflow.",
    ]


def load_app_connector_ids() -> dict[str, str]:
    manifest = json.loads(APP_MANIFEST_REFERENCE.read_text(encoding="utf-8"))
    apps = manifest.get("apps") if isinstance(manifest, dict) else None
    if not isinstance(apps, dict):
        return {}
    return {
        normalize_source_name(app_name): str(metadata["id"])
        for app_name, metadata in apps.items()
        if isinstance(app_name, str)
        and isinstance(metadata, dict)
        and isinstance(metadata.get("id"), str)
        and metadata["id"]
    }


def plugin_connector_ids(
    plugin_name: str,
    metadata: dict[str, Any],
    app_connector_ids: dict[str, str],
) -> set[str]:
    plugin_alias = normalize_source_name(plugin_name)
    return {
        connector_id
        for source_name in preferred_source_routes(metadata)
        if normalize_source_name(source_name) == plugin_alias
        for connector_id in [app_connector_ids.get(normalize_source_name(source_name))]
        if connector_id
    }


def compact_install_candidate(candidate: dict[str, Any]) -> dict[str, Any]:
    return {
        key: candidate[key]
        for key in (
            "id",
            "name",
            "display_name",
            "tool_type",
            "has_skills",
            "app_connector_ids",
        )
        if key in candidate
    }


def match_installable_plugin_candidates(
    source_category_config: dict[str, Any],
    candidates: list[dict[str, Any]] | dict[str, Any],
    app_connector_ids: dict[str, str] | None = None,
) -> dict[str, list[dict[str, Any]]]:
    """Rank installable plugins using config order, plugin slugs, and connector ids."""
    if isinstance(candidates, dict):
        raw_candidates = candidates.get("tools")
        candidates = raw_candidates if isinstance(raw_candidates, list) else []
    connector_ids = app_connector_ids if app_connector_ids is not None else load_app_connector_ids()
    matches: dict[str, list[dict[str, Any]]] = {}
    for category_id, metadata in source_category_config.items():
        category_matches: list[dict[str, Any]] = []
        for rank, plugin_name in enumerate(metadata.get("preferred_plugins") or []):
            plugin_alias = normalize_source_name(plugin_name)
            configured_connector_ids = plugin_connector_ids(plugin_name, metadata, connector_ids)
            for candidate in candidates:
                if not isinstance(candidate, dict) or candidate.get("tool_type") != "plugin":
                    continue
                candidate_aliases = {
                    normalize_source_name(candidate.get("name")),
                    normalize_source_name(candidate.get("display_name")),
                    normalize_source_name(str(candidate.get("id") or "").split("@", 1)[0]),
                }
                candidate_connector_ids = {
                    str(connector_id)
                    for connector_id in candidate.get("app_connector_ids") or []
                    if isinstance(connector_id, str)
                }
                reasons: list[str] = []
                if plugin_alias and plugin_alias in candidate_aliases:
                    reasons.append("plugin_name")
                if configured_connector_ids & candidate_connector_ids:
                    reasons.append("app_connector_id")
                if not reasons:
                    continue
                category_matches.append(
                    {
                        "preferred_plugin": plugin_name,
                        "preference_rank": rank,
                        "match_reasons": reasons,
                        "candidate": compact_install_candidate(candidate),
                    }
                )
                break
        if category_matches:
            matches[category_id] = category_matches
    return matches


def plugin_first_setup_recovery(
    metadata: dict[str, Any],
    fallback_setup_action: str,
) -> dict[str, Any]:
    recovery = {
        "type": "plugin_first_source_setup",
        "preferred_plugins": unique_strings(metadata.get("preferred_plugins") or []),
        "configured_source_routes": preferred_source_routes(metadata),
        "candidate_lookup": "functions.list_available_plugins_to_install",
        "candidate_match": "plugin_name_slug_or_app_connector_id_intersection",
        "install_request": "functions.request_plugin_install",
        "install_requires_user_approval": True,
        "fallback_setup_action": fallback_setup_action,
    }
    legacy_app_fallbacks = unique_strings(metadata.get("preferred_apps") or [])
    if legacy_app_fallbacks:
        recovery["legacy_app_fallbacks"] = legacy_app_fallbacks
    return recovery


def connector_confirmation_base_entry(
    category_id: str,
    metadata: dict[str, Any],
) -> dict[str, Any]:
    preferred_plugins = unique_strings(metadata.get("preferred_plugins") or [])
    preferred_apps = unique_strings(metadata.get("preferred_apps") or [])
    entry: dict[str, Any] = {
        "id": category_id,
        "label": metadata["label"],
        "state_scope": "onboarding_only_not_durable_connector_readiness",
        "workflow_time_behavior": "attempt_actual_reads_only_when_a_workflow_needs_the_source",
        "eager_read": False,
    }
    if preferred_plugins:
        entry["preferred_plugins"] = preferred_plugins
    if preferred_apps:
        entry["preferred_apps"] = preferred_apps
    return entry


def onboarding_status(onboarding_state: dict[str, Any] | None) -> str:
    if not onboarding_state:
        return "missing"
    return str(onboarding_state.get("status") or "active")


def connector_categories(onboarding_state: dict[str, Any] | None) -> dict[str, dict[str, Any]]:
    state = onboarding_state or {}
    connector_confirmation = state.get("connector_confirmation") or {}
    if not isinstance(connector_confirmation, dict):
        return {}
    categories = connector_confirmation.get("categories")
    if isinstance(categories, dict):
        return categories
    return {
        str(category_id): entry
        for category_id, entry in connector_confirmation.items()
        if category_id not in {"status", "last_shown", "preferences"}
        and isinstance(entry, dict)
    }


def source_status(entry: dict[str, Any] | None) -> str:
    raw_status = str((entry or {}).get("status") or "needs_confirmation").casefold()
    aliases = {
        "available": "needs_confirmation",
        "blocked": "unavailable",
        "choose_source": "needs_confirmation",
        "connected": "active",
        "manual": "active",
        "needs_setup_probe": "needs_confirmation",
        "not_available": "missing",
        "selected": "needs_confirmation",
        "selected_for_verification": "needs_confirmation",
        "selected_needs_auth": "needs_confirmation",
    }
    return aliases.get(raw_status, raw_status)


def source_setup_action(status: str) -> str:
    actions = {
        "active": "none_try_on_use",
        "needs_confirmation": "ask_user_to_choose_or_confirm_source",
        "missing": "explain_workflow_impact_and_it_admin_options",
        "unavailable": "ask_admin_or_manual_fallback",
        "declined": "none_declined",
        "skipped": "none_skipped",
        "skipped_for_now": "none_skipped",
        "deferred": "none_deferred",
        "deferred_environment_api_limitations": "none_deferred",
        "not_applicable": "none_not_applicable",
    }
    return actions.get(status, "ask_user_to_choose_or_confirm_source")


def normalized_connector_confirmation(
    source_category_config: dict[str, Any],
    onboarding_state: dict[str, Any] | None,
) -> dict[str, dict[str, Any]]:
    raw_categories = connector_categories(onboarding_state)
    state = onboarding_state or {}
    raw_confirmation = state.get("connector_confirmation") or {}
    raw_preferences = raw_confirmation.get("preferences") if isinstance(raw_confirmation, dict) else {}
    if not isinstance(raw_preferences, dict):
        raw_preferences = {}
    inventory = state.get("connector_inventory") or {}
    if not isinstance(inventory, dict):
        inventory = {}
    confirmation: dict[str, dict[str, Any]] = {}
    for category_id, metadata in source_category_config.items():
        raw_entry = raw_categories.get(category_id)
        if raw_entry is None:
            raw_entry = raw_preferences.get(category_id)
        raw_entry = raw_entry if isinstance(raw_entry, dict) else {}
        preferred_plugins = unique_strings(metadata.get("preferred_plugins") or [])
        preferred_routes = preferred_source_routes(metadata)
        entry = connector_confirmation_base_entry(category_id, metadata)

        if raw_entry:
            status = source_status(raw_entry)
            if status in ONBOARDING_RESOLVED_SOURCE_STATUSES:
                entry["status"] = status
                entry["setup_action"] = source_setup_action(status)
                copy_configured_route_metadata(entry, raw_entry, metadata)
                copy_source_resolution_metadata(entry, raw_entry)
            elif status in {"active", "needs_confirmation", "missing"}:
                entry["status"] = status
                preferred = raw_entry.get("preferred") or raw_entry.get("app")
                if isinstance(preferred, str) and preferred:
                    entry["preferred"] = preferred
                fallback = raw_entry.get("fallback") or raw_entry.get("backup")
                if isinstance(fallback, str) and fallback:
                    entry["fallback"] = fallback
                if status == "active":
                    raw_routes = raw_entry.get("routes")
                    if isinstance(raw_routes, list):
                        compacted_routes = [
                            route
                            for route in (
                                compact_source_route(raw_route, metadata) for raw_route in raw_routes
                            )
                            if route is not None
                        ]
                        routes = [
                            route
                            for route in compacted_routes
                            if not unproven_plugin_route(route)
                        ]
                        if routes:
                            entry["routes"] = routes
                            if "preferred" not in entry:
                                first_preferred = routes[0].get("preferred")
                                if isinstance(first_preferred, str) and first_preferred:
                                    entry["preferred"] = first_preferred
                        elif compacted_routes:
                            entry = connector_confirmation_base_entry(category_id, metadata)
                            entry.update(
                                {
                                    "status": "needs_confirmation",
                                    "candidates": preferred_routes,
                                    "setup_action": "run_plugin_first_source_setup",
                                    "setup_note": (
                                        "plugin_route_requires_plugin_install_and_surface_evidence_before_active"
                                    ),
                                }
                            )
                    if entry.get("status") == "active":
                        if raw_entry.get("confirmed_at"):
                            entry["confirmed_at"] = raw_entry["confirmed_at"]
                        entry["setup_action"] = "none_try_on_use"
                        copy_configured_route_metadata(entry, raw_entry, metadata)
                        copy_source_resolution_metadata(entry, raw_entry)
                        if unproven_plugin_route(entry):
                            entry = connector_confirmation_base_entry(category_id, metadata)
                            entry.update(
                                {
                                    "status": "needs_confirmation",
                                    "candidates": preferred_routes,
                                    "setup_action": "run_plugin_first_source_setup",
                                    "setup_note": (
                                        "plugin_route_requires_plugin_install_and_surface_evidence_before_active"
                                    ),
                                }
                            )
                elif status == "needs_confirmation":
                    candidates = raw_entry.get("candidates")
                    if not isinstance(candidates, list) or not candidates:
                        if preferred:
                            candidates = [preferred]
                        else:
                            candidates = preferred_routes
                    entry["candidates"] = unique_strings(candidates)
                    entry["setup_action"] = source_setup_action(status)
                    copy_configured_route_metadata(entry, raw_entry, metadata)
                    copy_source_resolution_metadata(entry, raw_entry)
                else:
                    options = raw_entry.get("options")
                    if not isinstance(options, list) or not options:
                        options = preferred_routes
                    entry["options"] = unique_strings(options)
                    entry["it_admin_options"] = raw_entry.get(
                        "it_admin_options"
                    ) or missing_source_it_options(entry["options"])
                    entry["setup_action"] = source_setup_action(status)
                    copy_configured_route_metadata(entry, raw_entry, metadata)
                    copy_source_resolution_metadata(entry, raw_entry)
            else:
                entry["status"] = "needs_confirmation"
                entry["candidates"] = preferred_routes
                entry["setup_action"] = source_setup_action("needs_confirmation")
        else:
            configured_apps = {
                normalize_source_name(app)
                for app in list_from_inventory(
                    inventory,
                    "active_apps",
                    "active",
                    "installed_and_active",
                    "connected_apps",
                    "available_apps",
                    "available",
                    "installed_apps",
                    "surfaced_apps",
                )
            }
            available_matches = matching_configured_sources(preferred_routes, configured_apps)
            if available_matches:
                entry["status"] = "needs_confirmation"
                entry["candidates"] = available_matches
                entry["setup_action"] = source_setup_action("needs_confirmation")
            elif inventory:
                entry["status"] = "missing"
                entry["options"] = preferred_routes
                entry["it_admin_options"] = missing_source_it_options(preferred_routes)
                entry["setup_action"] = source_setup_action("missing")
            else:
                entry["status"] = "needs_confirmation"
                entry["candidates"] = preferred_routes
                entry["setup_action"] = source_setup_action("needs_confirmation")

        if entry.get("status") == "active" and raw_entry.get("status") == "manual":
            entry.setdefault("source_kind", "manual")
            entry.setdefault("skill_surface", "manual")
            entry.setdefault("runtime_action", "use_manual_or_exported_context")

        if "preferred" not in entry:
            entry["preferred"] = raw_entry.get("preferred")

        relevant_skills = metadata.get("relevant_skills") or []
        if relevant_skills and str(entry.get("source_kind") or "").casefold() != "plugin":
            entry["helper_skills"] = relevant_skills
            entry["helper_skills_apply_when"] = ["app", "connector"]

        plugin_preference_order = preferred_source_routes(metadata)
        if (
            preferred_plugins
            and plugin_preference_order
            and entry["status"] in PLUGIN_FIRST_SETUP_STATUSES
        ):
            entry["plugin_preference_order"] = plugin_preference_order
            if not active_plugin_route_present(entry):
                previous_setup_action = entry.get("setup_action")
                entry["setup_action"] = "run_plugin_first_source_setup"
                if previous_setup_action and previous_setup_action != entry["setup_action"]:
                    entry["fallback_setup_action"] = previous_setup_action
                entry["setup_recovery"] = plugin_first_setup_recovery(
                    metadata,
                    str(previous_setup_action or source_setup_action(entry["status"])),
                )
        normalize_unacknowledged_core_source_fallback(category_id, entry, metadata)
        confirmation[category_id] = entry
    return confirmation


def connector_confirmation_status(
    source_category_config: dict[str, Any],
    onboarding_state: dict[str, Any] | None,
) -> str:
    state = onboarding_state or {}
    if not connector_categories(onboarding_state) and not state.get("connector_inventory"):
        return "pending"
    confirmation = normalized_connector_confirmation(source_category_config, onboarding_state)
    statuses = [confirmation[category_id]["status"] for category_id in CORE_CATEGORY_IDS]
    if statuses and all(status in SOURCE_CLASSIFIED_STATUSES for status in statuses):
        return "completed"
    if any(status for status in statuses):
        return "in_progress"
    return "pending"


def connector_confirmation_action_required(
    source_category_config: dict[str, Any],
    onboarding_state: dict[str, Any] | None,
) -> bool:
    if connector_confirmation_status(source_category_config, onboarding_state) == "pending":
        return False
    confirmation = normalized_connector_confirmation(source_category_config, onboarding_state)
    return any(
        confirmation[category_id]["status"] in SOURCE_ACTION_REQUIRED_STATUSES
        for category_id in CORE_CATEGORY_IDS
    )


def connector_setup_confirmation_status(
    source_category_config: dict[str, Any],
    onboarding_state: dict[str, Any] | None,
) -> str:
    confirmation_status = connector_confirmation_status(source_category_config, onboarding_state)
    if confirmation_status == "pending":
        return "pending"
    if connector_confirmation_action_required(source_category_config, onboarding_state):
        return "in_progress"
    return "completed"


def compact_connector_setup_summary_entry(entry: dict[str, Any]) -> dict[str, Any]:
    compact = {
        key: entry[key]
        for key in (
            "id",
            "label",
            "status",
            "preferred",
            "setup_action",
            "fallback_setup_action",
            "source_kind",
        )
        if key in entry
    }
    for key in ("candidates", "options"):
        values = entry.get(key)
        if isinstance(values, list) and values:
            compact[key] = unique_strings(values)
    return compact


def build_connector_setup_summary(
    source_category_config: dict[str, Any],
    onboarding_state: dict[str, Any] | None,
) -> dict[str, Any]:
    confirmation = normalized_connector_confirmation(source_category_config, onboarding_state)
    ready: list[dict[str, Any]] = []
    needs_attention: list[dict[str, Any]] = []
    fallback_or_closed: list[dict[str, Any]] = []
    plugin_setup_opportunities: list[dict[str, Any]] = []
    unresolved_core_ids: list[str] = []
    for category_id, entry in confirmation.items():
        status = entry["status"]
        summary_entry = compact_connector_setup_summary_entry(entry)
        if status == "active":
            ready.append(summary_entry)
        elif status in ONBOARDING_RESOLVED_SOURCE_STATUSES:
            fallback_or_closed.append(summary_entry)
        else:
            needs_attention.append(summary_entry)
        if entry.get("setup_action") == "run_plugin_first_source_setup":
            plugin_setup_opportunities.append(summary_entry)
        if category_id in CORE_CATEGORY_IDS and status in SOURCE_ACTION_REQUIRED_STATUSES:
            unresolved_core_ids.append(category_id)
    next_entry = needs_attention[0] if needs_attention else None
    return {
        "status": connector_setup_confirmation_status(source_category_config, onboarding_state),
        "classification_status": connector_confirmation_status(
            source_category_config,
            onboarding_state,
        ),
        "action_required": connector_confirmation_action_required(
            source_category_config,
            onboarding_state,
        ),
        "has_setup_gaps": bool(needs_attention or plugin_setup_opportunities),
        "ready": ready,
        "active": ready,
        "needs_attention": needs_attention,
        "needs_choice": needs_attention,
        "fallback_or_closed": fallback_or_closed,
        "not_set_up": fallback_or_closed,
        "plugin_setup_opportunities": plugin_setup_opportunities,
        "unresolved_core_ids": unresolved_core_ids,
        "core_complete": connector_setup_confirmation_status(
            source_category_config,
            onboarding_state,
        )
        == "completed",
        "next_action": (
            {
                "category_id": next_entry["id"],
                "label": next_entry["label"],
                "status": next_entry["status"],
                "preferred": next_entry["preferred"],
                "setup_action": next_entry["setup_action"],
            }
            if next_entry
            else None
        ),
        "user_facing_guidance": (
            "Use this summary for capability or setup-status answers. During onboarding, "
            "resolve one highest-value source action at a time. Active sources are FYI only; "
            "attempt actual reads only when a workflow needs the source."
        ),
    }


def semantic_layer_setup_status(onboarding_state: dict[str, Any] | None) -> str:
    state = onboarding_state or {}
    return str((state.get("semantic_layer_setup") or {}).get("status") or "pending")


def semantic_layer_refresh_status(onboarding_state: dict[str, Any] | None) -> str:
    state = onboarding_state or {}
    return str((state.get("semantic_layer_refresh") or {}).get("status") or "pending")


def semantic_layer_setup_resolved(onboarding_state: dict[str, Any] | None) -> bool:
    setup_status = semantic_layer_setup_status(onboarding_state)
    if setup_status not in SEMANTIC_SETUP_COMPLETE_STATUSES:
        return False
    if setup_status in SEMANTIC_SETUP_TARGET_STATUSES:
        return semantic_layer_refresh_status(onboarding_state) in SEMANTIC_REFRESH_COMPLETE_STATUSES
    return True


def hero_prompt_state(onboarding_state: dict[str, Any] | None) -> dict[str, Any]:
    state = onboarding_state or {}
    choice = state.get("hero_prompt_choice")
    if isinstance(choice, dict):
        return choice
    legacy = state.get("hero_prompts")
    return legacy if isinstance(legacy, dict) else {}


def first_hero_prompt_status(onboarding_state: dict[str, Any] | None) -> str:
    choice = hero_prompt_state(onboarding_state)
    status = str(choice.get("status") or "")
    if status in HERO_PROMPT_COMPLETE_STATUSES:
        return "completed"
    if status == "selected":
        return "in_progress"
    skill_experience = (onboarding_state or {}).get("skill_experience") or {}
    if any(
        isinstance(skill_experience.get(skill), dict)
        and skill_experience[skill].get("first_tried_at")
        for skill in HERO_SKILLS
    ):
        return "completed"
    if (onboarding_state or {}).get("completed_hero_prompts"):
        return "completed"
    return "pending"


def core_onboarding_complete(
    source_category_config: dict[str, Any],
    onboarding_state: dict[str, Any] | None,
) -> bool:
    if not onboarding_state:
        return False
    explicit_status = str(
        (onboarding_state.get("core_onboarding") or {}).get("status") or ""
    ).casefold()
    if explicit_status in {"completed", "complete", "complete_with_fallback"}:
        return True
    return (
        connector_setup_confirmation_status(source_category_config, onboarding_state)
        == "completed"
        and semantic_layer_setup_resolved(onboarding_state)
    )


def progress_task_list(
    source_category_config: dict[str, Any],
    onboarding_state: dict[str, Any] | None,
) -> list[dict[str, str]]:
    state = onboarding_state or {}
    status = onboarding_status(onboarding_state)
    task_specs = (
        (
            "orientation",
            "Orientation",
            (state.get("orientation") or {}).get("status") in {"shown", "completed"},
        ),
        (
            "source_setup_confirmation",
            "Check main analytics sources",
            connector_setup_confirmation_status(source_category_config, onboarding_state)
            == "completed",
        ),
        (
            "semantic_layer_setup",
            "Set Up Data Context",
            semantic_layer_setup_resolved(onboarding_state),
        ),
        ("hero_prompt", "Hero prompt", first_hero_prompt_status(onboarding_state) == "completed"),
    )
    found_in_progress = False
    task_list: list[dict[str, str]] = []
    for task_id, label, completed in task_specs:
        if completed:
            task_status = "completed"
        elif not found_in_progress and status not in {"complete", "quiet"}:
            task_status = "in_progress"
            found_in_progress = True
        else:
            task_status = "pending"
        task_list.append({"id": task_id, "label": label, "status": task_status})
    return task_list


def next_onboarding_action(
    source_category_config: dict[str, Any],
    onboarding_state: dict[str, Any] | None,
) -> dict[str, str] | None:
    tasks = progress_task_list(source_category_config, onboarding_state)
    for task in tasks:
        if task["status"] == "completed":
            continue
        mapping = {
            "orientation": ("start_data_analytics_onboarding", "show orientation"),
            "source_setup_confirmation": (
                "confirm_analytics_sources",
                "confirm active or missing sources",
            ),
            "semantic_layer_setup": (
                "introduce_semantic_layer_setup",
                "set up data context",
            ),
            "hero_prompt": ("offer_first_hero_prompt", "run or resolve the first hero prompt"),
        }
        action_id, label = mapping[task["id"]]
        return {"id": action_id, "label": label}
    return None


def semantic_layer_registry(user_context_text: str | None) -> list[dict[str, str]]:
    if not user_context_text:
        return []
    bounds = section_bounds(user_context_text)
    semantic_section = bounds.get("semantic layers")
    if not semantic_section:
        return []
    start, end, _ = semantic_section
    section = user_context_text[start:end]
    entries: list[dict[str, str]] = []
    for block in re.split(r"(?m)^- Area:\s*", section)[1:]:
        lines = block.splitlines()
        area = lines[0].strip()
        entry: dict[str, str] = {"area": area}
        for line in lines[1:]:
            match = re.match(
                r"\s*-\s*(Skill Name|Skill Path|Source Inventory Path|Last Updated):\s*(.+?)\s*$",
                line,
            )
            if match:
                entry[match.group(1).lower().replace(" ", "_")] = match.group(2)
        if "skill_path" in entry:
            entries.append(entry)
    return entries


def saved_anchor_values(user_context_text: str | None) -> dict[str, list[str]]:
    if not user_context_text:
        return {"areas": [], "metrics": [], "dashboards": [], "tables": [], "goals": []}
    return {
        "areas": [entry["area"] for entry in semantic_layer_registry(user_context_text)],
        "metrics": [],
        "dashboards": [],
        "tables": [],
        "goals": [],
    }


def build_hero_prompt_candidates(
    user_context_text: str | None,
    onboarding_state: dict[str, Any] | None,
) -> list[dict[str, str]]:
    anchors = saved_anchor_values(user_context_text)
    semantic_setup = (onboarding_state or {}).get("semantic_layer_setup") or {}
    area = semantic_setup.get("area") or (anchors["areas"][0] if anchors["areas"] else None)
    metric = anchors["metrics"][0] if anchors["metrics"] else None
    dashboard = anchors["dashboards"][0] if anchors["dashboards"] else None
    goal = anchors["goals"][0] if anchors["goals"] else None
    target = area or goal or dashboard or metric
    if not target:
        return []

    return [
        {
            "skill": "product-business-analysis",
            "label": "Build a decision-ready report",
            "prompt": (
                f"Build a decision-ready report for {target}: explain what is happening, "
                "identify the main drivers, recommend where the team should focus next, "
                "and include sources, caveats, and useful charts."
            ),
        }
    ]


def reorder_hero_prompt_candidates(
    candidates: list[dict[str, str]],
    onboarding_state: dict[str, Any] | None,
) -> list[dict[str, str]]:
    selected_skill = str(hero_prompt_state(onboarding_state).get("selected_skill") or "")
    if not selected_skill:
        return candidates
    selected = [candidate for candidate in candidates if candidate["skill"] == selected_skill]
    remaining = [candidate for candidate in candidates if candidate["skill"] != selected_skill]
    return selected + remaining


def current_skill_experience(
    workflow: str,
    request_mode: str,
    onboarding_state: dict[str, Any] | None,
) -> dict[str, Any]:
    skill_experience = (onboarding_state or {}).get("skill_experience") or {}
    entry = skill_experience.get(workflow) if isinstance(skill_experience, dict) else None
    entry = entry if isinstance(entry, dict) else {}
    introduced = bool(entry.get("introduced_at"))
    tried = bool(entry.get("first_tried_at"))
    dismissed = bool(entry.get("dismissed_at"))
    return {
        "skill": workflow,
        "introduced": introduced,
        "tried": tried,
        "dismissed": dismissed,
        "intro_eligible": workflow in HERO_SKILLS and not introduced and not dismissed,
        "cta_owner": "onboarding" if request_mode == "guided_onboarding_workflow" else "skill",
    }


def final_obligations(
    request_mode: str,
    user_context_status: str,
    source_category_config: dict[str, Any],
    onboarding_state: dict[str, Any] | None,
) -> list[dict[str, Any]]:
    if request_mode != "ordinary_workflow":
        return []
    status = onboarding_status(onboarding_state)
    if status in {"complete", "quiet"}:
        return []
    if user_context_status in {"missing", "unreadable"}:
        return [
            {
                "id": "offer_data_analytics_onboarding_next_step",
                "timing": "append_after_main_answer",
                "template": markdown_template_from_onboarding_reference(
                    "Ordinary Workflow Onboarding CTA"
                ),
                "next_action": {"id": "start_data_analytics_onboarding"},
                "skip_when": "the response requires a clarification or the user asked for quiet behavior",
            }
        ]
    if not core_onboarding_complete(source_category_config, onboarding_state):
        return [
            {
                "id": "complete_data_analytics_core_onboarding",
                "timing": "append_after_main_answer",
                "template": markdown_template_from_onboarding_reference(
                    "Active Core Onboarding Reminder"
                ),
                "requirement": "core onboarding is not complete",
                "next_action": next_onboarding_action(source_category_config, onboarding_state),
                "skip_when": "the response requires a clarification or the user asked for quiet behavior",
            }
        ]
    return []


def conditional_guidance(request_mode: str, user_context_status: str) -> list[dict[str, Any]]:
    if request_mode != "ordinary_workflow":
        return []
    if user_context_status not in {"missing", "unreadable"}:
        return []
    return [
        {
            "id": "context_gap_note",
            "template": markdown_template_from_onboarding_reference("Context Gap Note"),
            "potential_gaps": [
                "Data Analytics source-routing preferences or semantic-layer registry are missing or unreadable"
            ],
        }
    ]


def main() -> int:
    args = parse_args()
    state_dir = state_dir_from_args(args)
    user_context_path = state_dir / "user-context.md"
    onboarding_state_path = state_dir / "onboarding-state.json"

    user_context = read_text_payload(
        user_context_path,
        max_context_bytes=args.max_context_bytes,
        sections=args.section,
    )
    onboarding_state = read_json_payload(
        onboarding_state_path,
        max_context_bytes=args.max_context_bytes,
    )
    onboarding_data = (
        onboarding_state.get("data") if onboarding_state["status"] == "present" else None
    )
    source_category_config = load_source_category_config()
    user_context_text = payload_text(user_context)
    saved_source_preferences = extract_saved_source_preferences(
        user_context_text,
        source_category_config,
    )
    connector_confirmation = normalized_connector_confirmation(
        source_category_config, onboarding_data
    )
    connector_setup_summary = build_connector_setup_summary(source_category_config, onboarding_data)
    hero_prompt_candidates = reorder_hero_prompt_candidates(
        build_hero_prompt_candidates(user_context_text, onboarding_data),
        onboarding_data,
    )
    task_list = progress_task_list(source_category_config, onboarding_data)
    payload = {
        "schema": "data_analytics_preflight.v1",
        "read_only": True,
        "workflow": args.workflow,
        "request_mode": args.request_mode,
        "state": {
            "state_dir": str(state_dir),
            "user_context_status": user_context["status"],
            "onboarding_state_status": onboarding_state["status"],
        },
        "files": {
            "user_context": public_file_payload(user_context, include_content=False),
            "onboarding_state": public_file_payload(onboarding_state, include_content=False),
        },
        "current_skill_experience": current_skill_experience(
            args.workflow,
            args.request_mode,
            onboarding_data,
        ),
        "context": {
            "user_context": summarize_user_context(user_context_text, source_category_config),
            "source_preferences": saved_source_preferences,
            "source_category_config": source_category_config,
            "connector_confirmation": connector_confirmation,
            "connector_setup_summary": connector_setup_summary,
            "semantic_layers": semantic_layer_registry(user_context_text),
            "hero_prompt_candidates": hero_prompt_candidates,
            "primary_hero_prompt": hero_prompt_candidates[0] if hero_prompt_candidates else None,
            "extra_hero_prompt_candidates": hero_prompt_candidates[1:3],
        },
        "control": {
            "response_mode": args.request_mode,
            "final_obligations": final_obligations(
                args.request_mode,
                user_context["status"],
                source_category_config,
                onboarding_data,
            ),
            "conditional_guidance": conditional_guidance(args.request_mode, user_context["status"]),
            "onboarding_progress": {
                "status": onboarding_status(onboarding_data),
                "core_onboarding": {
                    "complete": core_onboarding_complete(source_category_config, onboarding_data),
                    "remaining_step_ids": [
                        item["id"] for item in task_list if item["status"] != "completed"
                    ],
                    "next_action": next_onboarding_action(source_category_config, onboarding_data),
                },
                "task_list": task_list,
            },
        },
    }
    print(json.dumps(payload, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
