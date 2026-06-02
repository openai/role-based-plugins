---
name: variation-lab
description: Create universal remix and variation surfaces for Creative Production outputs. Use when the user wants to change subject, product, character, scene, style, copy, format, camera, palette, layout, props, or proof/data after an explorer or builder has produced reviewable outputs.
---

# Variation Lab

Read `../../references/artifact-contracts.md` before creating, repairing, or reporting artifacts.

Read `../../references/experience-contract.md` before writing the user-facing handoff or reporting artifact links.

Use this skill when a Creative Production output should become editable through slots and locks rather than treated as a one-off final image, page, chart, or video.

Variation Lab is the universal Build-stage remix layer. It appears after a review wall, generated asset board, selected route, or built asset when the user is narrowing toward the exact thing they want. It is not a top-level Explore chooser, and it is not final polish by default.

It applies after Ads Explorer, Style Explorer, Scene Explorer, Moodboard Explorer, Shot Explorer, Video Explorer route packets, Generative Polish, or another reviewable Creative Production output when the user wants obvious next moves such as:

- change character;
- change scene or location;
- change subject or product;
- change style;
- change copy;
- change format;
- more like this.

## Role

Explore surfaces remain direction-first, and clean review walls remain inspection-first. Variation Lab is the action-first companion surface for building more controlled versions from outputs the user has already seen.

Do not overload review walls with controls. Instead, create a `variation-manifest.json` plus a Variation Lab surface that shows:

- the selected or generated assets;
- a large selected hero asset with the remaining assets as small image-only tiles underneath;
- small reject controls that cross out weak assets while preserving review context;
- a dropdown-style slot chooser;
- recommended options for the selected slot;
- `+` controls to queue multiple remix ideas;
- a selected-variation tray;
- a compact `Remix` action that sends or copies a conversation-ready request;
- source provenance from the originating skill.

## Workflow

1. Identify the source output.
   - Use a review manifest, selected route file, generated image set, chart/page output, or user-provided asset.
   - Capture source skill, route, prompt, and image path when available.

2. Choose the asset type.
   - Use `image_ad`, `style_route`, `scene`, `moodboard`, `chart`, `document`, `video`, or `generic_visual`.
   - Asset type controls the default slots and locks.

3. Build the lab manifest and static fallback.

```bash
python3 plugins/creative-production/scripts/variation_lab.py \
  --out-dir <run-dir> \
  --review-manifest <manifest.json> \
  --title "Variation Lab" \
  --asset-type image_ad \
  --source-skill ads-explorer
```

4. Use libraries for real generation.
   - `scene` slots should draw from the scene library.
   - `style` and `palette` slots should draw from the style library.
   - `character` slots should draw from the character library when available.
   - `subject` slots should use uploaded references or asset library entries.
   - `copy` and `proof_data` slots must use approved copy, sources, or data.

5. Hand off to the production owner.
   - Use `variation-lab` before final polish when the user wants more versions of an existing output, especially for ads, social posts, product-placement images, pages, charts, or videos.
   - Use `generative-polish` after the selected variation is ready for publish-bound image composition.
   - Use `charts-polish` for chart variations.
   - Use `video-explorer` when a still/frame remix needs a refreshed motion route packet.
   - Use the originating explorer when the user is still exploring.

6. Use the shared mood-board widget for inline image review.
   - For ordinary file-backed Variation Lab runs, generate `variation-lab.html` plus its colocated `server.mjs`, start the local server, and keep the served local URL as the durable `Variation Lab` action surface.
   - When an inline MCP surface is useful, render the current variation asset set with `render_moodboard_board_widget`. The mood-board widget is the default inline review surface for variation images.
   - If local images do not reliably carry into the Apps iframe, link the verified `variation-lab.html` surface instead.
   - For local image assets sent to the shared mood-board widget, pass an absolute filesystem `path` on each asset. Do not use a `localhost` or `127.0.0.1` URL as the primary widget image source; local HTTP URLs are fragile inside the Apps iframe.
   - Keep the served Variation Lab page as the durable action surface for file-based remix state.
   - The served page autosaves selected remix choices to `variation-remix-request.json` after a short debounce. On any follow-up after handing off a lab, check that file first and use it if it contains draft or ready remix items. Do not ask the user to copy/paste selections already saved by the lab.
   - The inline mood-board surface should preserve the review intent: large selected preview, thumbnail review, reject/selection affordances, and follow-up actions for remix/edit where available.
   - Before handoff, verify the selected image renders and the saved remix state remains readable from the local lab.

