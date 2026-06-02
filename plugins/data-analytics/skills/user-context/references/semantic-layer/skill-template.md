# Semantic Layer Skill Template

Use this reference when drafting the generated semantic-layer skill. The target skill should be small enough to load quickly and should route detailed data knowledge into references.

## Recommended File Shape

```text
<skills-root>/
  <area>-semantic-layer/
    SKILL.md
    references/
      source-inventory.md
      semantic-layer.md
      evidence.md
```

Use more reference files only when the area is large enough to justify them, such as `metrics.md`, `tables.md`, `query-patterns.md`, or `gotchas.md`.

For multiple product or business areas, create one folder per area. Keep shared source links or cross-skill references explicit rather than merging unrelated semantics into one large skill.

## Target SKILL.md Shape

```markdown
---
name: <area>-semantic-layer
description: Use when answering data questions for <area>, including metric definitions, table choice, dimensions, joins, dashboard reconciliation, and common query patterns.
---

# <Area> Semantic Layer

## Purpose

Use this skill to answer <area> data questions with the canonical metrics, tables, grains, joins, caveats, and validation steps captured in `references/semantic-layer.md`.

## Skill Configuration

### Source Order

1. Transformation code and authoritative data docs.
2. Verified dashboards and reviewed SQL.
3. Table metadata, lineage, and owner notes.
4. Query history as observed usage evidence.
5. Team communication context and existing local skills as supporting context.

When sources disagree, state the conflict and verify before giving a high-confidence answer.

### Evidence Standard

Use source-backed facts from the semantic-layer references. Label any answer that depends on stale, inferred, query-history-only, or team-communication-only evidence.

## Workflow

1. Classify the user's question: metric definition, table choice, query drafting, dashboard reconciliation, trend diagnosis, or data-quality concern.
2. Read `references/semantic-layer.md` and any linked metric, table, or query-pattern reference relevant to the question.
3. Use the canonical metric and table guidance first; use observed query patterns only when canonical docs are missing or compatible.
4. For queries, preserve table grain, time zone, date column, filters, joins, and inclusion or exclusion rules.
5. Validate against the source order before finalizing answers that could affect business decisions.

## Output

Return the direct answer first, then the source-backed caveats, tables or metrics used, and validation gaps. Include SQL only when the user asks for a query or when SQL is the clearest answer.
```

## semantic-layer.md Shape

```markdown
# <Area> Semantic Layer

## Scope

- Area:
- Intended users:
- Current source coverage:
- Source inventory: `references/source-inventory.md`
- Last synthesized:

## Core Entities

| Entity | Description | Primary IDs | Important Grain Notes | Sources |
| --- | --- | --- | --- | --- |

## Metrics

| Metric | Definition | Numerator | Denominator | Time Grain | Canonical Source | Caveats |
| --- | --- | --- | --- | --- | --- | --- |

## Dimensions And Filters

| Dimension Or Filter | Meaning | Allowed Values Or Logic | Applies To | Sources |
| --- | --- | --- | --- | --- |

## Tables

| Table | When To Use | Grain | Join Keys | Freshness | Caveats | Sources |
| --- | --- | --- | --- | --- | --- | --- |

## Query Patterns

- Pattern:
  - Use when:
  - Key tables:
  - Required filters:
  - Common joins:
  - Example skeleton:

## Gotchas

- Gotcha:
  - Impact:
  - How to avoid:
  - Source:

## Open Questions

- Question:
  - Why it matters:
  - Best owner or source to check next:
```

## evidence.md Shape

```markdown
# Evidence Register

| Fact Or Claim | Source Type | Source Link Or Path | Retrieved Or Observed | Confidence | Notes |
| --- | --- | --- | --- | --- | --- |
```

## source-inventory.md Shape

Create `references/source-inventory.md` whenever the workflow creates or drafts a target semantic-layer skill package. Intake-only runs may return the same inventory in chat without creating the file.

```markdown
# Source Inventory

| Source | Type | Locator | Connector Or Tool | Permission Status | Last Checked | Automation Eligible | Update Boundary | Notes |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
```

Use `Automation Eligible` to distinguish sources the weekly automation can poll directly from sources that require manual export, one-off permission, or user review. Use `Update Boundary` to say whether the automation may update semantic-layer references automatically, must draft a proposed update, or must only report changes.

## Drafting Rules

- Put durable semantic facts in the generated skill's references, not in chat-only prose.
- Keep `SKILL.md` operational and short; move table catalogs, metric dictionaries, query examples, and evidence into references.
- Keep the source inventory current enough that a weekly polling automation can determine what to check and what update boundary applies.
- Use source links, file paths, dashboard IDs, table names, and repo paths as provenance.
- Label stale, inferred, query-history-only, or team-communication-only facts.
- Preserve unresolved conflicts as explicit open questions.
- Avoid raw sensitive data, credentials, long message quotes, and copied dashboard exports.
