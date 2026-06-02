---
name: moodboard-explorer
description: Use when a business brief needs image-first mood boards, visual territories, audience feel, campaign references, or brand direction before remix, video handoff, asset production, or polish.
---

# Mood Board Explorer

Build a personalized image-first mood-board stream from a light intake plus inferred profile/context.

Read `../../references/experience-contract.md` before writing the user-facing handoff or reporting artifact links.

Read `../../references/artifact-contracts.md` before creating, repairing, or reporting artifacts.

Read `../../references/codex-exec-image-generation.md` before running image generation.

Read `../../references/image-building-strategy.md` alongside the Codex exec contract for first-pass imagery rules.

## Pipeline Role

This skill owns the Explore stage in the Explore > Build > Polish workflow.

Use it as the broad visual front door for campaign mood, brand direction, creative territories, audience feel, editorial references, and profile-aware inspiration. It produces directional evidence and handoff specs, not canonical production assets.

Explorer outputs should include a reviewable board or gallery, source/context signals, visual territory notes, prompt/spec metadata, recommended directions, and a concise build handoff for the next skill.

Use active Build/Polish owners only after a canonical or selected base exists:

- `variation-lab` for controlled remix batches after a generated mood board or selected territory has concrete outputs to vary.
- `charts-polish` for chart-specific visual variants.
- `video-explorer` for motion routes and selected-route video packets.
- `generative-polish` for publish-bound marketing finish.
- `texture-builder` for reusable textures, backgrounds, or material systems.

If the anchor is a specific product, packaging reference, or product concept and the user wants family-level coverage or review galleries, hand off to `offer-explorer`.

## Workflow

1. Run the intake gate.
   - Read `references/intake.md` before creating a mood board spec.
   - Choose the intake depth from the Mood Board Qualification Scale in `references/intake.md`.
   - Every fresh mood board request must go through intake before spec writing, image generation, or HTML board creation.
   - When MCP widgets are available, render `render_moodboard_board_widget` with no images and an `intake` payload. The mood-board app detects the empty image list and shows the intake suggestions inside the board surface.
   - The chat around the board surface should handle brand/source material, exclusions, and any optional 1-3 reference image request. The empty-board intake should stay to compact question-led chip groups defined in `references/intake.md`.
   - After rendering the empty-board intake, stop and wait for the user selection or app follow-up. Do not create the board spec in the same step.
   - When the request is already an app follow-up such as "Continue with this qualified moodboard intake and create the board," treat intake as complete and proceed directly to context gathering and generation.
   - If MCP widgets are unavailable, ask the same intake questions in chat, wait for the answer, and state that the board intake surface could not be used.

2. Gather profile/context.
   - Read local project instructions such as `AGENTS.md` when present.
   - Use user-provided profile, recent workspace artifacts, or relevant local notes.
   - Infer durable preferences, mood, audience, palette, source imagery, must-have motifs, and constraints. Avoid exposing private details or internal scaffolding in the board.

3. Create the board spec.
   - Write a JSON spec with `meta`, `signals`, and 16-30 `items`.
   - Each item needs `id`, `title`, `caption`, `source`, `tone`, `motif`, `palette`, and `prompt`.
   - When the board will be shown in the MCP mood-board app, add image-specific `remixSuggestions` keyed by `style`, `palette`, `scene`, `props`, `character`, and `format` when you can infer useful directions from that tile. Each suggestion should include `label`, `description`, and `promptHint`; do not rely on generic fixed remix copy when the item title, caption, prompt, palette, motif, or source context gives you sharper directions.
   - Each generated image is one tile inside the mood board, not a mood board itself. Prompts must ask for one self-contained visual reference image: a single scene, object detail, surface, setting, material study, or photographic composition.
   - Prompts should produce image-only outputs: no readable text, no logos, no private details, no UI labels, no collage, no grid, no contact sheet, no scrapbook, no split panels, and no mood-board layout inside the tile.
   - Avoid prompt phrases such as "mood board tile", "moodboard image", "collage", "reference sheet", or "layout". Use phrases such as "single editorial photograph", "single visual reference image", "one composed scene", or "one material detail".
   - Vary composition enough that the board does not repeat too quickly.
   - Include enough signal metadata to support a later build handoff: visual territory, audience cue, palette, motif, and focused output type when clear.

4. Resolve the image generation path.
   - Before creating the local mood-board runtime, follow the Codex exec contract in `../../references/codex-exec-image-generation.md`.
   - Do not ask for credentials or expose legacy fallback choices.
   - Do not ask the user to review a placeholder board shell, pick territories from ungenerated placeholders, approve the visual direction, or open a web artifact before generation is ready.
   - If the user chooses prompt-only planning instead of image generation, deliver the spec and prompt manifest as a planning artifact without presenting the local HTML artifact as the primary review surface.

5. Create the local board runtime after the generation path is confirmed.
   - Use the bundled template and script:

