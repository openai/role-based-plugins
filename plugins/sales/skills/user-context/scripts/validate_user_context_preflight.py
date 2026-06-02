#!/usr/bin/env python3
"""Validate the Sales user-context preflight invariant."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

PLUGIN_ROOT = Path(__file__).resolve().parents[3]
SKILLS_ROOT = PLUGIN_ROOT / "skills"
REQUIRED_PATH = "`$CODEX_HOME/state/plugins/{marketplace_id}/{plugin_id}/user-context.md`"
SIBLING_REQUIRED_PHRASES = (
    "Mandatory pre-answer gate:",
    f"Actually read {REQUIRED_PATH}",
    "Do not treat routing to the context skill, listing files, or checking that the file exists as sufficient",
    "saved profile/preferences must be loaded into context and applied",
    "trigger onboarding from `skills/user-context/references/onboarding.md`",
)
SIBLING_PREFLIGHT_HANDOFF_PHRASES = (
    "Mandatory pre-answer gate:",
    "Invoke `sales:user-context` in preflight mode",
    "Use the returned `sales_preflight` envelope as authoritative",
)
USER_CONTEXT_REQUIRED_PHRASES = (
    "## Mandatory Pre-Answer Gate",
    "use `scripts/sales_preflight.py` as the default state-read path",
    "on behalf of other Sales skills that call `sales:user-context`",
    "set the tool's `max_output_tokens` to at least `25000`",
    "warn the user that Sales preflight was truncated and that Sales plugin memory or preflight context may be getting bloated",
    f"reports read status for {REQUIRED_PATH}",
    "Do not treat listing files, checking that files exist, or saying they should be read as sufficient",
    "saved preferences, profile, context, source preferences, and source-of-truth pointers must be loaded and applied",
    "actually read the relevant state files manually",
    "follow `references/onboarding.md`",
    "Ordinary workflow preflight should read these files through `scripts/sales_preflight.py`",
    "sales_preflight.py",
    "modify `user-context.md` directly",
    "Never run parallel writes against the same Sales state files",
    "Script-Driven Preflight Payload",
    "set `max_output_tokens` to at least `25000`",
    "do not treat preflight as complete until the full output is visible",
    "Loading the relevant skill-owned experience guidance is mandatory whenever that skill is the primary workflow",
    "the final continuation invariant for primary outputs and follow-up turns",
    "end with one concrete user-visible next action phrased as a natural sentence or question",
    "Lead with the actual question the user needs to answer",
)
SOFT_ONLY_PHRASES = (
    "Invoke `user-context` in preflight mode",
    "Do not treat routing to `user-context`",
    "follow `skills/user-context/references/onboarding.md`",
    "mental checklist / scratchpad",
)
FORMULAIC_CLARIFICATION_PROMPT_PHRASES = (
    "**I need one detail to continue.**",
    "**I need a few forecast choices to continue.**",
    "Reply with a letter, or send",
    "allow the user to reply with a letter or provide a different answer",
)
CLICKABLE_INLINE_SOURCE_PHRASE = "When referencing sources inline, prefer clickable Markdown links"
AUDIENCE_AND_LANGUAGE_SECTION = """### Audience And Language

Write for Sales users, not plugin maintainers. This applies to final answers, setup/status readbacks, failure explanations, tool preambles, and mid-turn progress narration.

