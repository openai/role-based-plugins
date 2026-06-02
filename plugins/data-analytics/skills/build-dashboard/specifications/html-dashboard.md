# HTML Dashboard Specification

Use this when the dashboard should be delivered as a portable static HTML file rather than a connected BI dashboard, MCP artifact dashboard, or Streamlit app.

## When To Use

- Use HTML when the user requests a static file or when BI and MCP surfaces are not suitable for the requested handoff.
- Do not use HTML to bypass missing source access. HTML dashboards must still be source-backed, validated, and reproducible from reviewed data.
- Prefer MCP artifacts for in-Codex handoff and BI tools for shared operating dashboards with managed refresh.

## Build Shape

- Build a single portable HTML file when practical, with compact embedded data and no external runtime dependency unless the user asked for one.
- Lead with the dashboard's primary metric context, then trends, diagnostic breakdowns, and detail tables.
- Keep filters and interactions limited to controls that materially help the reader explore the dashboard.
- Preserve source provenance in a visible sources or methodology section, including query links, source tables, freshness, definitions, and important filters.
- Use compact reader-facing number formats in cards, chart labels, axes, tooltips, headings, and narrative text unless exact values are the point.
- Define business-specific KPI labels in nearby text or a source/methodology section so the dashboard can be understood without reading SQL.

## Validation

- Validate that the HTML opens locally, renders charts and tables, and has no obvious JavaScript errors.
- Inspect the rendered page at desktop and narrow widths for clipping, overlap, unreadable labels, and broken controls.
- Confirm that cards, charts, and tables reconcile against the reviewed source extracts before handoff.
