import { ArrowDown, ArrowUp, Boxes, Camera, ChartArea, ChartBar, ChartColumn, ChartColumnStacked, ChartLine, ChartNoAxesColumn, ChartNoAxesCombined, ChartScatter, ChartSpline, Check, ChevronDown, ChevronLeft, ChevronRight, Copy, Database, Ellipsis, Expand, Filter as FunnelIcon, FileDown, FileText, Globe, Pencil, Presentation, RefreshCw, Table2, Tally3, Trash2, X, } from "lucide-react";
import { useCallback, useEffect, useId, useLayoutEffect, useMemo, useRef, useState } from "react";
import { createPortal } from "react-dom";
import { AnalyticsLayoutCanvas } from "./layout/AnalyticsLayoutCanvas";
import { isChartType as sharedIsChartType } from "./charting/chart-compatibility";
import { applyChartSpecOverride, chartEncoding, chartEncodingField, chartEncodingFields, chartEncodingLabel, chartHasEncodingSpec, chartSpecOverrideFromWidgetSpec, chartUsedFields, compatibleChartTypesFor, compatibleChartTypesForArtifactCard, withChartType } from "./charting/chart-app-helpers";
import { ChartRenderer } from "./charting/ChartRenderer";
import { RichMarkdown } from "./layout/RichMarkdown";
import { copyElementAsImage, copyTextToClipboard, imageCopySuccessMessage, shouldOfferImageClipboardCopy, usePreparedImageExport } from "./imageExport";
function resizeEditableTextarea(element) {
if (!element)
return;
element.style.height = "auto";
element.style.height = `${element.scrollHeight}px`;
}
function cloneSerializable(value) {
return JSON.parse(JSON.stringify(value));
}
const DEFAULT_DASHBOARD_CARD_LAYOUT = "half";
const DEFAULT_REPORT_CARD_LAYOUT = "full";
const CARD_DRAG_CANCEL_SELECTOR = ".viz-card__no-drag, button, a, input, textarea, select, [contenteditable='true'], .rich-markdown-editor, [role='button'], [role='menu'], [role='menuitem'], [role='menuitemradio']";
const CHART_FULLSCREEN_HEIGHT = 520;
const TABLE_CARD_PAGE_SIZE = 15;
const TABLE_COLUMN_DEFAULT_WIDTH = 144;
const TABLE_COLUMN_DENSE_HORIZONTAL_PADDING = 16;
const TABLE_COLUMN_HEADER_CHROME_WIDTH = 24;
const TABLE_COLUMN_KEYBOARD_STEP = 24;
const TABLE_COLUMN_MAX_WIDTH = 420;
const TABLE_COLUMN_MIN_WIDTH = 88;
const TABLE_COLUMN_NUMERIC_MAX_WIDTH = 136;
const TABLE_COLUMN_SAMPLE_SIZE = 50;
const TABLE_COLUMN_TEXT_MAX_WIDTH = 220;
const TABLE_COLUMN_LONG_TEXT_MAX_WIDTH = 260;
const EMPTY_ACCESS_ISSUES = [];
const EMPTY_CARDS = [];
const EMPTY_CHARTS = [];
const EMPTY_FILTERS = [];
const EMPTY_REPORT_BLOCKS = [];
const EMPTY_TABLES = [];
const KPI_COLUMN_BREAKPOINTS = [
{ minWidth: 760, columns: 3 },
{ minWidth: 520, columns: 2 },
{ minWidth: 392, columns: 2 }
];
function getHeatmapFill(intensity) {
const index = clamp(Math.floor(intensity * heatmapBlueScale.length), 0, heatmapBlueScale.length - 1);
return heatmapBlueScale[index];
}
async function fetchJson(path, init) {
const response = await fetch(path, { cache: "no-store", ...init });
const text = await response.text();
const payload = text ? JSON.parse(text) : {};
if (!response.ok) {
const message = typeof payload?.error === "string" ? payload.error : `Request failed: ${response.status}`;
throw new Error(message);
}
return payload;
}
async function fetchOptionalJson(path, init) {
try {
return await fetchJson(path, init);
}
catch {
return null;
}
}
function asNumber(value) {
if (typeof value === "number" && Number.isFinite(value))
return value;
if (typeof value === "string" && value.trim() !== "") {
const numeric = Number(value.replace(/,/g, ""));
if (Number.isFinite(numeric))
return numeric;
}
return null;
}
function asFiniteNumber(value, fallback = 0) {
if (typeof value === "number" && Number.isFinite(value))
return value;
if (typeof value === "string") {
const numeric = Number(value);
if (Number.isFinite(numeric))
return numeric;
}
return fallback;
}
function clamp(value, min, max) {
return Math.max(min, Math.min(max, value));
}
function formatValue(value, format = "compact") {
const numeric = asNumber(value);
if (numeric == null)
return value == null ? "n/a" : String(value);
if (format === "percent") {
return new Intl.NumberFormat(undefined, {
maximumFractionDigits: 1,
style: "percent"
}).format(numeric);
}
if (format === "currency") {
return new Intl.NumberFormat(undefined, {
currency: "USD",
maximumFractionDigits: 2,
notation: "compact",
style: "currency"
}).format(numeric);
}
if (format === "number") {
return new Intl.NumberFormat(undefined, { maximumFractionDigits: 2 }).format(numeric);
}
return new Intl.NumberFormat(undefined, {
maximumFractionDigits: 2,
notation: "compact"
}).format(numeric);
}
function cardLabel(card) {
return cardMetrics(card)[0]?.label ?? card.id;
}
function rowMatchesFilter(row, filter) {
if (!filter)
return true;
return Object.entries(filter).every(([field, expected]) => String(row[field] ?? "") === String(expected ?? ""));
}
function movementDirection(value) {
if (typeof value !== "string")
return null;
const trimmed = value.trim();
if (!trimmed)
return null;
if (/^[+↑]/.test(trimmed))
return "positive";
if (/^[-−↓]/.test(trimmed))
return "negative";
return null;
}
function formatMetricValue(value, metric) {
if (value == null || value === "")
return null;
const numeric = asNumber(value);
const rendered = formatValue(value, metric.format);
if (!metric.signed || numeric == null || numeric === 0)
return rendered;
return `${numeric > 0 ? "+" : ""}${rendered}`;
}
function metricMovementDirection(value, signed = false) {
if (!signed)
return null;
const numeric = asNumber(value);
if (numeric != null) {
if (numeric > 0)
return "positive";
if (numeric < 0)
return "negative";
return "neutral";
}
return movementDirection(value);
}
function cardMetrics(card) {
return Array.isArray(card.metrics) ? card.metrics : [];
}
function MetricInfoIcon({ className }) {
return (<svg aria-hidden="true" className={className} fill="none" height="21" viewBox="0 0 21 21" width="21" xmlns="http://www.w3.org/2000/svg">
<path d="M10.6 9.70459C11.0142 9.70461 11.35 10.0404 11.35 10.4546V13.7876C11.35 14.2018 11.0142 14.5376 10.6 14.5376C10.1858 14.5376 9.84998 14.2018 9.84998 13.7876V10.4546C9.84998 10.0404 10.1858 9.70459 10.6 9.70459Z" fill="currentColor"/>
<path d="M10.6 6.2876C11.1292 6.28762 11.558 6.71732 11.558 7.24658C11.5578 7.77569 11.1291 8.20457 10.6 8.20459C10.0708 8.20459 9.64215 7.7757 9.64197 7.24658C9.64197 6.71731 10.0707 6.2876 10.6 6.2876Z" fill="currentColor"/>
<path clipRule="evenodd" d="M10.6 2.53955C14.9713 2.53955 18.515 6.08326 18.515 10.4546C18.515 14.8259 14.9713 18.3696 10.6 18.3696C6.22864 18.3696 2.68494 14.8259 2.68494 10.4546C2.68494 6.08326 6.22864 2.53955 10.6 2.53955ZM10.6 3.86963C6.96318 3.86963 4.01501 6.81779 4.01501 10.4546C4.01501 14.0914 6.96318 17.0396 10.6 17.0396C14.2368 17.0396 17.1849 14.0914 17.1849 10.4546C17.1849 6.81779 14.2368 3.86963 10.6 3.86963Z" fill="currentColor" fillRule="evenodd"/>
</svg>);
}
function MetricDescriptionPopover({ description, label }) {
const tooltipId = useId();
const buttonRef = useRef(null);
const popoverRef = useRef(null);
const [isOpen, setIsOpen] = useState(false);
const [popoverStyle, setPopoverStyle] = useState(null);
const updatePopoverPosition = useCallback(() => {
if (typeof window === "undefined")
return;
const anchor = buttonRef.current?.getBoundingClientRect();
if (!anchor)
return;
const margin = 12;
const gap = 8;
const maxWidth = Math.max(120, Math.min(320, window.innerWidth - margin * 2));
const popoverRect = popoverRef.current?.getBoundingClientRect();
const width = Math.min(popoverRect?.width ?? maxWidth, maxWidth);
const height = popoverRect?.height ?? 0;
let left = anchor.left + anchor.width / 2 - width / 2;
left = clamp(left, margin, window.innerWidth - margin - width);
let top = anchor.bottom + gap;
if (height && top + height > window.innerHeight - margin && anchor.top - height - gap >= margin) {
top = anchor.top - height - gap;
}
else if (height) {
top = clamp(top, margin, window.innerHeight - margin - height);
}
setPopoverStyle((current) => {
if (current?.left === left && current?.top === top && current?.maxWidth === maxWidth)
return current;
return { left, maxWidth, top };
});
}, []);
useEffect(() => {
if (!isOpen) {
setPopoverStyle(null);
return;
}
updatePopoverPosition();
const frame = window.requestAnimationFrame(updatePopoverPosition);
window.addEventListener("resize", updatePopoverPosition);
window.addEventListener("scroll", updatePopoverPosition, true);
return () => {
window.cancelAnimationFrame(frame);
window.removeEventListener("resize", updatePopoverPosition);
window.removeEventListener("scroll", updatePopoverPosition, true);
};
}, [isOpen, updatePopoverPosition]);
const renderedPopoverStyle = popoverStyle
? { left: popoverStyle.left, maxWidth: popoverStyle.maxWidth, top: popoverStyle.top }
: { left: 0, maxWidth: "min(320px, calc(100vw - 24px))", top: 0, visibility: "hidden" };
return (<span className="kpi-info-wrap" onBlur={() => setIsOpen(false)} onFocus={() => setIsOpen(true)} onMouseEnter={() => setIsOpen(true)} onMouseLeave={() => setIsOpen(false)}>
<button aria-describedby={isOpen ? tooltipId : undefined} aria-label={`${label}: ${description}`} className="kpi-info" ref={buttonRef} type="button">
<MetricInfoIcon className="kpi-info-icon"/>
</button>
{isOpen && typeof document !== "undefined" ? createPortal(<span className="kpi-info-popover" id={tooltipId} ref={popoverRef} role="tooltip" style={renderedPopoverStyle}>
{description}
</span>, document.body) : null}
</span>);
}
function tableColumnFormat(column) {
if (column.format)
return column.format;
return column.type === "currency" || column.type === "number" || column.type === "percent"
? column.type
: undefined;
}
function tableColumnLooksLikeMovement(column) {
return column.movement === true || column.semantic === "movement" || column.role === "movement";
}
function tableCellMovementClass(column, value) {
if (!tableColumnLooksLikeMovement(column))
return "";
const numeric = asNumber(value);
const direction = numeric == null ? movementDirection(value) : numeric > 0 ? "positive" : numeric < 0 ? "negative" : "neutral";
if (!direction || direction === "neutral")
return "";
return `table-cell-movement table-cell-movement-${direction}`;
}
function formatTableDate(value) {
if (value == null || value === "")
return "";
if (value instanceof Date && !Number.isNaN(value.getTime())) {
return new Intl.DateTimeFormat(undefined, { dateStyle: "medium" }).format(value);
}
if (typeof value !== "string")
return String(value);
const trimmed = value.trim();
const monthMatch = trimmed.match(/^(\d{4})-(\d{2})$/);
if (monthMatch) {
const [, yearValue, monthValue] = monthMatch;
const date = new Date(Date.UTC(Number(yearValue), Number(monthValue) - 1, 1));
if (!Number.isNaN(date.getTime())) {
return new Intl.DateTimeFormat(undefined, {
month: "short",
timeZone: "UTC",
year: "numeric"
}).format(date);
}
}
const dayMatch = trimmed.match(/^(\d{4})-(\d{2})-(\d{2})(?:$|[T\s])/);
if (dayMatch) {
const [, yearValue, monthValue, dayValue] = dayMatch;
const date = new Date(Date.UTC(Number(yearValue), Number(monthValue) - 1, Number(dayValue)));
if (!Number.isNaN(date.getTime())) {
return new Intl.DateTimeFormat(undefined, {
day: "numeric",
month: "short",
timeZone: "UTC",
year: "numeric"
}).format(date);
}
}
return trimmed;
}
function formatTableCellValue(column, value) {
if (column.type === "date")
return formatTableDate(value);
const format = tableColumnFormat(column);
const rendered = format ? formatValue(value, format) : String(value ?? "");
if (!tableColumnLooksLikeMovement(column))
return rendered;
const numeric = asNumber(value);
if (numeric == null || numeric === 0)
return rendered;
return `${numeric > 0 ? "+" : ""}${rendered}`;
}
function normalizedTableTextLength(value) {
return String(value ?? "").replace(/\s+/g, " ").trim().length;
}
function percentileValue(values, percentile) {
if (!values.length)
return 0;
const sorted = [...values].sort((a, b) => a - b);
const index = clamp(Math.ceil(sorted.length * percentile) - 1, 0, sorted.length - 1);
return sorted[index];
}
function isNumericTableColumn(column, rows) {
if (tableColumnFormat(column))
return true;
let observed = false;
for (const row of rows.slice(0, TABLE_COLUMN_SAMPLE_SIZE)) {
const value = row[column.field];
if (value == null || value === "")
continue;
observed = true;
if (asNumber(value) == null)
return false;
}
return observed;
}
function tableColumnDisplayText(column, row) {
return formatTableCellValue(column, row[column.field]);
}
function estimateTableColumnWidth(column, rows, density) {
const sampleRows = rows.slice(0, TABLE_COLUMN_SAMPLE_SIZE);
const labelLength = normalizedTableTextLength(column.label);
const cellLengths = sampleRows
.map((row) => normalizedTableTextLength(tableColumnDisplayText(column, row)))
.filter((length) => length > 0);
const p90Length = percentileValue([labelLength, ...cellLengths], 0.9);
const maxLength = Math.max(labelLength, ...cellLengths, 0);
const columnKey = `${column.field} ${column.label}`.toLowerCase();
const isLongTextColumn = /(comment|description|detail|explanation|insight|interpretation|note|reason|summary)/.test(columnKey)
|| maxLength > 34;
const isNumericColumn = isNumericTableColumn(column, sampleRows);
const isDateColumn = /(date|day|month|quarter|week)/.test(columnKey);
const horizontalPadding = TABLE_COLUMN_HEADER_CHROME_WIDTH + (density === "dense" ? TABLE_COLUMN_DENSE_HORIZONTAL_PADDING : 0);
const charWidth = isNumericColumn ? 7.2 : 7.4;
const targetLength = isLongTextColumn
? Math.min(Math.max(labelLength + 4, p90Length), 44)
: Math.max(labelLength, p90Length);
const measuredWidth = Math.ceil(targetLength * charWidth + horizontalPadding);
if (isNumericColumn) {
const minWidth = tableColumnFormat(column) === "percent" ? 96 : 108;
return clamp(measuredWidth, minWidth, TABLE_COLUMN_NUMERIC_MAX_WIDTH);
}
if (isDateColumn) {
return clamp(measuredWidth, 116, 156);
}
if (isLongTextColumn) {
return clamp(measuredWidth, 220, TABLE_COLUMN_LONG_TEXT_MAX_WIDTH);
}
return clamp(measuredWidth, density === "dense" ? 124 : 112, TABLE_COLUMN_TEXT_MAX_WIDTH);
}
function estimateTableColumnWidths(table, rows, density) {
return Object.fromEntries(table.columns.map((column) => [
column.field,
estimateTableColumnWidth(column, rows, density)
]));
}
function formatDate(value) {
if (!value)
return "Unknown";
const date = new Date(value);
if (Number.isNaN(date.getTime()))
return value;
return new Intl.DateTimeFormat(undefined, {
dateStyle: "medium",
timeStyle: "short"
}).format(date);
}
function snapshotStatusLabel(status) {
if (!status || status === "ready")
return null;
if (status === "fixture")
return "Fixture data";
if (status === "partial")
return null;
return "Blocked snapshot";
}
function getRows(snapshot, dataset) {
return snapshot?.datasets?.[dataset] ?? [];
}
function asArray(value) {
return Array.isArray(value) ? value : [];
}
function asRecord(value) {
return value && typeof value === "object" && !Array.isArray(value)
? value
: {};
}
function normalizeManifest(rawManifest) {
const manifest = asRecord(rawManifest);
return {
...manifest,
version: 1,
title: typeof manifest.title === "string" ? manifest.title : "Data Analytics artifact",
generatedAt: typeof manifest.generatedAt === "string" ? manifest.generatedAt : "",
filters: asArray(manifest.filters).map((rawFilter) => {
const filter = asRecord(rawFilter);
return {
...filter,
targets: asArray(filter.targets)
};
}),
cards: asArray(manifest.cards).map((rawCard) => asRecord(rawCard)),
charts: asArray(manifest.charts).map((rawChart) => {
const chart = asRecord(rawChart);
return {
...chart,
referenceLines: asArray(chart.referenceLines)
};
}),
tables: asArray(manifest.tables).map((rawTable) => {
const table = asRecord(rawTable);
return {
...table,
columns: asArray(table.columns)
};
}),
sources: asArray(manifest.sources).map((rawSource) => asRecord(rawSource)),
blocks: asArray(manifest.blocks).map((rawBlock) => {
const block = asRecord(rawBlock);
return {
...block,
cardIds: asArray(block.cardIds)
};
})
};
}
function normalizeSnapshot(rawSnapshot) {
const snapshot = asRecord(rawSnapshot);
const datasets = {};
const rawDatasets = asRecord(snapshot.datasets);
for (const [dataset, rows] of Object.entries(rawDatasets)) {
datasets[dataset] = asArray(rows).filter((row) => Boolean(row) && typeof row === "object" && !Array.isArray(row));
}
return {
...snapshot,
version: 1,
generatedAt: typeof snapshot.generatedAt === "string" ? snapshot.generatedAt : "",
datasets,
accessIssues: asArray(snapshot.accessIssues)
};
}
function filterTargets(filter) {
const targets = [{ dataset: filter.dataset, field: filter.field }];
for (const target of filter.targets ?? []) {
targets.push({ dataset: target.dataset, field: target.field ?? filter.field });
}
const seen = new Set();
return targets.filter((target) => {
const key = `${target.dataset}\u0001${target.field}`;
if (seen.has(key))
return false;
seen.add(key);
return true;
});
}
function filterFieldForDataset(filter, dataset) {
return filterTargets(filter).find((target) => target.dataset === dataset)?.field ?? null;
}
function dashboardSurfaceDatasets(cards, charts, tables) {
return new Set([...cards, ...charts, ...tables]
.map((surface) => surface.dataset)
.filter((dataset) => Boolean(dataset)));
}
function isGlobalFilter(filter, cards, charts, tables) {
const requiredDatasets = dashboardSurfaceDatasets(cards, charts, tables);
if (requiredDatasets.size <= 1)
return true;
const targetDatasets = new Set(filterTargets(filter).map((target) => target.dataset));
return [...requiredDatasets].every((dataset) => targetDatasets.has(dataset));
}
function getGlobalFilters(filters, cards, charts, tables) {
return filters.filter((filter) => isGlobalFilter(filter, cards, charts, tables));
}
function filterRowsForDataset(rows, dataset, filters, selectedFilters, usedFields = []) {
const usedFieldSet = new Set(usedFields.filter(Boolean));
const explicitAllFields = new Set(filters
.map((filter) => {
const field = filterFieldForDataset(filter, dataset);
const selected = selectedFilters[filter.id] ?? filter.defaultValue ?? "all";
return field && selected === "all" && rows.some((row) => String(row[field] ?? "") === "all")
? field
: null;
})
.filter((field) => Boolean(field)));
const filteredRows = rows.filter((row) => filters.every((filter) => {
const field = filterFieldForDataset(filter, dataset);
if (!field)
return true;
const selected = selectedFilters[filter.id] ?? filter.defaultValue ?? "all";
if (selected === "all") {
return !explicitAllFields.has(field) || String(row[field] ?? "") === "all";
}
return String(row[field] ?? "") === selected;
}));
const aggregateFields = Object.keys(rows[0] ?? {}).filter((field) => {
if (usedFieldSet.has(field))
return false;
let hasAggregate = false;
let hasBreakdown = false;
for (const row of filteredRows) {
const value = String(row[field] ?? "");
if (value === "all")
hasAggregate = true;
else if (value)
hasBreakdown = true;
if (hasAggregate && hasBreakdown)
return true;
}
return false;
});
if (!aggregateFields.length)
return filteredRows;
const aggregateRows = filteredRows.filter((row) => aggregateFields.every((field) => String(row[field] ?? "") === "all"));
return aggregateRows.length ? aggregateRows : filteredRows;
}
function DashboardShell({ children, detailMode = false, isEditMode = false, surface }) {
return (<main className={`dashboard-shell ${surface === "report" ? "report-shell" : ""} ${detailMode ? "chart-detail-shell" : ""} ${isEditMode ? "is-app-editing" : ""}`.trim()} data-edit-mode={isEditMode ? "true" : "false"}>
{children}
</main>);
}
function dashboardCardLayout(layout) {
return layout ?? DEFAULT_DASHBOARD_CARD_LAYOUT;
}
function reportCardLayout(layout) {
return layout ?? DEFAULT_REPORT_CARD_LAYOUT;
}
function contentLayoutKey(manifest) {
if (!manifest)
return null;
const base = `${manifest.title}:${manifest.generatedAt}`;
return `datascience-dashboard:content-layout:${base}`;
}
function chartTextKey(manifest) {
if (!manifest)
return null;
const base = `${manifest.title}:${manifest.generatedAt}`;
return `datascience-dashboard:chart-text:${base}`;
}
function chartTypeKey(manifest) {
if (!manifest)
return null;
const base = `${manifest.title}:${manifest.generatedAt}`;
return `datascience-${manifest.surface ?? "dashboard"}:chart-type:${base}`;
}
function chartSpecKey(manifest) {
if (!manifest)
return null;
const base = `${manifest.title}:${manifest.generatedAt}`;
return `datascience-${manifest.surface ?? "dashboard"}:chart-spec:${base}`;
}
function pageTitleTextKey(manifest) {
if (!manifest)
return null;
const base = `${manifest.title}:${manifest.generatedAt}`;
return `datascience-${manifest.surface ?? "dashboard"}:page-title:${base}`;
}
function tableTextKey(manifest) {
if (!manifest)
return null;
const base = `${manifest.title}:${manifest.generatedAt}`;
return `datascience-${manifest.surface ?? "dashboard"}:table-text:${base}`;
}
function storageKeyHash(value) {
let hash = 2166136261;
for (let index = 0; index < value.length; index += 1) {
hash ^= value.charCodeAt(index);
hash = Math.imul(hash, 16777619);
}
return (hash >>> 0).toString(36);
}
function blockTextKey(manifest) {
if (!manifest)
return null;
const base = `${manifest.title}:${manifest.generatedAt}`;
const blockSignature = (manifest.blocks ?? [])
.map((block) => `${block.id}:${block.type}:${typeof block.body === "string" ? storageKeyHash(block.body) : ""}`)
.join(",");
return `datascience-report:block-text:${base}:${storageKeyHash(blockSignature)}`;
}
function deletedReportBlocksKey(manifest) {
if (!manifest)
return null;
const base = `${manifest.title}:${manifest.generatedAt}`;
const blockSignature = (manifest.blocks ?? [])
.map((block) => block.id)
.join(",");
return `datascience-report:deleted-blocks:${base}:${blockSignature}`;
}
function tableColumnWidthKey(manifest) {
if (!manifest)
return null;
const base = `${manifest.title}:${manifest.generatedAt}`;
const surface = manifest.surface ?? "dashboard";
const tableSignature = (manifest.tables ?? [])
.map((table) => `${table.id}:${table.columns.map((column) => column.field).join("|")}`)
.join(",");
return `datascience-${surface}:table-column-widths:${base}:${tableSignature}`;
}
function reportContentLayoutKey(manifest) {
if (!manifest)
return null;
const base = `${manifest.title}:${manifest.generatedAt}`;
const blockSignature = (manifest.blocks ?? [])
.map((block) => `${block.id}:${reportCardLayout(block.layout)}`)
.join(",");
return `datascience-report:content-layout:v3:${base}:${blockSignature}`;
}
function sourceForChart(chart, sources) {
if (chart?.source && typeof chart.source === "object")
return chart.source;
return sources.find((source) => source.id === chart.sourceId) ?? null;
}
function sourceForTable(table, sources) {
if (table?.source && typeof table.source === "object")
return table.source;
return sources.find((source) => source.id === table.sourceId) ?? null;
}
function sourceQueryFromChartSpec(chart) {
return chart?.source?.query ?? null;
}
function sourceQueryFromSourceSpec(source) {
if (!source)
return null;
return source.query ?? null;
}
function queryTextFromSourceQuery(sourceQuery) {
return (sourceQuery?.sql ?? "").trim();
}
function accessIssueForChart(chart, issues) {
return (issues.find((issue) => issue.dataset === chart.dataset) ??
issues.find((issue) => issue.sourceId && issue.sourceId === chart.sourceId) ??
null);
}
function activeFilterSummary(filters, selectedFilters) {
const active = filters
.map((filter) => {
const value = selectedFilters[filter.id] ?? filter.defaultValue ?? "all";
return value === "all" ? null : `${filter.label}: ${value}`;
})
.filter(Boolean);
return active.length ? active.join(", ") : "None";
}
function stringListFromValue(value) {
if (Array.isArray(value)) {
return value
.map((item) => {
if (item && typeof item === "object") {
const label = item.label ?? item.name ?? item.table ?? item.field ?? item.metric ?? item.id;
const detail = item.description ?? item.definition ?? item.value ?? item.expression;
return label && detail ? `${label}: ${detail}` : label ?? detail;
}
return item;
})
.map((item) => String(item ?? "").trim())
.filter(Boolean);
}
if (value && typeof value === "object") {
return Object.entries(value)
.map(([key, item]) => `${key}: ${item}`)
.map((item) => item.trim())
.filter(Boolean);
}
const textValue = String(value ?? "").trim();
return textValue ? [textValue] : [];
}
function firstStringList(objects, keys) {
for (const object of objects) {
if (!object)
continue;
for (const key of keys) {
const values = stringListFromValue(object[key]);
if (values.length)
return values;
}
}
return [];
}
function isLikelySourceTableName(value) {
const tableName = String(value ?? "").trim().replace(/^[`"\[]|[`"\]]$/g, "");
return /^[A-Za-z0-9_-]+(?:\.[A-Za-z0-9_-]+){1,3}$/.test(tableName);
}
function sourceTableNamesFromMetadata(objects) {
const values = firstStringList(objects, ["tables_used", "tablesUsed", "source_tables", "sourceTables", "tables"]);
return values.filter(isLikelySourceTableName);
}
function extractTablesFromQuery(queryText) {
const tables = [];
const seen = new Set();
const pattern = /\b(?:from|join)\s+([`"\[]?[\w.-]+(?:\.[\w.-]+){0,3}[`"\]]?)/gi;
let match;
while ((match = pattern.exec(queryText ?? ""))) {
const table = match[1].replace(/^[`"\[]|[`"\]]$/g, "");
const normalized = table.toLowerCase();
if (!table || seen.has(normalized))
continue;
seen.add(normalized);
tables.push(table);
}
return tables;
}
function sourceBuildDetails({ activeFilters, columns = [], dataset, metrics = [], source, sourceQuery, snapshot }) {
const queryText = queryTextFromSourceQuery(sourceQueryFromSourceSpec(source)) || queryTextFromSourceQuery(sourceQuery) || "";
const metadataObjects = [source, sourceQueryFromSourceSpec(source), sourceQuery].filter(Boolean);
const explicitTables = sourceTableNamesFromMetadata(metadataObjects);
const inferredTables = extractTablesFromQuery(queryText);
const tables = explicitTables.length ? explicitTables : inferredTables;
const filters = firstStringList(metadataObjects, [
"filters",
"filter_descriptions",
"filterDescriptions",
"filter_description",
"filterDescription",
]);
const metricDefinitions = firstStringList(metadataObjects, [
"metric_definitions",
"metricDefinitions",
"metrics_definition",
"metricDefinition",
]);
const fallbackMetrics = metricDefinitions.length
? metricDefinitions
: metrics.length
? metrics.map((metric) => `${metric.label}: displayed from ${metric.field}`)
: columns
.filter((column) => ["number", "percent", "currency"].includes(column.format ?? column.type ?? ""))
.map((column) => `${column.label ?? column.field}: displayed from ${column.field}`)
.slice(0, 6);
const filterRows = filters.length ? filters : activeFilters && activeFilters !== "None" ? [activeFilters] : ["None declared"];
const tableRows = tables.length ? tables : ["Not declared"];
const snapshotValue = sourceQuery?.executed_at ?? sourceQueryFromSourceSpec(source)?.executed_at ?? snapshot?.generatedAt ?? "Not declared";
const primarySource = tableRows[0] === "Not declared" ? dataset ?? "reviewed rows" : tableRows[0];
const summary = `This block uses ${primarySource} for dataset ${dataset ?? "unknown"}.${filterRows[0] !== "None declared" ? ` Filters: ${filterRows.slice(0, 2).join("; ")}.` : ""} Use the source query below to inspect the exact logic.`;
return {
dataset: dataset ?? "Not declared",
fields: columns
.map((column) => column.field ?? column.key ?? column.label)
.filter(Boolean),
filters: filterRows,
metricDefinitions: fallbackMetrics.length ? fallbackMetrics : ["Displayed directly from source columns"],
snapshot: snapshotValue,
summary,
tables: tableRows
};
}
function detailText(values, fallback = "Not declared") {
const items = Array.isArray(values) ? values.filter(Boolean) : [values].filter(Boolean);
return items.length ? items.join("; ") : fallback;
}
function detailList(values, fallback = "Not declared") {
const items = Array.isArray(values) ? values.filter(Boolean) : [values].filter(Boolean);
if (!items.length)
return fallback;
return (<div className="source-detail-list">
{items.map((item, index) => <div className="source-detail-list-item" key={`${index}-${item}`}>
{item}
</div>)}
</div>);
}
function compareTableValues(a, b, field, direction) {
const aValue = a[field];
const bValue = b[field];
if (aValue == null && bValue == null)
return 0;
if (aValue == null)
return direction === "asc" ? 1 : -1;
if (bValue == null)
return direction === "asc" ? -1 : 1;
let result = 0;
if (typeof aValue === "number" && typeof bValue === "number") {
result = aValue - bValue;
}
else {
result = String(aValue).localeCompare(String(bValue), undefined, {
numeric: true,
sensitivity: "base"
});
}
return direction === "asc" ? result : -result;
}
function MetricBadge({ metric, row }) {
const value = row[metric.field];
const renderedValue = formatMetricValue(value, metric);
if (!renderedValue)
return null;
const direction = metricMovementDirection(value, metric.signed === true);
return (<div className={`metric-badge ${direction ?? "neutral"}`}>
<span className="metric-badge-label">{metric.label}</span>
<span className="metric-badge-value">{renderedValue}</span>
</div>);
}
function KpiCard({ card, filters, selectedFilters, snapshot }) {
const metrics = cardMetrics(card);
const [primaryMetric, ...supportingMetrics] = metrics;
const rows = filterRowsForDataset(getRows(snapshot, card.dataset), card.dataset, filters, selectedFilters, metrics.map((metric) => metric.field));
const row = rows.find((candidate) => rowMatchesFilter(candidate, card.filter)) ?? {};
const label = cardLabel(card);
const description = card.description?.trim();
return (<section className="kpi-card">
<div className="kpi-label-row">
<div className="kpi-label">{label}</div>
{description ? <MetricDescriptionPopover description={description} label={label}/> : null}
</div>
<div className="kpi-value">{primaryMetric ? formatValue(row[primaryMetric.field], primaryMetric.format) : "—"}</div>
{supportingMetrics.length ? (<div className="metric-badge-row">
{supportingMetrics.map((metric) => (<MetricBadge key={`${metric.field}:${metric.label}`} metric={metric} row={row}/>))}
</div>) : null}
</section>);
}
function getKpiColumnCount(width, cardCount) {
const breakpoint = KPI_COLUMN_BREAKPOINTS.find((item) => width >= item.minWidth);
return Math.max(1, Math.min(cardCount, breakpoint?.columns ?? 1));
}
function useMeasuredElementSize() {
const ref = useRef(null);
const [size, setSize] = useState({ height: 0, width: 0 });
useEffect(() => {
const element = ref.current;
if (!element)
return;
let frame = 0;
const updateWidth = () => {
window.cancelAnimationFrame(frame);
frame = window.requestAnimationFrame(() => {
const rect = element.getBoundingClientRect();
setSize({
height: Math.floor(rect.height),
width: Math.floor(rect.width)
});
});
};
updateWidth();
const observer = new ResizeObserver(updateWidth);
observer.observe(element);
window.addEventListener("resize", updateWidth);
return () => {
window.cancelAnimationFrame(frame);
observer.disconnect();
window.removeEventListener("resize", updateWidth);
};
}, []);
return [ref, size];
}
function KpiStrip({ cards, filters, selectedFilters, snapshot }) {
const [stripRef, stripSize] = useMeasuredElementSize();
const fallbackWidth = typeof window === "undefined" ? 0 : window.innerWidth;
const columns = getKpiColumnCount(stripSize.width || fallbackWidth, cards.length);
const placeholderCount = (columns - (cards.length % columns)) % columns;
const stripStyle = { "--kpi-columns": columns };
if (!cards.length)
return null;
return (<section className={`kpi-strip kpi-columns-${columns}`} style={stripStyle} aria-label="Key metrics" ref={stripRef}>
{cards.map((card) => (<KpiCard card={card} filters={filters} key={card.id} selectedFilters={selectedFilters} snapshot={snapshot}/>))}
{Array.from({ length: placeholderCount }, (_, index) => (<div aria-hidden="true" className="kpi-card kpi-card-placeholder" key={`kpi-placeholder-${index}`}/>))}
</section>);
}
const MENU_CLOSE_ANIMATION_MS = 100;
const NARROW_FIXED_MENU_QUERY = "(max-width: 560px)";
function useDashboardMenu(isOpen, onOpenChange) {
const menuButtonRef = useRef(null);
const menuRef = useRef(null);
const isOpenRef = useRef(isOpen);
const [shouldRenderMenu, setShouldRenderMenu] = useState(isOpen);
const [menuMotionClass, setMenuMotionClass] = useState("opening");
const [fixedMenuStyle, setFixedMenuStyle] = useState(undefined);
useEffect(() => {
isOpenRef.current = isOpen;
}, [isOpen]);
const updateFixedMenuStyle = useCallback(() => {
if (typeof window === "undefined") {
return;
}
if (!window.matchMedia(NARROW_FIXED_MENU_QUERY).matches) {
setFixedMenuStyle(undefined);
return;
}
const anchor = menuButtonRef.current?.getBoundingClientRect();
if (!anchor) {
return;
}
const menuSurface = menuRef.current?.matches?.('[role="menu"]')
? menuRef.current
: menuRef.current?.querySelector?.('[role="menu"]');
const margin = 12;
const gap = 6;
const surfaceHeight = menuSurface?.getBoundingClientRect?.().height ?? 0;
let top = anchor.bottom + gap;
if (surfaceHeight && top + surfaceHeight > window.innerHeight - margin && anchor.top - surfaceHeight - gap >= margin) {
top = anchor.top - surfaceHeight - gap;
}
else if (surfaceHeight) {
top = clamp(top, margin, window.innerHeight - margin - surfaceHeight);
}
else {
top = clamp(top, margin, window.innerHeight - margin);
}
setFixedMenuStyle((current) => {
if (current?.top === top)
return current;
return { top };
});
}, []);
function menuItems() {
return Array.from(menuRef.current?.querySelectorAll('[role="menuitem"], [role="menuitemradio"]') ?? []).filter((item) => !item.disabled);
}
function focusMenuItem(position) {
window.requestAnimationFrame(() => {
const items = menuItems();
if (!items.length)
return;
const index = position === "first"
? 0
: position === "last"
? items.length - 1
: Math.max(0, Math.min(items.length - 1, position));
items[index]?.focus();
});
}
function openMenu() {
setShouldRenderMenu(true);
setMenuMotionClass("opening");
onOpenChange(true);
}
function closeMenu() {
onOpenChange(false);
}
function setMenuOpen(nextIsOpen) {
if (nextIsOpen) {
openMenu();
return;
}
closeMenu();
}
function toggleMenu() {
const nextIsOpen = !isOpenRef.current;
setMenuOpen(nextIsOpen);
return nextIsOpen;
}
useEffect(() => {
if (isOpen) {
setShouldRenderMenu(true);
setMenuMotionClass("opening");
return;
}
if (!shouldRenderMenu)
return;
setMenuMotionClass("closing");
const closeTimer = window.setTimeout(() => {
setShouldRenderMenu(false);
}, MENU_CLOSE_ANIMATION_MS);
return () => {
window.clearTimeout(closeTimer);
};
}, [isOpen, shouldRenderMenu]);
useLayoutEffect(() => {
if (!shouldRenderMenu) {
setFixedMenuStyle(undefined);
return;
}
updateFixedMenuStyle();
const frame = window.requestAnimationFrame(updateFixedMenuStyle);
window.addEventListener("resize", updateFixedMenuStyle);
window.addEventListener("scroll", updateFixedMenuStyle, true);
return () => {
window.cancelAnimationFrame(frame);
window.removeEventListener("resize", updateFixedMenuStyle);
window.removeEventListener("scroll", updateFixedMenuStyle, true);
};
}, [shouldRenderMenu, updateFixedMenuStyle]);
useEffect(() => {
if (!isOpen)
return;
function handlePointerDown(event) {
const target = event.target;
if (!menuRef.current?.contains(target) && !menuButtonRef.current?.contains(target)) {
closeMenu();
}
}
function handleKeyDown(event) {
if (event.key === "Escape") {
closeMenu();
menuButtonRef.current?.focus();
}
}
document.addEventListener("pointerdown", handlePointerDown);
document.addEventListener("keydown", handleKeyDown);
return () => {
document.removeEventListener("pointerdown", handlePointerDown);
document.removeEventListener("keydown", handleKeyDown);
};
}, [isOpen, onOpenChange]);
return {
closeMenu,
fixedMenuStyle,
handleMenuButtonKeyDown: (event) => {
if (event.key === "ArrowDown" || event.key === "ArrowUp") {
event.preventDefault();
openMenu();
focusMenuItem(event.key === "ArrowDown" ? "first" : "last");
}
},
handleMenuKeyDown: (event) => {
if (event.key !== "ArrowDown" &&
event.key !== "ArrowUp" &&
event.key !== "Home" &&
event.key !== "End" &&
event.key !== "Escape") {
return;
}
event.preventDefault();
if (event.key === "Escape") {
closeMenu();
menuButtonRef.current?.focus();
return;
}
const items = menuItems();
if (!items.length)
return;
const activeIndex = items.findIndex((item) => item === document.activeElement);
if (event.key === "Home") {
focusMenuItem("first");
return;
}
if (event.key === "End") {
focusMenuItem("last");
return;
}
const offset = event.key === "ArrowDown" ? 1 : -1;
const nextIndex = activeIndex === -1
? (event.key === "ArrowDown" ? 0 : items.length - 1)
: (activeIndex + offset + items.length) % items.length;
focusMenuItem(nextIndex);
},
menuButtonRef,
menuMotionClass,
menuRef,
toggleMenu,
shouldRenderMenu
};
}
function FilterMenu({ label, onChange, options, value }) {
const [isOpen, setIsOpen] = useState(false);
const { closeMenu, handleMenuButtonKeyDown, handleMenuKeyDown, menuButtonRef, menuMotionClass, menuRef, toggleMenu, shouldRenderMenu } = useDashboardMenu(isOpen, setIsOpen);
const selectedOption = options.find((option) => option.value === value) ?? options[0];
return (<div className="filter-menu" ref={menuRef}>
<button aria-expanded={isOpen} aria-haspopup="menu" className="filter-menu-button" onClick={toggleMenu} onKeyDown={handleMenuButtonKeyDown} ref={menuButtonRef} type="button">
<span className="filter-menu-label">{label}</span>
<span className="filter-menu-value">{selectedOption?.label ?? value}</span>
<ChevronDown aria-hidden="true" size={14} strokeWidth={2}/>
</button>
{shouldRenderMenu ? (<div className={`filter-menu-list menu-surface ${menuMotionClass}`} onKeyDown={handleMenuKeyDown} role="menu">
{options.map((option) => {
const isSelected = option.value === value;
return (<button aria-checked={isSelected} className="filter-menu-item" key={option.value} onClick={() => {
onChange(option.value);
closeMenu();
}} role="menuitemradio" type="button">
<span>{option.label}</span>
{isSelected ? <Check aria-hidden="true" size={14} strokeWidth={2}/> : null}
</button>);
})}
</div>) : null}
</div>);
}
function FilterToolbar({ filters, snapshot, selectedFilters, onChange }) {
if (!filters.length)
return null;
return (<div className="filter-toolbar" aria-label="Analytics filters">
<div className="filter-group">
{filters.map((filter) => {
const options = Array.from(new Set(getRows(snapshot, filter.dataset).map((row) => String(row[filter.field] ?? ""))))
.filter(Boolean)
.sort();
const filterOptions = [
...(filter.includeAll === false ? [] : [{ label: "All", value: "all" }]),
...options.map((option) => ({ label: option, value: option }))
];
const value = selectedFilters[filter.id] ?? filter.defaultValue ?? "all";
return (<FilterMenu key={filter.id} label={filter.label} onChange={(nextValue) => onChange({ ...selectedFilters, [filter.id]: nextValue })} options={filterOptions} value={value}/>);
})}
</div>
</div>);
}
function PanelHeader({ action, children, title, subtitle, titleRowClassName, titleRowProps }) {
return (<div className="panel-header">
<div {...titleRowProps} className={`panel-title-row ${titleRowClassName ?? ""} ${titleRowProps?.className ?? ""}`.trim()}>
{children ?? (<div>
<h2>{title}</h2>
{subtitle ? <p>{subtitle}</p> : null}
</div>)}
</div>
{action}
</div>);
}
function EditablePageTitle({ ariaLabel, isEditMode, onChange, onRequestEditMode, placeholder, readOnly = false, title }) {
const [isEditing, setIsEditing] = useState(false);
const textareaRef = useRef(null);
const displayTitle = title.trim() ? title : placeholder;
useEffect(() => {
if (isEditing)
resizeEditableTextarea(textareaRef.current);
}, [isEditing, title]);
function startEditing() {
if (readOnly)
return;
if (!isEditMode)
onRequestEditMode();
setIsEditing(true);
}
if (readOnly) {
return (<div className="page-title-edit-target page-title-readonly">
<h1>{displayTitle}</h1>
</div>);
}
if (isEditing) {
return (<textarea aria-label={ariaLabel} autoFocus className="page-title-editor viz-card__no-drag" onBlur={() => setIsEditing(false)} onChange={(event) => {
resizeEditableTextarea(event.currentTarget);
onChange(event.currentTarget.value);
}} placeholder={placeholder} ref={textareaRef} rows={1} value={title}/>);
}
return (<div aria-label={ariaLabel} className="page-title-edit-target viz-card__no-drag" data-page-title-edit-mode={isEditMode ? "true" : "false"} onClick={() => {
if (isEditMode)
startEditing();
}} onDoubleClick={startEditing} onKeyDown={(event) => {
if (event.key === "Enter" || event.key === " ") {
event.preventDefault();
startEditing();
}
}} role="button" tabIndex={0}>
<h1>{displayTitle}</h1>
</div>);
}
function composeHeaderMarkdown(title, description) {
return description?.trim() ? `## ${title}\n\n${description}` : `## ${title}`;
}
function composeVisualHeaderMarkdown(title, description, headerMarkdown) {
if (headerMarkdown?.trim()) {
return headerMarkdown;
}
return composeHeaderMarkdown(title, description);
}
function composePageTitle(manifest) {
const fallbackTitle = manifest?.surface === "report" ? "Data Analytics Report" : "Data Analytics Dashboard";
return manifest?.title?.trim() || fallbackTitle;
}
function composeChartHeaderMarkdown(chart) {
return composeVisualHeaderMarkdown(chart.title, chart.showDescription ? chart.subtitle : undefined, chart.headerMarkdown);
}
function composeTableHeaderMarkdown(table) {
return composeVisualHeaderMarkdown(table.title, table.showDescription ? table.subtitle : undefined, table.headerMarkdown);
}
function reportBlockBodyMarkdown(block) {
return typeof block.body === "string" ? block.body : "";
}
function visibleString(value) {
return typeof value === "string" && value.trim() ? value : undefined;
}
function composeBlockMarkdown(block, textOverride) {
if (visibleString(textOverride?.bodyMarkdown))
return textOverride.bodyMarkdown;
return reportBlockBodyMarkdown(block);
}
function composeBlockHtml(block, textOverride) {
if (visibleString(textOverride?.html))
return textOverride.html;
return typeof block.body === "string" ? block.body : "";
}
const REPORT_HTML_BLOCK_CSP = [
"default-src 'none'",
"base-uri 'none'",
"connect-src 'none'",
"font-src data:",
"form-action 'none'",
"frame-src 'none'",
"img-src data: blob:",
"media-src data: blob:",
"object-src 'none'",
"script-src 'none'",
"style-src 'unsafe-inline'",
].join("; ");
function sandboxedReportHtml(html) {
return `<!doctype html><html><head><meta charset="utf-8"><meta http-equiv="Content-Security-Policy" content="${REPORT_HTML_BLOCK_CSP}"><meta name="viewport" content="width=device-width, initial-scale=1"><base target="_blank"><style>html,body{margin:0;background:transparent;}img,svg,canvas,video{max-width:100%;height:auto;}</style></head><body>${html}</body></html>`;
}
function measureHtmlFrameHeight(frame) {
const documentElement = frame?.contentDocument?.documentElement;
const body = frame?.contentDocument?.body;
if (!documentElement && !body)
return 0;
return Math.ceil(Math.max(documentElement?.scrollHeight ?? 0, body?.scrollHeight ?? 0));
}
function markdownPlainText(markdown) {
return markdown
.replace(/^#{1,6}\s+/gm, "")
.replace(/\*\*([^*]+)\*\*/g, "$1")
.replace(/`([^`]+)`/g, "$1")
.replace(/\[([^\]]+)\]\([^)]+\)/g, "$1")
.trim();
}
function markdownFirstLine(markdown, fallback) {
const first = markdownPlainText(markdown).split(/\r?\n/).find((line) => line.trim());
return first?.trim() || fallback;
}
function ChartBody({ accessIssue, chart, filters, isFullscreen = false, selectedFilters, snapshot }) {
const [visibleSeries, setVisibleSeries] = useState();
const rawRows = filterRowsForDataset(getRows(snapshot, chart.dataset), chart.dataset, filters, selectedFilters, chartUsedFields(chart));
if (accessIssue) {
return (<div className="permission-card">
<div className="permission-card-title">Missing data access</div>
<p>{accessIssue.message}</p>
{accessIssue.actionHref ? (<a href={accessIssue.actionHref} rel="noreferrer" target="_blank">
{accessIssue.actionLabel ?? "Request access"}
</a>) : accessIssue.actionLabel ? (<span>{accessIssue.actionLabel}</span>) : null}
</div>);
}
if (!rawRows.length) {
return <div className="empty-state">No rows match the selected filters.</div>;
}
return (<ChartRenderer chart={chart} height={isFullscreen ? CHART_FULLSCREEN_HEIGHT : undefined} onVisibleSeriesChange={setVisibleSeries} rows={rawRows} surface={isFullscreen ? "explorer" : "card"} visibleSeries={visibleSeries}/>);
}
function VizCard({ accessIssue, chart, children, isEditMode, isMenuOpen, layout, onCopyResult, onDeleteBlock, onRequestEditMode, onTextChange, onMenuOpenChange, onModalOpen, textOverride }) {
const cardRef = useRef(null);
const { closeMenu, fixedMenuStyle, handleMenuButtonKeyDown, handleMenuKeyDown, menuButtonRef, menuMotionClass, menuRef, toggleMenu, shouldRenderMenu } = useDashboardMenu(isMenuOpen, onMenuOpenChange);
const [imageExportState, setImageExportState] = useState({ status: "idle" });
const { getPreparedImageBlob, preparedImageExportStatus, prepareImageExport, resetPreparedImageExport } = usePreparedImageExport(cardRef);
const fallbackHeaderMarkdown = textOverride?.title || textOverride?.subtitle
? composeHeaderMarkdown(textOverride.title ?? chart.title, textOverride.subtitle ?? chart.subtitle)
: composeChartHeaderMarkdown(chart);
const displayHeaderMarkdown = textOverride?.headerMarkdown ?? fallbackHeaderMarkdown;
const displayChart = {
...chart,
subtitle: undefined,
title: markdownFirstLine(displayHeaderMarkdown, chart.title)
};
function prepareImageExportQuietly(force = false) {
if (accessIssue || !shouldOfferImageClipboardCopy())
return;
const prepared = prepareImageExport({ force });
if (prepared)
void prepared.promise.catch(() => undefined);
}
async function handleCopyAsImage() {
if (!cardRef.current)
return;
setImageExportState({ status: "loading" });
try {
const copyResult = await copyElementAsImage(cardRef.current, getPreparedImageBlob());
setImageExportState({ status: "idle" });
resetPreparedImageExport();
onCopyResult(imageCopySuccessMessage("Copied widget as image.", copyResult));
}
catch (error) {
setImageExportState({
error: error instanceof Error ? error.message : "Failed to copy image.",
status: "error"
});
onCopyResult(error instanceof Error ? error.message : "Failed to copy image.", true);
}
}
const menuItem = (label, icon, onClick, disabled = false, tone = "default", onPrepare) => (<button className={`viz-card-menu-item ${tone === "danger" ? "viz-card-menu-item-danger" : ""}`.trim()} disabled={disabled} key={label} onFocus={onPrepare} onClick={() => {
void onClick();
closeMenu();
}} onPointerEnter={onPrepare} role="menuitem" type="button">
<span aria-hidden="true" className="viz-card-menu-icon">
{icon}
</span>
<span>{label}</span>
</button>);
return (<section className={`panel chart-panel viz-card ${accessIssue ? "has-permission-issue" : ""}`} id={chart.id} ref={cardRef}>
<PanelHeader action={<div className="viz-card-actions" data-image-export-exclude="true" ref={menuRef}>
<button aria-expanded={isMenuOpen} aria-label={`Open options for ${displayChart.title}`} className="viz-card-menu-button viz-card__no-drag" onClick={(event) => {
event.stopPropagation();
const nextIsMenuOpen = toggleMenu();
if (nextIsMenuOpen) {
prepareImageExportQuietly(true);
}
else {
resetPreparedImageExport();
}
}} onFocus={() => prepareImageExportQuietly()} onKeyDown={handleMenuButtonKeyDown} onPointerEnter={() => prepareImageExportQuietly()} ref={menuButtonRef} type="button">
<Ellipsis aria-hidden="true" size={18} strokeWidth={2}/>
</button>
{shouldRenderMenu ? (<div className={`viz-card-menu viz-card__no-drag menu-surface ${menuMotionClass}`} onKeyDown={handleMenuKeyDown} role="menu" style={fixedMenuStyle}>
{menuItem("Edit chart", <ChartNoAxesCombined size={18} strokeWidth={2}/>, () => onModalOpen({ chart: displayChart, kind: "fullscreen" }))}
{menuItem("View data source", <Database size={18} strokeWidth={2}/>, () => onModalOpen({ chart: displayChart, kind: "source" }))}
{shouldOfferImageClipboardCopy()
? menuItem("Copy as image", <Camera size={18} strokeWidth={2}/>, handleCopyAsImage, Boolean(accessIssue) ||
imageExportState.status === "loading" ||
preparedImageExportStatus === "pending", "default", prepareImageExportQuietly)
: null}
{onDeleteBlock ? menuItem("Delete", <Trash2 size={18} strokeWidth={2}/>, onDeleteBlock, false, "danger") : null}
</div>) : null}
</div>} subtitle={displayChart.subtitle} title={displayChart.title} titleRowClassName="viz-card__drag-handle">
<RichMarkdown ariaLabel={`Edit markdown header for ${chart.title}`} className="editable-cell-header" isEditMode={isEditMode} markdown={displayHeaderMarkdown} onMarkdownChange={(nextMarkdown) => onTextChange(chart.id, { headerMarkdown: nextMarkdown })} onRequestEditMode={onRequestEditMode} placeholder={composeChartHeaderMarkdown(chart)} variant="cellHeader"/>
</PanelHeader>
{children}
</section>);
}
function AccessIssueStrip({ issues }) {
if (!issues.length)
return null;
return (<section className="access-issue-strip" aria-label="Data access issues">
<div>
<strong>{issues.length === 1 ? "Data access blocker" : "Data access blockers"}</strong>
<p>Some report data could not load because the source query could not complete.</p>
</div>
<ul>
{issues.map((issue) => (<li key={issue.id}>
<span>{issue.scope ?? issue.dataset ?? issue.sourceId ?? issue.id}</span>
<span>{issue.message}</span>
{issue.actionHref ? (<a href={issue.actionHref} rel="noreferrer" target="_blank">
{issue.actionLabel ?? "Request access"}
</a>) : null}
</li>))}
</ul>
</section>);
}
const SQL_KEYWORDS = new Set([
"and",
"as",
"asc",
"by",
"case",
"desc",
"distinct",
"else",
"end",
"from",
"group",
"in",
"is",
"join",
"left",
"like",
"max",
"min",
"not",
"null",
"on",
"or",
"order",
"over",
"partition",
"right",
"select",
"sum",
"then",
"when",
"where",
"with"
]);
const SQL_FUNCTIONS = new Set([
"avg",
"cast",
"coalesce",
"concat",
"count",
"current_date",
"date_trunc",
"dateadd",
"date_add",
"round",
"nullif"
]);
const SQL_TOKEN_PATTERN = /(--[^\n]*|'(?:''|[^'])*'|<>|!=|<=|>=|\b\d+(?:\.\d+)?\b|\b[a-zA-Z_][a-zA-Z0-9_]*\b|[(),.;=*+\-/%<>])/g;
const SQL_FORMAT_LINE_STARTERS = new Set([
"from",
"group",
"having",
"limit",
"order",
"select",
"union",
"where",
"with"
]);
const SQL_JOIN_MODIFIERS = new Set([
"cross",
"full",
"inner",
"join",
"left",
"outer",
"right"
]);
function sqlFormatTokens(sql) {
const tokens = [];
let cursor = 0;
for (const match of sql.matchAll(SQL_TOKEN_PATTERN)) {
const token = match[0];
const index = match.index ?? 0;
const rawGap = sql.slice(cursor, index).trim();
if (rawGap)
tokens.push(...rawGap.split(/\s+/));
tokens.push(token);
cursor = index + token.length;
}
const tail = sql.slice(cursor).trim();
if (tail)
tokens.push(...tail.split(/\s+/));
return tokens;
}
function isSqlWord(token) {
return /^[a-zA-Z_][a-zA-Z0-9_]*$/.test(token);
}
function formatSqlForDisplay(sql) {
const tokens = sqlFormatTokens(sql.trim());
if (!tokens.length)
return "";
const lines = [];
let current = "";
let indent = 0;
const contextStack = [];
let previousToken = "";
function currentIndent(level = indent) {
return "  ".repeat(Math.max(0, level));
}
function pushLine(nextIndent = indent) {
const text = current.trimEnd();
if (text.trim())
lines.push(text);
current = currentIndent(nextIndent);
}
function append(token, { tight = false } = {}) {
if (!current)
current = currentIndent();
const trimmed = current.trimEnd();
const needsSpace = !tight &&
trimmed &&
!trimmed.endsWith("(") &&
!trimmed.endsWith(".") &&
token !== "." &&
token !== "," &&
token !== ")" &&
token !== ";";
current = `${trimmed}${needsSpace ? " " : ""}${token}`;
previousToken = token;
}
for (let index = 0; index < tokens.length; index += 1) {
const token = tokens[index];
const lower = token.toLowerCase();
const previousLower = previousToken.toLowerCase();
const nextLower = tokens[index + 1]?.toLowerCase?.() ?? "";
if (token.startsWith("--")) {
if (current.trim())
pushLine();
append(token);
pushLine();
continue;
}
if (SQL_FORMAT_LINE_STARTERS.has(lower)) {
if (current.trim() && !current.trimEnd().endsWith("("))
pushLine();
append(lower.toUpperCase());
continue;
}
if (SQL_JOIN_MODIFIERS.has(lower)) {
if (!(lower === "join" && SQL_JOIN_MODIFIERS.has(previousLower)) && current.trim())
pushLine();
append(lower.toUpperCase());
continue;
}
if (token === "(") {
const functionCall = SQL_FUNCTIONS.has(previousLower) ||
(isSqlWord(previousToken) && !SQL_KEYWORDS.has(previousLower) && previousLower !== "as");
append(token, { tight: functionCall });
contextStack.push(functionCall ? "function" : "group");
if (!functionCall && (nextLower === "select" || previousLower === "as")) {
indent += 1;
pushLine();
}
else if (!functionCall) {
indent += 1;
}
continue;
}
if (token === ")") {
const context = contextStack.pop();
const nextIndent = Math.max(0, indent - 1);
if (context !== "function" && current.trim() && current.trim() !== currentIndent().trim())
pushLine(nextIndent);
indent = nextIndent;
append(token, { tight: true });
continue;
}
if (token === ",") {
append(token, { tight: true });
if (contextStack[contextStack.length - 1] !== "function")
pushLine();
continue;
}
if (token === ".") {
append(token, { tight: true });
continue;
}
if (token === ";") {
append(token, { tight: true });
pushLine();
continue;
}
append(SQL_KEYWORDS.has(lower) || SQL_FUNCTIONS.has(lower) ? lower.toUpperCase() : token);
}
if (current.trim())
pushLine();
return lines.join("\n");
}
function highlightSql(sql) {
const nodes = [];
let cursor = 0;
for (const match of sql.matchAll(SQL_TOKEN_PATTERN)) {
const token = match[0];
const index = match.index ?? 0;
if (index > cursor) {
nodes.push(sql.slice(cursor, index));
}
const lower = token.toLowerCase();
let className = "sql-token";
if (token.startsWith("--")) {
className += " comment";
}
else if (token.startsWith("'")) {
className += " string";
}
else if (/^\d/.test(token)) {
className += " number";
}
else if (SQL_KEYWORDS.has(lower)) {
className += " keyword";
}
else if (SQL_FUNCTIONS.has(lower)) {
className += " function";
}
else if (/^[(),.;=*+\-/%]$/.test(token)) {
className += " punctuation";
}
else {
className += " identifier";
}
nodes.push(<span className={className} key={`${index}-${token}`}>
{token}
</span>);
cursor = index + token.length;
}
if (cursor < sql.length) {
nodes.push(sql.slice(cursor));
}
return nodes;
}
const SOURCE_FETCH_TIMEOUT_MS = 10000;
function DataSourceDetails({ children, details, source, sourceQuery }) {
return (<div className="source-modal-sections">
<section className="source-modal-section">
<h3>Details</h3>
<dl className="details-grid source-details-grid">
<div>
<dt>Dataset</dt>
<dd>{details.dataset}</dd>
</div>
<div>
<dt>Tables used</dt>
<dd>{detailList(details.tables)}</dd>
</div>
<div>
<dt>Filters</dt>
<dd>{detailText(details.filters)}</dd>
</div>
<div>
<dt>Metric definitions</dt>
<dd>{detailList(details.metricDefinitions)}</dd>
</div>
<div>
<dt>Snapshot</dt>
<dd>{formatDate(details.snapshot)}</dd>
</div>
</dl>
</section>
<section className="source-modal-section">
<h3>Source query</h3>
<SourceQueryBlock source={source} sourceQuery={sourceQuery}/>
</section>
<section className="source-modal-section">
<h3>Data table</h3>
{children}
</section>
</div>);
}
function SourceQueryBlock({ source, sourceQuery }) {
const [sourceContent, setSourceContent] = useState({ status: "idle" });
const [copyStatus, setCopyStatus] = useState("idle");
const codeRef = useRef(null);
const inlineSourceText = queryTextFromSourceQuery(sourceQueryFromSourceSpec(source)) || queryTextFromSourceQuery(sourceQuery) || "";
const displaySourceText = sourceContent.status === "loaded" ? formatSqlForDisplay(sourceContent.text) : "";
useEffect(() => {
if (inlineSourceText) {
setSourceContent({ status: "loaded", text: inlineSourceText });
return;
}
if (!source?.path) {
setSourceContent({ status: "idle" });
return;
}
let cancelled = false;
const controller = new AbortController();
const timeout = window.setTimeout(() => controller.abort(), SOURCE_FETCH_TIMEOUT_MS);
setSourceContent({ status: "loading" });
fetch(`/api/source-file?path=${encodeURIComponent(source.path)}`, {
cache: "no-store",
signal: controller.signal
})
.then(async (response) => {
const text = await response.text();
if (!response.ok)
throw new Error(text || `Request failed: ${response.status}`);
return text;
})
.then((text) => {
if (!cancelled)
setSourceContent({ status: "loaded", text });
})
.catch((error) => {
if (!cancelled) {
const isAbort = error instanceof Error && error.name === "AbortError";
setSourceContent({
error: isAbort
? "Source request timed out. Refresh the app and try again."
: error instanceof Error
? error.message
: "Failed to load source",
status: "error"
});
}
})
.finally(() => {
window.clearTimeout(timeout);
});
return () => {
cancelled = true;
window.clearTimeout(timeout);
controller.abort();
};
}, [inlineSourceText, source?.path]);
useEffect(() => {
if (copyStatus === "idle")
return;
const timeout = window.setTimeout(() => setCopyStatus("idle"), 1800);
return () => window.clearTimeout(timeout);
}, [copyStatus]);
async function handleCopyQuery(text) {
try {
await copyTextToClipboard(text);
setCopyStatus("copied");
}
catch {
setCopyStatus("blocked");
}
}
if (sourceContent.status === "loading")
return <>Loading source...</>;
if (sourceContent.status === "error") {
return <span className="source-error">{sourceContent.error}</span>;
}
if (sourceContent.status === "loaded") {
return (<div className="source-query-shell">
{source?.path || source?.href || source?.label || sourceQuery?.id || sourceQuery?.engine ? (<div className="source-query-meta">
<span>
{source?.href ? (<a href={source.href} rel="noreferrer" target="_blank">
{source.path ?? source.label}
</a>) : (source?.path ?? source?.label ?? sourceQuery?.id ?? sourceQuery?.engine)}
</span>
<button className="source-query-copy" onClick={() => void handleCopyQuery(displaySourceText || sourceContent.text)} type="button">
<Copy aria-hidden="true" size={14} strokeWidth={2}/>
{copyStatus === "copied"
? "Copied"
: copyStatus === "blocked"
? "Copy failed"
: "Copy query"}
</button>
</div>) : null}
<pre className="source-query">
<code ref={codeRef}>{highlightSql(displaySourceText || sourceContent.text)}</code>
</pre>
</div>);
}
return <>No source query file mapped.</>;
}
function useModalScrollLock(enabled) {
useEffect(() => {
if (!enabled)
return undefined;
const previousOverflow = document.body.style.overflow;
const previousOverscrollBehavior = document.body.style.overscrollBehavior;
document.body.style.overflow = "hidden";
document.body.style.overscrollBehavior = "none";
return () => {
document.body.style.overflow = previousOverflow;
document.body.style.overscrollBehavior = previousOverscrollBehavior;
};
}, [enabled]);
}
function sourcePreviewColumns(rows, columns = []) {
if (columns.length)
return columns;
const fields = [];
const seen = new Set();
for (const row of rows) {
for (const field of Object.keys(row)) {
if (!seen.has(field)) {
seen.add(field);
fields.push(field);
}
}
}
return fields.map((field) => ({ field, label: field }));
}
function SourceDataTable({ columns = [], dataset, density = "dense", rows = [] }) {
const previewRows = useMemo(() => asArray(rows).filter((row) => row && typeof row === "object"), [rows]);
const previewDataset = dataset ?? "__source_preview_rows";
const table = useMemo(() => ({
columns: sourcePreviewColumns(previewRows, columns),
dataset: previewDataset,
id: `source-preview-${previewDataset}`
}), [columns, previewDataset, previewRows]);
const snapshot = useMemo(() => ({ datasets: { [previewDataset]: previewRows } }), [previewDataset, previewRows]);
const [columnWidths, setColumnWidths] = useState({});
useEffect(() => {
setColumnWidths({});
}, [table.id]);
return (<div className="source-data-table">
<TableContent allowColumnResize={false} columnWidths={columnWidths} density={density} filters={EMPTY_FILTERS} onColumnWidthsChange={(_tableId, nextWidths) => setColumnWidths(nextWidths)} selectedFilters={{}} snapshot={snapshot} table={table}/>
</div>);
}
function querySourceForChart(chart, sources) {
const directSource = sourceForChart(chart, sources);
return (directSource ??
sources.find((source) => {
const label = source.label?.toLowerCase() ?? "";
const path = source.path?.toLowerCase() ?? "";
return path.endsWith(".sql") || label.includes("sql") || label.includes("quer");
}) ??
null);
}
function chartMetricsForBuildDetails(chart) {
const metrics = [];
const seen = new Set();
function addMetric(field, label) {
if (!field || seen.has(field))
return;
seen.add(field);
metrics.push({ field, label: label || field });
}
addMetric(chart.encodings?.y?.field, chart.encodings?.y?.label);
for (const field of chart.encodings?.y?.fields ?? []) {
addMetric(field, field);
}
return metrics;
}
function ChartSourceModalDialog({ activeFilters, chart, manifest, onClose, rows = [], snapshot }) {
const dialogRef = useRef(null);
const source = querySourceForChart(chart, manifest?.sources ?? []);
const sourceQuery = sourceQueryFromSourceSpec(source);
const buildDetails = sourceBuildDetails({
activeFilters,
dataset: chart.dataset,
metrics: chartMetricsForBuildDetails(chart),
source,
sourceQuery,
snapshot
});
useModalScrollLock(true);
useEffect(() => {
const dialog = dialogRef.current;
if (dialog && !dialog.open) {
dialog.showModal();
}
}, []);
return (<dialog aria-labelledby="chart-source-modal-title" className="native-modal source-modal" onCancel={onClose} onClick={(event) => {
if (event.target === event.currentTarget) {
event.currentTarget.close();
}
}} onClose={onClose} ref={dialogRef}>
<section className="modal-panel source-modal-panel">
<div className="modal-header">
<div>
<h2 id="chart-source-modal-title">Data source</h2>
<p>{chart.title}</p>
</div>
<button aria-label="Close data source" className="modal-close-button" onClick={() => dialogRef.current?.close()} type="button">
<X aria-hidden="true" size={20} strokeWidth={2}/>
</button>
</div>
<DataSourceDetails details={buildDetails} source={source} sourceQuery={sourceQuery}>
<SourceDataTable dataset={chart.dataset} rows={rows}/>
</DataSourceDetails>
</section>
</dialog>);
}
function safeScriptJson(value) {
return JSON.stringify(value).replace(/</g, "\\u003c");
}
function chartWidgetDetailHtml(html, widgetInstanceId) {
const bridge = `<script>
window.openai = {
...(window.openai || {}),
availableDisplayModes: ["modal"],
displayMode: "modal",
widgetInstanceId: ${safeScriptJson(widgetInstanceId)},
requestDisplayMode(request) {
const mode = typeof request === "string" ? request : request && request.mode;
window.parent.postMessage({ type: "datascience-chart-widget-display-mode", mode }, "*");
return Promise.resolve({ mode });
},
sendFollowUpMessage(payload) {
window.parent.postMessage(
{
originUrl: payload && payload.originUrl,
prompt: payload && payload.prompt,
type: "datascience-chart-widget-codex-prompt"
},
"*"
);
return Promise.resolve({ ok: true });
},
openCodexPrompt(payload) {
return this.sendFollowUpMessage(payload);
}
};
</script>`;
return html.includes("</head>") ? html.replace("</head>", `${bridge}</head>`) : `${bridge}${html}`;
}
function shouldUseHostedChartModal(packageInfo) {
return packageInfo?.hostedReadOnly === true || packageInfo?.deliveryMode === "site_creator";
}
function ChartDetailPage({ accessIssue, chart, filters, manifest, onChartSpecChange, onClose, packageInfo, rows, selectedFilters, snapshot }) {
const dialogRef = useRef(null);
const iframeRef = useRef(null);
const pendingPostTimersRef = useRef([]);
const [widgetHtml, setWidgetHtml] = useState(null);
const [widgetError, setWidgetError] = useState(null);
const [sourceQueryText, setSourceQueryText] = useState(null);
const source = querySourceForChart(chart, manifest?.sources ?? []);
const hostedChartModal = shouldUseHostedChartModal(packageInfo);
const widgetInstanceId = `report-chart-detail-${chart.id}`;
const widgetPayload = useMemo(() => chartWidgetPayload(chart, rows, source, snapshot, sourceQueryText), [chart, rows, source, snapshot, sourceQueryText]);
const widgetUrl = useMemo(() => `/api/inline-chart-widget?displayMode=modal&widgetInstanceId=${encodeURIComponent(widgetInstanceId)}`, [widgetInstanceId]);
const clearPendingPostTimers = useCallback(() => {
pendingPostTimersRef.current.forEach((timer) => window.clearTimeout(timer));
pendingPostTimersRef.current = [];
}, []);
const postWidgetPayload = useCallback(() => {
iframeRef.current?.contentWindow?.postMessage({
displayMode: "modal",
payload: widgetPayload,
targetWidgetInstanceId: widgetInstanceId
}, "*");
}, [widgetInstanceId, widgetPayload]);
const scheduleWidgetPayloadPosts = useCallback(() => {
clearPendingPostTimers();
pendingPostTimersRef.current = [0, 50, 150, 350].map((delay) => window.setTimeout(postWidgetPayload, delay));
}, [clearPendingPostTimers, postWidgetPayload]);
useEffect(() => {
const dialog = dialogRef.current;
if (dialog && !dialog.open) {
dialog.showModal();
}
}, []);
useEffect(() => {
let cancelled = false;
if (hostedChartModal) {
setWidgetHtml(null);
setWidgetError(null);
return () => {
cancelled = true;
};
}
setWidgetHtml(null);
setWidgetError(null);
void fetch(widgetUrl)
.then((response) => {
if (!response.ok)
throw new Error(`Shared chart detail failed to load (${response.status}).`);
return response.text();
})
.then((html) => {
if (!cancelled)
setWidgetHtml(chartWidgetDetailHtml(html, widgetInstanceId));
})
.catch((error) => {
if (!cancelled)
setWidgetError(error instanceof Error ? error.message : "Shared chart detail failed to load.");
});
return () => {
cancelled = true;
};
}, [hostedChartModal, widgetInstanceId, widgetUrl]);
useEffect(() => {
let cancelled = false;
if (hostedChartModal) {
setSourceQueryText(null);
return () => {
cancelled = true;
};
}
const inlineSourceText = queryTextFromSourceQuery(sourceQueryFromSourceSpec(source));
if (inlineSourceText) {
setSourceQueryText(inlineSourceText);
return () => {
cancelled = true;
};
}
if (!source?.path) {
setSourceQueryText(null);
return () => {
cancelled = true;
};
}
setSourceQueryText(null);
void fetch(`/api/source-file?path=${encodeURIComponent(source.path)}`, {
headers: { Accept: "text/plain" }
})
.then((response) => {
if (!response.ok)
return "";
return response.text();
})
.then((text) => {
if (!cancelled)
setSourceQueryText(text.trim() || null);
})
.catch(() => {
if (!cancelled)
setSourceQueryText(null);
});
return () => {
cancelled = true;
};
}, [hostedChartModal, source?.path, source?.query?.query]);
useEffect(() => {
if (hostedChartModal || !widgetHtml)
return;
scheduleWidgetPayloadPosts();
}, [hostedChartModal, scheduleWidgetPayloadPosts, widgetHtml]);
useEffect(() => clearPendingPostTimers, [clearPendingPostTimers]);
useEffect(() => {
if (hostedChartModal)
return undefined;
function handleWidgetMessage(event) {
const data = event.data;
if (!data || typeof data !== "object")
return;
if (data.type === "datascience-chart-widget-display-mode" && data.mode === "inline") {
onClose();
}
if (data.type === "datascience-chart-widget-spec-reset" && data.widgetInstanceId === widgetInstanceId) {
onChartSpecChange(chart.id, null);
}
if (data.type === "datascience-chart-widget-spec-change" && data.widgetInstanceId === widgetInstanceId) {
onChartSpecChange(chart.id, data.visualization_spec);
}
if (data.type === "datascience-chart-widget-codex-prompt" && typeof data.prompt === "string") {
sendCodexPromptToHost(data.prompt, null);
}
}
window.addEventListener("message", handleWidgetMessage);
return () => window.removeEventListener("message", handleWidgetMessage);
}, [chart.id, hostedChartModal, onChartSpecChange, onClose, widgetInstanceId]);
return (<dialog aria-label={`Edit ${chart.title}`} className={`native-modal chart-explore-modal ${hostedChartModal ? "chart-hosted-explore-modal" : ""}`.trim()} onCancel={onClose} onClick={(event) => {
if (event.target === event.currentTarget) {
event.currentTarget.close();
}
}} onClose={onClose} ref={dialogRef}>
<section className={`modal-panel chart-explore-panel ${hostedChartModal ? "chart-hosted-explore-panel" : ""}`.trim()}>
<section aria-label={`Edit ${chart.title}`} className={`chart-detail-page unified-chart-detail-page chart-explore-body ${hostedChartModal ? "chart-hosted-explore-body" : ""}`.trim()}>
{hostedChartModal ? (<ChartBody accessIssue={accessIssue} chart={chart} filters={filters} isFullscreen selectedFilters={selectedFilters} snapshot={snapshot}/>) : null}
{!hostedChartModal && !widgetHtml && !widgetError ? <div className="chart-detail-loading">Loading chart detail...</div> : null}
{widgetError ? <div className="empty-state error-state">{widgetError}</div> : null}
{!hostedChartModal ? (<iframe className="unified-chart-detail-frame" hidden={!widgetHtml || Boolean(widgetError)} onLoad={scheduleWidgetPayloadPosts} ref={iframeRef} srcDoc={widgetHtml ?? ""} title={`Edit ${chart.title}`}/>) : null}
</section>
</section>
</dialog>);
}
function chartWidgetColumnType(column, value) {
if (column?.type === "date")
return "date";
if (column?.format || column?.type === "currency" || column?.type === "number" || column?.type === "percent")
return "number";
if (typeof value === "number")
return "number";
if (typeof value === "string" && /^\d{4}-\d{2}(?:-\d{2})?(?:$|[T\s])/.test(value))
return "date";
return "text";
}
function chartWidgetEncodingColumn(chart, role, rows) {
const field = chartEncodingField(chart, role);
if (!field)
return null;
const encoding = chartEncoding(chart, role);
return {
key: field,
label: chartEncodingLabel(chart, role, field),
type: encoding.type === "temporal" ? "date" : encoding.type === "quantitative" ? "number" : chartWidgetColumnType(encoding, rows[0]?.[field]),
unit: encoding.unit
};
}
function chartWidgetSource(source, sourceQuery, queryText, snapshot) {
return {
id: source?.id,
label: source?.label,
path: source?.path,
href: source?.href,
query: {
engine: sourceQuery?.engine ?? source?.label ?? "report manifest",
executed_at: sourceQuery?.executed_at ?? snapshot?.generatedAt,
id: sourceQuery?.id ?? source?.path ?? source?.href,
url: sourceQuery?.url,
sql: queryText || "",
description: sourceQuery?.description,
language: sourceQuery?.language ?? (source?.path?.toLowerCase().endsWith(".sql") ? "SQL" : undefined),
tables_used: sourceQuery?.tables_used,
filters: sourceQuery?.filters,
metric_definitions: sourceQuery?.metric_definitions
}
};
}
function chartWidgetPayloadFromEncodings(chart, rows, source, snapshot, sourceQueryText) {
const xField = chartEncodingField(chart, "x");
const yField = chartEncodingField(chart, "y");
const yFields = chartEncodingFields(chart, "y");
const colorField = chartEncodingField(chart, "color");
const chartSourceQuery = sourceQueryFromChartSpec(chart);
const sourceSpecQuery = sourceQueryFromSourceSpec(source);
const sourceQuery = chartSourceQuery ?? sourceSpecQuery;
const queryText = queryTextFromSourceQuery(chartSourceQuery) ||
queryTextFromSourceQuery(sourceSpecQuery) ||
sourceQueryText?.trim();
const unit = chart.unit ?? chartEncoding(chart, "y").unit ?? (chart.valueFormat === "currency" ? "USD" : chart.valueFormat === "percent" ? "%" : undefined);
const settings = chartWidgetSettings(chart);
if (xField && yField) {
const columns = [
chartWidgetEncodingColumn(chart, "x", rows),
colorField ? chartWidgetEncodingColumn(chart, "color", rows) : null,
chartWidgetEncodingColumn(chart, "y", rows)
].filter(Boolean);
return {
ok: true,
widget_type: "chart",
title: chart.title,
subtitle: chart.showDescription ? chart.subtitle : undefined,
source: chartWidgetSource(source, sourceQuery, queryText, snapshot),
result_table: {
columns,
row_count: rows.length,
rows: rows.map((row) => Object.fromEntries(columns.map((column) => [column.key, row[column.key]]))),
truncated: false
},
visualization_spec: {
version: "1",
intent: chart.intent ?? "custom",
visualization_type: chart.type,
encodings: {
x: { field: xField, type: chartEncoding(chart, "x").type ?? "nominal" },
y: { aggregate: chartEncoding(chart, "y").aggregate ?? "sum", field: yField, type: "quantitative", unit },
...(colorField ? { color: { field: colorField, type: chartEncoding(chart, "color").type ?? "nominal" } } : {})
},
presentation: {
show_controls: true,
unit,
view_mode: "both"
},
settings
}
};
}
if (xField && yFields.length) {
const longRows = rows.flatMap((row) => yFields.map((field) => ({
[xField]: row[xField],
series: field,
value: row[field]
})));
return {
ok: true,
widget_type: "chart",
title: chart.title,
subtitle: chart.showDescription ? chart.subtitle : undefined,
source: chartWidgetSource(source, sourceQuery, queryText, snapshot),
result_table: {
columns: [
{ key: xField, label: chartEncodingLabel(chart, "x", xField), type: chartWidgetColumnType(chartEncoding(chart, "x"), rows[0]?.[xField]) },
{ key: "series", label: "Series", type: "text" },
{ key: "value", label: chartEncodingLabel(chart, "y", "Value"), type: "number", unit }
],
row_count: longRows.length,
rows: longRows,
truncated: false
},
visualization_spec: {
version: "1",
intent: chart.intent ?? "custom",
visualization_type: chart.type,
encodings: {
x: { field: xField, type: chartEncoding(chart, "x").type ?? "nominal" },
y: { aggregate: "sum", field: "value", type: "quantitative", unit },
color: { field: "series", type: "nominal" }
},
presentation: {
show_controls: true,
unit,
view_mode: "both"
},
settings
}
};
}
return null;
}
function chartWidgetSettings(chart) {
const source = chart?.settings && typeof chart.settings === "object" && !Array.isArray(chart.settings) ? chart.settings : {};
const type = chart?.type;
const orientation = source.orientation === "horizontal" || type === "horizontalBar" || type === "horizontalStackedBar" || type === "horizontalStackedBar100"
? "horizontal"
: source.orientation === "vertical"
? "vertical"
: undefined;
const groupMode = source.groupMode ?? source.group_mode ?? (type === "stackedBar100" || type === "horizontalStackedBar100"
? "stacked100"
: type === "stackedBar" || type === "horizontalStackedBar"
? "stacked"
: undefined);
return {
...(orientation ? { orientation } : {}),
...(["grouped", "stacked", "stacked100"].includes(groupMode) ? { group_mode: groupMode } : {})
};
}
function chartWidgetPayload(chart, rows, source, snapshot, sourceQueryText) {
const encodedPayload = chartHasEncodingSpec(chart) ? chartWidgetPayloadFromEncodings(chart, rows, source, snapshot, sourceQueryText) : null;
if (encodedPayload)
return encodedPayload;
return null;
}
function TableContent({ allowColumnResize = true, columnWidths, density, filters, onColumnWidthsChange, selectedFilters, snapshot, table, isFullscreen = false }) {
const rows = filterRowsForDataset(getRows(snapshot, table.dataset), table.dataset, filters, selectedFilters, table.columns.map((column) => column.field));
const [page, setPage] = useState(0);
const [sortState, setSortState] = useState(null);
const [isColumnResizing, setIsColumnResizing] = useState(false);
const headerCellRefs = useRef({});
const tableWrapRef = useRef(null);
const sortedRows = useMemo(() => {
if (!sortState)
return rows;
return [...rows].sort((a, b) => compareTableValues(a, b, sortState.field, sortState.direction));
}, [rows, sortState]);
const pageSize = isFullscreen ? Math.max(1, sortedRows.length) : TABLE_CARD_PAGE_SIZE;
const totalPages = Math.max(1, Math.ceil(sortedRows.length / pageSize));
const currentPage = Math.min(page, totalPages - 1);
const shouldShowPagination = rows.length > 0 && !isFullscreen && totalPages > 1;
const shouldShowCount = rows.length > 0 && shouldShowPagination;
const shouldShowFooter = shouldShowCount || shouldShowPagination;
const resultCountLabel = `${sortedRows.length.toLocaleString()} ${sortedRows.length === 1 ? "result" : "results"}`;
const visibleRows = isFullscreen
? sortedRows
: sortedRows.slice(currentPage * pageSize, currentPage * pageSize + pageSize);
const estimatedColumnWidths = useMemo(() => estimateTableColumnWidths(table, rows, density), [density, rows, table]);
const activeColumnWidths = useMemo(() => {
return Object.fromEntries(table.columns.map((column) => [
column.field,
clamp(Math.round(columnWidths[column.field] ?? estimatedColumnWidths[column.field] ?? TABLE_COLUMN_DEFAULT_WIDTH), TABLE_COLUMN_MIN_WIDTH, TABLE_COLUMN_MAX_WIDTH)
]));
}, [columnWidths, estimatedColumnWidths, table.columns]);
const tablePixelWidth = table.columns.reduce((total, column) => total + activeColumnWidths[column.field], 0);
const tableStyle = {
minWidth: `${tablePixelWidth}px`,
tableLayout: "fixed",
width: `${tablePixelWidth}px`
};
useEffect(() => {
setPage(0);
}, [isFullscreen, rows.length, sortState]);
useLayoutEffect(() => {
if (tableWrapRef.current) {
tableWrapRef.current.scrollLeft = 0;
}
}, [isFullscreen, rows.length, table.id]);
function toggleSort(field) {
setSortState((current) => {
if (current?.field !== field)
return { direction: "asc", field };
return { direction: current.direction === "asc" ? "desc" : "asc", field };
});
}
function measuredColumnWidths() {
return Object.fromEntries(table.columns.map((column) => {
const measuredWidth = headerCellRefs.current[column.field]?.getBoundingClientRect().width;
const width = measuredWidth ?? activeColumnWidths[column.field] ?? TABLE_COLUMN_DEFAULT_WIDTH;
return [
column.field,
clamp(Math.round(width), TABLE_COLUMN_MIN_WIDTH, TABLE_COLUMN_MAX_WIDTH)
];
}));
}
function resizeColumnBy(field, delta, shouldPersist) {
const baseWidths = { ...activeColumnWidths, ...measuredColumnWidths(), ...columnWidths };
const currentWidth = baseWidths[field] ?? TABLE_COLUMN_DEFAULT_WIDTH;
onColumnWidthsChange(table.id, {
...baseWidths,
[field]: clamp(Math.round(currentWidth + delta), TABLE_COLUMN_MIN_WIDTH, TABLE_COLUMN_MAX_WIDTH)
}, { persist: shouldPersist });
}
function startColumnResize(event, field) {
event.preventDefault();
event.stopPropagation();
const baseWidths = { ...activeColumnWidths, ...measuredColumnWidths(), ...columnWidths };
const startWidth = baseWidths[field] ?? TABLE_COLUMN_DEFAULT_WIDTH;
const startX = event.clientX;
let latestWidths = baseWidths;
onColumnWidthsChange(table.id, baseWidths, { persist: false });
setIsColumnResizing(true);
document.body.style.cursor = "col-resize";
document.body.style.userSelect = "none";
function handlePointerMove(moveEvent) {
const nextWidth = clamp(Math.round(startWidth + moveEvent.clientX - startX), TABLE_COLUMN_MIN_WIDTH, TABLE_COLUMN_MAX_WIDTH);
latestWidths = { ...baseWidths, [field]: nextWidth };
onColumnWidthsChange(table.id, latestWidths, { persist: false });
}
function finishResize() {
window.removeEventListener("pointermove", handlePointerMove);
window.removeEventListener("pointerup", finishResize);
window.removeEventListener("pointercancel", finishResize);
document.body.style.cursor = "";
document.body.style.userSelect = "";
setIsColumnResizing(false);
onColumnWidthsChange(table.id, latestWidths, { persist: true });
}
window.addEventListener("pointermove", handlePointerMove);
window.addEventListener("pointerup", finishResize);
window.addEventListener("pointercancel", finishResize);
}
function handleResizeHandleKeyDown(event, field) {
if (event.key !== "ArrowLeft" && event.key !== "ArrowRight")
return;
event.preventDefault();
event.stopPropagation();
resizeColumnBy(field, event.key === "ArrowRight" ? TABLE_COLUMN_KEYBOARD_STEP : -TABLE_COLUMN_KEYBOARD_STEP, true);
}
return (<>
{rows.length ? (<div className={`table-wrap table-density-${density} ${isFullscreen ? "fullscreen" : ""}`} ref={tableWrapRef}>
<div className="table-scroll-content">
<table className={`data-table data-table-${density} data-table-resizable ${isColumnResizing ? "is-column-resizing" : ""}`} style={tableStyle}>
<colgroup>
{table.columns.map((column) => (<col key={column.field} style={{ width: `${activeColumnWidths[column.field]}px` }}/>))}
</colgroup>
<thead>
<tr>
{table.columns.map((column) => {
const isSorted = sortState?.field === column.field;
const format = tableColumnFormat(column);
const isNumericColumn = isNumericTableColumn(column, rows);
const isCenteredColumn = column.align === "center";
const SortIcon = isSorted ? (sortState.direction === "asc" ? ArrowUp : ArrowDown) : null;
return (<th aria-sort={isSorted
? sortState.direction === "asc"
? "ascending"
: "descending"
: "none"} key={column.field} ref={(element) => {
headerCellRefs.current[column.field] = element;
}} className={isNumericColumn ? "table-header-number" : isCenteredColumn ? "center" : undefined} style={{ width: `${activeColumnWidths[column.field]}px` }}>
<button className="table-sort-button" onClick={() => toggleSort(column.field)} type="button">
<span>{column.label}</span>
{SortIcon ? <SortIcon aria-hidden="true" size={14} strokeWidth={2}/> : null}
</button>
{allowColumnResize ? (<button aria-label={`Resize ${column.label} column`} className="table-column-resize-handle" onKeyDown={(event) => handleResizeHandleKeyDown(event, column.field)} onPointerDown={(event) => startColumnResize(event, column.field)} title={`Resize ${column.label} column`} type="button"/>) : null}
</th>);
})}
</tr>
</thead>
<tbody>
{visibleRows.map((row, rowIndex) => (<tr key={`${currentPage}-${rowIndex}`}>
{table.columns.map((column) => {
const value = row[column.field];
const format = tableColumnFormat(column);
const isNumericColumn = isNumericTableColumn(column, rows);
const isCenteredColumn = column.align === "center";
const className = [
isNumericColumn ? "table-cell-number" : "",
isCenteredColumn ? "center" : "",
tableCellMovementClass(column, value)
].filter(Boolean).join(" ") || undefined;
return (<td className={className} key={column.field}>
{formatTableCellValue(column, value)}
</td>);
})}
</tr>))}
</tbody>
</table>
</div>
</div>) : (<div className="empty-state">No rows match the selected filters.</div>)}
{shouldShowFooter ? (<div className="table-pagination">
{shouldShowCount ? <span className="table-result-count">{resultCountLabel}</span> : null}
{shouldShowPagination ? (<div className="table-page-control">
<span>
Page {currentPage + 1} of {totalPages}
</span>
<div className="table-page-buttons">
<button aria-label="Previous page" className="table-arrow-button" disabled={currentPage === 0} onClick={() => setPage((nextPage) => Math.max(0, nextPage - 1))} type="button">
<ChevronLeft aria-hidden="true" size={16} strokeWidth={2}/>
</button>
<button aria-label="Next page" className="table-arrow-button" disabled={currentPage >= totalPages - 1} onClick={() => setPage((nextPage) => Math.min(totalPages - 1, nextPage + 1))} type="button">
<ChevronRight aria-hidden="true" size={16} strokeWidth={2}/>
</button>
</div>
</div>) : null}
</div>) : null}
</>);
}
function DataTable({ columnWidths, filters, isEditMode, isMenuOpen, layout, manifest, onColumnWidthsChange, onDeleteBlock, onMenuOpenChange, onModalOpen, onRequestEditMode, onTextChange, selectedFilters, snapshot, table, textOverride }) {
const tableDensity = table.density ?? (manifest?.surface === "report" ? "spacious" : "dense");
const displayHeaderMarkdown = textOverride?.headerMarkdown ?? composeTableHeaderMarkdown(table);
const displayTitle = markdownFirstLine(displayHeaderMarkdown, table.title);
const { closeMenu, fixedMenuStyle, handleMenuButtonKeyDown, handleMenuKeyDown, menuButtonRef, menuMotionClass, menuRef, toggleMenu, shouldRenderMenu } = useDashboardMenu(isMenuOpen, onMenuOpenChange);
const menuItem = (label, icon, onClick, tone = "default") => (<button className={`viz-card-menu-item ${tone === "danger" ? "viz-card-menu-item-danger" : ""}`.trim()} key={label} onClick={() => {
onClick();
closeMenu();
}} role="menuitem" type="button">
<span aria-hidden="true" className="viz-card-menu-icon">
{icon}
</span>
<span>{label}</span>
</button>);
return (<section className={`panel table-panel table-card ${layout === "half" ? "" : "layout-full"}`}>
<PanelHeader action={<div className="viz-card-actions" data-image-export-exclude="true" ref={menuRef}>
<button aria-expanded={isMenuOpen} aria-label={`Open options for ${table.title}`} className="viz-card-menu-button viz-card__no-drag" onClick={(event) => {
event.stopPropagation();
toggleMenu();
}} onKeyDown={handleMenuButtonKeyDown} ref={menuButtonRef} type="button">
<Ellipsis aria-hidden="true" size={18} strokeWidth={2}/>
</button>
{shouldRenderMenu ? (<div className={`viz-card-menu menu-surface ${menuMotionClass}`} onKeyDown={handleMenuKeyDown} role="menu" style={fixedMenuStyle}>
{menuItem("View data source", <Database size={18} strokeWidth={2}/>, () => onModalOpen({ kind: "source", table }))}
{menuItem("View fullscreen", <Expand size={18} strokeWidth={2}/>, () => onModalOpen({ kind: "fullscreen", table }))}
{onDeleteBlock ? menuItem("Delete", <Trash2 size={18} strokeWidth={2}/>, onDeleteBlock, "danger") : null}
</div>) : null}
</div>} subtitle={table.subtitle} title={displayTitle} titleRowClassName="table-card__drag-handle">
<RichMarkdown ariaLabel={`Edit markdown header for ${table.title}`} className="editable-cell-header" isEditMode={isEditMode} markdown={displayHeaderMarkdown} onMarkdownChange={(nextMarkdown) => onTextChange(table.id, { headerMarkdown: nextMarkdown })} onRequestEditMode={onRequestEditMode} placeholder={composeTableHeaderMarkdown(table)} variant="cellHeader"/>
</PanelHeader>
<TableContent columnWidths={columnWidths} density={tableDensity} filters={filters} onColumnWidthsChange={onColumnWidthsChange} selectedFilters={selectedFilters} snapshot={snapshot} table={table}/>
</section>);
}
function TableModalDialog({ activeFilters, columnWidths, filters, kind, manifest, onColumnWidthsChange, onClose, selectedFilters, snapshot, table }) {
const dialogRef = useRef(null);
const source = sourceForTable(table, manifest?.sources ?? []);
const title = kind === "fullscreen" ? table.title : "Data source";
const sourceQuery = sourceQueryFromSourceSpec(source);
const previewRows = filterRowsForDataset(getRows(snapshot, table.dataset), table.dataset, filters, selectedFilters, table.columns.map((column) => column.field));
const buildDetails = sourceBuildDetails({
activeFilters,
columns: table.columns,
dataset: table.dataset,
source,
sourceQuery,
snapshot
});
useModalScrollLock(kind === "source");
useEffect(() => {
const dialog = dialogRef.current;
if (dialog && !dialog.open) {
dialog.showModal();
}
}, []);
return (<dialog aria-labelledby="table-modal-title" className={`native-modal ${kind === "source" ? "source-modal" : ""}`.trim()} onCancel={onClose} onClick={(event) => {
if (event.target === event.currentTarget) {
event.currentTarget.close();
}
}} onClose={onClose} ref={dialogRef}>
<section className={`modal-panel ${kind === "source" ? "source-modal-panel" : ""}`.trim()}>
<div className="modal-header">
<div>
<h2 id="table-modal-title">{title}</h2>
{kind === "fullscreen" && source?.label ? <p>{source.label}</p> : null}
</div>
<button aria-label={`Close ${kind === "source" ? "data source" : "fullscreen table"}`} className="modal-close-button" onClick={() => dialogRef.current?.close()} type="button">
<X aria-hidden="true" size={20} strokeWidth={2}/>
</button>
</div>
{kind === "fullscreen" ? (<TableContent columnWidths={columnWidths} density={table.density ?? (manifest?.surface === "report" ? "spacious" : "dense")} filters={filters} isFullscreen onColumnWidthsChange={onColumnWidthsChange} selectedFilters={selectedFilters} snapshot={snapshot} table={table}/>) : (<DataSourceDetails details={buildDetails} source={source} sourceQuery={sourceQuery}>
<SourceDataTable columns={table.columns} dataset={table.dataset} density={table.density ?? (manifest?.surface === "report" ? "spacious" : "dense")} rows={previewRows}/>
</DataSourceDetails>)}
</section>
</dialog>);
}
function ReportTextBlock({ block, isEditMode, isMenuOpen, onCopyResult, onDeleteBlock, onMenuOpenChange, onRequestEditMode, onTextChange, textOverride }) {
const cardRef = useRef(null);
const toneClass = `report-block-${block.type}`;
const blockMarkdown = composeBlockMarkdown(block, textOverride);
const { closeMenu, fixedMenuStyle, handleMenuButtonKeyDown, handleMenuKeyDown, menuButtonRef, menuMotionClass, menuRef, toggleMenu, shouldRenderMenu } = useDashboardMenu(isMenuOpen, onMenuOpenChange);
const { getPreparedImageBlob, preparedImageExportStatus, prepareImageExport, resetPreparedImageExport } = usePreparedImageExport(cardRef);
async function handleCopyMarkdown() {
try {
await copyTextToClipboard(blockMarkdown.trim());
onCopyResult("Copied markdown.");
}
catch (error) {
onCopyResult(error instanceof Error ? error.message : "Failed to copy markdown.", true);
}
}
function prepareImageExportQuietly(force = false) {
if (!shouldOfferImageClipboardCopy())
return;
const prepared = prepareImageExport({ force });
if (prepared)
void prepared.promise.catch(() => undefined);
}
async function handleCopyAsImage() {
if (!cardRef.current)
return;
try {
const copyResult = await copyElementAsImage(cardRef.current, getPreparedImageBlob());
resetPreparedImageExport();
onCopyResult(imageCopySuccessMessage("Copied text block as image.", copyResult));
}
catch (error) {
onCopyResult(error instanceof Error ? error.message : "Failed to copy image.", true);
}
}
const menuItem = (label, icon, onClick, tone = "default", onPrepare, disabled = false) => (<button className={`viz-card-menu-item ${tone === "danger" ? "viz-card-menu-item-danger" : ""}`.trim()} disabled={disabled} key={label} onFocus={onPrepare} onClick={() => {
void onClick();
closeMenu();
}} onPointerEnter={onPrepare} role="menuitem" type="button">
<span aria-hidden="true" className="viz-card-menu-icon">
{icon}
</span>
<span>{label}</span>
</button>);
return (<section className={`panel report-block report-markdown-block ${toneClass}`} id={block.id} ref={cardRef}>
<div className="viz-card-actions" data-image-export-exclude="true" ref={menuRef}>
<button aria-expanded={isMenuOpen} aria-label={`Open options for ${markdownFirstLine(blockMarkdown, "Text block")}`} className="viz-card-menu-button viz-card__no-drag" onClick={(event) => {
event.stopPropagation();
const nextIsMenuOpen = toggleMenu();
if (nextIsMenuOpen) {
prepareImageExportQuietly(true);
}
else {
resetPreparedImageExport();
}
}} onFocus={() => prepareImageExportQuietly()} onKeyDown={handleMenuButtonKeyDown} onPointerEnter={() => prepareImageExportQuietly()} ref={menuButtonRef} type="button">
<Ellipsis aria-hidden="true" size={18} strokeWidth={2}/>
</button>
{shouldRenderMenu ? (<div className={`viz-card-menu viz-card__no-drag menu-surface ${menuMotionClass}`} onKeyDown={handleMenuKeyDown} role="menu" style={fixedMenuStyle}>
{menuItem("Copy markdown", <Copy size={18} strokeWidth={2}/>, handleCopyMarkdown)}
{shouldOfferImageClipboardCopy()
? menuItem("Copy as image", <Camera size={18} strokeWidth={2}/>, handleCopyAsImage, "default", prepareImageExportQuietly, preparedImageExportStatus === "pending")
: null}
{menuItem("Delete", <Trash2 size={18} strokeWidth={2}/>, onDeleteBlock, "danger")}
</div>) : null}
</div>
<div className="report-block-body markdown-body">
<RichMarkdown ariaLabel={`Edit markdown for ${block.type}`} className="report-markdown-editor" isEditMode={isEditMode} markdown={blockMarkdown} minRows={Math.max(2, Math.min(6, blockMarkdown.split(/\r?\n/).length))} onMarkdownChange={(nextMarkdown) => onTextChange(block.id, { bodyMarkdown: nextMarkdown })} onRequestEditMode={onRequestEditMode} placeholder={composeBlockMarkdown(block)} variant="reportBlock"/>
</div>
</section>);
}
function ReportHtmlBlock({ block, htmlOverride, isEditMode, isMenuOpen, onHtmlChange, onCopyResult, onDeleteBlock, onMenuOpenChange }) {
const html = composeBlockHtml(block, htmlOverride);
const title = block.id || "HTML block";
const { closeMenu, fixedMenuStyle, handleMenuButtonKeyDown, handleMenuKeyDown, menuButtonRef, menuMotionClass, menuRef, toggleMenu, shouldRenderMenu } = useDashboardMenu(isMenuOpen, onMenuOpenChange);
const frameRef = useRef(null);
const resizeObserverRef = useRef(null);
const [frameHeight, setFrameHeight] = useState(0);
const updateFrameHeight = useCallback(() => {
const nextHeight = measureHtmlFrameHeight(frameRef.current);
if (nextHeight > 0)
setFrameHeight(nextHeight);
}, []);
const handleFrameLoad = useCallback(() => {
resizeObserverRef.current?.disconnect();
const frameDocument = frameRef.current?.contentDocument;
if (frameDocument && typeof ResizeObserver !== "undefined") {
const observer = new ResizeObserver(updateFrameHeight);
if (frameDocument.documentElement)
observer.observe(frameDocument.documentElement);
if (frameDocument.body)
observer.observe(frameDocument.body);
resizeObserverRef.current = observer;
}
updateFrameHeight();
}, [updateFrameHeight]);
useEffect(() => {
setFrameHeight(0);
}, [html]);
useEffect(() => {
return () => resizeObserverRef.current?.disconnect();
}, []);
async function handleCopyHtml() {
try {
await copyTextToClipboard(html);
onCopyResult("Copied HTML.");
}
catch (error) {
onCopyResult(error instanceof Error ? error.message : "Failed to copy HTML.", true);
}
}
const menuItem = (label, icon, onClick, tone = "default") => (<button className={`viz-card-menu-item ${tone === "danger" ? "viz-card-menu-item-danger" : ""}`.trim()} key={label} onClick={() => {
void onClick();
closeMenu();
}} role="menuitem" type="button">
<span aria-hidden="true" className="viz-card-menu-icon">
{icon}
</span>
<span>{label}</span>
</button>);
return (<section className="report-block report-html-block" id={block.id}>
<div className="viz-card-actions" data-image-export-exclude="true" ref={menuRef}>
<button aria-expanded={isMenuOpen} aria-label={`Open options for ${title}`} className="viz-card-menu-button viz-card__no-drag" onClick={(event) => {
event.stopPropagation();
toggleMenu();
}} onKeyDown={handleMenuButtonKeyDown} ref={menuButtonRef} type="button">
<Ellipsis aria-hidden="true" size={18} strokeWidth={2}/>
</button>
{shouldRenderMenu ? (<div className={`viz-card-menu viz-card__no-drag menu-surface ${menuMotionClass}`} onKeyDown={handleMenuKeyDown} role="menu" style={fixedMenuStyle}>
{menuItem("Copy HTML", <Copy size={18} strokeWidth={2}/>, handleCopyHtml)}
{menuItem("Delete", <Trash2 size={18} strokeWidth={2}/>, onDeleteBlock, "danger")}
</div>) : null}
</div>
{isEditMode ? (<textarea aria-label={`Edit HTML for ${title}`} className="report-html-editor" onChange={(event) => onHtmlChange(block.id, { html: event.target.value })} spellCheck={false} value={html}/>) : (<iframe className="report-html-frame" onLoad={handleFrameLoad} ref={frameRef} sandbox="allow-same-origin" srcDoc={sandboxedReportHtml(html)} style={frameHeight ? { height: `${frameHeight}px` } : undefined} title={title}/>)}
</section>);
}
function ReportMetricStripBlock({ cards, filters, id, isMenuOpen, onCopyResult, onDeleteBlock, onMenuOpenChange, selectedFilters, snapshot }) {
const cardRef = useRef(null);
const { closeMenu, fixedMenuStyle, handleMenuButtonKeyDown, handleMenuKeyDown, menuButtonRef, menuMotionClass, menuRef, toggleMenu, shouldRenderMenu } = useDashboardMenu(isMenuOpen, onMenuOpenChange);
const { getPreparedImageBlob, preparedImageExportStatus, prepareImageExport, resetPreparedImageExport } = usePreparedImageExport(cardRef);
function prepareImageExportQuietly(force = false) {
if (!shouldOfferImageClipboardCopy())
return;
const prepared = prepareImageExport({ force });
if (prepared)
void prepared.promise.catch(() => undefined);
}
async function handleCopyAsImage() {
if (!cardRef.current)
return;
try {
const copyResult = await copyElementAsImage(cardRef.current, getPreparedImageBlob());
resetPreparedImageExport();
onCopyResult(imageCopySuccessMessage("Copied key metrics as image.", copyResult));
}
catch (error) {
onCopyResult(error instanceof Error ? error.message : "Failed to copy image.", true);
}
}
const menuItem = (label, icon, onClick, tone = "default", onPrepare, disabled = false) => (<button className={`viz-card-menu-item ${tone === "danger" ? "viz-card-menu-item-danger" : ""}`.trim()} disabled={disabled} key={label} onFocus={onPrepare} onClick={() => {
void onClick();
closeMenu();
}} onPointerEnter={onPrepare} role="menuitem" type="button">
<span aria-hidden="true" className="viz-card-menu-icon">
{icon}
</span>
<span>{label}</span>
</button>);
return (<section className="report-metric-strip-block" id={id} ref={cardRef}>
<div className="viz-card-actions" data-image-export-exclude="true" ref={menuRef}>
<button aria-expanded={isMenuOpen} aria-label="Open options for key metrics" className="viz-card-menu-button viz-card__no-drag" onClick={(event) => {
event.stopPropagation();
const nextIsMenuOpen = toggleMenu();
if (nextIsMenuOpen) {
prepareImageExportQuietly(true);
}
else {
resetPreparedImageExport();
}
}} onFocus={() => prepareImageExportQuietly()} onKeyDown={handleMenuButtonKeyDown} onPointerEnter={() => prepareImageExportQuietly()} ref={menuButtonRef} type="button">
<Ellipsis aria-hidden="true" size={18} strokeWidth={2}/>
</button>
{shouldRenderMenu ? (<div className={`viz-card-menu viz-card__no-drag menu-surface ${menuMotionClass}`} onKeyDown={handleMenuKeyDown} role="menu" style={fixedMenuStyle}>
{shouldOfferImageClipboardCopy()
? menuItem("Copy as image", <Camera size={18} strokeWidth={2}/>, handleCopyAsImage, "default", prepareImageExportQuietly, preparedImageExportStatus === "pending")
: null}
{menuItem("Delete", <Trash2 size={18} strokeWidth={2}/>, onDeleteBlock, "danger")}
</div>) : null}
</div>
<KpiStrip cards={cards} filters={filters} selectedFilters={selectedFilters} snapshot={snapshot}/>
</section>);
}
function ReportBlockCard({ accessIssues, block, blockTextOverride, chart, chartSpecOverride, chartTextOverride, chartTypeOverride, columnWidths, filters, isBlockMenuOpen, isChartMenuOpen, isEditMode, isTableMenuOpen, layout, manifest, onBlockMenuOpenChange, onBlockTextChange, onChartTypeChange, onChartMenuOpenChange, onColumnWidthsChange, onDeleteBlock, onChartModalOpen, onCopyResult, onRequestEditMode, onTableMenuOpenChange, onTableModalOpen, onTableTextChange, onTextChange, selectedFilters, snapshot, table, tableTextOverride }) {
if (block.type === "html") {
return (<ReportHtmlBlock block={block} htmlOverride={blockTextOverride} isEditMode={isEditMode} isMenuOpen={isBlockMenuOpen} onHtmlChange={onBlockTextChange} onCopyResult={onCopyResult} onDeleteBlock={onDeleteBlock} onMenuOpenChange={onBlockMenuOpenChange}/>);
}
if (block.type === "chart" && chart) {
const overriddenChart = applyChartSpecOverride(chart, chartSpecOverride);
const chartRows = filterRowsForDataset(getRows(snapshot, overriddenChart.dataset), overriddenChart.dataset, filters, selectedFilters, chartUsedFields(overriddenChart));
const chartTypeOptions = compatibleChartTypesForArtifactCard(overriddenChart, chartRows);
const requestedType = chartTypeOverride ?? overriddenChart.type;
const activeType = chartTypeOptions.some((option) => option.type === requestedType)
? requestedType
: overriddenChart.type;
const displayChart = withChartType(overriddenChart, activeType);
const accessIssue = accessIssueForChart(displayChart, accessIssues);
return (<VizCard accessIssue={accessIssue} chart={displayChart} chartTypeOptions={chartTypeOptions} isEditMode={isEditMode} isMenuOpen={isChartMenuOpen} layout={layout} onChartTypeChange={onChartTypeChange} onCopyResult={onCopyResult} onDeleteBlock={onDeleteBlock} onMenuOpenChange={onChartMenuOpenChange} onModalOpen={onChartModalOpen} onRequestEditMode={onRequestEditMode} onTextChange={onTextChange} textOverride={chartTextOverride}>
<ChartBody accessIssue={accessIssue} chart={displayChart} filters={filters} layout={layout} selectedFilters={selectedFilters} snapshot={snapshot}/>
</VizCard>);
}
if (block.type === "table" && table) {
return (<DataTable columnWidths={columnWidths} filters={filters} isEditMode={isEditMode} isMenuOpen={isTableMenuOpen} layout={layout} manifest={manifest} onColumnWidthsChange={onColumnWidthsChange} onDeleteBlock={onDeleteBlock} onMenuOpenChange={onTableMenuOpenChange} onModalOpen={onTableModalOpen} onRequestEditMode={onRequestEditMode} onTextChange={onTableTextChange} selectedFilters={selectedFilters} snapshot={snapshot} table={table} textOverride={tableTextOverride}/>);
}
return (<ReportTextBlock block={block} isEditMode={isEditMode} isMenuOpen={isBlockMenuOpen} onCopyResult={onCopyResult} onDeleteBlock={onDeleteBlock} onMenuOpenChange={onBlockMenuOpenChange} onRequestEditMode={onRequestEditMode} onTextChange={onBlockTextChange} textOverride={blockTextOverride}/>);
}
const EXPORT_TARGET_LABELS = {
site: "Publish to Sites",
html: "Create HTML file",
pdf: "Create PDF",
document: "Create Google Doc",
slides: "Create Google Slides"
};
const EXPORT_TARGET_ICONS = {
site: <Globe aria-hidden="true" size={16} strokeWidth={2}/>,
html: <FileText aria-hidden="true" size={16} strokeWidth={2}/>,
pdf: <FileDown aria-hidden="true" size={16} strokeWidth={2}/>,
document: <FileText aria-hidden="true" size={16} strokeWidth={2}/>,
slides: <Presentation aria-hidden="true" size={16} strokeWidth={2}/>
};
function packageControls(packageInfo) {
return packageInfo?.controls && typeof packageInfo.controls === "object" ? packageInfo.controls : {};
}
function artifactCapabilities(packageInfo) {
const controls = packageControls(packageInfo);
const hostedReadOnly = packageInfo?.hostedReadOnly === true || packageInfo?.deliveryMode === "site_creator";
return {
canEdit: !hostedReadOnly && controls.edit !== false,
canPublishHostedLink: !hostedReadOnly && controls.exportHostedLink !== false && controls.hostedLink !== false,
canExportHtml: controls.html !== false,
canExportPdf: controls.pdf !== false,
canExportDocument: controls.document !== false,
canExportSlides: controls.slides !== false
};
}
function exportTargetsForCapabilities(capabilities) {
return Object.keys(EXPORT_TARGET_LABELS).filter((target) => {
if (target === "site")
return capabilities.canPublishHostedLink;
if (target === "html")
return capabilities.canExportHtml;
if (target === "pdf")
return capabilities.canExportPdf;
if (target === "document")
return capabilities.canExportDocument;
if (target === "slides")
return capabilities.canExportSlides;
return false;
});
}
function appSurfaceLabel(manifest) {
return manifest?.surface === "report" ? "report" : "dashboard";
}
function compactArtifactUrl() {
try {
const url = new URL(window.location.href);
for (const name of ["locale", "deviceType", "unsafeSkipTargetOriginCheck"]) {
url.searchParams.delete(name);
}
return url.toString();
}
catch {
return window.location.href;
}
}
function usefulContextPath(value) {
const trimmedValue = value?.trim();
return trimmedValue && trimmedValue !== "tool payload" && !trimmedValue.startsWith("mcp://")
? trimmedValue
: null;
}
function promptContext(manifest, snapshot, packageInfo) {
const packagePath = usefulContextPath(packageInfo?.root);
const manifestPath = usefulContextPath(packageInfo?.manifestPath);
const snapshotPath = usefulContextPath(packageInfo?.snapshotPath);
return [
`Artifact URL: ${compactArtifactUrl()}`,
packagePath ? `Package path: ${packagePath}` : null,
manifestPath ? `Manifest file: ${manifestPath}` : null,
snapshotPath ? `Snapshot file: ${snapshotPath}` : null,
`Generated at: ${snapshot?.generatedAt ?? manifest?.generatedAt ?? "unknown"}`
]
.filter((line) => Boolean(line))
.join("\n");
}
function refreshPrompt(manifest, snapshot, packageInfo) {
const surface = appSurfaceLabel(manifest);
return `Refresh this ${surface} app using the artifact manifest's declared sources and the latest available time frame.

Inspect the artifact manifest for source details before rerunning. Update the snapshot data and generatedAt metadata, rebuild any static export, and verify the refreshed ${surface} in the in-app browser. Keep the current layout and narrative structure unless the latest data makes a statement incorrect.

${promptContext(manifest, snapshot, packageInfo)}`;
}
function exportPrompt(target, manifest, snapshot, packageInfo) {
const surface = appSurfaceLabel(manifest);
const context = promptContext(manifest, snapshot, packageInfo);
if (target === "site") {
return `Publish this ${surface} app as a hosted Site Creator link.

Use the current Data Analytics artifact as the source of truth. Create or reuse a Site Creator project for this ${surface}, materialize a Cloudflare Worker-compatible app that serves the current manifest, bounded snapshot, package metadata, and inline-safe source text through /api/manifest, /api/snapshot, /api/package, and /api/source-file, then deploy it through Site Creator. Preserve the rendered layout, charts, tables, source details, and narrative. Default access to workspace_all unless I explicitly ask for narrower access, and report the production URL plus the access mode.

If the local package files are unavailable from the context below, stop and ask for the report package or validated artifact payload rather than publishing an empty or stale report.

${context}`;
}
if (target === "html") {
return `Export this ${surface} app as a static, portable HTML artifact. Include the content title, narrative, charts, tables, and source details. Omit the interactive top bar and app-only controls from the exported artifact. Verify the HTML before delivery.

${context}`;
}
if (target === "document") {
return `Use the existing data-analytics:report-to-google-doc workflow to export this ${surface} app as a polished native document artifact. Use the current app content and static HTML export when available, preserve headings, charts, tables, source details, and the executive narrative, then verify the created document.

${context}`;
}
if (target === "slides") {
return `Use the existing data-analytics:report-to-google-slides workflow to export this ${surface} app as an executive-ready native slides artifact. Preserve the core claims, charts, tables, caveats, and source details, and verify the created deck.

${context}`;
}
return `Use the existing data-analytics:report-to-pdf workflow to create a PDF artifact from this ${surface} app. Use the static HTML/export path when available, preserve the content title, narrative, charts, tables, caveats, and source details, omit interactive top bars, share menus, edit controls, and app-only controls, then verify the PDF before delivery.

${context}`;
}
function setOptionalCodexSearchParam(url, name, value) {
const trimmedValue = value?.trim();
if (!trimmedValue)
return;
url.searchParams.set(name, trimmedValue);
}
function codexPromptUrl(prompt, packageInfo) {
const url = new URL("codex://threads/new");
setOptionalCodexSearchParam(url, "prompt", prompt);
setOptionalCodexSearchParam(url, "originUrl", packageInfo?.originUrl);
setOptionalCodexSearchParam(url, "path", packageInfo?.root);
return url.toString();
}
function codexHostPromptPayload(prompt, packageInfo) {
return {
originUrl: packageInfo?.originUrl,
path: packageInfo?.root,
prompt
};
}
function sendCodexPromptToHost(prompt, packageInfo) {
const hostApi = window.openai;
const payload = codexHostPromptPayload(prompt, packageInfo);
const launchers = [hostApi?.sendFollowUpMessage, hostApi?.openCodexPrompt];
for (const launch of launchers) {
if (typeof launch !== "function")
continue;
try {
void Promise.resolve(launch.call(hostApi, payload)).catch(() => { });
return true;
}
catch {
}
}
return false;
}
function isLocalPreviewHost() {
return ["localhost", "127.0.0.1", "::1"].includes(window.location.hostname);
}
function launchCodexDeepLink(url) {
if (isLocalPreviewHost())
return false;
let linkClicked = false;
try {
const link = document.createElement("a");
link.href = url;
link.target = "_top";
link.rel = "noopener noreferrer";
link.style.display = "none";
document.body.appendChild(link);
link.click();
link.remove();
linkClicked = true;
}
catch {
}
try {
if (window.top === window) {
window.location.assign(url);
return true;
}
}
catch {
}
return linkClicked;
}
function openCodexPrompt(prompt, packageInfo, onCopyResult) {
const url = codexPromptUrl(prompt, packageInfo);
const launched = launchCodexDeepLink(url);
const sentToHost = sendCodexPromptToHost(prompt, packageInfo);
const openedCodex = sentToHost || launched;
void copyTextToClipboard(prompt)
.then(() => {
onCopyResult(sentToHost
? "Started in this chat."
: openedCodex
? "Codex prompt copied. Opening Codex if supported."
: "Prompt copied. Open Codex and paste it to continue.", false);
})
.catch(() => {
onCopyResult(openedCodex
? "Opening Codex if supported, but prompt copy was blocked."
: "Could not copy the Codex prompt from this preview.", true);
});
}
function AnalyticsTopBarFreshness({ dateLabel, onRefresh, status, statusLabel }) {
const refreshTitle = dateLabel === "Unknown"
? "Refresh using latest available data."
: `Refresh using latest available data. Last updated ${dateLabel}.`;
const refreshLabel = dateLabel === "Unknown" ? "Refresh" : dateLabel;
return (<div className="analytics-top-bar-freshness">
<button aria-label={refreshTitle} className="top-bar-button top-bar-button-ghost top-bar-refresh-button" onClick={onRefresh} title={refreshTitle} type="button">
<RefreshCw aria-hidden="true" size={14} strokeWidth={2}/>
<span>{refreshLabel}</span>
{statusLabel ? <span className={`snapshot-status ${status}`}>{statusLabel}</span> : null}
</button>
</div>);
}
function AnalyticsTopBar({ chrome = "full", isEditMode, onCancelEdit, manifest, onCopyResult, onEdit, onRequestFullscreen, onSaveEdit, onTitleChange, packageInfo, snapshot, title }) {
const [isExportMenuOpen, setIsExportMenuOpen] = useState(false);
const { closeMenu, fixedMenuStyle, handleMenuButtonKeyDown, handleMenuKeyDown, menuButtonRef, menuMotionClass, menuRef, toggleMenu, shouldRenderMenu } = useDashboardMenu(isExportMenuOpen, setIsExportMenuOpen);
const capabilities = artifactCapabilities(packageInfo);
const exportTargets = exportTargetsForCapabilities(capabilities);
const lastRefresh = formatDate(snapshot?.generatedAt ?? manifest?.generatedAt);
const statusLabel = snapshotStatusLabel(snapshot?.status);
const dateLabel = lastRefresh;
const showStatusLabel = manifest?.surface !== "report" && statusLabel;
const showActions = chrome === "full";
const showInlineExpand = chrome === "inline" && typeof onRequestFullscreen === "function";
function requestRefresh() {
void openCodexPrompt(refreshPrompt(manifest, snapshot, packageInfo), packageInfo, onCopyResult);
}
function requestExport(target) {
closeMenu();
void openCodexPrompt(exportPrompt(target, manifest, snapshot, packageInfo), packageInfo, onCopyResult);
}
return (<div className="analytics-top-bar" aria-label={`${appSurfaceLabel(manifest)} actions`}>
<div className="analytics-top-bar-title">
<EditablePageTitle ariaLabel={`Edit ${appSurfaceLabel(manifest)} title`} isEditMode={isEditMode} onChange={onTitleChange} onRequestEditMode={onEdit} placeholder={composePageTitle(manifest)} readOnly={!showActions || !capabilities.canEdit} title={title}/>
</div>
{showInlineExpand ? (<div className="analytics-top-bar-actions">
<button aria-label={`Expand ${appSurfaceLabel(manifest)} fullscreen`} className="top-bar-button" onClick={onRequestFullscreen} title={`Expand ${appSurfaceLabel(manifest)} fullscreen`} type="button">
<Expand aria-hidden="true" size={14} strokeWidth={2}/>
<span>Expand</span>
</button>
</div>) : showActions ? (<div className="analytics-top-bar-actions">
<AnalyticsTopBarFreshness dateLabel={dateLabel} onRefresh={requestRefresh} status={snapshot?.status} statusLabel={showStatusLabel ? statusLabel : null}/>
{isEditMode && capabilities.canEdit ? (<>
<button className="top-bar-button" onClick={onCancelEdit} type="button">
<span>Cancel</span>
</button>
<button className="top-bar-button top-bar-button-primary" onClick={onSaveEdit} type="button">
<span>Save changes</span>
</button>
</>) : (<>
{capabilities.canEdit ? (
<button className="top-bar-button top-bar-edit-button" onClick={onEdit} type="button">
<Pencil aria-hidden="true" size={14} strokeWidth={2}/>
<span>Edit</span>
</button>
): null}
{exportTargets.length ? (
<div className="export-menu">
<button ref={menuButtonRef} aria-expanded={isExportMenuOpen} aria-haspopup="menu" className="top-bar-button" onClick={toggleMenu} onKeyDown={handleMenuButtonKeyDown} type="button">
<span>Export</span>
<ChevronDown aria-hidden="true" size={14} strokeWidth={2}/>
</button>
{shouldRenderMenu ? (<div ref={menuRef} className={`export-menu-list menu-surface ${menuMotionClass}`} onKeyDown={handleMenuKeyDown} role="menu" style={fixedMenuStyle}>
{exportTargets.map((target) => (<button className="export-menu-item" key={target} onClick={() => requestExport(target)} role="menuitem" type="button">
{EXPORT_TARGET_ICONS[target]}
{EXPORT_TARGET_LABELS[target]}
</button>))}
</div>) : null}
</div>
): null}
</>)}
</div>) : null}
</div>);
}
export default function App({ displayMode = "fullscreen", onRequestFullscreen } = {}) {
const [manifest, setManifest] = useState(null);
const [snapshot, setSnapshot] = useState(null);
const [packageInfo, setPackageInfo] = useState(null);
const [error, setError] = useState(null);
const [selectedFilters, setSelectedFilters] = useState({});
const [tableColumnWidths, setTableColumnWidths] = useState({});
const [pageTitle, setPageTitle] = useState("");
const [chartTextOverrides, setChartTextOverrides] = useState({});
const [chartSpecOverrides, setChartSpecOverrides] = useState({});
const [chartTypeOverrides, setChartTypeOverrides] = useState({});
const [tableTextOverrides, setTableTextOverrides] = useState({});
const [blockTextOverrides, setBlockTextOverrides] = useState({});
const [deletedReportBlockIds, setDeletedReportBlockIds] = useState([]);
const [openMenuChartId, setOpenMenuChartId] = useState(null);
const [openMenuTableId, setOpenMenuTableId] = useState(null);
const [openMenuBlockId, setOpenMenuBlockId] = useState(null);
const [chartModal, setChartModal] = useState(null);
const [tableModal, setTableModal] = useState(null);
const [copyMessage, setCopyMessage] = useState(null);
const [isEditMode, setIsEditMode] = useState(false);
const [layoutResetKey, setLayoutResetKey] = useState(0);
const editSnapshotRef = useRef(null);
const layoutDraftsRef = useRef({ dashboard: null, report: null });
useEffect(() => {
async function load() {
try {
const [nextManifest, nextSnapshot, nextPackageInfo] = await Promise.all([
fetchJson("/api/manifest"),
fetchJson("/api/snapshot"),
fetchOptionalJson("/api/package")
]);
setManifest(normalizeManifest(nextManifest));
setSnapshot(normalizeSnapshot(nextSnapshot));
setPackageInfo(nextPackageInfo);
}
catch (loadError) {
setError(loadError instanceof Error ? loadError.message : "Failed to load report");
}
}
void load();
}, []);
const filters = manifest?.filters ?? EMPTY_FILTERS;
const cards = manifest?.cards ?? EMPTY_CARDS;
const charts = manifest?.charts ?? EMPTY_CHARTS;
const tables = manifest?.tables ?? EMPTY_TABLES;
const reportBlocks = manifest?.blocks ?? EMPTY_REPORT_BLOCKS;
const globalFilters = useMemo(() => getGlobalFilters(filters, cards, charts, tables), [cards, charts, filters, tables]);
const accessIssues = snapshot?.accessIssues ?? EMPTY_ACCESS_ISSUES;
const storageKey = contentLayoutKey(manifest);
const chartTextStorageKey = chartTextKey(manifest);
const chartSpecStorageKey = chartSpecKey(manifest);
const chartTypeStorageKey = chartTypeKey(manifest);
const pageTitleTextStorageKey = pageTitleTextKey(manifest);
const tableTextStorageKey = tableTextKey(manifest);
const blockTextStorageKey = blockTextKey(manifest);
const deletedReportBlockStorageKey = deletedReportBlocksKey(manifest);
const tableColumnWidthStorageKey = tableColumnWidthKey(manifest);
const reportStorageKey = reportContentLayoutKey(manifest);
const isReport = manifest?.surface === "report";
const activeSurfaceFilters = isReport ? filters : globalFilters;
const capabilities = useMemo(() => artifactCapabilities(packageInfo), [packageInfo]);
const activeEditMode = capabilities.canEdit && isEditMode;
const requestEditMode = capabilities.canEdit ? beginEditMode : undefined;
useEffect(() => {
document.title = pageTitle.trim() || composePageTitle(manifest);
}, [manifest, pageTitle]);
useEffect(() => {
if (!capabilities.canEdit && isEditMode) {
setIsEditMode(false);
}
}, [capabilities.canEdit, isEditMode]);
const cardsById = useMemo(() => new Map(cards.map((card) => [card.id, card])), [cards]);
const chartsById = useMemo(() => new Map(charts.map((chart) => [chart.id, chart])), [charts]);
const tablesById = useMemo(() => new Map(tables.map((table) => [table.id, table])), [tables]);
const reportGridBlocks = reportBlocks;
const visibleReportGridBlocks = useMemo(() => {
if (!deletedReportBlockIds.length)
return reportGridBlocks;
const deletedIds = new Set(deletedReportBlockIds);
return reportGridBlocks.filter((block) => !deletedIds.has(block.id));
}, [deletedReportBlockIds, reportGridBlocks]);
useEffect(() => {
if (!reportGridBlocks.length || !deletedReportBlockStorageKey) {
setDeletedReportBlockIds([]);
return;
}
const stored = window.localStorage.getItem(deletedReportBlockStorageKey);
if (!stored) {
setDeletedReportBlockIds([]);
return;
}
try {
const parsed = JSON.parse(stored);
const knownIds = new Set(reportGridBlocks.map((block) => block.id));
const nextIds = Array.isArray(parsed)
? parsed.filter((id) => typeof id === "string" && knownIds.has(id))
: [];
setDeletedReportBlockIds(nextIds);
}
catch {
setDeletedReportBlockIds([]);
}
}, [deletedReportBlockStorageKey, reportGridBlocks]);
useEffect(() => {
if (!tables.length || !tableColumnWidthStorageKey) {
setTableColumnWidths({});
return;
}
const stored = window.localStorage.getItem(tableColumnWidthStorageKey);
if (!stored) {
setTableColumnWidths({});
return;
}
try {
const parsed = JSON.parse(stored);
const tableFields = new Map(tables.map((table) => [table.id, new Set(table.columns.map((column) => column.field))]));
const nextState = {};
if (parsed && typeof parsed === "object" && !Array.isArray(parsed)) {
for (const [tableId, rawWidths] of Object.entries(parsed)) {
const fields = tableFields.get(tableId);
if (!fields || !rawWidths || typeof rawWidths !== "object" || Array.isArray(rawWidths)) {
continue;
}
const nextWidths = {};
for (const [field, rawWidth] of Object.entries(rawWidths)) {
const width = typeof rawWidth === "number" ? rawWidth : Number(rawWidth);
if (fields.has(field) && Number.isFinite(width)) {
nextWidths[field] = clamp(Math.round(width), TABLE_COLUMN_MIN_WIDTH, TABLE_COLUMN_MAX_WIDTH);
}
}
if (Object.keys(nextWidths).length) {
nextState[tableId] = nextWidths;
}
}
}
setTableColumnWidths(nextState);
}
catch {
setTableColumnWidths({});
}
}, [tableColumnWidthStorageKey, tables]);
useEffect(() => {
const fallbackTitle = composePageTitle(manifest);
if (!pageTitleTextStorageKey) {
setPageTitle(fallbackTitle);
return;
}
const storedTitle = window.localStorage.getItem(pageTitleTextStorageKey);
setPageTitle(storedTitle ?? fallbackTitle);
}, [manifest, pageTitleTextStorageKey]);
useEffect(() => {
if (!charts.length || !chartTextStorageKey)
return;
const stored = window.localStorage.getItem(chartTextStorageKey);
if (!stored) {
setChartTextOverrides({});
return;
}
try {
const parsed = JSON.parse(stored);
const knownIds = new Set(charts.map((chart) => chart.id));
const nextOverrides = {};
for (const [chartId, override] of Object.entries(parsed)) {
if (knownIds.has(chartId)
&& override
&& typeof override === "object"
&& (typeof override.headerMarkdown === "string"
|| typeof override.title === "string"
|| typeof override.subtitle === "string")) {
nextOverrides[chartId] = {
...(typeof override.headerMarkdown === "string" ? { headerMarkdown: override.headerMarkdown } : {}),
...(typeof override.title === "string" ? { title: override.title } : {}),
...(typeof override.subtitle === "string" ? { subtitle: override.subtitle } : {})
};
}
}
setChartTextOverrides(nextOverrides);
}
catch {
setChartTextOverrides({});
}
}, [chartTextStorageKey, charts]);
useEffect(() => {
if (!charts.length || !chartSpecStorageKey) {
setChartSpecOverrides({});
return;
}
const stored = window.localStorage.getItem(chartSpecStorageKey);
if (!stored) {
setChartSpecOverrides({});
return;
}
try {
const parsed = JSON.parse(stored);
const chartsByIdForStorage = new Map(charts.map((chart) => [chart.id, chart]));
const nextOverrides = {};
if (parsed && typeof parsed === "object" && !Array.isArray(parsed)) {
for (const [chartId, override] of Object.entries(parsed)) {
const chart = chartsByIdForStorage.get(chartId);
if (!chart || !override || typeof override !== "object" || Array.isArray(override)) {
continue;
}
const sanitized = {};
if (sharedIsChartType(override.type)) {
sanitized.type = override.type;
}
const chartFields = new Set(chartUsedFields(chart));
if (override.encodings && typeof override.encodings === "object" && !Array.isArray(override.encodings)) {
const sizeEncoding = override.encodings.size;
if (sizeEncoding && typeof sizeEncoding === "object" && !Array.isArray(sizeEncoding) && typeof sizeEncoding.field === "string" && chartFields.has(sizeEncoding.field)) {
sanitized.encodings = { ...chart.encodings, size: { ...sizeEncoding, field: sizeEncoding.field } };
}
}
if (override.settings && typeof override.settings === "object" && !Array.isArray(override.settings)) {
sanitized.settings = {
...(override.settings.orientation === "horizontal" || override.settings.orientation === "vertical" ? { orientation: override.settings.orientation } : {}),
...(["grouped", "stacked", "stacked100"].includes(override.settings.groupMode) ? { groupMode: override.settings.groupMode } : {}),
};
if (!Object.keys(sanitized.settings).length) {
delete sanitized.settings;
}
}
if (Object.keys(sanitized).length) {
nextOverrides[chartId] = sanitized;
}
}
}
setChartSpecOverrides(nextOverrides);
}
catch {
setChartSpecOverrides({});
}
}, [chartSpecStorageKey, charts]);
useEffect(() => {
if (!charts.length || !chartTypeStorageKey) {
setChartTypeOverrides({});
return;
}
const stored = window.localStorage.getItem(chartTypeStorageKey);
if (!stored) {
setChartTypeOverrides({});
return;
}
try {
const parsed = JSON.parse(stored);
const knownIds = new Set(charts.map((chart) => chart.id));
const nextOverrides = {};
for (const [chartId, chartType] of Object.entries(parsed)) {
if (knownIds.has(chartId) && isChartType(chartType)) {
nextOverrides[chartId] = chartType;
}
}
setChartTypeOverrides(nextOverrides);
}
catch {
setChartTypeOverrides({});
}
}, [chartTypeStorageKey, charts]);
useEffect(() => {
if (!tables.length || !tableTextStorageKey)
return;
const stored = window.localStorage.getItem(tableTextStorageKey);
if (!stored) {
setTableTextOverrides({});
return;
}
try {
const parsed = JSON.parse(stored);
const knownIds = new Set(tables.map((table) => table.id));
const nextOverrides = {};
for (const [tableId, override] of Object.entries(parsed)) {
if (knownIds.has(tableId)
&& override
&& typeof override === "object"
&& typeof override.headerMarkdown === "string") {
nextOverrides[tableId] = { headerMarkdown: override.headerMarkdown };
}
}
setTableTextOverrides(nextOverrides);
}
catch {
setTableTextOverrides({});
}
}, [tableTextStorageKey, tables]);
useEffect(() => {
if (!reportGridBlocks.length || !blockTextStorageKey)
return;
const stored = window.localStorage.getItem(blockTextStorageKey);
if (!stored) {
setBlockTextOverrides({});
return;
}
try {
const parsed = JSON.parse(stored);
const knownIds = new Set(reportGridBlocks.map((block) => block.id));
const nextOverrides = {};
for (const [blockId, override] of Object.entries(parsed)) {
if (knownIds.has(blockId) && override && typeof override === "object") {
const nextOverride = {
...(visibleString(override.bodyMarkdown) ? { bodyMarkdown: override.bodyMarkdown } : {}),
...(visibleString(override.html) ? { html: override.html } : {})
};
if (Object.keys(nextOverride).length)
nextOverrides[blockId] = nextOverride;
}
}
setBlockTextOverrides(nextOverrides);
}
catch {
setBlockTextOverrides({});
}
}, [blockTextStorageKey, reportGridBlocks]);
const filterDefaults = useMemo(() => {
return Object.fromEntries(activeSurfaceFilters.map((filter) => [filter.id, filter.defaultValue ?? "all"]));
}, [activeSurfaceFilters]);
useEffect(() => {
setSelectedFilters((current) => ({ ...filterDefaults, ...current }));
}, [filterDefaults]);
useEffect(() => {
if (!copyMessage)
return;
const timeout = window.setTimeout(() => setCopyMessage(null), 2600);
return () => window.clearTimeout(timeout);
}, [copyMessage]);
function persistEditableState() {
if (pageTitleTextStorageKey) {
window.localStorage.setItem(pageTitleTextStorageKey, pageTitle);
}
if (chartTextStorageKey) {
window.localStorage.setItem(chartTextStorageKey, JSON.stringify(chartTextOverrides));
}
if (chartSpecStorageKey) {
window.localStorage.setItem(chartSpecStorageKey, JSON.stringify(chartSpecOverrides));
}
if (chartTypeStorageKey) {
window.localStorage.setItem(chartTypeStorageKey, JSON.stringify(chartTypeOverrides));
}
if (tableTextStorageKey) {
window.localStorage.setItem(tableTextStorageKey, JSON.stringify(tableTextOverrides));
}
if (blockTextStorageKey) {
window.localStorage.setItem(blockTextStorageKey, JSON.stringify(blockTextOverrides));
}
if (deletedReportBlockStorageKey) {
window.localStorage.setItem(deletedReportBlockStorageKey, JSON.stringify(deletedReportBlockIds));
}
if (tableColumnWidthStorageKey) {
window.localStorage.setItem(tableColumnWidthStorageKey, JSON.stringify(tableColumnWidths));
}
if (storageKey && layoutDraftsRef.current.dashboard) {
window.localStorage.setItem(storageKey, JSON.stringify(layoutDraftsRef.current.dashboard));
}
if (reportStorageKey && layoutDraftsRef.current.report) {
window.localStorage.setItem(reportStorageKey, JSON.stringify(layoutDraftsRef.current.report));
}
}
function closeInlineMenus() {
setOpenMenuBlockId(null);
setOpenMenuChartId(null);
setOpenMenuTableId(null);
}
function beginEditMode() {
if (isEditMode)
return;
editSnapshotRef.current = {
blockTextOverrides: cloneSerializable(blockTextOverrides),
chartSpecOverrides: cloneSerializable(chartSpecOverrides),
chartTextOverrides: cloneSerializable(chartTextOverrides),
chartTypeOverrides: cloneSerializable(chartTypeOverrides),
deletedReportBlockIds: [...deletedReportBlockIds],
pageTitle,
tableColumnWidths: cloneSerializable(tableColumnWidths),
tableTextOverrides: cloneSerializable(tableTextOverrides)
};
layoutDraftsRef.current = { dashboard: null, report: null };
closeInlineMenus();
setIsEditMode(true);
}
function cancelEditMode() {
const snapshotState = editSnapshotRef.current;
if (snapshotState) {
setBlockTextOverrides(cloneSerializable(snapshotState.blockTextOverrides));
setChartSpecOverrides(cloneSerializable(snapshotState.chartSpecOverrides ?? {}));
setChartTextOverrides(cloneSerializable(snapshotState.chartTextOverrides));
setChartTypeOverrides(cloneSerializable(snapshotState.chartTypeOverrides));
setDeletedReportBlockIds([...snapshotState.deletedReportBlockIds]);
setPageTitle(snapshotState.pageTitle);
setTableColumnWidths(cloneSerializable(snapshotState.tableColumnWidths));
setTableTextOverrides(cloneSerializable(snapshotState.tableTextOverrides));
}
editSnapshotRef.current = null;
layoutDraftsRef.current = { dashboard: null, report: null };
closeInlineMenus();
setIsEditMode(false);
setLayoutResetKey((current) => current + 1);
}
function saveEditMode() {
persistEditableState();
editSnapshotRef.current = null;
layoutDraftsRef.current = { dashboard: null, report: null };
closeInlineMenus();
setIsEditMode(false);
}
function recordDashboardLayoutDraft(nextItems) {
layoutDraftsRef.current.dashboard = nextItems;
}
function recordReportLayoutDraft(nextItems) {
layoutDraftsRef.current.report = nextItems;
}
function updatePageTitle(nextTitle) {
setPageTitle(nextTitle);
if (!isEditMode && pageTitleTextStorageKey) {
window.localStorage.setItem(pageTitleTextStorageKey, nextTitle);
}
}
function updateChartText(chartId, nextText) {
setChartTextOverrides((current) => {
const merged = {
...current,
[chartId]: {
...current[chartId],
...nextText
}
};
if (!isEditMode && chartTextStorageKey) {
window.localStorage.setItem(chartTextStorageKey, JSON.stringify(merged));
}
return merged;
});
}
function updateChartType(chartId, nextType) {
setChartTypeOverrides((current) => {
const originalType = charts.find((chart) => chart.id === chartId)?.type;
const merged = { ...current };
if (!originalType || nextType === originalType) {
delete merged[chartId];
}
else {
merged[chartId] = nextType;
}
if (!isEditMode && chartTypeStorageKey) {
window.localStorage.setItem(chartTypeStorageKey, JSON.stringify(merged));
}
return merged;
});
}
function updateChartSpec(chartId, widgetSpec) {
const chart = charts.find((candidate) => candidate.id === chartId);
if (!chart)
return;
if (!widgetSpec) {
setChartSpecOverrides((current) => {
const merged = { ...current };
delete merged[chartId];
if (!isEditMode && chartSpecStorageKey) {
window.localStorage.setItem(chartSpecStorageKey, JSON.stringify(merged));
}
return merged;
});
setChartTypeOverrides((current) => {
const merged = { ...current };
delete merged[chartId];
if (!isEditMode && chartTypeStorageKey) {
window.localStorage.setItem(chartTypeStorageKey, JSON.stringify(merged));
}
return merged;
});
return;
}
const nextOverride = chartSpecOverrideFromWidgetSpec(chart, widgetSpec);
const nextType = sharedIsChartType(nextOverride.type) ? nextOverride.type : chart.type;
setChartSpecOverrides((current) => {
const merged = { ...current };
if (Object.keys(nextOverride).length) {
merged[chartId] = nextOverride;
}
else {
delete merged[chartId];
}
if (!isEditMode && chartSpecStorageKey) {
window.localStorage.setItem(chartSpecStorageKey, JSON.stringify(merged));
}
return merged;
});
setChartTypeOverrides((current) => {
const merged = { ...current };
if (nextType === chart.type) {
delete merged[chartId];
}
else {
merged[chartId] = nextType;
}
if (!isEditMode && chartTypeStorageKey) {
window.localStorage.setItem(chartTypeStorageKey, JSON.stringify(merged));
}
return merged;
});
}
function updateTableColumnWidths(tableId, nextWidths, options = {}) {
setTableColumnWidths((current) => {
const tableSpec = tablesById.get(tableId);
if (!tableSpec)
return current;
const validFields = new Set(tableSpec.columns.map((column) => column.field));
const sanitizedWidths = {};
for (const [field, rawWidth] of Object.entries(nextWidths)) {
const width = typeof rawWidth === "number" ? rawWidth : Number(rawWidth);
if (validFields.has(field) && Number.isFinite(width)) {
sanitizedWidths[field] = clamp(Math.round(width), TABLE_COLUMN_MIN_WIDTH, TABLE_COLUMN_MAX_WIDTH);
}
}
const merged = { ...current };
if (Object.keys(sanitizedWidths).length) {
merged[tableId] = sanitizedWidths;
}
else {
delete merged[tableId];
}
if (!isEditMode && options.persist !== false && tableColumnWidthStorageKey) {
window.localStorage.setItem(tableColumnWidthStorageKey, JSON.stringify(merged));
}
return merged;
});
}
function updateTableText(tableId, nextText) {
setTableTextOverrides((current) => {
const merged = {
...current,
[tableId]: {
...current[tableId],
...nextText
}
};
if (!isEditMode && tableTextStorageKey) {
window.localStorage.setItem(tableTextStorageKey, JSON.stringify(merged));
}
return merged;
});
}
function updateBlockText(blockId, nextText) {
setBlockTextOverrides((current) => {
const nextBlockOverride = {
...current[blockId],
...nextText
};
if ("bodyMarkdown" in nextText && !visibleString(nextText.bodyMarkdown)) {
delete nextBlockOverride.bodyMarkdown;
}
if ("html" in nextText && !visibleString(nextText.html)) {
delete nextBlockOverride.html;
}
const merged = { ...current };
if (Object.keys(nextBlockOverride).length)
merged[blockId] = nextBlockOverride;
else
delete merged[blockId];
if (!isEditMode && blockTextStorageKey) {
window.localStorage.setItem(blockTextStorageKey, JSON.stringify(merged));
}
return merged;
});
}
function deleteReportBlocks(blockIds) {
const idsToDelete = [...new Set(blockIds)];
if (!idsToDelete.length)
return;
setDeletedReportBlockIds((current) => {
const existingIds = new Set(current);
const nextIds = [...current];
for (const blockId of idsToDelete) {
if (!existingIds.has(blockId)) {
nextIds.push(blockId);
}
}
if (nextIds.length === current.length)
return current;
if (!isEditMode && deletedReportBlockStorageKey) {
window.localStorage.setItem(deletedReportBlockStorageKey, JSON.stringify(nextIds));
}
return nextIds;
});
setOpenMenuBlockId(null);
setOpenMenuChartId(null);
setOpenMenuTableId(null);
}
function deleteReportBlock(blockId) {
deleteReportBlocks([blockId]);
}
const dashboardContentBlocks = useMemo(() => {
const chartBlocks = charts.map((chart) => ({
className: "analytics-layout-item-chart",
defaultLayout: dashboardCardLayout(chart.layout),
id: `chart:${chart.id}`,
render: (layout, { setLayout }) => {
const overriddenChart = applyChartSpecOverride(chart, chartSpecOverrides[chart.id]);
const chartRows = filterRowsForDataset(getRows(snapshot, overriddenChart.dataset), overriddenChart.dataset, activeSurfaceFilters, selectedFilters, chartUsedFields(overriddenChart));
const chartTypeOptions = compatibleChartTypesForArtifactCard(overriddenChart, chartRows);
const requestedType = chartTypeOverrides[chart.id] ?? overriddenChart.type;
const activeType = chartTypeOptions.some((option) => option.type === requestedType)
? requestedType
: overriddenChart.type;
const displayChart = withChartType(overriddenChart, activeType);
const accessIssue = accessIssueForChart(displayChart, accessIssues);
return (<VizCard accessIssue={accessIssue} chart={displayChart} chartTypeOptions={chartTypeOptions} isEditMode={activeEditMode} isMenuOpen={openMenuChartId === chart.id} layout={layout} onChartTypeChange={updateChartType} onCopyResult={(message, isError = false) => setCopyMessage({ isError, message })} onRequestEditMode={requestEditMode} onTextChange={updateChartText} onMenuOpenChange={(nextOpen) => {
setOpenMenuTableId(null);
setOpenMenuChartId(nextOpen ? chart.id : null);
}} onModalOpen={setChartModal} textOverride={chartTextOverrides[chart.id]}>
<ChartBody accessIssue={accessIssue} chart={displayChart} filters={activeSurfaceFilters} layout={layout} selectedFilters={selectedFilters} snapshot={snapshot}/>
</VizCard>);
}
}));
const tableBlocks = tables.map((table) => ({
className: "analytics-layout-item-table",
defaultLayout: dashboardCardLayout(table.layout ?? "full"),
id: `table:${table.id}`,
render: (layout) => (<DataTable columnWidths={tableColumnWidths[table.id] ?? {}} filters={activeSurfaceFilters} isEditMode={activeEditMode} isMenuOpen={openMenuTableId === table.id} layout={layout} manifest={manifest} onColumnWidthsChange={updateTableColumnWidths} onMenuOpenChange={(nextOpen) => {
setOpenMenuChartId(null);
setOpenMenuTableId(nextOpen ? table.id : null);
}} onModalOpen={setTableModal} onRequestEditMode={requestEditMode} onTextChange={updateTableText} selectedFilters={selectedFilters} snapshot={snapshot} table={table} textOverride={tableTextOverrides[table.id]}/>)
}));
const htmlBlocks = visibleReportGridBlocks
.filter((block) => block.type === "html")
.map((block) => ({
className: "analytics-layout-item-html",
defaultLayout: dashboardCardLayout(block.layout ?? "full"),
id: `html:${block.id}`,
render: () => (<ReportHtmlBlock block={block} htmlOverride={blockTextOverrides[block.id]} isEditMode={activeEditMode} isMenuOpen={openMenuBlockId === block.id} onHtmlChange={updateBlockText} onCopyResult={(message, isError = false) => setCopyMessage({ isError, message })} onDeleteBlock={capabilities.canEdit ? () => deleteReportBlock(block.id) : undefined} onMenuOpenChange={(nextOpen) => {
setOpenMenuChartId(null);
setOpenMenuTableId(null);
setOpenMenuBlockId(nextOpen ? block.id : null);
}}/>)
}));
return [...chartBlocks, ...tableBlocks, ...htmlBlocks];
}, [
accessIssues,
activeSurfaceFilters,
activeEditMode,
capabilities.canEdit,
chartTextOverrides,
chartSpecOverrides,
chartTypeOverrides,
charts,
manifest,
openMenuBlockId,
openMenuChartId,
openMenuTableId,
requestEditMode,
selectedFilters,
snapshot,
tableColumnWidths,
tableTextOverrides,
tables,
visibleReportGridBlocks
]);
const reportContentBlocks = useMemo(() => {
return visibleReportGridBlocks.map((block) => {
if (block.type === "metric-strip") {
const metricCards = (block.cardIds ?? [])
.map((cardId) => cardsById.get(cardId))
.filter((card) => Boolean(card));
return {
className: "report-stack-item report-stack-item-metric-strip",
defaultLayout: reportCardLayout(block.layout),
id: block.id,
render: () => (<ReportMetricStripBlock cards={metricCards} filters={activeSurfaceFilters} id={block.id} isMenuOpen={openMenuBlockId === block.id} onCopyResult={(message, isError = false) => setCopyMessage({ isError, message })} onDeleteBlock={capabilities.canEdit ? () => deleteReportBlock(block.id) : undefined} onMenuOpenChange={(nextOpen) => {
setOpenMenuChartId(null);
setOpenMenuTableId(null);
setOpenMenuBlockId(nextOpen ? block.id : null);
}} selectedFilters={selectedFilters} snapshot={snapshot}/>)
};
}
const chart = block.chartId ? chartsById.get(block.chartId) : undefined;
const table = block.tableId ? tablesById.get(block.tableId) : undefined;
return {
className: `report-stack-item report-stack-item-${block.type}`,
defaultLayout: reportCardLayout(block.layout),
id: block.id,
render: (layout) => (<ReportBlockCard accessIssues={accessIssues} block={block} blockTextOverride={blockTextOverrides[block.id]} chart={chart} chartSpecOverride={chart ? chartSpecOverrides[chart.id] : undefined} chartTextOverride={chart ? chartTextOverrides[chart.id] : undefined} chartTypeOverride={chart ? chartTypeOverrides[chart.id] : undefined} columnWidths={table ? tableColumnWidths[table.id] ?? {} : {}} filters={activeSurfaceFilters} isBlockMenuOpen={openMenuBlockId === block.id} isChartMenuOpen={Boolean(chart && openMenuChartId === chart.id)} isEditMode={activeEditMode} isTableMenuOpen={Boolean(table && openMenuTableId === table.id)} layout={layout} manifest={manifest} onBlockMenuOpenChange={(nextOpen) => {
setOpenMenuChartId(null);
setOpenMenuTableId(null);
setOpenMenuBlockId(nextOpen ? block.id : null);
}} onBlockTextChange={updateBlockText} onChartTypeChange={updateChartType} onChartMenuOpenChange={(nextOpen) => {
setOpenMenuTableId(null);
setOpenMenuBlockId(null);
setOpenMenuChartId(chart && nextOpen ? chart.id : null);
}} onChartModalOpen={setChartModal} onColumnWidthsChange={updateTableColumnWidths} onCopyResult={(message, isError = false) => setCopyMessage({ isError, message })} onDeleteBlock={capabilities.canEdit ? () => deleteReportBlock(block.id) : undefined} onRequestEditMode={requestEditMode} onTableMenuOpenChange={(nextOpen) => {
setOpenMenuChartId(null);
setOpenMenuBlockId(null);
setOpenMenuTableId(table && nextOpen ? table.id : null);
}} onTableModalOpen={setTableModal} onTableTextChange={updateTableText} onTextChange={updateChartText} selectedFilters={selectedFilters} snapshot={snapshot} table={table} tableTextOverride={table ? tableTextOverrides[table.id] : undefined}/>)
};
});
}, [
accessIssues,
activeSurfaceFilters,
activeEditMode,
blockTextOverrides,
cardsById,
capabilities.canEdit,
chartSpecOverrides,
chartTextOverrides,
chartTypeOverrides,
chartsById,
manifest,
openMenuBlockId,
openMenuChartId,
openMenuTableId,
requestEditMode,
selectedFilters,
snapshot,
tableColumnWidths,
tableTextOverrides,
tablesById,
visibleReportGridBlocks
]);
if (error) {
return (<DashboardShell surface={manifest?.surface}>
<div className="empty-state error-state">{error}</div>
</DashboardShell>);
}
const activeFilters = activeFilterSummary(activeSurfaceFilters, selectedFilters);
const chartModalSourceChart = chartModal
? chartsById.get(chartModal.chart.id) ?? chartModal.chart
: null;
const chartModalBaseChart = chartModalSourceChart
? applyChartSpecOverride(chartModalSourceChart, chartSpecOverrides[chartModalSourceChart.id])
: null;
const chartModalRows = chartModalBaseChart
? filterRowsForDataset(getRows(snapshot, chartModalBaseChart.dataset), chartModalBaseChart.dataset, activeSurfaceFilters, selectedFilters, chartUsedFields(chartModalBaseChart))
: [];
const chartModalTypeOptions = chartModalBaseChart
? compatibleChartTypesFor(chartModalBaseChart, chartModalRows)
: [];
const chartModalRequestedType = chartModalBaseChart
? chartTypeOverrides[chartModalBaseChart.id] ?? chartModalBaseChart.type
: null;
const chartModalActiveType = chartModalRequestedType && chartModalTypeOptions.some((option) => option.type === chartModalRequestedType)
? chartModalRequestedType
: chartModalBaseChart?.type ?? null;
const activeChartModal = chartModal?.kind === "fullscreen" && chartModalBaseChart && chartModalActiveType
? {
chart: withChartType({
...chartModalBaseChart,
subtitle: chartModal.chart.subtitle,
title: chartModal.chart.title
}, chartModalActiveType)
}
: null;
if (isReport) {
return (<DashboardShell isEditMode={activeEditMode} surface="report">
<AnalyticsTopBar chrome={displayMode === "inline" ? "inline" : "full"} isEditMode={activeEditMode} manifest={manifest} onCancelEdit={cancelEditMode} onCopyResult={(message, isError = false) => setCopyMessage({ isError, message })} onEdit={requestEditMode} onRequestFullscreen={onRequestFullscreen} onSaveEdit={saveEditMode} onTitleChange={updatePageTitle} packageInfo={packageInfo} snapshot={snapshot} title={pageTitle}/>
<AccessIssueStrip issues={accessIssues}/>
{copyMessage ? (<div className={`copy-toast ${copyMessage.isError ? "error" : ""}`} role="status">
{copyMessage.message}
</div>) : null}

<AnalyticsLayoutCanvas ariaLabel="Report blocks" blocks={reportContentBlocks} cancelSelector={CARD_DRAG_CANCEL_SELECTOR} className="report-content-grid report-block-stack" isEditMode={activeEditMode} layoutResetKey={layoutResetKey} onLayoutChange={recordReportLayoutDraft} storageKey={reportStorageKey}/>
{activeChartModal ? (<ChartDetailPage accessIssue={accessIssueForChart(activeChartModal.chart, accessIssues)} chart={activeChartModal.chart} filters={activeSurfaceFilters} manifest={manifest} onChartSpecChange={updateChartSpec} onClose={() => setChartModal(null)} packageInfo={packageInfo} rows={chartModalRows} selectedFilters={selectedFilters} snapshot={snapshot}/>) : null}
{chartModal?.kind === "source" && chartModalBaseChart ? (<ChartSourceModalDialog activeFilters={activeFilters} chart={{
...chartModalBaseChart,
subtitle: chartModal.chart.subtitle,
title: chartModal.chart.title
}} manifest={manifest} onClose={() => setChartModal(null)} rows={chartModalRows} snapshot={snapshot}/>) : null}
{tableModal ? (<TableModalDialog activeFilters={activeFilters} columnWidths={tableColumnWidths[tableModal.table.id] ?? {}} filters={activeSurfaceFilters} kind={tableModal.kind} manifest={manifest} onColumnWidthsChange={updateTableColumnWidths} onClose={() => setTableModal(null)} selectedFilters={selectedFilters} snapshot={snapshot} table={tableModal.table}/>) : null}
</DashboardShell>);
}
return (<DashboardShell isEditMode={activeEditMode} surface={manifest?.surface}>
<AnalyticsTopBar chrome={displayMode === "inline" ? "inline" : "full"} isEditMode={activeEditMode} manifest={manifest} onCancelEdit={cancelEditMode} onCopyResult={(message, isError = false) => setCopyMessage({ isError, message })} onEdit={requestEditMode} onRequestFullscreen={onRequestFullscreen} onSaveEdit={saveEditMode} onTitleChange={updatePageTitle} packageInfo={packageInfo} snapshot={snapshot} title={pageTitle}/>
<AccessIssueStrip issues={accessIssues}/>
{copyMessage ? (<div className={`copy-toast ${copyMessage.isError ? "error" : ""}`} role="status">
{copyMessage.message}
</div>) : null}

<FilterToolbar filters={activeSurfaceFilters} onChange={setSelectedFilters} selectedFilters={selectedFilters} snapshot={snapshot}/>

<KpiStrip cards={cards} filters={activeSurfaceFilters} selectedFilters={selectedFilters} snapshot={snapshot}/>

<AnalyticsLayoutCanvas ariaLabel="Dashboard content" blocks={dashboardContentBlocks} cancelSelector={CARD_DRAG_CANCEL_SELECTOR} className="dashboard-content-grid" isEditMode={activeEditMode} layoutResetKey={layoutResetKey} onLayoutChange={recordDashboardLayoutDraft} storageKey={storageKey}/>
{activeChartModal ? (<ChartDetailPage accessIssue={accessIssueForChart(activeChartModal.chart, accessIssues)} chart={activeChartModal.chart} filters={activeSurfaceFilters} manifest={manifest} onChartSpecChange={updateChartSpec} onClose={() => setChartModal(null)} packageInfo={packageInfo} rows={chartModalRows} selectedFilters={selectedFilters} snapshot={snapshot}/>) : null}
{chartModal?.kind === "source" && chartModalBaseChart ? (<ChartSourceModalDialog activeFilters={activeFilters} chart={{
...chartModalBaseChart,
subtitle: chartModal.chart.subtitle,
title: chartModal.chart.title
}} manifest={manifest} onClose={() => setChartModal(null)} rows={chartModalRows} snapshot={snapshot}/>) : null}
{tableModal ? (<TableModalDialog activeFilters={activeFilters} columnWidths={tableColumnWidths[tableModal.table.id] ?? {}} filters={activeSurfaceFilters} kind={tableModal.kind} manifest={manifest} onColumnWidthsChange={updateTableColumnWidths} onClose={() => setTableModal(null)} selectedFilters={selectedFilters} snapshot={snapshot} table={tableModal.table}/>) : null}
</DashboardShell>);
}
