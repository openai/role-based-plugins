# Sales

This plugin packages a portable subset of sales workflows as manual-first skills.

The goal is to make the workflows useful for an arbitrary company that may have:
- strong CRM and meeting notes provider coverage
- partial tooling with CSV exports and shared document stores
- mostly manual notes, transcripts, and spreadsheets

Most customer-facing skills in this plugin must work with uploaded files, pasted context, exports, and web research when source tools are unavailable. Transcript-specific workflows must support uploaded or pasted transcript material when possible, but they should not use public web research as a substitute for customer quote evidence. During onboarding or explicit source setup, Sales should inspect the environment, prefer related plugins whenever they are installed or installable, and use direct app/connector routes only as fallback. Setup writes the resolved route into onboarding state; ordinary preflight reads that route, and workflows use it when they need the source. Treat external customer-facing communications and internal team discussion as distinct source categories so the workflow can choose an external email or shared-thread source separately from an internal channel source.

## Plugin structure

- `skills/`: generalized skill packages
- `.app.json`: app connector configuration
- `skills/user-context/plugin-author-config/`: author-editable user-context knowledge, source-category/preferred-app, and default automation configuration surfaces

## Risk items and known unknowns

| Area | Risk / known unknown | Current posture |
| --- | --- | --- |
| App IDs | All `.app.json` IDs are workspace-specific. Customer release needs the target workspace's connector IDs or app installation flow. | Flagged; manifest shape is valid, but IDs must be manually revalidated against the target workspace's app/connector registry before release or customer install. Salesforce and Agentforce Sales are represented as separate source entries so the model can choose the best Salesforce-family plugin or connector path. |
| Source category coverage | Some workflows can benefit from enrichment or market context through the `data_enrichment` source category. | Source setup writes the resolved route for each category. Prefer related plugin setup, including plugins that contain a configured connector, then configured app/connector setup, then fall back to manual exports, user-provided context, or public research when appropriate. |
| Account intelligence / customer 360 | There is no dedicated source category for customer-specific account-intelligence systems. | Represent account state and history with `crm`, narrative notes with `document_store`, and recency signals with `meeting_notes`, `external_messaging`, `internal_messaging`, and `calendar`. Add a new source category only if a release target has a real source category for it. |
| Call-transcript tooling | Coaching and VOC skills use `meeting_notes` heavily. | Prefer a dedicated meeting-notes or transcript app such as Zoom, Granola, Fireflies, or another approved meeting-notes source, and confirm it supports search, fetch, transcript URLs, and enough participant metadata for quote attribution. Drive-hosted meeting notes can be used when reachable through document search, but they are fallback coverage and should be treated as summarized notes unless they contain speaker-labeled transcript text. |
| Manual and web-only lanes | Public web research, LinkedIn enrichment, and generic customer-360/account-intelligence systems do not have dedicated configured connectors today. Task tracker context can use configured `monday` when explicitly requested, but no current workflow lists project tracker as a source category by default. | Keep manual sources optional, explicitly user-provided, or represented through existing source categories (`crm`, `document_store`, `external_messaging`, `internal_messaging`, `calendar`, `meeting_notes`) when the mapping is clear. Treat `monday` as opt-in task-tracker context. |

## Included skills

- `index`
- `hubspot`
- `salesforce`
- `analyze-account-signals`
- `build-competitive-brief`
- `follow-up-after-call`
- `enrich-company-and-contact-data`
- `plan-deal-strategy`
- `find-key-internal-sources`
- `prepare-for-meeting`
- `suggest-sales-next-step`
- `prioritize-accounts`
- `find-customer-quotes`
- `review-forecast`
- `user-context`
- `get-rep-call-feedback`
- `review-rep-call-trends`
- `build-business-case`
- `zoominfo`

## Design rules

