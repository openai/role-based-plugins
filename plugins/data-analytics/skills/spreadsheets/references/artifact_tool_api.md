# Artifact Tool API Reference

Use this reference when building or editing workbooks with `@oai/artifact-tool` and the core `SKILL.md` workflow is not enough. Keep API lookup targeted; do not load this file for lightweight routing or non-spreadsheet analysis.

## Contents
- Imports and startup
- Build patterns and conventions
- API discovery and formula lookup
- Existing workbook inspection
- Feature-specific notes and pitfalls
- Quick API surface
- Runnable JavaScript example

# Using artifact_tool APIs (JavaScript)

## Imports + Startup

Import existing workbook only when needed:
```js
import { FileBlob, SpreadsheetFile } from "@oai/artifact-tool";

const input = await FileBlob.load("path/to/input.xlsx");
const workbook = await SpreadsheetFile.importXlsx(input);
```

Import CSV text directly when the source or intermediate data is CSV:
```js
import fs from "node:fs/promises";
import { Workbook } from "@oai/artifact-tool";

const csvText = await fs.readFile("path/to/input.csv", "utf8");
const workbook = await Workbook.fromCSV(csvText, { sheetName: "Sheet1" });
```
Prefer `Workbook.fromCSV(...)` over hand-parsing CSV rows; clean or analyze CSV with Python/Node first only when needed.

Create new workbook:
```js
import fs from "node:fs/promises";
import { SpreadsheetFile, Workbook } from "@oai/artifact-tool";

const workbook = Workbook.create();
const sheet = workbook.worksheets.add("Inputs");
```

Final export:
```js
await fs.mkdir(outputDir, { recursive: true });
const output = await SpreadsheetFile.exportXlsx(workbook);
await output.save(`${outputDir}/output.xlsx`);
```

## Build Patterns
- Prefer block writes (`range.values`, `range.formulas`) over per-cell loops. Matrix shape must match the target range (for example `"D4:M4"` should be a 1x10 matrix, row x col).
- Seed scalar formulas once, then `fillDown()` / `fillRight()`. For dynamic-array formulas (`SEQUENCE`, `UNIQUE`, `FILTER`, `SORT`, `VSTACK`, `HSTACK`), write only the anchor cell and let the result spill after.
- Use `range.displayFormulas` plus `range.formulaInfos` when you need to understand a spill child or a data-table output cell.
- You do not need to call recalculate; calculation automatically happens.
- Date handling:
  - Prefer real `Date` objects for sortable/charted/formula date columns.
  - Apply date formats explicitly (for example `yyyy-mm-dd`).
- Use JSON-serializable values for non-Date cells: `string | number | boolean | null`.
- If a cell is intended to display literal text that begins with `=`, write it as a value prefixed with a single quote (for example `'=B2*C2`). This includes formula descriptions, validation examples, and labels; do not write these cells through `range.formulas`.
- Create every worksheet referenced by formulas before writing any cross-sheet formulas.
- When rebuilding dashboards, delete drawings first with `sheet.deleteAllDrawings()`. `range.clear()` does not remove charts, shapes, or images.
- Verify with `await workbook.inspect(...)`; use `workbook.help(...)` only when the quick surface below is insufficient.
- For formula audits or tracing how a formula is calculated, use `workbook.trace("Sheet!A1")` on the key output/check cells. It takes only a cell reference and returns the full tree, so print a capped summary. Do not dump raw traces.

## Conventions
- Use camelCase API names and option keys.
- Cell/range addressing: A1 notation (`sheet.getRange("A1:C10")`).
- Drawing anchors (`sheet.charts`, `sheet.shapes`, `sheet.images`): 0-based `{ row, col }`.
- Drawing offsets/extents use pixels (`rowOffsetPx`, `colOffsetPx`, `widthPx`, `heightPx`).

## API Discovery
- Use this quick API surface first.
- Use `workbook.help(...)` only when blocked by uncertainty.
- For help queries, start with exact feature/path lookups (`chart`, `worksheet.getRange`, `worksheet.freezePanes`, `range.dataValidation`, `chart.series.add`). If an exact path fails, one broader wildcard search is allowed.
- Do not repeat semantically similar help queries.
- If one help query returns 0 matches, reformulate once, then proceed best-effort.
- `render` can be used to examine an existing workbook visually and for visual verifications.

