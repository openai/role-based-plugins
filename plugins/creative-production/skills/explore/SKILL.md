---
name: explore
description: "Use when a broad business creative brief needs the Creative Production Explore front door: a compact chooser for Positioning, Mood boards, Scenes, Offers, Ads, Shots, Styles, Logos, Video, or active production Assets."
---

# Explore

Render the main Explore-stage decision surface for open-ended Creative Production requests.

This skill does not generate the board, assets, or final creative itself. It turns a broad business visual intent into a small set of concrete paths the user can choose from.

Read `../../references/experience-contract.md` when writing the chat handoff around Explore.

Read `../../references/artifact-contracts.md` before routing into artifact-producing paths or reporting existing artifacts.

Read `../../references/codex-exec-image-generation.md` before routing the user into any path that may generate images.

## Role In The Journey

Use this as the front door when the user has supplied a business context and wants to explore what to do next.

The visible surface is named **Explore**.

It should feel like a compact creative path chooser, not a library, review queue, dashboard, or quality-control surface.

Treat the choices as a scale of creative commitment:

- audience and positioning;
- broad visual feeling;
- product or service in context;
- offers;
- static ads;
- camera shots;
- styles;
- logos;
- video directions;
- assets.

The conversation should carry that scale in plain creative language. The mood-board empty-state surface stays compact and clickable.

## Generation Setup

Image generation uses Codex exec fanout through `../../references/codex-exec-image-generation.md`. Do not ask for credentials and do not offer legacy fallback choices. The Explore chooser should still be usable before generation; generation-heavy paths should hand off to their focused skill, which owns the worker batch and review surface.

## Required Paths

Use these candidate paths as the complete Explore vocabulary:

- **Positioning**: opens `positioning-explorer` to clarify audience, occasion, growth goal, proof, and exclusions before visual generation.
- **Mood boards**: opens `moodboard-explorer` for image-first mood, visual territories, audience feel, and creative references.
- **Scenes**: opens `scene-explorer` when the user wants to see the offer, venue, service, or product in realistic contexts. Use the scene library for point-of-sale, customer, retail, venue, consultation, demo, and handoff environments.
- **Offers**: opens `offer-explorer` when the user wants to test a product, service, venue, or experience across structured prompt families and review galleries.
- **Ads**: opens `ads-explorer` when the user wants static ad directions, paid-social concepts, campaign image routes, proof-led ads, ecommerce ads, OOH mockups, UGC thumbnails, or an image-led ad review wall.
- **Shots**: opens `shot-explorer` when the user has a visual anchor and wants alternate camera angles, crops, pans, zooms, macro details, or product-view options before polish.
- **Styles**: opens `style-explorer` after there is a selected mood board, reference image, or visual anchor.
- **Logos**: opens `logo-explorer` when the user wants brand marks, wordmarks, lockups, or identity-system concepts.
- **Video**: opens `video-explorer` when the user wants to compare video territories, story hooks, motion styles, scenes, pacing, formats, and reference-frame directions before production.
- **Assets**: opens the Build stage only when the user has enough context to produce real outputs or choose a known asset family. Prefer a strong focused skill when one applies: `ads-explorer` for ad concepts, `moodboard-explorer` for visual territories, `style-explorer` for reusable systems, `video-explorer` for motion, `logo-explorer` for identity, `variation-lab` for remix batches, `offer-explorer` for landing-page hero or web-module variation exploration, and `generative-polish` for selected fixed-size publishable image assets. Do not use Assets as a catch-all planning board when a focused skill can create the next visible result.

Do not render Variation Lab as a first-click Explore tile. It belongs after reviewable outputs exist in Build, when a selected ad, social post, product-placement image, page, chart, video, or asset board needs remixing.

## Brief Completeness Gate

Before showing Explore path cards, route boards, or creative recommendations, confirm the brief has enough campaign context: product or offer, campaign goal, audience, market or location, channels, and brand constraints. Missing fields must remain missing; do not fill them with demo values, examples, assumptions, or defaults.

