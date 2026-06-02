---
name: offer-explorer
description: Use when a product, digital product, service, venue, experience, or campaign brief needs offer-led prompt families, contact sheets, review galleries, expansion packs, or coverage checks before remix, asset production, or polish.
---

# Offer Explorer

Generate product-, digital-product-, venue-, service-, or experience-specific image prompts across the business visual prompt library, then package the outputs as a reviewable offer exploration: prompt manifest, JSONL batch, individual images, contact sheet, and HTML gallery.

Read `../../references/experience-contract.md` before writing the user-facing handoff or reporting artifact links.

Read `../../references/artifact-contracts.md` before creating, repairing, or reporting artifacts.

Read `../../references/codex-exec-image-generation.md` before running image generation.

Read `../../references/image-building-strategy.md` alongside the Codex exec contract for first-pass imagery rules.

## Pipeline Role

This skill owns the offer-specific Explore stage in the Explore > Build > Polish workflow.

Use it to test one product, packaging reference, digital product UI, venue, service experience, or product concept across the prompt-family library. It produces directional evidence and handoff specs, not canonical production assets.

Explorer outputs should include offer facts to preserve, family or route coverage, a prompt manifest, generated images when requested, a contact sheet or review gallery, recommended directions, and a concise build handoff for the next skill.

Use active Build/Polish owners only after a canonical or selected base exists:

- `variation-lab` for controlled remix batches after a review gallery has concrete outputs to vary.
- `charts-polish` for chart-specific visual variants.
- `video-explorer` for motion routes and selected-route video packets.
- `generative-polish` for publish-bound marketing finish.
- `texture-builder` for reusable textures, backgrounds, or material systems.

Use `moodboard-explorer` first when the request is broader than an offer anchor: campaign mood, brand direction, audience feel, or creative territory exploration.

Use `scene-explorer` first when the request is primarily about environments, customer moments, point-of-sale scenes, venue/service contexts, or where a supplied offer should appear in the real world.

## Run Types

- `family`: one offer-specific image prompt for each selected prompt family. Core produces 25 items; most expansion packs produce five items. Use for fast coverage checks and creative review.
- `prompt`: every family crossed with the four route prompts: Executive Briefing, Operator Workbench, Campaign Asset, and Editorial Concept. Core produces 100 items; five-family expansion packs produce 20 routed prompts. Use when the full prompt library or a web/hero route needs real variation coverage.
- `pack`: optional domain expansion selected with `--pack`. Core is the default. Expansion packs add specialized families, commonly five, or routed prompts when used with `--scale prompt`. Checked-in supplemental packs can define their own family count.
- `landing-page-web-modules`: defaults to prompt scale so hero/web-module workflows produce 20 variations. Use `--scale family` only when the user explicitly asks for a quick or credit-saving scan.

Available expansion packs:

- `cpg-product-packaging`: packaging, flavor, shelf, ingredient, and ecommerce visuals for CPG products.
- `digital-product-placements`: app, SaaS, dashboard, and UI-first placements where the product interface is the proof object. Produces 12 family-scale jobs by default.
- `saas-product-ui`: product UI, workflow, integrations, outcomes, and feature-adoption visuals.
- `events-webinars`: event hero, agenda, speaker, attendee, and recap visuals.
- `paid-social-testing`: scroll-stopping, UGC, comparison, offer, and retargeting variants.
- `hospitality-venue-scenes`: restaurant, bar, hotel, venue, and service-experience visuals across customer occasions and revenue-driving contexts.
- `partner-customer-proof`: customer story, partner motion, implementation, ROI, and community proof visuals.
- `localization-governance`: regional adaptation, compliance, accessibility, privacy, and regulated-market visuals.
- `seo-geo-content-visuals`: search-answer, explainer, tutorial, glossary, and comparison content visuals.
- `landing-page-web-modules`: hero, feature grid, social proof, pricing, and conversion-section visuals. This pack defaults to 20 routed prompts for hero/web workflows.
- `retail-ecommerce`: PDP, marketplace, bundle, seasonal, and omnichannel merchandising visuals.
- `executive-comms`: board, strategy memo, analyst, roadmap, and incident communications visuals.
- `cross-industry-product-advertising`: placeholder-driven product ad archetypes that adapt the environment, surface, lighting, benefit signal, and supporting cues to the supplied product rather than forcing a fixed product/background pairing.

## Workflow

1. Capture the offer anchor.
   - If the user provides an image, describe the product facts that must be preserved: pack shape, color, logo placement, materials, flavor cues, visible ingredients, and category.
   - If the user provides a digital product, app, SaaS, dashboard, or UI-first brief, extract the product surface, workflow, proof cues, privacy constraints, and what UI details must stay sparse or exact.
   - If the user provides a venue, service, or experience brief, extract the facts that must be preserved: location, category, audience, occasion, service moment, available references, and business goal.
   - If the user provides only a product or venue brief, extract the same facts from the brief.
   - Do not introduce another brand, venue, product category, endorsement, or unsupported claim.

