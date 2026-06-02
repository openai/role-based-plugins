---
name: generative-polish
description: >-
  Create publish-safe generative polish for business visuals. Use when the user
  asks to make a selected asset, social card, carousel, launch visual, chart
  card, or creative pack visually stronger while preserving exact text, data,
  logos, dimensions, safe zones, filenames, and review metadata.
---

# Generative Polish

Generative polish is a bounded creative technique: build the message-critical creative with deterministic tools, generate or edit only the visual finish with ImageGen, then re-compose the final asset deterministically.

The goal is to get premium visual quality without letting generative image tools rewrite approved copy, distort charts, alter product claims, invent UI, or break social placement specs.

Read `../../references/experience-contract.md` before writing user-facing plans, handoffs, or artifact links.

Read `../../references/artifact-contracts.md` before creating, repairing, or reporting artifacts.

Read `../../references/review-renderer.md` before creating local review pages, contact sheets, or asset pack previews.

Read `../../references/codex-exec-image-generation.md` before running ImageGen.

Read `../../references/image-building-strategy.md` alongside the Codex exec contract for first-pass imagery rules.

When using deterministic SVG, chart, page, or layout exports from another workflow, treat that file as the canonical layer. Do not use generative polish to alter chart data, rewrite approved text, change template status, or replace canonical source artifacts.

Use approved media only when the user provides it or points to a separately maintained source. The plugin no longer bundles a brand-media registry, so publish-bound marketing derivatives should treat media inputs as explicit external references.

Use `variation-lab` before this skill when the user wants to explore changes to an existing output, such as character, scene, product placement, style, palette, copy direction, crop, camera, format, props, layout, or proof/data. Use generative polish after the user has selected a variation and needs publish-bound exactness for text, charts, logos, dimensions, safe zones, filenames, and review metadata.

When this skill receives a selected style system or concrete output format from a focused handoff, treat it as production intent. Build actual reviewable outputs or clearly state the missing production input. Do not return only an inventory, route board, or planning list after the user has asked to continue with a selected style.

## Hero Variation Routing

If the user asks for a hero workflow, landing-page hero, web hero, or page-module directions and wants options, variations, or exploration, route to `offer-explorer` with `--pack landing-page-web-modules` at prompt scale before using this skill. That route produces 20 reviewable hero/web-module variations by default. Do not treat Explore's six path tiles, a five-family web-module scan, or the 3-6 ImageGen fallback as the completed hero variation set.

Use generative polish for hero work only after there is a selected direction, deterministic base, fixed destination format, or publish-bound asset to finish. If a hero request mixes exploration and final polish, create or request the broader review board first, then polish the selected hero.

## Core Principle

Use each layer for what it can control best:

| Layer | Owner | Reason |
|---|---|---|
| Exact copy, claims, labels, CTA | Python, SVG, HTML, design template | Text must remain reviewable and exact. |
| Data, charts, axes, numbers | Python, SVG, charting library | Values and geometry must remain accurate. |
| Logo placement, safe zones, dimensions | Python, SVG, HTML, template | Brand and placement constraints must be deterministic. |
| File naming, manifests, preview packs | Python, Canva resize tooling, or deterministic export tooling | Handoff must be repeatable. |
| Background mood, lighting, texture, depth | ImageGen | These benefit from generative visual quality. |
| Editorial scene, abstract metaphor, hero treatment | ImageGen | These are high-polish but usually not claim-critical. |

Do not let ImageGen own precision-critical layers unless the user explicitly accepts the risk and the output is only exploratory.

## Default Workflow

1. Define the asset system.
   - Identify the destination formats, aspect ratios, channels, approval state, and whether the work is exploratory or publish-bound.
   - For social placement packs, keep the deterministic master as source of truth. If the selected asset lives in Canva or the user wants Canva-native social variants, use `canva:canva-resize-for-all-social-media` as the social polish/resize owner. Otherwise export exact-size local variants from the deterministic renderer.

2. Lock the deterministic base.
   - Create the exact card layout, text, chart, CTA, logo area, source line, and safe zones in Python, SVG, HTML/CSS, or another deterministic renderer.
   - Keep text and data in editable variables when possible.

3. Generate the polish layer.
   - Use ImageGen for backgrounds, textures, dimensional treatment, lighting, editorial illustration, or scene concepts.
   - Prompt for no text, no logos, no charts, no UI, and no claims unless those elements are meant to be purely abstract.
   - Preserve empty areas or safe zones where deterministic overlays will sit.

4. Composite deterministically.
   - Bring the ImageGen layer back into Python/SVG/HTML and place exact copy, charts, marks, and metadata on top.
   - Export final fixed-size assets from the deterministic renderer.

