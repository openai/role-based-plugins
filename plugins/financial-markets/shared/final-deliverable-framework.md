# Final Deliverable Framework

Use this standard for all Public Equity Investing skills. The goal is to give the user a human-readable investment artifact first, while keeping machine-readable files available for audit, reruns, and downstream automation. For user-facing HTML, also follow `shared/html-artifact-standard.md`.

Before selecting this plugin for an untagged request, apply `shared/invocation-policy.md`. Activate Public Equity Investing only when it is explicitly named or tagged, or when the prompt is an unmistakable listed-equity investor workflow.

Before an artifact-owning lead skill begins source gathering or analysis for a new standalone reader-facing artifact, read `shared/deliverable-intake-policy.md` and collect any materially missing choices through its adaptive `request_user_input` preflight, subject to the workflow-resolved catalyst-calendar, explicit full earnings-deep-dive,
explicit pre-earnings-preview, explicit full event-analysis, and substantive idea-generation format defaults documented there. Respect formats already requested, preserve the surface of an existing artifact being reviewed or edited, and have downstream support or presentation skills reuse resolved choices without prompting again.

Use the presentation-surface precedence in `shared/deliverable-intake-policy.md` as the controlling format rule. A new standalone reader-facing output defaults to polished standalone HTML when no explicit format, existing-artifact delivery, obvious workbook, or explicit native deck/document workflow takes precedence.

When HTML is selected or defaulted, create the HTML artifact before responding. Do not reopen the presentation decision after source gathering or analysis, and do not substitute a full inline report for the selected HTML deliverable; use chat as a concise cover note linking to the hero artifact.

The `public-equity-investing` router reads `internal-support/policy.md` before loading bundled internal evidence control,
generic cleaning, rendering, style, or sector-context support. Those support capabilities do not appear as selectable skill entrypoints. `financials-normalizer` and `model-audit-tieout` remain visible when normalization or model review is the user's requested job, and may also support an owning workflow.

## Hero lanes

Choose one hero lane before drafting or running scripts:

| Lane | Use when | Hero artifact |
|---|---|---|
| HTML dashboard or report | Substantial public-equity research, catalyst calendars, earnings previews or deep dives, event-driven work, pipeline or sector diligence, ETF/index constituent diligence, benchmark-relative research, thesis trackers, idea generation, memos, and source-heavy reports. | Polished standalone `.html` tailored to the workflow and following `shared/html-artifact-standard.md`; use internal `dashboard-builder` when a standardized or payload-driven dashboard is selected. |
| XLSX workbook | DCF, three-statement, comps model, model update, tracker, and other workbook-style outputs. Financial normalization and data cleaning use this lane only for explicit standalone normalization/cleanup asks or when the owning workflow needs a workbook handoff. | `.xlsx` with a first visible `Cover` tab that acts as an insight dashboard. |
| Concise chat answer | The user explicitly requests chat, inline, quick, no-file, or a similarly lightweight response. | Chat response with source posture and caveats. |
| Support and audit files | Reproducibility, validation, manifests, logs, deterministic runners, and data interchange. | JSON, CSV, Markdown, logs, and manifests as secondary files only. |

Markdown, raw JSON, CSV, manifests, run logs, and plan files are not the default user-facing deliverable. Use them as intermediate, support, audit, or explicit-request outputs. When a deterministic runner writes a Markdown sidecar by default, name it `support_note.md` or a specific `*_support_note.md`; reserve `report.md` for explicit legacy compatibility flags.

Internal support playbooks follow the router-bundled `skills/public-equity-investing/internal-support/policy.md` and `shared/support-layer-routing-contract.md`: when invoked by an owning workflow, their CSV/XLSX/JSON/Markdown/profiles/ledgers are secondary support unless the user explicitly asked for that support artifact as the deliverable.

## HTML recommendation triggers

Treat a polished HTML artifact as the recommended presentation path when the ask includes:

- 60-day, 90-day, or multi-category catalyst calendars;
- earnings preview, earnings deep dive, post-print diligence, or full report;
- event calendar, regulatory/FDA calendar, clinical pipeline map, or investor-day/macro/company catalyst map;
- substantive idea-generation screen, market map, watchlist review, or reusable/source-heavy candidate set;
- thesis tracker, diligence map, pipeline map, PM cockpit, source-heavy memo, ETF/index or constituent diligence, benchmark-relative exposure review, or multi-tab/table deliverable;
- any request with many dates, many sources, multiple tables, or a need to scan and jump between sections.

