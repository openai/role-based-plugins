#!/usr/bin/env python3
"""Regression tests for the Sales user-context preflight helper."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SKILL_ROOT = Path(__file__).resolve().parents[1]
PLUGIN_ROOT = SKILL_ROOT.parents[1]
SCRIPT_DIR = SKILL_ROOT / "scripts"
INIT_SCRIPT = SCRIPT_DIR / "init_user_context_state.py"
RESET_SCRIPT = SCRIPT_DIR / "reset_user_context_state.py"
VALIDATE_AUTOMATION_SCRIPT = SCRIPT_DIR / "validate_sales_automation_setup.py"
STATE_MARKETPLACE_ID = "role-specific-plugins"
STATE_PLUGIN_ID = "sales"
ONBOARDING_REFERENCE = SKILL_ROOT / "references/onboarding.md"
AUTOMATION_REFERENCE = SKILL_ROOT / "references/automation.md"
SOURCE_RUNTIME_REFERENCE = SKILL_ROOT / "references/source-category-runtime.md"
CALL_FOLLOWUP_SKILL = PLUGIN_ROOT / "skills/follow-up-after-call/SKILL.md"
MEETING_PREP_SKILL = PLUGIN_ROOT / "skills/prepare-for-meeting/SKILL.md"
INTERNAL_NAVIGATION_SKILL = PLUGIN_ROOT / "skills/find-key-internal-sources/SKILL.md"
SALES_COMPANY_RESEARCH_SKILL = PLUGIN_ROOT / "skills/sales-company-research/SKILL.md"
CONNECTOR_CONFIRMATION_COPY = "## Step 2: Confirm Active/Missing Sources"
MEETING_PROMPT_COPY = "### Step 4A: Choose First Hero Prompt"
HERO_OUTPUT_COPY = "### Step 4C: Run Selected First Hero Demo"
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


class SalesStateHelperTests(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory(
            prefix="sales-user-context-tests-",
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
            msg=(
                f"command failed: {' '.join(args)}\nSTDOUT:\n{proc.stdout}\nSTDERR:\n{proc.stderr}"
            ),
        )
        return json.loads(proc.stdout)

    def preflight(self, *extra: str, state_dir: Path | None = None) -> dict:
        return self.run_json(
            [
                sys.executable,
                str(SCRIPT_DIR / "sales_preflight.py"),
                "--workflow",
                "prepare-for-meeting",
                "--state-dir",
                str(state_dir or self.state_dir),
                *extra,
            ]
        )

    def namespaced_state_dir(self, codex_home: Path) -> Path:
        return codex_home / "state/plugins" / STATE_MARKETPLACE_ID / STATE_PLUGIN_ID

    def all_connector_confirmation(self, status: str = "active") -> dict[str, dict[str, str]]:
        config = json.loads(
            (
                PLUGIN_ROOT / "skills/user-context/plugin-author-config/source-category-config.json"
            ).read_text(encoding="utf-8")
        )
        return {
            category_id: {
                "status": status,
                "preferred": metadata["preferred_apps"][0],
            }
            for category_id, metadata in config["categories"].items()
        }

    def skill_experience_state(
        self,
        *,
        introduced: set[str] | None = None,
        tried: set[str] | None = None,
        dismissed: set[str] | None = None,
    ) -> dict[str, dict[str, str | None]]:
        introduced = introduced or set()
        tried = tried or set()
        dismissed = dismissed or set()
        state = {}
        for skill in USER_FACING_SKILLS:
            state[skill] = {
                "introduced_at": "2026-05-25T00:00:00Z"
                if skill in introduced or skill in tried
                else None,
                "first_tried_at": "2026-05-25T00:01:00Z" if skill in tried else None,
                "last_suggested_at": None,
                "dismissed_at": "2026-05-25T00:02:00Z" if skill in dismissed else None,
            }
        return state

    def ready_automation(
        self,
        automation_id: str,
        thread_id: str,
        thread_title: str,
        *,
        status: str = "active",
    ) -> dict[str, str]:
        return {
            "status": status,
            "canonical_id": automation_id,
            "kind": "heartbeat",
            "readback_status": "verified",
            "target_thread_id": thread_id,
            "target_thread_title": thread_title,
            "target_thread_status": "pinned",
        }

    def ready_automations(self) -> dict[str, dict[str, str]]:
        return {
            "weekly_sales_company_research": self.ready_automation(
                "auto_weekly",
                "thread_weekly",
                "Sales Company Research",
            ),
            "daily_sales_tips": self.ready_automation(
                "auto_tips",
                "thread_tips",
                "Sales Tips",
            ),
        }

    def write_automation_toml(
        self,
        automations_dir: Path,
        canonical_id: str,
        *,
        kind: str,
        name: str,
        prompt: str,
        rrule: str,
        target_thread_id: str | None,
    ) -> None:
        automation_dir = automations_dir / canonical_id
        automation_dir.mkdir(parents=True)
        target_line = (
            f'target_thread_id = "{target_thread_id}"\n' if target_thread_id else ""
        )
        (automation_dir / "automation.toml").write_text(
            (
                "version = 1\n"
                f'id = "{canonical_id}"\n'
                f'kind = "{kind}"\n'
                f'name = "{name}"\n'
                f'prompt = {json.dumps(prompt)}\n'
                'status = "ACTIVE"\n'
                f'rrule = "{rrule}"\n'
                f"{target_line}"
            ),
            encoding="utf-8",
        )

    def test_missing_preflight_returns_onboarding_obligation_and_context_gap_guidance(self) -> None:
        payload = self.preflight(state_dir=self.tmp_path / "missing")

        self.assertTrue(payload["read_only"])
        self.assertEqual(payload["state"]["user_context_status"], "missing")
        self.assertEqual(
            payload["control"]["current_skill_experience"]["skill"],
            "prepare-for-meeting",
        )
        self.assertFalse(payload["control"]["current_skill_experience"]["introduced"])
        self.assertTrue(payload["control"]["current_skill_experience"]["intro_eligible"])
        self.assertEqual(payload["control"]["current_skill_experience"]["cta_owner"], "skill")
        self.assertNotIn("category_state_status", payload["state"])
        self.assertEqual(payload["state"]["onboarding_state_status"], "missing")
        obligation = payload["control"]["final_obligations"][0]
        self.assertEqual(obligation["id"], "offer_sales_onboarding_next_step")
        self.assertEqual(obligation["timing"], "append_after_main_answer")
        self.assertTrue(obligation["template"].startswith("## Sales Setup Required"))
        self.assertIn(
            "This is required before Sales can reliably use your connected sources",
            obligation["template"],
        )
        self.assertIn(
            "source and use your authoritative company context",
            obligation["template"],
        )
        self.assertIn("Reply `start` to continue.", obligation["template"])
        self.assertNotIn("**Next Step**", obligation["template"])
        self.assertEqual(obligation["next_action"]["id"], "start_sales_onboarding")
        self.assertIn("requires a clarification", obligation["skip_when"])
        self.assertEqual(payload["control"]["final_response_checks"], [])
        self.assertEqual(
            payload["control"]["conditional_guidance"][0]["id"],
            "context_gap_note",
        )
        self.assertEqual(
            payload["control"]["conditional_guidance"][0]["potential_gaps"],
            ["saved Sales user context is missing or unreadable"],
        )
        sources = payload["context"]["sources"]
        self.assertTrue(sources["has_setup_gaps"])
        self.assertEqual(
            {
                category_id
                for category_id, entry in sources["categories"].items()
                if entry["status"] == "needs_confirmation"
            },
            set(sources["categories"]),
        )
        first_source = next(iter(sources["categories"].values()))
        self.assertIn("preferred_apps", first_source)
        self.assertEqual(
            sources["resolution"],
            "plugin_or_app_or_connector_then_manual_context",
        )
        self.assertNotIn("impact", first_source)

    def test_default_preflight_reads_namespaced_state_dir(self) -> None:
        codex_home = self.tmp_path / "codex-home"
        state_dir = self.namespaced_state_dir(codex_home)
        state_dir.mkdir(parents=True)
        (state_dir / "user-context.md").write_text(
            "# Output Preferences\n\n## Saved Links And Context\n\nKeep it short.\n",
            encoding="utf-8",
        )
        (state_dir / "onboarding-state.json").write_text(
            json.dumps({"status": "complete"}),
            encoding="utf-8",
        )

        payload = self.run_json(
            [
                sys.executable,
                str(SCRIPT_DIR / "sales_preflight.py"),
                "--workflow",
                "prepare-for-meeting",
                "--codex-home",
                str(codex_home),
            ]
        )

        self.assertEqual(payload["state"]["state_dir"], str(state_dir))
        self.assertEqual(payload["state"]["user_context_status"], "present")
        self.assertIn("Output Preferences: Keep it short.", payload["context"]["user_context"]["entries"])

    def test_direct_onboarding_mode_suppresses_ordinary_final_obligation(self) -> None:
        payload = self.preflight(
            "--request-mode",
            "direct_onboarding_status",
            state_dir=self.tmp_path / "missing",
        )

        self.assertEqual(payload["control"]["response_mode"], "direct_onboarding_status")
        self.assertEqual(payload["control"]["final_obligations"], [])
        self.assertEqual(payload["control"]["conditional_guidance"], [])

    def test_guided_onboarding_workflow_suppresses_ordinary_onboarding_obligation(self) -> None:
        payload = self.preflight(
            "--request-mode",
            "guided_onboarding_workflow",
            state_dir=self.tmp_path / "missing",
        )

        self.assertEqual(payload["control"]["response_mode"], "guided_onboarding_workflow")
        self.assertEqual(payload["control"]["final_obligations"], [])
        self.assertEqual(payload["control"]["conditional_guidance"], [])

    def test_active_onboarding_does_not_offer_to_start_over(self) -> None:
        self.state_dir.mkdir(parents=True)
        (self.state_dir / "user-context.md").write_text(
            "# Output Preferences\n\n## Saved Links And Context\n\nstatus: not provided\n",
            encoding="utf-8",
        )
        (self.state_dir / "onboarding-state.json").write_text(
            json.dumps({"status": "active"}),
            encoding="utf-8",
        )

        payload = self.preflight()

        obligation = payload["control"]["final_obligations"][0]
        self.assertEqual(obligation["id"], "complete_sales_core_onboarding")
        self.assertIn("core onboarding is not complete", obligation["requirement"])
        self.assertEqual(payload["control"]["final_response_checks"], [])
        self.assertEqual(payload["control"]["conditional_guidance"], [])

    def test_complete_onboarding_suppresses_ordinary_onboarding_obligation(self) -> None:
        self.state_dir.mkdir(parents=True)
        (self.state_dir / "onboarding-state.json").write_text(
            json.dumps({"status": "complete"}),
            encoding="utf-8",
        )

        payload = self.preflight()

        self.assertEqual(payload["control"]["final_obligations"], [])

    def test_explicit_core_onboarding_completion_does_not_override_missing_automation_readback(
        self,
    ) -> None:
        self.state_dir.mkdir(parents=True)
        (self.state_dir / "onboarding-state.json").write_text(
            json.dumps(
                {
                    "status": "active",
                    "connector_confirmation": self.all_connector_confirmation(),
                    "core_onboarding": {"status": "completed"},
                }
            ),
            encoding="utf-8",
        )

        status_payload = self.preflight("--request-mode", "direct_onboarding_status")
        progress = status_payload["control"]["onboarding_progress"]
        task_statuses = {item["id"]: item["status"] for item in progress["task_list"]}

        self.assertFalse(progress["core_onboarding"]["complete"])
        self.assertEqual(progress["core_onboarding"]["remaining_step_ids"], ["sales_automation_setup"])
        self.assertEqual(task_statuses["connector_setup_confirmation"], "completed")
        self.assertEqual(task_statuses["sales_automation_setup"], "in_progress")

        ordinary_payload = self.preflight()
        self.assertIn(
            "complete_sales_core_onboarding",
            [item["id"] for item in ordinary_payload["control"]["final_obligations"]],
        )

    def test_fallback_core_completion_and_default_connector_preferences_are_authoritative(
        self,
    ) -> None:
        self.state_dir.mkdir(parents=True)
        (self.state_dir / "onboarding-state.json").write_text(
            json.dumps(
                {
                    "status": "active",
                    "connector_confirmation": {
                        "status": "completed_with_defaults",
                        "preferences": {
                            "calendar": {"preferred": "Google Calendar", "status": "active"},
                            "crm": {"preferred": "Salesforce", "status": "active"},
                            "document_store": {
                                "backup": "Notion",
                                "preferred": "Google Drive",
                                "status": "active",
                            },
                            "spreadsheets": {
                                "preferred": "Google Drive",
                                "status": "active",
                            },
                            "external_messaging": {"preferred": "Gmail", "status": "active"},
                            "internal_messaging": {"preferred": "Slack", "status": "active"},
                            "meeting_notes": {
                                "preferred": "Zoom",
                                "status": "active",
                            },
                            "data_enrichment": {
                                "preferred": None,
                                "status": "skipped_for_now",
                            },
                            "agreements": {
                                "preferred": None,
                                "status": "skipped_for_now",
                            },
                        },
                    },
                    "core_onboarding": {
                        "completed_at": "2026-05-27T19:15:04.064136+00:00",
                        "remaining_steps": [],
                        "status": "complete_with_fallback_automation",
                    },
                    "automations": {
                        "weekly_sales_company_research": {
                            "status": "deferred_environment_api_limitations",
                        },
                        "daily_sales_tips": {
                            "status": "installed_fallback_current_thread",
                            "canonical_id": "daily-sales-tips",
                            "target_thread_id": "thread_tips",
                        },
                    },
                    "initial_resource_discovery": {
                        "status": "deferred_environment_api_limitations",
                    },
                }
            ),
            encoding="utf-8",
        )

        status_payload = self.preflight("--request-mode", "direct_onboarding_status")
        progress = status_payload["control"]["onboarding_progress"]
        task_statuses = {item["id"]: item["status"] for item in progress["task_list"]}
        sources = status_payload["context"]["sources"]
        confirmation = sources["categories"]

        self.assertTrue(progress["core_onboarding"]["complete"])
        self.assertEqual(progress["core_onboarding"]["remaining_step_ids"], [])
        self.assertEqual(task_statuses["connector_setup_confirmation"], "completed")
        self.assertEqual(task_statuses["sales_automation_setup"], "completed")
        self.assertEqual(confirmation["crm"]["status"], "active")
        self.assertEqual(confirmation["crm"]["preferred"], "Salesforce")
        self.assertEqual(confirmation["document_store"]["preferred"], "Google Drive")
        self.assertEqual(confirmation["spreadsheets"]["preferred"], "Google Drive")
        self.assertEqual(confirmation["data_enrichment"]["status"], "skipped_for_now")
        self.assertEqual(confirmation["agreements"]["status"], "skipped_for_now")
        self.assertEqual(
            confirmation["data_enrichment"]["setup_action"],
            "run_plugin_first_source_setup",
        )
        self.assertTrue(sources["has_setup_gaps"])
        self.assertEqual(
            {
                category_id
                for category_id, entry in confirmation.items()
                if entry["status"] == "active"
            },
            {
                "calendar",
                "crm",
                "document_store",
                "external_messaging",
                "internal_messaging",
                "meeting_notes",
                "spreadsheets",
            },
        )
        self.assertEqual(
            [
                category_id
                for category_id, entry in confirmation.items()
                if entry["status"] != "active"
            ],
            ["agreements", "data_enrichment"],
        )
        self.assertNotIn("impact", confirmation["data_enrichment"])

        ordinary_payload = self.preflight()
        self.assertNotIn(
            "complete_sales_core_onboarding",
            [item["id"] for item in ordinary_payload["control"]["final_obligations"]],
        )

    def test_connector_defaults_and_fallback_automations_derive_core_completion(
        self,
    ) -> None:
        self.state_dir.mkdir(parents=True)
        (self.state_dir / "onboarding-state.json").write_text(
            json.dumps(
                {
                    "status": "active",
                    "connector_confirmation": {
                        "status": "completed_with_defaults",
                        "preferences": {
                            "calendar": {"preferred": "Google Calendar", "status": "active"},
                            "crm": {"preferred": "Salesforce", "status": "active"},
                            "document_store": {
                                "backup": "Notion",
                                "preferred": "Google Drive",
                                "status": "active",
                            },
                            "spreadsheets": {
                                "preferred": "Google Drive",
                                "status": "active",
                            },
                            "external_messaging": {"preferred": "Gmail", "status": "active"},
                            "internal_messaging": {"preferred": "Slack", "status": "active"},
                            "meeting_notes": {
                                "preferred": "Zoom",
                                "status": "active",
                            },
                            "data_enrichment": {
                                "preferred": None,
                                "status": "skipped_for_now",
                            },
                            "agreements": {
                                "preferred": None,
                                "status": "skipped_for_now",
                            },
                        },
                    },
                    "automations_intro": {"status": "accepted_fallback_installed"},
                    "automations": {
                        "weekly_sales_company_research": {
                            "status": "deferred_environment_api_limitations",
                        },
                        "daily_sales_tips": {
                            "status": "installed_fallback_current_thread",
                            "canonical_id": "daily-sales-tips",
                            "target_thread_id": "thread_tips",
                        },
                    },
                    "initial_resource_discovery": {
                        "status": "deferred_environment_api_limitations",
                    },
                }
            ),
            encoding="utf-8",
        )

        status_payload = self.preflight("--request-mode", "direct_onboarding_status")
        progress = status_payload["control"]["onboarding_progress"]
        task_statuses = {item["id"]: item["status"] for item in progress["task_list"]}

        self.assertTrue(progress["core_onboarding"]["complete"])
        self.assertEqual(progress["core_onboarding"]["remaining_step_ids"], [])
        self.assertEqual(task_statuses["connector_setup_confirmation"], "completed")
        self.assertEqual(task_statuses["sales_automation_setup"], "completed")

        ordinary_payload = self.preflight()
        self.assertEqual(ordinary_payload["control"]["final_obligations"], [])

    def test_onboarding_progress_uses_canonical_overall_steps(self) -> None:
        self.state_dir.mkdir(parents=True)
        (self.state_dir / "onboarding-state.json").write_text(
            json.dumps(
                {
                    "status": "active",
                    "orientation": {"status": "shown"},
                    "connector_confirmation": self.all_connector_confirmation(),
                    "meeting_prep_prompt": {
                        "status": "confirmed",
                        "selected_prompt": "Prep me for the Acme QBR tomorrow.",
                    },
                    "meeting_prep_run": {"status": "completed"},
                    "first_guided_workflow_review": {"status": "completed"},
                    "plugin_memory_intro": {"status": "shown"},
                    "accepted_preference_memory": {"status": "saved"},
                    "automations": self.ready_automations(),
                    "initial_resource_discovery": {
                        "status": "started",
                        "target_thread_title": "Sales Company Research",
                    },
                    "skill_experience": self.skill_experience_state(
                        tried={
                            "prepare-for-meeting",
                            "follow-up-after-call",
                            "prioritize-accounts",
                        }
                    ),
                }
            ),
            encoding="utf-8",
        )

        payload = self.preflight("--request-mode", "direct_onboarding_status")
        progress = payload["control"]["onboarding_progress"]["task_list"]

        self.assertEqual(
            [item["label"] for item in progress],
            [
                "Orientation",
                "Connector setup/confirmation",
                "Sales automation setup",
                "First hero prompt",
                "Other hero prompts",
            ],
        )
        self.assertEqual(
            [item["status"] for item in progress],
            ["completed", "completed", "completed", "completed", "completed"],
        )
        self.assertTrue(payload["control"]["onboarding_progress"]["core_onboarding"]["complete"])
        self.assertNotIn("Add starter context", [item["label"] for item in progress])
        self.assertNotIn("Search company context", [item["label"] for item in progress])

    def test_first_hero_prompt_can_be_any_core_hero_skill(self) -> None:
        self.state_dir.mkdir(parents=True)
        (self.state_dir / "onboarding-state.json").write_text(
            json.dumps(
                {
                    "status": "active",
                    "orientation": {"status": "shown"},
                    "connector_confirmation": self.all_connector_confirmation(),
                    "automations": self.ready_automations(),
                    "initial_resource_discovery": {"status": "started"},
                    "hero_prompt_choice": {
                        "status": "selected",
                        "selected_skill": "follow-up-after-call",
                    },
                    "first_guided_workflow_review": {"status": "completed"},
                    "accepted_preference_memory": {"status": "skipped"},
                    "skill_experience": self.skill_experience_state(tried={"follow-up-after-call"}),
                }
            ),
            encoding="utf-8",
        )

        payload = self.preflight("--request-mode", "direct_onboarding_status")
        progress = {
            item["label"]: item["status"]
            for item in payload["control"]["onboarding_progress"]["task_list"]
        }

        self.assertEqual(progress["First hero prompt"], "completed")
        self.assertEqual(progress["Other hero prompts"], "in_progress")

    def test_skipped_first_hero_prompt_is_resolved(self) -> None:
        self.state_dir.mkdir(parents=True)
        (self.state_dir / "onboarding-state.json").write_text(
            json.dumps(
                {
                    "status": "active",
                    "connector_confirmation": self.all_connector_confirmation(),
                    "automations": self.ready_automations(),
                    "initial_resource_discovery": {"status": "started"},
                    "core_onboarding": {"status": "completed"},
                    "hero_prompt_choice": {"status": "skipped"},
                }
            ),
            encoding="utf-8",
        )

        payload = self.preflight("--request-mode", "direct_onboarding_status")
        progress = {
            item["label"]: item["status"]
            for item in payload["control"]["onboarding_progress"]["task_list"]
        }

        self.assertEqual(progress["First hero prompt"], "completed")

    def test_hero_prompt_choices_offer_only_untried_core_skills(self) -> None:
        self.state_dir.mkdir(parents=True)
        (self.state_dir / "onboarding-state.json").write_text(
            json.dumps(
                {
                    "status": "active",
                    "orientation": {"status": "shown"},
                    "connector_confirmation": self.all_connector_confirmation(),
                    "automations": self.ready_automations(),
                    "initial_resource_discovery": {"status": "started"},
                    "first_guided_workflow_review": {"status": "completed"},
                    "accepted_preference_memory": {"status": "skipped"},
                    "skill_experience": self.skill_experience_state(
                        tried={"prepare-for-meeting"},
                        dismissed={"prioritize-accounts"},
                    ),
                }
            ),
            encoding="utf-8",
        )

        payload = self.preflight("--request-mode", "direct_onboarding_status")
        choices = payload["control"]["onboarding_progress"]["hero_prompt_choices"]

        self.assertEqual(choices["current_offer_label"], "Choose Your Next Sales Demo")
        self.assertEqual(choices["suggested_options"], ["follow-up-after-call"])
        self.assertEqual(
            choices["resolved_core_skills"],
            ["prepare-for-meeting", "prioritize-accounts"],
        )

    def test_onboarding_progress_marks_only_uncertain_sources_action_required(
        self,
    ) -> None:
        self.state_dir.mkdir(parents=True)
        (self.state_dir / "onboarding-state.json").write_text(
            json.dumps(
                {
                    "status": "active",
                    "connector_confirmation": {
                        "calendar": {
                            "status": "active",
                            "preferred": "Google Calendar",
                        },
                        "crm": {
                            "status": "needs_confirmation",
                            "candidates": ["Salesforce", "HubSpot"],
                        },
                    },
                    "skill_experience": self.skill_experience_state(),
                }
            ),
            encoding="utf-8",
        )

        payload = self.preflight("--request-mode", "direct_onboarding_status")
        progress = {
            item["label"]: item for item in payload["control"]["onboarding_progress"]["task_list"]
        }

        self.assertEqual(progress["Connector setup/confirmation"]["status"], "in_progress")
        self.assertTrue(progress["Connector setup/confirmation"]["action_required"])
        self.assertNotIn("Draft proposed Sales context", progress)

    def test_init_script_creates_first_run_state_from_templates_without_category_state(
        self,
    ) -> None:
        proc = subprocess.run(
            [
                sys.executable,
                str(INIT_SCRIPT),
                "--state-dir",
                str(self.state_dir),
            ],
            text=True,
            capture_output=True,
        )

        self.assertEqual(proc.returncode, 0, msg=proc.stderr)
        self.assertIn("user-context.md: created", proc.stdout)
        self.assertNotIn("category-state.json", proc.stdout)
        user_context = self.state_dir / "user-context.md"
        category_state = self.state_dir / "category-state.json"
        onboarding_state = self.state_dir / "onboarding-state.json"
        author_config_text = (
            PLUGIN_ROOT / "skills/user-context/plugin-author-config/user-context-config.md"
        ).read_text(encoding="utf-8")
        self.assertTrue(user_context.exists())
        self.assertFalse(category_state.exists())
        self.assertTrue(onboarding_state.exists())
        self.assertIn("# Sales User Context Config", author_config_text)
        self.assertIn("## Category Entry Shape", author_config_text)
        self.assertIn("## Default Categories", author_config_text)
        self.assertNotIn("## User Resources", author_config_text)
        self.assertNotIn("\n## Saved Links And Context", author_config_text)
        self.assertNotIn("- Priority:", author_config_text)
        self.assertNotIn("- Use When:", author_config_text)
        user_context_text = user_context.read_text(encoding="utf-8")
        self.assertIn(
            "Unresolved `status: not provided` entries are setup prompts",
            user_context_text,
        )
        self.assertIn("## Saved Links And Context\n\nstatus: not provided", user_context_text)
        self.assertNotIn("# Sales User Context Config", user_context_text)
        self.assertNotIn("- Priority:", user_context_text)
        self.assertNotIn("- Use When:", user_context_text)
        onboarding_state_data = json.loads(onboarding_state.read_text(encoding="utf-8"))
        self.assertEqual(
            set(onboarding_state_data["automations"]),
            {
                "daily_sales_tips",
                "weekly_sales_company_research",
            },
        )
        self.assertEqual(
            onboarding_state_data["automations"]["daily_sales_tips"]["frequency"],
            "weekdays at 9:00 AM local time",
        )
        self.assertNotIn(
            "initial_run_status",
            onboarding_state_data["automations"]["daily_sales_tips"],
        )
        self.assertEqual(
            onboarding_state_data["automations"]["weekly_sales_company_research"][
                "target_thread_title"
            ],
            "Sales Company Research",
        )
        self.assertIn("meeting_prep_prompt", onboarding_state_data)
        self.assertIn("hero_prompt_choice", onboarding_state_data)
        self.assertEqual(
            onboarding_state_data["hero_prompt_choice"]["options"],
            [
                "prepare-for-meeting",
                "follow-up-after-call",
                "prioritize-accounts",
            ],
        )
        self.assertIn("last_offered_skills", onboarding_state_data["hero_prompt_choice"])
        self.assertIn("plugin_memory_intro", onboarding_state_data)
        self.assertIn("accepted_preference_memory", onboarding_state_data)
        self.assertIn("shown_at", onboarding_state_data["plugin_memory_intro"])
        self.assertIn("approved_at", onboarding_state_data["accepted_preference_memory"])
        self.assertIn("saved_at", onboarding_state_data["accepted_preference_memory"])
        self.assertNotIn("prep_doc", onboarding_state_data)
        self.assertIn("automations_intro", onboarding_state_data)
        self.assertIn("initial_resource_discovery", onboarding_state_data)
        self.assertIn("target_thread_title", onboarding_state_data["initial_resource_discovery"])
        self.assertIn("call_followup_intro", onboarding_state_data)
        self.assertIn("internal_navigation_intro", onboarding_state_data)
        self.assertIn("skill_experience", onboarding_state_data)
        self.assertIn("prepare-for-meeting", onboarding_state_data["skill_experience"])
        self.assertNotIn("starter_context", onboarding_state_data)
        self.assertNotIn("plugin_memory_orientation", onboarding_state_data)
        self.assertNotIn("key_team_docs", onboarding_state_data)
        self.assertNotIn("background_context_discovery", onboarding_state_data)
        self.assertNotIn("company_context_discovery", onboarding_state_data)

    def test_reset_script_backs_up_known_and_legacy_state_files(self) -> None:
        self.state_dir.mkdir(parents=True)
        for filename in (
            "user-context.md",
            "category-state.json",
            "onboarding-state.json",
        ):
            (self.state_dir / filename).write_text(filename, encoding="utf-8")
        backup_dir = self.tmp_path / "sales-backup-fixed"

        proc = subprocess.run(
            [
                sys.executable,
                str(RESET_SCRIPT),
                "--state-dir",
                str(self.state_dir),
                "--backup-dir",
                str(backup_dir),
            ],
            text=True,
            capture_output=True,
        )

        self.assertEqual(proc.returncode, 0, msg=proc.stderr)
        self.assertIn(f"Backup directory: {backup_dir}", proc.stdout)
        self.assertFalse(self.state_dir.exists())
        for filename in (
            "user-context.md",
            "category-state.json",
            "onboarding-state.json",
        ):
            self.assertFalse((self.state_dir / filename).exists())
            self.assertEqual(
                (backup_dir / filename).read_text(encoding="utf-8"),
                filename,
            )

    def test_reset_script_dry_run_does_not_move_files(self) -> None:
        self.state_dir.mkdir(parents=True)
        (self.state_dir / "user-context.md").write_text("memory", encoding="utf-8")
        backup_dir = self.tmp_path / "sales-backup-dry-run"

        proc = subprocess.run(
            [
                sys.executable,
                str(RESET_SCRIPT),
                "--state-dir",
                str(self.state_dir),
                "--backup-dir",
                str(backup_dir),
                "--dry-run",
            ],
            text=True,
            capture_output=True,
        )

        self.assertEqual(proc.returncode, 0, msg=proc.stderr)
        self.assertIn("Dry run only; no files were moved.", proc.stdout)
        self.assertTrue((self.state_dir / "user-context.md").exists())
        self.assertFalse(backup_dir.exists())

    def test_automation_setup_validator_accepts_heartbeat_threads_and_research_kickoff(self) -> None:
        automations_dir = self.tmp_path / "automations"
        self.state_dir.mkdir(parents=True)
        research_prompt = (
            "Load and follow `$sales:sales-company-research` in scheduled research mode. "
            "Use the skill's dynamic source discovery, Sales user-context save policy, "
            "review gates, coverage-note guidance, and output contract, and compare against "
            "entries already flagged or saved from this pinned thread."
        )
        tips_prompt = (
            "Load and follow `$sales:suggest-sales-next-step` in scheduled Sales check-in mode. "
            "Produce a short natural-language check-in on recent Sales work and the next Sales "
            "workflow worth trying, preserving the heartbeat automation response format."
        )
        self.write_automation_toml(
            automations_dir,
            "sales-company-research",
            kind="heartbeat",
            name="Sales Company Research",
            prompt=research_prompt,
            rrule="FREQ=WEEKLY;BYDAY=MO;BYHOUR=9;BYMINUTE=0;BYSECOND=0",
            target_thread_id="thread_research",
        )
        self.write_automation_toml(
            automations_dir,
            "sales-tips",
            kind="heartbeat",
            name="Sales Tips",
            prompt=tips_prompt,
            rrule="FREQ=WEEKLY;BYDAY=MO,TU,WE,TH,FR;BYHOUR=9;BYMINUTE=0;BYSECOND=0",
            target_thread_id="thread_tips",
        )
        (self.state_dir / "onboarding-state.json").write_text(
            json.dumps(
                {
                    "automations": {
                        "weekly_sales_company_research": {
                            "status": "configured",
                            "canonical_id": "sales-company-research",
                            "kind": "heartbeat",
                            "readback_status": "confirmed",
                            "target_thread_id": "thread_research",
                            "target_thread_title": "Sales Company Research",
                            "target_thread_status": "pinned",
                        },
                        "daily_sales_tips": {
                            "status": "configured",
                            "canonical_id": "sales-tips",
                            "kind": "heartbeat",
                            "readback_status": "confirmed",
                            "target_thread_id": "thread_tips",
                            "target_thread_title": "Sales Tips",
                            "target_thread_status": "pinned",
                        },
                    },
                    "initial_resource_discovery": {
                        "status": "started",
                        "target_thread_id": "thread_research",
                        "target_thread_title": "Sales Company Research",
                    },
                }
            ),
            encoding="utf-8",
        )

        payload = self.run_json(
            [
                sys.executable,
                str(VALIDATE_AUTOMATION_SCRIPT),
                "--state-dir",
                str(self.state_dir),
                "--automations-dir",
                str(automations_dir),
                "--require-onboarding-defaults",
            ]
        )

        self.assertTrue(payload["ok"])
        self.assertEqual(
            payload["validated"],
            ["weekly_sales_company_research", "daily_sales_tips"],
        )

    def test_automation_setup_validator_rejects_cron_and_missing_research_kickoff(self) -> None:
        automations_dir = self.tmp_path / "automations"
        self.state_dir.mkdir(parents=True)
        self.write_automation_toml(
            automations_dir,
            "sales-company-research",
            kind="cron",
            name="Sales Company Research",
            prompt="expanded prompt",
            rrule="FREQ=WEEKLY;BYDAY=MO;BYHOUR=9;BYMINUTE=0;BYSECOND=0",
            target_thread_id=None,
        )
        self.write_automation_toml(
            automations_dir,
            "sales-tips",
            kind="heartbeat",
            name="Sales Tips",
            prompt="expanded prompt",
            rrule="FREQ=WEEKLY;BYDAY=MO,TU,WE,TH,FR;BYHOUR=9;BYMINUTE=0;BYSECOND=0",
            target_thread_id="thread_tips",
        )
        (self.state_dir / "onboarding-state.json").write_text(
            json.dumps(
                {
                    "automations": {
                        "weekly_sales_company_research": {
                            "status": "configured",
                            "canonical_id": "sales-company-research",
                            "target_thread_title": "Sales Company Research",
                        },
                        "daily_sales_tips": {
                            "status": "configured",
                            "canonical_id": "sales-tips",
                            "kind": "heartbeat",
                            "readback_status": "confirmed",
                            "target_thread_id": "thread_tips",
                            "target_thread_title": "Sales Tips",
                            "target_thread_status": "pinned",
                        },
                    }
                }
            ),
            encoding="utf-8",
        )

        payload = self.run_json(
            [
                sys.executable,
                str(VALIDATE_AUTOMATION_SCRIPT),
                "--state-dir",
                str(self.state_dir),
                "--automations-dir",
                str(automations_dir),
                "--require-onboarding-defaults",
            ],
            expect=1,
        )
        failures = "\n".join(payload["failures"])

        self.assertFalse(payload["ok"])
        self.assertIn("weekly_sales_company_research: stored kind is heartbeat", failures)
        self.assertIn(
            "weekly_sales_company_research: stored prompt matches automation-config.md Instructions",
            failures,
        )

    def test_onboarding_reference_preserves_connector_and_guided_output_copy(self) -> None:
        text = ONBOARDING_REFERENCE.read_text(encoding="utf-8")

        self.assertIn("# Sales Onboarding Flow", text)
        self.assertIn("Common Onboarding Message Frame", text)
        self.assertIn(CONNECTOR_CONFIRMATION_COPY, text)
        self.assertIn(MEETING_PROMPT_COPY, text)
        self.assertIn(HERO_OUTPUT_COPY, text)
        self.assertIn("### Step 4B: Introduce Selected First Hero Workflow", text)
        self.assertIn("### Step 4D: Review And Iterate", text)
        self.assertIn("### Step 4E: Introduce Plugin Memory And Save Preference", text)
        self.assertIn("Do not run another hero workflow until the user picks", text)
        self.assertIn("hero_prompt_choice", text)
        self.assertNotIn("### Step 3E: Optional Save Prep Doc", text)
        self.assertIn("## Step 3: Sales Automations", text)
        self.assertIn("### Step 3A: Introduce Sales Automations", text)
        self.assertIn("### Step 3B: Set Up Sales Automations", text)
        self.assertIn("## Step 5: Other Hero Prompts", text)
        self.assertIn("### Step 5A: Choose Next Hero Prompt", text)
        self.assertIn("### Step 5B: Introduce Selected Remaining Hero Workflow", text)
        self.assertIn("### Step 5C: Run Selected Remaining Hero Demo", text)
        self.assertIn("### Step 5D: Review And Continue Remaining Hero", text)
        self.assertIn("## Step 6: Completion", text)
        self.assertIn(
            "Here's your meeting prep, using",
            text,
        )
        self.assertIn(
            "Do not render `What Happened`, `Recap`, or another walkthrough heading by default",
            text,
        )
        self.assertIn("render that feedback CTA as an H2/H3 heading", text)
        self.assertNotIn("Recommended Next Steps", text)
        self.assertIn(
            "How does that look? Any other changes, or should we show the next demo workflow choices?",
            text,
        )
        self.assertNotIn("should I save any reusable preference and move on?", text)
        self.assertIn("must never be a narrow-preference save approval", text)
        self.assertIn(
            "Only require explicit yes for broad, sensitive, ambiguous, high-risk, or externally visible preferences",
            text,
        )
        self.assertIn("Do not save plugin memory on every iteration", text)
        self.assertIn("Calendar attachment is explicit-user-request only", text)
        self.assertIn("initial_resource_discovery", text)
        self.assertIn("Pre-tool gate: before the first automation", text)
        self.assertIn("outside the dedicated automation target threads created by `automation.md`", text)
        self.assertIn("prefer plugin setup", text)
        self.assertIn("direct app/connector setup", text)
        self.assertIn("asks for connect/auth, skip, or manual fallback", text)

    def test_inventory_requires_setup_to_write_resolved_source_routes(self) -> None:
        self.state_dir.mkdir(parents=True)
        (self.state_dir / "onboarding-state.json").write_text(
            json.dumps(
                {
                    "status": "active",
                    "connector_inventory": {
                        "active_apps": ["Google Calendar"],
                        "available_apps": ["Salesforce", "HubSpot"],
                    },
                }
            ),
            encoding="utf-8",
        )

        payload = self.preflight("--request-mode", "direct_onboarding_status")
        confirmation = payload["context"]["sources"]["categories"]

        self.assertEqual(confirmation["calendar"]["status"], "needs_confirmation")
        self.assertEqual(confirmation["calendar"]["candidates"], ["Google Calendar"])
        self.assertEqual(
            confirmation["calendar"]["setup_action"],
            "run_plugin_first_source_setup",
        )
        self.assertEqual(confirmation["crm"]["status"], "needs_confirmation")
        self.assertEqual(confirmation["crm"]["candidates"], ["Salesforce", "HubSpot"])
        self.assertEqual(
            confirmation["crm"]["setup_action"],
            "run_plugin_first_source_setup",
        )
        self.assertEqual(confirmation["meeting_notes"]["status"], "missing")
        self.assertEqual(
            confirmation["meeting_notes"]["options"],
            ["Zoom", "Granola", "Otter.ai", "Fireflies", "Outreach", "Rox"],
        )
        self.assertTrue(confirmation["meeting_notes"]["it_admin_options"])
        self.assertEqual(
            confirmation["meeting_notes"]["setup_action"],
            "run_plugin_first_source_setup",
        )
        self.assertEqual(confirmation["data_enrichment"]["status"], "missing")
        self.assertEqual(
            confirmation["data_enrichment"]["it_admin_options"],
            [
                "Ask IT or a workspace admin whether Codex access can be enabled for one of: ZoomInfo, Clay, HG Insights, Rox, Apollo, Actively, Meticulate."
            ],
        )

    def test_configured_connector_route_is_returned_for_runtime_use(self) -> None:
        self.state_dir.mkdir(parents=True)
        confirmation_state = self.all_connector_confirmation()
        confirmation_state["crm"] = {
            "status": "active",
            "preferred": "Salesforce",
            "source_kind": "connector",
            "skill_surface": "sales_vendored_helper",
            "connector": {"name": "Salesforce"},
            "installed_evidence": "connector_inventory",
        }
        (self.state_dir / "onboarding-state.json").write_text(
            json.dumps(
                {
                    "status": "active",
                    "connector_confirmation": confirmation_state,
                }
            ),
            encoding="utf-8",
        )

        payload = self.preflight("--request-mode", "direct_onboarding_status")
        confirmation = payload["context"]["sources"]["categories"]

        self.assertEqual(confirmation["crm"]["status"], "active")
        self.assertEqual(confirmation["crm"]["preferred"], "Salesforce")
        self.assertEqual(confirmation["crm"]["source_kind"], "connector")
        self.assertEqual(confirmation["crm"]["skill_surface"], "sales_vendored_helper")
        self.assertEqual(confirmation["crm"]["connector"], {"name": "Salesforce"})
        self.assertEqual(confirmation["crm"]["installed_evidence"], "connector_inventory")
        self.assertEqual(
            confirmation["crm"]["runtime_action"],
            "use_connector_or_app_with_sales_helper_guidance",
        )
        self.assertEqual(confirmation["crm"]["setup_action"], "run_plugin_first_source_setup")
        self.assertEqual(
            confirmation["crm"]["plugin_preference_order"],
            ["Salesforce", "Agentforce Sales", "HubSpot", "Close", "Zoho", "Pipedrive"],
        )
        self.assertEqual(
            confirmation["crm"]["setup_recovery"]["plugin_preferred_over"],
            "active_or_available_app_connector_routes",
        )
        self.assertIn("helper_skills", confirmation["crm"])
        self.assertEqual(confirmation["crm"]["helper_skills_apply_when"], ["app", "connector"])
        source_step = next(
            item
            for item in payload["control"]["onboarding_progress"]["task_list"]
            if item["id"] == "connector_setup_confirmation"
        )
        self.assertEqual(source_step["status"], "completed")
        self.assertFalse(source_step.get("action_required", False))

    def test_configured_plugin_route_uses_plugin_surface_without_sales_helper(self) -> None:
        self.state_dir.mkdir(parents=True)
        confirmation_state = self.all_connector_confirmation()
        confirmation_state["crm"] = {
            "status": "active",
            "preferred": "Salesforce",
            "source_kind": "plugin",
            "skill_surface": "plugin_owned",
            "plugin": {
                "id": "salesforce@example-marketplace",
                "name": "salesforce",
            },
            "installed_evidence": "installed_plugin_skill_visible",
        }
        (self.state_dir / "onboarding-state.json").write_text(
            json.dumps(
                {
                    "status": "active",
                    "connector_confirmation": confirmation_state,
                }
            ),
            encoding="utf-8",
        )

        payload = self.preflight("--request-mode", "direct_onboarding_status")
        confirmation = payload["context"]["sources"]["categories"]

        self.assertEqual(confirmation["crm"]["status"], "active")
        self.assertEqual(confirmation["crm"]["preferred"], "Salesforce")
        self.assertEqual(confirmation["crm"]["source_kind"], "plugin")
        self.assertEqual(confirmation["crm"]["skill_surface"], "plugin_owned")
        self.assertEqual(
            confirmation["crm"]["plugin"],
            {"id": "salesforce@example-marketplace", "name": "salesforce"},
        )
        self.assertEqual(
            confirmation["crm"]["installed_evidence"],
            "installed_plugin_skill_visible",
        )
        self.assertEqual(
            confirmation["crm"]["runtime_action"],
            "use_plugin_owned_skill_or_tools",
        )
        self.assertNotIn("helper_skills", confirmation["crm"])

    def test_configured_plugin_route_uses_new_install_and_surface_evidence(self) -> None:
        self.state_dir.mkdir(parents=True)
        confirmation_state = self.all_connector_confirmation()
        confirmation_state["crm"] = {
            "status": "active",
            "preferred": "HubSpot",
            "source_kind": "plugin",
            "skill_surface": "plugin_owned",
            "plugin": {
                "id": "hubspot@openai-curated",
                "name": "HubSpot",
            },
            "plugin_install_evidence": "request_plugin_install_completed",
            "app_surface_evidence": "callable_app_tools_visible",
            "skill_surface_evidence": "plugin_skills_visible",
        }
        (self.state_dir / "onboarding-state.json").write_text(
            json.dumps(
                {
                    "status": "active",
                    "connector_confirmation": confirmation_state,
                }
            ),
            encoding="utf-8",
        )

        payload = self.preflight("--request-mode", "direct_onboarding_status")
        confirmation = payload["context"]["sources"]["categories"]

        self.assertEqual(confirmation["crm"]["status"], "active")
        self.assertEqual(confirmation["crm"]["preferred"], "HubSpot")
        self.assertEqual(confirmation["crm"]["source_kind"], "plugin")
        self.assertEqual(confirmation["crm"]["skill_surface"], "plugin_owned")
        self.assertEqual(
            confirmation["crm"]["plugin"],
            {"id": "hubspot@openai-curated", "name": "HubSpot"},
        )
        self.assertEqual(
            confirmation["crm"]["plugin_install_evidence"],
            "request_plugin_install_completed",
        )
        self.assertEqual(
            confirmation["crm"]["app_surface_evidence"],
            "callable_app_tools_visible",
        )
        self.assertEqual(
            confirmation["crm"]["skill_surface_evidence"],
            "plugin_skills_visible",
        )
        self.assertEqual(
            confirmation["crm"]["runtime_action"],
            "use_plugin_owned_skill_or_tools",
        )
        self.assertNotIn("helper_skills", confirmation["crm"])

    def test_configured_multi_route_source_category_is_returned_for_runtime_use(self) -> None:
        self.state_dir.mkdir(parents=True)
        confirmation_state = self.all_connector_confirmation()
        confirmation_state["document_store"] = {
            "status": "active",
            "routes": [
                {
                    "preferred": "Google Drive",
                    "source_kind": "plugin",
                    "skill_surface": "plugin_owned",
                    "plugin": {
                        "id": "google-drive@openai-curated",
                        "name": "Google Drive",
                    },
                    "plugin_install_evidence": "plugin_in_available_plugins",
                    "skill_surface_evidence": "plugin_skills_visible",
                },
                {
                    "preferred": "Notion",
                    "source_kind": "plugin",
                    "skill_surface": "plugin_owned",
                    "plugin": {
                        "id": "notion@openai-curated",
                        "name": "Notion",
                    },
                    "plugin_install_evidence": "plugin_in_available_plugins",
                    "skill_surface_evidence": "plugin_skills_visible",
                },
            ],
        }
        (self.state_dir / "onboarding-state.json").write_text(
            json.dumps(
                {
                    "status": "active",
                    "connector_confirmation": confirmation_state,
                }
            ),
            encoding="utf-8",
        )

        payload = self.preflight("--request-mode", "direct_onboarding_status")
        document_store = payload["context"]["sources"]["categories"]["document_store"]

        self.assertEqual(document_store["status"], "active")
        self.assertNotIn("setup_action", document_store)
        self.assertEqual(
            [route["preferred"] for route in document_store["routes"]],
            ["Google Drive", "Notion"],
        )
        for route in document_store["routes"]:
            self.assertEqual(route["source_kind"], "plugin")
            self.assertEqual(route["skill_surface"], "plugin_owned")
            self.assertEqual(route["runtime_action"], "use_plugin_owned_skill_or_tools")
        self.assertNotIn("setup_recovery", document_store)

    def test_plugin_route_without_visible_skill_surface_stays_unresolved(self) -> None:
        self.state_dir.mkdir(parents=True)
        confirmation_state = self.all_connector_confirmation()
        confirmation_state["crm"] = {
            "status": "active",
            "preferred": "HubSpot",
            "source_kind": "plugin",
            "skill_surface": "plugin_owned",
            "plugin": {
                "id": "hubspot@openai-curated",
                "name": "HubSpot",
            },
            "plugin_install_evidence": "request_plugin_install_completed",
        }
        (self.state_dir / "onboarding-state.json").write_text(
            json.dumps(
                {
                    "status": "active",
                    "connector_confirmation": confirmation_state,
                }
            ),
            encoding="utf-8",
        )

        payload = self.preflight("--request-mode", "direct_onboarding_status")
        confirmation = payload["context"]["sources"]["categories"]

        self.assertEqual(confirmation["crm"]["status"], "needs_confirmation")
        self.assertEqual(confirmation["crm"]["setup_action"], "run_plugin_first_source_setup")
        self.assertEqual(
            confirmation["crm"]["setup_note"],
            "plugin_route_requires_plugin_install_and_surface_evidence_before_active",
        )

    def test_saved_preferred_source_leads_plugin_preference_order(self) -> None:
        self.state_dir.mkdir(parents=True)
        (self.state_dir / "user-context.md").write_text(
            "# Source Preferences And Defaults\n\n"
            "## Saved Links And Context\n\n"
            "Agentforce Sales CRM preference\n"
            "- Date Added: 2026-05-29.\n"
            "- Useful Context: Agentforce Sales is the preferred CRM source.\n"
            "- Future Use: Use Agentforce Sales when Sales needs CRM account or pipeline context.\n",
            encoding="utf-8",
        )
        confirmation_state = self.all_connector_confirmation()
        confirmation_state["crm"] = {
            "status": "missing",
            "options": ["Salesforce", "Agentforce Sales", "HubSpot"],
        }
        (self.state_dir / "onboarding-state.json").write_text(
            json.dumps(
                {
                    "status": "active",
                    "connector_confirmation": confirmation_state,
                }
            ),
            encoding="utf-8",
        )

        payload = self.preflight("--request-mode", "direct_onboarding_status")
        crm = payload["context"]["sources"]["categories"]["crm"]

        self.assertEqual(crm["status"], "missing")
        self.assertEqual(crm["saved_source_preferences"], ["Agentforce Sales"])
        self.assertEqual(
            crm["plugin_preference_order"],
            ["Agentforce Sales", "Salesforce", "HubSpot", "Close", "Zoho", "Pipedrive"],
        )
        self.assertEqual(crm["setup_action"], "run_plugin_first_source_setup")
        self.assertEqual(
            crm["fallback_setup_action"],
            "explain_workflow_impact_and_it_admin_options",
        )
        self.assertEqual(
            crm["setup_recovery"],
            {
                "type": "plugin_first_source_setup",
                "preferred_sources": [
                    "Agentforce Sales",
                    "Salesforce",
                    "HubSpot",
                    "Close",
                    "Zoho",
                    "Pipedrive",
                ],
                "plugin_preferred_over": "active_or_available_app_connector_routes",
                "candidate_match": (
                    "candidate_name_display_id_or_app_connector_id_matches_preferred_source"
                ),
                "candidate_lookup": "functions.list_available_plugins_to_install",
                "install_request": "functions.request_plugin_install_after_user_approval",
                "retry_policy": (
                    "retry_on_future_workflows_after_failed_setup_or_pending_visibility"
                ),
                "decline_scope": (
                    "suppress_current_workflow_only_unless_user_saves_do_not_use"
                ),
                "fallback": (
                    "use_existing_app_connector_route_or_manual_context_when_no_plugin_candidate_or_user_declines"
                ),
            },
        )

    def test_failed_preferred_plugin_setup_stays_retryable_until_user_declines(self) -> None:
        self.state_dir.mkdir(parents=True)
        (self.state_dir / "user-context.md").write_text(
            "# Source Preferences And Defaults\n\n"
            "## Saved Links And Context\n\n"
            "Agentforce Sales CRM preference\n"
            "- Date Added: 2026-05-29.\n"
            "- Useful Context: Agentforce Sales is the preferred CRM source.\n"
            "- Future Use: Use Agentforce Sales when Sales needs CRM account or pipeline context.\n",
            encoding="utf-8",
        )
        confirmation_state = self.all_connector_confirmation()
        confirmation_state["crm"] = {
            "status": "deferred",
            "preferred": "Agentforce Sales",
        }
        (self.state_dir / "onboarding-state.json").write_text(
            json.dumps(
                {
                    "status": "active",
                    "connector_confirmation": confirmation_state,
                }
            ),
            encoding="utf-8",
        )

        payload = self.preflight("--request-mode", "direct_onboarding_status")
        crm = payload["context"]["sources"]["categories"]["crm"]

        self.assertEqual(crm["status"], "deferred")
        self.assertEqual(crm["setup_action"], "run_plugin_first_source_setup")
        self.assertEqual(
            crm["setup_recovery"]["retry_policy"],
            "retry_on_future_workflows_after_failed_setup_or_pending_visibility",
        )

        confirmation_state["crm"] = {
            "status": "declined",
            "preferred": "Agentforce Sales",
        }
        (self.state_dir / "onboarding-state.json").write_text(
            json.dumps(
                {
                    "status": "active",
                    "connector_confirmation": confirmation_state,
                }
            ),
            encoding="utf-8",
        )

        payload = self.preflight("--request-mode", "direct_onboarding_status")
        crm = payload["context"]["sources"]["categories"]["crm"]

        self.assertEqual(crm["status"], "declined")
        self.assertNotIn("setup_recovery", crm)

    def test_unproven_plugin_route_is_not_returned_as_active(self) -> None:
        self.state_dir.mkdir(parents=True)
        confirmation_state = self.all_connector_confirmation()
        confirmation_state["meeting_notes"] = {
            "status": "active",
            "label": "Zoom",
            "source_kind": "plugin",
            "skill_surface": "plugin_owned",
            "plugin": "Zoom",
        }
        (self.state_dir / "onboarding-state.json").write_text(
            json.dumps(
                {
                    "status": "active",
                    "connector_confirmation": confirmation_state,
                }
            ),
            encoding="utf-8",
        )

        payload = self.preflight("--request-mode", "direct_onboarding_status")
        confirmation = payload["context"]["sources"]["categories"]

        self.assertEqual(confirmation["meeting_notes"]["status"], "needs_confirmation")
        self.assertEqual(
            confirmation["meeting_notes"]["candidates"],
            ["Zoom", "Granola", "Otter.ai", "Fireflies", "Outreach", "Rox"],
        )
        self.assertEqual(
            confirmation["meeting_notes"]["setup_action"],
            "run_plugin_first_source_setup",
        )
        self.assertEqual(
            confirmation["meeting_notes"]["setup_note"],
            "plugin_route_requires_plugin_install_and_surface_evidence_before_active",
        )

    def test_user_selected_available_source_stays_unresolved_until_read_probe(self) -> None:
        self.state_dir.mkdir(parents=True)
        confirmation_state = self.all_connector_confirmation()
        confirmation_state["crm"] = {
            "status": "selected",
            "preferred": "Salesforce",
        }
        (self.state_dir / "onboarding-state.json").write_text(
            json.dumps(
                {
                    "status": "active",
                    "connector_confirmation": confirmation_state,
                }
            ),
            encoding="utf-8",
        )

        payload = self.preflight("--request-mode", "direct_onboarding_status")
        confirmation = payload["context"]["sources"]["categories"]

        self.assertEqual(confirmation["crm"]["status"], "needs_confirmation")
        self.assertEqual(confirmation["crm"]["preferred"], "Salesforce")
        self.assertEqual(confirmation["crm"]["candidates"], ["Salesforce"])
        self.assertEqual(
            confirmation["crm"]["setup_action"],
            "run_plugin_first_source_setup",
        )
        self.assertEqual(
            confirmation["crm"]["fallback_setup_action"],
            "verify_selected_app_with_simple_read",
        )
        self.assertEqual(confirmation["crm"]["saved_source_preferences"], ["Salesforce"])
        self.assertEqual(
            confirmation["crm"]["plugin_preference_order"],
            ["Salesforce", "Agentforce Sales", "HubSpot", "Close", "Zoho", "Pipedrive"],
        )

    def test_connector_confirmation_progress_requires_confirmation_before_first_workflow(
        self,
    ) -> None:
        self.state_dir.mkdir(parents=True)
        connector_confirmation = self.all_connector_confirmation()
        connector_confirmation["crm"] = {
            "status": "needs_confirmation",
            "candidates": ["Salesforce"],
        }
        (self.state_dir / "onboarding-state.json").write_text(
            json.dumps(
                {
                    "status": "active",
                    "orientation": {"status": "shown"},
                    "connector_confirmation": connector_confirmation,
                }
            ),
            encoding="utf-8",
        )

        payload = self.preflight("--request-mode", "direct_onboarding_status")
        progress = payload["control"]["onboarding_progress"]["task_list"]
        labels = [item["label"] for item in progress]
        connector_step = progress[labels.index("Connector setup/confirmation")]
        automation_step = progress[labels.index("Sales automation setup")]
        first_hero_step = progress[labels.index("First hero prompt")]

        self.assertLess(
            labels.index("Orientation"),
            labels.index("Connector setup/confirmation"),
        )
        self.assertLess(
            labels.index("Connector setup/confirmation"),
            labels.index("Sales automation setup"),
        )
        self.assertLess(
            labels.index("Sales automation setup"),
            labels.index("First hero prompt"),
        )
        self.assertEqual(connector_step["status"], "in_progress")
        self.assertTrue(connector_step["action_required"])
        self.assertEqual(automation_step["status"], "pending")
        self.assertEqual(first_hero_step["status"], "pending")

    def test_review_loop_stays_before_optional_doc_branch(self) -> None:
        self.state_dir.mkdir(parents=True)
        (self.state_dir / "onboarding-state.json").write_text(
            json.dumps(
                {
                    "status": "active",
                    "orientation": {"status": "shown"},
                    "connector_confirmation": self.all_connector_confirmation(),
                    "meeting_prep_prompt": {"status": "confirmed"},
                    "meeting_prep_run": {"status": "completed"},
                    "first_guided_workflow_review": {"status": "in_progress"},
                    "skill_experience": self.skill_experience_state(tried={"prepare-for-meeting"}),
                    "personalization_captured": [],
                }
            ),
            encoding="utf-8",
        )

        payload = self.preflight("--request-mode", "direct_onboarding_status")
        progress = payload["control"]["onboarding_progress"]["task_list"]
        by_label = {item["label"]: item for item in progress}

        self.assertEqual(by_label["First hero prompt"]["status"], "in_progress")
        self.assertEqual(by_label["Sales automation setup"]["status"], "in_progress")
        self.assertNotIn("Save prep doc", by_label)

    def test_plugin_memory_resolution_unblocks_sales_automations(self) -> None:
        self.state_dir.mkdir(parents=True)
        (self.state_dir / "onboarding-state.json").write_text(
            json.dumps(
                {
                    "status": "active",
                    "orientation": {"status": "shown"},
                    "connector_confirmation": self.all_connector_confirmation(),
                    "meeting_prep_prompt": {"status": "confirmed"},
                    "meeting_prep_run": {"status": "completed"},
                    "first_guided_workflow_review": {"status": "completed"},
                    "accepted_preference_memory": {"status": "skipped"},
                    "skill_experience": self.skill_experience_state(tried={"prepare-for-meeting"}),
                    "personalization_captured": [],
                }
            ),
            encoding="utf-8",
        )

        payload = self.preflight("--request-mode", "direct_onboarding_status")
        progress = {
            item["label"]: item["status"]
            for item in payload["control"]["onboarding_progress"]["task_list"]
        }

        self.assertNotIn("Save prep doc", progress)
        self.assertEqual(progress["Sales automation setup"], "in_progress")
        self.assertEqual(progress["First hero prompt"], "completed")

    def test_source_preferences_do_not_count_as_plugin_memory_intro(self) -> None:
        self.state_dir.mkdir(parents=True)
        (self.state_dir / "onboarding-state.json").write_text(
            json.dumps(
                {
                    "status": "active",
                    "orientation": {"status": "shown"},
                    "connector_confirmation": self.all_connector_confirmation(),
                    "meeting_prep_prompt": {"status": "confirmed"},
                    "meeting_prep_run": {"status": "completed"},
                    "first_guided_workflow_review": {"status": "completed"},
                    "skill_experience": self.skill_experience_state(tried={"prepare-for-meeting"}),
                    "personalization_captured": [
                        {
                            "category": "Source Preferences",
                            "summary": "Prefer Notion for Sales docs.",
                        }
                    ],
                }
            ),
            encoding="utf-8",
        )

        payload = self.preflight("--request-mode", "direct_onboarding_status")
        progress = {
            item["label"]: item["status"]
            for item in payload["control"]["onboarding_progress"]["task_list"]
        }

        self.assertEqual(progress["Sales automation setup"], "in_progress")
        self.assertEqual(progress["First hero prompt"], "completed")
        self.assertNotIn("Save prep doc", progress)

    def test_sales_automations_require_immediate_discovery_proposal_search(self) -> None:
        self.state_dir.mkdir(parents=True)
        ready_automation = self.ready_automation(
            "auto_123",
            "thread_123",
            "Sales Company Research",
        )
        ready_scheduled_automations = {
            key: value
            for key, value in self.ready_automations().items()
            if key != "weekly_sales_company_research"
        }
        (self.state_dir / "onboarding-state.json").write_text(
            json.dumps(
                {
                    "status": "active",
                    "orientation": {"status": "shown"},
                    "automations_intro": {"status": "started"},
                    "automations": {
                        "weekly_sales_company_research": ready_automation,
                        **{
                            key: value
                            for key, value in self.ready_automations().items()
                            if key != "weekly_sales_company_research"
                        },
                    },
                    "initial_resource_discovery": {
                        "status": "started",
                        "target_thread_title": "Sales Company Research",
                    },
                    "skill_experience": self.skill_experience_state(),
                    "personalization_captured": [],
                }
            ),
            encoding="utf-8",
        )
        payload = self.preflight("--request-mode", "direct_onboarding_status")
        missing_tip_step = next(
            item
            for item in payload["control"]["onboarding_progress"]["task_list"]
            if item["id"] == "sales_automation_setup"
        )
        self.assertEqual(missing_tip_step["status"], "completed")

        for discovery_state, expected_status, expected_action_required in (
            ({}, "pending", False),
            (
                {"status": "started", "target_thread_title": "Sales Company Research"},
                "completed",
                False,
            ),
            ({"status": "proposal_ready"}, "completed", True),
            ({"status": "completed"}, "completed", False),
        ):
            with self.subTest(discovery_state=discovery_state):
                (self.state_dir / "onboarding-state.json").write_text(
                    json.dumps(
                        {
                            "status": "active",
                            "orientation": {"status": "shown"},
                            "automations": {
                                "weekly_sales_company_research": ready_automation,
                                **ready_scheduled_automations,
                            },
                            "initial_resource_discovery": discovery_state,
                            "skill_experience": self.skill_experience_state(),
                            "personalization_captured": [],
                        }
                    ),
                    encoding="utf-8",
                )

                payload = self.preflight("--request-mode", "direct_onboarding_status")
                weekly_step = next(
                    item
                    for item in payload["control"]["onboarding_progress"]["task_list"]
                    if item["id"] == "sales_automation_setup"
                )

                self.assertEqual(weekly_step["status"], expected_status)
                self.assertEqual(
                    bool(weekly_step.get("action_required")),
                    expected_action_required,
                )

    def test_cron_automations_do_not_complete_default_sales_automation_setup(self) -> None:
        self.state_dir.mkdir(parents=True)
        cron_automations = {
            key: {
                "status": "installed",
                "canonical_id": value["canonical_id"],
                "kind": "cron",
                "target_thread_id": value["target_thread_id"],
                "target_thread_title": value["target_thread_title"],
                "target_thread_status": "pinned",
                "readback_status": "verified",
            }
            for key, value in self.ready_automations().items()
        }
        (self.state_dir / "onboarding-state.json").write_text(
            json.dumps(
                {
                    "status": "active",
                    "orientation": {"status": "shown"},
                    "connector_confirmation": self.all_connector_confirmation(),
                    "automations": cron_automations,
                    "initial_resource_discovery": {
                        "status": "started",
                        "target_thread_title": "Sales Company Research",
                    },
                    "core_onboarding": {"status": "completed"},
                }
            ),
            encoding="utf-8",
        )

        payload = self.preflight("--request-mode", "direct_onboarding_status")
        progress = payload["control"]["onboarding_progress"]
        statuses = {item["id"]: item["status"] for item in progress["task_list"]}

        self.assertFalse(progress["core_onboarding"]["complete"])
        self.assertEqual(statuses["sales_automation_setup"], "in_progress")
        self.assertEqual(progress["core_onboarding"]["remaining_step_ids"], ["sales_automation_setup"])

    def test_automations_without_readback_and_pinned_thread_metadata_are_not_ready(
        self,
    ) -> None:
        self.state_dir.mkdir(parents=True)
        incomplete_automations = {
            key: {
                "status": "installed",
                "canonical_id": value["canonical_id"],
                "kind": "heartbeat",
                "target_thread_id": value["target_thread_id"],
            }
            for key, value in self.ready_automations().items()
        }
        (self.state_dir / "onboarding-state.json").write_text(
            json.dumps(
                {
                    "status": "active",
                    "orientation": {"status": "shown"},
                    "connector_confirmation": self.all_connector_confirmation(),
                    "automations": incomplete_automations,
                    "initial_resource_discovery": {
                        "status": "started",
                        "target_thread_title": "Sales Company Research",
                    },
                    "core_onboarding": {"status": "completed"},
                }
            ),
            encoding="utf-8",
        )

        payload = self.preflight("--request-mode", "direct_onboarding_status")
        progress = payload["control"]["onboarding_progress"]
        statuses = {item["id"]: item["status"] for item in progress["task_list"]}

        self.assertFalse(progress["core_onboarding"]["complete"])
        self.assertEqual(statuses["sales_automation_setup"], "in_progress")

    def test_call_followup_drafts_are_blockquoted_team_recaps(self) -> None:
        contract = CALL_FOLLOWUP_SKILL.read_text(encoding="utf-8")

        self.assertIn("email body formatted as block quote text", contract)
        self.assertIn("Format the verbatim email body as a Markdown block quote", contract)
        self.assertIn("### External Comms", contract)
        self.assertIn("Not applicable: this was an internal call.", contract)
        self.assertIn("### Internal Follow-Up", contract)
        self.assertIn("standard bold section labels", contract)
        self.assertIn("`**Next Steps**`", contract)
        self.assertIn(
            "Format the verbatim internal follow-up draft as a Markdown block quote",
            contract,
        )
        self.assertIn("internal follow-up draft is a team meeting recap", contract)
        self.assertIn("Include a brief summary, next steps, owners or TBDs", contract)
        self.assertIn("Call notes: no useful link available", contract)
        self.assertIn(
            "clickable Markdown link when the connector exposes a useful URL",
            contract,
        )
        self.assertIn("clickable Markdown call-notes link", contract)
        self.assertIn(
            "narrow, low-risk accepted preferences can be summarized and saved automatically",
            contract,
        )

    def test_sales_skills_prefer_clickable_inline_sources(self) -> None:
        required_phrase = "When referencing sources inline, prefer clickable Markdown links"
        for skill_path in sorted((PLUGIN_ROOT / "skills").glob("*/SKILL.md")):
            with self.subTest(skill=skill_path.parent.name):
                self.assertIn(required_phrase, skill_path.read_text(encoding="utf-8"))

    def test_sales_skills_have_standard_audience_language(self) -> None:
        required_section = """### Audience And Language