5. Validate before handoff.
   - Check dimensions, crop, contrast, type size, chart accuracy, text exactness, source/provenance, filenames, manifests, and preview-board behavior.
   - For local image packs, create a shared-review-renderer preview or contact sheet so the user sees the actual exported assets in the standard Creative Production review style.
   - For publish-bound marketing work, label review status and route high-risk items through the relevant quality gate.

## ImageGen Prompting Rules

Prompts for polish layers should constrain ImageGen away from approval-sensitive content:

```text
Create a premium visual background/polish layer for a marketing social card.
No text, no logos, no UI, no charts, no numbers, no product claims, no watermarks.
Leave clean negative space for deterministic copy and chart overlays.
Use polished lighting, depth, texture, and composition suitable for a high-quality launch campaign.
```

When using an existing deterministic card as a reference, state what must not change:

```text
Use the provided image only as a composition/style reference.
Do not rewrite, add, or interpret any text.
Do not alter chart values, axes, logos, product UI, or source lines.
Focus only on background polish, depth, lighting, and texture.
```

If exact text or charts appear in an ImageGen output, treat them as non-final. Rebuild those elements deterministically after generation.

## Common Patterns

### Social Carousel

- Python/SVG/HTML owns the card grid, exact headline, chart, CTA, and source note.
- ImageGen creates card backgrounds, textures, editorial scenes, or metaphorical hero visuals.
- Final cards are composited and exported as fixed PNGs, then previewed in social placements.

### Chart Card

- Python renders the chart and labels from data.
- ImageGen creates a polished backdrop or material treatment.
- Python overlays the chart, headline, and source line after generation.
- If a validated chart SVG or export exists, use that as the exact chart layer. Use `charts-polish` only for exploratory chart-specific image variants; use this generative-polish workflow for publish-bound chart cards that require deterministic recomposition.

### Launch Hero Visual

- ImageGen creates a hero scene or abstract campaign visual.
- Deterministic layout adds launch name, CTA, product/source link, and review labels.
- For first-pass hero exploration, use the 20-variation `offer-explorer` web-module route before creating publish-bound composites.
- Avoid generated screenshots or fake product UI unless clearly marked exploratory.

### Social Polish / Format Pack

- Keep the deterministic full-size asset as the master.
- When an inline MCP review surface is useful for generated polish packs, render the exported image set with `render_moodboard_board_widget`; keep deterministic manifests and exact-size exports as the durable source of truth.
- If the master is a Canva design, or the user asks for Canva/social exports, use `canva:canva-resize-for-all-social-media` to create platform copies, preserve the original design, and return PNG export links plus Canva edit links.
- If the work is local and not Canva-backed, export exact-size variants from the deterministic renderer with `full/`, `preview/`, manifest, platform index, and any needed placement preview.
- Use generative polish before final export or as a controlled background/texture layer inside the format generator. Do not let resize or adaptation change copy, chart data, logos, claims, or source lines.

## Guardrails

- Do not use ImageGen to generate final legal, pricing, availability, benchmark, security, partner, customer, or product-capability claims.
- Do not rely on ImageGen-rendered text, numbers, code, charts, tables, logos, or source lines for publish-bound work.
- Do not create fake product UI, unofficial brand marks, customer proof, or partner lockups.
- Do not hide that an image layer was generated when review context requires provenance.
- Do not let visual polish override readability, contrast, accessibility, or placement fit.

## Output Shape

Save generated polish runs under `outputs/imagegen/generative-polish/<run-id>/` unless the user specifies another folder. Keep deterministic bases, ImageGen layers, final composites, manifests, and preview packs separated inside the run folder.

For local asset packs triggered by Explore or an asset-board handoff, return the pack as exports plus manifest plus shared review page/contact sheet. Use the shared renderer preset that matches the review surface, usually `image-wall` for asset grids or `detail-review` for one selected route. The inline widget can be offered as a convenience after the files exist, but it is not the primary deliverable.

When social variants are produced through Canva, report Canva edit links and PNG export links separately, and state that the original source design was left unchanged.

For generative polish requests, respond with:

```text
Generative polish plan: <asset or campaign>
Deterministic layers:
- <copy/chart/logo/dimensions/etc.>

ImageGen polish layers:
- <background/texture/lighting/scene/etc.>

Composition method:
- <Python/SVG/HTML/template path>

Artifact paths:
- <deterministic base / ImageGen layer / final exports / manifest>

Social polish:
- <local format pack / Canva resize outputs / not needed>

Source and media provenance:
- <approved media, user-provided references, generated layers, external design links>

Review risks:
- <text, chart, claim, logo, screenshot, partner/customer, etc.>

Validation checklist:
- <dimensions, text exactness, chart accuracy, contrast, manifest, previews>

Next action:
- <generate polish prompt / build deterministic base / export format pack / request approval>
```
