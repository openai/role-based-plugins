# Creative Production v0.1.10

Creative Production helps teams explore visual directions, build business assets, and polish selected outputs without losing the business context.

Explore
- $explore Start from this restaurant campaign brief and show the creative paths forward.
- $positioning-explorer Shape audience, occasion, proof, and growth-route options before visual generation.
- $moodboard-explorer Make a Memorial Day mood board for premium chocolates based on this brief.
- $scene-explorer Show this shoe in 25 business point-of-sale scenes across retail, service, demo, pickup, and handoff contexts.
- $scene-explorer Explore an upscale French restaurant as venue scenes across date night, private dining, business lunch, wine dinner, and local discovery.
- $offer-explorer Explore boxed chocolate gift set visual options based on this product image.
- $ads-explorer Explore this product image across 25 diverse static ad directions as an image-led review wall.
- $logo-explorer Explore logo concepts for this brand brief and usage context.
- $shot-explorer Upload this product image and generate overhead, side, back, pan, zoom, and extreme-detail shot variants.
- $style-explorer Explore reusable visual style routes for this selected chocolate concept or business brief.
- $video-explorer Explore vertical video territories, hooks, motion styles, scenes, pacing, and format routes for this campaign.

Build
- Remix and Adapt
  - $variation-lab Remix selected ads, social posts, product-placement images, pages, charts, or videos by changing subject, character, scene, style, copy, format, camera, palette, layout, props, or proof/data after a review wall or asset board.

Polish
- $charts-polish Polish the chocolate sales chart based on this chart.
- $generative-polish Make a publish-ready chocolate social asset based on this content and image.

Shared
- $studio-voice Rewrite this Creative Production response so it feels like a creative production session.
- Use the Moodboard Intake Widget before generation when selectable creative cues would help the user shape the board.
- Use Creative Production to run Explore > Build > Polish for a chocolate campaign.
- Shared asset libraries are part of the operating substrate: hydratable scene-library, image-ad-library, offer-library, texture references, and external brand-media assets supplied by the user or workspace.

Image generation
- Creative Production can create prompts, specs, review pages, handoffs, and generated images without plugin-side API keys.
- Full local image generation uses Codex exec fanout through `runtime/codex_exec_image_batch.py`; workers call native `image_gen.imagegen` and write status artifacts.
- Do not ask users to paste credentials into chat and do not keep direct image API fallback paths.
- Before high-volume generation, state the planned image count and review surface. Use bounded worker settings so stalled child runs are abandoned and summarized.
- See `references/codex-exec-image-generation.md`.

Architecture note
- Creative Production is intentionally asset-backed and heavier than a typical prompt-only plugin. Its active registries and prompt packs are part of the product contract because reusable visual systems matter more than lightweight surface area.
- User-facing handoffs should feel like a creative work session and generated deliverables should live in stable `outputs/` folders. See `references/experience-contract.md`.
- Static review boards should be generated from manifests through the shared Review Renderer, using named presets such as `image-wall`, `selector-board`, `positioning-board`, `moodboard`, or `detail-review`. User-facing handoffs should link natural labels such as `review board`, `mood board`, or `contact sheet` instead of exposing raw filenames. See `references/review-renderer.md` and the cross-skill contract matrix in `references/artifact-contracts.md`.
- Variation Lab is the Build-stage remix layer after review walls and asset boards. Explore chooses directions; Variation Lab turns selected or generated outputs into slot-and-lock remix batches for ads, social assets, product-placement images, pages, charts, and videos before final polish. See `references/variation-lab.md`.
- Video is user-facing as an Explore path when the user is choosing hooks, motion style, pacing, scenes, and formats. `video-explorer` also produces the provider-neutral selected-route packet for downstream production.
- Texture generation supports the asset/library substrate and declared media slots. Treat it as a reusable surface/background capability unless the user explicitly asks for a texture generation run.
- The plugin does not bundle rendered example media directly in Git. Product and offer archetypes and selected visual references hydrate through `assets/hydration/asset-bundle.json`; user-supplied or workspace-approved media should be treated as external input.
- Template-backed chart, object, white-paper, template-ingestion, template-first contract, and provider-specific video production skills are not part of this Creative Production surface.