For substantive single-company 60/90-day catalyst calendars, resolve the format to a polished HTML catalyst calendar unless the user requests another format, a quick/no-file answer, or a workbook/tracker. In interactive runs,
ask only remaining material choices such as depth; allow another format as a non-blocking opt-out.

For explicit post-earnings deep dives, full reports, or reusable/source-heavy post-print packages, resolve the format to a polished standalone HTML post-earnings report unless the user requests another format, a quick/no-file answer, or workbook/model-update output. In interactive runs, ask only remaining material choices such as depth, audience/use, or focus.

For explicit pre-earnings previews, full preview reports, or reusable/source-heavy pre-print packages, resolve the format to a polished standalone HTML pre-earnings report unless the user requests another format, a quick/no-file answer, or workbook/model output. In interactive runs, ask only remaining material choices such as depth, audience/use, or focus.

For explicit full event analyses, full event reports, or reusable/source-heavy special-situations packages, resolve the format to a polished standalone HTML event report unless the user requests another format, a quick/no-file answer,
or model/math output. In interactive runs, ask only remaining material choices such as depth, audience/use, or focus.

For substantive idea-generation screens, market maps, watchlist reviews, or reusable/source-heavy candidate sets, resolve the format to a polished standalone HTML idea-triage report unless the user requests another format, a quick/no-file answer, or workbook/tracker output. In interactive runs, ask only remaining material choices such as depth, audience/use, or focus.

For other workflows in this list, use `shared/deliverable-intake-policy.md`
before selecting a materially unresolved format or depth in interactive runs.
In non-interactive runs, apply the workflow's documented recommended defaults and disclose the assumed format and depth in the delivery message or accompanying summary rather than as visible hero-artifact metadata.

Stay chat-only only when the user selects or explicitly asks for a quick read,
short answer, summary, no file, no dashboard, or one named event/section as a lightweight response. Do not infer chat-only intent from direct question wording or the absence of a requested file.

## Full-depth default

Full analytical coverage is the recommended depth and the non-interactive fallback. Rendering as HTML is not a reason to compress the substance, and full coverage does not require a fixed section or module inventory. In an interactive run, honor the depth selected during intake. Compress when the user selects or explicitly asks for summary, short, quick, brief, one-pager,
TL;DR, or a single requested section.

## Citation standard

For HTML dashboard/report outputs:

- Material figures, confirmed dates, time-sensitive facts, and consequential factual claims should be visibly traceable to supporting sources near the point of use.
- Keep confirmed facts, inferred timing, assumptions, and PM judgment distinguishable.
- In source-heavy outputs, include a readable source ledger or equivalent audit surface.
- Prefer unobtrusive citation treatment that supports review without dominating the layout.

Source visibility belongs near the number or claim the reader is evaluating, not only in a final references list.

When the standardized `dashboard-builder` path is selected, production dashboard JSON remains a support artifact, but it must still be complete because the rendered HTML depends on it. Those dashboards require `mode`, `layout`, `metadata`, `hero`, `snapshot`, tabs/modules, source ledger, `metadata.citation_policy: "strict"`, `metadata.payload_stage: "production"`, freeze time, source posture, readiness label/posture, and decision context. Draft/support payloads may use warning-mode validation only when they are clearly marked as draft/support and the final human artifact does not imply PM-ready, client-ready, committee-ready, external, or publication-ready status.

## Workbook cover standard

Every generated workbook should open to a first visible `Cover` tab that functions as an insight dashboard. It should include:

- recommendation, net read, or decision question;
- model/workbook status and decision-readiness label;
- key metrics, valuation/model outputs, scenario results, or event pressure;
- source posture, stale/missing evidence, warnings, hard failures, and unsupported assumptions;
- major sensitivities, catalyst/risk flags, or thesis breaks;
- what not to use the workbook for when caveated;
- workbook map as a secondary navigation block.

A table-of-contents cover is not enough. If the first tab does not answer the investment question, `model-audit-tieout` should flag it.

## Final handoff

Final responses should name the hero artifact first, then supporting files, then limitations. Do not lead with JSON, Markdown, CSV, run logs, or manifests unless the user explicitly requested those formats.