2. Choose the run size.
   - Use `--scale family` for one image per family.
   - Use `--scale prompt` for the routed prompt matrix: 100 items for core, or 20 items for a five-family expansion pack.
   - Use `--pack <id>` when the request clearly belongs to a specialized marketing surface.
   - Use `--subject-kind digital-product --pack digital-product-placements` for app, SaaS, dashboard, AI feature, or UI-first work where the product interface should carry the proof.
   - For hero workflow, landing-page hero, web hero, or page-module variation requests, use `--pack landing-page-web-modules`. Let the script default to prompt scale or pass `--scale prompt` explicitly in the plan; do not treat a five-family scan or Explore's six path tiles as the completed hero variation set.
   - Use `--subject-kind venue` for restaurants, hotels, bars, hospitality venues, and other location-based service experiences.
   - Do not generate 100 images without confirming cost/time expectations unless the user has explicitly asked for the full generation.

3. Build the exploration batch.
   - Use `scripts/build_offer_explorer.py`.
   - Before reading `references/family-map.json` or `references/expansion-packs.json`, run `python ../../scripts/hydrate_assets.py --check`.
   - If the check reports missing assets, run `python ../../scripts/hydrate_assets.py` or hydrate from the Drive upload payload with `--source-dir`.
   - The script reads hydratable `references/family-map.json`, optional `references/expansion-packs.json`, and checked-in supplemental packs from `references/packs/`, writes `jobs.jsonl`, and writes `prompts-manifest.json`.
   - Use one prompt per family or one prompt per family-route combination. Do not collapse families or generate weak synonym variants.

4. Generate images when requested.
   - Use Codex exec fanout from `../../references/codex-exec-image-generation.md`.
   - Use the bundled `build_offer_explorer.py` script, not ad hoc API code.
   - Default generation settings: 4 workers, 2 attempts, 600 seconds per attempt.
   - For expensive or high-volume changes beyond the 25-image family run, confirm before running.

5. Package review artifacts.
   - Contact sheet: `offer-contact-sheet.png`
   - Review board: `review-board.html`
   - Prompt manifest: `prompts-manifest.json`
   - Batch input: `jobs.jsonl`
   - Originals and web-sized image copies in the output folder.
   - The script writes `moodboard-widget-payload.json` through the shared review renderer. When an inline MCP review surface is available, pass that payload to `render_moodboard_board_widget`. Do not introduce a separate Offer widget or rename the skill to fit the surface.

6. Review quality.
   - Confirm the product, digital product UI, venue, service, or experience remains visibly central in every family.
   - For digital products, verify that UI/product-proof language remains visible in the prompt and that the image direction does not drift into generic abstract SaaS imagery.
   - Watch for generated text errors, fake endorsements, unintended competitor/category drift, unsupported claims, or over-dense UI text.
   - Treat packaging/logo text fidelity as directional unless the workflow uses a stricter image-edit/reference-preservation path.

7. Prepare the build handoff.
   - Identify the strongest families, routes, or expansion-pack directions.
   - Use the same lightweight handoff wording as the other explorers: selected direction, preserve, avoid, focused next owner, and artifact path.
   - Name the focused next owner when clear: `variation-lab`, `style-explorer`, `texture-builder`, `video-explorer`, `charts-polish`, or `generative-polish`.
   - State what should be preserved in the next stage: subject facts, product or venue details, material/service cues, category, route/family rationale, channel fit, and approval constraints.

## Commands

Prepare a visual exploration without generating images:

```bash
python3 skills/offer-explorer/scripts/build_offer_explorer.py \
  --offer-name "Ferrero Rocher Milk Hazelnut" \
  --offer-brief "Premium vertical chocolate-bar box with gold foil side panels, warm brown center, white/gold medallion area, milk chocolate pieces, hazelnut inclusions, whole and halved hazelnuts." \
  --scale family \
  --out-dir outputs/imagegen/ferrero-family-review
```

Generate the full 25-image exploration:

```bash
python3 skills/offer-explorer/scripts/build_offer_explorer.py \
  --offer-name "Ferrero Rocher Milk Hazelnut" \
  --offer-brief "Premium vertical chocolate-bar box with gold foil side panels, warm brown center, white/gold medallion area, milk chocolate pieces, hazelnut inclusions, whole and halved hazelnuts." \
  --scale family \
  --out-dir outputs/imagegen/ferrero-family-review \
  --generate --force
```

Prepare the full 100-prompt exploration without generating images:

