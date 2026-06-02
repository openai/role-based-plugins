---
name: shot-explorer
description: Explore selected camera-angle, crop, zoom, and macro-detail variants from an uploaded image. Use when the user wants a Shot Explorer, product shot variants, alternate views, closeups, pan/zoom exploration, or camera/composition options before polish.
---

# Shot Explorer

Use this skill when the user has a visual anchor and wants to choose which shot directions to generate: alternate angles, crop/pan options, zooms, macro details, and one useful surprise angle.

Read `../../references/experience-contract.md` before writing the user-facing handoff or reporting artifact links.

Read `../../references/artifact-contracts.md` before creating, repairing, or reporting artifacts.

Read `../../references/codex-exec-image-generation.md` before running image generation.

Read `../../references/image-building-strategy.md` alongside the Codex exec contract for first-pass imagery rules.

## Pipeline Role

This skill owns shot and composition exploration in the Explore > Build > Polish workflow. It starts from an existing image and produces reviewable shot options that can feed `variation-lab`, `generative-polish`, `video-explorer`, or another active Build/Polish skill.

Use it after there is a visual anchor to preserve:

- a product, packaging, object, apparel, venue, UI, character, or scene reference;
- a selected generated image that needs camera-angle exploration;
- a base asset from `offer-explorer`, `scene-explorer`, `style-explorer`, or `generative-polish`.

It does not produce final publish-bound ad layouts, deterministic product labels, legal copy, or brand-safe final crops. If the user needs a first broad visual territory, use `moodboard-explorer` or `offer-explorer` first. Use `variation-lab` after rendered shot outputs when the user wants controlled remixing.

## Anchor And Scope

Preserve the source image's subject identity:

- silhouette, proportions, colors, visible materials, logos, packaging shape, and important surface details;
- category and business context;
- approved copy or markings already present in the source;
- channel constraints, if supplied.

Vary only camera and composition dimensions:

- angle: overhead, side profile, three-quarter, low hero, back;
- crop/pan: pan left/right, zoom in, wider context;
- detail: macro texture, material edge, surface texture;
- surprise: one commercially useful unexpected angle.

Do not introduce unsupported claims, fake endorsements, new brand names, competitor marks, or new readable text unless the user explicitly asks for that.

## Core Pattern

Shot Explorer should use the same interaction shape as the other Creative Production explorers:

1. Capture or confirm the source image.
2. Render a compact intake widget so the user can tick the shot directions they want.
3. Stop and wait for the widget selection or follow-up.
4. Generate only the selected shot directions as a batch.
5. Display the results through the same shared Creative Production `image-wall` review HTML and contact sheet used by the other explorers, not a bespoke Shot Explorer control app or special Shot-only review preset.
6. End with shot metadata and a handoff to the next stage.

The first user-visible surface is the intake picker, and the main review surface is the shared renderer used by the other explorers. Do not create a separate dark upload/control/feed UI for ordinary Shot Explorer runs.

## Workflow

1. Capture the source.
   - If the user provides an image in chat or a file path, use it as `--base-asset`.
   - If no source is available, ask for the image before continuing; shot exploration depends on reference-image preservation.
   - State what must survive in every shot: subject shape, color, materials, logo/text treatment, and category.

2. Run the intake gate.
   - When MCP widgets are available, render `render_shot_intake_widget` with three compact groups: angles, crops, and details.
   - Include any obvious source context in the widget title or summary, but keep the widget itself to tickable shot directions.
   - After rendering the intake widget, stop and wait for the selection or widget follow-up. Do not create prompts, generate images, or render review HTML in the same step.
   - When the request is already a widget follow-up such as "Continue with this qualified shot intake and create the shots," treat intake as complete and proceed.
   - If MCP widgets are unavailable, ask the same shot-direction choices in chat and wait for the answer.

3. Build the selected shot batch.
   - Use the bundled script:

```bash
python3 <skill>/scripts/create_shot_explorer.py \
  --base-asset "<path-to-image>" \
  --output <output-dir> \
  --selected overhead \
  --selected side-profile \
  --selected macro-detail \
  --force
```

   - Choose an output directory under a stable workspace path such as `outputs/shot-explorer/<brief-slug>/`, unless the user provides a durable destination.
   - The script writes `data/shot-spec.json`, `data/prompts-manifest.json`, `data/jobs.jsonl`, `data/selected-shot-route.json`, `data/handoff.md`, `review-board.html`, `moodboard-widget-payload.json`, and a contact sheet when images exist.
   - If generation is not approved, save the prompt manifest and handoff metadata so the run can resume later. Do not present prompt cards as the main user-facing review result.

