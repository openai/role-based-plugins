# Semantic Layer Setup

Use this reference when onboarding, direct setup, or maintenance work needs to create, refresh, inspect, or repair a Data Analytics semantic layer for a product or business area.

A semantic layer is a source-backed local skill that helps future Data Analytics runs answer data questions with the right metrics, tables, joins, grains, dimensions, caveats, and query patterns. The output is an agent-facing Codex skill, not a warehouse migration, semantic modeling project, or BI rebuild.

## Required References

- Read `source-intake.md` before asking the user for inputs or deciding which sources are enough.
- Read `connector-playbook.md` before crawling links, dashboards, team communication channels, data warehouse sources, code repositories, docs, or local skills.
- Read `skill-template.md` before drafting or creating the target semantic-layer skill.
- Read `weekly-polling-automation.md` before offering, creating, or updating recurring source polling.

## Setup Contract

- Identify or infer one coherent product, business, metric, source, or reporting area from the user's provided context or sources. Also identify intended users, destination, and whether the user wants intake-only planning, evidence crawling, a draft skill, direct local skill creation, refresh, inspection, or repair.
- Default direct local creations to `$CODEX_HOME/skills/<area>-semantic-layer` unless the user chose another destination. Ask before placing a generated semantic-layer skill inside a plugin.
- Create one target semantic-layer skill per coherent area by default. Keep unrelated areas separate unless the user explicitly wants one cross-product layer.
- Do not require the user to name the area up front. Require user-provided or user-approved useful context or at least one starting source before a source-backed crawl. If the user has only broad intent and no source or context, ask for one item from `source-intake.md`; if they want a skeleton only, label it as ungrounded.
- Build a source inventory before crawling. For direct creation or draft-file work, write it to `references/source-inventory.md`; for intake-only work, return it in chat. Before saving, summarize sources checked, missing high-value source lanes, and rejected or lower-confidence candidates.
- Resolve connectors lazily when the active source lane needs them. Prefer the most specific installed first-party connector or source tool; when unavailable, ask for the smallest useful export, pasted excerpt, local checkout, SQL text, schema description, screenshot, or alternate source. If the user selected a source during onboarding but the current semantic-layer lane has not read it yet, use the configured route from `../source-category-runtime.md` and attempt the actual read only when that lane needs the source.
- Do not create or refresh a semantic-layer skill from ambient connector availability, saved user context, or guessed app results alone. The user must provide or approve the inputs, or explicitly choose to skip or defer setup.
- Keep raw sensitive data, credentials, secrets, row-level customer examples, and long private messages out of generated files.

## Evidence And Synthesis

Cover the available evidence lanes: tables and namespaces, verified dashboards, raw SQL, team communication, data documentation, code repositories, and existing local skills.

Infer expected source lanes from the user's target metric, grain, domain, and supplied starting points. For example, a daily revenue semantic layer should look for daily-grain warehouse evidence, revenue metric docs or dashboards, and revenue-specific team communication before accepting weekly subscription or generic analytics sources as sufficient. If the best reachable sources are nearby but not exact, label the layer `Limited` or `Directional`, record the mismatch, and ask for the smallest source that would close the gap when the mismatch changes future answers.

Use this source precedence unless the user provides a stronger local rule:

1. Transformation code, tests, and authoritative data documentation, including maintained docs, metric dictionaries, source-backed semantic-layer skills, and user-trusted canonical data skills.
2. Verified dashboards and reviewed SQL.
3. Table metadata, lineage, schema comments, and owners.
4. Query history as observed usage evidence.
5. Team communication announcements or discussion, weighted by recency, authoritativeness, and durable links.
6. Other existing local skills, treated as helpful context until corroborated.

A user can promote a local data skill by naming it as canonical or trusted for the current domain; treat that as authoritative data documentation when it has clear scope and explicit metric, table, grain, or exclusion rules. Still verify high-stakes, stale, time-sensitive, or conflicting claims against the underlying cited source or connected app when possible.

Flag unresolved conflicts instead of smoothing them over. The generated skill should say which metric or table definition is canonical, which is deprecated or dashboard-specific, and what future agents should verify before high-stakes answers.

## Create Or Refresh The Target Skill

- Name the target skill after the area and job, usually `<area>-semantic-layer` or `<area>-data-semantics`.
- Keep the generated `SKILL.md` focused on how future agents should answer data questions, where to find canonical context, and when to verify. Put detailed metrics, tables, query patterns, gotchas, and evidence into directly linked references.
- Make the layer discoverable by recording the durable pointer in `$CODEX_HOME/state/plugins/data-analytics/user-context.md` under `# Semantic Layers`: area, skill name, absolute path, source inventory path, last updated date, and future-use guidance.
- Record operational setup or refresh status in `$CODEX_HOME/state/plugins/data-analytics/onboarding-state.json`.
- Validate generated standalone skills with the relevant authoring validator when files are created locally. Do not claim the skill is invokable until the runtime can see the top-level skill; Codex reload may be required.

## Output Contract

- Intake-only: return source inventory, missing high-value inputs, connector readiness, and crawl plan.
- Crawl-and-synthesis: return semantic-layer summary, source coverage, unresolved conflicts, confidence notes, and target skill structure.
- Direct create or refresh: return created or updated file paths, durable pointer written, validation results, source-use checkpoint, connector gaps, activation note when relevant, and the weekly polling resolution.
- Blocked: state the exact missing connector, permission, source, or destination decision and provide the best manual fallback.

## Quality Bar

- Preserve provenance for every important metric, table, query pattern, and caveat.
- Keep generated instructions operational: future agents should know which source to check first and what to do when sources disagree.
- Prefer compact semantic-layer references over copied artifacts.
- Continue with a partial skill when enough source-backed context exists, but label coverage honestly.
- Ask before external writes, dashboard changes, team communication posts, repo changes, connector installs, or recurring automation creation.
