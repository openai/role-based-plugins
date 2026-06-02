from __future__ import annotations

import importlib.util
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SKILL_ROOT = Path(__file__).resolve().parents[1]
SCRIPT_DIR = SKILL_ROOT / "scripts"
PLUGIN_ROOT = SKILL_ROOT.parents[1]
ONBOARDING_REFERENCE = SKILL_ROOT / "references/onboarding.md"
SOURCE_RUNTIME_REFERENCE = SKILL_ROOT / "references/source-category-runtime.md"
AUTOMATION_REFERENCE = SKILL_ROOT / "references/automation.md"
SOURCE_CATEGORY_CONFIG = SKILL_ROOT / "plugin-author-config/source-category-config.json"
APP_MANIFEST = PLUGIN_ROOT / ".app.json"
SEMANTIC_LAYER_SETUP_REFERENCE = SKILL_ROOT / "references/semantic-layer/setup.md"
SEMANTIC_LAYER_SOURCE_INTAKE_REFERENCE = SKILL_ROOT / "references/semantic-layer/source-intake.md"
SEMANTIC_LAYER_SKILL_TEMPLATE_REFERENCE = SKILL_ROOT / "references/semantic-layer/skill-template.md"
SEMANTIC_LAYER_WEEKLY_POLLING_REFERENCE = (
    SKILL_ROOT / "references/semantic-layer/weekly-polling-automation.md"
)
HERO_SKILLS = (
    PLUGIN_ROOT / "skills/metric-diagnostics/SKILL.md",
    PLUGIN_ROOT / "skills/product-business-analysis/SKILL.md",
    PLUGIN_ROOT / "skills/kpi-reporting/SKILL.md",
)
PREFLIGHT_SPEC = importlib.util.spec_from_file_location(
    "data_analytics_preflight",
    SCRIPT_DIR / "data_analytics_preflight.py",
)
assert PREFLIGHT_SPEC and PREFLIGHT_SPEC.loader
PREFLIGHT_MODULE = importlib.util.module_from_spec(PREFLIGHT_SPEC)
PREFLIGHT_SPEC.loader.exec_module(PREFLIGHT_MODULE)

# Representative functions.list_available_plugins_to_install fixture for plugin-first routing.
LIVE_INSTALLABLE_PLUGIN_CANDIDATES = [
    {
        "id": "databricks@openai-curated",
        "name": "databricks",
        "tool_type": "plugin",
        "has_skills": True,
        "app_connector_ids": ["templated_apps_Databricks"],
    },
    {
        "id": "bigquery@openai-curated",
        "name": "bigquery",
        "tool_type": "plugin",
        "has_skills": True,
        "app_connector_ids": ["connector_7c3f2c8cdbf64bb0b183ff52f527a06e"],
    },
    {
        "id": "snowflake@openai-curated",
        "name": "snowflake",
        "tool_type": "plugin",
        "has_skills": True,
        "app_connector_ids": ["templated_apps_Snowflake"],
    },
    {
        "id": "outlook-calendar@openai-curated",
        "name": "outlook-calendar",
        "tool_type": "plugin",
        "has_skills": True,
        "app_connector_ids": ["connector_e6a7394682e24467ac68c60696f275a4"],
    },
    {
        "id": "outlook-email@openai-curated",
        "name": "outlook-email",
        "tool_type": "plugin",
        "has_skills": True,
        "app_connector_ids": ["connector_4aaab2856305417b993eca9a216aaf6e"],
    },
    {
        "id": "sharepoint@openai-curated",
        "name": "sharepoint",
        "tool_type": "plugin",
        "has_skills": True,
        "app_connector_ids": ["connector_1e4f6a44acf14e3ca1d96672f8c945bc"],
    },
    {
        "id": "slack@openai-curated",
        "name": "slack",
        "tool_type": "plugin",
        "has_skills": True,
        "app_connector_ids": ["REPLACE_WITH_SLACK_APP_OR_CONNECTOR_ID"],
    },
    {
        "id": "teams@openai-curated",
        "name": "teams",
        "tool_type": "plugin",
        "has_skills": True,
        "app_connector_ids": ["connector_246af0940da3457da0e751171dc1ce60"],
    },
    {
        "id": "thoughtspot@openai-curated",
        "name": "thoughtspot",
        "tool_type": "plugin",
        "has_skills": True,
        "app_connector_ids": ["REPLACE_WITH_THOUGHTSPOT_APP_OR_CONNECTOR_ID"],
    },
    {
        "id": "omni-analytics@openai-curated",
        "name": "omni-analytics",
        "tool_type": "plugin",
        "has_skills": True,
        "app_connector_ids": ["REPLACE_WITH_OMNI_ANALYTICS_APP_OR_CONNECTOR_ID"],
    },
    {
        "id": "metabase@openai-curated",
        "name": "metabase",
        "tool_type": "plugin",
        "has_skills": True,
        "app_connector_ids": ["templated_apps_Metabase"],
    },
    {
        "id": "amplitude@openai-curated",
        "name": "amplitude",
        "tool_type": "plugin",
        "has_skills": True,
        "app_connector_ids": ["REPLACE_WITH_AMPLITUDE_APP_OR_CONNECTOR_ID"],
    },
    {
        "id": "mixpanel@openai-curated",
        "name": "mixpanel",
        "tool_type": "plugin",
        "has_skills": True,
        "app_connector_ids": ["REPLACE_WITH_MIXPANEL_APP_OR_CONNECTOR_ID"],
    },
    {
        "id": "hex@openai-curated",
        "name": "hex",
        "tool_type": "plugin",
        "has_skills": True,
        "app_connector_ids": ["REPLACE_WITH_HEX_APP_OR_CONNECTOR_ID"],
    },
    {
        "id": "deepnote@openai-curated",
        "name": "deepnote",
        "tool_type": "plugin",
        "has_skills": True,
        "app_connector_ids": ["REPLACE_WITH_DEEPNOTE_APP_OR_CONNECTOR_ID"],
    },
]
SESSION_ENABLED_PLUGIN_CANDIDATES = [
    {"id": "github@openai-curated", "name": "github", "tool_type": "plugin"},
    {"id": "gmail@openai-curated", "name": "gmail", "tool_type": "plugin"},
    {"id": "google-calendar@openai-curated", "name": "google-calendar", "tool_type": "plugin"},
    {"id": "google-drive@openai-curated", "name": "google-drive", "tool_type": "plugin"},
    {"id": "notion@openai-curated", "name": "notion", "tool_type": "plugin"},
]


