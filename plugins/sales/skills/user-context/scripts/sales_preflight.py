#!/usr/bin/env python3
"""Read Sales local state and emit a compact deterministic preflight payload."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))
from state_paths import STATE_DIR_HELP, resolve_state_dir

PLUGIN_ROOT = Path(__file__).resolve().parents[3]
ONBOARDING_REFERENCE = PLUGIN_ROOT / "skills/user-context/references/onboarding.md"
SOURCE_CATEGORY_CONFIG_REFERENCE = (
    PLUGIN_ROOT / "skills/user-context/plugin-author-config/source-category-config.json"
)
AUTOMATION_CONFIG_REFERENCE = (
    PLUGIN_ROOT / "skills/user-context/plugin-author-config/automation-config.md"
)

DEFAULT_MAX_CONTEXT_BYTES = 2_000_000


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Read Sales user-context and onboarding-state files "
            "and return context plus workflow control obligations as JSON."
        )
    )
    parser.add_argument(
        "--workflow",
        default="ordinary",
        help="Calling Sales workflow name, for example prepare-for-meeting.",
    )
    parser.add_argument(
        "--request-mode",
        choices=("ordinary_workflow", "direct_onboarding_status", "guided_onboarding_workflow"),
        default="ordinary_workflow",
        help=(
            "Whether the caller is doing ordinary work, direct setup/onboarding, "
            "or a focused workflow launched from the onboarding path."
        ),
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
        "--max-context-bytes",
        type=int,
        default=DEFAULT_MAX_CONTEXT_BYTES,
        help=(
            "Compatibility limit for raw file reads. Compact preflight still renders a "
            "derived summary instead of raw file contents."
        ),
    )
    parser.add_argument(
        "--section",
        action="append",
        default=[],
        help=(
            "Markdown section heading to return even when full context is omitted. Can be repeated."
        ),
    )
    return parser.parse_args()


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
            next_level = len(next_match.group(1))
            if next_level <= level:
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


def parse_saved_context_heading(line: str) -> dict[str, str]:
    match = re.match(r"^\[(.+)\]\(([^)]+)\)\s*$", line)
    if match:
        return {"name": match.group(1).strip(), "url": match.group(2).strip()}
    return {"name": line.strip()}


def guardrail_sentences(text: str) -> list[str]:
    sentences = re.split(r"(?<=[.!?])\s+", text.strip())
    return [
        sentence
        for sentence in sentences
        if re.search(
            r"\b(avoid|approved|current|currentness|do not|fresh|higher authority|"
            r"human review|keep|unless|verify|review|sensitive|treat)\b",
            sentence,
            flags=re.IGNORECASE,
        )
    ]


def summarize_user_context(markdown: str | None) -> dict[str, Any]:
    """Return a compact complete rendering of saved Sales user context."""
    if not markdown:
        return {"entries": [], "unresolved_categories": []}

    entries: list[str] = []
    unresolved_categories: list[str] = []
    category: str | None = None
    in_saved_context = False
    current_entry: dict[str, Any] | None = None

    def flush_entry() -> None:
        nonlocal current_entry
        if current_entry:
            parts = [f"{current_entry['category']}: {current_entry['name']}"]
            if current_entry.get("url"):
                parts.append(f"<{current_entry['url']}>")
            if current_entry.get("context"):
                parts.append(current_entry["context"])
            guardrails = guardrail_sentences(str(current_entry.get("use") or ""))
            if guardrails:
                parts.append(" ".join(guardrails))
            notes = current_entry.get("notes")
            if notes:
                parts.extend(str(note) for note in notes)
            entries.append(" | ".join(parts))
            current_entry = None

    for raw_line in markdown.splitlines():
        line = raw_line.strip()
        if not line or line.startswith("<!--") or line.startswith("-->"):
            continue
        heading = re.match(r"^# ([^#].*?)\s*$", line)
        if heading:
            flush_entry()
            category = heading.group(1).strip()
            in_saved_context = False
            continue
        if line == "## Saved Links And Context":
            flush_entry()
            in_saved_context = True
            continue
        if not category or not in_saved_context:
            continue
        if line == "Status: Not Provided":
            flush_entry()
            unresolved_categories.append(category)
            continue
        if not line.startswith("- "):
            flush_entry()
            current_entry = {"category": category, **parse_saved_context_heading(line)}
            continue
        if not current_entry:
            continue
        bullet = line[2:].strip()
        for prefix, key in (
            ("Date Added:", "date_added"),
            ("Useful Context:", "context"),
            ("Future Use:", "use"),
        ):
            if bullet.startswith(prefix):
                current_entry[key] = bullet[len(prefix) :].strip().rstrip(".")
                break
        else:
            current_entry.setdefault("notes", []).append(bullet)
    flush_entry()
    return {"entries": entries, "unresolved_categories": unresolved_categories}


NEGATIVE_SOURCE_PREFERENCE_RE = re.compile(
    r"\b(do not use|don't use|never use|declin(?:e|ed)|skip|not preferred|avoid)\b",
    flags=re.IGNORECASE,
)

SOURCE_PREFERENCE_SECTION_HINTS = {
    "source",
    "sources",
    "preference",
    "preferences",
    "preferred",
    "default",
    "defaults",
    "connector",
    "connectors",
    "crm",
    "calendar",
    "meeting",
    "notes",
    "docs",
    "documents",
    "email",
    "messaging",
    "messages",
    "enrichment",
    "agreement",
    "agreements",
    "contract",
    "contracts",
    "signature",
    "signatures",
}

SOURCE_CATEGORY_ALIASES = {
    "crm": {"crm", "account", "accounts", "opportunity", "opportunities", "pipeline"},
    "calendar": {"calendar", "meetings"},
    "meeting_notes": {"meeting", "meetings", "notes", "transcript", "transcripts", "recordings"},
    "document_store": {"docs", "documents", "drive", "sharepoint", "notion"},
    "data_enrichment": {"enrichment", "firmographic", "technographic", "market", "signals"},
    "external_messaging": {"external", "customer", "customers", "email", "thread", "threads"},
    "internal_messaging": {"internal", "slack", "teams", "messages", "messaging"},
    "agreements": {
        "agreement",
        "agreements",
        "approval",
        "approvals",
        "contract",
        "contracts",
        "docusign",
        "esignature",
        "signature",
        "signatures",
    },
}


def source_preference_section_name(category_name: str) -> bool:
    tokens = {
        token.casefold()
        for token in re.findall(r"[a-z0-9]+", category_name, flags=re.IGNORECASE)
    }
    return bool(tokens & SOURCE_PREFERENCE_SECTION_HINTS)


def entry_mentions_source_category(entry: str, category_id: str, label: str) -> bool:
    entry_tokens = {
        token.casefold()
        for token in re.findall(r"[a-z0-9]+", entry, flags=re.IGNORECASE)
    }
    aliases = {
        token.casefold()
        for token in re.findall(
            r"[a-z0-9]+",
            f"{category_id.replace('_', ' ')} {label}",
            flags=re.IGNORECASE,
        )
        if len(token) > 2
    }
    aliases.update(SOURCE_CATEGORY_ALIASES.get(category_id, set()))
    return bool(entry_tokens & aliases)


def extract_saved_source_preferences(
    markdown: str | None,
    source_category_config: dict[str, dict[str, Any]],
) -> dict[str, list[str]]:
    """Find exact configured source preferences that the user saved in Sales memory."""
    if not markdown:
        return {}
    preferences: dict[str, list[str]] = {}
    for entry in summarize_user_context(markdown).get("entries", []):
        if not isinstance(entry, str) or ":" not in entry:
            continue
        section_name, _ = entry.split(":", 1)
        section_has_source_hint = source_preference_section_name(section_name)
        if NEGATIVE_SOURCE_PREFERENCE_RE.search(entry):
            continue
        normalized_entry = normalize_app_name(entry)
        for category_id, metadata in source_category_config.items():
            label = str(metadata.get("label") or category_id)
            if not section_has_source_hint and not entry_mentions_source_category(
                entry,
                category_id,
                label,
            ):
                continue
            for preferred_app in preferred_source_routes(metadata):
                preferred_app_name = str(preferred_app)
                if normalize_app_name(preferred_app_name) not in normalized_entry:
                    continue
                category_preferences = preferences.setdefault(category_id, [])
                if preferred_app_name not in category_preferences:
                    category_preferences.append(preferred_app_name)
    return preferences


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
    except OSError as exc:
        payload["status"] = "unreadable"
        payload["error"] = str(exc)
        return payload
    except UnicodeDecodeError as exc:
        payload["status"] = "unreadable"
        payload["error"] = f"utf-8 decode failed: {exc}"
        return payload

    encoded_len = len(text.encode("utf-8"))
    payload.update(
        {
            "status": "present",
            "bytes": encoded_len,
            "sha256": sha256_text(text),
            "mtime": file_mtime(path),
            "sections": extract_sections(text, sections),
        }
    )
    payload["content"] = text
    if encoded_len > max_context_bytes:
        payload["raw_content_exceeds_compat_limit"] = (
            f"{encoded_len} > {max_context_bytes}"
        )
    return payload


def read_json_payload(path: Path, max_context_bytes: int) -> dict[str, Any]:
    payload = read_text_payload(path, max_context_bytes=max_context_bytes, sections=[])
    payload["data"] = None
    if payload["status"] != "present":
        return payload
    try:
        payload["data"] = json.loads(payload["content"] or path.read_text(encoding="utf-8"))
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


def context_gap_note_template() -> str:
    return markdown_template_from_onboarding_reference("Context Gap Note")


ONBOARDING_STEP_DEFINITIONS = (
    {
        "id": "start_sales_onboarding",
        "label": "Orientation",
        "phrase": "orienting you to Sales onboarding",
    },
    {
        "id": "connector_setup_confirmation",
        "label": "Connector setup/confirmation",
        "phrase": "completing Sales connector setup and source confirmation",
    },
    {
        "id": "sales_automation_setup",
        "label": "Sales automation setup",
        "phrase": "setting up Sales automations and context discovery",
        "parallel_continuation": True,
    },
    {
        "id": "first_hero_prompt",
        "label": "First hero prompt",
        "phrase": "choosing and trying the first Sales hero prompt",
    },
    {
        "id": "other_hero_prompts",
        "label": "Other hero prompts",
        "phrase": "trying the remaining guided Sales workflows",
    },
)

NEXT_ONBOARDING_ACTION_PHRASES = {
    step["id"]: step["phrase"] for step in ONBOARDING_STEP_DEFINITIONS
}
WEEKLY_DISCOVERY_AUTOMATION_ID = "weekly_sales_company_research"
DAILY_TIPS_AUTOMATION_ID = "daily_sales_tips"
SCHEDULED_HELP_AUTOMATION_IDS = [DAILY_TIPS_AUTOMATION_ID]
ONBOARDING_AUTOMATION_IDS = [
    WEEKLY_DISCOVERY_AUTOMATION_ID,
    *SCHEDULED_HELP_AUTOMATION_IDS,
]
USER_FACING_SKILLS = (
    "analyze-account-signals",
    "build-competitive-brief",
    "follow-up-after-call",
    "suggest-sales-next-step",
    "enrich-company-and-contact-data",
    "plan-deal-strategy",
    "find-key-internal-sources",
    "prepare-for-meeting",
    "prioritize-accounts",
    "find-customer-quotes",
    "review-forecast",
    "get-rep-call-feedback",
    "review-rep-call-trends",
    "build-business-case",
)
HELPER_OR_ROUTER_SKILLS = {"salesforce", "hubspot", "zoominfo", "user-context", "index"}
CORE_ONBOARDING_SKILLS = (
    "prepare-for-meeting",
    "follow-up-after-call",
    "prioritize-accounts",
)
POST_COMPLETION_GUIDED_SKILLS = (
    "analyze-account-signals",
    "plan-deal-strategy",
    "review-forecast",
    "build-competitive-brief",
    "find-customer-quotes",
    "build-business-case",
    "enrich-company-and-contact-data",
    "find-key-internal-sources",
    "get-rep-call-feedback",
    "review-rep-call-trends",
    "suggest-sales-next-step",
)
RESOLVED_TASK_STATUSES = {
    "accepted_fallback_installed",
    "complete",
    "complete_with_fallback_automation",
    "completed",
    "completed_with_defaults",
    "declined",
    "deferred",
    "deferred_environment_api_limitations",
    "done",
    "fallback_weekday_check_in_installed",
    "installed_fallback_current_thread",
    "not_applicable",
    "skipped",
    "skipped_for_now",
}

ONBOARDING_RESOLVED_SETUP_DISPOSITIONS = {
    "declined",
    "deferred",
    "deferred_environment_api_limitations",
    "not_applicable",
    "skipped",
    "skipped_for_now",
    "unavailable",
}

FULL_AUTOMATION_READY_STATUSES = {"active", "installed", "ready", "verified"}
FALLBACK_AUTOMATION_READY_STATUSES = {
    "accepted_fallback_installed",
    "complete_with_fallback_automation",
    "fallback_daily_sales_tips_installed",
    "fallback_weekday_check_in_installed",
    "installed_fallback_current_thread",
}
AUTOMATION_READBACK_READY_STATUSES = {
    "clean",
    "read_back",
    "readback_verified",
    "verified",
}
TARGET_THREAD_READY_STATUSES = {
    "pinned",
    "ready",
    "verified",
    "verified_pinned",
}


def next_onboarding_action(onboarding_progress: dict[str, Any]) -> dict[str, str | None]:
    task_list = onboarding_progress.get("task_list")
    if not isinstance(task_list, list):
        return {
            "id": None,
            "label": "Finish Sales onboarding",
            "phrase": "finishing Sales onboarding",
        }
    for task in task_list:
        if not isinstance(task, dict):
            continue
        status = str(task.get("status") or "").casefold()
        if status in RESOLVED_TASK_STATUSES:
            continue
        if (
            task.get("parallel_continuation")
            and status == "in_progress"
            and not task.get("action_required")
        ):
            continue
        task_id = str(task.get("id") or "")
        label = str(task.get("label") or "Finish Sales onboarding")
        task_phrase = task.get("phrase")
        return {
            "id": task_id or None,
            "label": label,
            "phrase": (
                task_phrase
                if isinstance(task_phrase, str) and task_phrase
                else NEXT_ONBOARDING_ACTION_PHRASES.get(
                    task_id,
                    label[:1].lower() + label[1:] if label else "finishing Sales onboarding",
                )
            ),
        }
    return {
        "id": None,
        "label": "Finish Sales onboarding",
        "phrase": "finishing Sales onboarding",
    }


def ordinary_onboarding_cta_template(next_action: dict[str, str | None]) -> str:
    template = markdown_template_from_onboarding_reference("Ordinary Workflow Onboarding CTA")
    return template


def core_onboarding_reminder_template(next_action: dict[str, str | None]) -> str:
    template = markdown_template_from_onboarding_reference("Core Onboarding Reminder")
    phrase = next_action.get("phrase") or next_action.get("label") or "finishing Sales core setup"
    return template.replace("{next_core_action}", str(phrase))


def parse_source_category_config() -> dict[str, dict[str, Any]]:
    if not SOURCE_CATEGORY_CONFIG_REFERENCE.exists():
        return {}
    config = json.loads(SOURCE_CATEGORY_CONFIG_REFERENCE.read_text(encoding="utf-8"))
    categories = config.get("categories") if isinstance(config, dict) else None
    if not isinstance(categories, dict):
        return {}
    catalog: dict[str, dict[str, Any]] = {}
    for category_id, raw_metadata in categories.items():
        if not isinstance(raw_metadata, dict):
            continue
        preferred_apps = raw_metadata.get("preferred_apps")
        preferred_plugins = raw_metadata.get("preferred_plugins")
        relevant_skills = raw_metadata.get("relevant_skills")
        metadata: dict[str, Any] = {
            "label": raw_metadata.get("label") or category_id,
            "preferred_plugins": preferred_plugins
            if isinstance(preferred_plugins, list)
            else [],
            "preferred_apps": preferred_apps if isinstance(preferred_apps, list) else [],
            "relevant_skills": relevant_skills if isinstance(relevant_skills, list) else [],
        }
        catalog[category_id] = metadata
    return catalog


def normalize_app_name(value: Any) -> str:
    return re.sub(r"[^a-z0-9]+", "", str(value or "").casefold())


def preferred_source_routes(metadata: dict[str, Any]) -> list[str]:
    routes = [
        *[str(plugin) for plugin in metadata.get("preferred_plugins") or []],
        *[str(app) for app in metadata.get("preferred_apps") or []],
    ]
    return list(dict.fromkeys(route for route in routes if route))


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
            return "sales_vendored_helper"
        return "direct_tool"
    if source_kind == "manual":
        return "manual"
    return None


def default_runtime_action(source_kind: str | None, skill_surface: str | None) -> str | None:
    if source_kind == "plugin":
        return "use_plugin_owned_skill_or_tools"
    if source_kind in {"app", "connector"}:
        if skill_surface == "sales_vendored_helper":
            return "use_connector_or_app_with_sales_helper_guidance"
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
        elif isinstance(raw_entry.get("manual"), dict):
            source_kind = "manual"
        elif entry.get("status") == "active" and entry.get("preferred"):
            source_kind = "connector"

    if source_kind:
        entry["source_kind"] = source_kind

    for key in ("plugin", "app", "connector", "manual"):
        compact = compact_mapping(raw_entry.get(key))
        if compact is not None:
            entry[key] = compact

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


def active_plugin_route_present(confirmation: dict[str, Any]) -> bool:
    if confirmation.get("source_kind") == "plugin":
        return True
    routes = confirmation.get("routes")
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


def plugin_route_candidate(raw_entry: dict[str, Any], entry: dict[str, Any]) -> str | None:
    for value in (
        entry.get("preferred"),
        raw_entry.get("preferred"),
        raw_entry.get("label"),
    ):
        if isinstance(value, str) and value:
            return value
    plugin = raw_entry.get("plugin")
    if isinstance(plugin, str) and plugin:
        return plugin
    if isinstance(plugin, dict):
        for key in ("name", "id"):
            value = plugin.get(key)
            if isinstance(value, str) and value:
                return value
    return None


def list_from_inventory(inventory: dict[str, Any], *keys: str) -> list[str]:
    values: list[str] = []
    for key in keys:
        raw = inventory.get(key)
        if isinstance(raw, list):
            values.extend(str(item) for item in raw if isinstance(item, str) and item)
    return values


def first_matching_app(preferred_apps: list[str], candidates: set[str]) -> str | None:
    for app in preferred_apps:
        if normalize_app_name(app) in candidates:
            return app
    return None


def matching_apps(preferred_apps: list[str], candidates: set[str]) -> list[str]:
    return [app for app in preferred_apps if normalize_app_name(app) in candidates]


def missing_source_it_options(preferred_apps: list[str], category_id: str = "") -> list[str]:
    source_list = ", ".join(preferred_apps) if preferred_apps else "a matching source"
    if category_id == "data_enrichment":
        return [
            (
                "Ask IT or a workspace admin whether Codex access can be enabled for "
                f"one of: {source_list}."
            )
        ]
    return [
        f"Ask IT or a workspace admin to install or enable one of: {source_list}.",
        "Use exported, pasted, or manually supplied context for the current workflow.",
    ]


def normalize_connector_confirmation_entry(
    category_id: str,
    metadata: dict[str, Any],
    raw_entry: Any,
    inventory: dict[str, Any],
) -> dict[str, Any]:
    label = metadata.get("label") or category_id
    preferred_apps = [str(app) for app in metadata.get("preferred_apps") or []]
    preferred_plugins = [str(plugin) for plugin in metadata.get("preferred_plugins") or []]
    preferred_routes = preferred_source_routes(metadata)
    base: dict[str, Any] = {
        "label": label,
        "preferred_apps": preferred_apps,
        "state_scope": "onboarding_only_not_durable_connector_readiness",
        "workflow_time_behavior": "attempt_actual_reads_only_when_a_workflow_needs_the_source",
        "eager_read": False,
    }
    if preferred_plugins:
        base["preferred_plugins"] = preferred_plugins

    if isinstance(raw_entry, dict):
        status = str(raw_entry.get("status") or "").casefold()
        if status == "available":
            status = "needs_confirmation"
        if status in {"selected", "selected_for_verification", "needs_setup_probe"}:
            status = "needs_confirmation"
        if status == "not_available":
            status = "missing"
        if status in ONBOARDING_RESOLVED_SETUP_DISPOSITIONS:
            entry = dict(base)
            entry["status"] = status
            entry["setup_action"] = "none_try_on_use"
            copy_configured_route_metadata(entry, raw_entry, metadata)
            return entry
        if status in {"active", "needs_confirmation", "missing"}:
            entry = dict(base)
            entry["status"] = status
            if status == "active":
                preferred = raw_entry.get("preferred") or raw_entry.get("app")
                if preferred:
                    entry["preferred"] = str(preferred)
                fallback = raw_entry.get("fallback") or raw_entry.get("backup")
                if fallback:
                    entry["fallback"] = str(fallback)
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
                        entry = dict(base)
                        entry["status"] = "needs_confirmation"
                        entry["candidates"] = preferred_routes
                        entry["setup_action"] = "run_plugin_first_source_setup"
                        entry["setup_note"] = (
                            "plugin_route_requires_plugin_install_and_surface_evidence_before_active"
                        )
                if entry.get("status") == "active":
                    if raw_entry.get("confirmed_at"):
                        entry["confirmed_at"] = raw_entry["confirmed_at"]
                    entry["setup_action"] = "none_try_on_use"
                    copy_configured_route_metadata(entry, raw_entry, metadata)
                    if unproven_plugin_route(entry):
                        entry = dict(base)
                        entry["status"] = "needs_confirmation"
                        entry["candidates"] = preferred_routes
                        entry["setup_action"] = "run_plugin_first_source_setup"
                        entry["setup_note"] = (
                            "plugin_route_requires_plugin_install_and_surface_evidence_before_active"
                        )
            elif status == "needs_confirmation":
                candidates = raw_entry.get("candidates")
                if not isinstance(candidates, list) or not candidates:
                    selected = raw_entry.get("preferred") or raw_entry.get("app")
                    if selected:
                        candidates = [str(selected)]
                    else:
                        candidates = preferred_routes
                entry["candidates"] = [str(candidate) for candidate in candidates]
                selected = raw_entry.get("preferred") or raw_entry.get("app")
                if selected:
                    entry["preferred"] = str(selected)
                    entry["setup_action"] = "verify_selected_app_with_simple_read"
                else:
                    entry["setup_action"] = "ask_user_to_choose_preferred_app"
                copy_configured_route_metadata(entry, raw_entry, metadata)
            else:
                options = raw_entry.get("options")
                if not isinstance(options, list) or not options:
                    options = preferred_routes
                entry["options"] = [str(option) for option in options]
                entry["it_admin_options"] = raw_entry.get(
                    "it_admin_options"
                ) or missing_source_it_options(entry["options"], category_id)
                entry["setup_action"] = "explain_workflow_impact_and_it_admin_options"
                copy_configured_route_metadata(entry, raw_entry, metadata)
            return entry

    configured_apps = {
        normalize_app_name(app)
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
    available_matches = matching_apps(preferred_apps, configured_apps)
    if available_matches:
        entry = dict(base)
        entry.update(
            {
                "status": "needs_confirmation",
                "candidates": available_matches,
                "setup_action": "run_plugin_first_source_setup",
            }
        )
        return entry

    if inventory:
        entry = dict(base)
        entry.update(
            {
                "status": "missing",
                "options": preferred_routes,
                "it_admin_options": missing_source_it_options(preferred_routes, category_id),
                "setup_action": "run_plugin_first_source_setup",
            }
        )
        return entry

    entry = dict(base)
    entry.update(
        {
            "status": "needs_confirmation",
            "candidates": preferred_routes,
            "setup_action": "run_plugin_first_source_setup",
        }
    )
    return entry


def build_connector_confirmation(
    source_category_config: dict[str, dict[str, Any]],
    onboarding_data: Any,
) -> dict[str, dict[str, Any]]:
    raw_confirmation = (
        onboarding_data.get("connector_confirmation") if isinstance(onboarding_data, dict) else None
    )
    if not isinstance(raw_confirmation, dict):
        raw_confirmation = {}
    inventory = (
        onboarding_data.get("connector_inventory") if isinstance(onboarding_data, dict) else {}
    )
    if not isinstance(inventory, dict):
        inventory = {}

    confirmation: dict[str, dict[str, Any]] = {}
    raw_preferences = raw_confirmation.get("preferences")
    if not isinstance(raw_preferences, dict):
        raw_preferences = {}
    for category_id, metadata in source_category_config.items():
        raw_entry = raw_confirmation.get(category_id)
        if raw_entry is None:
            raw_entry = raw_preferences.get(category_id)
        confirmation[category_id] = normalize_connector_confirmation_entry(
            category_id,
            metadata,
            raw_entry,
            inventory,
        )
    return confirmation


def compact_source_categories(
    source_category_config: dict[str, dict[str, Any]],
    connector_confirmation: dict[str, dict[str, Any]],
    saved_source_preferences: dict[str, list[str]] | None = None,
) -> dict[str, Any]:
    categories: dict[str, dict[str, Any]] = {}
    for category_id, metadata in source_category_config.items():
        confirmation = connector_confirmation.get(category_id, {})
        status = str(confirmation.get("status") or "unknown").casefold()
        preferred_apps = [str(app) for app in metadata.get("preferred_apps") or []]
        preferred_plugins = [str(plugin) for plugin in metadata.get("preferred_plugins") or []]
        preferred_routes = preferred_source_routes(metadata)
        entry: dict[str, Any] = {
            "label": metadata.get("label") or category_id,
            "status": status,
        }
        if status != "active":
            if preferred_plugins:
                entry["preferred_plugins"] = preferred_plugins
            entry["preferred_apps"] = preferred_apps
        if confirmation.get("preferred") is not None:
            entry["preferred"] = confirmation.get("preferred")
        if confirmation.get("fallback") is not None:
            entry["fallback"] = confirmation.get("fallback")
        if confirmation.get("candidates"):
            entry["candidates"] = confirmation.get("candidates")
        if confirmation.get("options"):
            entry["options"] = confirmation.get("options")
        for key in (
            "source_kind",
            "skill_surface",
            "plugin",
            "app",
            "connector",
            "manual",
            "installed_evidence",
            "plugin_install_evidence",
            "app_surface_evidence",
            "connector_surface_evidence",
            "skill_surface_evidence",
            "tool_surface_evidence",
            "runtime_action",
            "routes",
            "setup_note",
        ):
            if confirmation.get(key) is not None:
                entry[key] = confirmation.get(key)
        helper_skills = metadata.get("relevant_skills") or []
        if helper_skills and confirmation.get("source_kind") != "plugin":
            entry["helper_skills"] = helper_skills
            entry["helper_skills_apply_when"] = ["app", "connector"]
        if status != "active" or confirmation.get("setup_action") != "none_try_on_use":
            entry["setup_action"] = confirmation.get("setup_action")
        if confirmation.get("it_admin_options"):
            entry["it_admin_options"] = confirmation.get("it_admin_options")

        saved_preferences = list((saved_source_preferences or {}).get(category_id, []))
        explicit_preference = entry.get("preferred")
        if isinstance(explicit_preference, str) and explicit_preference in preferred_routes:
            saved_preferences.append(explicit_preference)
        saved_preferences = list(dict.fromkeys(saved_preferences))
        plugin_preference_order = list(dict.fromkeys([*saved_preferences, *preferred_routes]))
        active_plugin_route = status == "active" and active_plugin_route_present(confirmation)
        if plugin_preference_order and status in PLUGIN_FIRST_SETUP_STATUSES and not active_plugin_route:
            previous_setup_action = entry.get("setup_action")
            entry["plugin_preference_order"] = plugin_preference_order
            if saved_preferences:
                entry["saved_source_preferences"] = saved_preferences
            entry["setup_action"] = "run_plugin_first_source_setup"
            if previous_setup_action and previous_setup_action != entry["setup_action"]:
                entry["fallback_setup_action"] = previous_setup_action
            entry["setup_recovery"] = {
                "type": "plugin_first_source_setup",
                "preferred_sources": plugin_preference_order,
                "plugin_preferred_over": "active_or_available_app_connector_routes",
                "candidate_match": "candidate_name_display_id_or_app_connector_id_matches_preferred_source",
                "candidate_lookup": "functions.list_available_plugins_to_install",
                "install_request": "functions.request_plugin_install_after_user_approval",
                "retry_policy": "retry_on_future_workflows_after_failed_setup_or_pending_visibility",
                "decline_scope": "suppress_current_workflow_only_unless_user_saves_do_not_use",
                "fallback": "use_existing_app_connector_route_or_manual_context_when_no_plugin_candidate_or_user_declines",
            }
        categories[category_id] = entry
    return {
        "resolution": "plugin_or_app_or_connector_then_manual_context",
        "has_setup_gaps": any(
            str(entry.get("status") or "").casefold() != "active"
            or entry.get("setup_action") not in {None, "none_try_on_use"}
            for entry in categories.values()
        ),
        "categories": categories,
    }


def parse_automation_config() -> dict[str, dict[str, Any]]:
    if not AUTOMATION_CONFIG_REFERENCE.exists():
        return {}
    text = AUTOMATION_CONFIG_REFERENCE.read_text(encoding="utf-8")
    if "## Default Automations" in text:
        text = text.split("## Default Automations", 1)[1]
    matches = list(re.finditer(r"(?m)^`([a-z0-9_]+)`\s*$", text))
    catalog: dict[str, dict[str, Any]] = {}
    for index, match in enumerate(matches):
        automation_id = match.group(1)
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        block = text[match.end() : end]
        entry: dict[str, Any] = {"id": automation_id}
        for field, key in (
            ("Name", "name"),
            ("Frequency", "frequency"),
            ("Instructions", "instructions"),
        ):
            field_match = re.search(rf"(?m)^- {re.escape(field)}:\s*(.+?)\s*$", block)
            if field_match:
                value = field_match.group(1).strip()
                if key in {"name", "target_thread_title", "frequency"}:
                    value = value.rstrip(".")
                entry[key] = value
        if "name" in entry:
            entry["target_thread_title"] = entry["name"]
        if all(
            key in entry for key in ("name", "target_thread_title", "frequency", "instructions")
        ):
            catalog[automation_id] = entry
    return catalog


def compact_automation_state(
    automation_config: dict[str, dict[str, Any]],
    onboarding_data: Any,
) -> dict[str, dict[str, Any]]:
    raw_automations = (
        onboarding_data.get("automations") if isinstance(onboarding_data, dict) else {}
    )
    if not isinstance(raw_automations, dict):
        raw_automations = {}
    automations: dict[str, dict[str, Any]] = {}
    for automation_id, config in automation_config.items():
        raw_state = raw_automations.get(automation_id)
        if not isinstance(raw_state, dict):
            raw_state = {}
        automations[automation_id] = {
            "status": raw_state.get("status") or "not_configured",
            "frequency": config.get("frequency"),
        }
        if raw_state.get("initial_run_status") is not None:
            automations[automation_id]["initial_run_status"] = raw_state.get(
                "initial_run_status"
            )
    return automations


def workflow_keys(records: Any) -> set[str]:
    keys: set[str] = set()
    if not isinstance(records, list):
        return keys
    for record in records:
        if not isinstance(record, dict):
            continue
        for field in ("workflow", "key"):
            value = record.get(field)
            if isinstance(value, str) and value:
                keys.add(value)
    return keys


def skill_experience_state(onboarding_data: Any) -> dict[str, dict[str, Any]]:
    if not isinstance(onboarding_data, dict):
        return {}
    raw_state = onboarding_data.get("skill_experience")
    if not isinstance(raw_state, dict):
        return {}
    state: dict[str, dict[str, Any]] = {}
    for skill, raw_entry in raw_state.items():
        if isinstance(skill, str) and isinstance(raw_entry, dict):
            state[skill] = raw_entry
    return state


def skill_experience_entry(onboarding_data: Any, skill: str) -> dict[str, Any]:
    return skill_experience_state(onboarding_data).get(skill, {})


def skill_has_been_introduced(onboarding_data: Any, skill: str) -> bool:
    entry = skill_experience_entry(onboarding_data, skill)
    if entry.get("introduced_at"):
        return True
    return str(entry.get("status") or "").casefold() in {"introduced", "tried", "accepted"}


def skill_has_been_tried(onboarding_data: Any, skill: str) -> bool:
    entry = skill_experience_entry(onboarding_data, skill)
    if entry.get("first_tried_at"):
        return True
    return str(entry.get("status") or "").casefold() in {"tried", "accepted", "completed"}


def skill_has_been_dismissed(onboarding_data: Any, skill: str) -> bool:
    entry = skill_experience_entry(onboarding_data, skill)
    if entry.get("dismissed_at"):
        return True
    return str(entry.get("status") or "").casefold() in {"declined", "deferred", "skipped"}


def completed_skill_experience_keys(onboarding_data: Any) -> set[str]:
    return {
        skill
        for skill in skill_experience_state(onboarding_data)
        if skill_has_been_tried(onboarding_data, skill)
    }


def deferred_skill_experience_keys(onboarding_data: Any) -> set[str]:
    return {
        skill
        for skill in skill_experience_state(onboarding_data)
        if skill_has_been_dismissed(onboarding_data, skill)
    }


def build_current_skill_experience(
    workflow: str,
    request_mode: str,
    onboarding_data: Any,
) -> dict[str, Any]:
    skill = workflow or "ordinary"
    entry = skill_experience_entry(onboarding_data, skill)
    user_facing = skill in USER_FACING_SKILLS
    introduced = skill_has_been_introduced(onboarding_data, skill)
    tried = skill_has_been_tried(onboarding_data, skill)
    if request_mode in {"direct_onboarding_status", "guided_onboarding_workflow"}:
        cta_owner = "onboarding"
    elif user_facing:
        cta_owner = "skill"
    else:
        cta_owner = "none"
    intro_eligible = (
        user_facing
        and not introduced
        and request_mode in {"ordinary_workflow", "guided_onboarding_workflow"}
    )
    return {
        "skill": skill,
        "user_facing": user_facing,
        "helper_or_router": skill in HELPER_OR_ROUTER_SKILLS,
        "introduced": introduced,
        "tried": tried,
        "intro_eligible": intro_eligible,
        "cta_owner": cta_owner,
    }


def onboarding_step_block(onboarding_data: Any, key: str) -> dict[str, Any]:
    if not isinstance(onboarding_data, dict):
        return {}
    block = onboarding_data.get(key)
    return block if isinstance(block, dict) else {}


def raw_step_status(onboarding_data: Any, key: str) -> str:
    block = onboarding_step_block(onboarding_data, key)
    return str(block.get("status") or "").casefold()


def standard_block_status(onboarding_data: Any, key: str) -> str:
    status = raw_step_status(onboarding_data, key)
    if status in RESOLVED_TASK_STATUSES | {
        "attached",
        "confirmed",
        "introduced",
        "saved",
        "selected",
        "shown",
    }:
        return "completed"
    if status in {
        "active",
        "drafted",
        "in_progress",
        "offered",
        "pending_approval",
        "prompted",
        "ready_for_review",
        "reviewing",
        "running",
        "started",
        "suggested",
    }:
        return "in_progress"
    return "pending"


def orientation_progress_status(onboarding_data: Any) -> str:
    if not isinstance(onboarding_data, dict):
        return "pending"
    status = raw_step_status(onboarding_data, "orientation")
    if status in {"complete", "completed", "shown"}:
        return "completed"
    if onboarding_data.get("last_orientation_shown"):
        return "completed"
    if status in {"active", "in_progress", "started"}:
        return "in_progress"
    return "pending"


def meeting_prep_demo_status(onboarding_data: Any, resolved_workflows: set[str]) -> str:
    if skill_has_been_tried(onboarding_data, "prepare-for-meeting"):
        return "completed"
    if "prepare-for-meeting" in resolved_workflows:
        return "completed"
    run_status = standard_block_status(onboarding_data, "meeting_prep_run")
    if run_status != "pending":
        return run_status
    prompt_status = standard_block_status(onboarding_data, "meeting_prep_prompt")
    if prompt_status != "pending":
        return "in_progress"
    last_suggested = onboarding_step_block(onboarding_data, "last_skill_suggested")
    key = str(last_suggested.get("key") or last_suggested.get("workflow") or "").casefold()
    if key == "prepare-for-meeting":
        return "in_progress"
    return "pending"


def prep_review_status(onboarding_data: Any, resolved_workflows: set[str]) -> str:
    status = standard_block_status(onboarding_data, "first_guided_workflow_review")
    if status != "pending":
        return status
    if "prepare-for-meeting" in resolved_workflows:
        return "in_progress"
    return "pending"


def plugin_memory_status(onboarding_data: Any, resolved_workflows: set[str]) -> str:
    explicit_status = standard_block_status(onboarding_data, "accepted_preference_memory")
    if explicit_status != "pending":
        return explicit_status
    intro_status = standard_block_status(onboarding_data, "plugin_memory_intro")
    if intro_status == "completed":
        return "in_progress"
    if prep_review_status(onboarding_data, resolved_workflows) == "completed":
        return "in_progress"
    return "pending"


def sales_automations_intro_status(
    onboarding_data: Any,
    automation_config: dict[str, dict[str, Any]],
    resolved_workflows: set[str],
) -> str:
    if standard_block_status(onboarding_data, "automations_intro") == "completed":
        return "completed"
    automation_status = sales_automations_status(onboarding_data, automation_config)
    if automation_status != "pending":
        return "completed"
    if plugin_memory_status(onboarding_data, resolved_workflows) == "completed":
        return "in_progress"
    return "pending"


def sales_automations_setup_status(
    onboarding_data: Any,
    automation_config: dict[str, dict[str, Any]],
    resolved_workflows: set[str],
) -> str:
    automation_status = sales_automations_status(onboarding_data, automation_config)
    if automation_status != "pending":
        return automation_status
    if (
        sales_automations_intro_status(
            onboarding_data,
            automation_config,
            resolved_workflows,
        )
        == "completed"
    ):
        return "in_progress"
    return "pending"


def call_followup_intro_status(onboarding_data: Any, resolved_workflows: set[str]) -> str:
    if skill_has_been_introduced(onboarding_data, "follow-up-after-call"):
        return "completed"
    if "follow-up-after-call" in resolved_workflows:
        return "completed"
    if standard_block_status(onboarding_data, "call_followup_intro") == "completed":
        return "completed"
    return "pending"


def call_followup_status(onboarding_data: Any, resolved_workflows: set[str]) -> str:
    if skill_has_been_tried(onboarding_data, "follow-up-after-call"):
        return "completed"
    if "follow-up-after-call" in resolved_workflows:
        return "completed"
    if call_followup_intro_status(onboarding_data, resolved_workflows) == "completed":
        return "in_progress"
    return "pending"


def internal_navigation_intro_status(onboarding_data: Any, resolved_workflows: set[str]) -> str:
    if skill_has_been_introduced(onboarding_data, "find-key-internal-sources"):
        return "completed"
    if "find-key-internal-sources" in resolved_workflows:
        return "completed"
    if standard_block_status(onboarding_data, "internal_navigation_intro") == "completed":
        return "completed"
    return "pending"


def internal_navigation_status(onboarding_data: Any, resolved_workflows: set[str]) -> str:
    if skill_has_been_tried(onboarding_data, "find-key-internal-sources"):
        return "completed"
    if "find-key-internal-sources" in resolved_workflows:
        return "completed"
    if internal_navigation_intro_status(onboarding_data, resolved_workflows) == "completed":
        return "in_progress"
    return "pending"


def connector_confirmation_status(
    onboarding_data: Any,
    source_category_config: dict[str, dict[str, Any]],
) -> str:
    if not isinstance(onboarding_data, dict):
        return "pending"
    raw_confirmation = onboarding_data.get("connector_confirmation")
    inventory = onboarding_data.get("connector_inventory")
    has_classification_input = (
        isinstance(raw_confirmation, dict)
        and bool(raw_confirmation)
        or isinstance(inventory, dict)
        and bool(inventory)
    )
    if not has_classification_input:
        return "pending"
    normalized_confirmation = build_connector_confirmation(source_category_config, onboarding_data)
    statuses: list[str] = []
    for category_id in source_category_config:
        status = ""
        normalized_entry = normalized_confirmation.get(category_id)
        if isinstance(normalized_entry, dict):
            status = str(normalized_entry.get("status") or "").casefold()
        if status == "available":
            status = "needs_confirmation"
        if status == "not_available":
            status = "missing"
        statuses.append(status)
    if statuses and all(
        status
        in {
            "active",
            "needs_confirmation",
            "missing",
            "declined",
            "deferred",
            "deferred_environment_api_limitations",
            "skipped",
            "not_applicable",
            "skipped_for_now",
            "unavailable",
        }
        for status in statuses
    ):
        return "completed"
    if any(status for status in statuses):
        return "in_progress"
    return "pending"


def connector_confirmation_action_required(
    onboarding_data: Any,
    source_category_config: dict[str, dict[str, Any]] | None = None,
) -> bool:
    if not isinstance(onboarding_data, dict):
        return False
    if source_category_config:
        if connector_confirmation_status(onboarding_data, source_category_config) == "pending":
            return False
        entries = build_connector_confirmation(source_category_config, onboarding_data).values()
    else:
        raw_confirmation = onboarding_data.get("connector_confirmation")
        if not isinstance(raw_confirmation, dict):
            return False
        entries = raw_confirmation.values()
    for entry in entries:
        if not isinstance(entry, dict):
            continue
        status = str(entry.get("status") or "").casefold()
        if status in {"available", "needs_confirmation", "missing", "not_available"}:
            return True
    return False


def source_questions_status(
    onboarding_data: Any,
    source_category_config: dict[str, dict[str, Any]],
) -> str:
    confirmation_status = connector_confirmation_status(onboarding_data, source_category_config)
    if confirmation_status == "pending":
        return "pending"
    if connector_confirmation_action_required(onboarding_data, source_category_config):
        return "in_progress"
    return "completed"


def introduce_meeting_prep_status(
    onboarding_data: Any,
    source_category_config: dict[str, dict[str, Any]],
) -> str:
    if skill_has_been_introduced(onboarding_data, "prepare-for-meeting"):
        return "completed"
    if standard_block_status(onboarding_data, "meeting_prep_intro") == "completed":
        return "completed"
    if standard_block_status(onboarding_data, "meeting_prep_prompt") != "pending":
        return "completed"
    if standard_block_status(onboarding_data, "meeting_prep_run") != "pending":
        return "completed"
    if source_questions_status(onboarding_data, source_category_config) == "completed":
        return "in_progress"
    return "pending"


def hero_prompt_choice_status(onboarding_data: Any) -> str:
    status = standard_block_status(onboarding_data, "hero_prompt_choice")
    if status != "pending":
        return status
    choice = onboarding_step_block(onboarding_data, "hero_prompt_choice")
    if choice.get("selected_skill") or choice.get("selected_anchor") or choice.get("last_shown"):
        return "in_progress"
    if standard_block_status(onboarding_data, "meeting_prep_prompt") != "pending":
        return "completed"
    return "pending"


def selected_first_hero_skill(onboarding_data: Any) -> str | None:
    choice = onboarding_step_block(onboarding_data, "hero_prompt_choice")
    selected = choice.get("selected_skill")
    if isinstance(selected, str) and selected in CORE_ONBOARDING_SKILLS:
        return selected
    prompt = onboarding_step_block(onboarding_data, "meeting_prep_prompt")
    if prompt.get("selected_prompt") or prompt.get("meeting_ref"):
        return "prepare-for-meeting"
    return None


def core_hero_skill_is_resolved(onboarding_data: Any, skill: str) -> bool:
    return skill_has_been_tried(onboarding_data, skill) or skill_has_been_dismissed(
        onboarding_data, skill
    )


def remaining_core_hero_skills(onboarding_data: Any) -> list[str]:
    return [
        skill
        for skill in CORE_ONBOARDING_SKILLS
        if not core_hero_skill_is_resolved(onboarding_data, skill)
    ]


def hero_prompt_choice_summary(onboarding_data: Any) -> dict[str, Any]:
    remaining = remaining_core_hero_skills(onboarding_data)
    resolved = [skill for skill in CORE_ONBOARDING_SKILLS if skill not in remaining]
    choice = onboarding_step_block(onboarding_data, "hero_prompt_choice")
    return {
        "core_skill_order": list(CORE_ONBOARDING_SKILLS),
        "resolved_core_skills": resolved,
        "remaining_core_skills": remaining,
        "suggested_options": remaining[:3],
        "current_offer_label": (
            "Choose Your First Sales Demo"
            if len(remaining) == len(CORE_ONBOARDING_SKILLS)
            else "Choose Your Next Sales Demo"
        ),
        "selection_state": choice,
    }


def compact_hero_prompt_choice_summary(onboarding_data: Any) -> dict[str, Any]:
    summary = hero_prompt_choice_summary(onboarding_data)
    choice = summary.get("selection_state")
    compact: dict[str, Any] = {
        "current_offer_label": summary.get("current_offer_label"),
        "resolved_core_skills": summary.get("resolved_core_skills") or [],
        "remaining_core_skills": summary.get("remaining_core_skills") or [],
        "suggested_options": summary.get("suggested_options") or [],
    }
    if isinstance(choice, dict):
        for key in ("status", "selected_skill", "selected_anchor"):
            if choice.get(key) is not None:
                compact[key] = choice[key]
    return compact


def discovery_state(onboarding_data: Any) -> dict[str, Any]:
    initial_discovery = onboarding_step_block(onboarding_data, "initial_resource_discovery")
    if initial_discovery:
        return initial_discovery
    background_discovery = onboarding_step_block(onboarding_data, "background_context_discovery")
    if background_discovery:
        return background_discovery
    return onboarding_step_block(onboarding_data, "company_context_discovery")


def resource_discovery_status(onboarding_data: Any) -> str:
    if not isinstance(onboarding_data, dict):
        return "pending"
    status = str(discovery_state(onboarding_data).get("status") or "").casefold()
    if status in {
        "complete",
        "completed",
        "declined",
        "deferred",
        "deferred_environment_api_limitations",
        "no_useful_results",
        "not_useful",
        "saved",
        "skipped",
        "skipped_for_now",
        "unavailable",
    }:
        return "completed"
    if status in {
        "active",
        "approved",
        "drafted",
        "drafting",
        "in_progress",
        "kicked_off",
        "pending_approval",
        "proposed",
        "proposal_ready",
        "ready_for_review",
        "running",
        "running_in_pinned_thread",
        "sent_to_thread",
        "started",
    }:
        return "in_progress"
    return "pending"


def resource_discovery_action_required(onboarding_data: Any) -> bool:
    status = str(discovery_state(onboarding_data).get("status") or "").casefold()
    return status in {"pending_approval", "proposed", "proposal_ready", "ready_for_review"}


def sales_automations_status(
    onboarding_data: Any,
    automation_config: dict[str, dict[str, Any]],
) -> str:
    configured_ids = [
        automation_id
        for automation_id in ONBOARDING_AUTOMATION_IDS
        if automation_id in automation_config
    ]
    if not configured_ids:
        return "completed"
    automation_status = automation_progress_status(
        onboarding_data,
        automation_config,
        automation_ids=configured_ids,
    )
    if automation_status != "completed":
        return automation_status
    if WEEKLY_DISCOVERY_AUTOMATION_ID not in configured_ids:
        return "completed"
    discovery_status = resource_discovery_status(onboarding_data)
    if discovery_status in {"completed", "in_progress"}:
        return "completed"
    return "pending"


def connector_setup_confirmation_status(
    onboarding_data: Any,
    source_category_config: dict[str, dict[str, Any]],
) -> str:
    confirmation_status = connector_confirmation_status(onboarding_data, source_category_config)
    if confirmation_status == "pending":
        return "pending"
    if source_questions_status(onboarding_data, source_category_config) == "completed":
        return "completed"
    return "in_progress"


def sales_automation_setup_status(
    onboarding_data: Any,
    automation_config: dict[str, dict[str, Any]],
    source_category_config: dict[str, dict[str, Any]],
) -> str:
    automation_status = sales_automations_status(onboarding_data, automation_config)
    if automation_status == "completed":
        return "completed"
    if automation_status == "in_progress":
        return "in_progress"
    if standard_block_status(onboarding_data, "automations_intro") != "pending":
        return "in_progress"
    if connector_setup_confirmation_status(onboarding_data, source_category_config) == "completed":
        return "in_progress"
    return "pending"


def core_onboarding_progress_status(
    onboarding_data: Any,
    automation_config: dict[str, dict[str, Any]],
    source_category_config: dict[str, dict[str, Any]],
) -> str:
    explicit_status = standard_block_status(onboarding_data, "core_onboarding")
    connector_status = connector_setup_confirmation_status(onboarding_data, source_category_config)
    automation_status = sales_automation_setup_status(
        onboarding_data,
        automation_config,
        source_category_config,
    )
    if explicit_status == "completed":
        if connector_status == "completed" and automation_status == "completed":
            return "completed"
        return "in_progress"
    if connector_status == "completed" and automation_status == "completed":
        return "completed"
    if connector_status != "pending" or automation_status != "pending":
        return "in_progress"
    return "pending"


def first_hero_prompt_status(
    onboarding_data: Any,
    automation_config: dict[str, dict[str, Any]],
    source_category_config: dict[str, dict[str, Any]],
    resolved_workflows: set[str],
) -> str:
    resolved_core_workflows = set(CORE_ONBOARDING_SKILLS) & resolved_workflows
    if resolved_core_workflows and all(
        skill_has_been_dismissed(onboarding_data, skill) for skill in resolved_core_workflows
    ):
        return "completed"

    if "prepare-for-meeting" in resolved_core_workflows:
        run_status = meeting_prep_demo_status(onboarding_data, resolved_workflows)
    elif resolved_core_workflows:
        run_status = "completed"
    else:
        run_status = "pending"

    if run_status != "pending":
        if run_status != "completed":
            return run_status

        review_status = standard_block_status(onboarding_data, "first_guided_workflow_review")
        if review_status == "pending":
            return "in_progress"
        if review_status != "completed":
            return review_status

        memory_block = onboarding_step_block(onboarding_data, "accepted_preference_memory")
        has_memory_candidate = any(
            memory_block.get(field)
            for field in ("candidate", "proposed_preference", "preference", "summary")
        )
        memory_status = standard_block_status(onboarding_data, "accepted_preference_memory")
        if has_memory_candidate and memory_status != "completed":
            return "in_progress"
        return "completed"

    if (
        core_onboarding_progress_status(
            onboarding_data,
            automation_config,
            source_category_config,
        )
        != "completed"
    ):
        return "pending"

    choice_status = hero_prompt_choice_status(onboarding_data)
    if choice_status == "completed":
        if raw_step_status(onboarding_data, "hero_prompt_choice") in RESOLVED_TASK_STATUSES:
            return "completed"
        return "in_progress"
    if choice_status == "in_progress":
        return "in_progress"
    return "in_progress"


def other_hero_prompts_status(
    onboarding_data: Any,
    automation_config: dict[str, dict[str, Any]],
    source_category_config: dict[str, dict[str, Any]],
    resolved_workflows: set[str],
) -> str:
    first_status = first_hero_prompt_status(
        onboarding_data,
        automation_config,
        source_category_config,
        resolved_workflows,
    )
    if first_status != "completed":
        return "pending"
    resolved_core_workflows = set(CORE_ONBOARDING_SKILLS) & resolved_workflows
    if set(CORE_ONBOARDING_SKILLS).issubset(resolved_core_workflows):
        return "completed"
    if any(
        skill_has_been_introduced(onboarding_data, skill)
        or skill_has_been_tried(onboarding_data, skill)
        or skill_has_been_dismissed(onboarding_data, skill)
        for skill in CORE_ONBOARDING_SKILLS
        if skill not in resolved_core_workflows
    ):
        return "in_progress"
    return "in_progress"


def onboarding_step_status(
    step_id: str,
    onboarding_data: Any,
    automation_config: dict[str, dict[str, Any]],
    source_category_config: dict[str, dict[str, Any]],
    completed_workflows: set[str],
    resolved_workflows: set[str],
) -> str:
    if step_id == "start_sales_onboarding":
        return orientation_progress_status(onboarding_data)
    if step_id == "connector_setup_confirmation":
        return connector_setup_confirmation_status(onboarding_data, source_category_config)
    if step_id == "sales_automation_setup":
        return sales_automation_setup_status(
            onboarding_data,
            automation_config,
            source_category_config,
        )
    if step_id == "first_hero_prompt":
        return first_hero_prompt_status(
            onboarding_data,
            automation_config,
            source_category_config,
            resolved_workflows,
        )
    if step_id == "other_hero_prompts":
        return other_hero_prompts_status(
            onboarding_data,
            automation_config,
            source_category_config,
            resolved_workflows,
        )
    return "pending"


def build_onboarding_step(
    definition: dict[str, Any],
    onboarding_data: Any,
    automation_config: dict[str, dict[str, Any]],
    source_category_config: dict[str, dict[str, Any]],
    completed_workflows: set[str],
    resolved_workflows: set[str],
) -> dict[str, Any]:
    step_id = str(definition["id"])
    step = {
        "id": step_id,
        "label": definition["label"],
        "status": onboarding_step_status(
            step_id,
            onboarding_data,
            automation_config,
            source_category_config,
            completed_workflows,
            resolved_workflows,
        ),
    }
    if definition.get("parallel_continuation"):
        step["parallel_continuation"] = True
    if step_id == "connector_setup_confirmation" and connector_confirmation_action_required(
        onboarding_data,
        source_category_config,
    ):
        step["action_required"] = True
    if (
        step_id
        in {
            "sales_automation_setup",
            "first_hero_prompt",
            "other_hero_prompts",
        }
        and step["status"] == "in_progress"
    ):
        step["action_required"] = True
    if step_id == "sales_automation_setup" and resource_discovery_action_required(onboarding_data):
        step["action_required"] = True
    return step


def automation_entry_is_ready(entry: Any) -> bool:
    if not isinstance(entry, dict):
        return False
    status = str(entry.get("status") or "").casefold()
    if status in ONBOARDING_RESOLVED_SETUP_DISPOSITIONS:
        return True
    if status in FALLBACK_AUTOMATION_READY_STATUSES:
        return bool(entry.get("canonical_id") and entry.get("target_thread_id"))
    if status not in FULL_AUTOMATION_READY_STATUSES:
        return False
    if str(entry.get("kind") or "").casefold() != "heartbeat":
        return False
    if str(entry.get("readback_status") or "").casefold() not in AUTOMATION_READBACK_READY_STATUSES:
        return False
    if not all(
        entry.get(field)
        for field in ("canonical_id", "target_thread_id", "target_thread_title")
    ):
        return False
    target_status = str(entry.get("target_thread_status") or "").casefold()
    return target_status in TARGET_THREAD_READY_STATUSES or entry.get("target_thread_pinned") is True


def automation_entry_has_started(entry: Any) -> bool:
    if not isinstance(entry, dict):
        return False
    return any(
        entry.get(field)
        for field in (
            "status",
            "canonical_id",
            "target_thread_id",
            "target_thread_status",
            "last_installed",
            "last_offered",
            "cadence",
            "preferred_time",
        )
    )


def automation_progress_status(
    onboarding_data: Any,
    automation_config: dict[str, dict[str, Any]],
    automation_ids: list[str] | None = None,
) -> str:
    if not automation_config:
        return "pending"
    automations = onboarding_data.get("automations") if isinstance(onboarding_data, dict) else None
    if not isinstance(automations, dict):
        return "pending"
    configured_ids = automation_ids if automation_ids is not None else list(automation_config)
    configured_entries = [automations.get(automation_id) for automation_id in configured_ids]
    if configured_entries and all(automation_entry_is_ready(entry) for entry in configured_entries):
        return "completed"
    if any(automation_entry_has_started(entry) for entry in configured_entries):
        return "in_progress"
    return "pending"


def onboarding_is_complete_or_quiet(onboarding_status: str) -> bool:
    return onboarding_status.casefold() in {"complete", "completed", "quiet"}


def build_onboarding_progress(
    onboarding_data: Any,
    automation_config: dict[str, dict[str, Any]],
    source_category_config: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    completed_workflows = completed_skill_experience_keys(onboarding_data)
    deferred_workflows = deferred_skill_experience_keys(onboarding_data)
    resolved_workflows = completed_workflows | deferred_workflows

    task_list = [
        build_onboarding_step(
            definition,
            onboarding_data,
            automation_config,
            source_category_config,
            completed_workflows,
            resolved_workflows,
        )
        for definition in ONBOARDING_STEP_DEFINITIONS
    ]
    core_step_ids = ["connector_setup_confirmation", "sales_automation_setup"]
    core_steps = [task for task in task_list if task.get("id") in core_step_ids]
    core_remaining = [
        task
        for task in core_steps
        if str(task.get("status") or "").casefold() not in RESOLVED_TASK_STATUSES
    ]
    core_status = core_onboarding_progress_status(
        onboarding_data,
        automation_config,
        source_category_config,
    )
    if core_status == "completed":
        for task in core_steps:
            task["status"] = "completed"
            task.pop("action_required", None)
        core_remaining = []
    elif len(core_remaining) == len(core_steps) and all(
        str(task.get("status") or "").casefold() == "pending" for task in core_remaining
    ):
        core_status = "pending"

    return {
        "flow_id": "standard_sales_onboarding",
        "core_onboarding": {
            "status": core_status,
            "complete": core_status == "completed",
            "required_step_ids": core_step_ids,
            "remaining_step_ids": [str(task.get("id") or "") for task in core_remaining],
            "remaining_labels": [str(task.get("label") or "") for task in core_remaining],
            "next_action": next_onboarding_action({"task_list": core_steps}),
        },
        "core_onboarding_skills": list(CORE_ONBOARDING_SKILLS),
        "hero_prompt_choices": compact_hero_prompt_choice_summary(onboarding_data),
        "task_list": task_list,
    }


def compact_status(file_payload: dict[str, Any]) -> str:
    return str(file_payload.get("status") or "missing")


def build_payload(args: argparse.Namespace) -> dict[str, Any]:
    state_dir = resolve_state_dir(args.codex_home, args.state_dir)
    user_context = read_text_payload(
        state_dir / "user-context.md",
        max_context_bytes=args.max_context_bytes,
        sections=args.section,
    )
    onboarding_state = read_json_payload(
        state_dir / "onboarding-state.json",
        max_context_bytes=args.max_context_bytes,
    )

    user_context_status = compact_status(user_context)
    onboarding_state_status = compact_status(onboarding_state)

    onboarding_data = onboarding_state.get("data") if onboarding_state_status == "present" else None
    onboarding_status = "missing"
    if isinstance(onboarding_data, dict):
        onboarding_status = str(onboarding_data.get("status") or "active")
    elif onboarding_state_status == "unreadable":
        onboarding_status = "unreadable"

    source_category_config = parse_source_category_config()
    automation_config = parse_automation_config()
    saved_source_preferences = extract_saved_source_preferences(
        user_context.get("content"),
        source_category_config,
    )
    connector_confirmation = build_connector_confirmation(
        source_category_config,
        onboarding_data,
    )
    sources = compact_source_categories(
        source_category_config,
        connector_confirmation,
        saved_source_preferences,
    )
    automations = compact_automation_state(automation_config, onboarding_data)
    onboarding_progress = build_onboarding_progress(
        onboarding_data,
        automation_config,
        source_category_config,
    )
    current_skill_experience = build_current_skill_experience(
        args.workflow,
        args.request_mode,
        onboarding_data,
    )

    quiet = onboarding_status == "quiet"
    potential_context_gaps: list[str] = []
    if user_context_status != "present":
        potential_context_gaps.append("saved Sales user context is missing or unreadable")

    final_obligations: list[dict[str, Any]] = []
    final_response_checks: list[dict[str, Any]] = []
    conditional_guidance: list[dict[str, Any]] = []
    if args.request_mode == "ordinary_workflow" and onboarding_status.casefold() == "missing":
        onboarding_cta_action = next_onboarding_action(onboarding_progress)
        final_obligations.append(
            {
                "id": "offer_sales_onboarding_next_step",
                "timing": "append_after_main_answer",
                "text_ref": (
                    "skills/user-context/references/onboarding.md#ordinary-workflow-onboarding-cta"
                ),
                "template": ordinary_onboarding_cta_template(onboarding_cta_action),
                "next_action": onboarding_cta_action,
                "requirement": (
                    "After answering the user's immediate Sales request, append the provided "
                    "Sales Setup Required CTA because onboarding has not started, unless the "
                    "immediate workflow is blocked on a required clarification. Keep the exact "
                    "heading, body, and final reply line. Do not add the next onboarding "
                    "action, full roadmap, source-status details, setup diagnostics, or a time "
                    "estimate. Do not downgrade this to a context-gap note, setup aside, or "
                    "passive future-improvement note. When a required clarification is needed, "
                    "the clarification must be the sole final natural continuation and this onboarding "
                    "CTA is deferred."
                ),
                "skip_when": (
                    "Skip only when the response is direct onboarding/setup/status work, "
                    "a focused workflow launched from the onboarding path, onboarding is "
                    "complete, onboarding is quiet, or the user explicitly asked to stop "
                    "or quiet onboarding guidance, or the immediate workflow requires a "
                    "clarification before it can proceed."
                ),
                "onboarding_status": onboarding_status,
            }
        )
    elif args.request_mode == "ordinary_workflow" and onboarding_status.casefold() in {
        "active",
        "in_progress",
        "started",
    }:
        core_onboarding = onboarding_progress.get("core_onboarding")
        core_complete = (
            isinstance(core_onboarding, dict) and core_onboarding.get("complete") is True
        )
        if not core_complete:
            next_core_action = (
                core_onboarding.get("next_action")
                if isinstance(core_onboarding, dict)
                else next_onboarding_action(onboarding_progress)
            )
            if not isinstance(next_core_action, dict):
                next_core_action = next_onboarding_action(onboarding_progress)
            final_obligations.append(
                {
                    "id": "complete_sales_core_onboarding",
                    "timing": "append_after_main_answer",
                    "text_ref": (
                        "skills/user-context/references/onboarding.md#core-onboarding-reminder"
                    ),
                    "template": core_onboarding_reminder_template(next_core_action),
                    "next_action": next_core_action,
                    "requirement": (
                        "Sales onboarding is already active, but core onboarding is not "
                        "complete. After answering only urgent or directly requested Sales "
                        "work, direct the user to resume the next unresolved core setup item. "
                        "Do not append the Sales Onboarding start CTA or ask whether to start "
                        "onboarding. If the primary workflow has a skill-owned final "
                        "continuation, fold this reminder into that same final natural "
                        "continuation as the move-on path instead of rendering a standalone onboarding "
                        "reminder plus another CTA."
                    ),
                    "skip_when": (
                        "Skip when the response is direct onboarding/setup/status work, a "
                        "focused workflow launched from the onboarding path, onboarding is "
                        "complete or quiet, core onboarding is complete, or the user explicitly "
                        "asked to stop or quiet onboarding guidance."
                    ),
                    "onboarding_status": onboarding_status,
                }
            )
        else:
            final_response_checks.append(
                {
                    "id": "active_onboarding_does_not_start_over",
                    "text_ref": (
                        "skills/user-context/references/onboarding.md#active-onboarding-reminder"
                    ),
                    "onboarding_status": onboarding_status,
                }
            )
    if args.request_mode == "ordinary_workflow" and not quiet and potential_context_gaps:
        conditional_guidance.append(
            {
                "id": "context_gap_note",
                "timing": "append_after_main_answer_only_if_material",
                "text_ref": "skills/user-context/references/onboarding.md#context-gap-note",
                "template": context_gap_note_template(),
                "apply_when": (
                    "append only when the completed workflow answer has a material gap "
                    "that saved context or a source category the workflow attempted would improve"
                ),
                "omit_when": (
                    "omit when available evidence was sufficient or the gap did not affect "
                    "confidence, completeness, or ability to act"
                ),
                "potential_gaps": potential_context_gaps,
            }
        )

    return {
        "schema_version": "sales_preflight.v2",
        "workflow": args.workflow,
        "read_only": True,
        "state": {
            "state_dir": str(state_dir),
            "user_context_status": user_context_status,
            "onboarding_state_status": onboarding_state_status,
            "onboarding_status": onboarding_status,
            "quiet": quiet,
        },
        "context": {
            "user_context": summarize_user_context(user_context.get("content")),
            "sources": sources,
            "automations": automations,
        },
        "control": {
            "response_mode": args.request_mode,
            "current_skill_experience": current_skill_experience,
            "final_obligations": final_obligations,
            "final_response_checks": final_response_checks,
            "conditional_guidance": conditional_guidance,
            "onboarding_progress": onboarding_progress,
            "manual_file_read_fallback_allowed_when": [
                "this script fails",
                "the user explicitly asks for raw file inspection",
            ],
        },
        "provenance": {
            "user_context": "read" if user_context_status == "present" else user_context_status,
            "onboarding_state": (
                "read" if onboarding_state_status == "present" else onboarding_state_status
            ),
            "generated_at": datetime.now(timezone.utc).isoformat(),
        },
    }


def main() -> int:
    args = parse_args()
    try:
        payload = build_payload(args)
    except Exception as exc:  # pragma: no cover - last-resort CLI guard
        print(
            json.dumps(
                {
                    "schema_version": "sales_preflight.v2",
                    "status": "error",
                    "error": str(exc),
                },
                indent=2,
                sort_keys=True,
            )
        )
        return 1
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
