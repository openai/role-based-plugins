---
name: logo-explorer
description: Use when a brand brief needs logo concepts, wordmarks, lockups, identity-system routes, or a logo review board before vector production or final brand polish.
---

# Logo Explorer

Use this skill when the user wants an interactive logo exploration surface: a review board of candidate logo directions, each labeled with a strategic design route, where selections and rejections steer the next round.

Read `../../references/experience-contract.md` before writing the user-facing handoff or reporting artifact links.

Read `../../references/artifact-contracts.md` before creating, repairing, or reporting artifacts.

Read `../../references/codex-exec-image-generation.md` before running image generation.

Read `../../references/image-building-strategy.md` alongside the Codex exec contract for first-pass imagery rules.

## Pipeline Role

This skill owns logo and identity-route exploration in the Explore > Build > Polish workflow.

Use it after there is a brand anchor to preserve:

- a brand name or product name;
- an existing logo, sketch, mark, or wordmark;
- a short identity brief with audience, category, positioning, and usage contexts;
- a selected mood-board territory that needs logo-system exploration.

It helps choose a logo direction; it does not produce final trademark-cleared, production-ready vector identity files. Treat production vector identity work as an external or post-P0 handoff after a route is selected.

Use `moodboard-explorer` first when the user is still deciding broad brand feeling, category territory, or audience mood. Use `style-explorer` when the subject is an existing visual asset and only finish/treatment should vary.

## Anchor And Scope

Start only when there is enough identity anchor to refine. If the user provides only "make a logo," ask one compact clarification for the brand name and category.

Treat logo direction as the variable layer. Preserve approved facts:

- exact brand or product name spelling;
- category and audience;
- existing mark geometry, if supplied;
- required colors, accessibility constraints, and usage contexts;
- claims, taglines, and legal restrictions.

Vary only logo-system dimensions such as mark metaphor, wordmark construction, lockup balance, geometry, contrast, palette direction, icon/monogram approach, and small-size performance.

Generated text and logo typography are directional unless the workflow uses a stricter vector or deterministic text path.

## Reference-Image Logo Briefs

When the user supplies product photos, existing logos, sketches, campaign marks, or visual references, treat those references as the core generation context.

For reference-image logo briefs:

- Search the local Creative Production prompt libraries and prior run patterns for logo-specific prompt families before writing new prompts. Reuse or adapt approved logo-board, lockup-board, derivation-sheet, risk-review, and vector-parameter prompt patterns when they fit the brief.
- Use image chaining or image-edit generation when supplied reference images are central to the brief.
- Preserve supplied images as references through the generation pipeline. Do not replace reference-image exploration with hand-authored SVGs, CSS drawings, icon sketches, or text-only mockups unless the user explicitly asks for deterministic vector drafting.
- If the user provides an official or partner logo as a reference, use it according to the brief and legal constraints. If the brief does not grant permission to create a co-branded or official lockup, treat the logo as motif/brand-context reference and generate original campaign-safe concepts.
   - Use generated raster logo boards for the first decision surface. Move to vector construction only after a route is selected and the next owner is an external or post-P0 production identity step.

## Core Pattern

Build the first screen as the usable logo board, not a landing page.

Default interaction model:

1. Show one selected anchor plus many exploratory logo routes.
2. Generate options from distinct identity strategies, not weak style synonyms.
3. Render routes on a white inspection background so transparent logo areas read as white.
4. Let the user select or attach a route directly from the review surface.
5. Let the user reject routes, and use those rejects to suppress future directions.
5. Fill images progressively as each generation completes; do not block the whole board on one slow or failed image.
6. Keep failures local to the tile with a retry path.
7. End with a selected logo route, rejected direction notes, prompt metadata, and a handoff to final logo/vector production.

## Workflow

1. Confirm the identity anchor and scope.
   - Capture brand name, category, audience, usage contexts, must-preserve constraints, and must-avoid territory.
   - If an existing logo or sketch is supplied, describe what must survive: mark silhouette, proportions, colors, wordmark treatment, spacing, and lockup logic.