class DataAnalyticsStateHelperTests(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory(
            prefix="data-analytics-user-context-tests-",
            dir="/private/tmp",
        )
        self.tmp_path = Path(self._tmp.name)
        self.state_dir = self.tmp_path / "state"
        self.maxDiff = None

    def tearDown(self) -> None:
        self._tmp.cleanup()

    def run_json(self, args: list[str], *, expect: int = 0) -> dict:
        proc = subprocess.run(args, text=True, capture_output=True)
        self.assertEqual(
            proc.returncode,
            expect,
            msg=f"command failed: {' '.join(args)}\nSTDOUT:\n{proc.stdout}\nSTDERR:\n{proc.stderr}",
        )
        return json.loads(proc.stdout)

    def preflight(self, *extra: str, state_dir: Path | None = None) -> dict:
        return self.run_json(
            [
                sys.executable,
                str(SCRIPT_DIR / "data_analytics_preflight.py"),
                "--workflow",
                "metric-diagnostics",
                "--state-dir",
                str(state_dir or self.state_dir),
                *extra,
            ]
        )

    def write_state(
        self,
        *,
        user_context: str | None = None,
        onboarding_state: dict | None = None,
        state_dir: Path | None = None,
    ) -> Path:
        target = state_dir or self.state_dir
        target.mkdir(parents=True, exist_ok=True)
        if user_context is not None:
            (target / "user-context.md").write_text(user_context, encoding="utf-8")
        if onboarding_state is not None:
            (target / "onboarding-state.json").write_text(
                json.dumps(onboarding_state),
                encoding="utf-8",
            )
        return target

    def active_core_categories(self) -> dict[str, dict[str, str]]:
        return {
            "structured_data": {"status": "active", "preferred": "Databricks"},
            "team_communication": {"status": "active", "preferred": "Slack"},
            "company_docs": {"status": "active", "preferred": "Google Drive"},
        }

    def source_category_config(self) -> dict:
        return json.loads(SOURCE_CATEGORY_CONFIG.read_text(encoding="utf-8"))["categories"]

    def test_missing_preflight_returns_setup_obligation_context_gap_and_empty_hero_prompt(
        self,
    ) -> None:
        payload = self.preflight(state_dir=self.tmp_path / "missing")
        self.assertTrue(payload["read_only"])
        self.assertEqual(payload["state"]["user_context_status"], "missing")
        self.assertEqual(payload["state"]["onboarding_state_status"], "missing")
        self.assertTrue(payload["current_skill_experience"]["intro_eligible"])
        obligation = payload["control"]["final_obligations"][0]
        self.assertEqual(obligation["id"], "offer_data_analytics_onboarding_next_step")
        self.assertIn("## Data Analytics Setup Required", obligation["template"])
        self.assertEqual(payload["control"]["conditional_guidance"][0]["id"], "context_gap_note")
        self.assertEqual(payload["context"]["hero_prompt_candidates"], [])
        self.assertIsNone(payload["context"]["primary_hero_prompt"])
        self.assertEqual(
            payload["context"]["connector_setup_summary"]["needs_attention"][0]["status"],
            "needs_confirmation",
        )

    def test_direct_and_guided_modes_suppress_ordinary_setup_obligation(self) -> None:
        direct_payload = self.preflight("--request-mode", "direct_onboarding_status")
        guided_payload = self.preflight("--request-mode", "guided_onboarding_workflow")
        self.assertEqual(direct_payload["control"]["final_obligations"], [])
        self.assertEqual(guided_payload["control"]["final_obligations"], [])
        self.assertEqual(direct_payload["control"]["conditional_guidance"], [])
        self.assertEqual(guided_payload["control"]["conditional_guidance"], [])
        self.assertEqual(guided_payload["current_skill_experience"]["cta_owner"], "onboarding")

    def test_legacy_verified_connector_status_maps_to_active_try_on_use(self) -> None:
        self.assertEqual(
            PREFLIGHT_MODULE.source_status({"status": "connected"}),
            "active",
        )
        self.assertEqual(PREFLIGHT_MODULE.source_status({"status": "manual"}), "active")
        self.assertEqual(
            PREFLIGHT_MODULE.source_status({"status": "selected_needs_auth"}),
            "needs_confirmation",
        )
        self.assertEqual(PREFLIGHT_MODULE.source_status({"status": "choose_source"}), "needs_confirmation")

    def test_configured_plugin_routes_are_manifest_backed_and_add_google_calendar(
        self,
    ) -> None:
        categories = self.source_category_config()
        self.assertEqual(categories["team_communication"]["preferred_plugins"], ["Slack", "Teams"])
        self.assertEqual(
            categories["company_docs"]["preferred_plugins"],
            ["Google Drive", "SharePoint", "Notion"],
        )
        self.assertEqual(
            categories["email_context"]["preferred_plugins"],
            ["Gmail", "Outlook Email"],
        )
        self.assertEqual(
            categories["calendar_context"]["preferred_plugins"],
            ["Google Calendar", "Outlook Calendar"],
        )
        self.assertNotIn("preferred_apps", categories["calendar_context"])
        self.assertEqual(categories["code_repository"]["preferred_plugins"], ["GitHub"])
        app_manifest = json.loads(APP_MANIFEST.read_text(encoding="utf-8"))
        self.assertEqual(
            app_manifest["apps"]["google_calendar"]["id"],
            "connector_947e0d954944416db111db556030eea6",
        )
        self.assertEqual(
            PREFLIGHT_MODULE.load_app_connector_ids()["googlecalendar"],
            "connector_947e0d954944416db111db556030eea6",
        )

    def test_live_install_listing_fixture_matches_every_installable_data_analytics_plugin(
        self,
    ) -> None:
        matches = PREFLIGHT_MODULE.match_installable_plugin_candidates(
            self.source_category_config(),
            {"tools": LIVE_INSTALLABLE_PLUGIN_CANDIDATES},
        )
        self.assertEqual(
            {
                category_id: [entry["preferred_plugin"] for entry in entries]
                for category_id, entries in matches.items()
            },
            {
                "structured_data": ["Databricks", "BigQuery", "Snowflake"],
                "team_communication": ["Slack", "Teams"],
                "company_docs": ["SharePoint"],
                "dashboards_bi": ["ThoughtSpot", "Omni Analytics", "Metabase"],
                "behavior_signals": ["Amplitude", "Mixpanel"],
                "notebook_lab": ["Hex", "Deepnote"],
                "email_context": ["Outlook Email"],
                "calendar_context": ["Outlook Calendar"],
            },
        )

    def test_configured_plugins_match_installable_or_enabled_plugin_surfaces(self) -> None:
        categories = self.source_category_config()
        matches = PREFLIGHT_MODULE.match_installable_plugin_candidates(
            categories,
            [*LIVE_INSTALLABLE_PLUGIN_CANDIDATES, *SESSION_ENABLED_PLUGIN_CANDIDATES],
        )
        self.assertEqual(
            {
                category_id: [entry["preferred_plugin"] for entry in entries]
                for category_id, entries in matches.items()
            },
            {
                category_id: metadata["preferred_plugins"]
                for category_id, metadata in categories.items()
                if metadata.get("preferred_plugins")
            },
        )

    def test_plugin_candidate_matching_uses_connector_id_when_slug_changes(self) -> None:
        matches = PREFLIGHT_MODULE.match_installable_plugin_candidates(
            self.source_category_config(),
            [
                {
                    "id": "renamed-plugin@openai-curated",
                    "name": "renamed-plugin",
                    "tool_type": "plugin",
                    "app_connector_ids": ["REPLACE_WITH_SLACK_APP_OR_CONNECTOR_ID"],
                }
            ],
        )
        slack_match = matches["team_communication"][0]
        self.assertEqual(slack_match["preferred_plugin"], "Slack")
        self.assertEqual(slack_match["match_reasons"], ["app_connector_id"])

    def test_plugin_candidate_matching_ignores_description_only_category_similarity(self) -> None:
        matches = PREFLIGHT_MODULE.match_installable_plugin_candidates(
            self.source_category_config(),
            [
                {
                    "id": "broad-search@openai-curated",
                    "name": "broad-search",
                    "display_name": "Broad Search",
                    "description": "Indexes Slack and Teams for team communication.",
                    "tool_type": "plugin",
                    "has_skills": True,
                }
            ],
        )
        self.assertNotIn("team_communication", matches)

    def test_preflight_exposes_plugin_setup_before_connector_fallback(self) -> None:
        payload = self.preflight(state_dir=self.tmp_path / "missing")
        confirmation = payload["context"]["connector_confirmation"]
        slack = confirmation["team_communication"]
        self.assertEqual(slack["setup_action"], "run_plugin_first_source_setup")
        self.assertEqual(
            slack["fallback_setup_action"],
            "ask_user_to_choose_or_confirm_source",
        )
        self.assertEqual(slack["plugin_preference_order"], ["Slack", "Teams"])
        self.assertEqual(
            slack["setup_recovery"]["candidate_lookup"],
            "functions.list_available_plugins_to_install",
        )
        self.assertEqual(
            slack["setup_recovery"]["install_request"],
            "functions.request_plugin_install",
        )
        calendar = confirmation["calendar_context"]
        self.assertEqual(
            calendar["plugin_preference_order"],
            ["Google Calendar", "Outlook Calendar"],
        )
        self.assertIn(
            "team_communication",
            {
                entry["id"]
                for entry in payload["context"]["connector_setup_summary"][
                    "plugin_setup_opportunities"
                ]
            },
        )

    def test_preflight_keeps_onboarding_state_provenance_without_raw_state_echo(self) -> None:
        self.write_state(onboarding_state={"status": "active", "connector_confirmation": {}})
        payload = self.preflight()
        onboarding_state = payload["files"]["onboarding_state"]
        self.assertEqual(onboarding_state["status"], "present")
        self.assertFalse(onboarding_state["omitted"])
        self.assertNotIn("content", onboarding_state)
        self.assertNotIn("data", onboarding_state)
        self.assertNotIn(
            "setup_recovery",
            payload["context"]["connector_setup_summary"]["needs_attention"][0],
        )
        self.assertIn(
            "setup_recovery",
            payload["context"]["connector_confirmation"]["structured_data"],
        )

    def test_connector_inventory_classifies_routes_without_eager_reads(self) -> None:
        self.write_state(
            onboarding_state={
                "status": "active",
                "connector_inventory": {
                    "active_apps": ["Slack"],
                    "available_apps": ["Databricks"],
                },
            }
        )
        payload = self.preflight("--request-mode", "direct_onboarding_status")
        confirmation = payload["context"]["connector_confirmation"]

        self.assertEqual(confirmation["structured_data"]["status"], "needs_confirmation")
        self.assertEqual(confirmation["structured_data"]["candidates"], ["Databricks"])
        self.assertEqual(confirmation["team_communication"]["status"], "needs_confirmation")
        self.assertEqual(confirmation["team_communication"]["candidates"], ["Slack"])
        self.assertEqual(confirmation["company_docs"]["status"], "missing")
        self.assertFalse(confirmation["structured_data"]["eager_read"])
        self.assertEqual(
            confirmation["structured_data"]["workflow_time_behavior"],
            "attempt_actual_reads_only_when_a_workflow_needs_the_source",
        )

    def test_helper_skills_apply_to_app_fallback_but_not_active_plugin_routes(self) -> None:
        source_config = {
            "team_communication": {
                "label": "Team communication",
                "preferred_plugins": ["slack"],
                "preferred_apps": ["Slack"],
                "relevant_skills": [{"app": "Slack", "skill": "slack-helper"}],
            }
        }
        connector_fallback = PREFLIGHT_MODULE.normalized_connector_confirmation(
            source_config,
            {
                "connector_confirmation": {
                    "categories": {
                        "team_communication": {
                            "status": "active",
                            "preferred": "Slack",
                            "source_kind": "connector",
                        }
                    }
                }
            },
        )["team_communication"]
        self.assertEqual(connector_fallback["setup_action"], "run_plugin_first_source_setup")
        self.assertEqual(connector_fallback["fallback_setup_action"], "none_try_on_use")
        self.assertEqual(connector_fallback["helper_skills_apply_when"], ["app", "connector"])

        plugin_route = PREFLIGHT_MODULE.normalized_connector_confirmation(
            source_config,
            {
                "connector_confirmation": {
                    "categories": {
                        "team_communication": {
                            "status": "active",
                            "preferred": "slack",
                            "source_kind": "plugin",
                            "plugin_install_evidence": "plugin_in_available_plugins",
                            "skill_surface_evidence": "plugin_skills_visible",
                        }
                    }
                }
            },
        )["team_communication"]
        self.assertEqual(plugin_route["setup_action"], "none_try_on_use")
        self.assertNotIn("fallback_setup_action", plugin_route)
        self.assertNotIn("setup_recovery", plugin_route)
        self.assertNotIn("helper_skills", plugin_route)

    def test_validator_rejects_preferred_plugin_without_manifest_dependency(self) -> None:
        plugin_copy = self.tmp_path / "data-analytics"
        shutil.copytree(PLUGIN_ROOT, plugin_copy)
        config_path = plugin_copy / "skills/user-context/plugin-author-config/source-category-config.json"
        config = json.loads(config_path.read_text(encoding="utf-8"))
        config["categories"]["calendar_context"]["preferred_plugins"].append("missing-calendar")
        config_path.write_text(json.dumps(config, indent=2) + "\n", encoding="utf-8")
        proc = subprocess.run(
            [
                sys.executable,
                str(SCRIPT_DIR / "validate_user_context_preflight.py"),
                str(plugin_copy),
                "--plugin-id",
                "data-analytics",
            ],
            text=True,
            capture_output=True,
        )
        self.assertNotEqual(proc.returncode, 0)
        self.assertIn(
            "preferred plugin missing-calendar must be declared in .app.json",
            proc.stderr,
        )

    def test_validator_rejects_preferred_app_without_manifest_dependency(self) -> None:
        plugin_copy = self.tmp_path / "data-analytics"
        shutil.copytree(PLUGIN_ROOT, plugin_copy)
        config_path = plugin_copy / "skills/user-context/plugin-author-config/source-category-config.json"
        config = json.loads(config_path.read_text(encoding="utf-8"))
        config["categories"]["calendar_context"]["preferred_apps"] = ["Missing Calendar"]
        config_path.write_text(json.dumps(config, indent=2) + "\n", encoding="utf-8")
        proc = subprocess.run(
            [
                sys.executable,
                str(SCRIPT_DIR / "validate_user_context_preflight.py"),
                str(plugin_copy),
                "--plugin-id",
                "data-analytics",
            ],
            text=True,
            capture_output=True,
        )
        self.assertNotEqual(proc.returncode, 0)
        self.assertIn(
            "preferred app Missing Calendar must be declared in .app.json",
            proc.stderr,
        )

    def test_validator_rejects_saved_context_heading_in_author_config(self) -> None:
        plugin_copy = self.tmp_path / "data-analytics"
        shutil.copytree(PLUGIN_ROOT, plugin_copy)
        config_path = plugin_copy / "skills/user-context/plugin-author-config/user-context-config.md"
        config = config_path.read_text(encoding="utf-8")
        config_path.write_text(
            config.replace(
                "# Semantic Layers\n\n",
                "# Semantic Layers\n\n## Saved Links And Context\n\n",
                1,
            ),
            encoding="utf-8",
        )
        proc = subprocess.run(
            [
                sys.executable,
                str(SCRIPT_DIR / "validate_user_context_preflight.py"),
                str(plugin_copy),
                "--plugin-id",
                "data-analytics",
            ],
            text=True,
            capture_output=True,
        )
        self.assertNotEqual(proc.returncode, 0)
        self.assertIn("default user context must not contain: ## Saved Links And Context", proc.stderr)

    def test_selected_source_needs_confirmation_stays_unresolved_until_user_resolves_it(
        self,
    ) -> None:
        self.write_state(
            user_context="""# Data Analytics Source Routing Preferences

Store durable Data Analytics source-routing choices explicitly selected for future use.

## structured_data

- Prefer:
- Avoid:

# Semantic Layers

status: not provided
""",
            onboarding_state={
                "status": "active",
                "orientation": {"status": "shown"},
                "connector_confirmation": {
                    "structured_data": {
                        "status": "needs_confirmation",
                        "preferred": "Databricks",
                    },
                    "team_communication": {"status": "active", "preferred": "Slack"},
                    "company_docs": {"status": "active", "preferred": "Google Drive"},
                },
            },
        )
        payload = self.preflight()
        summary = payload["context"]["connector_setup_summary"]
        self.assertEqual(payload["context"]["user_context"]["semantic_layer_count"], 0)
        self.assertFalse(summary["core_complete"])
        self.assertEqual(summary["next_action"]["category_id"], "structured_data")
        self.assertEqual(
            summary["next_action"]["setup_action"],
            "run_plugin_first_source_setup",
        )
        self.assertEqual(summary["needs_attention"][0]["status"], "needs_confirmation")
        self.assertNotIn(
            "structured_data",
            {entry["id"] for entry in summary["ready"]},
        )
        self.assertEqual(
            payload["control"]["final_obligations"][0]["id"],
            "complete_data_analytics_core_onboarding",
        )

    def test_unacknowledged_deferred_core_sources_reopen_as_needs_confirmation(self) -> None:
        self.write_state(
            onboarding_state={
                "status": "active",
                "orientation": {"status": "shown"},
                "connector_confirmation": {
                    "status": "completed",
                    "structured_data": {"status": "deferred"},
                    "team_communication": {"status": "deferred"},
                    "company_docs": {"status": "active", "preferred": "Google Drive"},
                },
            }
        )
        payload = self.preflight("--request-mode", "direct_onboarding_status")
        confirmation = payload["context"]["connector_confirmation"]
        summary = payload["context"]["connector_setup_summary"]
        self.assertEqual(confirmation["structured_data"]["status"], "needs_confirmation")
        self.assertEqual(confirmation["structured_data"]["recorded_status"], "deferred")
        self.assertEqual(
            confirmation["structured_data"]["setup_note"],
            "core_source_requires_explicit_user_resolution_before_fallback",
        )
        self.assertEqual(confirmation["team_communication"]["status"], "needs_confirmation")
        self.assertFalse(summary["core_complete"])
        self.assertEqual(
            summary["unresolved_core_ids"],
            ["structured_data", "team_communication"],
        )
        self.assertEqual(
            [entry["id"] for entry in summary["needs_attention"][:2]],
            ["structured_data", "team_communication"],
        )
        self.assertEqual(summary["next_action"]["category_id"], "structured_data")
        self.assertEqual(
            payload["control"]["onboarding_progress"]["task_list"][1]["status"],
            "in_progress",
        )

    def test_connector_confirmation_status_without_core_categories_stays_pending(self) -> None:
        self.write_state(
            onboarding_state={
                "status": "active",
                "orientation": {"status": "shown"},
                "connector_confirmation": {"status": "completed"},
            }
        )
        payload = self.preflight("--request-mode", "direct_onboarding_status")
        summary = payload["context"]["connector_setup_summary"]
        self.assertEqual(summary["classification_status"], "pending")
        self.assertFalse(summary["core_complete"])
        self.assertEqual(
            payload["control"]["onboarding_progress"]["task_list"][1]["status"],
            "in_progress",
        )

    def test_explicit_core_source_defer_counts_as_recorded_known_gap(self) -> None:
        self.write_state(
            onboarding_state={
                "status": "active",
                "connector_confirmation": {
                    "structured_data": {"status": "deferred", "resolution": "user_deferred"},
                    "team_communication": {
                        "status": "deferred",
                        "resolution": "user_continued_with_known_gap",
                    },
                    "company_docs": {"status": "active", "preferred": "Google Drive"},
                },
            }
        )
        payload = self.preflight("--request-mode", "direct_onboarding_status")
        confirmation = payload["context"]["connector_confirmation"]
        summary = payload["context"]["connector_setup_summary"]
        self.assertEqual(confirmation["structured_data"]["status"], "deferred")
        self.assertEqual(confirmation["structured_data"]["resolution"], "user_deferred")
        self.assertTrue(summary["core_complete"])
        self.assertEqual(summary["unresolved_core_ids"], [])
        self.assertEqual(
            {entry["id"] for entry in summary["fallback_or_closed"]},
            {"structured_data", "team_communication"},
        )

    def test_core_onboarding_complete_requires_active_or_explicit_fallback_sources(self) -> None:
        self.write_state(
            onboarding_state={
                "status": "active",
                "orientation": {"status": "shown"},
                "connector_confirmation": {
                    **self.active_core_categories(),
                },
                "semantic_layer_setup": {"status": "created"},
                "semantic_layer_refresh": {"status": "declined"},
            }
        )
        payload = self.preflight("--request-mode", "direct_onboarding_status")
        progress = payload["control"]["onboarding_progress"]
        task_statuses = {item["id"]: item["status"] for item in progress["task_list"]}
        self.assertTrue(progress["core_onboarding"]["complete"])
        self.assertEqual(task_statuses["source_setup_confirmation"], "completed")
        self.assertEqual(task_statuses["semantic_layer_setup"], "completed")
        self.assertEqual(task_statuses["hero_prompt"], "in_progress")

    def test_core_onboarding_complete_allows_semantic_layer_skip_without_refresh(self) -> None:
        self.write_state(
            onboarding_state={
                "status": "active",
                "orientation": {"status": "shown"},
                "connector_confirmation": {
                    "status": "completed",
                    **self.active_core_categories(),
                },
                "semantic_layer_setup": {"status": "skipped"},
            }
        )
        payload = self.preflight("--request-mode", "direct_onboarding_status")
        progress = payload["control"]["onboarding_progress"]
        task_statuses = {item["id"]: item["status"] for item in progress["task_list"]}
        self.assertTrue(progress["core_onboarding"]["complete"])
        self.assertEqual(task_statuses["semantic_layer_setup"], "completed")
        self.assertEqual(task_statuses["hero_prompt"], "in_progress")

    def test_active_core_incomplete_returns_single_reminder_with_next_action(self) -> None:
        self.write_state(
            user_context="""# Data Analytics Source Routing Preferences

Store durable Data Analytics source-routing choices explicitly selected for future use.

## structured_data

- Prefer:
- Avoid:

# Semantic Layers

status: not provided
""",
            onboarding_state={"status": "active", "orientation": {"status": "shown"}},
        )
        payload = self.preflight()
        obligation = payload["control"]["final_obligations"][0]
        self.assertEqual(obligation["id"], "complete_data_analytics_core_onboarding")
        self.assertEqual(obligation["next_action"]["id"], "confirm_analytics_sources")
        self.assertIn("**Next Step**", obligation["template"])
        self.assertIn("Reply `continue onboarding`", obligation["template"])
        self.assertEqual(len(payload["control"]["final_obligations"]), 1)

    def test_complete_and_quiet_onboarding_suppress_auto_obligations(self) -> None:
        for status in ("complete", "quiet"):
            with self.subTest(status=status):
                state_dir = self.tmp_path / status
                self.write_state(onboarding_state={"status": status}, state_dir=state_dir)
                payload = self.preflight(state_dir=state_dir)
                self.assertEqual(payload["control"]["final_obligations"], [])

    def test_semantic_layer_registry_and_hero_prompt_candidates_come_from_context(
        self,
    ) -> None:
        self.write_state(
            user_context="""# Data Analytics Source Routing Preferences

Store durable Data Analytics source-routing choices explicitly selected for future use.

## structured_data

- Prefer: Databricks
- Avoid: Snowflake

# Semantic Layers

- Area: API
  - Skill Name: api-semantic-layer
  - Skill Path: /tmp/api-semantic-layer
  - Source Inventory Path: /tmp/api-semantic-layer/references/source-inventory.md
  - Last Updated: 2026-05-29
""",
            onboarding_state={"status": "active", "semantic_layer_setup": {"area": "API"}},
        )
        payload = self.preflight()
        self.assertNotIn("user_context_markdown", payload["context"])
        self.assertNotIn("content", payload["files"]["user_context"])
        self.assertTrue(payload["context"]["user_context"]["normalization_complete"])
        self.assertEqual(payload["context"]["semantic_layers"][0]["area"], "API")
        self.assertEqual(payload["context"]["source_preferences"]["structured_data"], {
            "preferred": ["Databricks"],
            "avoid": ["Snowflake"],
        })
        self.assertEqual(len(payload["context"]["hero_prompt_candidates"]), 1)
        self.assertEqual(payload["context"]["primary_hero_prompt"]["skill"], "product-business-analysis")
        self.assertEqual(
            payload["context"]["primary_hero_prompt"]["label"],
            "Build a decision-ready report",
        )
        self.assertEqual(
            payload["context"]["primary_hero_prompt"]["prompt"],
            (
                "Build a decision-ready report for API: explain what is happening, "
                "identify the main drivers, recommend where the team should focus next, "
                "and include sources, caveats, and useful charts."
            ),
        )
        self.assertEqual(payload["context"]["extra_hero_prompt_candidates"], [])

    def test_large_user_context_renders_source_preferences_and_requested_section(self) -> None:
        self.write_state(
            user_context="""# Data Analytics Source Routing Preferences

Store durable Data Analytics source-routing choices explicitly selected for future use.

## structured_data

- Prefer: Databricks
- Avoid: Snowflake

## company_docs

- Prefer: Google Drive
- Avoid:

# Semantic Layers

""" + ("x" * 2048),
        )
        payload = self.preflight(
            "--max-context-bytes",
            "80",
            "--section",
            "Data Analytics Source Routing Preferences",
        )
        self.assertNotIn("user_context_markdown", payload["context"])
        self.assertNotIn("content", payload["files"]["user_context"])
        self.assertTrue(payload["files"]["user_context"]["omitted"])
        self.assertEqual(payload["files"]["user_context"]["sections"][0]["status"], "present")
        self.assertTrue(payload["context"]["user_context"]["normalization_complete"])
        self.assertEqual(
            payload["context"]["source_preferences"],
            {
                "structured_data": {
                    "preferred": ["Databricks"],
                    "avoid": ["Snowflake"],
                },
                "company_docs": {"preferred": ["Google Drive"]},
            },
        )
        self.assertEqual(
            payload["context"]["user_context"]["source_routing_preferences"],
            payload["context"]["source_preferences"],
        )

    def test_reset_moves_active_state_files(self) -> None:
        self.state_dir.mkdir(parents=True)
        user_context_path = self.state_dir / "user-context.md"
        onboarding_state_path = self.state_dir / "onboarding-state.json"
        user_context_path.write_text("# Context\n", encoding="utf-8")
        onboarding_state_path.write_text(json.dumps({"status": "active"}), encoding="utf-8")
        backup_dir = self.tmp_path / "backup"
        proc = subprocess.run(
            [
                sys.executable,
                str(SCRIPT_DIR / "reset_user_context_state.py"),
                "--state-dir",
                str(self.state_dir),
                "--backup-dir",
                str(backup_dir),
            ],
            text=True,
            capture_output=True,
        )
        self.assertEqual(proc.returncode, 0, msg=proc.stderr)
        self.assertFalse(user_context_path.exists())
        self.assertFalse(onboarding_state_path.exists())
        self.assertTrue((backup_dir / "user-context.md").exists())
        self.assertTrue((backup_dir / "onboarding-state.json").exists())

    def test_initializer_creates_user_context_and_onboarding_state(self) -> None:
        proc = subprocess.run(
            [
                sys.executable,
                str(SCRIPT_DIR / "init_user_context_state.py"),
                "--state-dir",
                str(self.state_dir),
            ],
            text=True,
            capture_output=True,
        )
        self.assertEqual(proc.returncode, 0, msg=proc.stderr)
        user_context = (self.state_dir / "user-context.md").read_text(encoding="utf-8")
        self.assertNotIn("# Data Analytics User Context Config", user_context)
        self.assertNotIn("- Priority:", user_context)
        self.assertNotIn("- Use When:", user_context)
        self.assertIn(
            "Store durable Data Analytics source-routing choices explicitly selected for future use.",
            user_context,
        )
        self.assertEqual(user_context.count("## "), 9)
        self.assertEqual(user_context.count("- Prefer:"), 9)
        self.assertEqual(user_context.count("- Avoid:"), 9)
        self.assertEqual(user_context.count("status: not provided"), 1)
        onboarding_state = json.loads((self.state_dir / "onboarding-state.json").read_text())
        self.assertEqual(onboarding_state["status"], "active")
        self.assertNotIn("connector_inventory", onboarding_state)
        self.assertNotIn("seed_sources", onboarding_state["semantic_layer_setup"])
        self.assertEqual(onboarding_state["semantic_layer_setup"]["seed_source_count"], 0)
        self.assertIn("hero_prompt_choice", onboarding_state)
        self.assertIn("skill_experience", onboarding_state)

    def test_onboarding_contract_mentions_active_sources_and_one_first_hero_prompt(
        self,
    ) -> None:
        onboarding_text = ONBOARDING_REFERENCE.read_text(encoding="utf-8")
        source_runtime_text = SOURCE_RUNTIME_REFERENCE.read_text(encoding="utf-8")
        automation_text = AUTOMATION_REFERENCE.read_text(encoding="utf-8")
        self.assertIn("Check Main Analytics Sources", onboarding_text)
        self.assertIn("Resolve Source Questions", onboarding_text)
        self.assertIn("transition without a proof read", onboarding_text)
        self.assertIn("Set Up Data Context", onboarding_text)
        self.assertIn("Codex gets better at data work", onboarding_text)
        self.assertIn("Send anything you would point a new analyst to", onboarding_text)
        self.assertIn("Reply with any starting points, or say `skip for now`", onboarding_text)
        self.assertIn("Do not: require the user to name a product or business area up front", onboarding_text)
        self.assertNotIn("smallest useful seed", onboarding_text)
        self.assertNotIn("first semantic layer", onboarding_text)
        self.assertNotIn("main source categories", onboarding_text)
        self.assertIn("Show one strong prompt first", onboarding_text)
        self.assertIn("Do not: show three hero prompts initially", onboarding_text)
        self.assertIn("write the prompt you would rather try instead", onboarding_text)
        self.assertIn("`skip` to finish onboarding", onboarding_text)
        self.assertIn("Step 5, `complete_or_quiet`, when the user skips or defers", onboarding_text)
        self.assertIn("`needs_confirmation`", source_runtime_text)
        self.assertIn("Do not run a proof query during onboarding", source_runtime_text)
        self.assertIn("Do not mark setup complete", automation_text)
        for hero_skill in HERO_SKILLS:
            text = hero_skill.read_text(encoding="utf-8")
            self.assertIn("data-analytics:user-context", text)

    def test_semantic_layer_setup_uses_lightweight_generated_skills_and_source_checkpoint(
        self,
    ) -> None:
        setup_text = SEMANTIC_LAYER_SETUP_REFERENCE.read_text(encoding="utf-8")
        source_intake_text = SEMANTIC_LAYER_SOURCE_INTAKE_REFERENCE.read_text(encoding="utf-8")
        template_text = SEMANTIC_LAYER_SKILL_TEMPLATE_REFERENCE.read_text(encoding="utf-8")
        weekly_polling_text = SEMANTIC_LAYER_WEEKLY_POLLING_REFERENCE.read_text(
            encoding="utf-8"
        )
        self.assertIn("source-use checkpoint", setup_text)
        self.assertIn("rejected or lower-confidence candidates", setup_text)
        self.assertIn("Infer expected source lanes", setup_text)
        self.assertIn("nearby but not exact", setup_text)
        self.assertIn("authoritative data documentation", setup_text)
        self.assertIn("source-backed semantic-layer skills", setup_text)
        self.assertIn("user-trusted canonical data skills", setup_text)
        self.assertIn("treat that as authoritative data documentation", setup_text)
        self.assertIn("authoritative data documentation", weekly_polling_text)
        self.assertIn("source-backed semantic-layer skills", weekly_polling_text)
        self.assertIn("user-trusted canonical data skills", weekly_polling_text)
        self.assertIn("Infer useful source families", source_intake_text)
        self.assertIn("do not treat ambient app availability as user approval", source_intake_text)
        self.assertIn("Send anything you would point a new analyst to", source_intake_text)
        self.assertIn("Reply with any starting points, or say `skip for now`", source_intake_text)
        self.assertIn("## Start Here", template_text)
        self.assertIn("## References", template_text)
        self.assertIn("Answering Rules", template_text)
        self.assertIn("## Quick Reference", template_text)
        self.assertIn("## Entity Clarification", template_text)
        self.assertIn("## Standard Filters And Dimensions", template_text)
        self.assertIn("evidence.md`: detailed provenance, only when the layer needs separate evidence tracking", template_text)
        self.assertIn("Do not put setup-time policy or full evidence procedures", template_text)
        self.assertNotIn("### Source Order", template_text)
        self.assertNotIn("### Evidence Standard", template_text)


if __name__ == "__main__":
    unittest.main()