- Target audience language is part of the plugin contract. Sales is for sellers, account teams, sales leaders, and sales-adjacent operators, many of whom are non-technical. User-facing output should use practical sales and business language by default. Standard terms such as `CRM`, `Slack`, `email`, `pipeline`, `forecast`, `connected tools`, `connector`, `source`, `draft`, and `next step` are acceptable when they help the user decide or act. Keep internal implementation and state-machine terms out of final answers unless the user asks for implementation details; examples include `preflight`, `cursor`, `probe`, `state file`, raw connector/refetch ids, `metadata`, `runtime`, `artifact`, `lane`, and provider taxonomy. When a technical term is necessary, pair it with the seller value and the decision it affects.
- No direct connector reference syntax appears in skill instructions. Source usage is optional and described by neutral source categories such as `crm`, `meeting_notes`, or `data_enrichment`; setup chooses and writes the source route, then runtime workflows consume it. For missing sources and connector-covered sources, prefer related plugin setup before connector/app setup and manual fallback. Use `external_messaging` for customer-facing email/shared-thread evidence and `internal_messaging` for internal channels, team discussion, and internal draft destinations.
- Task tracker/project tracker context is available through configured `monday`; use it only when the user or workflow explicitly expands into project/task tracking, and add or validate a project tracker source category before making it a normal lane in a focused skill.
- Category-level helper routing lives in `skills/user-context/plugin-author-config/source-category-config.json` as `relevant_skills`. Use those helper skills only when the attempted source category and selected app/source match, and keep the focused workflow authoritative for the seller task. Plugin-first setup behavior lives in `skills/user-context/references/source-category-runtime.md`; do not duplicate install-list, plugin candidate matching, active-connector upgrade prompts, or connector fallback policy inside individual focused skills.
- Default onboarding automations live in `skills/user-context/plugin-author-config/automation-config.md` using author-friendly fields: name, frequency, and instructions. The target thread title is derived from the name. Keep heartbeat setup, thread creation, pinning, readback, and duplicate cleanup mechanics in `skills/user-context/references/automation.md`. Guided onboarding installs weekly discovery automatically only when that visible step is active; the first orientation stays fast and does not create automations.
- Every user-facing Sales skill owns its first-run experience inline in `SKILL.md`: intro copy, starter prompts, anchor rules, normal next-step candidates, and onboarding-yield behavior. Onboarding can choose which skill to run next, but it should not duplicate skill-specific intro or starter-prompt copy. First-run definitions should be sparse and user-value-driven: include only acronyms, ambiguous sales jargon, or high-consequence workflow terms that materially change how the user interprets the workflow. Do not define ordinary artifact labels, obvious output sections, or self-evident phrases such as prep brief, follow-up package, focus hypothesis, customer-facing asset, work now, why now, or internal follow-up.
- When a workflow selects HubSpot or Salesforce for `crm`, use the matching connector user guide skill for connector-specific rules and constructs, including CRM-backed drafting. Do not use those guides for another CRM connector or for flows with no CRM lane.
- Store private sales terminology, company-specific CRM field conventions, buyer personas, source-of-truth links, customer/account context, output preferences, messaging norms, escalation paths, and other Sales plugin-scoped facts in `$CODEX_HOME/state/plugins/role-based-plugins/sales/user-context.md` through `user-context`, not in bundled plugin files.
- Every `SKILL.md`, including helper/provider guides, must include the mandatory user-context pre-answer gate before ordinary workflow work. Do not soften this to "invoke user-context"; future edits should preserve wording that requires actually reading and applying `$CODEX_HOME/state/plugins/role-based-plugins/sales/user-context.md` before connector search, evidence retrieval, or drafting.
- The state directory is marketplace-namespaced to avoid collisions with other `sales` plugins.

## Validation

Use the read-only helper script as the normal state preflight path:

```bash
python3 plugins/sales/skills/user-context/scripts/sales_preflight.py --workflow prepare-for-meeting
```

`skills/user-context/scripts/sales_preflight.py` is read-only and returns the Sales state context, file provenance, static source-category definitions and relevant helper skills from `skills/user-context/plugin-author-config/source-category-config.json`, default automation definitions from `skills/user-context/plugin-author-config/automation-config.md`, workflow-time source behavior from `skills/user-context/references/source-category-runtime.md`, onboarding status, and any final response guidance that must be considered after the main workflow answer. First-run state creation remains automated through `plugins/sales/skills/user-context/scripts/init_user_context_state.py`, which copies the bundled user-context and onboarding-state templates and seeds onboarding automation state from `automation-config.md`. After that initialization, user-context writes should be direct batched edits to `user-context.md` plus a single operational JSON update when needed; do not use a per-entry write helper for ordinary memory saves or approved discovery entries.

Run this after editing Sales skill instructions:

```bash
python3 plugins/sales/skills/user-context/scripts/validate_user_context_preflight.py
python3 -m unittest discover -s plugins/sales/skills/user-context/tests -p "test_*.py"
```

The preflight check fails when any skill lacks the mandatory user-context pre-answer gate, falls back to the softer "Invoke `user-context` in preflight mode" wording, or the user-context preflight script and tests are missing from the workflow contract.
