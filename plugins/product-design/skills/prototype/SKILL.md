---
name: prototype
description: "Route coded prototype requests after Product Design get-context has confirmed the design brief. Use for building prototypes from URLs, images, mockups, Figma, existing code, or ideas that need visual exploration before build."
---

# Design Prototypes

You're tasked with creating a frontend-only, interactive website or app, that the user can click through and use.

Select the best workflow from the following options to solve the user's request

## Golden Rule of Prototyping

- Do not build until you have a visual target and the chosen workflow reaches `$image-to-code` or `$url-to-code`.
- A visual target is an app or website design to build from: a user-provided image, a source URL, or an ImageGen design selected by the user.
- A `$get-context` brief is not a visual target.
- After `$get-context`, route to `$ideate` unless the user already provided a concrete visual source.
- If `$ideate` creates options, stop and wait for the user to choose one.
- The chosen option becomes the required visual target for `$image-to-code`.

## Critical Overrides

- Refer to the Plugin router [$index](../index/SKILL.md) before proceeding.
- Follow [$critical-overrides](../../references/critical-overrides.md).
- Refer to [references/existing-codebase-edits.md](references/existing-codebase-edits.md) for best practices on making edits to existing codebases.

## User Context

Before starting, load [$user-context](../user-context/SKILL.md) and run its preflight script when local shell access is available.

Use saved product URLs, Figma files, screenshots, reference images, codebase paths, Storybook, tokens, design systems, brand assets, component refs, browser preferences, and share targets as grounding material when relevant.

Do not inspect every saved reference. Inspect only what the current task needs.

## Setup Is Not Prototype Work

If the user only asks to set up Product Design, do not continue in this skill. Use [$user-context](../user-context/SKILL.md).

## Workflows

The following workflows support cloning, redesigning, extending, and building products from scratch. Choose the workflow that best matches the user's request, or use the skills as helpers if the request does not match one workflow cleanly.

Always start with `$get-context` to confirm the design brief before proceeding to the next workflow step. If required details are missing, `$get-context` asks for them. If the user already supplied the product, visual, and interactivity details, `$get-context` plays back the brief in your own words. Do not proceed to `$ideate`, `$url-to-code`, or `$image-to-code` until the brief has been played back and either confirmed by the user or already confirmed earlier in the thread.

### Clone product

"Recreate {URL}"

Required next steps:

- `$get-context` - confirm the design brief, including the target URL, purpose, source constraints, and interactivity level.
- `$url-to-code` - recreate the app or website shown at the URL.

"Recreate {image}"

Required next steps:

- `$get-context` - confirm the design brief, including what the image represents, source constraints, and interactivity level.
- `$image-to-code` - recreate the app or website design shown in the image.

### New product

"Build me {idea}"

Required next steps:

- `$get-context` - confirm the design brief, including the product idea, user goal, visual direction, source constraints, and interactivity level.
- `$ideate` - generate exactly three app or website design options; show them and wait for selection.
- `$image-to-code` - only after the user selects an option.

### Redesign product

"Redesign this {image}"

Required next steps:

- `$get-context` - confirm the design brief, including the redesign goal, visual direction, source constraints, and interactivity level.
- `$ideate` - attach the provided app or website design to ImageGen; generate exactly three redesign options; show them and wait for selection.
- `$image-to-code` - only after the user selects an option.

"Redesign this {URL}"

Required next steps:

- `$get-context` - confirm the design brief, including the target URL, redesign goal, source constraints, and interactivity level.
- `$ideate` - attach provided app or website screenshot at the URL to ImageGen; generate exactly three redesign options; show them and wait for selection.
- `$image-to-code` - only after the user selects an option; use the URL as reference for existing content, structure, and interactions.

"Redesign my app"

Required next steps:

- `$get-context` - confirm the design brief, including the app surface, redesign goal, source constraints, and interactivity level.
- Find the app or website in the codebase.
- If there is more than one possible target, ask the user which one to redesign and whether they want to edit it directly or create a fresh prototype.
- `$ideate` - use the existing app or website as the source; generate exactly three redesign options; show them and wait for selection.
- `$image-to-code` - only after the user selects an option; refer to [references/existing-codebase-edits.md](references/existing-codebase-edits.md)

### Extend product

"Add {feature} to this {URL}"

Required next steps:

- `$get-context` - confirm the design brief, including the target URL, feature behavior, source constraints, and interactivity level.
- `$url-to-code` - recreate the app or website and add the requested feature.

"Add {feature} to my app"

Required next steps:

- `$get-context` - confirm the design brief, including the app surface, feature behavior, source constraints, and interactivity level.
- Find the app or website in the codebase.
- If there is more than one possible target, ask the user which one to extend.
- Implement the requested feature in the existing app or website; refer to [references/existing-codebase-edits.md](references/existing-codebase-edits.md)

When the user references a product name without a source URL or image, use the browser skill of choice to get actual screenshots of the product. Only fallback to web search images if the product isn't accessible.

## Hard Rules

- Written design direction is not a visual target. Use it as input to `$ideate` and ImageGen.
- Do not build from a brief alone.
- For redesigns, use `$ideate` to generate exactly three design options, show them, and wait for the user to choose one.
- Do not build a redesign until the user has chosen a design option.
- When a new product has no visual target after `$get-context`, use `$ideate` to generate exactly three design options, show them, and wait for the user to choose one.
- If the user gives feedback, or says they like more than one design, use `$ideate` to create a new ImageGen mock with the feedback or combined direction before build.
- Pass the user's written direction and attached design references into `$ideate` and ImageGen.
- If the current folder looks like an existing prototype and it is unclear whether to edit it or create a new one, ask the user.
