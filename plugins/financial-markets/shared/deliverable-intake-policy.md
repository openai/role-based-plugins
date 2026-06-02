# Adaptive Deliverable Intake Policy

Use this policy before a Public Equity Investing skill acting as the lead owner creates a new standalone reader-facing artifact. It applies to research reports, memos, models, valuation packages, event and catalyst artifacts,
risk/monitoring views, and dashboards. Presentation and support skills consume resolved choices from an owning workflow; they ask only when independently invoked to create a new standalone hero deliverable.

## Presentation-Surface Precedence

Resolve presentation format in this order:

1. Honor an explicit user-requested format.
2. Preserve the format of an existing artifact for edits and direct reviews unless the user requests conversion. When the workflow creates a separate review report, use that workflow's declared natural artifact without converting the source artifact.
3. Use the workflow's obvious natural artifact when the job is inherently artifact-specific:
   - Use an XLSX workbook for models, reusable calculations, schedules, trackers, normalization, and data cleaning.
   - Use a native deck or document for explicit slide, deck, presentation, or document work.
4. Apply a saved reader-facing output preference as the default when multiple reader-facing formats remain reasonable.
5. Otherwise, resolve any new standalone reader-facing output to polished standalone HTML.
6. Use chat-only output only when the user explicitly requests chat, inline, quick, no-file, or a similarly lightweight response.

Do not silently choose chat because the request appears narrow, conversational, or easy to answer inline. HTML is the normal fallback for a completed reader-facing deliverable, not a signal to compress analysis or force a standardized dashboard.

A direct analytical question, a detail-page hero prompt, or the absence of a requested filename is not an explicit lightweight-response request. Do not choose chat-only output because a concise answer seems sufficient or more useful. When a saved HTML preference applies and the workflow's natural artifact is reader-facing HTML, create the HTML artifact.

Once the presentation surface resolves to HTML, treat that as a committed deliverable decision. Create the HTML artifact before responding; do not later reconsider whether the analysis belongs in chat, split the full deliverable between the artifact and chat, or substitute an inline report. Use chat only as a concise cover note linking to the HTML artifact.

## When To Ask

Before source gathering, substantive analysis, building, or rendering,
determine whether output format, analysis depth, audience/use, and material analytical focus are already stated or evident from the request.

- Ask only for materially unresolved choices.
- Do not ask the format question when the user already requests DOCX, HTML,
  PPTX, XLSX, a dashboard, or inline output.
- For a substantive single-company 60/90-day `catalyst-calendar` request,
  treat a polished HTML catalyst calendar as the workflow-resolved format unless the user requests another surface, a quick/no-file answer, or a workbook/tracker. In an interactive run, ask only remaining material choices such as depth, audience/use, or focus; present another format as an opt-out rather than a blocking intake decision.
