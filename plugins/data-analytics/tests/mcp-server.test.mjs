import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { createRequire } from "node:module";
import { test } from "node:test";


const require = createRequire(import.meta.url);
const server = require("../mcp/server.cjs");

function sourceQueryForTest() {
  return {
    query: {
      engine: "trino",
      sql: "SELECT category, value FROM warehouse.chart_source",
      description: "Loads category/value rows for chart tests.",
      id: "test-query",
    },
  };
}

function queryTablePayload() {
  return {
    title: "ARR trend",
    source: {
      query: {
        engine: "databricks",
        sql: "SELECT reporting_date, arr_b FROM gtm.example",
        description: "Loads ARR by reporting date for widget tests.",
        id: "query-123",
        executed_at: "2026-05-01T00:00:00Z",
      },
    },
    table: {
      columns: [
        { key: "reporting_date", label: "Reporting date", type: "date" },
        { key: "arr_b", label: "ARR", type: "number", unit: "$B" },
      ],
      rows: [
        { reporting_date: "2026-03-31", arr_b: 2.73 },
        { reporting_date: "2026-04-30", arr_b: 2.9 },
      ],
      row_count: 2,
      truncated: false,
    },
    chart: {
      type: "line",
      fields: {
        x: { field: "reporting_date", type: "temporal", time_unit: "month" },
        y: { field: "arr_b", type: "quantitative", aggregate: "sum", unit: "$B" },
      },
    },
    display: {
      baseline: 2.8,
      unit: "$B",
      controls: true,
    },
  };
}

function artifactPayload(surface = "dashboard") {
  const manifest = {
    version: 1,
    surface,
    title: "Revenue momentum",
    generatedAt: "2026-05-07T00:00:00Z",
    cards: [
      {
        id: "revenue_card",
        dataset: "weekly_revenue",
        metrics: [{ label: "Revenue", field: "revenue_m", format: "currency" }],
      },
    ],
    charts: [
      {
        id: "revenue_chart",
        title: "Revenue by segment",
        type: "bar",
        dataset: "weekly_revenue",
        sourceId: "weekly_revenue_sql",
        encodings: {
          x: { field: "segment", type: "nominal" },
          y: { field: "revenue_m", type: "quantitative" },
        },
      },
    ],
    tables: [
      {
        id: "revenue_table",
        title: "Revenue rows",
        dataset: "weekly_revenue",
        sourceId: "weekly_revenue_sql",
        columns: [
          { field: "segment", label: "Segment" },
          { field: "revenue_m", label: "Revenue", format: "currency" },
        ],
      },
    ],
    sources: [{ id: "weekly_revenue_sql", label: "Revenue SQL", path: "queries/revenue.sql" }],
  };
  if (surface === "report") {
    manifest.blocks = [
      {
        id: "summary_text",
        type: "markdown",
        body: "Revenue is concentrated in Beta.",
      },
      {
        id: "revenue_chart_block",
        type: "chart",
        chartId: "revenue_chart",
      },
      {
        id: "revenue_table_block",
        type: "table",
        tableId: "revenue_table",
      },
    ];
  } else {
    manifest.blocks = [
      {
        id: "revenue_metrics",
        type: "metric-strip",
        cardIds: ["revenue_card"],
      },
      {
        id: "revenue_chart_block",
        type: "chart",
        chartId: "revenue_chart",
      },
      {
        id: "revenue_table_block",
        type: "table",
        tableId: "revenue_table",
      },
    ];
  }
  return {
    surface,
    manifest,
    snapshot: {
      version: 1,
      generatedAt: "2026-05-07T00:00:00Z",
      status: "ready",
      datasets: {
        weekly_revenue: [
          { segment: "Alpha", revenue_m: 12 },
          { segment: "Beta", revenue_m: 18 },
        ],
      },
    },
    sources: [
      {
        id: "weekly_revenue_sql",
        query: {
          engine: "trino",
          sql: "SELECT segment, revenue_m FROM warehouse.weekly_revenue",
          description: "Loads weekly revenue by segment for artifact tests.",
        },
      },
    ],
  };
}

async function widgetResourceHtml(uri) {
  const response = await server.handleRpc({
    jsonrpc: "2.0",
    id: 1,
    method: "resources/read",
    params: { uri },
  });
  return response.result.contents[0].text;
}

test("MCP widget resources serve bundled apps, not local development redirects", async () => {
  const chartHtml = await widgetResourceHtml(server.CHART_WIDGET_URI);
  const tableHtml = await widgetResourceHtml(server.TABLE_WIDGET_URI);
  const artifactHtml = await widgetResourceHtml(server.ARTIFACT_WIDGET_URI);

  for (const html of [chartHtml, tableHtml, artifactHtml]) {
    assert.doesNotMatch(html, /Redirecting to the local widget source/);
    assert.doesNotMatch(html, /window\.location\.replace\(target\)/);
  }
  assert.match(chartHtml, /@modelcontextprotocol\/ext-apps/);
  assert.match(tableHtml, /@modelcontextprotocol\/ext-apps/);
  assert.match(artifactHtml, /Data Analytics Artifact App/);
});

test("JavaScript MCP server renders hosted artifact payloads", () => {
  const payload = server.callTool("render_artifact", artifactPayload("report"));

  assert.equal(payload.widget_type, "artifact");
  assert.equal(payload.surface, "report");
  assert.equal(payload.manifest.title, "Revenue momentum");
  assert.equal(payload.snapshot.datasets.weekly_revenue[1].segment, "Beta");
});

test("JavaScript MCP server exposes only canonical tool names", () => {
  const names = server.toolDefinitions().map((tool) => tool.name);
  assert.deepEqual(names, [
    "validate_artifact",
    "render_artifact",
    "export_artifact_package",
    "render_chart",
    "render_table",
  ]);

  assert.throws(
    () => server.callTool("render_datascience_chart", queryTablePayload()),
    /unknown Data Analytics widget tool: render_datascience_chart/,
  );
});

test("JavaScript MCP server advertises Data Analytics icons on server info", async () => {
  assert.equal(server.DATA_ANALYTICS_ICONS[0].mimeType, "image/svg+xml");
  assert.deepEqual(server.DATA_ANALYTICS_ICONS[0].sizes, ["24x24"]);
  assert.match(server.DATA_ANALYTICS_ICONS[0].src, /^data:image\/svg\+xml;base64,/);
  assert.equal(server.DATA_ANALYTICS_ICONS[1].mimeType, "image/png");
  assert.deepEqual(server.DATA_ANALYTICS_ICONS[1].sizes, ["360x360"]);
  assert.match(server.DATA_ANALYTICS_ICONS[1].src, /^data:image\/png;base64,/);

  for (const tool of server.toolDefinitions()) {
    assert.equal(tool.icons, undefined);
  }

  const response = await server.handleRpc({
    jsonrpc: "2.0",
    id: 1,
    method: "initialize",
    params: {},
  });
  assert.equal(response.result.serverInfo.title, "Data Analytics Widgets");
  assert.equal(
    response.result.serverInfo.description,
    "Render Data Analytics charts, tables, dashboards, and report artifacts.",
  );
  assert.deepEqual(response.result.serverInfo.icons, server.DATA_ANALYTICS_ICONS);
});