```bash
python3 <skill>/scripts/create_mood_board.py --spec <spec.json> --output <output-dir> --force
node <output-dir>/server.mjs
```

   - Choose an output directory under a stable workspace path such as `outputs/moodboards/<brief-slug>/`, unless the user provides a durable destination.
   - The generated app must include the local HTML/debug artifact and colocated generated assets so the run can be reopened or debugged later.
   - Do not stop at a prompt list, JSON spec, image files, or chat-only summary. The user-facing output of this skill is the inline MCP mood-board widget rendered through `render_moodboard_board_widget`.
   - Never show the local HTML page, local server URL, or server command as the normal review handoff. Those surfaces are debug-only and should be mentioned only when the user explicitly asks to debug or inspect the local server/HTML artifact.
   - MCP handoff invariant: never pass arbitrary local files from chat image generation, `.codex/generated_images`, downloads, or other external folders directly as `items[].imageUrl`, `items[].path`, or `routes[]` to `render_moodboard_board_widget`. First persist those files into the saved `runDirectory` under `generated/`, materialize widget previews under `generated/mcp-thumbs/`, update `data/stream.json` so `imageUrl` points at `/generated/mcp-thumbs/*.jpg`, keep the full-resolution file in `sourceImageUrl`, then render the widget with `runDirectory`.

6. Generate images with the confirmed path.
   - Before high-volume generation, state the planned image count and review surface.
   - Confirm before generating more than 12 images in one pass. "One pass" means the user-approved generation scope for the turn, not a transport batch size.
   - Use the largest supported request batch for the approved count. The local moodboard `/api/images` endpoint accepts up to 64 images and routes them through Codex exec workers, so send 64 or fewer approved images in one request. For approved runs above 64, chunk into groups of 64. Reduce the request size only after a concrete worker failure, timeout, or transport error.
   - For follow-up generation or annotation/remix requests that ask for multiple new images, default to the same Codex exec-backed `/api/images` batch path rather than generating one-off images in chat. Use a single batch for 64 or fewer approved follow-up images, then retry only the failed item ids when the status file shows partial failure.
   - Do not run a separate manual worker probe. The `/api/images` endpoint calls `runtime/codex_exec_image_batch.py`, and that runner automatically performs a preflight before launching the full image set.
   - If local Codex CLI state has previously shown `Operation not permitted`, or the current sandbox is likely to block `~/.codex` state access, request escalated/outside-sandbox execution when starting the local mood-board server instead of first burning a sandboxed generation attempt.
   - If preflight still says Codex cannot initialize local state because `~/.codex` is read-only or an in-process app-server client cannot start, disclose that runtime issue briefly, rerun the local mood-board server with escalated permissions, and retry the same approved batch with a new idempotency key. Do not treat this as a prompt-quality failure.
   - Call the local app server. The server exposes a per-run token at `/api/session`; include it in `X-BV-Run-Token` and set `confirmGenerate: true` so generation cannot be triggered by an untrusted local page:

```bash
node -e "const fs=require('fs'); const crypto=require('crypto'); const base='http://127.0.0.1:<port>'; const data=JSON.parse(fs.readFileSync('<output-dir>/data/stream.json','utf8')); const idempotencyKey=crypto.createHash('sha256').update(JSON.stringify(data.items.map(i=>i.id))).digest('hex').slice(0,16); fetch(base+'/api/session').then(r=>r.json()).then(s=>fetch(base+'/api/images',{method:'POST',headers:{'content-type':'application/json','x-bv-run-token':s.runToken},body:JSON.stringify({images:data.items,confirmGenerate:true,idempotencyKey})})).then(r=>r.json()).then(j=>console.log(JSON.stringify(j,null,2)))"
```

7. Verify visually.
   - Use the local URL or browser only for agent-side verification when needed; do not present it to the user as the review surface.
   - Check that the canvas is image-first, clean, and not repetitive.
   - Confirm primary click selection, expand-to-view, remove, copy, and Open in actions work.
   - Note that clipboard image copy can be browser-permission dependent; the local server clipboard bridge should keep image copy working without routing the visible UI through Finder.
   - After the initial generated batch succeeds, render `render_moodboard_board_widget` with the saved `runDirectory` in the same turn so the generated images and inline mood board appear together.
   - Before handoff, ensure the saved `data/stream.json` uses `/generated/mcp-thumbs/*.jpg` preview images for `imageUrl` and preserves full-resolution generated PNGs in `sourceImageUrl`. The local server should do this automatically after generation; if an inline MCP page reports `totalItemCount` greater than `itemCount`, treat it as a preview/materialization bug rather than a generation failure. The fix is to materialize or repair the item preview under `generated/mcp-thumbs/`, point `imageUrl` at that preview, keep the full-resolution asset in `sourceImageUrl`, and refresh the mounted board from the saved run.
   - If the chat transcript shows attached/generated images but the inline MCP board shows placeholder tiles, diagnose it as a saved-run materialization problem first. Check `data/stream.json`, `run-state.json`, and `generated/mcp-thumbs/`; repair the saved run and refresh from `runDirectory` instead of rerendering with raw local image paths.
   - When a follow-up creates new images for an existing mood board, persist them into the existing `runDirectory`. If the local mood-board server already updated `data/stream.json`, do not call `append_moodboard_board_items`; the mounted board detects the saved run update through its status/page refresh tools.
   - Use `append_moodboard_board_items` only when the new image files/items were produced outside the mood-board server and still need to be merged into the saved run. The append tool owns widget-preview materialization for those external follow-up images: saved stream items should use `/generated/mcp-thumbs/*.jpg` for `imageUrl` and preserve full-resolution images in `sourceImageUrl`. After append, verify the existing mounted board with `get_moodboard_board_status` and `get_moodboard_board_page`; do not re-render `render_moodboard_board_widget` after append unless there is no visible board, the mounted board is stale after status/page refresh, or the user explicitly asks for a separate board.
   - When handing any existing generated board to an inline MCP surface, render `render_moodboard_board_widget` with the saved `runDirectory`.