- For an explicit post-earnings `deep dive`, `full report`, or reusable/source-heavy post-print package, treat a polished standalone HTML post-earnings report as the workflow-resolved format unless the user requests another surface, a quick/no-file answer, or workbook/model-update output. In an interactive run, ask only remaining material choices such as depth, audience/use, or focus.
- For an explicit `pre-earnings preview`, `full preview report`, or reusable/source-heavy pre-print package, treat a polished standalone HTML pre-earnings report as the workflow-resolved format unless the user requests another surface, a quick/no-file answer, or workbook/model output. In an interactive run, ask only remaining material choices such as depth, audience/use, or focus.
- For an explicit `full event analysis`, `full event report`, or reusable/source-heavy special-situations package, treat a polished standalone HTML event report as the workflow-resolved format unless the user requests another surface, a quick/no-file answer, or model/math output. In an interactive run, ask only remaining material choices such as depth, audience/use, or focus.
- For a substantive `idea-generation` screen, market map, watchlist review, or reusable/source-heavy candidate set, treat a polished standalone HTML idea-triage report as the workflow-resolved format unless the user requests another surface, a quick/no-file answer, or workbook/tracker output. In an interactive run, ask only remaining material choices such as depth, audience/use, or focus.
- For an explicit `investment committee memo`, substantive buy-side `investment memo`, or reusable/source-heavy public-equity memo, treat a polished standalone HTML investment committee memo as the workflow-resolved format unless the user requests another surface, a quick/no-file answer, `.docx`, or a standardized dashboard. In an interactive run, ask only remaining material choices such as depth, audience/use, or focus.
- For a substantive reusable `meeting-prep` packet or explicit HTML meeting brief, treat a polished standalone HTML live-meeting brief as the workflow-resolved format unless the user requests another surface, a quick/no-file answer, or a standardized dashboard. In an interactive run, ask only remaining material choices such as depth, audience/use, meeting type, or focus.
- For a substantive reusable `long-short-pitch` package or explicit HTML trade pitch, treat a polished standalone HTML trade-pitch report as the workflow-resolved format unless the user requests another surface, a quick/no-file answer, or a standardized dashboard. In an interactive run, ask only remaining material choices such as depth, audience/use, trade direction, or focus.
- For a substantive reusable `economic-impact-report` package or explicit HTML public-equity shock analysis, treat a polished standalone HTML economic-impact report as the workflow-resolved format unless the user requests another surface, a quick/no-file answer, or a standardized dashboard. In an interactive run, ask only remaining material choices such as depth, audience/use, or focus.
- For a substantive reusable `scenario-sensitivity-generator` package, explicit HTML scenario report, or sourced discrete-event success/delay/break overlay, treat a polished standalone HTML scenario report as the workflow-resolved format unless the user requests another surface, a quick/no-file answer, workbook/model output, or a standardized dashboard. In an interactive run, ask only remaining material choices such as depth, audience/use, or focus.
- For a substantive standalone `model-audit-tieout` review of an existing model or explicit HTML model-audit request, treat a polished standalone HTML model-audit report as the workflow-resolved format unless the user requests another surface, a quick/no-file answer, remediation output, or a standardized dashboard. In an interactive run, ask only remaining material choices such as depth, audience/use, materiality, or focus.
- For a substantive standalone `deck-report-qc` review of an existing deck or report with supporting materials, treat a polished standalone HTML senior-review QC report as the workflow-resolved format unless the user requests another surface, a quick/no-file answer, or a standardized dashboard. In an interactive run, ask only remaining material choices such as depth, circulation stage, audience/use, or review focus. An embedded QC check inherits the owning workflow's resolved surface and does not create a new HTML report by default.
- For an explicit `initiating coverage` report, substantive `long_only_initiation`, or reusable/source-heavy coverage launch, treat a polished standalone HTML initiation report as the workflow-resolved format unless the user requests another surface, a quick/no-file answer, a model/workbook-first deliverable, or a standardized dashboard. In an interactive run, ask only remaining material choices such as depth, audience/use, or focus.
- For a substantive `integrated_risk_plan`, reusable position-and-hedge package, or explicit HTML risk-plan request, treat a polished standalone HTML risk decision report as the workflow-resolved format unless the user requests another surface, a quick/no-file answer, workbook output, or a standardized dashboard. In an interactive run, ask only remaining material choices such as loss-budget interpretation, depth, audience/use, or focus.
- A format-only request resolves only the delivery surface. For example,
  "make a doc" can select a Word document, but does not resolve depth,
  audience/use, or analytical focus. Do not silently infer those choices.
- When editing or reviewing an existing deck, workbook, or document, preserve the existing format unless the user asks for conversion. Ask only missing depth, audience/use, or focus questions that change the work.
- Apply a saved reader-facing output preference as the default when multiple reader-facing formats are reasonable. A saved HTML preference resolves the presentation surface to HTML in those cases; do not silently choose chat or ask a format question. Do not let a saved HTML preference override an obvious workbook, deck, document, or existing-artifact workflow. Models, model updates, trackers, workbook audits, workbook-first calculations, deck requests, document requests, and edits to an existing artifact keep their natural format unless the user explicitly asks for conversion.
- Reuse choices already confirmed in the current conversation or workflow.
  Downstream modeling, QC, and dashboard rendering do not ask again unless a new hero artifact creates a consequential unresolved choice.
- Keep preferences in conversational context only; do not add fields to dashboard payloads, workbooks, manifests, run logs, or schemas.

## Native Prompt Contract

If a material choice remains unresolved and `request_user_input` is callable in an interactive Codex runtime, call `request_user_input` before creating the hero artifact:

- Include only unresolved decisions and no more than three questions.
- Supply two or three meaningful options for each question.
- The UI provides a free-form `Other` response automatically; never include an `Other` option in the options list.
- Filter format choices to surfaces that are available in the active runtime.
  If a requested format is infeasible, ask for a feasible alternative.