test("JavaScript MCP server validates artifact payloads without widget metadata", async () => {
  const payload = server.callTool("validate_artifact", artifactPayload("report"));

  assert.equal(payload.ok, true);
  assert.equal(payload.validation_type, "artifact");
  assert.equal(payload.surface, "report");
  assert.equal(payload.manifest_title, "Revenue momentum");
  assert.equal(payload.dataset_count, 1);
  assert.equal(payload.artifact_payload.widget_type, "artifact");

  const validateTool = server
    .toolDefinitions()
    .find((tool) => tool.name === "validate_artifact");
  assert.ok(validateTool);
  assert.equal(validateTool._meta, undefined);

  const rpcPayload = await server.handleRpc({
    jsonrpc: "2.0",
    id: 1,
    method: "tools/call",
    params: { name: "validate_artifact", arguments: artifactPayload("report") },
  });
  assert.equal(rpcPayload.result.structuredContent.ok, true);
  assert.equal(rpcPayload.result._meta, undefined);
});

test("JavaScript MCP server rejects artifact chart y encodings without numeric values", () => {
  const args = artifactPayload("report");
  args.manifest.charts[0] = {
    ...args.manifest.charts[0],
    title: "Product-line share by country",
    dataset: "product_line_share",
    encodings: {
      x: { field: "country_name", type: "nominal" },
      y: { field: "product_line", type: "nominal" },
    },
  };
  args.snapshot.datasets.product_line_share = [
    { country_name: "India", product_line: "Consumer", share_pct: 71 },
    { country_name: "India", product_line: "API", share_pct: 18 },
  ];

  assert.throws(
    () => server.callTool("validate_artifact", args),
    /manifest\.charts\[0\]\.encodings\.y\.field "product_line" must reference a numeric dataset field/,
  );
});

test("JavaScript MCP server rejects legacy artifact chart fields", () => {
  const args = artifactPayload("report");
  args.manifest.charts[0].xField = "segment";

  assert.throws(
    () => server.callTool("validate_artifact", args),
    /manifest\.charts\[0\]\.xField is not supported for artifact charts; use encodings/,
  );
});

test("JavaScript MCP server rejects table-shaped artifact snapshot datasets", () => {
  const args = artifactPayload("report");
  args.snapshot.datasets.weekly_revenue = {
    columns: [
      { key: "segment", label: "Segment" },
      { key: "revenue_m", label: "Revenue", type: "currency" },
    ],
    rows: args.snapshot.datasets.weekly_revenue,
  };

  assert.throws(
    () => server.callTool("render_artifact", args),
    /snapshot\.datasets\.weekly_revenue must be an array of row objects/,
  );
});

test("JavaScript MCP server rejects key aliases for report table columns", () => {
  const args = artifactPayload("report");
  args.manifest.tables[0].columns = [
    { key: "segment", label: "Segment" },
    { key: "revenue_m", label: "Revenue", type: "currency" },
  ];

  assert.throws(
    () => server.callTool("render_artifact", args),
    /manifest\.tables\["revenue_table"\]\.columns\[0\]\.field/,
  );
});

test("JavaScript MCP server accepts body strings in report markdown blocks", () => {
  const args = artifactPayload("report");
  args.manifest.blocks[0] = {
    id: "summary_text",
    type: "markdown",
    body: "## Summary\n\n- **Beta** leads\n- [Source](https://example.com)",
  };

  const payload = server.callTool("render_artifact", args);

  assert.equal(payload.manifest.blocks[0].body, "## Summary\n\n- **Beta** leads\n- [Source](https://example.com)");
});

test("JavaScript MCP server rejects legacy narrative fields and removed block types", () => {
  const args = artifactPayload("report");
  args.manifest.blocks[0].markdown = "Legacy markdown field";
  delete args.manifest.blocks[0].body;
  assert.throws(
    () => server.callTool("render_artifact", args),
    /uses markdown, but markdown blocks render body/,
  );

  const titled = artifactPayload("report");
  titled.manifest.blocks[0].title = "Legacy title";
  titled.manifest.blocks[0].content = "Legacy content";
  delete titled.manifest.blocks[0].body;
  assert.throws(
    () => server.callTool("render_artifact", titled),
    /uses content, but markdown blocks render body/,
  );

  const bodyArray = artifactPayload("report");
  bodyArray.manifest.blocks[0].body = ["Legacy array body"];
  assert.throws(
    () => server.callTool("render_artifact", bodyArray),
    /body must be a non-empty string/,
  );

  const textType = artifactPayload("report");
  textType.manifest.blocks[0].type = "text";
  assert.throws(
    () => server.callTool("render_artifact", textType),
    /type must be one of markdown, metric-strip, chart, table, html/,
  );

  const removedType = artifactPayload("report");
  removedType.manifest.blocks.push({
    id: "next_steps",
    type: "recommendation",
    body: "Review account drivers.",
  });
  assert.throws(
    () => server.callTool("render_artifact", removedType),
    /type must be one of markdown, metric-strip, chart, table, html/,
  );
});

test("JavaScript MCP server preserves inline ordered-list markers in report body", () => {
  const args = artifactPayload("report");
  args.manifest.blocks[0] = {
    id: "summary_text",
    type: "markdown",
    body: "1. Review account drivers 2. Ask account teams for context 3. Monitor next week",
  };
  args.manifest.blocks.push({
    id: "questions_text",
    type: "markdown",
    body: "1. Is the gain durable? 2. Which migrations explain it?",
  });

  const payload = server.callTool("render_artifact", args);

  assert.equal(
    payload.manifest.blocks[0].body,
    "1. Review account drivers 2. Ask account teams for context 3. Monitor next week",
  );
  assert.equal(
    payload.manifest.blocks[3].body,
    "1. Is the gain durable? 2. Which migrations explain it?",
  );
});

test("JavaScript MCP server leaves percent chart scale to the manifest data contract", () => {
  const args = artifactPayload("report");
  args.manifest.charts[0].valueFormat = "percent";
  args.manifest.charts[0].encodings.y = { field: "share", type: "quantitative" };
  args.snapshot.datasets.weekly_revenue = [
    { segment: "Alpha", share: 2.0 },
    { segment: "Beta", share: 0.851 },
  ];

  assert.equal(server.callTool("validate_artifact", args).ok, true);
});

test("JavaScript MCP server requires explicit artifact chart source links", () => {
  const args = artifactPayload("report");
  delete args.manifest.charts[0].sourceId;

  assert.throws(
    () => server.callTool("validate_artifact", args),
    /actual SQL query text/,
  );
});

test("JavaScript MCP server accepts custom HTML artifact blocks", () => {
  const args = artifactPayload("report");
  args.manifest.blocks.push({
    id: "custom_html",
    type: "html",
    body: '<section style="font: 14px sans-serif"><strong>Custom HTML</strong><div data-value="42"></div></section>',
  });

  const payload = server.callTool("render_artifact", args);

  assert.equal(payload.manifest.blocks[3].type, "html");
  assert.match(payload.manifest.blocks[3].body, /Custom HTML/);

  const htmlField = artifactPayload("report");
  htmlField.manifest.blocks.push({
    id: "custom_html",
    type: "html",
    html: "<strong>Custom HTML</strong>",
  });
  assert.throws(
    () => server.callTool("render_artifact", htmlField),
    /uses html, but html blocks render body/,
  );

  const fixedHeight = artifactPayload("report");
  fixedHeight.manifest.blocks.push({
    id: "custom_html",
    type: "html",
    body: "<strong>Custom HTML</strong>",
    height: 240,
  });
  assert.throws(
    () => server.callTool("render_artifact", fixedHeight),
    /height is not supported for html blocks/,
  );

  const missingHtml = artifactPayload("report");
  missingHtml.manifest.blocks.push({
    id: "custom_html",
    type: "html",
  });

  assert.throws(
    () => server.callTool("validate_artifact", missingHtml),
    /manifest\.blocks\[3\]\.body must be a non-empty HTML string/,
  );
});

