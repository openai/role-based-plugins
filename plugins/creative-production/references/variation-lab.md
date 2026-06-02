# Creative Production Variation Lab

Variation Lab is the universal Build-stage remix layer for Creative Production outputs. It is not ad-specific. Any explorer or builder can hand off a generated output as a slot-and-lock asset that supports deliberate variations after the user has seen a review wall, asset board, selected route, or built asset.

## Core Model

Every remixable output should declare:

- `asset_type`: image ad, style route, scene, moodboard, chart, document/page, video, or generic visual.
- `source`: originating skill, route, prompt, index, and image/page path.
- `slots`: things the user can change next.
- `locks`: things that must stay stable.
- `suggested_variations`: obvious next moves to show in the UI.

Use `scripts/variation_lab.py` to generate `variation-manifest.json` and `variation-lab.html` from an existing review manifest.

## Flow Placement

- Explore chooses directions and should stay compact: positioning, mood boards, scenes, offers, styles, logos, shots, or ad families.
- Build creates reviewable outputs and uses Variation Lab when the user wants more controlled versions of already-rendered work.
- Polish happens after a variation is selected or publish-bound exactness is needed.

Use Variation Lab as the default next surface for ads, social assets, product-placement images, page concepts, charts, videos, and other generated assets when the user asks to change the character, scenery, product, style, palette, copy, crop, format, camera, props, layout, or proof/data. Do not expose it as a first-click Explore tile unless the user explicitly asks to open an existing remix lab.

## Universal Slots

- `subject`: product, object, venue, chart, page, or hero subject.
- `character`: persona, role, wardrobe, expression, pose.
- `scene`: environment, location, time of day, occasion, usage moment.
- `style`: treatment, lighting, rendering mode, material finish.
- `copy`: headline, labels, CTA, sections, narrative emphasis.
- `format`: channel, aspect ratio, crop, export size.
- `camera`: lens, shot angle, zoom, pan, detail.
- `palette`: colors, materials, texture, finish.
- `props`: supporting objects and context.
- `layout`: hierarchy, module structure, spacing, callout placement.
- `proof_data`: proof, data, citation, source-backed support.

## Asset-Type Profiles

- Ads: subject, character, scene, style, copy, format, camera, palette, props.
- Style routes: style, palette, scene, character, subject, copy, format.
- Scenes: scene, props, character, camera, style, subject, format.
- Moodboards: style, palette, scene, props, character, format.
- Charts: style, palette, layout, format, copy, with data locked.
- Documents/pages: layout, style, palette, copy, proof/data, format.
- Videos: scene, character, style, copy, format, camera, props.

Social posts and product-placement images should use `image_ad` when they are ad-like and `generic_visual` when they are broader creative assets until a more specific profile exists.

The profile should guide the UI, but the generating skill still owns final production safety. For example, a chart can change palette or layout, but chart data stays locked unless an approved data replacement is supplied.

## UX Contract

- Review walls remain inspection-first and clean.
- Variation Lab is the action-first companion surface, but inline MCP image review should use the shared mood-board widget.
- The first screen should keep the selected asset as the hero image, with the other generated options as small image-only tiles underneath.
- Do not show route names, style names, "pick this style" prompts, lock panels, or detailed updated-panel cards in the default UI. Keep those details in the manifest and handoff payload.
- Add lightweight review controls on the imagery: rejected variants should stay visible as crossed-out thumbnails, and the selected hero should expose a small reject control that marks it rejected and advances to the next viable image.
- The composer should be compact: show `Create More Variations`, a `Change` dropdown with plain slot names such as Style and Palette, recommended options for that slot, `+` controls, selected chips, and a primary `Remix` CTA.
- Slot recommendations should prioritize options that have not already been rendered in the current review set when that can be inferred from route labels.
- Multiple selections should compile into remix recipes, not independent one-off notes. Group selections by source asset, then combine selected options across different slots using a cartesian strategy. For example, two styles and two characters should produce four new image jobs. Multiple options in the same slot are alternatives; options in different slots are combined.
- Avoid per-option `Send` buttons. Users should queue one or more changes and use `Remix` once, so the next chat turn receives a single batch request.
- Cap oversized recipe expansions with a visible count rather than silently dropping selections.
- Preserve locks in the generated handoff payload, but do not render them as a visible section unless the user asks for review or audit detail.
- Pull from existing libraries when available: scenes, styles, characters, templates, approved copy, source data, and uploaded products.
- The `Remix` CTA should prepare a conversation-ready request. For file-backed runs, serve `variation-lab.html` from the generated local `server.mjs`. The page autosaves draft and ready remix choices to `variation-remix-request.json` after a short debounce, so the next Codex follow-up can read the saved choices without asking the user to copy/paste.
- Use `render_moodboard_board_widget` as the inline MCP surface for the current variation asset set.
- After remix generation, prepend the generated images to the same Variation Lab asset set and regenerate `variation-lab.html` so the user keeps compiling the board instead of being sent to a separate review wall.
- In user-facing handoffs, hyperlink this as `Variation Lab` rather than exposing the raw `variation-lab.html` filename.
