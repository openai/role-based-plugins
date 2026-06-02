# Data Analytics MCP Apps

## Purpose

This plugin contains a complex fullscreen analytics artifact workspace plus compact inline chart and table widgets. Preserve that architecture when iterating: artifacts are snapshot-first workspaces, while chart and table widgets are focused views of reviewed query results.

## Visual Style

Follow the local Codex style contract in `src/codex-style-contract.md`.
`src/styles/codex-theme.css` is the copied Codex fallback baseline and must load before `src/analytics-app/tokens.css`. Shared surfaces, controls, typography, spacing, borders, radii, shadows, focus, and motion should resolve through the Codex tokens. Analytics CSS may extend the baseline for charts, KPI states, tables, report widths, and dashboard layouts.

## Fullscreen Behavior

Inline surfaces that support fullscreen expose a compact top-right fullscreen control and hide it after fullscreen is active.

## Workflow

Before future changes, start with the installed `codex-mcp-app-devkit` skill so it can route to the app-development workflow and the Codex visual references. Use `npm run preview:widgets` for local previews, `npm run build` for all widget bundles, `npm run typecheck` for TypeScript, and `npm test` for MCP server and widget contract coverage.

The plugin package is materialized directly from this directory. After changing widget source, run `npm run build` so `assets/` and normalized bundle parts stay aligned, then reinstall the updated development plugin from the Plugin Development marketplace when testing inside Codex.
