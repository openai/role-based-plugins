---
name: public-equity-investing
description: Route Public Equity Investing only when explicitly named or tagged, or for an unmistakable listed-equity investor workflow tied to a public security, such as earnings investment work, a long/short thesis, public-equity valuation or model update, catalysts, or position sizing. Do not use for generic company research, reports, documents, models, valuation, or share-price questions.
---

# Public Equity Investing Router

## Invocation Gate

Read `../../shared/invocation-policy.md` before choosing any specialist. If the prompt is neither an explicit Public Equity Investing invocation nor a perfect-fit listed-equity investor mandate, do not route into this plugin.

## User Context Preflight

After the invocation gate passes and before substantive Public Equity Investing work, run `python3 skills/user-context/scripts/user_context_preflight.py` with the shell working directory set to this plugin's root. Set the working directory before the first attempt; do not probe alternate relative paths.

Use the returned envelope as a soft read-only preflight. Apply relevant entries from `saved_context` to the routed work. Missing, malformed, unreadable, or uninitialized state must never block the requested workflow. Do not initialize, overwrite, repair, or reset state during ordinary workflow preflight. Do not inspect connectors or source readiness.

When an ordinary workflow returns `next_action.id = "offer_orientation"`, complete the requested work and then append one short optional setup offer: `I can also set up saved Public Equity Investing preferences and source pointers for future work. Want to do that now?`

Do not append the offer for direct saved-context setup or status requests. Do not append it when `next_action` is `null`, including after onboarding is completed, deferred, or quiet. Leave other onboarding steps to the explicit `user-context` flow.

Route explicit remember, save, update, forget, inspect, export, reset, source-setup, or automation-setup requests for Public Equity Investing context to `skills/user-context/SKILL.md` from the plugin root as the primary workflow.

## Workflow Routing

After the gate passes, use `../../shared/final-deliverable-framework.md` to assign the owning research, model, event, or risk skill. For a new substantive hero artifact, that owner reads `../../shared/deliverable-intake-policy.md` before source gathering or analysis; support and presentation skills inherit resolved choices and do not re-prompt.

## Internal Support

Read `internal-support/policy.md` when the selected workflow needs evidence control, generic data cleaning, rendering, style application, sector context, or provider-specific call shaping after selecting a callable connector route. Those supporting capabilities are bundled internal playbooks rather than selectable skills. Keep standalone normalization and model-audit requests with the visible `financials-normalizer` and `model-audit-tieout` workflows. For an explicitly requested internal support-only task admitted to this plugin, this router coordinates the task through the matching internal playbook.
