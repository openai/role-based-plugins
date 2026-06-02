import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { createRequire } from "node:module";
import { test } from "node:test";

const require = createRequire(import.meta.url);
const server = require("../mcp/server.cjs");

function read(relativePath) {
  return readFileSync(new URL(relativePath, import.meta.url), "utf8");
}

test("widget entrypoints load the Codex baseline before analytics tokens", () => {
  const sources = [
    read("../src/analytics-app/main.tsx"),
    read("../src/datascience-artifact-widget.jsx"),
    read("../src/datascience-chart-widget.js"),
    read("../src/datascience-table-widget.js"),
  ];

  for (const source of sources) {
    assert.ok(source.includes("codex-theme.css"));
    assert.ok(source.indexOf("codex-theme.css") < source.indexOf("tokens.css"));
  }

  const baseline = read("../src/styles/codex-theme.css");
  assert.match(baseline, /--codex-accent:/);
  assert.match(baseline, /--codex-font-sans:/);
});

test("analytics tokens alias shared roles to the Codex baseline", () => {
  const tokens = read("../src/analytics-app/tokens.css");

  assert.match(tokens, /--ds-bg: var\(--codex-bg\);/);
  assert.match(tokens, /--ds-surface: var\(--codex-panel\);/);
  assert.match(tokens, /--ds-border: var\(--codex-border\);/);
  assert.match(tokens, /--ds-shadow: var\(--codex-shadow-lg\);/);
  assert.match(tokens, /--ds-dropdown-row-height: var\(--codex-button-height\);/);

  const chartTokens = read("../src/analytics-app/charting/chart-tokens.css");
  assert.match(chartTokens, /--ds-chart-font-family: var\(--ds-font, var\(--codex-font-sans,/);
});

test("report tables retain contained horizontal scrolling and Codex-aligned reading edges", () => {
  const source = read("../src/analytics-app/tables/DataTable.jsx");
  const tableStyles = read("../src/analytics-app/tables/data-table.css");
  const styles = read("../src/analytics-app/styles.css");
  const app = read("../src/analytics-app/App.tsx");

  assert.match(source, /const DEFAULT_PAGE_SIZE = 15;/);
  assert.match(read("../src/datascience-table-widget.js"), /const TABLE_CARD_PAGE_SIZE = 15;/);
  assert.match(read("../src/analytics-app/tokens.css"), /--ds-report-content-half-width: 384px;/);
  assert.match(styles, /--report-table-content-inset: max\(var\(--ds-gutter\), calc\(50vw - var\(--ds-report-content-half-width\)\)\);/);
  assert.match(styles, /\.report-stack-item-table \.table-wrap \{[\s\S]*width: 100%;/);
  assert.match(styles, /\.report-stack-item-table \.table-wrap \{[\s\S]*max-width: 100%;/);
  assert.match(styles, /\.report-stack-item-table \.table-wrap \{[\s\S]*margin-left: 0;/);
  assert.match(styles, /\.report-stack-item-table \.table-scroll-content \{[\s\S]*padding-left: 0;/);
  assert.match(styles, /\.table-density-spacious table:not\(\.data-table-resizable\) \{/);
  assert.match(app, /minWidth: `\$\{tablePixelWidth\}px`/);
  assert.match(app, /width: `\$\{tablePixelWidth\}px`/);
  assert.match(styles, /--ds-menu-hover-bg: #2b2b2b;/);
  assert.doesNotMatch(styles, /\.report-stack-item-table \.table-wrap \{[^}]*padding-left:/);
  assert.match(styles, /\.modal-panel \{[\s\S]*background: var\(--ds-overlay-bg\);/);
  assert.match(styles, /\.native-modal\.source-modal \{[\s\S]*width: min\(800px, calc\(100vw - 48px\)\);/);
  assert.match(styles, /\.source-modal-panel \{[\s\S]*background: var\(--ds-overlay-bg\);[\s\S]*padding: 20px;/);
  assert.match(read("../src/analytics-app/tokens.css"), /--ds-menu-bg: var\(--ds-overlay-bg\);/);
  assert.match(styles, /\.metric-badge \{[\s\S]*background: var\(--ds-surface-tertiary\);/);
  assert.match(styles, /\.metric-badge\.positive \{[\s\S]*color: var\(--ds-green\);/);
  assert.match(styles, /\.metric-badge\.negative \{[\s\S]*color: var\(--ds-red\);/);
  assert.match(tableStyles, /\.data-table td \{[\s\S]*color: var\(--ds-text-secondary\);/);
  assert.match(tableStyles, /\.data-table td:first-child \{[\s\S]*color: var\(--ds-text-primary\);/);
  assert.match(source, /tableWrapRef\.current\.scrollLeft = 0/);
  assert.match(app, /const TABLE_CARD_PAGE_SIZE = 15;/);
  assert.match(app, /ref=\{tableWrapRef\}>\s*<div className="table-scroll-content">/);
  assert.match(app, /minWidth: `\$\{tablePixelWidth\}px`/);
  assert.match(app, /width: `\$\{tablePixelWidth\}px`/);
  assert.match(tableStyles, /\.table-sort-button:hover,\s*\.table-sort-button:focus-visible \{[\s\S]*border-radius: 0;/);
});

test("report top-bar title uses the compact supported text style", () => {
  const styles = read("../src/analytics-app/styles.css");
  const title = styles
    .split(".analytics-top-bar .page-title-edit-target h1 {", 2)[1]
    .split("}", 1)[0];
  const editor = styles
    .split(".analytics-top-bar .page-title-editor {", 2)[1]
    .split("}", 1)[0];

  for (const block of [title, editor]) {
    assert.match(block, /font-size: 14px;/);
    assert.match(block, /font-weight: 500;/);
    assert.match(block, /line-height: 20px;/);
    assert.match(block, /letter-spacing: -0\.13px;/);
  }
});

test("chart detail actions use edit language", () => {
  const app = read("../src/analytics-app/App.tsx");
  const widget = read("../src/datascience-chart-widget.js");

  assert.match(app, /menuItem\("Edit chart"/);
  assert.doesNotMatch(app, /Switch chart type/);
  assert.doesNotMatch(app, /<h2>Edit chart<\/h2>/);
  assert.doesNotMatch(app, /Explore chart/);
  assert.match(widget, /"Edit chart"/);
  assert.doesNotMatch(widget, /Explore chart/);
});

test("artifact top bar shows the snapshot date as the refresh label", () => {
  const app = read("../src/analytics-app/App.tsx");

  assert.match(app, /const refreshLabel = dateLabel === "Unknown" \? "Refresh" : dateLabel;/);
  assert.match(app, /<span>\{refreshLabel\}<\/span>/);
  assert.doesNotMatch(app, /<span>Refresh<\/span>\\n\{statusLabel/);
});

test("artifact chart edit modal uses contained modal chart chrome", () => {
  const app = read("../src/analytics-app/App.tsx");
  const appStyles = read("../src/analytics-app/styles.css");
  const widget = read("../src/datascience-chart-widget.js");
  const widgetStyles = read("../src/datascience-chart-widget.css");

  assert.match(app, /inline-chart-widget\?displayMode=modal/);
  assert.match(app, /displayMode: "modal"/);
  assert.match(app, /function chartWidgetSettings\(chart\)/);
  assert.match(app, /settings\s*\n\s*\}/);
  assert.match(app, /datascience-chart-widget-spec-reset/);
  assert.match(app, /onChartSpecChange\(chart\.id, null\)/);
  assert.doesNotMatch(app, /chart-explore-header/);
  assert.match(appStyles, /\.native-modal\.chart-explore-modal \{[\s\S]*width: min\(1180px, calc\(100vw - 96px\)\);/);
  assert.match(widget, /function isDetailDisplayMode\(mode = displayMode\)/);
  assert.match(widget, /raw === "modal" \|\| raw === "dialog"/);
  assert.match(widget, /modal-title-close-button/);
  assert.match(widget, /requestDisplayMode\("inline"\)/);
  assert.match(widgetStyles, /\.widget\[data-display-mode="modal"\] \.detail-topbar \{[\s\S]*display: none;/);
  assert.match(widgetStyles, /\.widget\[data-display-mode="modal"\] \.bottom-split \{[\s\S]*display: none;/);
  assert.match(widgetStyles, /\.widget\[data-display-mode="modal"\] \.modal-title-close-button \{[\s\S]*display: inline-flex;/);
  assert.match(widgetStyles, /html\[data-display-mode="modal"\],\s*body\[data-display-mode="modal"\] \{[\s\S]*overflow: hidden;/);
  assert.match(widgetStyles, /\.widget\[data-display-mode="modal"\] \.chart-shell \{[\s\S]*height: 100%;[\s\S]*min-height: 0;/);
  assert.match(widgetStyles, /\.widget:is\(\[data-display-mode="fullscreen"\], \[data-display-mode="modal"\]\) \.detail-title-section h1 \{[\s\S]*font-size: 28px;[\s\S]*line-height: 34px;/);
  assert.doesNotMatch(widget, /segmented\.className = "segmented chart-setting-segmented"/);
  assert.match(widget, /function openSettingMenu\(anchor, label, value, options, onChange\)/);
  assert.doesNotMatch(widget, /panel\.appendChild\(menuHeader\(label\)\)/);
  assert.match(widget, /function settingDropdownChip\(label, value, options, onChange\)/);
  assert.match(widget, /button\.setAttribute\("aria-haspopup", "menu"\)/);
  assert.match(widget, /button\.append\(labelEl, caretIcon\("field-pill-caret"\)\)/);
  assert.match(widget, /\? "Chart type"\s*: chartTypeLabel\(activeVisualizationType\)/);
  assert.match(widget, /if \(!detailChrome\) button\.appendChild\(field\)/);
  assert.match(widget, /visibleSeries = \{\};/);
  assert.match(widget, /function notifyChartSpecReset\(\)/);
  assert.match(widget, /type: "datascience-chart-widget-spec-reset"/);
  assert.match(widget, /closeFieldMenus\(\{ immediate: true \}\)/);
  assert.match(widgetStyles, /\.detail-title-row \{[\s\S]*width: 100%;/);
  assert.match(widgetStyles, /\.widget:is\(\[data-display-mode="fullscreen"\], \[data-display-mode="modal"\]\) \.app-main \{[\s\S]*flex: 1 1 auto;[\s\S]*width: 100%;/);
  assert.match(widgetStyles, /\.widget:is\(\[data-display-mode="fullscreen"\], \[data-display-mode="modal"\]\) \.detail-title-section h1 \{[\s\S]*flex: 1 1 auto;/);
  assert.match(widgetStyles, /\.modal-title-close-button \{[\s\S]*margin-left: auto;/);
  const expandedResetRule = widgetStyles.match(
    /\.widget:is\(\[data-display-mode="fullscreen"\], \[data-display-mode="modal"\]\) \.clear-button \{[^}]*\}/,
  );
  assert.ok(expandedResetRule);
  assert.doesNotMatch(expandedResetRule[0], /margin-left: auto/);
});

test("static exports omit interactive app chrome", () => {
  const app = read("../src/analytics-app/App.tsx");
  const widget = read("../src/datascience-chart-widget.js");

  for (const source of [app, widget]) {
    assert.match(source, /Omit the interactive top bar and app-only controls from the exported artifact/);
  }
});

test("artifact fallback uses encoded chart fields and fullscreen language", () => {
  const source = read("../src/datascience-artifact-widget.jsx");

  assert.match(source, /x: \{ field: "week", type: "(?:ordinal|temporal)" \}/);
  assert.match(source, /y: \{ field: "revenue_m", type: "quantitative", label: "Revenue"/);
  assert.doesNotMatch(source, /xField: "week"/);
  assert.doesNotMatch(source, /Open in sidebar/);
  assert.match(source, /requestArtifactDisplayMode\("fullscreen"/);
});

test("report and dashboard artifacts render inline with a single expand action", () => {
  const artifactSource = read("../src/datascience-artifact-widget.jsx");
  const app = read("../src/analytics-app/App.tsx");
  const styles = read("../src/analytics-app/styles.css");
  const host = read("../src/mcp-host.js");

  assert.match(artifactSource, /normalizeDisplayMode\([\s\S]*payload\?\.displayMode[\s\S]*\) \|\| "inline"/);
  assert.match(artifactSource, /const canRequestFullscreen =[\s\S]*displayMode !== "fullscreen";/);
  assert.match(artifactSource, /onRequestFullscreen=\{requestFullscreen\}/);
  assert.match(host, /initialDisplayMode/);
  assert.match(host, /rememberDismissedInitialDisplayMode\(name, "fullscreen"\)/);
  assert.match(host, /clearDismissedInitialDisplayMode\(name, "fullscreen"\)/);
  assert.match(host, /hasDismissedInitialDisplayMode\(name, normalized\)/);
  assert.doesNotMatch(artifactSource, /function ArtifactInlineLauncher/);
  assert.doesNotMatch(artifactSource, /showInlineLauncher/);
  assert.doesNotMatch(artifactSource, /datascience-artifact-inline-card/);
  assert.match(app, /function AnalyticsTopBar\(\{[\s\S]*onRequestFullscreen/);
  assert.match(app, /const showInlineExpand = chrome === "inline" && typeof onRequestFullscreen === "function";/);
  assert.match(app, /showInlineExpand \? \(<div className="analytics-top-bar-actions">/);
  assert.match(app, /<Expand aria-hidden="true" size=\{14\} strokeWidth=\{2\}\/>/);
  assert.match(app, /<span>Expand<\/span>/);
  assert.doesNotMatch(styles, /body\[data-display-mode="inline"\]/);
  assert.doesNotMatch(styles, /\.datascience-artifact-inline-card/);
  assert.doesNotMatch(styles, /\.datascience-artifact-display-button/);
});

test("artifact package export advertises its filesystem write behavior", () => {
  const exportTool = server.toolDefinitions().find((tool) => tool.name === "export_artifact_package");
  const renderTool = server.toolDefinitions().find((tool) => tool.name === "render_artifact");

  assert.ok(exportTool);
  assert.equal(exportTool.annotations.readOnlyHint, false);
  assert.equal(exportTool.annotations.destructiveHint, false);
  assert.equal(exportTool.annotations.idempotentHint, false);
  assert.ok(renderTool);
  assert.equal(renderTool.annotations.readOnlyHint, true);
});
