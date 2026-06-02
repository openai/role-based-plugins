---
name: ideate
description: "Generate image-based visual alternatives, remixes, or concept directions for a component, screen, feature, workflow, or product idea. Use when the user asks for design variants, visual exploration, remixes, or image-generated approaches from provided context."
---

# Ideate

You're tasked with generating design concepts for a user's idea.

Follow the shared Product Design routing guidance in [$index](../index/SKILL.md).

## Critical Overrides

Follow [critical-overrides](../../references/critical-overrides.md).

## User Context

Before starting, load [$user-context](../user-context/SKILL.md) and run its preflight script when local shell access is available.

Use saved product URLs, Figma files, screenshots, reference images, codebase paths, Storybook, tokens, design systems, brand assets, component refs, browser preferences, and share targets as grounding material when relevant.

Do not inspect every saved reference. Inspect only what the current task needs.

## Workflow

Before generating images:

1. Understand the brief.
   - Identify the target: component, screen, feature/workflow, or broad product idea.
   - Identify the intended user, product surface, and goal.
   - Preserve hard constraints from the user.
   - Run the `get-context` skill if you need more information from the user.

2. Resolve context.
   - Use provided files, screenshots, links, and visible references.
   - In a local workspace, look for nearby design documentation and other local visual context.
   - Check likely design context folders such as `storybook/`, `.storybook/`, `design-system/`, `design-systems/`, `tokens/`, `components/`, `app/`, and generated prototype roots.
   - In an existing project, look for existing product screenshots, similar flows, Storybook captures, design tokens, and component references before generating. Ask if the user can provide example screens similar to the one they are building if the existing app isn't accessible. Ensure you add design language and tokens to the Image Gen prompt.

3. Inspect references directly.
   - Look at screenshots, images, Figma frames, app surfaces, or other visual references before generating.
   - Do not infer from filenames alone.
   - If a named local path or reference is not visible, stop and ask the user to confirm the path, upload the file, start the local app, or point to the correct workspace.

4. Decide the variation mode.
   - If useful local design context exists and the user has not asked for a new style, stay within that existing direction.
   - If no useful design context exists, or the user asks for broad exploration, vary both concept and visual system.
   - For a specific component or existing surface, vary structure, interaction, hierarchy, and emphasis before varying brand style.
   - For a broad product idea, explore three meaningfully different product directions.

5. Check for access gaps.
   - If a connector, reference, or file cannot be accessed because of auth, permissions, expired login, missing scope, suspiciously empty results, or unavailable local state, stop.
   - Name the gap clearly and ask whether to troubleshoot access or continue without that source.
   - Do not generate images while silently ignoring a named reference.

6. Ask only if context is too thin.
   - Ask one targeted question only when available context is insufficient to generate useful directions.
   - Prefer asking about style direction, target audience, or the reference surface.

7. Attach images and mocks provided by the user to the Image Gen call along with your design brief.

8. Generate 3 independent options that have distinct information hierarchy, layout strategy, interaction model, or product framing.

Rules you must follow:

- Name each image clearly along with what number option it is (e.g., 1_brutalist_login_page.png).
- Use the Image Gen prompt below.
- Use the built-in Image Gen tool.
- Generate exactly three independent images unless the user overrides the count.
- Generate options in parallel when possible.
- Each option must be its own Image Gen result. Do not put multiple ideas in one image.
- Attach provided screenshots, files, app captures, Figma references, and visual source material as moodboard inspiration when available.
- Attach existing product screenshots, similar flows, Storybook captures, design tokens, and component references as grounding material when available.
- If a screenshot, image, or visual file is available, attach the actual image to the Image Gen call. Do not rely on text descriptions of it.
- Only claim a visual reference was attached if the Image Gen call actually received that image or a readable local image path.
- If you cannot attach the image, say that clearly and ask whether to continue with text-only direction.
- Preserve hard constraints from the brief in every image.
- After generating options, stop for the user's selection before any build work begins.

## Feedback Loop

If the user gives feedback after seeing options, generate revised options with that feedback.

If the user selects an option and gives feedback, do not assume build should begin. Ask one question:

> Should I build from this direction now, or generate another round with your feedback?

## Image Gen Prompt

Use this prompt attaching any attachment and your design brief to Image Gen

```text
Create realistic, production-quality UI designs with clear hierarchy, strong typography, intentional imagery, and purposeful spacing.

Keep the design simple. Avoid busy interfaces. Every section should have a clear purpose, and every element should earn its place.

Prioritize clarity, whitespace, and usability over decorative complexity.

### Layout

When deciding how to lay elements out on the page, this should be your priority order for tools to differentiate sections:

1. Use spacing, grouping, alignment, typography, and hierarchy on the same product surface.
2. Use simple dividers or row separators.
3. Use a subtle surface tint only when the base surface is not enough.
4. Use borders only when separation still is not clear.
5. Use shadows/elevation last, and sparingly.

Don'ts:
 - Do not default to a centered "app card" (the whole UI is in a card on the page) on top of a contrasting page background. Use the base page surface first unless the source product or user explicitly asks for a contained app panel.
 - Do not put cards inside cards. Do not make every major section a card. Do not make each list item its own card unless each item is truly a standalone object. A normal list should usually read as one grouped surface with lightweight row separation.
 - Do not make up extraneous features. Add only the things essential to accomplish what the prototype's goal is. Don't make up more features just to fill out a UI.

### Typography

 - Anchor UI typography to readable product sizes. Body text should usually sit between 14px and 16px, with the rest of the type scale built around that baseline.
 - Keep long-form text to a comfortable line length, generally no more than 65 characters per line.
 - Use no more than 2 fonts in a UI. You can use any font available in the project, or fonts provided free on Google Fonts. Pick the font that is best for the goal of the product and that matches with its intended look and feel.

### Presentation

 - Do not add browser or device chrome around the mockup.
 - Do not put multiple ideas into a single image generation.
 - Vary each idea as much as possible while adhering to the constraints given entirely.
```

## Output

After generation, provide

1. A short, memorable name for each concept that distills its choices down.

2. A short closing question that asks whether the user wants to keep exploring or choose one direction to continue.

If the image tool already displayed the generated images in the thread, do not embed the same images again in the final message.

If the image tool did not display the generated images, include one image per option.

Do not show the same generated image twice.

Example closing question:

> Want to explore more directions, or should I build one of these? If one works, tell me 1, 2, or 3.

Done means the requested number of independent images was generated and the user has been asked to select one.