## Efficient Formula Lookup
- If you know the function name, use exact lookup first: `workbook.help("fx.PMT", { include: "index,examples,notes", maxChars: 3000 })`.
- To browse a family, use `fx.*` with a category regex. Useful categories: `financial`, `math-trig`, `statistical`, `lookup-reference`, `logical`, `text`, `date-time`, `information`, `engineering`, `database`.
- For intent-based lookup, use a short natural query plus a narrow `search` regex of likely functions.
- Keep `maxChars` bounded; if results are noisy, narrow `search` rather than issuing many similar queries.

Useful help calls:
```js
console.log(workbook.help("shape.add", { include: "examples,notes" }).ndjson);
console.log(
  workbook.help("*", {
    search: "fill|borders|autofit",
    include: "index,examples,notes",
    maxChars: 6000,
  }).ndjson,
);
console.log(workbook.help("fx.PMT", { include: "index,examples,notes" }).ndjson);
console.log(workbook.help("fx.*", { search: "financial", include: "index,examples", maxChars: 4000 }).ndjson);
console.log(workbook.help("fx.*", { search: "math-trig", include: "index,examples", maxChars: 4000 }).ndjson);
console.log(workbook.help("lookup with fallback", { search: "XLOOKUP|INDEX|MATCH|IFERROR", include: "index,examples,notes", maxChars: 4000 }).ndjson);
```

## Reading existing/imported workbooks
- On existing/imported workbooks, get a compact summary via `inspect` to understand what already exists and where.
- Prefer `inspect(...)` for workbook understanding and discovery across broad areas.
- Prefer direct getters like `range.formulas` when you already know the target range and need the exact rectangular formula matrix.
- If formula locations are unknown, prefer `inspect({ kind: "formula", ... })` over reading `range.formulas` across a very large area.
- Prefer to set `maxChars`, `tableMaxRows`, `tableMaxCols`, and/or `maxResults` to prevent large dumps of data.
- For suspicious or high-impact outputs, use `workbook.trace("Sheet!A1")` to audit the dependency tree from final output/check cell back to source cells. Trace output can be large, so summarize by depth/node count before logging.

### Inspect for workbook understanding
- Compact summary:
```js
await wb.inspect({
  kind: "workbook,sheet,table",
  maxChars: 6000,
  tableMaxRows: 6,
  tableMaxCols: 6,
  tableMaxCellChars: 80,
});
```
- Quick overview of sheet ids and names: `await wb.inspect({ kind: "sheet", include: "id,name" })`
- Formula discovery in a targeted area: `await wb.inspect({ kind: "formula", sheetId: firstSheetName, range: "A1:Z30", maxChars: 2500, options: {maxResults:50} })`
- Checking existing styles in a targeted area: `await wb.inspect({ kind: "computedStyle", sheetId: firstSheetName, range: "A1:E10", maxChars: 2500 })`
- Common `kind` tokens: `workbook`, `sheet`, `table`, `region`, `match`, `formula`, `thread`, `computedStyle`, `definedName`, `drawing`
- Inspects can also be used to zoom in on specific areas, especially for target edits:
```js
await wb.inspect({
  kind: "region",
  sheetId: firstSheetName,
  range: "A1:Z30",
  maxChars: 2500,
});
```
- Inspect output may include JSON records with `"id"` values (for example `"ws/r5qsk5"`), which you can resolve back to workbook objects with `wb.resolve(...)`:
- `wb.resolve("ws/...")` -> worksheet
- `wb.resolve("th/...")` -> comment thread

## Additional feature-specific notes

### Merging cells
- Merging cells is useful for visual headers, title bands, note/source blocks, and labels that span columns.
- `range.merge()` merges the target range into one cell; `range.merge(true)` merges across each row in the target range.
- `range.unmerge()` reverses a merge.
For example:
```js
const range = sheet.getRange("I23:N24");
range.merge();
range.values = [["Source note spanning the recommendation panel"]];
```

