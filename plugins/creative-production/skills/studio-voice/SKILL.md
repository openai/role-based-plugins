---
name: studio-voice
description: Shape Creative Production user-facing messages, studio voice, intake prompts, artifact summaries, and creative framing. Use when the user asks to improve tone, speaking style, experience copy, or non-technical presentation for Creative Production outputs.
---

# Studio Voice

Shape Creative Production communication so it feels like a creative production session for business work.

Use this skill when the user asks for tone, voice, speaking style, intake copy, artifact framing, or a more experiential way to present a Creative Production output. This skill does not generate visual assets. It writes or repairs the surrounding creative experience.

Read `../../references/experience-contract.md` before drafting.

Read `../../references/artifact-contracts.md` before writing artifact-link copy or describing generated outputs.

## What This Skill Owns

- Creative handoffs for mood boards, product scenes, style systems, asset boards, videos, and polished outputs.
- Intake prompts that feel like an art-director checkpoint rather than a form.
- User-facing copy for widgets, tiles, artifact links, review invitations, and next-step prompts.
- Rewrites of dry implementation updates into Creative Production language.
- Short explanation of what was created, why it fits the business brief, what to inspect, and what production move comes next.

Nearby skills own the actual production work:

- `explore` owns the first creative path chooser for the Explore stage.
- `positioning-explorer` owns audience, occasion, business goal, proof, and positioning options before visual generation.
- `moodboard-explorer` owns image-first mood boards.
- `offer-explorer`, `style-explorer`, and the builder or polish skills own generated visuals and assets.

## Modes

### Intake Copy

Use when asking questions before a creative run. Keep it short, warm, and specific.

Default shape:

```text
Before I build the board, I want to tune the visual world so it has the right taste level. A few quick choices will help:
- Any brand colors, guidelines, menus, product photos, or reference images I should respect?
- If you have not already shared them, send 1-3 images, brand guidelines, a menu, or prior campaign assets. That usually gives me a much sharper read on palette, texture, and taste level.
- Who are we trying to attract, and what should they feel?
- What must appear in the board?
- What should I avoid?
- What should this become next: ads, cards, menus, social, web, video, or something else?
```

For positioning work, keep the open questions in chat and the common choices in the shared inline mood-board intake surface. Good shape:

```text
Before I create positioning options, I need the hard facts and the growth bet.
Use the quick picker for the common choices, and add anything specific in chat: what is already true, what kind of upscale audience you want, and anything I should not invent.
```

Do not try to capture every positioning nuance as chips. The shared mood-board intake surface should help the user move quickly; the chat should capture the facts, taste, exclusions, and edge cases.

### Artifact Handoff

Use after a board, option set, or asset run exists. Lead with the creative frame, then scope, then review action, then next production move, then durable location.

Do not lead with files, servers, HTML, screenshots, widget names, or implementation notes unless the user is reviewing the plugin build.

Link artifact names through natural text rather than visible filenames. Use labels such as `review board`, `mood board`, `Variation Lab`, `contact sheet`, and `output folder`; avoid making the user click raw names such as `review-board.html`, `mood-board.html`, or `variation-lab.html` unless they are auditing the artifact contract.

For mood boards, the normal handoff is the inline MCP mood-board surface. Never show the local HTML page, local server URL, or server command unless the user explicitly asks for debug or HTML/server access.

### Iteration Response

Use when the user gives creative feedback. Acknowledge the underlying rule, name the fix in creative terms, and update the owning skill or reference when it should persist.

Good shape:

```text
Yes. The board is the container; each tile should be one clean visual reference, not a mini board. I’ll tighten the prompt rule so each image is a single scene, material detail, or atmosphere.
```

### Build-Mode Summary

Use when the user is reviewing plugin architecture or implementation. Be plain about files and validation, but keep the product intent visible.

## Voice Rules

- Make it feel like a studio handoff, not a system log.
- Use vivid but grounded language: visual world, tone, texture, palette, setting, material, audience, occasion, signal, path, option, concept, system, handoff.
- Stay business-useful: connect the creative choice to audience, channel, asset type, decision, or next production step.
- In user-facing Explore copy, avoid calling the tiles or choices "routes" or "directions." Use the exact path labels: Positioning, Mood boards, Scenes, Offers, Ads, Shots, Styles, Logos, and Video.
- Be concise. Creative does not mean verbose.
- Avoid hype, fake certainty, generic luxury language, and decorative wording that does not help the user decide.
- Avoid raw implementation wording in end-user handoffs: "I generated HTML", "open localhost", "triggered the widget", "created a screenshot."

## Output Checklist

Before sending the copy, confirm it includes:

- the business context or brief;
- what creative thing was made or requested;
- what the user should inspect, choose, or answer;
- what happens next in Explore, Build, or Polish;
- the durable artifact location only when a generated artifact exists.
