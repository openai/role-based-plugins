---
name: style-explorer
description: Use when a selected concept, mood board, reference image, or business brief needs reusable style routes across image treatment, typography, palette, and visual-system copy before production or polish.
---

# Style Explorer

Use this skill when the user wants to compare reusable visual systems before producing business assets: a compact board of candidate style routes, each expressed through an image, typography treatment, color palette, and immersive style description. The user can select strong routes or rule out weak fits before moving to the next stage.

Read `../../references/experience-contract.md` before writing the user-facing handoff or reporting artifact links.

Read `../../references/artifact-contracts.md` before creating, repairing, or reporting artifacts.

Read `../../references/codex-exec-image-generation.md` before running image generation.

Read `../../references/image-building-strategy.md` alongside the Codex exec contract for first-pass imagery rules.

## Pipeline Role

This skill owns reusable style selection in the Explore > Build > Polish workflow.

Use it after a broad territory, product route, mood board, base asset, or sufficiently clear business brief exists and the user wants to decide what visual system should carry into future assets. It helps choose a style direction; it does not own final publish-bound composition.

Use `moodboard-explorer` first for broad campaign mood, brand direction, audience feel, or creative territory exploration. Use `offer-explorer` first for offer-led prompt-family coverage and review galleries.

If the user enters from `explore` and chooses "Style routes" before selecting a mood board, offer route, or scene route, treat the business brief itself as the anchor as long as it contains a clear business type, goal, and audience. If the brief is too thin, ask one compact intake question before rendering routes.

Use final polish skills after a style route is selected:

- `variation-lab` when the user wants to keep building from rendered route outputs by changing character, scene, product, copy, format, camera, palette, or related remix slots.
- `charts-polish` for chart-specific visual variants that preserve chart data.
- `generative-polish` for publish-bound marketing finish where deterministic layers own exact text, charts, logos, dimensions, safe zones, filenames, and review metadata.
- `texture-builder` when the selected style direction needs reusable textures, backgrounds, or declared media-slot fills.
- `video-explorer` when the selected style route should become a motion ad or vertical video packet.

## Anchor And Scope

Start when there is an anchor to refine:

- a selected mood-board territory;
- a selected offer visual route;
- a base image, chart, object, page, or creative asset;
- a clear business brief with audience, objective, and enough taste/context to propose style routes.

If the anchor is missing, ask for one compact clarification or hand off to `moodboard-explorer` or `offer-explorer`. Do not use this skill to invent the campaign concept, product facts, source claims, chart data, copy, or final layout from scratch.

Treat style as the variable layer. Preserve the anchor's subject, product facts, approved copy, chart/data meaning, logo rules, source context, and channel constraints. Vary only treatment dimensions such as lighting, material, rendering style, lens/angle, palette, texture, scene finish, depth, and composition emphasis.

## Core Pattern

Build the first screen as the usable style-route chooser, not a landing page and not a context summary.

Default interaction model:

1. Show compact tiles for distinct reusable style routes.
2. Each tile must include a real/generated raster image, a route-specific typography treatment, a six-to-eight color palette shown as square swatches, and immersive copy about the moment/style.
3. Let the user click a tile to select it.
4. Let the user rule out a tile with a small centered `x` control.
5. Provide one compact footer action to continue with the selected route(s).
6. End with selected style route(s), ruled-out directions, prompt/style metadata, and a handoff to the next stage.

Do not include working-context panels, "Exploratory Board" labels, asset-type chips, quality-review controls, prompt details, or "build next" panels in this first style chooser. The conversation already carries the business context, and asset selection comes later.

## Workflow

1. Confirm the anchor and scope.
   - If an anchor is missing, ask one compact clarification or hand off to `moodboard-explorer` or `offer-explorer`.
   - If the user chose style routes from the launcher and has not yet qualified style preferences, render `render_style_intake_widget` when MCP widgets are available. Stop after rendering and wait for the follow-up.
   - If the follow-up says it contains a qualified style intake, proceed directly into route generation from those selected signals.
   - Capture what must be preserved and avoided.

2. Create the style spec.
   - Write a JSON spec with `meta`, `constraints`, `routes`, and optional `handoff`.
   - Include 4-8 routes for the first chooser. Use more only when the user asks for broad exploration.
   - Each route needs `id`, `label`, `family`, `prompt`, `palette`, `typography`, and `description`.
   - `palette` should usually contain 6-8 hex colors shown as square swatches.
   - `description` should be immersive: moment, lighting, materials, mood, taste level, and what the style feels like. Do not describe asset types here.
   - Prompts should vary treatment only and should not invent new claims, copy, logos, product facts, chart data, or source evidence.

3. Generate the app.
   - Use the bundled template and script:

```bash
python3 <skill>/scripts/create_style_explorer.py --spec <spec.json> --output <output-dir> --force
node <output-dir>/server.mjs
```