## Common API Pitfalls
- Do not set undocumented attributes on remote objects.
- `Workbook.create()` starts with no sheets; add one before calling `getActiveWorksheet()`.
- Use matrix sizes that match target ranges unless you intentionally spill.
- Create every worksheet referenced by formulas before writing cross-sheet formulas.
- Avoid full-column formula references such as `A:A`, `$A:$A`, or `Sheet!B:B`. Prefer bounded ranges sized to the editable table, e.g. `$A$6:$A$205`, especially inside `COUNTIFS`, `SUMIFS`, `INDEX`, and lookup formulas.
- If export fails, checkpoint-export after major blocks to isolate the cause: base sheets, values/formulas, formatting, conditional formatting, tables, charts/rendering.
- If export fails after formatting or charts, simplify optional styling first: nested border configs, custom chart axis/series mutations, broad autofit/formatting, then nonessential drawings.

## Quick API Surface (High-Value + Common)

### Core workbook/file APIs
- `import { FileBlob, SpreadsheetFile, Workbook } from "@oai/artifact-tool"`
- `const workbook = Workbook.create(); const sheet = workbook.worksheets.add("Sheet1")`
- `const workbook = await SpreadsheetFile.importXlsx(arrayBufferOrFileBlob)`
- `const xlsx = await SpreadsheetFile.exportXlsx(workbook); await xlsx.save("output.xlsx")`
- `const inspect = await workbook.inspect({ kind: "sheet", include: "id,name", sheetId, range: "A1:C10" })`
- `const help = workbook.help("worksheet.getRange", { include: "index,examples" })`
- `const trace = workbook.trace("Checks!F2")` // summarize before logging
- Preferred: `const blob = await workbook.render({ sheetName: "Sheet1", autoCrop: "all", scale: 1, format: "png" })`
- To get the bytes and/or save the blob to file:
```js
const previewBytes = new Uint8Array(await preview.arrayBuffer());
await fs.writeFile(`${outputDir}/preview.png`, previewBytes);
```
- `const workbook = await Workbook.fromCSV(csvText, { sheetName: "Sheet1" })`
- `await workbook.fromCSV(csvText, { sheetName: "ImportedData" })`

### Worksheet selection/creation
- `workbook.worksheets.add(name)`
- `workbook.worksheets.getItem(name)`
- `workbook.worksheets.getOrAdd(name, { renameFirstIfOnlyNewSpreadsheet: true })`
- `workbook.worksheets.getItemAt(index)`
- `workbook.worksheets.getActiveWorksheet()` (only after at least one sheet exists)

### Worksheet operations
- `sheet.getRange("A1:C10")`, `sheet.getRangeByIndexes(startRow, startCol, rowCount, colCount)`, `sheet.getCell(row, col)`
- `sheet.getUsedRange(valuesOnly?)`
- `sheet.mergeCells("A1:C1")`, `sheet.unmergeCells("A1:C1")`
- `sheet.freezePanes.freezeRows(1)`, `sheet.freezePanes.freezeColumns(2)`, `sheet.freezePanes.unfreeze()`
- `sheet.tables`, `sheet.charts`, `sheet.sparklineGroups` (`sheet.sparklines` alias), `sheet.shapes`, `sheet.images`
- `sheet.showGridLines = false`
- `sheet.dataTables`, `sheet.conditionalFormattings`, `sheet.dataValidations`
- `sheet.deleteAllDrawings()` removes charts, shapes, and images before a dashboard rebuild.

### Range values/formulas
- `const range = sheet.getRange("A1:C10")`
- `range.values = [[...], ...]` (2D matrix of values)
- `range.formulas = [["=..."], ...]`
- `range.formulasR1C1 = [["=RC[-1]*2"]]`
- To read: `range.values` / `range.formulas` / `range.displayFormulas` / `range.formulaInfos` (for spill/array formulas)
- `range.write(matrixOrPayload)` (auto-sizes/spills from anchor as needed)
- `range.writeValues(matrixOrRows)`
- `range.fillDown()`, `range.fillRight()`
  - `sheet.getRange("D2").formulas = [["=..."]]`
  - `sheet.getRange("D2:D200").fillDown()`
- `range.clear({ applyTo: "contents" | "formats" | "all" })`
- `range.copyFrom(sourceRange, "values" | "formulas" | "all")` source and destination must have the same shape
- `range.copyTo(destRange, "values" | "formulas" | "all")`
- `range.offset(...)`, `range.resize(...)`, `range.getCurrentRegion()`, `range.getRow(i)`, `range.getColumn(j)`
- `range.getRangeByIndexes(...)`, `range.getCell(...)`
- `range.merge()`, `range.merge(true)` to merge across, `range.unmerge()`

