# Data Analytics User Context Config

Plugin authors edit this file when clarifying the minimal Data Analytics `user-context.md` scaffold. Keep onboarding mechanics in `../references/onboarding.md`, source-routing behavior in `../references/source-category-runtime.md`, and placeholder insertion in `../scripts/init_user_context_state.py`.

This file is intentionally narrow. `user-context.md` stores only durable Data Analytics source-routing choices explicitly selected for future use plus semantic-layer registry entries. Do not add general memory, output preferences, action-orientation preferences, connector readiness, onboarding state, automation setup details, copied source inventories, or arbitrary saved links here.

## User Context Shape

The initializer copies the content below `## Default User Context` into the user-facing file. Keep source category ids aligned with `source-category-config.json`. Each source category keeps blank `Prefer` and `Avoid` rows until the user explicitly selects a future routing default or a future source to avoid.

## Default User Context

# Data Analytics Source Routing Preferences

Store durable Data Analytics source-routing choices explicitly selected for future use.

## structured_data

- Prefer:
- Avoid:

## team_communication

- Prefer:
- Avoid:

## company_docs

- Prefer:
- Avoid:

## dashboards_bi

- Prefer:
- Avoid:

## behavior_signals

- Prefer:
- Avoid:

## notebook_lab

- Prefer:
- Avoid:

## email_context

- Prefer:
- Avoid:

## calendar_context

- Prefer:
- Avoid:

## code_repository

- Prefer:
- Avoid:

# Semantic Layers

Store durable semantic-layer registry entries that future Data Analytics runs should load before choosing metrics, tables, joins, or definitions.

status: not provided
