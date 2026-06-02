# Mood Board Intake

Ask only what is needed to make the board meaningfully better. Every fresh mood board run starts with this intake checkpoint, then proceeds to a reviewable HTML board after the user answers or submits the empty-board intake.

The checkpoint should feel creative and useful, not bureaucratic. Give the user the option to share visual source material, but do not make uploads mandatory.

## Qualification Standard

Before creating the board, try to understand:

- the business goal and audience;
- brand or color constraints;
- source material the board should respect;
- emotional territory and quality bar;
- must-have motifs, surfaces, or components;
- hard exclusions and brand risks;
- likely next asset types only when the user has already said the board is production-bound.

Proceed without further questioning only when the current request is already the follow-up from the board intake surface or the user has answered the chat intake. A fast first pass still uses a compact intake step; it does not skip intake entirely.

## Mood Board Qualification Scale

Choose the lightest intake level that can produce an excellent business-useful board.

| Level | Use When | Ask Before Generation | Output Expectation |
| --- | --- | --- | --- |
| 0. Rough spark | The user explicitly wants a fast first pass or ideation without friction. | One compact intake step covering theme, goal, and any available brand/reference material. | Fast exploratory board with clear assumptions. |
| 1. Creative direction | The user has a business brief but not enough taste, audience, or visual detail. | Default 4-6 question intake. | Strong exploratory board with audience, emotional territory, must-haves, and exclusions. |
| 2. Brand-anchored | The output should respect an existing brand, palette, venue, product, or campaign system. | Ask for brand guidelines, color palette, reference images, prior materials, must-use/must-avoid rules, and next output types. | Board that preserves brand signals and avoids off-brand exploration. |
| 3. Production-bound | The board will directly feed business cards, ads, menus, social posts, web visuals, packaging, or video. | Ask Level 2 plus channels, aspect ratios or asset types, approval constraints, and what must survive into Build or Polish. | Board with explicit production handoff notes and reusable visual principles. |

Default to Level 1 for business mood boards. Move to Level 2 when the user mentions brand guidelines, color palette, existing materials, a real venue/product, or a strong brand-quality concern. Move to Level 3 when the user already knows the board will become specific assets.

## Scale Component Mapping

Keep the intake scale and UI components separated clearly:

- Level 0 uses a very short chat-side prompt plus, when available, the same empty-board intake with only the most relevant chip groups.
- Level 1 is the default board intake path: question-led chips for feeling, included elements, and creative lane.
- Level 2 still uses the same board intake, but brand guidelines, reference images, menus, product photos, prior materials, colors, exclusions, and must-avoid rules are requested in chat around it.
- Level 3 still uses the same board intake, but production constraints such as channels, aspect ratios, approval needs, or next asset types are handled in chat after the exploratory direction is clearer.

Do not create a separate form-like widget for higher levels. The empty-board intake helps the user imagine visual ingredients; the chat carries business constraints, source material, and production requirements.

## Board Intake

When MCP widgets are available, use `render_moodboard_board_widget` with an empty image list and an `intake` payload for Level 1-3 intake. The mood-board app should show only compact keyword chips with selectable states plus a single action button when there are no pictures.

For a fresh request, render the empty-board intake and wait for the selection before generating the board. For an app follow-up that includes the selected cues, treat intake as complete and proceed to the HTML mood board.

Do not put brand/source-material capture, avoid/deny rules, next-asset choices, title copy, subtitle copy, source-material tiles, or freeform notes inside the intake panel. Ask those in the surrounding chat when needed. If the user has not already shared brand guidelines, reference images, menus, product photos, campaign assets, or prior designs, frame that request in chat as an optional quality boost, not a requirement.

Default chip groups should use question labels, not category labels or helper text:

- What should it make you feel?: concrete emotional routes, such as quiet prestige, date-night desire, private-club warmth, insider discovery, special-occasion trust, elegant appetite, local sophistication, old-world romance, or confident celebration.
- What elements must be included?: context-specific scene ingredients, not abstract category labels. For a restaurant, use chips such as candlelit tables, wine pours, chef hands, host greeting, banquette seating, brass and marble, fresh oysters, dessert finish, streetfront arrival, private dining, handwritten check, or pressed linens. For another business, make the chips equally specific to that product, venue, audience, service, material, or moment.
- Which creative lane feels closest?: restrained luxury, warm and inviting, editorial modern, lively social, heritage craft, minimal, theatrical, natural light.

Use neutral chips by default and a soft selected state. Avoid heavy selected chips in this intake surface.