### Formatting
- `range.format` supports `fill`, `font`, `numberFormat`, `borders`, alignments, `wrapText`
- `range.format.autofitColumns()`, `range.format.autofitRows()`
- Excel unit sizing:  `range.format.columnWidth = 18`, `range.format.rowHeight = 24`
- Pixel sizing: `range.format.columnWidthPx = 120`, `range.format.rowHeightPx = 24`
- `range.setNumberFormat("yyyy-mm-dd")`
- `range.format.numberFormat = [["0"], ["0.00"], ["@"]]`

### Data Validation
- `range.dataValidation = { rule: { type: "list", formula1: "Categories!$A$2:$A$4" } }`
- `range.dataValidation = { rule: { type: "list", values: ["Not Started", "In Progress"] } }`
- `sheet.dataValidations.add({ range: "B2:B100", rule: { type: "whole", operator: "between", formula1: 1, formula2: 10 } })`

### Conditional formatting
- Use `range.conditionalFormats.add(ruleType, ConditionalFormatConfig);`.
- Use `range.conditionalFormats.add(ruleType, {operator, formula, format});`. Choose ruleType, operator, color, and style strings from the inline types below.
```
type ConditionalFormatRuleType =
  | "cellIs" | "CellValue" | "Custom" | "expression"
  | "colorScale" | "dataBar" | "iconSet"
  | "containsText" | "notContainsText" | "beginsWith" | "endsWith"
  | "containsBlanks" | "notContainsBlanks" | "containsErrors" | "notContainsErrors"
  | "duplicateValues" | "uniqueValues" | "timePeriod" | "top10" | "aboveAverage";

type CellIsOperator =
  | "greaterThan"
  | "greaterThanOrEqual"
  | "lessThan"
  | "lessThanOrEqual"
  | "equal"
  | "notEqual"
  | "between"
  | "notBetween";

type ConditionalFormatConfig =
  | { operator: CellIsOperator; formula: string | number | Array<string | number>; format?: DifferentialFormatConfig }
  | { formula: string | number; format?: DifferentialFormatConfig }
  | { colors?: ColorConfig[]; thresholds?: CfvoInput[] }
  | { color?: ColorConfig; thresholds?: CfvoInput[]; gradient?: boolean }
  | { iconSet: string; showValue?: boolean; reverse?: boolean; thresholds?: CfvoInput[] }
  | { text: string; format?: DifferentialFormatConfig }
  | { timePeriod: "yesterday" | "today" | "tomorrow" | "last7Days" | "lastWeek" | "thisWeek" | "nextWeek" | "lastMonth" | "thisMonth" | "nextMonth"; format?: DifferentialFormatConfig }
  | { rank?: number; percent?: boolean; bottom?: boolean; format?: DifferentialFormatConfig }
  | { aboveAverage?: boolean; equalAverage?: boolean; stdDev?: number; format?: DifferentialFormatConfig };

type DifferentialFormatConfig = {
  fill?: FillConfig;
  font?: { bold?: boolean; italic?: boolean; color?: ColorConfig };
  border?: RangeBordersConfig;
  numberFormat?: string;
};

type CfvoInput =
  | "min"
  | "max"
  | number
  | `${number}%`
  | { type: "min" | "max" | "num" | "percent" | "percentile"; value?: string | number };
```
- Rule types (`ConditionalFormatRuleType`): "cellIs" | "CellValue" | "Custom" | "expression"
  | "colorScale" | "dataBar" | "iconSet"
  | "containsText" | "notContainsText" | "beginsWith" | "endsWith"
  | "containsBlanks" | "notContainsBlanks" | "containsErrors" | "notContainsErrors"
  | "duplicateValues" | "uniqueValues" | "timePeriod" | "top10" | "aboveAverage";
- Built-in `iconSet` names: `3Arrows`, `3Triangles`, `4Arrows`, `5Arrows`, `3ArrowsGray`, `4ArrowsGray`, `5ArrowsGray`, `3TrafficLights1`, `3Signs`, `4RedToBlack`, `3TrafficLights2`, `4TrafficLights`, `3Symbols`, `3Flags`, `3Symbols2`, `3Stars`, `5Quarters`, `5Boxes`, `4Rating`, `5Rating`.
- Custom conditional formatting: `range.conditionalFormats.addCustom(expression, {fill, font, border});`
- `range.conditionalFormats.deleteAll()` / `range.conditionalFormats.clear()`