2. Create the logo spec.
   - Write a JSON spec with `meta`, `constraints`, `routes`, and optional `handoff`.
   - Include 6-18 routes for most runs.
   - Each route needs `id`, `label`, `family`, and `prompt`.
   - Each route also needs decision advice: `best_for`, `decision_advice`, `watch_out`, and `next_step`.
   - Useful optional fields: `rationale`, `usage_contexts`, `next_prompt_hints`, and `final_owner`.
   - Prompts should vary identity direction only and should not invent claims, taglines, endorsements, legal marks, partner marks, or unapproved copy.
   - For image-chained logo boards, keep the prompt-family metadata and source-image paths in the manifest so later rounds can reproduce the chain.

3. Generate the app.
   - Use the bundled template and script:

```bash
python3 <skill>/scripts/create_logo_explorer.py --spec <spec.json> --output <output-dir> --force
node <output-dir>/server.mjs
```

4. Generate images through Codex exec workers.
   - Before high-volume generation, state the planned route count and review surface.
   - The local app generates routes independently through `/api/image`, caches PNGs by prompt hash, and keeps failed tiles retryable. The server injects a per-run `X-BV-Run-Token` into same-origin pages and requires `confirmGenerate: true` on image-generation requests.
   - When reference images are supplied, keep source-image paths and prompt-family metadata in the manifest and worker context. The output should be real PNG/JPEG/WebP logo-board imagery saved under the run folder.

5. Review and export the handoff.
   - Select the strongest route and reject poor fits.
   - Use the app export buttons, or read the persisted files under `<output-dir>/data/`.
   - Expected handoff files: `selected-logo-route.json` and `handoff.md`.

6. Present selected options in chat when an inline widget is available.
   - Prefer the shared static review renderer for the primary durable review surface. Use `scripts/review_renderer.py` with the `image-wall` preset for generated logo-board images unless the user explicitly needs a custom interactive selector.
   - Use `render_moodboard_board_widget` for inline logo review after verifying that every item image URL/path renders in the current environment. If image rendering cannot be verified, report that inline image review could not be verified; do not link to the local review page unless the user explicitly asks for debug access.
   - The shared mood-board widget is the only inline MCP review surface for generated logo-board imagery.
   - Use the local HTML board only for agent-side verification, deeper debug inspection, or explicit user requests for local/offline review.
   - For widget items, pass image paths known to work for that widget. Do not assume local absolute filesystem paths render inside an Apps SDK widget; verify first with the widget contract or a browser check.
   - Keep the widget focused: highlight the strongest 3-5 routes first, then include secondary options when useful.

## Recommended UI

- Use a white inspection surface by default. Avoid checkerboards for transparent PNG review unless the user explicitly asks for transparency inspection.
- Prefer square logo tiles with enough padding to judge silhouette, spacing, and small-size readability.
- Keep labels below the image; avoid overlays that hide logo shape.
- Include route family and usage contexts where available.
- Include compact decision advice on every route: best use, why it works, watch-out, and next step.
- Make each route selectable in the primary review surface. In an Apps SDK widget, use `Attach to chat`; in local HTML, provide selection plus copy/export fallback.
- Clicking the selected anchor should open a fullscreen preview.
- Avoid persistent bulky prompt editors unless the user asks for explicit prompt tuning.
- Static review pages should be generated through the shared Creative Production Review Renderer, not hand-written per run. The canonical file is `review-board.html`. The review should be inspection-first: white background, simple responsive image grid, no marketing-page header chrome, and stable relative image links.

## Generation Architecture

Prefer a local backend for image generation:

- The browser sends prompts to the local server.
- The server keeps the API key off the page.
- Cache generated images by prompt hash.
- Generate tiles independently so partial success is visible.
- Avoid regenerating the selected anchor when its image already exists.
- Save source references, prompts, model, quality, generated images, review manifest, rendered HTML, and handoff notes under one durable `outputs/logos/<brief-slug>/` folder.

## Logo Direction Logic

