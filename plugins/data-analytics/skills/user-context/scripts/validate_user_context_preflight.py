#!/usr/bin/env python3
"""Validate the Data Analytics user-context preflight invariant."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

MANDATORY_GATE_PHRASES = (
    "Mandatory pre-answer gate:",
    "Invoke `data-analytics:user-context` in preflight mode",
    "Use the returned `data_analytics_preflight` envelope as the source of truth",
    "not as substitutes for workflow-time reads from connected or provided sources",
)
USER_CONTEXT_MANDATORY_GATE_PHRASES = (
    "set the tool's `max_output_tokens` to at least `25000`",
    "warn the user that Data Analytics could not load all source-routing preferences and semantic-layer registry entries in one pass",
    "do not use the payload until the complete output is visible",
    "reports read status for `$CODEX_HOME/state/plugins/{marketplace_id}/{plugin_id}/user-context.md`",
)
PREFLIGHT_HELPER_PHRASES = (
    "summarize_user_context",
    "extract_saved_source_preferences",
    '"user_context": summarize_user_context(user_context_text, source_category_config)',
    '"source_preferences": saved_source_preferences',
    "semantic_layer_registry",
    "preferred_source_routes",
    "match_installable_plugin_candidates",
    "plugin_first_setup_recovery",
    "functions.list_available_plugins_to_install",
    "functions.request_plugin_install",
    "plugin_setup_opportunities",
)


def normalize_route_name(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", value.casefold())


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("plugin_path", type=Path)
    parser.add_argument("--plugin-id", default="data-analytics")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    plugin_root = args.plugin_path.resolve()
    skills_root = plugin_root / "skills"
    failures: list[str] = []

    required_paths = (
        skills_root / "user-context/SKILL.md",
        skills_root / "user-context/agents/openai.yaml",
        skills_root / "user-context/plugin-author-config/user-context-config.md",
        skills_root / "user-context/plugin-author-config/source-category-config.json",
        skills_root / "user-context/plugin-author-config/automation-config.md",
        skills_root / "user-context/references/onboarding.md",
        skills_root / "user-context/references/onboarding-examples.md",
        skills_root / "user-context/references/onboarding-state-template.json",
        skills_root / "user-context/references/source-category-runtime.md",
        skills_root / "user-context/references/automation.md",
        skills_root / "user-context/references/semantic-layer/setup.md",
        skills_root / "user-context/references/semantic-layer/source-intake.md",
        skills_root / "user-context/references/semantic-layer/connector-playbook.md",
        skills_root / "user-context/references/semantic-layer/skill-template.md",
        skills_root / "user-context/references/semantic-layer/weekly-polling-automation.md",
        skills_root / "user-context/scripts/data_analytics_preflight.py",
        skills_root / "user-context/scripts/init_user_context_state.py",
        skills_root / "user-context/scripts/reset_user_context_state.py",
        skills_root / "user-context/tests/test_state_helpers.py",
        skills_root / "index/SKILL.md",
    )
    for path in required_paths:
        if not path.exists():
            failures.append(f"Missing required user-context path: {path.relative_to(plugin_root)}")

    unexpected_semantic_layer_skill_dir = skills_root / ("create" + "-semantic-layer")
    if unexpected_semantic_layer_skill_dir.exists():
        failures.append(
            "Unexpected top-level semantic-layer setup skill: "
            f"{unexpected_semantic_layer_skill_dir.relative_to(plugin_root)}"
        )

    skill_files = sorted(skills_root.rglob("SKILL.md"))
    for skill_file in skill_files:
        text = skill_file.read_text(encoding="utf-8")
        rel = skill_file.relative_to(plugin_root)
        if rel == Path("skills/user-context/SKILL.md"):
            mandatory_gate = text.split("## Mandatory Pre-Answer Gate", 1)[-1].split(
                "\n## ",
                1,
            )[0]
            for phrase in (
                "## Mandatory Pre-Answer Gate",
                "scripts/data_analytics_preflight.py",
                "follow `references/onboarding.md`",
                "## First Run Setup",
                "Never run parallel writes against the same Data Analytics state files",
                "Do not use `user-context.md` as a general memory file",
                "If the user asks Data Analytics to remember arbitrary context, do not save it.",
            ):
                if phrase not in text:
                    failures.append(f"{rel} missing required phrase: {phrase}")
            for phrase in USER_CONTEXT_MANDATORY_GATE_PHRASES:
                if phrase not in mandatory_gate:
                    failures.append(f"{rel} mandatory gate missing required phrase: {phrase}")
            continue
        for phrase in MANDATORY_GATE_PHRASES:
            if phrase not in text:
                failures.append(f"{rel} missing mandatory preflight phrase: {phrase}")

    hero_skills = (
        skills_root / "metric-diagnostics/SKILL.md",
        skills_root / "product-business-analysis/SKILL.md",
        skills_root / "kpi-reporting/SKILL.md",
    )
    for hero_skill in hero_skills:
        text = hero_skill.read_text(encoding="utf-8")
        rel = hero_skill.relative_to(plugin_root)
        for phrase in ("data-analytics:user-context",):
            if phrase not in text:
                failures.append(f"{rel} missing user-context preflight handoff: {phrase}")

    preflight_script = skills_root / "user-context/scripts/data_analytics_preflight.py"
    if preflight_script.exists():
        preflight_text = preflight_script.read_text(encoding="utf-8")
        for phrase in PREFLIGHT_HELPER_PHRASES:
            if phrase not in preflight_text:
                failures.append(
                    "skills/user-context/scripts/data_analytics_preflight.py "
                    f"missing compact-context helper wording: {phrase}"
                )
        if "user_context_markdown" in preflight_text:
            failures.append(
                "skills/user-context/scripts/data_analytics_preflight.py must not emit "
                "legacy context.user_context_markdown"
            )

    onboarding_text = (skills_root / "user-context/references/onboarding.md").read_text(
        encoding="utf-8"
    )
    for phrase in (
        "## Step 2: Check Main Analytics Sources",
        "### Step 2A: Resolve Source Questions",
        "Do not preflight-read installed or active sources just to prove they work.",
        "transition without a proof read",
        "Source setup has covered each required source type as `active`",
        "Before Data Analytics sets up data context",
        "resolution: user_deferred",
        "### Step 4A: Offer First Hero Prompt",
        "Do not: show three hero prompts initially",
        "write the prompt you would rather try instead",
        "`skip` to finish onboarding",
        "Step 5, `complete_or_quiet`, when the user skips or defers",
        "## CTA Arbitration",
        "## Completion Criteria",
    ):
        if phrase not in onboarding_text:
            failures.append(
                f"skills/user-context/references/onboarding.md missing required phrase: {phrase}"
            )

    source_runtime_text = (
        skills_root / "user-context/references/source-category-runtime.md"
    ).read_text(encoding="utf-8")
    for phrase in (
        "## Setup-Owned Source Routes",
        "Preflight is a reader.",
        "functions.list_available_plugins_to_install",
        "## Plugin-First Setup For Missing Sources",
        "Do not proactively suggest every installable plugin",
        "## Missing Sources And Fallbacks",
        "`needs_confirmation`",
        "Do not perform an eager read just to prove an installed source works",
        "Do not run a proof query during onboarding",
        "attempt the smallest useful app or connector read",
        "core onboarding categories, not optional setup extras",
        "resolution: user_deferred",
    ):
        if phrase not in source_runtime_text:
            failures.append(
                "skills/user-context/references/source-category-runtime.md "
                f"missing required phrase: {phrase}"
            )

    automation_text = (skills_root / "user-context/references/automation.md").read_text(
        encoding="utf-8"
    )
    for phrase in (
        "Ask for explicit user approval",
        "Only say the default automation setup is complete",
        "Do not mark setup complete",
    ):
        if phrase not in automation_text:
            failures.append(
                f"skills/user-context/references/automation.md missing required phrase: {phrase}"
            )

    semantic_layer_setup_text = (
        skills_root / "user-context/references/semantic-layer/setup.md"
    ).read_text(encoding="utf-8")
    for phrase in (
        "source-use checkpoint",
        "Infer expected source lanes",
        "nearby but not exact",
        "rejected or lower-confidence candidates",
        "authoritative data documentation",
        "source-backed semantic-layer skills",
        "user-trusted canonical data skills",
        "treat that as authoritative data documentation",
    ):
        if phrase not in semantic_layer_setup_text:
            failures.append(
                "skills/user-context/references/semantic-layer/setup.md "
                f"missing required phrase: {phrase}"
            )

    semantic_layer_weekly_polling_text = (
        skills_root / "user-context/references/semantic-layer/weekly-polling-automation.md"
    ).read_text(encoding="utf-8")
    for phrase in (
        "authoritative data documentation",
        "source-backed semantic-layer skills",
        "user-trusted canonical data skills",
        "generic-local-skill-only evidence",
    ):
        if phrase not in semantic_layer_weekly_polling_text:
            failures.append(
                "skills/user-context/references/semantic-layer/weekly-polling-automation.md "
                f"missing required phrase: {phrase}"
            )

    semantic_layer_source_intake_text = (
        skills_root / "user-context/references/semantic-layer/source-intake.md"
    ).read_text(encoding="utf-8")
    for phrase in (
        "Infer useful source families",
        "do not treat ambient app availability as user approval",
    ):
        if phrase not in semantic_layer_source_intake_text:
            failures.append(
                "skills/user-context/references/semantic-layer/source-intake.md "
                f"missing required phrase: {phrase}"
            )

    semantic_layer_template_text = (
        skills_root / "user-context/references/semantic-layer/skill-template.md"
    ).read_text(encoding="utf-8")
    for phrase in (
        "## Start Here",
        "## References",
        "## Answering Rules",
        "## Quick Reference",
        "## Entity Clarification",
        "## Standard Filters And Dimensions",
        "only when the layer needs separate evidence tracking",
        "Do not put setup-time policy or full evidence procedures",
    ):
        if phrase not in semantic_layer_template_text:
            failures.append(
                "skills/user-context/references/semantic-layer/skill-template.md "
                f"missing required phrase: {phrase}"
            )
    for phrase in ("### Source Order", "### Evidence Standard"):
        if phrase in semantic_layer_template_text:
            failures.append(
                "skills/user-context/references/semantic-layer/skill-template.md "
                f"retains heavy generated-skill phrase: {phrase}"
            )

    app_manifest_path = plugin_root / ".app.json"
    manifest_app_aliases: set[str] = set()
    try:
        app_manifest = json.loads(app_manifest_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        failures.append(f"Invalid Data Analytics app manifest: {exc}")
    else:
        apps = app_manifest.get("apps") if isinstance(app_manifest, dict) else None
        if not isinstance(apps, dict) or not apps:
            failures.append("Data Analytics .app.json must define a non-empty apps object")
        else:
            manifest_app_aliases = {
                normalize_route_name(app_name)
                for app_name, metadata in apps.items()
                if isinstance(app_name, str)
                and isinstance(metadata, dict)
                and isinstance(metadata.get("id"), str)
                and metadata["id"]
            }

    try:
        source_config = json.loads(
            (
                skills_root / "user-context/plugin-author-config/source-category-config.json"
            ).read_text(encoding="utf-8")
        )
        json.loads(
            (skills_root / "user-context/references/onboarding-state-template.json").read_text(
                encoding="utf-8"
            )
        )
    except json.JSONDecodeError as exc:
        failures.append(f"Invalid user-context JSON: {exc}")
    else:
        if not isinstance(source_config, dict):
            failures.append(
                "skills/user-context/plugin-author-config/source-category-config.json "
                "must define a JSON object"
            )
            source_config = {}
        if source_config.get("schema_version") != "data_analytics_source_category_config.v1":
            failures.append(
                "skills/user-context/plugin-author-config/source-category-config.json "
                "missing schema_version data_analytics_source_category_config.v1"
            )
        if not isinstance(source_config.get("description"), str):
            failures.append(
                "skills/user-context/plugin-author-config/source-category-config.json "
                "must define a description"
            )
        elif "preferred plugin routing hints" not in source_config["description"]:
            failures.append(
                "skills/user-context/plugin-author-config/source-category-config.json "
                "description must document preferred plugin routing hints"
            )
        categories = source_config.get("categories")
        if not isinstance(categories, dict) or not categories:
            failures.append(
                "skills/user-context/plugin-author-config/source-category-config.json "
                "must define a non-empty categories object"
            )
        else:
            for category_id, metadata in categories.items():
                if not isinstance(category_id, str) or not re.fullmatch(
                    r"[a-z0-9_]+",
                    category_id,
                ):
                    failures.append(
                        "skills/user-context/plugin-author-config/source-category-config.json "
                        f"has invalid category id: {category_id}"
                    )
                    continue
                if not isinstance(metadata, dict):
                    failures.append(
                        "skills/user-context/plugin-author-config/source-category-config.json "
                        f"category {category_id} must be an object"
                    )
                    continue
                allowed_fields = {
                    "label",
                    "preferred_plugins",
                    "preferred_apps",
                    "relevant_skills",
                }
                unexpected_fields = sorted(set(metadata) - allowed_fields)
                if unexpected_fields:
                    failures.append(
                        "skills/user-context/plugin-author-config/source-category-config.json "
                        f"category {category_id} has unexpected fields: {unexpected_fields}"
                    )
                if not isinstance(metadata.get("label"), str) or not metadata["label"]:
                    failures.append(
                        "skills/user-context/plugin-author-config/source-category-config.json "
                        f"category {category_id} must define a non-empty label"
                    )
                preferred_plugins = metadata.get("preferred_plugins")
                if not isinstance(preferred_plugins, list) or not preferred_plugins:
                    failures.append(
                        "skills/user-context/plugin-author-config/source-category-config.json "
                        f"category {category_id} preferred_plugins must be a non-empty list"
                    )
                    preferred_plugins = []
                elif not all(
                    isinstance(plugin, str) and plugin for plugin in preferred_plugins
                ):
                    failures.append(
                        "skills/user-context/plugin-author-config/source-category-config.json "
                        f"category {category_id} preferred_plugins must contain non-empty strings"
                    )
                else:
                    for preferred_plugin in preferred_plugins:
                        if normalize_route_name(preferred_plugin) not in manifest_app_aliases:
                            failures.append(
                                "skills/user-context/plugin-author-config/"
                                "source-category-config.json "
                                f"category {category_id} preferred plugin {preferred_plugin} "
                                "must be declared in .app.json"
                            )
                preferred_apps = metadata.get("preferred_apps", [])
                if not isinstance(preferred_apps, list):
                    failures.append(
                        "skills/user-context/plugin-author-config/source-category-config.json "
                        f"category {category_id} preferred_apps must be a list"
                    )
                    preferred_apps = []
                elif not all(isinstance(app, str) and app for app in preferred_apps):
                    failures.append(
                        "skills/user-context/plugin-author-config/source-category-config.json "
                        f"category {category_id} preferred_apps must contain non-empty strings"
                    )
                else:
                    for preferred_app in preferred_apps:
                        if normalize_route_name(preferred_app) not in manifest_app_aliases:
                            failures.append(
                                "skills/user-context/plugin-author-config/"
                                "source-category-config.json "
                                f"category {category_id} preferred app {preferred_app} "
                                "must be declared in .app.json"
                            )
                relevant_skills = metadata.get("relevant_skills", [])
                if not isinstance(relevant_skills, list):
                    failures.append(
                        "skills/user-context/plugin-author-config/source-category-config.json "
                        f"category {category_id} relevant_skills must be a list"
                    )
                else:
                    for index, entry in enumerate(relevant_skills):
                        if not isinstance(entry, dict):
                            failures.append(
                                "skills/user-context/plugin-author-config/source-category-config.json "
                                f"category {category_id} relevant_skills[{index}] must be an object"
                            )
                            continue
                        for field in ("app", "skill"):
                            if not isinstance(entry.get(field), str) or not entry[field]:
                                failures.append(
                                    "skills/user-context/plugin-author-config/"
                                    "source-category-config.json "
                                    f"category {category_id} relevant_skills[{index}] "
                                    f"missing non-empty {field}"
                                )

    user_context_config_path = (
        skills_root / "user-context/plugin-author-config/user-context-config.md"
    )
    if user_context_config_path.exists():
        user_context_config = user_context_config_path.read_text(encoding="utf-8")
        for phrase in (
            "# Data Analytics User Context Config",
            "## User Context Shape",
            "## Default User Context",
            "Store durable Data Analytics source-routing choices explicitly selected for future use.",
            "Do not add general memory",
            "# Data Analytics Source Routing Preferences",
            "# Semantic Layers",
        ):
            if phrase not in user_context_config:
                failures.append(
                    "skills/user-context/plugin-author-config/user-context-config.md "
                    f"missing required phrase: {phrase}"
                )
        default_user_context = user_context_config.rsplit("## Default User Context", 1)[-1]
        for disallowed in ("- Priority:", "- Use When:", "## Saved Links And Context"):
            if disallowed in default_user_context:
                failures.append(
                    "skills/user-context/plugin-author-config/user-context-config.md "
                    f"default user context must not contain: {disallowed}"
                )
        source_category_ids = set((source_config.get("categories") or {}).keys())
        source_routing_section = default_user_context.split("# Semantic Layers", 1)[0]
        configured_sections = set(re.findall(r"(?m)^##\s+([a-z0-9_]+)\s*$", source_routing_section))
        if configured_sections != source_category_ids:
            failures.append(
                "skills/user-context/plugin-author-config/user-context-config.md "
                "source routing sections must match source-category-config.json"
            )
        for category_id in configured_sections:
            category_match = re.search(
                rf"(?ms)^##\s+{re.escape(category_id)}\s*$.*?(?=^##\s+|^#\s+Semantic Layers|\Z)",
                source_routing_section,
            )
            category_section = category_match.group(0) if category_match else ""
            for field in ("Prefer", "Avoid"):
                if len(re.findall(rf"(?m)^-\s+{field}:\s*$", category_section)) != 1:
                    failures.append(
                        "skills/user-context/plugin-author-config/user-context-config.md "
                        f"source routing category {category_id} must define one blank {field} row"
                    )
        if "status: not provided" not in default_user_context:
            failures.append(
                "skills/user-context/plugin-author-config/user-context-config.md "
                "semantic layer registry must start with status: not provided"
            )

    if failures:
        for failure in failures:
            print(f"- {failure}", file=sys.stderr)
        return 1
    print(f"Validated {len(skill_files)} Data Analytics skill preflight surfaces.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