Write for Sales users, not plugin maintainers. This applies to final answers, setup/status readbacks, failure explanations, tool preambles, and mid-turn progress narration.

Translate implementation work into practical Sales impact: what Sales is checking, setting up, saving, or preparing, and why it matters. Avoid implementation terms such as preflight, state file, cache, raw connector id, heartbeat, targetThreadId, schema, API, runtime, metadata, and provider taxonomy unless the user asks for debugging details."""
        legacy_phrases = (
            "Use practical sales and business language",
            "Prefer terms like accounts",
            "sales-adjacent operators",
            "preflight, cursor, probe",
        )
        for skill_path in sorted((PLUGIN_ROOT / "skills").glob("*/SKILL.md")):
            skill_text = skill_path.read_text(encoding="utf-8")
            with self.subTest(skill=skill_path.parent.name):
                self.assertEqual(1, skill_text.count(required_section))
                for phrase in legacy_phrases:
                    self.assertNotIn(phrase, skill_text)

    def test_sales_skills_use_natural_required_input_prompts(self) -> None:
        forbidden_phrases = (
            "**I need one detail to continue.**",
            "**I need a few forecast choices to continue.**",
            "Reply with a letter, or send",
            "allow the user to reply with a letter or provide a different answer",
        )
        for skill_path in sorted((PLUGIN_ROOT / "skills").glob("*/SKILL.md")):
            skill_text = skill_path.read_text(encoding="utf-8")
            with self.subTest(skill=skill_path.parent.name):
                for phrase in forbidden_phrases:
                    self.assertNotIn(phrase, skill_text)

    def test_meeting_prep_inner_sections_use_compact_labels(self) -> None:
        skill = MEETING_PREP_SKILL.read_text(encoding="utf-8")

        self.assertIn("## Output Shapes", skill)
        self.assertIn("Summary", skill)
        self.assertTrue(
            "compact bold labels, not Markdown H1/H2/H3 headings" in skill
            or all(
                phrase in skill
                for phrase in (
                    "## Summary",
                    "## Goal",
                    "## Open Questions",
                    "## Proposed Agenda",
                    "## Background Context",
                )
            )
        )

    def test_meeting_prep_has_simple_required_anchor_gate(self) -> None:
        skill = MEETING_PREP_SKILL.read_text(encoding="utf-8")

        self.assertIn("### Required Inputs", skill)
        self.assertIn("Source access can suggest concrete candidates", skill)
        self.assertIn("specific meeting/account anchor is selected or clearly inferable", skill)
        self.assertIn("bounded candidate pass", skill)
        self.assertIn("up to 5 concrete lettered options", skill)
        self.assertIn("Never present a generic instruction", skill)
        self.assertIn("{Natural clarification question", skill)
        self.assertIn(
            "The skill can still produce a limited brief from user-provided details alone",
            skill,
        )
        self.assertIn(
            "Do not stop solely because connectors are unavailable",
            skill,
        )
        self.assertNotIn("## Clarification Needed", skill)

    def test_internal_navigation_defines_internal_ownership(self) -> None:
        skill = INTERNAL_NAVIGATION_SKILL.read_text(encoding="utf-8")

        self.assertIn("### Internal Ownership", skill)
        self.assertIn("DRIs, approvers, SMEs, maintainers", skill)
        self.assertIn("recurring decision forums", skill)
        self.assertIn("canonical docs, escalation channels", skill)

    def test_preflight_reads_saved_state_and_ignores_legacy_category_state(self) -> None:
        self.state_dir.mkdir(parents=True)
        (self.state_dir / "user-context.md").write_text(
            "# Source Preferences And Defaults\n\n"
            "## Saved Links And Context\n\n"
            "Territory report preference\n"
            "- Date Added: 2026-05-22.\n"
            "- Useful Context: Validation-only Sales memory entry in a temporary state dir.\n"
            "- Future Use: Use this source before broad CRM searching for account scoping.\n",
            encoding="utf-8",
        )
        (self.state_dir / "category-state.json").write_text("{not-json", encoding="utf-8")
        (self.state_dir / "onboarding-state.json").write_text(
            json.dumps({"status": "quiet"}),
            encoding="utf-8",
        )

        payload = self.preflight()

        self.assertEqual(payload["state"]["user_context_status"], "present")
        self.assertTrue(payload["state"]["quiet"])
        self.assertEqual(payload["control"]["final_obligations"], [])
        self.assertNotIn("category_state", payload["context"])
        self.assertNotIn("category_readiness", payload["context"])
        self.assertNotIn("files_read", payload["provenance"])
        crm_source = payload["context"]["sources"]["categories"]["crm"]
        self.assertEqual(crm_source["status"], "needs_confirmation")
        self.assertNotIn("verified_app", crm_source)
        self.assertNotIn("installed", crm_source)
        self.assertEqual(
            payload["context"]["sources"]["resolution"],
            "plugin_or_app_or_connector_then_manual_context",
        )
        self.assertEqual(
            payload["context"]["user_context"]["entries"][0],
            (
                "Source Preferences And Defaults: Territory report preference | "
                "Validation-only Sales memory entry in a temporary state dir"
            ),
        )

    def test_sources_are_compact_runtime_preferences(self) -> None:
        payload = self.preflight("--workflow", "plan-deal-strategy")
        sources = payload["context"]["sources"]["categories"]

        self.assertEqual(
            sources["crm"]["helper_skills"],
            [
                {"app": "Salesforce", "skill": "salesforce"},
                {"app": "Agentforce Sales", "skill": "salesforce"},
                {"app": "HubSpot", "skill": "hubspot"},
            ],
        )
        self.assertEqual(
            payload["context"]["sources"]["resolution"],
            "plugin_or_app_or_connector_then_manual_context",
        )
        for entry in sources.values():
            self.assertNotIn("evidence", entry)
            self.assertNotIn("checked", entry)
            self.assertNotIn("importance", entry)
            self.assertNotIn("setup_preference_order", entry)

    def test_source_categories_have_no_author_configurable_importance_or_readiness_state(
        self,
    ) -> None:
        source_category_config_path = (
            PLUGIN_ROOT / "skills/user-context/plugin-author-config/source-category-config.json"
        )
        source_category_config = json.loads(source_category_config_path.read_text(encoding="utf-8"))
        source_category_config_text = json.dumps(source_category_config, sort_keys=True)
        source_category_runtime = SOURCE_RUNTIME_REFERENCE.read_text(encoding="utf-8")
        app_manifest = json.loads((PLUGIN_ROOT / ".app.json").read_text(encoding="utf-8"))
        declared_apps = {
            "".join(ch for ch in app_key.casefold() if ch.isalnum())
            for app_key in app_manifest["apps"]
        }

        self.assertEqual(
            source_category_config["schema_version"],
            "sales_source_category_config.v1",
        )
        self.assertIn("crm", source_category_config["categories"])
        self.assertIn("meeting_notes", source_category_config["categories"])
        self.assertIn("spreadsheets", source_category_config["categories"])
        for metadata in source_category_config["categories"].values():
            self.assertIn("label", metadata)
            self.assertIsInstance(metadata.get("preferred_apps"), list)
            self.assertLessEqual(
                set(metadata),
                {"label", "preferred_apps", "preferred_plugins", "relevant_skills"},
            )
            if "preferred_plugins" in metadata:
                self.assertIsInstance(metadata["preferred_plugins"], list)
                for preferred_plugin in metadata["preferred_plugins"]:
                    self.assertIsInstance(preferred_plugin, str)
                    self.assertTrue(preferred_plugin)
            if "relevant_skills" in metadata:
                self.assertIsInstance(metadata["relevant_skills"], list)
                for entry in metadata["relevant_skills"]:
                    self.assertIsInstance(entry, dict)
                    self.assertIsInstance(entry.get("app"), str)
                    self.assertIsInstance(entry.get("skill"), str)
            for preferred_app in metadata["preferred_apps"]:
                normalized = "".join(ch for ch in preferred_app.casefold() if ch.isalnum())
                aliases = {normalized}
                if normalized.endswith("com"):
                    aliases.add(normalized[:-3])
                if normalized == "agentforcesales":
                    aliases.add("salesforce")
                self.assertTrue(
                    aliases & declared_apps,
                    msg=f"{preferred_app} is not declared in .app.json",
                )
        self.assertIn(
            "Outlook Calendar",
            source_category_config["categories"]["calendar"]["preferred_apps"],
        )
        self.assertIn("salesforce", declared_apps)
        self.assertIn(
            "Outlook Email",
            source_category_config["categories"]["external_messaging"]["preferred_apps"],
        )
        self.assertIn(
            "Microsoft Teams",
            source_category_config["categories"]["internal_messaging"]["preferred_apps"],
        )
        self.assertIn(
            "Microsoft SharePoint",
            source_category_config["categories"]["document_store"]["preferred_apps"],
        )
        self.assertEqual(
            source_category_config["categories"]["spreadsheets"]["preferred_plugins"],
            ["Spreadsheets", "Microsoft Excel"],
        )
        self.assertEqual(
            source_category_config["categories"]["spreadsheets"]["preferred_apps"],
            ["Google Drive", "Microsoft SharePoint"],
        )
        self.assertEqual(
            source_category_config["categories"]["meeting_notes"]["preferred_apps"],
            ["Zoom", "Granola", "Otter.ai", "Fireflies", "Outreach", "Rox"],
        )
        self.assertIn(
            '"options": ["Zoom", "Granola", "Otter.ai", "Fireflies", "Outreach", "Rox"]',
            source_category_runtime,
        )
        self.assertIn("Plugin-First Setup For Missing Sources", source_category_runtime)
        self.assertIn("functions.list_available_plugins_to_install", source_category_runtime)
        self.assertIn("functions.request_plugin_install", source_category_runtime)
        self.assertIn("Available plugins", source_category_runtime)
        self.assertIn("Available skills", source_category_runtime)
        self.assertIn("plugin_install_evidence", source_category_runtime)
        self.assertIn("skill_surface_evidence", source_category_runtime)
        self.assertIn("app_surface_evidence", source_category_runtime)
        self.assertIn("run_plugin_first_source_setup", source_category_runtime)
        self.assertIn("saved_source_preferences", source_category_runtime)
        self.assertIn("plugin_preference_order", source_category_runtime)
        self.assertIn("plugin_first_source_setup", source_category_runtime)
        self.assertIn("connector-id intersection", source_category_runtime)
        self.assertIn("setup fails", source_category_runtime)
        self.assertIn("surface plugin-first setup again in a future workflow", source_category_runtime)
        self.assertIn("Prefer plugin candidates over connector candidates", source_category_runtime)
        self.assertIn(
            "including a plugin that contains or declares a connector/app id",
            source_category_runtime,
        )
        self.assertIn(
            "add dedicated Sales workflow support",
            source_category_runtime,
        )
        self.assertIn("Do not use `tool_search` as proof", source_category_runtime)
        self.assertIn("## Runtime Source Resolution", source_category_runtime)
        self.assertIn("A successful read is evidence for this run only", source_category_runtime)
        self.assertIn("## Durable Source Preferences", source_category_runtime)
        self.assertIn("I do not have ZoomInfo", source_category_runtime)
        self.assertNotIn("Importance:", source_category_config_text)
        self.assertNotIn("user_importance", source_category_config_text)
        self.assertNotIn("- Priority:", source_category_config_text)
        self.assertNotIn("- Typical apps:", source_category_config_text)
        self.assertNotIn("Required for:", source_category_config_text)
        self.assertNotIn("Recommended for:", source_category_config_text)
        self.assertNotIn("why_it_matters", source_category_config_text)
        self.assertNotIn("most_useful_for", source_category_config_text)
        self.assertNotIn("verification_note", source_category_config_text)
        self.assertFalse((SKILL_ROOT / "references/category-state-template.json").exists())
        self.assertFalse((SKILL_ROOT / "references/hero-prompts.md").exists())

    def test_automation_config_is_author_friendly_and_preflight_summarizes_it(self) -> None:
        automation_config = (
            PLUGIN_ROOT / "skills/user-context/plugin-author-config/automation-config.md"
        ).read_text(encoding="utf-8")

        for phrase in (
            "- Name:",
            "- Frequency:",
            "- Instructions:",
            "daily_sales_tips",
            "daily_meeting_prep",
            "weekly_sales_company_research",
            "## Later Journey Automations",
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
            self.assertIn(phrase, automation_config)
        for runtime_detail in (
            "Use GPT-5.5 with",
            "- Kind:",
            "- RRULE:",
            "- Skill:",
            "- Scheduled mode:",
            "- Prompt:",
            "Onboarding notification:",
            "- Target thread title:",
            "Sales company research is complete. {N} new resources saved.",
        ):
            self.assertNotIn(runtime_detail, automation_config)

        payload = self.preflight("--request-mode", "direct_onboarding_status")
        automation_plan = payload["context"]["automations"]
        self.assertEqual(
            automation_plan["daily_sales_tips"]["frequency"],
            "weekdays at 9:00 AM local time",
        )
        self.assertEqual(
            automation_plan["daily_meeting_prep"]["status"],
            "not_configured",
        )
        self.assertNotIn("instructions", automation_plan["daily_meeting_prep"])
        self.assertNotIn("target_thread_title", automation_plan["weekly_sales_company_research"])
        self.assertNotIn("instructions", automation_plan["weekly_sales_company_research"])

    def test_automation_runtime_specifies_supported_model_and_reasoning(self) -> None:
        automation_reference = AUTOMATION_REFERENCE.read_text(encoding="utf-8")

        for phrase in (
            '`model="gpt-5.5"`',
            '`thinking="low"`',
            '`thinking="xhigh"`',
            "do not fall back to `gpt-5`",
            "## Fast Setup Checklist",
            "Discover `automation_update` and the thread tools",
            "Create or update the automation with `kind=\"heartbeat\"`",
            "the exact `targetThreadId`",
            "stored `target_thread_id` matches the pinned thread",
            "Update `onboarding-state.json` with only operational metadata",
            "Stop. Report the concise setup result",
            "No setup kickoff; let the first scheduled check-in run on its own",
            "Do not send an immediate Sales Tips kickoff during onboarding",
            "Do not mark setup complete after a plain cron automation",
            "Sales Company Research: load and follow `$sales:sales-company-research`",
            "Do not paste source-family lists, ranking rules, save gates, output examples, model names, reasoning effort, or focused-skill workflow contracts",
        ):
            self.assertIn(phrase, automation_reference)

    def test_large_context_still_renders_compact_context(self) -> None:
        self.state_dir.mkdir(parents=True)
        (self.state_dir / "user-context.md").write_text(
            "# Action Orientation Preferences\n\n"
            "## Saved Links And Context\n\n"
            "Concise prep briefs\n"
            "- Date Added: 2026-05-22.\n"
            "- Useful Context: Section extraction validation.\n"
            "- Future Use: Preserve nested subsection content.\n\n"
            "# Other Category\n\n" + ("x" * 500),
            encoding="utf-8",
        )

        payload = self.preflight(
            "--max-context-bytes",
            "80",
            "--section",
            "Action Orientation Preferences",
        )

        self.assertNotIn("user_context_markdown", payload["context"])
        self.assertNotIn("omitted", payload["provenance"])
        self.assertEqual(payload["provenance"]["user_context"], "read")
        entry = payload["context"]["user_context"]["entries"][0]
        self.assertEqual(
            entry,
            "Action Orientation Preferences: Concise prep briefs | Section extraction validation",
        )

    def test_onboarding_copy_keeps_visible_action_close_small_and_plugin_first(self) -> None:
        onboarding = ONBOARDING_REFERENCE.read_text(encoding="utf-8")
        plugin_memory = (SKILL_ROOT / "references/plugin-memory.md").read_text(encoding="utf-8")
        automation_config = (
            PLUGIN_ROOT / "skills/user-context/plugin-author-config/automation-config.md"
        ).read_text(encoding="utf-8")

        self.assertIn("# Sales Onboarding Flow", onboarding)
        self.assertIn("Step 1: Orientation", onboarding)
        self.assertIn("Ordinary Workflow Onboarding CTA", onboarding)
        self.assertIn("## Sales Setup Required", onboarding)
        self.assertIn("Reply `start` to continue.", onboarding)
        self.assertIn(
            "This is required before Sales can reliably use your connected sources",
            onboarding,
        )
        self.assertIn(
            "Every onboarding message that is not complete must include primary content",
            onboarding,
        )
        self.assertIn("`Next Step` is the action prompt, not the explainer", onboarding)
        self.assertIn(
            "A natural final sentence, a compact action frame, or a self-contained numbered choice set can satisfy this requirement",
            onboarding,
        )
        self.assertIn(
            "Do not let the whole onboarding message be only a next-step frame", onboarding
        )
        self.assertIn("When the current step has open questions", onboarding)
        self.assertIn(
            "Use a compact numbered list when there is more than one question", onboarding
        )
        self.assertIn(
            "include the default escape hatch inside the relevant numbered item",
            onboarding,
        )
        self.assertIn("Do not add a separate summary prompt after the numbered list", onboarding)
        self.assertIn(
            "When introducing a workflow, skill, or new onboarding concept for the first time",
            onboarding,
        )
        self.assertIn("## New Concept Introduction Pattern", onboarding)
        self.assertIn("Do not create tiny transition turns", onboarding)
        self.assertIn("Okay, I've saved that. Now let's move on to the next step.", onboarding)
        self.assertIn("Okay, that finishes source setup for now. Sales will use", onboarding)
        self.assertIn(
            "do not render the full `Saved Sales Plugin Memory.` recap or `Saved today` list",
            onboarding,
        )
        self.assertIn(
            "Preserve real approval gates",
            onboarding,
        )
        self.assertIn("## {Concept Name}", onboarding)
        self.assertIn("the body should start with `This skill...`", onboarding)
        self.assertIn(
            "Plugin memory is how the Sales plugin remembers approved preferences",
            onboarding,
        )
        self.assertIn("simple automations to ensure Sales keeps getting better for you", onboarding)
        self.assertIn("Do not render user-facing CTAs with code-styled skill names", onboarding)
        self.assertIn("User-facing bullets should be polished sentence fragments", onboarding)
        self.assertIn("Do not start bullets with lowercase words", onboarding)
        self.assertIn("teach the preferred invocation pattern", onboarding)
        self.assertIn("The Sales plugin improves Codex at sales-related work", onboarding)
        self.assertIn("**How it works**", onboarding)
        self.assertIn("**What it can do**", onboarding)
        self.assertIn("It automatically improves your experience", onboarding)
        self.assertIn("start with `@Sales`", onboarding)
        self.assertIn("start a new thread and include `@Sales`", onboarding)
        self.assertIn("Ready to set that up?", onboarding)
        self.assertIn("After some searching, it looks like you're already set up", onboarding)
        self.assertIn("calls `functions.list_available_plugins_to_install` once for the setup pass", onboarding)
        self.assertIn("If the user confirms an installable plugin or connector candidate", onboarding)
        self.assertIn("installable related plugin needs approval", onboarding)
        self.assertIn("saved_source_preferences", onboarding)
        self.assertIn("add dedicated Sales workflow support", onboarding)
        self.assertIn("Keep plugin-first setup eligible for retry in future workflows", onboarding)
        self.assertIn("Do not call `request_plugin_install` in parallel", onboarding)
        self.assertIn("## Active Onboarding Reminder", onboarding)
        self.assertIn("Do not use the `## Sales Setup Required` start CTA", onboarding)
        self.assertIn("@Sales prepare me for my Acme renewal call tomorrow", onboarding)
        self.assertIn(
            "The numbered choice set is the final action prompt by itself",
            onboarding,
        )
        self.assertIn("do not add a `Next Step` heading", onboarding)
        self.assertIn(
            "Keep automation breadcrumbs, readback cards, and created-card text visually separate from the choice set",
            onboarding,
        )
        self.assertIn("Do not reuse a stale checklist from an earlier thread turn", onboarding)
        self.assertIn("mark the next unresolved visible step as `in_progress`", onboarding)
        self.assertIn("Do not render `Next Step` as an H1/H2/H3 heading", onboarding)
        self.assertIn("**Onboarding Complete**", onboarding)
        self.assertIn("You can keep going through the rest of the Sales skills", onboarding)
        self.assertIn("Say `okay` and I'll introduce Analyze Account Signals", onboarding)
        self.assertIn("Progress Checklist Contract", onboarding)
        self.assertIn("Orientation", onboarding)
        self.assertIn("Connector setup/confirmation", onboarding)
        self.assertIn("Sales automation setup", onboarding)
        self.assertIn("First hero prompt", onboarding)
        self.assertIn("Other hero prompts", onboarding)
        self.assertIn("core onboarding is complete", onboarding)
        self.assertNotIn("Choose prepare-for-meeting prompt", onboarding)
        self.assertNotIn("Save prep doc", onboarding)
        self.assertNotIn("Explain plugin memory", onboarding)
        self.assertNotIn("Capture key context", onboarding)
        self.assertIn("Choose Next Hero Prompt", onboarding)
        self.assertIn("Introduce Selected Remaining Hero Workflow", onboarding)
        self.assertIn("Run Selected Remaining Hero Demo", onboarding)
        self.assertIn("Review And Continue Remaining Hero", onboarding)
        self.assertIn("Sales Daily Meeting Prep", onboarding)
        self.assertNotIn("Sales Weekday Check-In", onboarding)
        self.assertNotIn("**Next Step: Resolve Sources, Then Try Prepare For Meeting**", onboarding)
        self.assertNotIn("Two source notes before we continue", onboarding)
        self.assertNotIn("Reply with a docs preference or enrichment info", onboarding)
        self.assertIn("You can skip anything now; Sales will ask again later", onboarding)
        self.assertIn("## Step 4: First Hero Prompt", onboarding)
        self.assertIn("Do not run another hero workflow until the user picks", onboarding)
        self.assertIn("treat the numbered choice as consent to try that workflow", onboarding)
        self.assertIn(
            "render that skill's compact first-run intro above the normal workflow output",
            onboarding,
        )
        self.assertIn("choose_first_hero_prompt", onboarding)
        self.assertIn("Introduce Selected First Hero Workflow", onboarding)
        self.assertIn("## Prepare For Meeting", onboarding)
        self.assertIn("start fresh with `This skill...`", onboarding)
        prepare_intro = onboarding.split("For Prepare For Meeting", 1)[1][:700]
        self.assertIn("`okay`", prepare_intro)
        self.assertIn("`calendar`", prepare_intro)
        self.assertIn("manual meeting details", prepare_intro)
        self.assertIn("skills/prepare-for-meeting/SKILL.md", onboarding)
        self.assertIn("inline experience guidance", onboarding)
        self.assertIn("move directly into Step 3A", onboarding)
        self.assertNotIn("Want me to introduce Prepare For Meeting next?", onboarding)
        self.assertIn("Sales will ask again later only when a workflow would materially benefit", onboarding)
        self.assertNotIn("**Next Step: Set Up Sales Automations**", onboarding)
        self.assertNotIn("\n## Sales Plugin Automations\n", onboarding)
        self.assertIn(
            "Should I set those up? They'll run in a different thread and notify you when they have something to review.",
            onboarding,
        )
        self.assertIn("Sales Tips", onboarding)
        self.assertIn(
            "Do not load hero workflow skill files or run a demo workflow until the user picks one",
            onboarding,
        )
        self.assertIn("automation.md#Fast Setup Checklist", onboarding)
        self.assertIn("Automations are set up and read back cleanly", onboarding)
        self.assertIn(
            "I also kicked off the first research run in the pinned **Sales Company Research** thread",
            onboarding,
        )
        self.assertIn(
            "starting with its next scheduled run",
            onboarding,
        )
        self.assertIn("one practical Sales workflow to try next", onboarding)
        self.assertIn("Do not compress the three hero choices into one inline sentence", onboarding)
        self.assertIn("each numbered option must be on its own line", onboarding)
        self.assertIn("Core onboarding is done. Pick a workflow to try first:", onboarding)
        self.assertIn(
            "1. **Prepare For Meeting:** Builds a concise brief for an upcoming customer or high-value sales meeting.",
            onboarding,
        )
        self.assertIn(
            "2. **Follow Up After Call:** Turns a recent call or notes into a recap, next steps, email draft, CRM-ready update, and internal recap.",
            onboarding,
        )
        self.assertIn(
            "3. **Prioritize Accounts:** Helps you understand what needs to be done with your accounts by flagging anomalies, building forecasts, and prioritizing accounts.",
            onboarding,
        )
        self.assertIn("1. **{Core skill display name}:** {One-sentence value description", onboarding)
        self.assertNotIn("1. Prepare For Meeting\n   {One-sentence value description", onboarding)
        self.assertNotIn("2. Follow Up After Call\n   {One-sentence value description", onboarding)
        self.assertIn("3. **{Core skill display name}:** {One-sentence value description", onboarding)
        self.assertNotIn(
            "Example prompt: `@Sales {realistic prompt from that skill's experience file}`",
            onboarding,
        )
        self.assertNotIn("Choose one to try first: `1`", onboarding)
        self.assertNotIn("Pick `1`, `2`, or `3`, or name a real meeting", onboarding)
        self.assertIn("weekly on Mondays at 9:00 AM local time", onboarding)
        self.assertIn("runs weekdays at 9:00 AM local time", onboarding)
        self.assertIn('FYI: The pinned thread **"{thread_title}"**', onboarding)
        self.assertIn(
            "Only say saved entries or proposals exist when state or readback confirms them",
            onboarding,
        )
        self.assertNotIn("**Next Step: Try Call Follow-Up**", onboarding)
        self.assertIn("## Step 5: Other Hero Prompts", onboarding)
        self.assertIn("choose_next_hero_prompt", onboarding)
        self.assertIn(
            "Hero demos use a repeatable artifact loop",
            onboarding,
        )
        self.assertIn("hero_workflow.current_status", onboarding)
        self.assertIn("offer_first_hero_action_or_next_demo", onboarding)
        self.assertIn("offer_remaining_hero_action_or_next_demo", onboarding)
        self.assertIn("normal next-step candidates", onboarding)
        self.assertIn("show the next demo workflow choices", onboarding)
        self.assertIn("start fresh with `This skill...`", onboarding)
        self.assertIn(
            "Choices can include the previous one or two workflows as repeat options",
            onboarding,
        )
        self.assertIn("Do not offer only previously tried workflows", onboarding)
        self.assertIn("skills/follow-up-after-call/SKILL.md", onboarding)
        self.assertNotIn("**Next Step: Try Prioritize Accounts**", onboarding)
        self.assertIn("## Step 6: Completion", onboarding)
        self.assertIn(
            "prioritize open pipeline by default",
            onboarding,
        )
        self.assertIn("skills/prioritize-accounts/SKILL.md", onboarding)
        self.assertNotIn("Add starter context", onboarding)
        self.assertNotIn("Connected Source Check", onboarding)
        self.assertIn("Do not preflight-read installed or active sources", onboarding)
        self.assertIn("Calendar attachment is explicit-user-request only", onboarding)
        self.assertIn("response-first fast path", onboarding)
        self.assertIn("Do not run `../scripts/init_user_context_state.py`", onboarding)
        self.assertIn("not in the main onboarding thread", onboarding)
        self.assertIn("Install or repair only `weekly_sales_company_research` and `daily_sales_tips`", onboarding)
        self.assertIn("`weekly_sales_company_research` and `daily_sales_tips`", onboarding)
        self.assertNotIn("Want me to introduce Follow Up After Call next?", onboarding)
        self.assertIn("return to the next demo workflow chooser", onboarding)
        self.assertIn("The initial Sales Company Research kickoff belongs in the pinned", onboarding)
        sales_company_research = SALES_COMPANY_RESEARCH_SKILL.read_text(encoding="utf-8")
        self.assertIn("pinned `Sales Company Research` automation thread", plugin_memory)
        self.assertIn("Exception: during the routine onboarding source setup step", plugin_memory)
        self.assertIn(
            "Plugin memory is how the Sales plugin remembers approved preferences",
            plugin_memory,
        )
        self.assertIn("Do not copy saved resource lists", plugin_memory)
        self.assertIn("Saved today:", plugin_memory)
        self.assertIn("save the accepted narrow preference in the same response", plugin_memory)
        self.assertIn("source-of-truth resources and answer/style preferences", plugin_memory)
        self.assertIn(
            "Discovery-derived memory may be saved by default only when it is high-confidence",
            plugin_memory,
        )
        self.assertIn("Route company-context discovery to `sales-company-research`", plugin_memory)
        self.assertIn("This reference owns the save and review gates", plugin_memory)
        self.assertIn("Keep the automation prompt thin by invoking `sales-company-research`", plugin_memory)
        self.assertIn("company-unique semantics", sales_company_research)
        self.assertIn("authoritative interpretation layers", sales_company_research)
        self.assertIn("pipeline stage definitions and exit criteria", sales_company_research)
        self.assertIn("do not append onboarding reminders or onboarding CTAs", sales_company_research)
        self.assertIn("Do not stop after the first few obviously relevant docs", sales_company_research)
        self.assertIn("second-pass search", sales_company_research)
        self.assertIn("Keep multiple resources when they serve distinct authority lanes", sales_company_research)
        self.assertIn("one-sentence utility description", sales_company_research)
        self.assertIn("Sales company research is complete. {N} new resources saved.", sales_company_research)
        self.assertIn("What was found", sales_company_research)
        self.assertIn("Where you can help", sales_company_research)
        self.assertIn("Do not include coverage notes or operational research bookkeeping", sales_company_research)
        self.assertIn("safe-use caveat", sales_company_research)
        self.assertIn("legal/comms/customer-facing claims guardrails", sales_company_research)
        self.assertIn("up to five `Where you can help` questions", sales_company_research)
        self.assertIn("Start each bullet with the resource title as a Markdown link", sales_company_research)
        self.assertIn("Do not include category labels such as `saved under`", sales_company_research)
        self.assertIn("Every saved resource must explain why it helps the user", sales_company_research)
        self.assertIn("Do not output bare link bullets", sales_company_research)
        self.assertIn("Convert material limitations into concrete `Where you can help` questions", sales_company_research)
        self.assertIn(
            "Load and follow `$sales:sales-company-research` in scheduled research mode",
            automation_config,
        )
        self.assertIn(
            "dynamic source discovery",
            automation_config,
        )
        self.assertNotIn("Use GPT-5.5 with", automation_config)
        self.assertIn("Iteration Acceptance Learning", plugin_memory)
        self.assertNotIn("3-5 minutes", onboarding)
        self.assertNotIn("setup/check usually takes 3-5 minutes", onboarding)
        self.assertNotIn("Saved setup state", onboarding)
        self.assertNotIn("Onboarding status", onboarding)

    def test_skill_experience_examples_teach_sales_invocation_pattern(self) -> None:
        self.assertFalse((SKILL_ROOT / "references/hero-prompts.md").exists())
        prepare_skill = MEETING_PREP_SKILL.read_text(encoding="utf-8")
        followup_skill = CALL_FOLLOWUP_SKILL.read_text(encoding="utf-8")
        internal_sources_skill = INTERNAL_NAVIGATION_SKILL.read_text(encoding="utf-8")
        index_skill = (PLUGIN_ROOT / "skills/index/SKILL.md").read_text(encoding="utf-8")
        onboarding = ONBOARDING_REFERENCE.read_text(encoding="utf-8")
        user_context_skill = (PLUGIN_ROOT / "skills/user-context/SKILL.md").read_text(
            encoding="utf-8"
        )

        self.assertIn("### First-Run Banner", prepare_skill)
        self.assertIn("## Prepare For Meeting", prepare_skill)
        self.assertIn("This skill creates a concise brief", prepare_skill)
        self.assertNotIn("Prepare For Meeting is a skill in the Sales plugin", prepare_skill)
        self.assertIn("### First-Run Banner", followup_skill)
        self.assertIn("## Follow Up After Call", followup_skill)
        self.assertIn("This skill turns a recent customer", followup_skill)
        self.assertNotIn("Follow Up After Call is a skill in the Sales plugin", followup_skill)
        self.assertIn("A quick call summary", onboarding)
        self.assertIn(
            "@Sales find who owns the Enterprise SSO rollout path for Acme",
            internal_sources_skill,
        )
        self.assertIn("### First-Run Banner", internal_sources_skill)
        self.assertIn("## Find Key Internal Sources", internal_sources_skill)
        self.assertIn(
            "This skill helps locate the people",
            internal_sources_skill,
        )

        self.assertIn(
            "start with `@Sales`, name the sales job, and use a realistic anchor", index_skill
        )
        self.assertIn("@Sales prepare me for my next customer meeting", index_skill)
        self.assertIn("@Sales follow up from my latest customer call", index_skill)
        self.assertIn("@Sales prioritize my accounts for pipeline focus this week", index_skill)
        self.assertIn(
            "Loading the relevant skill-owned experience guidance is mandatory whenever that skill is the primary workflow",
            user_context_skill,
        )
        self.assertIn(
            "the final continuation invariant for primary outputs and follow-up turns",
            user_context_skill,
        )
        self.assertIn(
            "end with one concrete user-visible next action phrased as a natural sentence or question",
            user_context_skill,
        )
        self.assertIn(
            "Clarification questions must be the final natural continuation",
            user_context_skill,
        )
        self.assertIn(
            "render the compact first-run intro section",
            user_context_skill,
        )

        for skill_name in USER_FACING_SKILLS:
            skill_text = (PLUGIN_ROOT / f"skills/{skill_name}/SKILL.md").read_text(encoding="utf-8")
            self.assertFalse(
                (PLUGIN_ROOT / f"skills/{skill_name}/references/experience.md").exists()
            )
            self.assertIn("### First-Run Banner", skill_text)
            self.assertIn("### Next Step Guidance", skill_text)
            self.assertIn(
                "#### Final Continuation Invariant",
                skill_text,
            )
            self.assertIn("another active parent flow owns the final CTA", skill_text)

    def test_prepare_for_meeting_offers_daily_prep_before_meeting_doc(self) -> None:
        skill_text = MEETING_PREP_SKILL.read_text(encoding="utf-8")

        self.assertLess(
            skill_text.index("| **Offer Daily Meeting Prep**"),
            skill_text.index("| **Create a meeting doc**"),
        )
        self.assertIn(
            "Daily Meeting Prep is the primary accepted-brief continuation owned by this skill",
            skill_text,
        )
        self.assertIn(
            "Do not offer meeting doc creation as the accepted-brief default while Daily Meeting Prep remains eligible",
            skill_text,
        )
        self.assertIn(
            "if Daily Meeting Prep is eligible, move to `Offer Daily Meeting Prep`",
            skill_text,
        )
        self.assertIn(
            "If the previous continuation was `Offer Daily Meeting Prep`, treat a lightweight acknowledgement as approval",
            skill_text,
        )

    def test_onboarding_has_no_eager_active_connector_reads(self) -> None:
        onboarding = ONBOARDING_REFERENCE.read_text(encoding="utf-8")

        self.assertIn("Do not preflight-read installed or active sources just to prove they work", onboarding)
        self.assertIn("prefer plugin setup", onboarding)
        self.assertIn("direct app/connector setup", onboarding)
        self.assertIn("without a proof read", onboarding)
        self.assertNotIn("verified source", onboarding.casefold())

if __name__ == "__main__":
    unittest.main()
