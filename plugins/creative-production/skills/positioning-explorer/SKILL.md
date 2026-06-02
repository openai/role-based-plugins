---
name: positioning-explorer
description: Explore commercially useful positioning routes before visual generation. Use when the user needs to clarify audience, occasion, growth goal, proof, or market angle before mood boards, scenes, style routes, business assets, ads, menus, cards, one-pagers, or video.
---

# Positioning Explorer

Use this skill when the user wants to decide what kind of demand a business should try to own before generating visuals.

This is an Explore-stage skill. It does not create final production assets. It turns a business brief into a small set of commercially distinct positioning routes that can feed mood boards, scene exploration, style routes, and asset production.

Read `../../references/experience-contract.md` before writing the user-facing handoff.

Read `../../references/artifact-contracts.md` before creating, repairing, or reporting artifacts.

Read `../../references/codex-exec-image-generation.md` before generating image-led route tiles.

Read `../../references/image-building-strategy.md` alongside the Codex exec contract for first-pass imagery rules.

## Role In The Journey

Use `positioning-explorer` after `explore` when the user chooses **Positioning**, or whenever the brief needs a sharper business angle before visuals.

The skill should answer:

- Who are we trying to attract?
- What occasion or buying moment are we trying to own?
- What business outcome should improve?
- What proof makes the route believable?
- What should the visuals make the audience believe?
- Which next visual path or business asset does the route unlock?

This skill should feel like a creative strategy checkpoint for business visuals, not a strategy deck, quality review, research report, or generic marketing plan.

## Intake Gate

Run a compact intake before generating routes unless the user has already provided enough information about goal, audience, occasion, proof, and constraints.

Use both chat and the widget:

- The chat asks the open questions that chips cannot capture.
- The widget captures common structured choices quickly.

Default chat frame:

```text
Before I create positioning routes, I need the hard facts and the growth bet.
Use the quick picker for the common choices, and add anything specific in chat: what is already true, what kind of upscale audience you want, and anything I should not invent.
```

Ask at most 2-3 open questions in chat:

- What is already true about the business that we should not invent?
- What kind of upscale are you aiming for: discreet, romantic, social, culinary, local, corporate, or something else?
- What do you already know you do not want?

When MCP widgets are available, render `render_moodboard_board_widget` with no images and a positioning-focused `intake` payload. Set `intake.mode` to `positioning` so the shared surface submits back to `positioning-explorer`. Keep this inside the shared inline mood-board surface.

The default widget groups are:

- "What are you trying to improve?"
- "Who are you trying to attract?"
- "What occasions should this be known for?"
- "What can we credibly build on?"
- "What should we avoid or exclude?"

Do not include a production-choice group in the intake payload. Production paths belong after routes exist.

After rendering the empty mood-board intake surface, stop and wait for the user selection or widget follow-up. Do not generate routes in the same step unless the user explicitly asks to skip intake.

When the request is already a widget follow-up such as "Continue with this qualified brief and create positioning routes," treat intake as complete.

## Route Generation

Generate 4-6 routes. Each route must combine at least three of these:

- audience;
- occasion;
- business outcome;
- believable proof;
- visual implication.

Strong route names are concrete and commercially legible:

- Client Hosting & Private Dining
- Grand Date-Night Reservation
- Wine-Led Regulars
- Premium Business Lunch
- San Francisco Sophisticates

Weak route names are abstract:

- Premium Experience
- Brand Elevation
- Creative Strategy
- Upscale Positioning

## Output Shape

The main output should be image-led positioning route tiles, not a text-heavy board.

Each route tile should include:

- one real or generated image that immediately expresses the environment, audience, and occasion;
- a short route name;
- a one-line commercial promise;
- compact chips for audience, occasion, business goal, and proof;
- a simple select/approve action.

Avoid SVG abstractions, strategy-card illustrations, palette-first visuals, or large text blocks. The user should feel the route before reading the details.

The route metadata should include:

```text
Selected positioning route:
Audience:
Occasion:
Business goal:
Value signal:
Proof needed:
Visual implications:
Assumptions:
Watch-outs:
Handoff paths:
Avoid:
```

Use a comparison table only as a secondary aid when it helps a business user decide. The table should not replace the image-led route tiles.

## Image Rules

Each route image should be one plausible environment or moment. It should not be a collage, mood board, grid, strategy diagram, or fake UI.

The image prompt must preserve source truth:

- Do not invent private rooms, lunch service, awards, press, wine programs, chef reputation, menu items, capacity, or location details.
- If a fact is unverified, label it as an assumption or ask before using it.
- Avoid fake readable text, logos, awards, or claims.
- Avoid generic luxury hotel restaurant visuals unless that is explicitly the desired route.

For restaurants, route images should show actual-feeling hospitality moments: a private table, client dinner, candlelit reservation, wine service, daylight lunch, local neighborhood arrival, or dining-room atmosphere.

## Handoff

After the user approves one or more routes, hand off to the next Explore or Build skill:

- `moodboard-explorer` for broad visual territories around the selected route.
- `scene-explorer` for restaurant, product, service, or offer-in-context images.
- `style-explorer` for reusable treatment after there is a visual anchor.
- `variation-lab`, `video-explorer`, `charts-polish`, or `generative-polish` when the user is ready for active Build, motion routing, or Polish work.

The handoff prompt must preserve the approved route:

Use the same lightweight handoff wording as the other explorers: selected direction, preserve, avoid, focused next owner, and artifact path when a route board or generated asset exists.

```text
Selected positioning route: Client Hosting & Private Dining
Audience: executives, founders, client hosts
Occasion: private dinners, board meals, team celebrations
Business goal: increase high-value bookings
Proof needed: private room, service, wine, prix fixe/event inquiry
Visual direction: discreet, polished, low-light, linen, brass, restrained type
Avoid: fake awards, discount framing, generic luxury hotel look
Next assets: private dining one-pager, LinkedIn ad, reservation card
```

## Exit Criteria

A successful positioning run ends with:

- a completed intake or explicit decision to skip intake;
- 4-6 commercially distinct route options;
- image-led route tiles or a clearly specified image-led route artifact;
- assumptions and proof needs called out;
- one or more selected routes;
- a concrete handoff into mood, scene, style, or asset production.
