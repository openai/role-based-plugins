---
name: spreadsheets
description: "Use this skill when a user requests to create, modify, analyze, visualize, or work with spreadsheet files (`.xlsx`, `.xls`, `.csv`, `.tsv`) or Google Sheets-targeted spreadsheet artifacts with formulas, formatting, charts, tables, and recalculation."
---

# Spreadsheets skill

This skill includes requirements and guidance for producing a correct, polished spreadsheet artifact quickly that completes the user's request. When producing spreadsheets, workbooks, or Google Sheets-targeted outputs, you will be judged on layout, readability, style, analytical workbook conventions, and correctness. Follow the requirements below for how to use the APIs effectively and how to verify your output before finalizing work for the user.

For analytical tasks, you are especially judged on correctness and quality. This skill improves spreadsheet construction and formatting; it does not own the analysis logic, source selection, market assumptions, or business conclusion when another workflow skill is the primary route. For analysis prompts, aim for an output that can compete with a strong analyst-built workbook, not just a functional grid. A good default shape is an executive summary or dashboard first, then assumptions/sources, then model/detail sheets. For simpler tasks like creating a template or tracker, prioritize doing the spreadsheet build and edits quickly, while ensuring the user's request is fulfilled.

For additional stylistic best practices, follow: `style_guidelines.md`

Read `charts.md` when creating or editing substantive charts, dashboards, or chart-ready summaries.

## Skill Configuration

### User Context

Mandatory pre-answer gate: Invoke `data-analytics:user-context` in preflight mode by loading [data-analytics:user-context](../user-context/SKILL.md) and running its preflight script before answering, searching connectors, retrieving evidence, creating artifacts, or drafting output. Do not look for a callable MCP tool named `data-analytics:user-context`. Use the returned `data_analytics_preflight` envelope as the source of truth for saved context, source-category mapping, semantic-layer registry, onboarding/final-response obligations, and conditional guidance; use saved context and semantic layers as source-selection inputs, not as substitutes for workflow-time reads from connected or provided sources. Do not read or reinterpret raw plugin state files unless preflight fails, declares required content omitted, local shell access is unavailable, or the user explicitly asks for raw state inspection.

## Google Sheets-targeted output

### New Creations

For a net-new Google Sheets request, create and verify a local `.xlsx` with this skill first. The native Google Sheets deliverable must then be produced by the Google Drive plugin's spreadsheet import action, `mcp__codex_apps__google_drive_import_spreadsheet`, with `upload_mode: "native_google_sheets"`.

Do not use Computer Use, Browser Use, blank-Google-Sheets creation plus Google Sheets write APIs, or another direct-to-Sheets construction path for net-new Google Sheets unless the user explicitly asks for that alternate workflow. If they do, mention first that output quality is expected to be best when a local `.xlsx` is imported through the Google Drive plugin.

If the Google Drive plugin is unavailable, use the plugin-install/user-elicitation flow to ask the user to install `google-drive@openai-curated`. If the plugin is available but `_import_spreadsheet` is missing, ask the user to reinstall or refresh the Google Drive plugin before continuing with the native Google Sheets deliverable.

After successful native import, the user-facing deliverable is the Google Sheets link. Treat the local `.xlsx` as a build artifact unless the user explicitly asks to keep or receive it.

### Edits

Use the Google Drive plugin's Google Sheets skill for edits to existing Google Sheets. The local `.xlsx` creation and native import workflow above applies only to net-new Google Sheets deliverables.



