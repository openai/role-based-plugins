# Sales User Context Config

Plugin authors edit this file when adding, removing, renaming, or clarifying the starter categories Sales should copy into a user's `user-context.md`. Keep save/update policy in `../references/plugin-memory.md`, onboarding mechanics in `../references/onboarding.md`, and placeholder insertion in `../scripts/init_user_context_state.py`.

These categories describe the links, docs, channels, examples, or user-provided information that make future Sales workflows more grounded. Keep each description to one or two sentences that say what the category is or does and when Codex should use it; that gives future Sales runs enough context to apply the saved user context without carrying a separate use-when field. The initializer adds `## Saved Links And Context` with `status: not provided` under every category when it creates the user-facing file. Do not include that saved-context heading, placeholder status, connector setup state, onboarding state, or automation setup details in this config.

## Category Entry Shape

Every category entry must use this shape:

```md
# Category Name

- Description: What this category is or does and when future Sales runs should apply it.
```

The entries below are the plugin-author customization surface. Keep each category as an H1 (`# Category Name`) because the initializer copies these headings into the user-facing scaffold.

## Default Categories

# CRM Update Rules And Write Safety

- Description: Rules for interpreting or changing CRM fields such as stage, forecast category, close date, next steps, approval paths, and review boundaries. Use this when drafting CRM-ready notes, interpreting deal health, or deciding whether a CRM write needs review.

# Book Of Business Source

- Description: Sources that explain the user's real customer book, including territory logic, named-account exceptions, account assignments, pod coverage, overlay responsibilities, and ownership refresh paths. Use this when scoping account research, filtering pipeline, or checking which ownership context applies.

# Customer And Account Source Docs

- Description: Trusted account-specific sources such as account plans, mutual action plans, exec briefs, QBRs, implementation plans, security or procurement notes, support summaries, and customer research folders. Use this when preparing customer work, answering account-status questions, or choosing the account team's source of truth.

# Account Rooms And Escalation Channels

- Description: Important rooms or channels and their norms for account collaboration, escalations, posting, tagging, review, and customer-visible boundaries. Use this when finding account history, drafting internal updates, or deciding where and how to ask for help.

# Deal Governance And Approval Trackers

- Description: Approval and governance sources for pricing, discounting, legal, procurement, security, implementation, executive sponsorship, launch readiness, or exceptions. Use this when reviewing deal risk, preparing close plans, or drafting asks for approvers.

# Product Positioning And Value Proposition Sources

- Description: Approved product messaging, positioning, SKU or package language, ICP and persona guidance, solution narratives, and product-specific claims to use or avoid. Use this when drafting customer-facing material, preparing meetings, or explaining product fit.

# Company Brand And Customer-Facing Asset Sources

- Description: Approved brand guidance, templates, asset libraries, examples, screenshots, diagrams, logos, and visual or tone rules for sales deliverables. Use this when creating or reviewing decks, one-pagers, exec briefs, QBRs, event collateral, or other customer-facing assets.

# Build Competitive Brief Sources

- Description: Approved competitive intelligence such as competitor lists, battlecards, win/loss notes, objection handling, displacement narratives, differentiation claims, and competitive do/don't language. Use this when preparing deal strategy, vendor comparisons, customer responses, or competitive risk notes.

# Sales Targets And Planning Sources

- Description: Quota context, targets, segment goals, GTM priorities, campaign focus areas, territory plans, leadership planning docs, and planning trackers that explain current sales focus. Use this when prioritizing accounts, reviewing forecast, selecting outbound motions, or preparing leadership updates.