If `request_user_input` is unavailable or errors in an interactive run, the missing material choices still require intake: ask one concise plain-text scoping question in normal chat and wait, covering only the unresolved preferences. Do not present a choice menu when the runtime disallows it, and do not silently select depth or audience. In a non-interactive run, do not attempt an intake exchange: apply the owning workflow's documented recommended defaults and disclose the assumed format and depth in the delivery message or accompanying chat summary, not as visible artifact metadata.
For a substantive 60/90-day catalyst calendar, those recommended defaults are a polished standalone HTML artifact and `Full working analysis`.
For an explicit full or reusable/source-heavy post-earnings deep dive, those recommended defaults are a polished standalone HTML post-earnings report and `Full working analysis`.
For an explicit full or reusable/source-heavy pre-earnings preview, those recommended defaults are a polished standalone HTML pre-earnings report and `Full working analysis`.
For an explicit full or reusable/source-heavy event-driven analysis, those recommended defaults are a polished standalone HTML event report and `Full working analysis`.
For a substantive idea-generation screen, market map, watchlist review, or reusable/source-heavy candidate set, those recommended defaults are a polished standalone HTML idea-triage report and `Full working analysis`.
For an explicit investment committee memo, substantive buy-side investment memo, or reusable/source-heavy public-equity memo, those recommended defaults are a polished standalone HTML investment committee memo and `Full working analysis`.
For a substantive reusable meeting-prep packet or explicit HTML meeting brief, those recommended defaults are a polished standalone HTML live-meeting brief and `Full working analysis`.
For a substantive reusable long/short pitch package or explicit HTML trade pitch, those recommended defaults are a polished standalone HTML trade-pitch report and `Full working analysis`.
For a substantive reusable economic-impact-report package or explicit HTML public-equity shock analysis, those recommended defaults are a polished standalone HTML economic-impact report and `Full working analysis`.
For a substantive reusable scenario-sensitivity-generator package, explicit HTML scenario report, or sourced discrete-event success/delay/break overlay, those recommended defaults are a polished standalone HTML scenario report and `Full working analysis`.
For a substantive standalone model-audit-tieout review of an existing model or explicit HTML model-audit request, those recommended defaults are a polished standalone HTML model-audit report and `Full working analysis`.
For a substantive standalone deck/report QC review with supporting materials, those recommended defaults are a polished standalone HTML senior-review QC report and `Full working analysis`.
For an explicit initiating coverage report, substantive long-only initiation, or reusable/source-heavy coverage launch, those recommended defaults are a polished standalone HTML initiation report and `Full working analysis`.
For a substantive integrated risk plan, reusable position-and-hedge package, or explicit HTML risk-plan request, those recommended defaults are a polished standalone HTML risk decision report and `Full working analysis`.

When using the interactive chat fallback in the Codex composer, append this sentence after the blocking question: "For clickable intake options,
switch to Plan mode with `Shift + Tab` in the Codex composer and resend your request; otherwise answer here and I will continue." This is guidance, not a requirement: do not require a mode change or use this hint instead of asking the unresolved scoping question.

## Format Choices

| Artifact lane | Options |
| --- | --- |
| Memo, narrative report, or briefing | `HTML report (Recommended)`, `Word document (.docx)`, `Inline response` |
| Deck or presentation | `PowerPoint deck (.pptx) (Recommended)`, `HTML storyboard`, `Inline outline` |
| Model, schedule, tracker, or tabular package | `Excel workbook (.xlsx) (Recommended)`, `HTML summary`, `Inline summary` |
| Dashboard or monitoring view | `HTML dashboard (Recommended)`, `Excel tracker`, `Inline brief` |

A selected presentation surface does not eliminate required model, evidence,
or QA companions. For example, a valuation model may retain an XLSX workbook even if the requested first-read presentation is HTML.

For a substantive single-company 60/90-day `catalyst-calendar`, the default presentation surface is a polished HTML catalyst calendar rather than an `HTML dashboard`. Do not ask the user to select a format unless they request an alternate output or the requested job no longer fits that calendar default.

For an explicit post-earnings `deep dive`, `full report`, or reusable/source-heavy post-print package, the default presentation surface is a polished standalone HTML post-earnings report rather than a standardized `HTML dashboard`. Do not ask the user to select a format unless they request an alternate output or the requested job no longer fits that deep-dive default.