# Tools + Contract
- Use Codex workspace dependencies for spreadsheet artifact work: resolve them through the workspace dependency loader or runtime skill, then treat the returned Node/Python runtimes, package directory, and verification details as authoritative. Do not use system `node`, system `python`, global npm packages, or repo-local installs.
- Use `@oai/artifact-tool` JS library, which exists in the default Codex workspace dependencies node_modules, for authoring, editing, inspecting, rendering, and exporting spreadsheet `.xlsx` workbooks.
- Run builders from a writable conversation-specific temp or workspace directory, not from the managed dependency directory. Outputs and scratch files may live under the OS temp directory.
- Start by setting up the work directory to work with normal Node module resolution: link or junction local `node_modules` to the workspace dependency node_modules so `import "@oai/artifact-tool"` resolves.
- Prefer one executable `.mjs` builder; patch and rerun it when iterating. Do NOT use shell heredocs or keep extra builder copies.
- If workspace dependencies or `@oai/artifact-tool` are unavailable, report a setup blocker; do not guess paths, install packages, use system deps, alter module resolution, copy/import bundled internals, or do a broad file system search.
- Do not search package internals or dump prototypes to discover APIs. Use the API reference below; if blocked, run at most one exact `workbook.help("<api_or_feature>")` query before building.
- Final response: include a short user-visible summary and standalone Markdown link(s) only to final `.xlsx` artifact(s), one per line: `[Revenue Model - MNST.xlsx](/absolute/path/to/revenue_model_mnst.xlsx)`.
- Do not mention internal tooling or support artifacts such as builders, rendered previews, JSON/CSV/log files, or scratch files unless explicitly requested.
- Do not use alternate workbook creation/editing libraries such as `openpyxl`, `xlsxwriter`, or `pandas.ExcelWriter` unless the user explicitly asks for a non-artifact-tool fallback.
- For analysis outside workbook authoring, use JS or spreadsheet formulas when sufficient. If Python is needed, use bundled Python libraries, save JSON/CSV intermediates, and have the JS builder create the workbook. Keep auditable/user-editable calculations as formulas.
- For nontrivial work, use `update_plan`: build quickly, verify/render, repair meaningful issues, then finalize without long polish loops. Incrementally rendering your work and assessing overall aesthetics, formatting and correctness along the way is very important (rigorously inspect the output and be confident in quality), but do not get stuck in a long render-verify loop. As part of your plan, think about the best practices and conventions to follow for the specific type of spreadsheet you're creating and the best way to structure the workbook for readability and usability.

# Analysis Workbook Shape
When a workflow such as `$market-sizing`, `$metric-diagnostics`, `$kpi-reporting`, or `$product-business-analysis` owns the analysis, use that workflow's structure first and focus this skill on workbook quality. Good analysis workbooks usually include:
- `Summary` or `Dashboard` for top-line answer, key metrics, charts, and interpretation.
- `Assumptions` or `Inputs` for editable drivers, scenarios, date ranges, and user-controlled variables.
- `Model`, `Calculations`, or `Detail` for formula-backed derivations and intermediate tables.
- `Sensitivity` or `Scenarios` when assumptions materially change the conclusion.
- `Sources` for compact citations, source notes, and provenance.
- `Checks` only when correctness depends on linked calculations, source reconciliation, or model integrity.

# General Rules
- Start meaningful edits quickly; avoid long upfront API exploration.
- Use `references/artifact_tool_api.md` when concrete API syntax is needed.
- If these skill instructions are already loaded in context, do not spend a shell turn re-reading this `SKILL.md` from disk. Move directly to the prompt, attachments, and workbook build.
- For workbook with multiple tabs/sheets, create/populate non-formula inputs/tables and sheets prior to populating cross-sheet formulas.

## Approach for quickly building a new spreadsheet
1. Setup: import `@oai/artifact-tool`, create workbook/sheets for new files.
2. Build quickly: bulk-write headers/data/formulas; then formatting/validation/conditional formatting; add charts/tables only when needed.
3. Use additional focused calls if helpful for streamed progress.
4. Near completion: inspect key ranges, scan formula errors, render all the sheets and verify, run a validation pass
5. Export `.xlsx`

## Making edits on a spreadsheet
If a user asks to edit or add to an existing spreadsheet:
- For visual fix requests, start with the smallest plausible local change rather than applying sheet-wide autofit, wrapping, or restyling.
- When making edits, ensure existing formulas and patterns are consistent. For example, if asked to add another column or row to a table and there is conditional formatting applied to the whole table, it should extend to the new column or rows as well.
- If specific cells/rows/columns are specified in prompt, limit edits to those ranges unless a broader change is clearly necessary. The exceptions are when other parts of the spreadsheet depend on them, e.g. if there's a dynamic chart that is based on the range of values in a table and a new row is added, the chart should include that new row. Another example is if conditional formatting was already set for a table from A1:C5, and you add a new column D, the conditional formatting should be updated (or deleted and re-created) to cover A1:D5.
- For column resizing, avoid autofitting by default: instead, inspect only relevant data range, measure the longest text entry in that range, and set columnWidthPx to an estimated width based on text length (with a reasonable min/max cap). Use autofit only when the user explicitly asks for it.

## Handling queries and questions
- The user may ask questions about the sheet instead of requesting an edit or a change. Simply answer those questions about the spreadsheet based on the context available rather than making an edit the user didn't intend for. You can use inspect to learn more or directly read values/formulas/tables etc via accessor methods.

# Error Recovery
On first error:
1. Read error text.
2. Run one targeted `workbook.help("<exact_api>")` query only if needed.
3. Retry with minimal patch (not full rewrite).
4. Continue from existing workbook state.

Do not loop indefinitely on similar failures.

# Quality Guidelines
- Keep layout readable and bounded, contents visible:
  - avoid extreme width/height from unconstrained autofit
  - cap oversized widths/heights after `autofit` + `wrap_text`