Use distinct identity families:

- wordmark: typographic, editorial, constructed, humanist
- monogram: initials, ligature, badge, modular letters
- symbol: abstract mark, category metaphor, product metaphor, motion cue
- geometric: grid, modular, low-detail, high-recognition
- heritage: seal, crest, craft, institutional
- tech: interface, node, cursor, agent, system signal
- playful: mascot-adjacent, soft geometry, sticker, rounded
- premium: restrained, quiet luxury, high-contrast, sparse
- utility: app icon, favicon-first, stamp, small-size-first
- adaptive: responsive lockup, family system, campaign mark

Selection should raise the weight of that family while preserving some diversity. Rejection should suppress the exact idea and reduce related family weight.

## Handoff Shape

Use the same lightweight handoff wording as the other explorers: selected direction, preserve, avoid, focused next owner, and artifact path.

For logo exploration runs, preserve:

- selected logo direction;
- visual family and route rationale;
- decision advice: best use, why it works, watch-out, and next production step;
- prompt and identity cues;
- rejected routes and suppressed families;
- brand name, category, audience, and usage contexts;
- constraints to preserve and avoid;
- caveats about generated typography, legal clearance, trademark review, and production vectorization;
- final owner: `generative-polish`, an active Build/Polish owner, or an external/post-P0 production identity step.

## Exit Criteria

A successful logo exploration ends with:

- a reviewable logo route grid;
- real generated logo-board imagery when reference images are supplied and generation is available;
- a shared-renderer review page with verified image rendering;
- an inline logo review widget only when the environment supports it and the images are verified to render;
- white-background logo tiles or boards with enough spacing to assess shape, lockup, and small-size behavior;
- per-route decision advice;
- selected and rejected logo directions;
- reusable prompt and identity metadata;
- a named next step for production vector/logo-system work;
- clear caveats about generated text, trademark clearance, brand fidelity, accessibility, and unsupported assumptions.

Before handoff, verify the review surface:

- load the local review page or fetch it over localhost/file path for agent-side verification only;
- confirm the expected image count appears;
- confirm each image request succeeds and has non-zero natural dimensions;
- confirm the durable manifest points to the same images the user sees;
- do not render or recommend an Apps SDK widget if its images fail to display.

## Spec Shape

```json
{
  "meta": {
    "title": "Logo exploration for Meridian Labs",
    "stage": "Logo exploration",
    "brand_name": "Meridian Labs",
    "anchor": "AI operations platform for healthcare teams",
    "summary": "Compare logo directions for a calm, precise clinical operations brand.",
    "base_asset": "path/to/existing-logo.png"
  },
  "constraints": {
    "preserve": ["brand name spelling: Meridian Labs", "healthcare operations category", "calm enterprise tone"],
    "avoid": ["medical cross icons", "fake certification seals", "partner logos", "readable taglines"]
  },
  "routes": [
    {
      "id": "monogram-signal",
      "label": "Monogram Signal",
      "family": "monogram",
      "usage_contexts": ["app icon", "sales deck", "website header"],
      "prompt": "Create a clean logo exploration tile for Meridian Labs. Show a simple ML monogram and adjacent wordmark direction on a white background. Preserve the exact brand name intent, healthcare operations category, and calm enterprise tone. No taglines, no fake seals, no partner marks.",
      "rationale": "Tests whether initials can create a compact product-app identity.",
      "best_for": "App icon, sales deck, and website header.",
      "decision_advice": "Use if the brand needs a compact product-led identity that can work without a full wordmark.",
      "watch_out": "Initials may feel generic unless the letter construction has a distinct gesture.",
      "next_step": "Vectorize the monogram and test it at favicon size before adding typography.",
      "final_owner": "external-production-identity"
    }
  ],
  "handoff": {
    "default_owner": "external-production-identity"
  }
}
```

## Files

- `assets/logo-explorer-app/`: reusable static app template and local image-generation server.
- `scripts/create_logo_explorer.py`: copies the template, validates the spec, copies an optional base asset, and writes app data.