test("JavaScript MCP server accepts additional ordered report blocks", () => {
  const args = artifactPayload("report");
  args.manifest.blocks.push({
    id: "questions_text",
    type: "markdown",
    body: "- Is the revenue shift durable?",
  });

  const payload = server.callTool("render_artifact", args);

  assert.equal(payload.manifest.blocks[3].id, "questions_text");
});

test("JavaScript MCP server validates metric-strip blocks", () => {
  const args = artifactPayload("report");
  args.manifest.blocks.unshift({
    id: "headline_metrics",
    type: "metric-strip",
    cardIds: ["revenue_card"],
  });

  const payload = server.callTool("validate_artifact", args);
  assert.equal(payload.ok, true);

  const missingCard = artifactPayload("report");
  missingCard.manifest.blocks.unshift({
    id: "headline_metrics",
    type: "metric-strip",
    cardIds: ["missing_card"],
  });
  assert.throws(
    () => server.callTool("validate_artifact", missingCard),
    /cardIds\[0\] does not match a manifest card/,
  );
});

test("funnel labels use an explicit high-contrast fill", () => {
  const chartTokens = readFileSync(
    new URL("../src/analytics-app/charting/chart-tokens.css", import.meta.url),
    "utf8",
  );
  const appCss = readFileSync(new URL("../src/analytics-app/styles.css", import.meta.url), "utf8");

  assert.match(chartTokens, /--ds-chart-funnel-label: #ffffff;/);
  for (const css of [chartTokens, appCss]) {
    const funnelLabelBlock = css.split(".funnel-label", 2)[1].split("}", 1)[0];
    assert.match(funnelLabelBlock, /fill: var\(--ds-chart-funnel-label, #ffffff\);/);
    assert.doesNotMatch(funnelLabelBlock, /mix-blend-mode/);
    assert.doesNotMatch(funnelLabelBlock, /fill: var\(--ds-surface/);
  }
});

test("bar charts render direct value labels without hover", () => {
  const renderer = readFileSync(
    new URL("../src/analytics-app/charting/ChartRenderer.tsx", import.meta.url),
    "utf8",
  );
  const chartTokens = readFileSync(
    new URL("../src/analytics-app/charting/chart-tokens.css", import.meta.url),
    "utf8",
  );

  assert.match(renderer, /function shouldShowBarValueLabels/);
  assert.match(renderer, /function visibleBarValueLabelSides/);
  assert.match(renderer, /const showBarValueLabels = shouldShowBarValueLabels/);
  assert.match(renderer, /barValueLabelSides\.hasNegative/);
  assert.match(renderer, /barValueLabelSides\.hasNonNegative/);
  assert.match(renderer, /<LabelList/);
  assert.match(renderer, /renderBarValueLabel/);
  assert.match(chartTokens, /\.chart-bar-value-label/);
});

test("signed vertical bar labels are positioned outside negative bars", () => {
  const renderer = readFileSync(
    new URL("../src/analytics-app/charting/ChartRenderer.tsx", import.meta.url),
    "utf8",
  );
  const labelRenderer = renderer
    .split("function renderBarValueLabel", 2)[1]
    .split("function categoryBarTooltipColor", 1)[0];

  assert.match(labelRenderer, /const top = Math\.min\(numericY, numericY \+ numericHeight\);/);
  assert.match(labelRenderer, /const bottom = Math\.max\(numericY, numericY \+ numericHeight\);/);
  assert.match(labelRenderer, /y=\{isNegative \? bottom \+ BAR_NEGATIVE_VALUE_LABEL_OFFSET : top - BAR_VALUE_LABEL_OFFSET\}/);
});

test("signed vertical bar labels reserve compact axis clearance", () => {
  const labelRenderer = readFileSync(
    new URL("../src/analytics-app/charting/ChartRenderer.tsx", import.meta.url),
    "utf8",
  );
  assert.match(labelRenderer, /const BAR_NEGATIVE_VALUE_LABEL_AXIS_GUTTER = 40;/);
});

test("encoded funnel charts keep a single series even when color is present", () => {
  const helpers = readFileSync(
    new URL("../src/analytics-app/charting/chart-app-helpers.tsx", import.meta.url),
    "utf8",
  );

  assert.match(helpers, /if \(chart\.type === "funnel" \|\| !colorField \|\| shouldKeepSignedBarAsSingleSeries/);
});

test("encoded grouped scatter rows preserve size and label fields", () => {
  const helpers = readFileSync(
    new URL("../src/analytics-app/charting/chart-app-helpers.tsx", import.meta.url),
    "utf8",
  );
  const groupedSeriesBlock = helpers
    .split("const seriesFields = new Map", 2)[1]
    .split("const rowsByX = new Map", 1)[0];

  assert.match(groupedSeriesBlock, /if \(chart\.type === "scatter"\)/);
  assert.match(groupedSeriesBlock, /rows: rows\.map/);
  assert.match(groupedSeriesBlock, /\{ \.\.\.row, \[seriesField\]: row\[yField\] \}/);
});

test("encoded grouped scatter renders each bubble from the encoded y field", () => {
  const renderer = readFileSync(
    new URL("../src/analytics-app/charting/ChartRenderer.tsx", import.meta.url),
    "utf8",
  );
  const scatterBlock = renderer
    .split(') : chart.type === "scatter" ? (', 2)[1]
    .split(') : chart.type === "area" || chart.type === "stackedArea" ?', 1)[0];

  assert.match(renderer, /const scatterYField = chart\.type === "scatter" \? chartEncodingField\(chart, "y"\) : undefined;/);
  assert.match(scatterBlock, /renderYAxis\(scatterYField \?\? firstSeries\.field\)/);
  assert.match(scatterBlock, /const seriesRows = rows\.filter\(\(row\) => asNumber\(row\[series\.field\]\) != null\);/);
  assert.match(scatterBlock, /const scatterDataKey = scatterYField && seriesRows\.some\(\(row\) => asNumber\(row\[scatterYField\]\) != null\)/);
  assert.match(scatterBlock, /data=\{seriesRows\}/);
  assert.match(scatterBlock, /dataKey=\{scatterDataKey\}/);
});

test("legend buttons stay transparent at rest while exposing hover and focus states", () => {
  const chartTokens = readFileSync(
    new URL("../src/analytics-app/charting/chart-tokens.css", import.meta.url),
    "utf8",
  );

  assert.match(chartTokens, /\.chart-legend-button:hover/);
  assert.match(chartTokens, /\.chart-legend-button:focus-visible/);
  assert.match(chartTokens, /\.chart-legend-button \{[\s\S]*border: 0;[\s\S]*background: transparent;/);
  assert.match(chartTokens, /\.chart-legend-button:hover \{[\s\S]*color: var\(--ds-chart-text\);/);
  assert.match(chartTokens, /box-shadow: 0 0 0 3px/);
});

test("source data modal tables fill the available modal width", () => {
  const app = readFileSync(new URL("../src/analytics-app/App.tsx", import.meta.url), "utf8");
  const css = readFileSync(new URL("../src/analytics-app/styles.css", import.meta.url), "utf8");

  assert.match(app, /className="source-data-table"/);
  assert.match(css, /\.source-data-table \{/);
  assert.match(css, /\.source-data-table \.table-scroll-content \{/);
  assert.match(css, /width: 100%;/);
  assert.match(css, /min-width: 100%;/);
});

test("funnel shapes use Recharts label view box geometry", () => {
  const renderer = readFileSync(
    new URL("../src/analytics-app/charting/ChartRenderer.tsx", import.meta.url),
    "utf8",
  );
  const shapeRenderer = renderer
    .split("function renderRoundedFunnelShape", 2)[1]
    .split("function renderFunnelCenterLabel", 1)[0];

  assert.match(shapeRenderer, /labelViewBox\?\.x \?\? x/);
  assert.match(shapeRenderer, /labelViewBox\?\.y \?\? y/);
  assert.match(shapeRenderer, /labelViewBox\?\.upperWidth \?\? upperWidth/);
  assert.match(shapeRenderer, /labelViewBox\?\.lowerWidth \?\? lowerWidth/);
  assert.match(shapeRenderer, /labelViewBox\?\.height \?\? height/);
});

test("category x-axis labels wrap when crowded and rotate only when requested", () => {
  const renderer = readFileSync(
    new URL("../src/analytics-app/charting/ChartRenderer.tsx", import.meta.url),
    "utf8",
  );
  const rotationPolicy = renderer
    .split("function shouldRotateCategoryXAxisLabels", 2)[1]
    .split("function shouldWrapCategoryXAxisLabels", 1)[0];
  const wrappingHeuristic = renderer
    .split("function shouldWrapCategoryXAxisLabels", 2)[1]
    .split("function getFunnelStageColor", 1)[0];

  assert.match(rotationPolicy, /categoryLabelPolicy === "rotate"/);
  assert.match(wrappingHeuristic, /availableWidth: number/);
  assert.match(wrappingHeuristic, /labelPolicy === "wrap"/);
  assert.match(wrappingHeuristic, /longestLabelWidth <= labelSlotWidth\) return false/);
  assert.match(wrappingHeuristic, /if \(maxLength >= CATEGORY_X_AXIS_LONG_LABEL_LENGTH\) return true/);
  assert.match(renderer, /function WrappedCategoryXAxisTick/);
});

test("numeric axis ticks omit repeated units while axis titles carry unit context", () => {
  const renderer = readFileSync(
    new URL("../src/analytics-app/charting/ChartRenderer.tsx", import.meta.url),
    "utf8",
  );
  const helpers = readFileSync(
    new URL("../src/analytics-app/charting/chart-app-helpers.tsx", import.meta.url),
    "utf8",
  );
  const transforms = readFileSync(
    new URL("../src/analytics-app/charting/chart-transforms.ts", import.meta.url),
    "utf8",
  );
  const numericTick = renderer
    .split("function NumericYAxisTick", 2)[1]
    .split("function XAxisEndpointTick", 1)[0];
  const horizontalBar = renderer
    .split('horizontal && !stacked && (chart.type === "bar" || chart.type === "horizontalBar") ? (', 2)[1]
    .split(") : horizontal && stacked && (", 1)[0];

  assert.match(numericTick, /formatValue\(payload\?\.value, valueFormat\)/);
  assert.doesNotMatch(numericTick, /\bunit\b/);
  assert.doesNotMatch(renderer, /tickFormatter=\{\(value\) => formatValue\(value, [^}\n]*chart\.unit/);
  assert.match(transforms, /labels: ticks\.map\(\(value\) => formatValue\(value, chart\.valueFormat\)\)/);
  assert.match(helpers, /function chartEncodingAxisTitle/);
  assert.match(helpers, /return `\$\{label\} \(\$\{unit\}\)`/);
  assert.match(horizontalBar, /<XAxis[^>]*label=\{horizontalValueAxisLabel\}/);
  assert.match(horizontalBar, /<YAxis[^>]*label=\{horizontalCategoryAxisLabel\}/);
  assert.doesNotMatch(horizontalBar, /label=\{yAxisLabel\}/);
  assert.doesNotMatch(horizontalBar, /label=\{xAxisLabel\}/);
});

test("the top bar uses the main page background surface", () => {
  const styles = readFileSync(new URL("../src/analytics-app/styles.css", import.meta.url), "utf8");
  const topBar = styles
    .split(".analytics-top-bar {", 2)[1]
    .split("}", 1)[0];

  assert.match(topBar, /background: var\(--ds-bg\);/);
  assert.doesNotMatch(topBar, /background: var\(--ds-surface\);/);
});

test("artifact table movement cells render explicit positive and negative signs", () => {
  const app = readFileSync(new URL("../src/analytics-app/App.tsx", import.meta.url), "utf8");
  const tableFormatter = app
    .split("function formatTableCellValue", 2)[1]
    .split("function normalizedTableTextLength", 1)[0];

  assert.match(tableFormatter, /tableColumnLooksLikeMovement\(column\)/);
  assert.match(tableFormatter, /numeric == null \|\| numeric === 0/);
  assert.match(tableFormatter, /return `\$\{numeric > 0 \? "\+" : ""\}\$\{rendered\}`/);
  assert.match(app, /tableCellMovementClass\(column, value\)/);
});

test("artifact card chart type menu is limited by data shape", () => {
  const compatibility = readFileSync(
    new URL("../src/analytics-app/charting/chart-compatibility.ts", import.meta.url),
    "utf8",
  );
  const helpers = readFileSync(
    new URL("../src/analytics-app/charting/chart-app-helpers.tsx", import.meta.url),
    "utf8",
  );
  const app = readFileSync(new URL("../src/analytics-app/App.tsx", import.meta.url), "utf8");

  assert.match(compatibility, /export function compatibleChartTypesForDataShape/);
  assert.match(compatibility, /const FUNNEL_SHAPE_TYPES: ChartType\[\] = \["bar", "funnel"\]/);
  assert.match(compatibility, /types: \["bar", "leaderboard"\]/);
  assert.match(compatibility, /const HIDDEN_BAR_VARIANT_TYPE_LIST: ChartType\[\] = \[/);
  assert.match(compatibility, /if \(chart\.type === "funnel" \|\| chart\.intent === "funnel"\) return FUNNEL_SHAPE_TYPES;/);
  assert.match(helpers, /export function compatibleChartTypesForArtifactCard/);
  assert.equal((app.match(/compatibleChartTypesForArtifactCard\(overriddenChart, chartRows\)/g) || []).length, 2);
  assert.match(app, /applyChartSpecOverride\(chart, chartSpecOverrides\[chart\.id\]\)/);
  assert.match(app, /const chartModalTypeOptions = chartModalBaseChart\s+\?\s+compatibleChartTypesFor\(chartModalBaseChart, chartModalRows\)/);
});

test("artifact data source dialogs use sectioned shared table content", () => {
  const app = readFileSync(new URL("../src/analytics-app/App.tsx", import.meta.url), "utf8");
  const styles = readFileSync(new URL("../src/analytics-app/styles.css", import.meta.url), "utf8");

  assert.match(app, /<h3>Details<\/h3>/);
  assert.match(app, /<h3>Source query<\/h3>/);
  assert.match(app, /<h3>Data table<\/h3>/);
  assert.match(app, /function SourceDataTable/);
  assert.match(app, /className="source-data-table"/);
  assert.match(app, /<TableContent allowColumnResize=\{false\} columnWidths=/);
  assert.doesNotMatch(app, /function SourcePreviewRows/);
  assert.match(app, /className="modal-close-button"/);
  assert.match(app, /useModalScrollLock\(true\)/);
  assert.match(styles, /\.native-modal\.source-modal/);
  assert.match(styles, /\.source-query \{[\s\S]*?overflow-x: hidden;[\s\S]*?white-space: pre-wrap;/);
});

test("JavaScript MCP server rejects ready artifacts with access issues", () => {
  const args = artifactPayload("report");
  args.snapshot.accessIssues = [
    {
      id: "optional_join_denied",
      sourceId: "exploratory_join",
      message: "Optional use-case join was not readable.",
    },
  ];

  assert.throws(
    () => server.callTool("render_artifact", args),
    /\$\.snapshot\.accessIssues is only allowed when \$\.snapshot\.status is partial or blocked/,
  );
});

test("JavaScript MCP server rejects malformed report block shapes before rendering", () => {
  const missingTitle = artifactPayload("report");
  delete missingTitle.manifest.title;
  assert.throws(
    () => server.callTool("render_artifact", missingTitle),
    /\$\.manifest\.title is required for artifact rendering/,
  );

  const blankTitle = artifactPayload("report");
  blankTitle.manifest.title = "  ";
  assert.throws(
    () => server.callTool("validate_artifact", blankTitle),
    /\$\.manifest\.title is required for artifact rendering/,
  );

  const withAudience = artifactPayload("report");
  withAudience.manifest.audience = "product stakeholders";
  assert.throws(
    () => server.callTool("validate_artifact", withAudience),
    /\$\.manifest\.audience is not supported/,
  );

  const withFreshness = artifactPayload("report");
  withFreshness.manifest.freshness = { snapshotPath: "data/snapshot.json" };
  assert.throws(
    () => server.callTool("validate_artifact", withFreshness),
    /\$\.manifest\.freshness is not supported/,
  );

  const withLegacyMetricDelta = artifactPayload("report");
  withLegacyMetricDelta.manifest.cards[0].deltaField = "wow";
  assert.throws(
    () => server.callTool("validate_artifact", withLegacyMetricDelta),
    /\$\.manifest\.cards\[0\]\.deltaField is not supported; use metrics\[\]/,
  );

  const withInitialView = artifactPayload("report");
  withInitialView.initial_view = { displayMode: "inline" };
  assert.throws(
    () => server.callTool("render_artifact", withInitialView),
    /initial_view is not supported/,
  );

  const withDefinitions = artifactPayload("report");
  withDefinitions.snapshot.definitions = [{ metric: "Revenue", definition: "Booked usage." }];
  assert.throws(
    () => server.callTool("validate_artifact", withDefinitions),
    /\$\.snapshot\.definitions is not supported/,
  );

  const noBlocks = artifactPayload("report");
  delete noBlocks.manifest.blocks;
  assert.throws(
    () => server.callTool("render_artifact", noBlocks),
    /must contain top-level artifact blocks/,
  );
});

test("JavaScript MCP server allows a visible report heading that matches the report title", () => {
  const args = artifactPayload("report");
  args.manifest.blocks[0].body = "# Revenue momentum";

  assert.equal(server.callTool("validate_artifact", args).ok, true);
});

test("JavaScript MCP server requires canonical dashboard blocks", () => {
  const noBlocks = artifactPayload("dashboard");
  delete noBlocks.manifest.blocks;
  assert.throws(
    () => server.callTool("render_artifact", noBlocks),
    /must contain top-level artifact blocks/,
  );

});

test("JavaScript MCP server requires reports to include a chart visualization", () => {
  const args = artifactPayload("report");
  args.manifest.blocks = args.manifest.blocks.filter((block) => block.type !== "chart");

  assert.throws(
    () => server.callTool("validate_artifact", args),
    /must include at least one chart block for report artifacts/,
  );
  assert.throws(
    () => server.callTool("render_artifact", args),
    /must include at least one chart block for report artifacts/,
  );
});

test("JavaScript MCP server advertises artifact handoff before fallback widgets", () => {
  const artifactTool = server
    .toolDefinitions()
    .find((tool) => tool.name === "render_artifact");
  const validateTool = server
    .toolDefinitions()
    .find((tool) => tool.name === "validate_artifact");

  assert.ok(artifactTool);
  assert.ok(validateTool);
  assert.match(server.SERVER_INSTRUCTIONS, /^Before rendering a report or dashboard artifact/);
  assert.match(server.SERVER_INSTRUCTIONS, /manifest\.blocks/);
  assert.match(server.SERVER_INSTRUCTIONS, /first markdown block whose body is a # heading matching manifest\.title/);
  assert.match(validateTool.description, /without rendering a hosted widget/);
  assert.equal(validateTool._meta, undefined);
  assert.match(artifactTool.description, /dashboard or report artifact/);
  assert.match(artifactTool.description, /Call validate_artifact first/);
  assert.match(artifactTool.inputSchema.properties.manifest.description, /top-level manifest\.blocks/);
  assert.match(artifactTool.inputSchema.properties.manifest.description, /first content heading/);
  assert.match(artifactTool.inputSchema.properties.manifest.properties.blocks.description, /type "html"/);
  assert.match(artifactTool.inputSchema.properties.manifest.properties.title.description, /first content heading/);
  const manifestSchema = artifactTool.inputSchema.properties.manifest;
  const cardSchema = manifestSchema.properties.cards.items;
  assert.ok(cardSchema.required.includes("metrics"));
  assert.equal(cardSchema.properties.valueField, undefined);
  assert.equal(cardSchema.properties.metrics.items.properties.field.type, "string");

  const tableColumnSchema = manifestSchema.properties.tables.items.properties.columns.items;
  assert.ok(tableColumnSchema.required.includes("field"));
  assert.equal(tableColumnSchema.properties.key, undefined);

  const blockSchema = manifestSchema.properties.blocks.items;
  assert.ok(blockSchema.required.includes("id"));
  assert.equal(blockSchema.properties.markdown, undefined);
  assert.deepEqual(artifactTool._meta.ui, {
    resourceUri: server.ARTIFACT_WIDGET_URI,
    visibility: ["model"],
  });
});

test("JavaScript MCP server rejects artifact source and safety violations", () => {
  const args = artifactPayload();
  args.sources[0].id = "not_declared";
  assert.throws(
    () => server.callTool("render_artifact", args),
    /declared in manifest\.sources/,
  );

  const unsafe = artifactPayload();
  unsafe.snapshot.datasets.weekly_revenue[0].customer_email = "person@example.com";
  assert.throws(
    () => server.callTool("render_artifact", unsafe),
    /looks unsafe/,
  );
});

test("JavaScript MCP server allows reviewed customer dimensions in artifacts", () => {
  const args = artifactPayload();
  args.contains_sensitive_data = true;
  args.snapshot.datasets.weekly_revenue[0].customer_name = "Acme Corp";

  const payload = server.callTool("render_artifact", args);

  assert.equal(payload.widget_type, "artifact");
  assert.equal(payload.snapshot.datasets.weekly_revenue[0].customer_name, "Acme Corp");
});

test("JavaScript MCP server renders query-shaped chart payloads", () => {
  const payload = server.callTool("render_chart", queryTablePayload());

  assert.equal(payload.widget_type, "chart");
  assert.equal(payload.source.query.id, "query-123");
  assert.equal(payload.chart.type, "line");
  assert.equal(payload.chart_spec.type, "line");
  assert.equal(payload.chart_spec.encodings.x.field, "reporting_date");
  assert.equal(payload.chart_spec.encodings.y.field, "arr_b");
  assert.equal("xField" in payload.chart_spec, false);
  assert.equal("series" in payload.chart_spec, false);
  assert.equal(payload.chart_spec.xAxisTitle, undefined);
  assert.equal(payload.chart_spec.yAxisTitle, undefined);
  assert.equal(payload.chart_spec.unit, "$B");
  assert.equal("referenceLines" in payload.chart_spec, false);
  assert.equal("chart_rows" in payload, false);
  assert.equal("x_field" in payload, false);
  assert.equal("y_field" in payload, false);
  assert.equal("x_axis_title" in payload, false);
  assert.equal("y_axis_title" in payload, false);
  assert.equal("time_unit" in payload, false);
  assert.deepEqual(payload.data, [
    {
      reporting_date: "2026-03-31",
      arr_b: 2.73,
      x: "2026-03-31",
      y: 2.73,
      size: null,
      series: "ARR",
    },
    {
      reporting_date: "2026-04-30",
      arr_b: 2.9,
      x: "2026-04-30",
      y: 2.9,
      size: null,
      series: "ARR",
    },
  ]);
});

test("JavaScript MCP server requires model-provided chart type and fields", () => {
  const missingType = queryTablePayload();
  delete missingType.chart.type;
  assert.throws(() => server.callTool("render_chart", missingType), /chart\.type is required/);

  const missingX = queryTablePayload();
  delete missingX.chart.fields.x;
  assert.throws(() => server.callTool("render_chart", missingX), /chart\.fields\.x\.field is required/);

  const missingY = queryTablePayload();
  delete missingY.chart.fields.y;
  assert.throws(() => server.callTool("render_chart", missingY), /chart\.fields\.y\.field is required/);
});

test("JavaScript MCP server accepts custom chart axis titles", () => {
  const args = queryTablePayload();
  args.display.x_axis_title = "Fiscal month";
  args.display.y_axis_title = "ARR, billions";

  const payload = server.callTool("render_chart", args);

  assert.equal(payload.display.x_axis_title, "Fiscal month");
  assert.equal(payload.display.y_axis_title, "ARR, billions");
  assert.equal(payload.chart_spec.xAxisTitle, "Fiscal month");
  assert.equal(payload.chart_spec.yAxisTitle, "ARR, billions");
  assert.equal("x_label" in payload, false);
  assert.equal("y_label" in payload, false);
});

test("JavaScript MCP server normalizes heatmap encodings to widget field roles", () => {
  const payload = server.callTool("render_chart", {
    title: "Heatmap",
    source: {
      query: {
        engine: "trino",
        sql: "SELECT day_name, segment, score FROM warehouse.heatmap_source",
        id: "heatmap-query",
      },
    },
    table: {
      columns: [
        { key: "day_name", label: "Day", type: "text" },
        { key: "segment", label: "Segment", type: "text" },
        { key: "score", label: "Score", type: "number" },
      ],
      rows: [
        { day_name: "Mon", segment: "Self-serve", score: 18 },
        { day_name: "Mon", segment: "Enterprise", score: 26 },
        { day_name: "Tue", segment: "Self-serve", score: 21 },
        { day_name: "Tue", segment: "Enterprise", score: 31 },
      ],
    },
    chart: {
      type: "heatmap",
      fields: {
        x: { field: "day_name", type: "ordinal" },
        y: { field: "segment", type: "nominal" },
        color: { field: "score", type: "quantitative" },
      },
    },
  });

  assert.equal(payload.chart.fields.y.field, "score");
  assert.equal(payload.chart.fields.color.field, "segment");
  assert.deepEqual(payload.data.map((point) => [point.x, point.y, point.series]), [
    ["Mon", 18, "Self-serve"],
    ["Mon", 26, "Enterprise"],
    ["Tue", 21, "Self-serve"],
    ["Tue", 31, "Enterprise"],
  ]);
});

test("JavaScript MCP server reports heatmap field roles when value encoding is not numeric", () => {
  assert.throws(() => server.callTool("render_chart", {
    title: "Heatmap",
    source: {
      query: {
        engine: "trino",
        sql: "SELECT day_name, segment, score_label FROM warehouse.heatmap_source",
        id: "heatmap-query",
      },
    },
    table: {
      columns: [
        { key: "day_name", label: "Day", type: "text" },
        { key: "segment", label: "Segment", type: "text" },
        { key: "score_label", label: "Score label", type: "text" },
      ],
      rows: [
        { day_name: "Mon", segment: "Self-serve", score_label: "Low" },
        { day_name: "Mon", segment: "Enterprise", score_label: "High" },
      ],
    },
    chart: {
      type: "heatmap",
      fields: {
        x: { field: "day_name", type: "ordinal" },
        y: { field: "score_label", type: "text" },
        color: { field: "segment", type: "nominal" },
      },
    },
  }), /numeric heatmap cell value/);
});

test("JavaScript MCP server keeps scatter size on the source field", () => {
  const payload = server.callTool("render_chart", {
    title: "ARR efficiency by segment",
    source: sourceQueryForTest(),
    table: {
      columns: [
        { key: "conversion_rate", label: "Conversion", type: "percent" },
        { key: "arr_usd", label: "ARR", type: "currency", unit: "USD" },
        { key: "active_accounts", label: "Active Accounts", type: "number" },
        { key: "segment", label: "Segment", type: "text" },
      ],
      rows: [
        { conversion_rate: 0.24, arr_usd: 1445000, active_accounts: 95, segment: "Enterprise" },
        { conversion_rate: 0.20, arr_usd: 846000, active_accounts: 161, segment: "Mid-Market" },
      ],
    },
    chart: {
      type: "scatter",
      fields: {
        x: { field: "conversion_rate", type: "quantitative" },
        y: { field: "arr_usd", type: "quantitative" },
        size: { field: "active_accounts", type: "quantitative" },
        color: { field: "segment", type: "nominal" },
      },
    },
  });

  assert.equal(payload.chart_spec.encodings.size.field, "active_accounts");
  assert.equal(payload.chart_spec.encodings.size.label, "Active Accounts");
  assert.equal(payload.chart_spec.encodings.size.format, "number");
  assert.equal(payload.chart_spec.encodings.x.field, "conversion_rate");
  assert.equal(payload.chart_spec.encodings.y.field, "arr_usd");
  assert.equal(payload.chart_spec.encodings.color.field, "segment");
  assert.equal("chart_rows" in payload, false);
  assert.deepEqual(payload.table.rows.map((row) => row.active_accounts), [95, 161]);
  assert.equal(payload.table.rows.some((row) => "__pointSize" in row), false);
});

test("JavaScript MCP server accepts non-scatter label fields as optional display metadata", () => {
  const payload = server.callTool("render_chart", {
    title: "Leaderboard",
    source: sourceQueryForTest(),
    table: {
      columns: [
        { key: "rank_order", label: "Rank", type: "number" },
        { key: "team", label: "Team", type: "text" },
        { key: "score", label: "Score", type: "number" },
      ],
      rows: [
        { rank_order: 1, team: "Team Atlas", score: 980 },
        { rank_order: 2, team: "Team Beacon", score: 870 },
      ],
    },
    chart: {
      type: "leaderboard",
      fields: {
        x: { field: "team", type: "nominal" },
        y: { field: "score", type: "quantitative" },
        label: { field: "rank_order", type: "quantitative" },
      },
    },
  });

  assert.equal(payload.ok, true);
  assert.equal(payload.chart.fields.label.field, "rank_order");
});

test("JavaScript MCP server exposes chart v1 settings in the chart schema", () => {
  const chartTool = server.toolDefinitions().find((tool) => tool.name === "render_chart");
  const properties = chartTool.inputSchema.properties;
  const chart = chartTool.inputSchema.properties.chart.properties;
  const options = chart.options.properties;
  const display = chartTool.inputSchema.properties.display.properties;
  const tableColumn = properties.table.properties.columns.items.properties;

  assert.match(properties.subtitle.description, /insight or takeaway/);
  assert.match(properties.subtitle.description, /source\.query/);
  assert.deepEqual(options.orientation.enum, ["vertical", "horizontal", null]);
  assert.deepEqual(options.grouping.enum, ["single", "grouped", "stacked", "stacked100", null]);
  assert.ok(options.points);
  assert.equal("zero_line" in options, false);
  assert.equal("limit" in options, false);
  assert.equal("show_values" in options, false);
  assert.equal("category_label_policy" in options, false);
  assert.equal("sort" in options, false);
  assert.equal("show_latest_value" in options, false);
  assert.equal("bins" in options, false);
  assert.equal("max_segments" in options, false);
  assert.equal("other_threshold" in options, false);
  assert.equal("show_percent" in options, false);
  assert.equal("legend" in display, false);
  assert.equal("view_mode" in display, false);
  assert.equal("labels" in display, false);
  assert.equal("number_format" in display, false);
  assert.deepEqual(tableColumn.format.enum, ["compact", "number", "percent", "currency", null]);
  assert.equal("version" in chart, false);
  assert.equal("comparisonContext" in chart, false);
  assert.equal("notes" in properties, false);
  assert.equal("datasets" in properties, false);
  assert.equal("selected_dataset" in properties, false);
  assert.equal("query_binding" in properties, false);
  assert.equal("facet" in chart.fields.properties, false);
  assert.equal("tooltip" in chart.fields.properties, false);
  assert.equal("sort" in chart, false);
  assert.equal("notes" in display, false);
  assert.equal("tooltip" in display, false);
  assert.equal("empty_state" in display, false);
  assert.equal("reference_lines" in display, false);
  assert.match(server.SERVER_INSTRUCTIONS, /chart\.type "bar"/);
  assert.match(server.SERVER_INSTRUCTIONS, /Chart subtitles should add a reader-facing insight/);
});

test("JavaScript MCP server rejects removed inline snake_case chart names", () => {
  const args = queryTablePayload();
  args.chart.type = "grouped_column";
  assert.throws(
    () => server.callTool("render_chart", args),
    /chart\.type must be one of/,
  );
});

test("JavaScript MCP server strips inline chart notes while table notes remain supported", () => {
  const chartArgs = queryTablePayload();
  chartArgs.notes = ["top-level chart note"];
  chartArgs.chart.version = "legacy";
  chartArgs.chart.comparisonContext = { baseline: "legacy" };
  chartArgs.chart.sort = "legacy";
  chartArgs.chart.options = {
    show_values: true,
    category_label_policy: "wrap",
    show_latest_value: true,
    bins: 12,
    max_segments: 8,
    other_threshold: 0.1,
    show_percent: true,
  };
  chartArgs.chart.fields.facet = { field: "legacy" };
  chartArgs.chart.fields.tooltip = [{ field: "legacy" }];
  chartArgs.display.notes = ["presentation chart note"];
  chartArgs.display.layout = "split";
  chartArgs.display.source_panel = "sidebar";
  chartArgs.display.sql_panel_position = "bottom_right";
  chartArgs.display.table_panel_position = "bottom_left";
  chartArgs.display.legend = { title: "Legacy" };
  chartArgs.display.view_mode = "table";
  chartArgs.display.number_format = "currency";
  chartArgs.display.labels = { values: "all" };
  chartArgs.query_binding = { label: "legacy binding" };
  chartArgs.datasets = [{ id: "legacy dataset input" }];
  chartArgs.selected_dataset = "legacy dataset input";

  const chartPayload = server.callTool("render_chart", chartArgs);
  const tablePayload = server.callTool("render_table", {
    title: "Preview",
    source: chartArgs.source,
    notes: ["table note"],
    columns: [{ key: "segment", label: "Segment", type: "text" }],
    rows: [{ segment: "Enterprise" }],
  });
  const tableSchema =
    server
      .toolDefinitions()
      .find((tool) => tool.name === "render_table")
      .inputSchema.properties;

  assert.equal("notes" in chartPayload, false);
  assert.equal("notes" in (chartPayload.display || {}), false);
  assert.equal("version" in chartPayload.chart, false);
  assert.equal("comparisonContext" in chartPayload.chart, false);
  assert.equal("sort" in chartPayload.chart, false);
  assert.deepEqual(chartPayload.chart.options, undefined);
  assert.equal("facet" in chartPayload.chart.fields, false);
  assert.equal("tooltip" in chartPayload.chart.fields, false);
  assert.equal("layout" in (chartPayload.display || {}), false);
  assert.equal("source_panel" in (chartPayload.display || {}), false);
  assert.equal("sql_panel_position" in (chartPayload.display || {}), false);
  assert.equal("table_panel_position" in (chartPayload.display || {}), false);
  assert.equal("legend" in (chartPayload.display || {}), false);
  assert.equal("view_mode" in (chartPayload.display || {}), false);
  assert.equal("number_format" in (chartPayload.display || {}), false);
  assert.equal("legend" in chartPayload.chart_spec, false);
  assert.equal("labels" in chartPayload.chart_spec, false);
  assert.equal("viewMode" in chartPayload.chart_spec.surface, false);
  assert.equal("view_mode" in chartPayload, false);
  assert.equal("labels" in (chartPayload.display || {}), false);
  assert.equal("datasets" in chartPayload, false);
  assert.equal("selected_dataset" in chartPayload, false);
  assert.equal("query_binding" in chartPayload, false);
  assert.ok("notes" in tableSchema);
  assert.deepEqual(tablePayload.notes, ["table note"]);
});

test("JavaScript MCP server preserves chart-compatible source SQL for table widgets", () => {
  const chartArgs = queryTablePayload();
  const payload = server.callTool("render_table", {
    title: "ARR rows",
    source: chartArgs.source,
    result_table: chartArgs.table,
  });
  const tableSchema =
    server
      .toolDefinitions()
      .find((tool) => tool.name === "render_table")
      .inputSchema.properties;

  assert.equal(payload.widget_type, "table");
  assert.equal(payload.source.query.sql, "SELECT reporting_date, arr_b FROM gtm.example");
  assert.equal("query" in payload.source.query, false);
  assert.equal(payload.source.query.id, "query-123");
  assert.equal(payload.source_query, undefined);
  assert.ok(tableSchema.source);
  assert.ok(tableSchema.source.properties.query.properties.sql);
  assert.ok(tableSchema.source.properties.query.properties.filters);
  assert.ok(tableSchema.source.properties.query.properties.description);
});

test("JavaScript MCP server removes source.query.query from table widget payloads", () => {
  const chartArgs = queryTablePayload();
  chartArgs.source.query.query = "Loads ARR by reporting date for widget tests.";

  const payload = server.callTool("render_table", {
    title: "ARR rows",
    source: chartArgs.source,
    result_table: chartArgs.table,
  });

  assert.equal(payload.widget_type, "table");
  assert.equal(payload.source.query.sql, "SELECT reporting_date, arr_b FROM gtm.example");
  assert.equal("query" in payload.source.query, false);
  assert.equal(payload.result_table.rows.length, 2);
});

test("JavaScript MCP server rejects payloads that only use removed source.query.query", () => {
  const chartArgs = queryTablePayload();
  delete chartArgs.source.query.sql;
  chartArgs.source.query.query = "SELECT reporting_date, arr_b FROM gtm.example";

  assert.throws(
    () => server.callTool("render_table", {
      title: "ARR rows",
      source: chartArgs.source,
      result_table: chartArgs.table,
    }),
    /actual SQL query text/,
  );
});

test("JavaScript MCP server rejects redundant bar chart type aliases", () => {
  assert.throws(() => server.callTool("render_chart", {
    title: "Revenue mix",
    source: sourceQueryForTest(),
    table: {
      columns: [
        { key: "segment", type: "text" },
        { key: "channel", type: "text" },
        { key: "revenue", type: "number" },
      ],
      rows: [
        { segment: "Enterprise", channel: "Direct", revenue: 40 },
        { segment: "Enterprise", channel: "Partner", revenue: 60 },
      ],
    },
    chart: {
      type: "horizontalStackedBar100",
      fields: {
        x: { field: "segment", type: "nominal" },
        y: { field: "revenue", type: "quantitative" },
        color: { field: "channel", type: "nominal" },
      },
    },
  }), /chart\.type must be one of/);
});

test("JavaScript MCP server rejects invalid grouped and percent stacked bar configs", () => {
  const baseArgs = {
    title: "Revenue mix",
    source: sourceQueryForTest(),
    table: {
      columns: [
        { key: "segment", type: "text" },
        { key: "channel", type: "text" },
        { key: "revenue", type: "number" },
      ],
      rows: [{ segment: "Enterprise", channel: "Direct", revenue: 0 }],
    },
    chart: {
      type: "bar",
      options: { grouping: "stacked" },
      fields: {
        x: { field: "segment", type: "nominal" },
        y: { field: "revenue", type: "quantitative" },
      },
    },
  };

  assert.throws(
    () => server.callTool("render_chart", baseArgs),
    /requires chart\.fields\.color\.field/,
  );

  const invalidPercent = structuredClone(baseArgs);
  invalidPercent.chart.options.grouping = "stacked100";
  invalidPercent.chart.fields.color = { field: "channel", type: "nominal" };
  assert.throws(
    () => server.callTool("render_chart", invalidPercent),
    /positive denominator/,
  );
});

test("JavaScript MCP server rejects auto chart setting modes", () => {
  const args = queryTablePayload();

  args.chart.options = { points: "auto" };
  assert.throws(
    () => server.callTool("render_chart", args),
    /chart\.options\.points must be one of always, never/,
  );
});

test("JavaScript MCP server warns on dense compact bars and pies", () => {
  const rows = Array.from({ length: 25 }, (_, index) => ({ category: `C${index}`, value: index + 1 }));
  const columns = [{ key: "category", type: "text" }, { key: "value", type: "number" }];
  const barPayload = server.callTool("render_chart", {
    title: "Dense categories",
    source: sourceQueryForTest(),
    table: { columns, rows },
    chart: {
      type: "bar",
      fields: { x: { field: "category" }, y: { field: "value" } },
    },
  });
  const piePayload = server.callTool("render_chart", {
    title: "Dense slices",
    source: sourceQueryForTest(),
    table: { columns, rows: rows.slice(0, 9) },
    chart: {
      type: "pie",
      fields: { x: { field: "category" }, y: { field: "value" } },
    },
  });

  assert.match(barPayload.quality_warnings.join(" "), /Compact bar chart has 25 categories/);
  assert.match(piePayload.quality_warnings.join(" "), /Compact pie chart has 9 slices/);
});

test("JavaScript MCP server returns typed resource errors", async () => {
  const response = await server.handleRpc({
    jsonrpc: "2.0",
    id: 1,
    method: "resources/read",
    params: { uri: "ui://widget/missing.html" },
  });

  assert.equal(response.error.code, -32602);
  assert.match(response.error.message, /unknown Data Analytics widget resource/);
});

test("JavaScript MCP server rejects legacy widget resource aliases", async () => {
  for (const uri of [
    server.CHART_WIDGET_URI.replace(".html", "-old.html"),
    server.TABLE_WIDGET_URI.replace(".html", "-old.html"),
    server.ARTIFACT_WIDGET_URI.replace(".html", "-old.html"),
  ]) {
    const response = await server.handleRpc({
      jsonrpc: "2.0",
      id: 1,
      method: "resources/read",
      params: { uri },
    });

    assert.equal(response.error.code, -32602);
    assert.match(response.error.message, /unknown Data Analytics widget resource/);
  }
});

test("artifact share menu labels Sites publishing clearly", () => {
  const app = readFileSync(new URL("../src/analytics-app/App.tsx", import.meta.url), "utf8");
  assert.match(app, /site: "Publish to Sites"/);
  assert.doesNotMatch(app, /Publish hosted link/);
});

test("local artifact fallback uses canonical chart encodings", () => {
  const widget = readFileSync(new URL("../src/datascience-artifact-widget.jsx", import.meta.url), "utf8");
  const fallback = widget.split("const fallbackPayload =", 2)[1].split("const hostedEmptyPayload", 1)[0];
  assert.match(fallback, /sourceId: "snapshot"/);
  assert.match(fallback, /encodings: \{/);
  assert.doesNotMatch(fallback, /xField:/);
  assert.doesNotMatch(fallback, /^\s+series:/m);
});

test("artifact charts wire clickable legend state into the renderer", () => {
  const app = readFileSync(new URL("../src/analytics-app/App.tsx", import.meta.url), "utf8");
  assert.match(app, /const \[visibleSeries, setVisibleSeries\] = useState\(\)/);
  assert.match(app, /onVisibleSeriesChange=\{setVisibleSeries\}/);
  assert.match(app, /visibleSeries=\{visibleSeries\}/);
});

test("JavaScript MCP server rejects unsafe widget fields", () => {
  const args = queryTablePayload();
  args.table.columns.push({ key: "customer_email", label: "Email" });
  args.table.rows[0].customer_email = "person@example.com";

  assert.throws(
    () => server.callTool("render_chart", args),
    /looks unsafe/,
  );
});

test("JavaScript MCP server allows reviewed customer dimensions in widgets", () => {
  const args = queryTablePayload();
  args.table.contains_sensitive_data = true;
  args.table.columns.push({ key: "customer_name", label: "Customer" });
  args.table.rows[0].customer_name = "Acme Corp";

  const payload = server.callTool("render_chart", args);

  assert.equal(payload.widget_type, "chart");
  assert.equal(payload.table.rows[0].customer_name, "Acme Corp");
});