4. Generate shots when approval is available.
   - Before high-volume generation, state the planned shot count and review surface.
   - Default to Fast mode for exploration. Use Pro mode only for selected directions or when preservation quality matters.
   - Source-image metadata is included in worker context, but generation is prompt-driven through native image generation; keep that caveat in handoff metadata.
   - Run selected generation with:

```bash
python3 <skill>/scripts/create_shot_explorer.py \
  --base-asset "<path-to-image>" \
  --output <output-dir> \
  --selected overhead \
  --selected side-profile \
  --selected macro-detail \
  --mode fast \
  --generate \
  --force
```

5. Review and export the handoff.
   - Open `review-board.html` or show it in the local/in-app browser only for agent-side verification or explicit debug requests.
   - Use the shared review page and contact sheet for inspection; do not launch a separate Shot Explorer server UI.
   - When an inline MCP review surface is available, pass `moodboard-widget-payload.json` to `render_moodboard_board_widget`. Keep the shot intake widget for pre-generation selection only.
   - The review wall should use the shared `layout: "wall"` / `image-wall` renderer and show generated images only. Prompt text belongs in `data/prompts-manifest.json`, not on the board.
   - If generated images are missing, leave the review page as the shared pending state and point to the manifest for resumable generation. Do not use prompt cards as a visible substitute for images.
   - Identify the strongest shot direction in the handoff once the user chooses one.
   - Keep rejected directions out of the next stage when the user has explicitly rejected them.

## Shared Review Output

Use the shared static review renderer, via `scripts/review_renderer.py` through the Shot Explorer script. Do not hand-write custom review HTML for this skill.

Review output should be:

- white-background, image-first, and consistent with other Creative Production review boards;
- one generated shot per tile;
- captions suppressed by default, following Ads Explorer's image-wall behavior;
- no Shot-specific review controls, side panels, prompt cards, or custom preset; use the same static image-wall HTML contract as Ads/Offer Explorer;
- prompt and generation details stored in metadata, not dominant on the first screen;
- durable under the run output folder, not only a transient localhost URL.

## Handoff Shape

Use the same lightweight handoff wording as the other explorers: selected direction, preserve, avoid, focused next owner, and artifact path.

For shot exploration runs, preserve:

- source image metadata and source hash;
- selected shot IDs, labels, groups, prompts, and generated image paths;
- rejected directions when the user has ruled them out;
- constraints to preserve and avoid;
- mode, model, quality, size, and generation caveats;
- final owner: `variation-lab`, `generative-polish`, `video-explorer`, or another named production skill.

## Exit Criteria

A successful shot exploration ends with:

- completed intake or an explicit decision to skip intake;
- generated or prompt-only shot options for the selected directions;
- a shared `review-board.html` gallery and contact sheet when images exist;
- reusable prompt metadata and source preservation constraints;
- a named next step for controlled remixing or production polish;
- caveats about generated text, logo fidelity, inferred reverse angles, product accuracy, and unsupported visual assumptions.

## Spec Shape

```json
{
  "meta": {
    "title": "Shot Explorer",
    "stage": "Shot exploration",
    "anchor": "Uploaded product image",
    "summary": "Select shot directions and generate camera variants."
  },
  "constraints": {
    "preserve": ["subject silhouette", "materials", "colors", "visible logo placement"],
    "avoid": ["new claims", "new brand names", "fake endorsements"]
  },
  "shots": [
    {
      "id": "macro-detail",
      "label": "macro detail",
      "group": "detail",
      "prompt": "Using the uploaded image as the source reference, create an extreme macro detail product photograph. Preserve the source subject identity, materials, colors, logo placement, surface texture, and category. No new readable text, claims, labels, or logos."
    }
  ],
  "review": {
    "layout": "wall",
    "title": "Shot Explorer",
    "showCaptions": false,
    "showPrompts": false
  },
  "handoff": {
    "default_owner": "generative-polish"
  }
}
```

## Files

- `scripts/create_shot_explorer.py`: validates the spec, copies an optional base asset, generates selected image-edit shots when approved, and renders the shared review page.