## Slot And Lock Contract

Slots are changeable:

- subject/product;
- character/persona;
- scene/location;
- style/treatment;
- copy/text;
- format/channel;
- camera/shot;
- palette/materials;
- props/context;
- layout/composition;
- proof/data.

Locks are stable:

- approved claims;
- product, logo, or package fidelity;
- chart data and source notes;
- citations and source evidence;
- dimensions and safe zones;
- selected route intent;
- accessibility and readability constraints.

## Flow Placement

- Explore chooses directions: positioning, mood, scene, offer, style, ad family, logo, or shot route.
- Build creates reviewable outputs: generated ads, social posts, product-placement images, pages, charts, videos, asset boards, and selected route derivatives.
- Variation Lab sits inside Build after those outputs exist. It lets the user queue controlled remix recipes across slots and compiles the resulting batch.
- Polish comes after the user selects a variation or asks for publish-ready cleanup. Use `generative-polish` for deterministic text, chart, logo, dimensions, safe-zone, and metadata control; use `charts-polish` for chart-specific polish.
- If the user asks for fresh directions rather than changes to specific outputs, return to the originating explorer instead of starting Variation Lab.

## Composer UX

The default UI should feel like a batch composer:

1. Select an output from the review set.
2. Reject weak outputs directly from the hero or thumbnail review surface; rejected outputs should remain visible but crossed out.
3. Choose a slot such as Style, Character, Scene, Copy, Palette, or Format. The dropdown label already says `Change`, so option labels should be plain slot names rather than `Change style`.
4. Show recommended options that are useful next, preferably excluding styles already rendered in the current set.
5. Let the user click `+` repeatedly to queue several remix ideas.
6. Show selected ideas as removable chips.
7. Use `Remix` as the primary CTA.
8. Do not show per-option `Send` buttons. Every selected option should queue into one batch so the next chat turn receives a single coherent remix request.
9. On click, combine selected ideas into remix recipes. Group by source asset, treat multiple options in the same slot as alternatives, and combine options across different slots. Two styles and two characters should become four image jobs.
10. Create a conversation-ready handoff request. For file-backed labs, the local server writes the latest draft or ready request to `variation-remix-request.json`; use that saved file on the next user follow-up. If the host exposes `uploadFile` and `sendFollowUpMessage`, attach the JSON and trigger the next chat turn; otherwise keep copy as a compact fallback.
11. After generation, prepend the new images to the same Variation Lab and regenerate `variation-lab.html`; do not send the user to a separate review wall for the normal remix path.

Avoid visible clutter in the default UI: no route titles, "pick this style" helper copy, lock panels, or detailed updated-panel cards. Keep those details in `variation-manifest.json` and the handoff payload.

## Output Shape

Save Variation Lab files beside the source run unless the user specifies another destination:

- `variation-manifest.json`
- `variation-lab.html`
- `server.mjs`
- `variation-remix-request.json` once the user selects or remixes changes in the served lab

The manifest is the reusable contract. The HTML is only the review/action surface.

In user-facing handoffs, link the served local surface as `Variation Lab` rather than asking the user to click the raw `variation-lab.html` filename.

Do not render the dedicated inline Variation Lab widget as the default surface. When an inline MCP image review is useful, render the current asset set with `render_moodboard_board_widget`; keep the served local `Variation Lab` URL as the durable action surface for remix state.

After Variation Lab is created, make it the primary active surface in the final handoff. Ask the user to compare options, reject weak ones, and queue remix changes. Prior boards, review walls, source routes, output folders, manifests, screenshots, and server files are secondary context only and should not be shown as equal choices. Do not create or lead with a `start-here`, index, or landing page unless the user asks to see everything, asks where to start, the session produced three or more user-facing artifacts, the outputs span different artifact types, or the handoff would otherwise contain too many links.

When the user sends any follow-up after interacting with a served lab, first inspect the lab output directory for `variation-remix-request.json`. If it exists and has non-empty `items`, continue from those saved choices without asking the user to restate them. If it exists with `status: "empty"` or no items, ask the user to select options in the lab and click Remix or send a new instruction.

## Reference

Use `references/variation-lab.md` for the shared slot library, asset profiles, and UX contract.
