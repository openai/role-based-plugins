---
name: public-equity-investing
description: Route Public Equity Investing only when explicitly named or tagged, or for an unmistakable listed-equity investor workflow tied to a public security, such as earnings investment work, a long/short thesis, public-equity valuation or model update, catalysts, or position sizing. Do not use for generic company research, reports, documents, models, valuation, or share-price questions.
---

# Public Equity Investing Router

## Bundled Path Resolution

Derive the plugin root once from the actual filesystem location of this `SKILL.md`: it is two parent directories above this router directory. Set the shell working directory to that plugin root before the first bundled read or command, and resolve every router-owned bundled path from that root. Use only plugin-root-relative paths such as `shared/...`, `skills/...`, and `skills/public-equity-investing/internal-support/...`. Do not apply `../..` to an already resolved plugin root, resolve paths from the broader marketplace or cache root, or probe alternate relative paths.

## Invocation Gate

Read `shared/invocation-policy.md` before choosing any specialist. If the prompt is neither an explicit Public Equity Investing invocation nor a perfect-fit listed-equity investor mandate, do not route into this plugin.

## User Context Preflight

After the invocation gate passes and before substantive Public Equity Investing work, run `python3 skills/user-context/scripts/user_context_preflight.py` with the shell working directory set to this plugin's root. Set the working directory before the first attempt; do not probe alternate relative paths.

Use the returned envelope as a soft read-only preflight. Pass relevant entries from `saved_context` to the selected lead skill as handoff context. The router must not interpret saved output preferences, resolve or announce a presentation surface, or decide whether the requested work belongs in chat. Missing, malformed, unreadable, or uninitialized state must never block the requested workflow. Do not initialize, overwrite, repair, or reset state during ordinary workflow preflight. Do not inspect connectors or source readiness.

When an ordinary workflow returns `next_action.id = "offer_orientation"`, complete the requested work and then append one short optional setup offer: `I can also save a couple of Public Equity Investing defaults, connect source tools, offer one optional automation, and help you pick a starter workflow. Want to do that now?`

Do not append the offer for direct saved-context setup or status requests. Do not append it when `next_action` is `null`, including after onboarding is completed, deferred, or quiet. Leave other onboarding steps to the explicit `user-context` flow.

Route explicit onboarding, setup, orientation, or get-started requests, including a detail-page starter such as `Help me get started`, plus explicit remember, save, update, forget, inspect, export, reset, source-setup, or automation-setup requests for Public Equity Investing context to `skills/user-context/SKILL.md` as the primary workflow.

## Workflow Routing

After the gate passes, select one owning research, model, event, or risk skill from the user's intent and the focused skill descriptions. The router owns admission and lead-skill selection only. After selecting the owner, load `skills/<lead-skill>/SKILL.md` from the plugin root before source gathering, analysis, connector use, deliverable intake, or any user-facing announcement about execution or packaging. The router must not continue substantive work as a substitute for the selected owner. Pass the request, routing rationale, and relevant saved context to the loaded owner without choosing or announcing format, depth, artifact architecture, or whether the request is lightweight. The selected owner applies `shared/final-deliverable-framework.md` as needed and, for a new standalone reader-facing hero artifact, reads `shared/deliverable-intake-policy.md` before source gathering or analysis to resolve any presentation decision. Support and presentation skills inherit resolved choices and do not re-prompt.

## Internal Support

Read `skills/public-equity-investing/internal-support/policy.md` when the selected workflow needs evidence control, generic data cleaning, rendering, style application, sector context, or provider-specific call shaping after selecting a callable connector route. Those supporting capabilities are bundled internal playbooks rather than selectable skills. Keep standalone normalization and model-audit requests with the visible `financials-normalizer` and `model-audit-tieout` workflows. For an explicitly requested internal support-only task admitted to this plugin, this router coordinates the task through the matching internal playbook.