For an explicit `pre-earnings preview`, `full preview report`, or reusable/source-heavy pre-print package, the default presentation surface is a polished standalone HTML pre-earnings report rather than a standardized `HTML dashboard`. Do not ask the user to select a format unless they request an alternate output or the requested job no longer fits that preview-report default.

For an explicit `full event analysis`, `full event report`, or reusable/source-heavy special-situations package, the default presentation surface is a polished standalone HTML event report rather than a standardized `HTML dashboard`. Do not ask the user to select a format unless they request an alternate output or the requested job no longer fits that event-report default.

For a substantive `idea-generation` screen, market map, watchlist review, or reusable/source-heavy candidate set, the default presentation surface is a polished standalone HTML idea-triage report rather than a standardized `HTML dashboard`. Do not ask the user to select a format unless they request an alternate output or the requested job no longer fits that idea-triage default.

For an explicit `investment committee memo`, substantive buy-side `investment memo`, or reusable/source-heavy public-equity memo, the default presentation surface is a polished standalone HTML investment committee memo rather than a standardized `HTML dashboard`. Do not ask the user to select a format unless they request an alternate output or explicitly request a standardized dashboard.

For a substantive reusable `meeting-prep` packet or explicit HTML meeting brief, the default presentation surface is a polished standalone HTML live-meeting brief rather than a standardized `HTML dashboard`. Do not ask the user to select a format unless they request an alternate output or explicitly request a standardized dashboard.

For a substantive reusable `long-short-pitch` package or explicit HTML trade pitch, the default presentation surface is a polished standalone HTML trade-pitch report rather than a standardized `HTML dashboard`. Do not ask the user to select a format unless they request an alternate output or explicitly request a standardized dashboard.

For a substantive reusable `economic-impact-report` package or explicit HTML public-equity shock analysis, the default presentation surface is a polished standalone HTML economic-impact report rather than a standardized `HTML dashboard`. Do not ask the user to select a format unless they request an alternate output or explicitly request a standardized dashboard.

For a substantive reusable `scenario-sensitivity-generator` package, explicit HTML scenario report, or sourced discrete-event success/delay/break overlay, the default presentation surface is a polished standalone HTML scenario report rather than a standardized `HTML dashboard`. Do not ask the user to select a format unless they request an alternate output, workbook/model output, or explicitly request a standardized dashboard.

For a substantive standalone `model-audit-tieout` review of an existing model or explicit HTML model-audit request, the default presentation surface is a polished standalone HTML model-audit report rather than a standardized `HTML dashboard`. Do not ask the user to select a format unless they request an alternate output, remediation output, or explicitly request a standardized dashboard.

For a substantive standalone `deck-report-qc` review of an existing deck or report with supporting materials, the default presentation surface is a polished standalone HTML senior-review QC report rather than a standardized `HTML dashboard`. Do not ask the user to select a format unless they request an alternate output or explicitly request a standardized dashboard.

For an explicit `initiating coverage` report, substantive `long_only_initiation`, or reusable/source-heavy coverage launch, the default presentation surface is a polished standalone HTML initiation report rather than a standardized `HTML dashboard`. Do not ask the user to select a format unless they request an alternate output, a model/workbook-first deliverable, or explicitly request a standardized dashboard.

For a substantive `integrated_risk_plan`, reusable position-and-hedge package, or explicit HTML risk-plan request, the default presentation surface is a polished standalone HTML risk decision report rather than a standardized `HTML dashboard`. Do not ask the user to select a format unless they request an alternate output, workbook output, or explicitly request a standardized dashboard.

## Depth And Framing

If depth is unresolved, offer:

- `Focused first pass`: top drivers, risks, targeted analysis, and next questions.
- `Full working analysis (Recommended)`: the normal complete working artifact.
- `Deep diligence package`: expanded scenarios, supporting tables, evidence requests, and appendices.

Depth is not readiness. Deep analysis does not permit PM-ready, client-ready,
committee-ready, publication-ready, or decision-grade language without the source and review gates required by the owning skill.

Use the third question slot for audience/use when it could change tone,
decision framing, disclosure, or delivery:

- `PM or investment team`
- `Client or research audience`
- `Internal committee`

If audience is known or immaterial and the requested work remains broad, ask for focus instead:

- `Thesis / catalysts`
- `Valuation / estimates`
- `Risk / monitoring`

## Expected Behavior

