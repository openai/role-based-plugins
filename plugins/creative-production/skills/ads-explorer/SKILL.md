---
name: ads-explorer
description: Explore a supplied product, service, venue, or offer across a diverse 25-family image-ad prompt library. Use when the user wants Ads Explorer, ad concept walls, image ad prompts, static ad variants, broad campaign ad exploration, or a review wall before final production.
---

# Ads Explorer

Use this skill when the user wants to see many different image-ad directions from one subject anchor: product reference image, packaging, service, venue, app, campaign offer, or business asset.

This is the Explore-stage owner for ad-format diversity. It is intentionally broader than `scene-explorer` and more ad-specific than `offer-explorer`.

Read `../../references/experience-contract.md` before writing the user-facing handoff.

Read `../../references/artifact-contracts.md` before creating, repairing, or reporting artifacts.

Read `../../references/codex-exec-image-generation.md` before running image generation.

Read `../../references/image-building-strategy.md` alongside the Codex exec contract for first-pass imagery rules.

## Pipeline Role

Use `ads-explorer` when the request is about ad formats, campaign images, paid social concepts, launch ads, proof-led ads, ecommerce ads, OOH mockups, UGC thumbnails, surreal product posters, or a visual wall of static ad directions.

Use `scene-explorer` first when the main question is where the product should appear in the real world.

Use `style-explorer` after the user chooses an ad direction and wants treatment routes.

Use `variation-lab` after the review wall when the user wants to keep compiling the board with controlled changes such as different character, scene, copy, format, crop, style, palette, camera, props, or product placement.

Use `variation-lab`, `generative-polish`, `video-explorer`, or another active Build/Polish owner after a direction is selected.

## Default Library

Use the hydratable pack at `../../assets/image-ad-library/packs/diverse-image-ad-archetypes.json`.
Before reading the pack, run `python ../../scripts/hydrate_assets.py --check`; if it is missing, run `python ../../scripts/hydrate_assets.py` or hydrate from the Drive upload payload with `--source-dir`.

The pack contains 25 reusable ad families. It declares:

- per-family prompt structure;
- per-family image size where a non-square crop is better;
- review-wall behavior with captions suppressed;
- copy safety rules for exact headline, CTA, claims, proof, and placeholder text.

## Workflow

1. Capture the subject anchor.
   - If the user supplies an image, preserve exact visible product facts: silhouette, colors, materials, labels, logos, markings, proportions, and use context.
   - If the user supplies a brief only, extract the same facts from the brief.
   - Capture approved copy, headline, CTA, claims, proof, audience, palette, channel, and avoid list.

2. Build the ad prompt wall.
   - Use the shared prompt-pack engine with the ad library:

```bash
python3 plugins/creative-production/skills/ads-explorer/scripts/build_ads_explorer.py \
  --ad-name "<subject name>" \
  --subject-kind product \
  --ad-brief "<facts to preserve, approved copy, audience, palette, and avoid list>" \
  --out-dir outputs/imagegen/<subject-slug>-diverse-image-ads
```

3. Generate images when requested.
   - Use Codex exec fanout from `../../references/codex-exec-image-generation.md`.
   - If a source image is supplied, include its path and preservation requirements in job metadata and prompts.
   - If no source image is available, use text-only generation from the prompt manifest.
   - Do not generate all 25 images unless the user asks for generation or clearly wants a full review wall.

4. Render the review wall.
   - The default review should be image-led: a wall of ads, no subtitles or captions under tiles.
   - Prompt details, family names, and sizing metadata should stay in `prompts-manifest.json` and `visual-explorer-metadata.json`.
   - Use mixed sizes from the pack. Do not force every ad to square.
   - When an inline MCP review surface is available, render the generated ad set with `render_moodboard_board_widget`. Do not introduce a dedicated Ads widget.

5. Handoff.
   - Identify strongest ad families and any format fit issues.
   - Note copy or product-fidelity risks.
   - Use the same lightweight handoff wording as the other explorers: selected direction, preserve, avoid, focused next owner, and artifact path.
   - Send selected directions to `variation-lab` for remix batches, `style-explorer` for treatment routes, `generative-polish` for publish-bound static image finish, `video-explorer` for motion packets, or another active Build/Polish owner.

## Copy Rules

- Use exact supplied text only.
- Avoid subtitles, explanatory body-copy captions, fake price tags, fake reviews, invented proof, and unsupplied CTA text.
- For proof, comparison, certification, ecommerce, and event formats, use placeholder zones unless the brief supplies real details.
- Treat generated text as directional. Final publish assets need deterministic type/layout.

## Exit Criteria

A successful Ads Explorer run ends with:

- 25 ad prompt directions or generated ad images;
- an image-led review wall;
- no caption-heavy review framing;
- mixed aspect ratios where useful;
- product facts and copy constraints preserved;
- selected directions and next production owner;
- if the user asks for more versions of selected ads, the next owner is `variation-lab` and new results should be prepended to the same lab rather than a separate review wall.

## Files

- `../../assets/image-ad-library/`: hydratable reusable ad library and registry.
- `../../assets/image-ad-library/packs/diverse-image-ad-archetypes.json`: hydratable default 25-ad pack.
- `scripts/build_ads_explorer.py`: wrapper around the shared offer explorer prompt-pack engine.