For a vague request such as "I'm preparing a new marketing campaign," ask a compact intake first:

```text
What are we marketing, what outcome do you want, who is it for, what market or location matters, which channels are in scope, and what brand constraints or avoid-list should I preserve?
```

Only render the mood-board app as the Explore path chooser after those basics are known and passed as structured `intake.context`. Demo restaurant/sample context belongs only in preview and example files, never in runtime widget normalization or live handoff payloads.

## Display Rule

The mood-board empty-state intake should show up to six paths by default, ranked for the user's current request. The chat handoff can mention the broader vocabulary when it helps orient the user, but the clickable surface should stay compact.

Rank paths using the strongest signals in the brief:

- audience, occasion, proof, or growth goal: Positioning;
- visual feel, references, palette, or territory: Mood boards or Styles;
- product, service, venue, retail, demo, or realistic context: Scenes or Offers;
- campaign, paid social, ecommerce, proof, launch, or static ad: Ads;
- existing visual anchor, crop, camera, angle, macro, or alternate view: Shots;
- brand mark, wordmark, lockup, or identity system: Logos;
- motion, hook, pacing, story, reel, or format: Video;
- selected direction, remix, publish-ready output, social card, launch asset, chart polish, or ready-to-build asset: Assets.

If relevance is ambiguous, use the first six in the scale: Positioning, Mood boards, Scenes, Offers, Ads, and Shots. Preserve the hidden paths in the follow-up prompt or a "more paths" handoff when the user asks for alternatives.

When the user clicks or asks for **Assets**, treat that as intent to build unless they explicitly ask to plan. If the asset type is known, move directly to the owner that can create reviewable outputs. For landing hero, web hero, or page-module requests that ask for options, variations, or directions, use `offer-explorer` with `--pack landing-page-web-modules` at prompt scale so the visible result is a 20-variation review board. Use `generative-polish` for landing heroes, social cards, carousel slides, launch visuals, and ad crops only after a direction or deterministic base has been selected. If the asset type is unknown, ask one compact choice or show a compact chooser of strong production paths; do not create another large planning board and call it the result.

## Rendering Guidance

- Render a compact mood-board empty-state card set by default, with no more than six cards unless the user explicitly asks to see all paths.
- Use `render_moodboard_board_widget` from the Creative Production MCP server for in-chat UI rendering. Pass an empty `items` array and `intake.mode: "explore"` so the mood-board app renders the Explore chooser as its empty-state intake surface.
- Do not pass arbitrary public website image URLs directly into Explore or Asset Board `imageUrl` fields. The inline widget may run with a restrictive resource CSP, so external hosts can be blocked even when the URL is valid. Use widget-safe sources only: generated assets copied into the widget/output bundle, images proxied or served by the widget server, data/blob sources when explicitly allowed by the widget CSP, or no `imageUrl` so the widget renders palette/visual treatments without broken images. Keep public images as source context in the chat handoff or follow-up prompt until they are made widget-safe.
- For image-led business boards, especially Asset Boards, Mood boards, Scenes, Ads, Shots, Styles, Logos, and Video route boards, do not treat the palette-only fallback as the finished visual result. Palette treatments are acceptable for a quick path chooser or when generation is explicitly deferred, but the next production step should create, bundle, proxy, or otherwise serve real review images from a widget-safe source.
- Keep widgets small. If a tile does not have a real widget-safe image, remove the image well entirely instead of showing a large decorative SVG or gradient. A no-image widget tile should be text-first with compact palette chips or an icon-sized cue only. Large visual space is reserved for actual review imagery, not placeholders.
- Keep labels concrete and output-shaped. Avoid abstract names such as "creative strategy", "review library", or "business essay".
- The chat message can carry the short explanation and bullets. The widget should stay visually scannable.
- Each tile must carry a precise follow-up prompt that names the next skill or path.
- Do not show internal skill names in the tile label unless the user is explicitly reviewing plugin architecture.
- Do not create a custom mood-board board when the user clicks Mood boards; hand off to `moodboard-explorer`.
- Do not create a text-heavy positioning board when the user clicks Positioning; hand off to `positioning-explorer`, which should run the shared inline mood-board intake gate first.