```bash
python3 skills/offer-explorer/scripts/build_offer_explorer.py \
  --offer-name "Ferrero Rocher Milk Hazelnut" \
  --offer-brief-file outputs/imagegen/ferrero-family-review/offer-brief.txt \
  --scale prompt \
  --out-dir outputs/imagegen/ferrero-100-offer-explorer
```

Prepare a domain expansion pack without generating images:

```bash
python3 skills/offer-explorer/scripts/build_offer_explorer.py \
  --offer-name "Ferrero Rocher Milk Hazelnut" \
  --offer-brief-file outputs/imagegen/ferrero-family-review/offer-brief.txt \
  --pack cpg-product-packaging \
  --scale prompt \
  --out-dir outputs/imagegen/ferrero-cpg-product-packaging-offer-explorer
```

Prepare a 12-direction digital product placement exploration without generating images:

```bash
python3 skills/offer-explorer/scripts/build_offer_explorer.py \
  --offer-name "Codex Team Review" \
  --offer-brief "SaaS workflow for reviewing coding-agent work. Preserve product UI, task queue, diff review, approval controls, team handoff, and privacy-safe placeholder data." \
  --subject-kind digital-product \
  --pack digital-product-placements \
  --scale family \
  --out-dir outputs/imagegen/codex-team-review-digital-product-placements-offer-explorer
```

Prepare a 20-variation landing-page hero/web-module exploration without generating images:

```bash
python3 skills/offer-explorer/scripts/build_offer_explorer.py \
  --offer-name "New Product Launch" \
  --offer-brief "Launch campaign for a product page. Preserve product, audience, page goal, proof cues, CTA, brand constraints, and mobile-safe hero composition." \
  --pack landing-page-web-modules \
  --scale prompt \
  --out-dir outputs/imagegen/new-product-launch-landing-page-web-modules-offer-explorer
```

Generate the full 100-image prompt exploration only when explicitly requested:

```bash
python3 skills/offer-explorer/scripts/build_offer_explorer.py \
  --offer-name "Ferrero Rocher Milk Hazelnut" \
  --offer-brief-file outputs/imagegen/ferrero-family-review/offer-brief.txt \
  --scale prompt \
  --out-dir outputs/imagegen/ferrero-100-offer-explorer \
  --generate --force
```

Rebuild the gallery/contact sheet from existing images:

```bash
python3 skills/offer-explorer/scripts/build_offer_explorer.py \
  --offer-name "Ferrero Rocher Milk Hazelnut" \
  --offer-brief-file outputs/imagegen/ferrero-family-review/offer-brief.txt \
  --scale family \
  --out-dir outputs/imagegen/ferrero-family-review \
  --review-only
```

Prepare a restaurant scene exploration without generating images:

```bash
python3 skills/offer-explorer/scripts/build_offer_explorer.py \
  --offer-name "Upscale French Restaurant in San Francisco" \
  --subject-kind venue \
  --offer-brief "French restaurant in San Francisco. Goal: increase sales by attracting a more upscale clientele. Preserve: French dining cues, San Francisco local context, premium but warm hospitality, reservation intent, date-night, private dining, business lunch, wine dinner, and neighborhood discovery occasions. Avoid tourist Paris cliches, fake awards, invented menu claims, and discount framing." \
  --pack hospitality-venue-scenes \
  --scale family \
  --out-dir outputs/imagegen/french-restaurant-hospitality-scenes
```

## Output Defaults

- Use a white, inspection-first review page.
- In user-facing handoffs, link the review artifact as `review board` rather than exposing the raw filename.
- Include short family labels in review artifacts.
- Keep generated images offer-led, with sparse labels only when the family requires a board, dashboard, or UI-like packet.
- Save family exploration output under `outputs/imagegen/<offer-slug>-offer-explorer/` unless the user specifies a folder.
- Save prompt exploration output under `outputs/imagegen/<offer-slug>-100-offer-explorer/` unless the user specifies a folder.
- Save expansion pack prompt output under `outputs/imagegen/<offer-slug>-<pack-id>-offer-explorer/` unless the user specifies a folder.

## Exit Criteria

A successful explorer run ends with:

- reviewable offer-led visual options;
- offer facts and source/context signals;
- selected or recommended directions;
- a build handoff naming the next skill and the asset to build;
- clear caveats about generated text, claims, logos, product fidelity, endorsements, category drift, or unsupported visual assumptions.

## Files

- `scripts/build_offer_explorer.py`: builds prompts, optionally runs ImageGen, and packages review artifacts.
- `references/family-map.json`: hydratable 25 prompt families and 4 route prompts used by the explorer.
- `references/expansion-packs.json`: hydratable specialized prompt-family packs for business and marketing use cases.
