---
name: scene-explorer
description: Explore business, service, customer, retail, and point-of-sale scenes that place a product, venue, service, or offer inside realistic commercial contexts. Use when the user wants scene prompts, product-in-environment exploration, service moments, consumer decision contexts, or reusable scene libraries before mood, style, asset, or polish work.
---

# Scene Explorer

Use this skill when the user wants to explore where a product, service, venue, or offer should appear in the real world.

This is the Explore-stage owner for commercial scenes: point of sale, customer decision moments, service environments, retail displays, showroom settings, customer handoffs, demo spaces, and business contexts.

Read `../../references/experience-contract.md` before writing the user-facing handoff.

Read `../../references/artifact-contracts.md` before creating, repairing, or reporting artifacts.

Read `../../references/codex-exec-image-generation.md` before running image generation.

Read `../../references/image-building-strategy.md` alongside the Codex exec contract for first-pass imagery rules.

## Pipeline Role

Use `scene-explorer` after the user has a subject anchor or a business category and wants to see that subject in relevant environments.

Use `moodboard-explorer` when the question is broad mood, taste, audience feeling, or creative territory.

Use `offer-explorer` when the question is offer-family coverage across the general prompt library.

Use `style-explorer` after a scene exists and the user wants many treatments of that scene.

Use builders or polish skills after a scene is selected:

- `variation-lab` when rendered scene outputs should become controlled remix batches by character, style, camera, format, palette, props, or product placement.
- `generative-polish` for publish-bound marketing image finish.
- `video-explorer` for motion routes based on a selected scene.
- `texture-builder` for backgrounds, surfaces, and material systems.

## Scene Definition

Each scene family should define:

- `sceneArchetype`: the reusable commercial moment, such as boutique try-on, consultation counter, demo island, pickup shelf, or trade-show booth.
- `placeholders`: variable inputs the scene can accept, such as `{subject}`, `{market_context}`, `{customer_type}`, `{tone}`, `{interaction}`, `{supporting_objects}`, `{brand_surface}`, and `{channel_use}`.
- `summary`: what business moment it represents.
- `businessGoal`: why a business would use it.
- `scene`: the visual environment.
- `sceneShape`: the compositional shape, such as counter, wall, table, aisle, booth, consultation desk, demo island, or handoff bay.
- `subjectPlacement`: where the supplied product, service asset, or offer should appear.
- `subjectSlot`: a machine-readable placement contract with slot type, placement, scale, interaction, service fallback, digital fallback, and what to preserve.
- `focus`: what the viewer should understand.
- `decision`: what business decision the scene helps make.
- `elements`: key visible parts.
- `constraints`: facts and safety rails.
- `avoid`: common failure modes.

The scene should be specific enough to produce an image, but generic enough to reuse across brands and future product images. Prefer slot language over hard-coded places or props unless the user has supplied those details.

## Default Pack

Use the hydratable `../../assets/scene-library/packs/business-point-of-sale-scenes.json` for broad cross-industry scene exploration.
Before reading it, run `python ../../scripts/hydrate_assets.py --check`; if it is missing, run `python ../../scripts/hydrate_assets.py` or hydrate from the Drive upload payload with `--source-dir`.

The pack contains 25 reusable scene families across retail, hospitality, services, healthcare, finance, mobility, events, ecommerce, and field sales.

## Workflow

1. Capture the subject anchor.
   - Product image, product description, service brief, venue brief, offer, campaign, or brand moment.
   - Preserve exact product appearance, claims, logo rules, menu facts, regulated claims, channel requirements, and known context.

2. Select scenes.
   - For broad exploration, use the 25-scene pack.
   - For narrow use, choose 5-8 scenes that fit the category and business goal.
   - Avoid near-duplicates. The value is environmental diversity.

3. Build prompts.
   - Use the offer explorer script as the shared prompt-pack engine:

```bash
python3 skills/offer-explorer/scripts/build_offer_explorer.py \
  --offer-name "<subject name>" \
  --subject-kind product \
  --offer-brief "<facts to preserve>" \
  --expansion-map assets/scene-library/packs/business-point-of-sale-scenes.json \
  --pack business-point-of-sale-scenes \
  --scale family \
  --out-dir outputs/imagegen/<subject-slug>-business-pos-scenes
```

Use `--subject-kind venue`, `--subject-kind service`, or `--subject-kind experience` when the subject is not a physical product.

4. Generate images only when requested.
   - A full 25-scene image run can be expensive. Confirm before generating all images.
   - No-image prompt manifests are useful for review and prioritization.
   - When generated scene images exist and an inline MCP review surface is available, render the scene set with `render_moodboard_board_widget`. Do not introduce a separate Scene widget.

5. Handoff.
   - Name the strongest scenes.
   - Explain which scene supports which business use: display, trial, demo, booking, consultation, checkout, event, loyalty, or handoff.
   - Use the same lightweight handoff wording as the other explorers: selected direction, preserve, avoid, focused next owner, and artifact path.
   - Send selected scenes to `variation-lab` for remix batches, `style-explorer` for treatment routes, `generative-polish` for publish-bound finish, `video-explorer` for motion packets, or an asset builder.

## Exit Criteria

A successful scene exploration ends with:

- reusable scene prompts or generated scene options;
- subject facts preserved;
- 5-25 distinct customer/business environments;
- clear business use for each scene;
- selected scene directions and next production owner.

## Files

- `../../assets/scene-library/packs/business-point-of-sale-scenes.json`: hydratable reusable scene-family pack consumed by this skill.