## Build Handoff Contract

Once a user has selected a style system, path, or asset format and asks to continue, produce or hand off to production outputs instead of another inventory of possible assets. Generated assets must be saved under a durable output folder and paired with the shared review renderer (`../../references/review-renderer.md`) or the established universal review style for the chosen output type. Use inline widgets only as a secondary convenience after the artifact exists; they are not the deliverable.

For asset packs, the expected handoff is: exported images or files, a manifest, a review board/contact sheet, and a concise explanation of what was generated and what still requires confirmation. Do not say "created" for a widget, plan, or route list unless actual reviewable assets or a durable artifact were written. In user-facing copy, hyperlink descriptive text such as `review board`, `mood board`, or `contact sheet` instead of exposing raw artifact filenames.

## User-Facing Handoff

Open with the creative paths available for the current business brief. Do not lead with the widget name, implementation surface, HTML file, or local preview mechanics.

Good shape:

"For the restaurant campaign, we can start with Positioning, Mood boards, Scenes, Offers, Ads, Shots, Styles, Logos, Video, or Assets. Pick the tile that feels closest to where you want to begin."

If the selected path needs images, say that Creative Production will generate them with bounded Codex exec workers and write a durable review surface. Keep worker details out of the path chooser unless the user asks.

## Default Tile Copy

- Positioning: "Clarify audience and occasion."
- Mood boards: "Image-first visual territories."
- Scenes: "See the offer in real contexts."
- Offers: "Test the core offer across families."
- Ads: "Explore static ad directions."
- Shots: "Try camera angles and crops."
- Styles: "Find a reusable look."
- Logos: "Explore identity concepts."
- Video: "Shape hooks and motion routes."
- Assets: "Start production-ready assets."

## Route Prompt Contracts

Use these prompt contracts when the Explore surface hands off directly into a focused explorer. Do not change the default launcher tiles just to expose one of these routes.

- Ads: `$ads-explorer Explore static ad directions for this business visual brief, preserving the provided context and constraints.`
- Shots: `$shot-explorer Explore camera shots, crops, and visual routes for this business visual brief, preserving the provided context and constraints.`
- Video: `$video-explorer Shape hooks and motion routes for this business visual brief, preserving the provided context and constraints.`

## Default Positioning Prompt

When the user clicks the Positioning tile, preserve the business context and use a prompt shaped like:

```text
$positioning-explorer Help me shape positioning options for this business visual brief. Start with the shared inline mood-board intake gate if needed, then create image-led options that clarify audience, occasion, business goal, proof, and visual implications.
```

## Exit Criteria

Explore is successful when:

- the user sees clear, creative paths forward;
- the selected path triggers the right follow-up skill or build path;
- the current business context is preserved in the follow-up prompt;
- the first click does not skip into a fake or duplicate surface.


## Explore Intake Payload

Render Explore through the mood-board app, not a separate Explore widget. Use this shape:

```json
{
  "title": "Explore creative paths",
  "summary": "Pick where to start for this brief.",
  "items": [],
  "intake": {
    "mode": "explore",
    "title": "Explore creative paths",
    "summary": "Pick where to start for this brief.",
    "actionLabel": "Start selected path",
    "context": { "brief": "..." },
    "groups": [
      {
        "id": "paths",
        "title": "Where should we start?",
        "options": [
          { "id": "mood-boards", "label": "Mood boards", "description": "Image-first visual territories.", "prompt": "$moodboard-explorer ..." }
        ]
      }
    ]
  }
}
```

When the user selects an Explore card, the app sends the selected option prompt if present. If no prompt is provided, it sends a structured Explore continuation with the selected path labels and context.