```js
const grid = sheet.getRange("B2:J10");
grid.conditionalFormats.add("colorScale", {
  criteria: [
    { type: "lowestValue", color: "#2563EB" },
    { type: "percentile", value: 50, color: "#FDE047" },
    { type: "highestValue", color: "#DC2626" },
  ],
});
```

### Tables
- When adding new tables, set explicit unique names (`TasksTable`, `SummaryTable`).
- You cannot have multiple tables over the same range. Before adding a table on an existing/imported workbook, confirm the target range does not already overlap an existing table. Prefer the initial compact `inspect` summary over a separate tables-only scan when available.
- `const table = sheet.tables.add("A1:H200", true, "TasksTable")`
- `table.rows.add(null, [[...], ...])`, `table.getDataRows()`, `table.getHeaderRowRange()`
- Read tables: `sheet.tables.items` -> `Table[]`
- Set + Getters: `table.name`, `table.style`, `table.style`, `table.showHeaders`
- Toggles for table utilities (set/get): `table.showTotals`, `table.showBandedColumns = true`, `table.showFilterButton`
- `table.delete()`

### Images
- `sheet.images.add({dataUrl: "data:image/png;base64,...", anchor: {from: { row: 1, col: 2 }, extent: { widthPx: 160, heightPx: 120 }}})`
```

### Threaded Comments
Follow this exact API when adding a note or comment:
- Required: First, always first call set_self to create an author `workbook.comments.setSelf({"displayName": "ChatGPT"})`
- Create a new thread with a single comment: `const thread = workbook.comments.addThread({"cell": sheet.getRange("E2")}, "Source: <website>")`
- To reply to a threaded comment: `thread.addReply("This is a reply to the comment")`
- To resolve/re-open a thread: `thread.resolve()`, `thread.reopen()`

### Charts
- When adding or moving charts, do not cover existing data. Put charts in a reserved rectangle with blank gutter columns/rows around the chart area.
- Fast chart path, no help lookup needed for common line/bar/scatter charts: write a compact helper range with text categories and one column per series, then chart that range.
- If chart data comes from editable/source data, make the helper range formula-backed instead of copying literal values.
```js
sheet.getRange("F4:H7").values = [
  ["Month", "Revenue", "EBITDA"],
  ["Jan", 100, 10],
  ["Feb", 120, 18],
  ["Mar", 130, 22],
];
const chart = sheet.charts.add("line", sheet.getRange("F4:H7"));
chart.setPosition("J4", "Q20");
chart.title = "Revenue and EBITDA Trend";
chart.hasLegend = true;
chart.xAxis = { axisType: "textAxis" };
chart.yAxis = { numberFormatCode: "$#,##0" };
```
- Fast chart path from range: `const chart = sheet.charts.add("line", sourceRange)` when the source range already has headers and text x-axis labels.
- Advanced fallback only: avoid manual `chart.series.add(...)` and `chart.legend = {...}` on the first pass unless source-range chart creation does not work (for example, non-continuous data). Use a helper range chart first, then add optional chart styling only if the basic chart renders and exports cleanly.
- If you want to set specific chart props after the helper-range path is not enough: `const chart = sheet.charts.add("bar", chartProps)`, then checkpoint export before adding optional styling.
- If using compat positioning, always set position: `chart.setPosition("F2", "M20")`.
- `sheet.charts.getItemOrNullObject("Chart 1")`, `sheet.charts.deleteAll()`
- To update x/y-axis, prefer compact config assignments such as `chart.xAxis = { axisType: "textAxis", tickLabelInterval: 2 }` and `chart.yAxis = { numberFormatCode: "$#,##0" }`. These help legibility and visibility.
- For month/date x-axes, prefer a chart helper range with text labels such as `Jan 2025` or `2025-01`. Do not rely on date axis number formats alone; rendered previews can show Excel serial numbers.
- Chart types: `"bar" | "line" | "area" | "pie" | "doughnut" | "scatter" | "bubble" | "radar" | "stock" | "treemap" | "sunburst" | "histogram" | "boxWhisker" | "waterfall" | "funnel" | "map"`.

### Sparklines
```
const group = sheet.sparklineGroups.add({
  type,
  targetRange,
  sourceData,
  dateAxisRange,
  seriesColor,
  negativeColor,
  markers,
  axis,
  lineWeight,
  displayEmptyCellsAs,
  displayHidden,
});
```
- Sparkline type is a string. Empty-cell display mode and axis min/max modes are proto enum numbers on the current facade; inspect nearby tests before setting them directly.
- Sparkline Inline Type:
```
type SparklineConfig = {
  type: "line" | "column" | "stacked";
  targetRange: Range | string;
  sourceData: Range | string;
  dateAxisRange?: Range | string;
  lineWeight?: number;
  displayHidden?: boolean;
  seriesColor?: ColorConfig;
  negativeColor?: ColorConfig;
  axisColor?: ColorConfig;
  markersColor?: ColorConfig;
  firstMarkerColor?: ColorConfig;
  lastMarkerColor?: ColorConfig;
  highMarkerColor?: ColorConfig;
  lowMarkerColor?: ColorConfig;
  markers?: SparklineMarkersOptions;
  axis?: SparklineAxisOptions;
};