- A new model or valuation-package request with no stated surface asks for format, depth, and any consequential audience/use preference before building, recommending `Excel workbook (.xlsx)`.
- An explicit HTML research report request skips the format question.
- "Make a doc about why Duolingo's stock has plummeted since last May"
  resolves Word format only and still asks for unresolved depth and audience before research begins.
- A review of an existing workbook preserves `.xlsx` as its selected surface.
- An analysis owner that has already collected preferences passes them through to model, QC, and `dashboard-builder` steps without repeated prompts.
- A substantive single-company 60/90-day catalyst-calendar request with no selected format or depth defaults to a polished HTML catalyst calendar; in an interactive run it asks for unresolved depth without blocking on format,
  and in a non-interactive run it proceeds with full working analysis and states those assumptions in the delivery message rather than in the investor-facing artifact.
- An explicit post-earnings deep dive or reusable/source-heavy post-print package with no selected format defaults to a polished standalone HTML post-earnings report; in an interactive run it asks only for unresolved depth, audience/use, or focus, and in a non-interactive run it proceeds with full working analysis while disclosing those assumptions outside the artifact.
- An explicit pre-earnings preview or reusable/source-heavy pre-print package with no selected format defaults to a polished standalone HTML pre-earnings report; in an interactive run it asks only for unresolved depth,
  audience/use, or focus, and in a non-interactive run it proceeds with full working analysis while disclosing those assumptions outside the artifact.
- An explicit full event analysis or reusable/source-heavy special-situations package with no selected format defaults to a polished standalone HTML event report; in an interactive run it asks only for unresolved depth,
  audience/use, or focus, and in a non-interactive run it proceeds with full working analysis while disclosing those assumptions outside the artifact.
- A substantive idea-generation screen, market map, watchlist review, or reusable/source-heavy candidate set with no selected format defaults to a polished standalone HTML idea-triage report; in an interactive run it asks only for unresolved depth, audience/use, or focus, and in a non-interactive run it proceeds with full working analysis while disclosing those assumptions outside the artifact.
- An explicit investment committee memo, substantive buy-side investment memo, or reusable/source-heavy public-equity memo with no selected format defaults to a polished standalone HTML investment committee memo; in an interactive run it asks only for unresolved depth, audience/use, or focus, and in a non-interactive run it proceeds with full working analysis while disclosing those assumptions outside the artifact.
- A substantive reusable meeting-prep packet or explicit HTML meeting brief defaults to a polished standalone HTML live-meeting brief; in an interactive run it asks only for unresolved depth, audience/use, meeting type, or focus, and in a non-interactive run it proceeds with full working analysis while disclosing those assumptions outside the artifact.
- A substantive reusable long/short pitch package or explicit HTML trade pitch defaults to a polished standalone HTML trade-pitch report; in an interactive run it asks only for unresolved depth, audience/use, trade direction, or focus, and in a non-interactive run it proceeds with full working analysis while disclosing those assumptions outside the artifact.
- A substantive reusable economic-impact-report package or explicit HTML public-equity shock analysis defaults to a polished standalone HTML economic-impact report; in an interactive run it asks only for unresolved depth, audience/use, or focus, and in a non-interactive run it proceeds with full working analysis while disclosing those assumptions outside the artifact.
- A substantive standalone model-audit-tieout review of an existing model or explicit HTML model-audit request defaults to a polished standalone HTML model-audit report; in an interactive run it asks only for unresolved depth, audience/use, materiality, or focus, and in a non-interactive run it proceeds with full working analysis while disclosing those assumptions outside the artifact.
- A substantive standalone deck/report QC review with supporting materials and no selected format defaults to a polished standalone HTML senior-review QC report; in an interactive run it asks only for unresolved depth, circulation stage, audience/use, or review focus, and in a non-interactive run it proceeds with full working analysis while disclosing those assumptions outside the artifact.
- An explicit initiating coverage report, substantive long-only initiation, or reusable/source-heavy coverage launch with no selected format defaults to a polished standalone HTML initiation report; in an interactive run it asks only for unresolved depth, audience/use, or focus, and in a non-interactive run it proceeds with full working analysis while disclosing those assumptions outside the artifact.
- A substantive integrated risk plan, reusable position-and-hedge package, or explicit HTML risk-plan request with no selected format defaults to a polished standalone HTML risk decision report; in an interactive run it asks only for unresolved loss-budget interpretation, depth, audience/use, or focus, and in a non-interactive run it proceeds with full working analysis while disclosing assumptions outside the artifact.
