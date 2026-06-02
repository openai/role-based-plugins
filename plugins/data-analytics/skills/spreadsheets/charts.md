# Chart Requirements and Guidance

Use this when creating or editing charts, dashboards, or chart-ready summaries in spreadsheet workbooks. Keep the chart useful first: accurate data binding, readable units, and legible labels matter more than decorative styling.

## Chart Requirements

- Use native Excel charts for chart deliverables when plottable data supports the requested comparison or trend.
- Chart from a bounded source/helper range whose first row is headers, first column is the displayed category or time label, and remaining columns are plotted series.
- Link helper values to source cells with formulas when the source data should remain auditable.
- Keep the full source table available when helper labels are abbreviated or grouped for chart readability.
- Do not place charts over source data or important notes; reserve a bounded chart area with whitespace around it.
- Percent, currency, date, and count axes must use an appropriate number format or visible data labels.
- For narrow chart-edit requests, preserve the requested edit scope and do not silently rewrite unrelated formulas, formatting, data tables, or workbook structure.
- For chart edits, inspect the visible chart area and source range for formula errors. Preserve unrelated pre-existing errors, mention them in the final response, and fix them only when they directly break the chart or the user asked for repair/audit.
- Render every meaningful chart sheet before export. Check for blank charts, disconnected or stale ranges, unreadable axis units, clipped labels, overcrowded tick labels, unintended multi-color single-series styling, and visible formula errors near chart inputs or outputs.

## Chart Guidance

- Use charts when they improve the answer; avoid redundant charts that repeat the same point.
- For dashboards, reporting, and analysis, place charts near the KPI blocks or source tables they explain when charts help the user make the decision.
- Multiple charts are useful when they communicate distinct KPIs, comparisons, or trends.
- When the workbook needs both a detailed data table and a chart, keep the detailed table for browsing/filtering and chart a smaller helper range with only the plotted fields.
- For single-series line charts, explicitly set one consistent line color and marker style. Do not rely on automatic Excel chart styles that may vary point colors, segment colors, or marker symbols inside one series.
- If markers are used, keep marker shape, fill, and outline consistent across the series unless each point intentionally encodes a category.
- Prefer a clear chart title, but do not use the title as the only place where units are visible when the axis values need interpretation.
- Axis titles are optional when the chart title and surrounding worksheet context make the dimension and measure unambiguous. Axis number formatting is not optional when the unit changes how the chart is read.
- Add data labels when exact values matter or when the axis unit is easy to misread. If data labels make the chart crowded, use fewer labels, improve axis formatting, or enlarge the chart rather than leaving units ambiguous.
- For long category labels, create readable shortened chart labels when the full labels would clip or wrap badly.
- For summary tables adjacent to charts, widen the category column, wrap only at natural word breaks, or move long descriptors into a notes column rather than allowing cramped within-word wrapping.
- For time-based charts, if raw dates would create crowded labels or unreliable date-axis grouping, add a grouped field such as Year, Quarter, Month, or Week to the chart source.
- If a chart fails export after optional styling, simplify styling before removing the chart: use a helper-range chart, reduce custom axis/series mutations, then retry export.