- Prefer formula-driven logic over manual painted cells when logic is expected.
- Derived values must be formulas (not hardcoded) and legible.
- Use absolute/relative references correctly for fill/copy behavior.
- Do not use magic numbers in formulas; reference cells (e.g. `=H6*(1+$B$3)`).
- Blank editable templates must look blank/neutral before user data is entered. Count, ranking, best/worst, IRR/RATE/XIRR, variance, and status formulas should guard on required input cells and return `""`, `0`, or a clear "No entries yet" state as appropriate. Alternatively, prefill with a few rows of example data.
- Include at least one visual summary for tracker/planning requests when appropriate (KPI block, chart, dashboard area).
- For dashboard, visualization, chart-ready analysis, budget/reporting, trend, schedule/timeline, and KPI prompts with plottable data, include at least one native Excel chart unless a verified export failure remains after simplifying the chart. Do not silently replace all charts with styled tables.
- For presentation-ready analytical workbooks, plain range formatting alone is usually not enough. Prefer real Excel structures where useful: tables, freeze panes, filters, data validation, conditional formats, and at least one chart/KPI/dashboard visual when the prompt implies summary analysis.
- In rendered previews of dashboards and summary sheets, check financial values and row labels at normal zoom. Widen columns, adjust row heights, or move chart panels until important numbers and text are not clipped, awkwardly wrapped, or hidden.

# Completion Criteria
Complete only when:
- Workbook content is populated and formulas compute.
- No obvious formula errors in key scanned ranges (no bad refs/off-by-one/circular errors).
- `.xlsx` saved to `outputs/<unique_thread_id>/`.
- Layout is organized, legible, and aligned to request style (or default formatting baseline).

# Verification Rules
Before final response, verify values/formulas and visual quality.

1. Inspect key ranges:
```js
const check = await workbook.inspect({
  kind: "table",
  range: "Dashboard!A1:H20",
  include: "values,formulas",
  tableMaxRows: 20,
  tableMaxCols: 12,
});
console.log(check.ndjson);
```

Inspect targeting:
- Prefer sheet-qualified ranges (`"Sheet!A1:H20"`) or `sheetId`.

2. Scan formula errors:
```js
const errors = await workbook.inspect({
  kind: "match",
  searchTerm: "#REF!|#DIV/0!|#VALUE!|#NAME\\?|#N/A",
  options: { useRegex: true, maxResults: 300 },
  summary: "final formula error scan",
});
console.log(errors.ndjson);
```

3. Render sheets/ranges to verify visual output (skip if already verified and no style changes):
```js
const blob = await workbook.render({ sheetName: "Sheet1", range: "A1:H20", scale: 2 });
```
Make sure you do at least one visual pass of all the sheets in the workbook before the final export.

Visual requirements:
- Fix severe defects before finalizing: blank/broken charts, clipped key headers or numbers, unreadable colors, obvious formula errors, default blank sheets, or content outside the visible working area.
- Ensure logical labels or titles appear once, texts are all clearly visible, and merged ranges exist where labels or content intentionally span multiple columns.
- Do one focused visual repair pass after the initial render. Do not spend additional passes on minor polish once the workbook is correct, legible, and exported; note any minor limitation briefly and finalize.

4. Keep verification compact:
- Inspect key ranges.
- Avoid huge NDJSON dumps.

5. Export:
```js
await fs.mkdir(outputDir, { recursive: true });
const output = await SpreadsheetFile.exportXlsx(workbook);
await output.save(`${outputDir}/output.xlsx`);
```

6. Finalize immediately after successful export + compact verification.
- Do not export extra `.xlsx` variants unless asked.
- Do not keep iterating on alternate designs once requirements are met, unless asked.

# Source, PDF, and Attachment Processing
- Use bundled runtime libraries for source extraction. For PDF or 10-K/10-Q style inputs, read PDF via bundled Python `pypdf` when available, then use one small structured extraction script to collect all required facts into a dict/JSON object. Avoid many ad hoc `rg`/`sed` passes over the same text.
- Keep source notes compact: record file name, section/table label, and enough context to audit the number. Do not paste large PDF excerpts into the workbook unless requested.
- Bundled Python libraries available for extraction/analysis include `pandas`, `numpy`, `pypdf`, `python-docx`, and `reportlab`.
- Bundled JS libraries available for document/PDF work include `docx`, `pdf-lib`, and `pdfjs-dist`.

# Artifact Tool API Reference
Read `references/artifact_tool_api.md` when building or editing workbooks and you need concrete JavaScript API syntax, API discovery, import/export patterns, existing-workbook inspection, feature-specific notes, or a runnable example. Use the workflow and verification rules above first; load the API reference only when needed.