type SparklineMarkersOptions = {
  show?: boolean;
  high?: boolean;
  low?: boolean;
  first?: boolean;
  last?: boolean;
  negative?: boolean;
};

type SparklineAxisOptions = {
  showAxis?: boolean;
  manualMin?: number;
  manualMax?: number;
  rightToLeft?: boolean;
};
```
- Range Alias: `const group = targetRange.sparklines.add(type, sourceRange, sparklineConfig);`
- Edit And Delete
```
group.seriesColor = colorConfig;
group.markers = markerConfig;
group.axis = axisConfig;
group.delete();
sheet.sparklineGroups.deleteAll();
```

### Help / Grep
Use `workbook.help(...)` primarily for obscure/advanced surfaces (for example deep chart axis settings, unusual drawing configs, pivot APIs, or uncommon option schemas).
- `workbook.help("enum.ShapeGeometry", { include: "index,notes" }).ndjson`
- `workbook.help("enum.*", { search: "ShapeGeometry|LineStyle", include: "index" }).ndjson`
- `workbook.help("shape.add", { include: "examples,notes" }).ndjson`
- `workbook.help("fx.RATE", { include: "index,examples,notes" }).ndjson`
- `workbook.help("cash flow return rate", { search: "IRR|XIRR|NPV|XNPV", include: "index,examples,notes", maxChars: 4000 }).ndjson`
- `workbook.help("*", { search: "fill|borders|autofit", include: "index,examples,notes", maxChars: 6000 }).ndjson`


### JavaScript example snippet (runnable)

```js
import fs from "node:fs/promises";
import { SpreadsheetFile, Workbook } from "@oai/artifact-tool";

const outputDir = "output";
await fs.mkdir(outputDir, { recursive: true });

const workbook = Workbook.create();
const sheet = workbook.worksheets.add("Summary");

sheet.getRange("A1:C4").values = [
  ["Month", "Revenue", "EBITDA"],
  ["Jan", 100, 10],
  ["Feb", 120, 18],
  ["Mar", 130, 22],
];
sheet.getRange("D1").values = [["Margin"]];
sheet.getRange("D2").formulas = [["=C2/B2"]];
sheet.getRange("D2:D4").fillDown();

sheet.getRange("A1:D1").format = {
  fill: "#0F766E",
  font: { bold: true, color: "#FFFFFF" },
};
sheet.getRange("B2:C4").format.numberFormat = "$#,##0";
sheet.getRange("D2:D4").format.numberFormat = "0.0%";

// Helper range links to source cells so edits update the chart.
sheet.getRange("F1:G1").values = [["Month", "Revenue"]];
sheet.getRange("F2:G2").formulas = [["=A2", "=B2"]];
sheet.getRange("F2:G4").fillDown();
const chart = sheet.charts.add("line", sheet.getRange("F1:G4"));
chart.title = "Revenue Trend";
chart.hasLegend = false;
chart.xAxis = { axisType: "textAxis" };
chart.yAxis = { numberFormatCode: "$#,##0" };
chart.setPosition("I1", "P15");

const preview = await workbook.render({
  sheetName: "Summary",
  autoCrop: "all",
  scale: 1,
  format: "png",
});
await fs.writeFile(`${outputDir}/summary.png`, new Uint8Array(await preview.arrayBuffer()));

const xlsx = await SpreadsheetFile.exportXlsx(workbook);
await xlsx.save(`${outputDir}/summary.xlsx`);
```