4. Generate images through Codex exec workers.
   - Before high-volume generation, state the planned route count and review surface.
   - The local app generates routes independently through `/api/image`, caches PNGs by prompt hash, and keeps failed tiles retryable. The server injects a per-run `X-BV-Run-Token` into same-origin pages and requires `confirmGenerate: true` on image-generation requests.

5. Review and export the handoff.
   - Select the strongest route and reject poor fits.
   - Use the app export buttons, or read the persisted files under `<output-dir>/data/`.
   - Expected handoff files: `selected-style-route.json` and `handoff.md`.
   - If a static image review wall is needed, render it from a manifest with `scripts/review_renderer.py` using the `image-wall` preset. Do not hand-write custom review HTML; the shared renderer writes `review-board.html`.
   - When an inline MCP review surface is available for generated style route images, render the route set with `render_moodboard_board_widget`. Keep `render_style_intake_widget` for pre-generation qualification only.

## Recommended UI

- Use a clean white background.
- Prefer compact grids: 3 columns for six routes on desktop, then 2 and 1 column responsively.
- Keep tiles smaller than asset boards; this is a chooser, not a gallery.
- Use real or generated raster imagery. Avoid SVG/vector placeholders as the primary route image.
- Make the route title and subtitle share the route typography.
- Show palette as traditional square swatches, not a pill strip.
- Use one small centered `x` circle to rule out a route.
- Use one simple footer action such as "Continue with selection."
- Keep route descriptions readable enough to immerse the user in the moment.

Do not show:

- working context;
- campaign brief repetition;
- asset categories such as business card, wine dinner ad, private dining card, video;
- "Pin", "More like this", and "Reject" button rows;
- review-library language;
- quality scoring or readiness checks.

## Generation Architecture

Prefer a local backend for image generation:

- The browser sends prompts to the local server.
- The server keeps the API key off the page.
- Cache generated images by prompt hash.
- Generate tiles independently or with `Promise.allSettled`, so partial success is visible.
- Avoid regenerating the selected anchor when its image already exists.

If the user asks for speed, use concurrent generation, but keep the UI progressive. The user should see placeholder tiles immediately, then images should fill in independently.

## Creative Direction Logic

Avoid fixed loops like `soft`, `deep`, `film`, `lens`. Use a broad idea pool with families:

- soft: plush, toy, cozy
- clean: icon, sticker, logo
- cinematic: noir, spotlight, poster-lit
- paint: gouache, watercolor, oil
- graphic: woodcut, riso, editorial
- surreal: collage, organic, dreamtoy
- material: clay, porcelain, chrome
- geometric: origami, low-poly
- retro: pixel, neon
- narrative: storybook, scene, character moment

Selection should raise the weight of that family while preserving some diversity. Rejection should suppress the exact idea and reduce related family weight.

## Handoff Shape

Use the same lightweight handoff wording as the other explorers: selected direction, preserve, avoid, focused next owner, and artifact path.

For style exploration runs, preserve:

- selected style direction;
- visual family and route rationale;
- prompt and style cues;
- rejected directions and suppressed families;
- base asset, territory, or product facts to preserve;
- final owner: `generative-polish`, `charts-polish`, `texture-builder`, `video-explorer`, or another named builder/polish skill.

## Exit Criteria

A successful style exploration ends with:

- a reviewable variant grid or adaptive style board;
- selected and rejected style directions;
- prompt/style metadata that can be reused;
- a named next step for production polish or asset building;
- caveats about generated text, logos, product fidelity, data accuracy, source claims, or unsupported visual assumptions.

## Spec Shape

```json
{
  "meta": {
    "title": "CPG launch style exploration",
    "anchor": "Selected product route",
    "summary": "Compare polish treatments for the approved product direction.",
    "base_asset": "path/to/anchor.png"
  },
  "constraints": {
    "preserve": ["pack shape", "gold foil", "hazelnut cues"],
    "avoid": ["medical claims", "fake endorsements", "new logo text"]
  },
  "routes": [
    {
      "id": "cinematic-macro",
      "label": "Cinematic Macro",
      "family": "cinematic",
      "palette": ["#15110f", "#4c241f", "#9c7245", "#f2eadf", "#ffffff", "#2f3b33"],
      "typography": {
        "tone": "editorial serif",
        "font_stack": "Iowan Old Style, Palatino, Georgia, serif"
      },
      "description": "A low, close, sensory world of warm highlights, dark table surfaces, shallow focus, and quiet premium tension.",
      "prompt": "Create a cinematic macro treatment of the selected product direction. Preserve the product facts exactly. No readable text, no new logos, no claims.",
      "rationale": "Tests premium lighting and close-up sensory detail.",
      "final_owner": "generative-polish"
    }
  ],
  "handoff": {
    "default_owner": "generative-polish"
  }
}
```

## Files

- `assets/style-explorer-app/`: reusable static app template and local image-generation server.
- `scripts/create_style_explorer.py`: copies the template, validates the spec, copies an optional base asset, and writes app data.