8. Handle annotation follow-ups.
   - For annotation context, first inspect `structuredContent.sourceImage.sourceImagePath`; if it is missing, resolve `runDirectory + sourceImageUrl` when `sourceImageUrl` points under `/generated/`.
   - Treat spot annotations as requests against the exact original image asset by default. Notes such as "remove this", "erase", "clean up", "fix this spot", "replace this", "crop this", or "preserve this composition" should use the original source image for an image-edit/inpaint-style revision when the available tool supports it, not a prompt-only replacement.
   - Preserve the source canvas size, aspect ratio, composition, lighting, camera, and style unless the user asks for broader changes. Modify only the annotated region when the note is localized. If the image-edit tool returns a slightly different pixel size, do not block board inclusion; append the result with a widget-safe preview and mention the dimension mismatch only if it affects the requested composition or downstream production handoff.
   - Treat notes such as "explore", "remix", "make another version", or "try a new direction" as variation requests rather than localized source edits.
   - Add revised outputs to the existing mood board by default. Include lineage metadata on the new item when possible: `parentItemId`, `sourceImagePath`, `annotation`, `annotationPoint`, and `editMode: "localized-source-edit"`.

9. Prepare the build handoff.
   - Identify the strongest territories or directions.
   - Use the same lightweight handoff wording as the other explorers: selected direction, preserve, avoid, focused next owner, and artifact path.
   - Name the focused next owner when clear: `variation-lab`, `offer-explorer`, `style-explorer`, `texture-builder`, `video-explorer`, `charts-polish`, or `generative-polish`.
   - State what should be preserved in the next stage: palette, motif, composition, audience cue, product facts, source context, or approval constraints.

## Output Defaults

- White background unless the user asks otherwise.
- Dense rounded masonry image board.
- No visible titles, captions, filters, or explanatory UI on the board itself.
- Primary tile click toggles multi-select and selected images attach to the thread composer when the host attachment bridge is available.
- A hover-only expand control opens the large image viewer with copy/Open in actions.
- Tile-level remove controls that persist through browser local storage.

## Exit Criteria

A successful explorer run ends with:

- reviewable visual options;
- source and context signals;
- selected or recommended directions;
- a build handoff naming the next skill and the asset to build;
- an inline MCP mood-board widget for review, plus a durable output path for the board data and generated images;
- clear caveats about generated text, claims, logos, product fidelity, private details, or unsupported visual assumptions.

## User-Facing Handoff

Describe the board as a creative starting point, not as generated files. Name the visual territories, the number of images or routes, what the user should choose next, and the likely business assets this direction can become.

Do not lead with "open the launcher", "open the HTML", "server is running", a generic review link, or "screenshot attached." Do not include a live URL, local HTML link, server path, or server command in the normal mood-board handoff.

Only mention or link the static HTML artifact when the user explicitly asks to debug, inspect, or open the local HTML/server version. In normal use, render `render_moodboard_board_widget` and refer to it as the mood board.

When the mood board is the only reviewable artifact, the primary handoff surface is the inline MCP `mood board`. Ask the user to pick the strongest direction before turning it into controlled Build-stage options such as Variation Lab. Do not create or lead with a `start-here`, index, output folder, manifest, screenshot, HTML link, local URL, or artifact inventory for a normal mood-board-only run.

When image generation is paused because the user has not approved a large run, do not lead with a web artifact. State the planned image count and inline MCP review surface, then ask for approval to generate that set through Codex exec workers. Do not make the spec, manifest, output folder, local HTML artifact, local URL, fallback choices, or worker internals more prominent than the approval action.

If a later step creates a Variation Lab from the board, the handoff focus moves to `Variation Lab`. Mention the original `mood board` only as a secondary context link after the primary Variation Lab action.

## Files

- `assets/mood-board-app/`: reusable static app template and local image-generation server.
- `scripts/create_mood_board.py`: copies the template and writes a board spec.
- `scripts/embed_moodboard_images.py`: copies generated files into the standard moodboard app and refreshes static artifacts.
- `references/intake.md`: compact intake questions and prompt-shaping guidance.