Translate implementation work into practical Sales impact: what Sales is checking, setting up, saving, or preparing, and why it matters. Avoid implementation terms such as preflight, state file, cache, raw connector id, heartbeat, targetThreadId, schema, API, runtime, metadata, and provider taxonomy unless the user asks for debugging details."""
LEGACY_AUDIENCE_LANGUAGE_PHRASES = (
    "Use practical sales and business language",
    "Prefer terms like accounts",
    "sales-adjacent operators",
    "preflight, cursor, probe",
)
USER_FACING_DEFAULT_PROMPTS = {
    "analyze-account-signals": "Analyze signals for one of my active accounts.",
    "build-competitive-brief": "Build a competitive brief for a competitor set.",
    "follow-up-after-call": "Help me follow up from a recent call.",
    "suggest-sales-next-step": "Suggest my next best Sales step.",
    "enrich-company-and-contact-data": "Enrich a company or contact list.",
    "plan-deal-strategy": "Build a deal strategy for an active account.",
    "find-key-internal-sources": "Find the key internal sources for a customer question.",
    "prepare-for-meeting": "Prepare me for an upcoming customer meeting.",
    "prioritize-accounts": "Prioritize accounts for pipeline focus.",
    "find-customer-quotes": "Find customer quotes about a feedback theme.",
    "review-forecast": "Review a forecast for risk and next actions.",
    "get-rep-call-feedback": "Give feedback on a rep's calls.",
    "review-rep-call-trends": "Review a rep's call trends.",
    "build-business-case": "Build a business case for a customer.",
}
HELPER_OR_ROUTER_SKILLS = {"salesforce", "hubspot", "zoominfo", "user-context", "index"}


def app_name_aliases(value: str) -> set[str]:
    normalized = re.sub(r"[^a-z0-9]+", "", value.casefold())
    aliases = {normalized}
    if normalized.endswith("com"):
        aliases.add(normalized[:-3])
    if normalized == "agentforcesales":
        aliases.add("salesforce")
    return aliases


def has_all_nearby_terms(
    text: str,
    anchor: str,
    required_terms: tuple[str | tuple[str, ...], ...],
    *,
    window: int = 1200,
) -> bool:
    anchor_index = text.find(anchor)
    if anchor_index < 0:
        return False
    nearby = text[anchor_index : anchor_index + window].casefold()
    for term in required_terms:
        if isinstance(term, tuple):
            if not any(option.casefold() in nearby for option in term):
                return False
        elif term.casefold() not in nearby:
            return False
    return True


def json_path_exists(value: object, path: tuple[str, ...]) -> bool:
    current = value
    for part in path:
        if not isinstance(current, dict) or part not in current:
            return False
        current = current[part]
    return True


def main() -> int:
    failures: list[str] = []
    skill_files = sorted(SKILLS_ROOT.glob("*/SKILL.md"))
    required_scripts = (
        PLUGIN_ROOT / "skills/user-context/scripts/sales_preflight.py",
        PLUGIN_ROOT / "skills/user-context/scripts/init_user_context_state.py",
        PLUGIN_ROOT / "skills/user-context/scripts/reset_user_context_state.py",
        PLUGIN_ROOT / "skills/user-context/scripts/validate_sales_automation_setup.py",
    )
    required_tests = (PLUGIN_ROOT / "skills/user-context/tests/test_state_helpers.py",)
    source_category_config = (
        PLUGIN_ROOT / "skills/user-context/plugin-author-config/source-category-config.json"
    )
    app_manifest = PLUGIN_ROOT / ".app.json"
    user_context_config = (
        PLUGIN_ROOT / "skills/user-context/plugin-author-config/user-context-config.md"
    )
    automation_config = (
        PLUGIN_ROOT / "skills/user-context/plugin-author-config/automation-config.md"
    )
    automation_reference = PLUGIN_ROOT / "skills/user-context/references/automation.md"
    legacy_source_category_config_md = (
        PLUGIN_ROOT / "skills/user-context/plugin-author-config/source-category-config.md"
    )
    legacy_category_state_template = (
        PLUGIN_ROOT / "skills/user-context/references/category-state-template.json"
    )
    source_category_runtime = (
        PLUGIN_ROOT / "skills/user-context/references/source-category-runtime.md"
    )
    plugin_memory_reference = PLUGIN_ROOT / "skills/user-context/references/plugin-memory.md"
    legacy_source_categories = PLUGIN_ROOT / "references/source-categories.md"
    legacy_source_category_catalog = PLUGIN_ROOT / "references/source-category-catalog.md"
    legacy_audience_reference = PLUGIN_ROOT / "references/audience-and-language.md"
    legacy_top_level_references = PLUGIN_ROOT / "references"
    legacy_top_level_scripts = PLUGIN_ROOT / "scripts"
    legacy_root_author_config = PLUGIN_ROOT / "plugin-author-config"
    hero_prompts = PLUGIN_ROOT / "skills/user-context/references/hero-prompts.md"
    onboarding_reference = PLUGIN_ROOT / "skills/user-context/references/onboarding.md"
    onboarding_state_template = (
        PLUGIN_ROOT / "skills/user-context/references/onboarding-state-template.json"
    )
    meeting_prep_skill = PLUGIN_ROOT / "skills/prepare-for-meeting/SKILL.md"
    preflight_script = PLUGIN_ROOT / "skills/user-context/scripts/sales_preflight.py"
    call_followup_skill = PLUGIN_ROOT / "skills/follow-up-after-call/SKILL.md"
    internal_navigation_skill = PLUGIN_ROOT / "skills/find-key-internal-sources/SKILL.md"
    sales_company_research_skill = PLUGIN_ROOT / "skills/sales-company-research/SKILL.md"
    sales_company_research_agent = (
        PLUGIN_ROOT / "skills/sales-company-research/agents/openai.yaml"
    )

    if not skill_files:
        failures.append(f"No skill files found under {SKILLS_ROOT}")
    for script_file in required_scripts:
        if not script_file.exists():
            failures.append(
                f"Missing required Sales state helper script: {script_file.relative_to(PLUGIN_ROOT)}"
            )
    for test_file in required_tests:
        if not test_file.exists():
            failures.append(
                f"Missing required Sales state helper test: {test_file.relative_to(PLUGIN_ROOT)}"
            )

    if onboarding_reference.exists():
        onboarding_text = onboarding_reference.read_text(encoding="utf-8")
        for phrase in (
            "# Sales Onboarding Flow",
            "## Common Onboarding Message Frame",
            "**Onboarding Complete**",
            "## Progress Checklist Contract",
            "## Step 1: Orientation",
            "## Step 2: Confirm Active/Missing Sources",
            "### Step 2A: Resolve Source Questions",
            "## Step 3: Sales Automations",
            "### Step 3A: Introduce Sales Automations",
            "### Step 3B: Set Up Sales Automations",
            "## Step 4: First Hero Prompt",
            "### Step 4A: Choose First Hero Prompt",
            "### Step 4B: Introduce Selected First Hero Workflow",
            "### Step 4C: Run Selected First Hero Demo",
            "### Step 4D: Review And Iterate",
            "### Step 4E: Introduce Plugin Memory And Save Preference",
            "## Step 5: Other Hero Prompts",
            "### Step 5A: Choose Next Hero Prompt",
            "### Step 5B: Introduce Selected Remaining Hero Workflow",
            "### Step 5C: Run Selected Remaining Hero Demo",
            "### Step 5D: Review And Continue Remaining Hero",
            "## Step 6: Completion",
            "## Ordinary Workflow Onboarding CTA",
            "The Sales plugin improves Codex at sales-related work",
            "**How it works**",
            "**What it can do**",
            "Ready to set that up?",
            "After some searching, it looks like you're already set up",
            "There are a few more connectors we can add to help Sales work as well as possible",
            "**Meeting notes** improves meeting prep and follow-ups",
            "You'll be prompted to install and authenticate plugins or connectors",
            "When the current step has open questions",
            "Use a compact numbered list when there is more than one question",
            "include the default escape hatch inside the relevant numbered item",
            "Do not add a separate summary prompt after the numbered list",
            "`Next Step` is the action prompt, not the explainer",
            "Do not let the whole onboarding message be only a next-step frame",
            "When introducing a workflow, skill, or new onboarding concept for the first time",
            "Use the New Concept Introduction Pattern",
            "Do not create tiny transition turns",
            "Okay, I've saved that. Now let's move on to the next step.",
            "Okay, that finishes source setup for now. Sales will use",
            "do not render the full `Saved Sales Plugin Memory.` recap or `Saved today` list",
            "Preserve real approval gates",
            "## New Concept Introduction Pattern",
            "## {Concept Name}",
            "This skill...",
            "Plugin memory is how the Sales plugin remembers approved preferences",
            "simple automations to ensure Sales keeps getting better for you",
            "the body should start with `This skill...`",
            "Do not render user-facing CTAs with code-styled skill names",
            "User-facing bullets should be polished sentence fragments",
            "Do not start bullets with lowercase words",
            "teach the preferred invocation pattern",
            "start with `@Sales`",
            "@Sales prepare me for my Acme renewal call tomorrow",
            "The numbered choice set is the final action prompt by itself",
            "do not add a `Next Step` heading",
            "Keep automation breadcrumbs, readback cards, and created-card text visually separate from the choice set",
            "Do not reuse a stale checklist from an earlier thread turn",
            "mark the next unresolved visible step as `in_progress`",
            "Reply `start` to continue.",
            "start a new thread and include `@Sales`",
            "## Active Onboarding Reminder",
            "## Core Onboarding Reminder",
            "You can keep going through the rest of the Sales skills one by one",
            "Say `okay` and I'll introduce Analyze Account Signals",
            "ID: `start_sales_onboarding`",
            "Orientation",
            "Connector setup/confirmation",
            "Sales automation setup",
            "First hero prompt",
            "Other hero prompts",
            "core onboarding is complete",
            "automation-config.md",
            "Do not preflight-read installed or active sources",
            "calls `functions.list_available_plugins_to_install` once for the setup pass",
            "If the user confirms an installable plugin or connector candidate",
            "installable related plugin needs approval",
            "add dedicated Sales workflow support",
            "Keep plugin-first setup eligible for retry in future workflows",
            "Do not call `request_plugin_install` in parallel",
            "Data enrichment adds missing company, contact, account",
            "Preferred options are ZoomInfo, Clay, HG Insights, Rox, Apollo, Actively, or Meticulate",
            "You can skip anything now; Sales will ask again later only when a workflow would materially benefit",
            "move directly into Step 3A",
            "## Step 4: First Hero Prompt",
            "Do not run another hero workflow until the user picks `1`, `2`, or `3`",
            "treat the numbered choice as consent to try that workflow",
            "render that skill's compact first-run intro above the normal workflow output",
            "hero_prompt_choice",
            "choose_first_hero_prompt",
            "Later hero choosers may include previously tried workflows as repeat options",
            "skills/prepare-for-meeting/SKILL.md",
            "inline experience guidance",
            "## Prepare For Meeting",
            "start fresh with `This skill...`",
            "@Sales prepare me for my Acme renewal call tomorrow",
            "Here's your meeting prep, using",
            "## Workflow Walkthrough On Request",
            "Do not render `What Happened`, `Recap`, or another walkthrough heading by default",
            "Do not render that feedback CTA as an H2/H3 heading",
            "How does that look? Any other changes, or should we show the next demo workflow choices?",
            "Only require explicit yes for broad, sensitive, ambiguous, high-risk, or externally visible preferences",
            "Do not save plugin memory on every iteration",
            "must never be a narrow-preference save approval",
            "Calendar attachment is explicit-user-request only",
            "Should I set those up? They'll run in a different thread and notify you when they have something to review.",
            "Do not load hero workflow skill files or run a demo workflow until the user picks one",
            "automation.md#Fast Setup Checklist",
            "Automations are set up and read back cleanly",
            "I also kicked off the first research run in the pinned **Sales Company Research** thread",
            "starting with its next scheduled run",
            "Do not compress the three hero choices into one inline sentence",
            "each numbered option must be on its own line",
            "Core onboarding is done. Pick a workflow to try first:",
            "1. **Prepare For Meeting:** Builds a concise brief for an upcoming customer or high-value sales meeting.",
            "2. **Follow Up After Call:** Turns a recent call or notes into a recap, next steps, email draft, CRM-ready update, and internal recap.",
            "3. **Prioritize Accounts:** Helps you understand what needs to be done with your accounts by flagging anomalies, building forecasts, and prioritizing accounts.",
            "Sales Company Research",
            "Sales Tips",
            "one practical Sales workflow to try next",
            "improve speed and correctness",
            "weekly on Mondays at 9:00 AM local time",
            "runs weekdays at 9:00 AM local time",
            "Sales Daily Meeting Prep",
            "not in the main onboarding thread",
            'FYI: The pinned thread **"{thread_title}"**',
            "Only say saved entries or proposals exist when state or readback confirms them",
            "Pinned",
            "initial_resource_discovery",
            "## Step 5: Other Hero Prompts",
            "choose_next_hero_prompt",
            "Hero demos use a repeatable artifact loop",
            "hero_workflow.current_status",
            "offer_first_hero_action_or_next_demo",
            "offer_remaining_hero_action_or_next_demo",
            "normal next-step candidates",
            "show the next demo workflow choices",
            "Choices can include the previous one or two workflows as repeat options",
            "Do not offer only previously tried workflows",
            "skills/follow-up-after-call/SKILL.md",
            "Suggest a real call even if it is not a customer call",
            "large, important-looking meeting as recent as possible",
            "ask for iteration first",
            "prioritize open pipeline by default",
            "skills/prioritize-accounts/SKILL.md",
        ):
            if phrase not in onboarding_text:
                failures.append(
                    f"skills/user-context/references/onboarding.md missing progress checklist contract wording: {phrase}"
                )
        if not has_all_nearby_terms(
            onboarding_text,
            "For Prepare For Meeting",
            (
                "`okay`",
                "`calendar`",
                ("manual meeting details", "manual fallback", "provide attendee/agenda details"),
            ),
        ):
            failures.append(
                "skills/user-context/references/onboarding.md missing Prepare For Meeting behavior: okay should search calendar before manual meeting-detail fallback"
            )
        if not has_all_nearby_terms(
            onboarding_text,
            "For Follow Up After Call",
            (
                "`okay`",
                "`calendar`",
                "`meeting_notes`",
                ("pasted notes/transcripts", "manual call evidence", "manual fallback"),
            ),
        ):
            failures.append(
                "skills/user-context/references/onboarding.md missing Follow Up After Call intro behavior: okay should search calendar and meeting_notes before manual evidence fallback"
            )
        if not has_all_nearby_terms(
            onboarding_text,
            "If the selected skill is Follow Up After Call",
            (
                "`calendar`",
                "`meeting_notes`",
                (
                    "before asking for manual call evidence",
                    "before manual call evidence",
                    "manual fallback",
                ),
            ),
        ):
            failures.append(
                "skills/user-context/references/onboarding.md missing Follow Up After Call run behavior: search calendar and meeting_notes before manual call evidence"
            )
        for stale_phrase in (
            "Guided Setup Continuation Rule",
            "Prepare For Meeting Demo Report Contract",
            "Connector Confirmation Copy Contract",
            "Plugin Memory Contract",
            "Weekly Discovery Contract",
            "Choose prepare-for-meeting prompt",
            "Explain plugin memory",
            "Capture key context",
            "Set up weekly discovery and run initial search",
            "Set up weekly Sales Resource Discovery",
            "Set up daily meeting prep and weekday check-in",
            "## Step 7: Scheduled Help",
            "## Step 7: Completion",
            "Reply with a docs preference or enrichment info",
            "walk how to customize",
            "## Welcome To Sales",
            "**What it can help with:**",
            "Sales source setup looks mostly ready",
            "Should I set up the recommended Sales automations?",
            "Sales Weekday Check-In",
        ):
            if stale_phrase in onboarding_text:
                failures.append(
                    f"skills/user-context/references/onboarding.md still contains stale onboarding phrase: {stale_phrase}"
                )
    else:
        failures.append(
            "Missing onboarding reference: skills/user-context/references/onboarding.md"
        )

    if not onboarding_state_template.exists():
        failures.append(
            "Missing onboarding state template: skills/user-context/references/onboarding-state-template.json"
        )
    else:
        try:
            onboarding_state_data = json.loads(
                onboarding_state_template.read_text(encoding="utf-8")
            )
        except json.JSONDecodeError as exc:
            failures.append(
                f"skills/user-context/references/onboarding-state-template.json is invalid JSON: {exc}"
            )
            onboarding_state_data = {}
        skill_experience = onboarding_state_data.get("skill_experience")
        hero_prompt_choice = onboarding_state_data.get("hero_prompt_choice")
        if not isinstance(hero_prompt_choice, dict):
            failures.append(
                "skills/user-context/references/onboarding-state-template.json missing hero_prompt_choice"
            )
        else:
            expected_options = [
                "prepare-for-meeting",
                "follow-up-after-call",
                "prioritize-accounts",
            ]
            if hero_prompt_choice.get("options") != expected_options:
                failures.append(
                    "onboarding-state-template hero_prompt_choice.options must list the three core hero skills"
                )
            for field in (
                "status",
                "selected_skill",
                "selected_anchor",
                "last_shown",
                "selected_at",
                "last_offered_skills",
            ):
                if field not in hero_prompt_choice:
                    failures.append(f"onboarding-state-template hero_prompt_choice missing {field}")
        if not isinstance(skill_experience, dict):
            failures.append(
                "skills/user-context/references/onboarding-state-template.json missing skill_experience"
            )
        else:
            for skill_name in USER_FACING_DEFAULT_PROMPTS:
                entry = skill_experience.get(skill_name)
                if not isinstance(entry, dict):
                    failures.append(
                        f"onboarding-state-template skill_experience missing {skill_name}"
                    )
                    continue
                for field in (
                    "introduced_at",
                    "first_tried_at",
                    "last_suggested_at",
                    "dismissed_at",
                ):
                    if field not in entry:
                        failures.append(
                            f"onboarding-state-template skill_experience.{skill_name} missing {field}"
                        )
            for helper_name in HELPER_OR_ROUTER_SKILLS:
                if helper_name in skill_experience:
                    failures.append(
                        f"onboarding-state-template must not track helper/router skill experience: {helper_name}"
                    )
    if preflight_script.exists():
        preflight_text = preflight_script.read_text(encoding="utf-8")
        for phrase in (
            "build_onboarding_progress",
            "ordinary_onboarding_cta_template",
            "offer_sales_onboarding_next_step",
            "#ordinary-workflow-onboarding-cta",
            "guided_onboarding_workflow",
            "ONBOARDING_STEP_DEFINITIONS",
            "start_sales_onboarding",
            "Orientation",
            "connector_setup_confirmation",
            "Connector setup/confirmation",
            "sales_automation_setup",
            "Sales automation setup",
            "first_hero_prompt",
            "First hero prompt",
            "hero_prompt_choice_status",
            "selected_first_hero_skill",
            "hero_prompt_choice_summary",
            "remaining_core_hero_skills",
            "hero_prompt_choices",
            "choosing and trying the first Sales hero prompt",
            "other_hero_prompts",
            "Other hero prompts",
            "core_onboarding",
            "complete_sales_core_onboarding",
            "#core-onboarding-reminder",
            "initial_resource_discovery",
            "DAILY_TIPS_AUTOMATION_ID",
            "SCHEDULED_HELP_AUTOMATION_IDS",
            "ONBOARDING_AUTOMATION_IDS",
            "sales_automation_setup_status",
            "compact_source_categories",
            "build_connector_confirmation",
            "plugin_or_app_or_connector_then_manual_context",
            "parse_automation_config",
            "compact_automation_state",
            "summarize_user_context",
            "weekly_sales_company_research",
            "USER_FACING_SKILLS",
            "CORE_ONBOARDING_SKILLS",
            "POST_COMPLETION_GUIDED_SKILLS",
            "build_current_skill_experience",
            "current_skill_experience",
        ):
            if phrase not in preflight_text:
                failures.append(
                    f"skills/user-context/scripts/sales_preflight.py missing progress helper wording: {phrase}"
                )

    if legacy_source_categories.exists():
        failures.append(
            "Legacy source category reference still exists: references/source-categories.md"
        )
    if legacy_source_category_catalog.exists():
        failures.append(
            "Legacy source category catalog still exists: references/source-category-catalog.md"
        )
    if legacy_audience_reference.exists():
        failures.append(
            "Legacy audience reference still exists: references/audience-and-language.md"
        )
    if legacy_top_level_references.exists():
        failures.append("Legacy top-level references directory still exists: references")
    if legacy_top_level_scripts.exists():
        failures.append("Legacy top-level scripts directory still exists: scripts")
    if legacy_root_author_config.exists():
        failures.append("Legacy root author config directory still exists: plugin-author-config")
    if legacy_source_category_config_md.exists():
        failures.append(
            "Legacy Markdown source category config still exists: skills/user-context/plugin-author-config/source-category-config.md"
        )
    if legacy_category_state_template.exists():
        failures.append(
            "Duplicate category-state template still exists: skills/user-context/references/category-state-template.json"
        )

    declared_app_aliases: set[str] = set()
    if not app_manifest.exists():
        failures.append("Missing app manifest: .app.json")
    else:
        try:
            app_manifest_config = json.loads(app_manifest.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            failures.append(f".app.json is invalid JSON: {exc}")
            app_manifest_config = {}
        declared_apps = app_manifest_config.get("apps")
        if not isinstance(declared_apps, dict) or not declared_apps:
            failures.append(".app.json must define a non-empty apps object")
        else:
            for app_key in declared_apps:
                if isinstance(app_key, str):
                    declared_app_aliases.update(app_name_aliases(app_key))

    if not source_category_config.exists():
        failures.append(
            "Missing source category config: skills/user-context/plugin-author-config/source-category-config.json"
        )
    else:
        try:
            source_config = json.loads(source_category_config.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            failures.append(
                f"skills/user-context/plugin-author-config/source-category-config.json is invalid JSON: {exc}"
            )
            source_config = {}
        source_text = json.dumps(source_config, sort_keys=True)
        if source_config.get("schema_version") != "sales_source_category_config.v1":
            failures.append(
                "skills/user-context/plugin-author-config/source-category-config.json missing schema_version sales_source_category_config.v1"
            )
        categories = source_config.get("categories")
        if not isinstance(categories, dict) or not categories:
            failures.append(
                "skills/user-context/plugin-author-config/source-category-config.json must define a non-empty categories object"
            )
        for phrase in (
            "## Category Authoring Schema",
            "Required for:",
            "Recommended for:",
            "## Workflow Posture",
            "## Setup Strength",
            "## Runtime Resolution",
            "## State Shape",
            "native connector/app MCP tool",
            "adjacent connector",
            "Do not use Computer Use",
            "browser automation",
            "- Typical apps:",
            "Use these importance values:",
            "`recommended`:",
        ):
            if phrase in source_text:
                failures.append(
                    f"skills/user-context/plugin-author-config/source-category-config.json contains deprecated source-category wording: {phrase}"
                )
        if "user_importance" in source_text:
            failures.append(
                "skills/user-context/plugin-author-config/source-category-config.json must not use user_importance"
            )
        if "- Priority:" in source_text:
            failures.append(
                "skills/user-context/plugin-author-config/source-category-config.json must not use source-category Priority fields"
            )

        for phrase in (
            "Importance:",
            "- Priority:",
            "Required for:",
            "Recommended for:",
            "## Workflow Posture",
            "user_importance",
        ):
            if phrase in source_text:
                failures.append(
                    f"skills/user-context/plugin-author-config/source-category-config.json must not define workflow-specific or user-specific source posture: {phrase}"
                )
        if isinstance(categories, dict):
            for category_id, metadata in categories.items():
                if not isinstance(category_id, str) or not category_id:
                    failures.append(
                        "skills/user-context/plugin-author-config/source-category-config.json has an invalid category id"
                    )
                    continue
                if not isinstance(metadata, dict):
                    failures.append(
                        f"skills/user-context/plugin-author-config/source-category-config.json category {category_id} must be an object"
                    )
                    continue
                required_category_fields = (
                    "label",
                    "preferred_apps",
                )
                for field in required_category_fields:
                    if field not in metadata:
                        failures.append(
                            f"skills/user-context/plugin-author-config/source-category-config.json category {category_id} missing: {field}"
                        )
                if not isinstance(metadata.get("preferred_apps"), list):
                    failures.append(
                        f"skills/user-context/plugin-author-config/source-category-config.json category {category_id} preferred_apps must be a list"
                    )
                elif declared_app_aliases:
                    for preferred_app in metadata["preferred_apps"]:
                        if not isinstance(preferred_app, str) or not preferred_app:
                            failures.append(
                                f"skills/user-context/plugin-author-config/source-category-config.json category {category_id} preferred_apps must contain non-empty strings"
                            )
                            continue
                        if not app_name_aliases(preferred_app) & declared_app_aliases:
                            failures.append(
                                f"skills/user-context/plugin-author-config/source-category-config.json category {category_id} preferred app {preferred_app} is not declared in .app.json"
                            )
                if "preferred_plugins" in metadata:
                    preferred_plugins = metadata.get("preferred_plugins")
                    if not isinstance(preferred_plugins, list):
                        failures.append(
                            f"skills/user-context/plugin-author-config/source-category-config.json category {category_id} preferred_plugins must be a list"
                        )
                    else:
                        for preferred_plugin in preferred_plugins:
                            if not isinstance(preferred_plugin, str) or not preferred_plugin:
                                failures.append(
                                    f"skills/user-context/plugin-author-config/source-category-config.json category {category_id} preferred_plugins must contain non-empty strings"
                                )
                relevant_skills = metadata.get("relevant_skills", [])
                if "relevant_skills" in metadata:
                    if not isinstance(relevant_skills, list):
                        failures.append(
                            f"skills/user-context/plugin-author-config/source-category-config.json category {category_id} relevant_skills must be a list"
                        )
                    else:
                        for index, entry in enumerate(relevant_skills):
                            if not isinstance(entry, dict):
                                failures.append(
                                    f"skills/user-context/plugin-author-config/source-category-config.json category {category_id} relevant_skills[{index}] must be an object"
                                )
                                continue
                            if not isinstance(entry.get("app"), str) or not entry.get("app"):
                                failures.append(
                                    f"skills/user-context/plugin-author-config/source-category-config.json category {category_id} relevant_skills[{index}] missing app"
                                )
                            if not isinstance(entry.get("skill"), str) or not entry.get("skill"):
                                failures.append(
                                    f"skills/user-context/plugin-author-config/source-category-config.json category {category_id} relevant_skills[{index}] missing skill"
                                )
                for removed_field in ("why_it_matters", "most_useful_for", "verification_note"):
                    if removed_field in metadata:
                        failures.append(
                            f"skills/user-context/plugin-author-config/source-category-config.json category {category_id} should not define {removed_field}; keep category config to label, preferred_plugins, preferred_apps, and relevant_skills"
                        )
                if "typical_apps" in metadata:
                    failures.append(
                        f"skills/user-context/plugin-author-config/source-category-config.json category {category_id} must use preferred_apps, not typical_apps"
                    )

    if not user_context_config.exists():
        failures.append(
            "Missing user context config: skills/user-context/plugin-author-config/user-context-config.md"
        )
    else:
        user_context_config_text = user_context_config.read_text(encoding="utf-8")
        for phrase in (
            "# Sales User Context Config",
            "## Category Entry Shape",
            "## Default Categories",
            "- Description:",
        ):
            if phrase not in user_context_config_text:
                failures.append(
                    f"skills/user-context/plugin-author-config/user-context-config.md missing author-friendly category field: {phrase}"
                )
        for deprecated_phrase in (
            "\n## User Resources",
            "\n## Saved Links And Context",
            "\nStatus: Not Provided",
            "\nstatus: not provided",
            "\n- Priority:",
            "\n- Use When:",
        ):
            if deprecated_phrase in user_context_config_text:
                failures.append(
                    f"skills/user-context/plugin-author-config/user-context-config.md contains generated user-context detail that belongs in init_user_context_state.py: {deprecated_phrase.strip()}"
                )

    if not automation_config.exists():
        failures.append(
            "Missing automation config: skills/user-context/plugin-author-config/automation-config.md"
        )
    else:
        automation_text = automation_config.read_text(encoding="utf-8")
        for phrase in (
            "## Default Automations",
            "## Later Journey Automations",
            "- Name:",
            "- Frequency:",
            "- Instructions:",
            "daily_sales_tips",
            "daily_meeting_prep",
            "weekly_sales_company_research",
            "Load and follow `$sales:suggest-sales-next-step`",
            "scheduled Sales check-in mode",
            "short natural-language check-in",
            "next Sales workflow worth trying",
            "Load and follow `$sales:sales-company-research`",
            "scheduled research mode",
            "dynamic source discovery",
            "Sales user-context save policy",
            "coverage-note guidance",
            "compare against entries already flagged or saved from this pinned thread",
            "Load and follow `$sales:prepare-for-meeting`",
        ):
            if phrase not in automation_text:
                failures.append(
                    f"skills/user-context/plugin-author-config/automation-config.md missing author-friendly automation field: {phrase}"
                )
        for deprecated_phrase in (
            "Use GPT-5.5 with",
            "- Target thread title:",
            "- Kind:",
            "- RRULE:",
            "- Skill:",
            "- Scheduled mode:",
            "- Prompt:",
            "Onboarding notification:",
            "Sales company research is complete. {N} new resources saved.",
        ):
            if deprecated_phrase in automation_text:
                failures.append(
                    f"skills/user-context/plugin-author-config/automation-config.md contains runtime/setup detail that belongs in automation.md or onboarding state: {deprecated_phrase}"
                )

    if not automation_reference.exists():
        failures.append(
            "Missing automation reference: skills/user-context/references/automation.md"
        )
    else:
        automation_reference_text = automation_reference.read_text(encoding="utf-8")
        for phrase in (
            '`model="gpt-5.5"`',
            '`thinking="low"`',
            '`thinking="xhigh"`',
            "do not fall back to `gpt-5`",
            "## Default Setup",
            "## Fast Setup Checklist",
            "Dedicated projectless thread titled `Sales Company Research`",
            "Dedicated projectless thread titled `Sales Tips`",
            "dedicated pinned thread titled `Sales Daily Meeting Prep`",
            "Discover `automation_update` and the thread tools",
            "Create or update the automation with `kind=\"heartbeat\"`",
            "the exact `targetThreadId`",
            "stored `target_thread_id` matches the pinned thread",
            "Update `onboarding-state.json` with only operational metadata",
            "Stop. Report the concise setup result",
            "No setup kickoff; let the first scheduled check-in run on its own",
            "Do not send an immediate Sales Tips kickoff during onboarding",
            "missing first Sales Company Research kickoff",
            "Do not mark setup complete after a plain cron automation",
            "Sales Company Research: load and follow `$sales:sales-company-research`",
            "Do not paste source-family lists, ranking rules, save gates, output examples, model names, reasoning effort, or focused-skill workflow contracts",
        ):
            if phrase not in automation_reference_text:
                failures.append(
                    f"skills/user-context/references/automation.md missing runtime automation wording: {phrase}"
                )

    if not source_category_runtime.exists():
        failures.append(
            "Missing source category runtime reference: skills/user-context/references/source-category-runtime.md"
        )
    else:
        runtime_text = source_category_runtime.read_text(encoding="utf-8")
        for phrase in (
            "## Runtime Source Resolution",
            "## Onboarding Connector Confirmation",
            "## Relevant Skills",
            "## Durable Source Preferences",
            "## Onboarding Behavior",
            "## Plugin-First Setup For Missing Sources",
            "source-category-config.json",
            "relevant_skills",
            "workflow needs them",
            "user-context.md",
            "do not write connector readiness state",
            "needs_confirmation",
            "functions.list_available_plugins_to_install",
            "functions.request_plugin_install",
            "Available plugins",
            "Available skills",
            "plugin_install_evidence",
            "skill_surface_evidence",
            "app_surface_evidence",
            "run_plugin_first_source_setup",
            "saved_source_preferences",
            "plugin_preference_order",
            "plugin_first_source_setup",
            "Prefer plugin candidates over connector candidates",
            "including a plugin that contains or declares a connector/app id",
            "add dedicated Sales workflow support",
            "Do not perform an eager read",
        ):
            if phrase not in runtime_text:
                failures.append(
                    f"skills/user-context/references/source-category-runtime.md missing: {phrase}"
                )

    if hero_prompts.exists():
        failures.append(
            "skills/user-context/references/hero-prompts.md should be removed; user-facing skill experience now lives with each skill"
        )

    for skill_name, default_prompt in USER_FACING_DEFAULT_PROMPTS.items():
        skill_dir = SKILLS_ROOT / skill_name
        if not skill_dir.exists():
            failures.append(f"Missing user-facing Sales skill directory: skills/{skill_name}")
            continue
        experience_file = skill_dir / "references/experience.md"
        if experience_file.exists():
            failures.append(f"skills/{skill_name}/references/experience.md should be moved inline")
        skill_file = skill_dir / "SKILL.md"
        if not skill_file.exists():
            failures.append(f"skills/{skill_name}/SKILL.md is required")
        else:
            skill_text = skill_file.read_text(encoding="utf-8")
            experience_phrases = (
                "### First-Run Banner",
                f"If Sales preflight says the {skill_name} experience has not been introduced",
                "### Next Step Guidance",
                "#### Final Continuation Invariant",
                "another active parent flow owns the final CTA",
            )
            for phrase in experience_phrases:
                if phrase not in skill_text:
                    failures.append(f"skills/{skill_name}/SKILL.md missing: {phrase}")
            if skill_name == "prioritize-accounts":
                for phrase in (
                    "### Input Parameter Confirmation",
                    "ask at most three high-impact, high-uncertainty questions",
                    "before searching connectors, reading sources, or drafting an answer",
                    "Do not treat connector/source availability",
                    "state assumptions in `Scope` instead of blocking",
                    "If the default or assumed source returns no owned open pipeline",
                    "label the result as assumption-based",
                    "Suppress any extra skill-owned final continuation when the clarification questions are already the next step",
                ):
                    if phrase not in skill_text:
                        failures.append(
                            f"skills/prioritize-accounts/SKILL.md missing input confirmation phrase: {phrase}"
                        )
        agent_file = skill_dir / "agents/openai.yaml"
        if not agent_file.exists():
            failures.append(f"skills/{skill_name}/agents/openai.yaml is required")
        elif f'default_prompt: "{default_prompt}"' not in agent_file.read_text(encoding="utf-8"):
            failures.append(
                f"skills/{skill_name}/agents/openai.yaml must use short default_prompt: {default_prompt}"
            )

    for helper_name in HELPER_OR_ROUTER_SKILLS:
        helper_experience = SKILLS_ROOT / helper_name / "references/experience.md"
        if helper_experience.exists():
            failures.append(
                f"Helper/router skill should not expose a first-run experience: skills/{helper_name}/references/experience.md"
            )

    if not meeting_prep_skill.exists():
        failures.append("Missing prepare-for-meeting skill: skills/prepare-for-meeting/SKILL.md")
    else:
        meeting_prep_skill_text = meeting_prep_skill.read_text(encoding="utf-8")
        for phrase in (
            "### Required Inputs",
            "Source access can suggest concrete candidates",
            "The skill can still produce a limited brief from user-provided details alone",
            "### First-Run Banner",
            "### Next Step Guidance",
            "### Workflow Sources",
            "## Output Shapes",
            "Clarification Stop",
            "Daily Meeting Prep is the primary accepted-brief continuation owned by this skill",
            "Do not offer meeting doc creation as the accepted-brief default while Daily Meeting Prep remains eligible",
            "if the visible continuation already offered Sales Daily Meeting Prep, treat the acknowledgement as approval",
            "record that disposition under `automations.daily_meeting_prep`",
        ):
            if phrase not in meeting_prep_skill_text:
                failures.append(f"skills/prepare-for-meeting/SKILL.md missing: {phrase}")
        if "Summary" not in meeting_prep_skill_text:
            failures.append("skills/prepare-for-meeting/SKILL.md missing summary section guidance")
        if not (
            "compact bold labels, not Markdown H1/H2/H3 headings" in meeting_prep_skill_text
            or all(
                phrase in meeting_prep_skill_text
                for phrase in (
                    "## Summary",
                    "## Goal",
                    "## Open Questions",
                    "## Proposed Agenda",
                    "## Background Context",
                )
            )
        ):
            failures.append(
                "skills/prepare-for-meeting/SKILL.md missing recognizable single-meeting output structure"
            )

    if not plugin_memory_reference.exists():
        failures.append(
            "Missing plugin memory reference: skills/user-context/references/plugin-memory.md"
        )
    else:
        plugin_memory_text = plugin_memory_reference.read_text(encoding="utf-8")
        for phrase in (
            "Plugin memory is how the Sales plugin remembers approved preferences",
            "Saved today:",
            "source-of-truth resources and answer/style preferences",
            "Discovery-derived memory may be saved by default only when it is high-confidence",
            "Do not copy saved resource lists",
            "Route company-context discovery to `sales-company-research`",
            "This reference owns the save and review gates",
            "Keep the automation prompt thin by invoking `sales-company-research`",
        ):
            if phrase not in plugin_memory_text:
                failures.append(
                    f"skills/user-context/references/plugin-memory.md missing: {phrase}"
                )

    if not sales_company_research_skill.exists():
        failures.append(
            "Missing sales-company-research skill: skills/sales-company-research/SKILL.md"
        )
    else:
        sales_company_research_text = sales_company_research_skill.read_text(encoding="utf-8")
        for phrase in (
            "name: sales-company-research",
            "Explicit-only Sales workflow",
            "Mandatory pre-answer gate:",
            "Invoke `sales:user-context` in preflight mode",
            "dynamic source discovery",
            "Do not hard-code a customer's connector stack",
            "do not append onboarding reminders or onboarding CTAs",
            "Do not stop after the first few obviously relevant docs",
            "second-pass search",
            "Keep multiple resources when they serve distinct authority lanes",
            "one-sentence utility description",
            "legal/comms/customer-facing claims guardrails",
            "Sales company research is complete. {N} new resources saved.",
            "Sales company research is complete. No new resources saved.",
            "Do not include coverage notes or operational research bookkeeping",
            "safe-use caveat",
            "Convert material limitations into concrete `Where you can help` questions",
            "What was found",
            "Where you can help",
            "up to five `Where you can help` questions",
            "Start each bullet with the resource title as a Markdown link",
            "Do not include category labels such as `saved under`",
            "Every saved resource must explain why it helps the user",
            "Do not output bare link bullets",
            "Use the output shapes above by default",
        ):
            if phrase not in sales_company_research_text:
                failures.append(
                    f"skills/sales-company-research/SKILL.md missing research workflow phrase: {phrase}"
                )
    if not sales_company_research_agent.exists():
        failures.append(
            "Missing sales-company-research agents metadata: skills/sales-company-research/agents/openai.yaml"
        )
    else:
        sales_company_research_agent_text = sales_company_research_agent.read_text(
            encoding="utf-8"
        )
        for phrase in (
            'display_name: "Sales Company Research"',
            "allow_implicit_invocation: false",
        ):
            if phrase not in sales_company_research_agent_text:
                failures.append(
                    f"skills/sales-company-research/agents/openai.yaml missing: {phrase}"
                )

    if not call_followup_skill.exists():
        failures.append("Missing call-followup skill: skills/follow-up-after-call/SKILL.md")
    else:
        call_output_text = call_followup_skill.read_text(encoding="utf-8")
        for phrase in (
            "Primary evidence` should name the source lane and source handle",
            "clickable Markdown link when the connector exposes a useful URL",
            "email body formatted as block quote text",
            "Format the verbatim email body as a Markdown block quote",
            "### External Comms",
            "Not applicable: this was an internal call.",
            "### Internal Follow-Up",
            "Format the verbatim internal follow-up draft as a Markdown block quote",
            "internal follow-up draft is a team meeting recap",
            "Include a brief summary, next steps, owners or TBDs",
            "Call notes: no useful link available",
            "standard bold section labels",
            "`**Next Steps**`",
            "narrow, low-risk accepted preferences can be summarized and saved automatically",
        ):
            if phrase not in call_output_text:
                failures.append(
                    f"skills/follow-up-after-call/SKILL.md missing call-followup output contract phrase: {phrase}"
                )

    if not internal_navigation_skill.exists():
        failures.append(
            "Missing find-key-internal-sources skill: skills/find-key-internal-sources/SKILL.md"
        )
    else:
        internal_navigation_text = internal_navigation_skill.read_text(encoding="utf-8")
        for phrase in (
            "### Internal Ownership",
            "DRIs, approvers, SMEs, maintainers",
            "recurring decision forums",
            "canonical docs, escalation channels",
        ):
            if phrase not in internal_navigation_text:
                failures.append(
                    f"skills/find-key-internal-sources/SKILL.md missing ownership guidance: {phrase}"
                )

    for skill_file in skill_files:
        text = skill_file.read_text(encoding="utf-8")
        if text.count(AUDIENCE_AND_LANGUAGE_SECTION) != 1:
            failures.append(
                f"{skill_file.relative_to(PLUGIN_ROOT)} missing standardized Audience And Language guidance"
            )
        for phrase in LEGACY_AUDIENCE_LANGUAGE_PHRASES:
            if phrase in text:
                failures.append(
                    f"{skill_file.relative_to(PLUGIN_ROOT)} still has legacy audience wording: {phrase}"
                )
        if CLICKABLE_INLINE_SOURCE_PHRASE not in text:
            failures.append(
                f"{skill_file.relative_to(PLUGIN_ROOT)} missing clickable inline source guidance"
            )
        required_phrases = (
            USER_CONTEXT_REQUIRED_PHRASES
            if skill_file.parent.name == "user-context"
            else SIBLING_REQUIRED_PHRASES
        )
        if skill_file.parent.name == "user-context":
            missing = [phrase for phrase in required_phrases if phrase not in text]
        else:
            explicit_missing = [phrase for phrase in SIBLING_REQUIRED_PHRASES if phrase not in text]
            handoff_missing = [
                phrase for phrase in SIBLING_PREFLIGHT_HANDOFF_PHRASES if phrase not in text
            ]
            missing = [] if not explicit_missing or not handoff_missing else handoff_missing
        if missing:
            failures.append(f"{skill_file.relative_to(PLUGIN_ROOT)} missing: {', '.join(missing)}")
        for phrase in SOFT_ONLY_PHRASES:
            if phrase in text:
                failures.append(
                    f"{skill_file.relative_to(PLUGIN_ROOT)} still uses soft preflight wording: {phrase}"
                )
        for phrase in FORMULAIC_CLARIFICATION_PROMPT_PHRASES:
            if phrase in text:
                failures.append(
                    f"{skill_file.relative_to(PLUGIN_ROOT)} still uses formulaic clarification prompt wording: {phrase}"
                )
        if "### Source Categories" in text:
            if "This skill includes these Sales source categories:" not in text:
                failures.append(
                    f"{skill_file.relative_to(PLUGIN_ROOT)} Source Categories section must name included categories"
                )
            for phrase in (
                "Use the `source_category_plan` returned by Sales preflight for source-category labels",
                "At runtime, use the `source_category_plan` returned by Sales preflight when available",
                "### Provider Guides\n\n- If `crm` resolves to HubSpot",
            ):
                if phrase in text:
                    failures.append(
                        f"{skill_file.relative_to(PLUGIN_ROOT)} still has legacy source-category boilerplate: {phrase}"
                    )

    if failures:
        print("Sales user-context preflight validation failed:")
        for failure in failures:
            print(f"- {failure}")
        return 1

    print(f"Sales user-context preflight validation passed for {len(skill_files)} skills.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