Keep the widget lightweight. The chat should still provide the art-director framing, and the intake panel should help the user imagine exact visual concepts quickly.

## Default Intake

Use this when the user asks for a business mood board and the brief is not already specific enough:

1. If you have not already shared them, do you have brand guidelines, a color palette, menus, product photos, prior campaign assets, or 1-3 reference images I should use as anchors?
2. Who exactly are we trying to attract or persuade, and what should they feel when they see this direction?
3. Are there specific scene ingredients that must appear: objects, foods, materials, people, service moments, surfaces, local cues, or cultural references?
4. What should the board avoid: colors, clichés, competitors, visual styles, objects, moods, claims, or anything off-brand?
5. Which creative lane feels closest: restrained luxury, warm and inviting, editorial and modern, lively and social, heritage craft, or something else?

If the user sounds overwhelmed, ask only:

1. What is the theme or topic?
2. What should the board help you feel, decide, or communicate?
3. Do you have any brand colors, images, or references I should respect?

Then infer the rest from the brief and clearly state assumptions in the handoff.

## Question Bank

Use these when the project needs more depth, the brand stakes are high, or the user asks for a more rigorous creative setup.

Brand and source material:

- Do you have brand guidelines, a logo, typography rules, menu design, packaging, sales deck, website, or prior campaign assets?
- Are there colors we must use, colors we should avoid, or references that define the brand's current visual world?
- Should the board stay close to existing brand assets, or is this an intentional exploration outside the current look?

Audience and business context:

- Who is the audience by role, taste, buying moment, budget, geography, or occasion?
- What business result should this creative direction support: reservations, premium positioning, lead generation, conversion, retention, event bookings, launch awareness, or sales enablement?
- What should the audience believe after seeing this visual world?

Emotional territory and quality bar:

- What feeling should dominate: desire, trust, exclusivity, ease, energy, craft, precision, warmth, curiosity, appetite, confidence, or status?
- What would make the board feel excellent to you rather than merely attractive?
- Should the direction feel safer and more ownable, or more surprising and exploratory?

Must-have elements:

- What objects, places, materials, people, ingredients, products, rituals, or environments need to show up?
- Are there cultural, seasonal, local, or category cues that matter?
- Should the board include close-up materials, full environments, human moments, product scenes, or graphic system cues?

Exclusions:

- What would make the board feel cheap, generic, off-brand, culturally wrong, or too expected?
- Are there competitor looks, stock-photo tropes, colors, symbols, or claims to avoid?
- Are there legal, brand, or product-fidelity constraints that should shape the visuals?

Production handoff:

- Which assets should this mood board unlock next: business cards, ads, menus, social posts, pitch slides, web visuals, packaging, video, charts, one-pagers, or templates?
- Does the next stage need a reusable style system, a product/venue scene set, or a concrete asset board?

## Good Intake Tone

Use language like:

"Before I build the board, I want to tune the visual world so it has the right taste level. A few quick choices will help: any brand colors or reference images, the audience feeling we need, must-have elements, and what to avoid."

When source material would improve quality, use language like:

"If you have not already shared them, send 1-3 images, brand guidelines, a menu, or prior campaign assets. That usually gives me a much sharper read on palette, texture, and taste level."

Avoid dry wording such as:

"Please provide all required inputs."

## Context To Infer

Use local profile/context when available:

- Repository `AGENTS.md` and project instructions.
- Durable user preferences from any explicitly provided profile or local defaults.
- Recent files, documents, notes, or workspace artifacts relevant to the topic.
- The target audience, output surface, and collaboration style implied by the request.

Do not expose internal scaffolding in the final board. Translate context into visual direction.

## Creative Brief Shape

After intake, form a compact brief:

```json
{
  "theme": "",
  "goal": "",
  "audience": "",
  "brand_inputs": [],
  "palette_direction": "",
  "emotional_register": "",
  "must_include": [],
  "visual_principles": [],
  "avoid": [],
  "next_outputs": [],
  "context_signals": []
}
```

## Image Prompt Pattern

Write 16-30 prompt items. Each item should:

- Be visually inspectable without text overlays.
- Use the requested theme and inferred profile.
- Stay coherent as a set while varying setting, composition, object scale, and distance.
- Prefer real or generated bitmap imagery over abstract diagrams.
- Avoid readable text, UI labels, logos, private details, and literal personal data.
- Include a white or clean neutral background if the user asks for a light board.
- Treat each item as one self-contained visual reference image inside the larger board, never a mini mood board, collage, contact sheet, or layout.

Use IDs that are stable and descriptive because removals persist by `id`.
