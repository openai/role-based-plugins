---
name: charts-polish
description: Polish existing charts, benchmark visuals, dashboards, or data-heavy slide graphics into high-craft business visuals with ImageGen while preserving every source data point. Use when the user asks for chart variants, chart styling, executive one-pagers, proof cards, creative learning memos, landing-page chart heroes, storyboard/proof treatments, social-ready chart scenes, 3D/minimal/drawing/character chart styles, or any batch of polished chart image experiments that must not change chart data.
---

# Charts Polish

Transform an existing chart image into polished business-visual variants using ImageGen. Treat this as a visual treatment skill, not a data redesign skill: the source chart remains the source of truth.

Read `../../references/artifact-contracts.md` before creating, repairing, or reporting artifacts.

Prefer a validated SVG/chart export as the source when available. Do not use this skill to repair unvalidated chart data, activate chart templates, or replace the canonical SVG/vector chart.

When the user provides approved photography, texture assets, or background references for a polished chart variant, treat them as external reference inputs rather than plugin-bundled media.

## Workflow

1. Load the chart target.
   - If the chart is a local file, inspect it with `view_image` before generating.
   - If style references or textures are local files, inspect those too.
   - Label roles explicitly in the prompt: `edit target`, `style reference`, `background reference`, or `favorite example`.

2. Choose one or more style routes.
   - Before using bundled favorite images, run `python ../../scripts/hydrate_assets.py --check`.
   - If the check reports missing assets, run `python ../../scripts/hydrate_assets.py` or hydrate from the Drive upload payload with `--source-dir`.
   - For the favorite tested routes, read `references/favorite-routes.md`.
   - For reusable prompt language, read `references/prompt-patterns.md`.
   - For batches, create one ImageGen call per route. Do not ask ImageGen for many distinct styles in one prompt.

3. Lock the chart data.
   - Preserve title, subtitle, legend, series colors, axis labels, axis ticks, benchmark/category labels, values, footnote, bar positions, bar heights, annotations, and relative geometry.
   - Do not add bars, duplicate bars, delete bars, reorder categories, relabel series, invent sources, add claims, add CTAs, or hide any chart information.
   - If using characters or scene elements, keep them in margins, whitespace, or outside the plot area. They must not touch or cover real bars, values, labels, or annotations.

4. Generate the visual.
   - Use the built-in `image_gen` tool by default.
   - Keep the chart central and legible unless the user explicitly asks for a looser concept.
   - Save generated outputs into the current project, usually under `outputs/imagegen/charts-polish/<run-id>/` or a user-specified folder.

5. Review before handing off.
   - Inspect each output for visible data drift, hidden labels, added chart marks, wrong values, or unreadable text.
   - If a route adds visual metadata, describe it as design framing rather than source-of-truth content.
   - For multi-image sets, create or update a contact sheet when useful.

## Default Prompt Skeleton

```text
Use case: style-transfer / productivity-visual edit
Asset type: polished business chart variant
Input images: Image 1 is the chart edit target; Image 2 is the style/background reference if provided.
Style route: <route name>

Primary request:
Create a <route name> version of the chart. Apply the route as visual treatment only. Keep the chart as the central readable object.

Data locks:
Preserve all chart data exactly: title, subtitle, legend labels, category labels, category subtitles, axis labels, axis ticks, footnote, all numeric values, bar positions, bar heights, leader annotations, and relative geometry.
Do not add new data, remove labels, rewrite claims, invent sources, add CTAs, add extra bars, duplicate bars, or hide any chart information.

Style constraints:
<route-specific style constraints>
```

## High-Risk Routes

Use stricter prompts for these:

- **Characters / Mini Me / social scenes**: characters stay outside the plot area and cannot sit on, climb on, touch, or cover actual bars.
- **3D charts**: depth cannot change perceived bar heights or add decorative columns.
- **Storyboards / channel walls / carousels**: keep one main chart; do not create extra mini charts unless the user explicitly asks.
- **Ad / UGC / landing-page routes**: do not add CTA copy, fake proof, testimonials, logos, dates, or unsupported claims.

## Relationship To Generative Polish

Use `charts-polish` for chart-specific creative exploration and polished chart image variants.

Use `../generative-polish/SKILL.md` for publish-bound marketing assets such as chart cards, social carousels, launch visuals, or creative packs. In that workflow, deterministic SVG/HTML/Python/template layers own exact chart data, copy, logos, dimensions, safe zones, filenames, and review metadata. ImageGen should supply only background, lighting, texture, depth, or scene treatment, then the final asset should be recomposed deterministically.

If an ImageGen output rewrites text, changes numbers, distorts chart geometry, invents UI, or adds claims, treat it as a non-final visual reference.

## Bundled Examples

Favorite examples hydrate into `assets/favorites/`. Use them as visual references when the user asks for the same route or for "the favorite chart styles." Do not assume their data is reusable; only their visual treatment is reusable.
