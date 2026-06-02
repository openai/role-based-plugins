---
name: image-to-code
description: "Implement a selected image, screenshot, mockup, or Image Gen reference as a faithful responsive frontend."
---

# Image to Code

You're tasked with translating the visual target image into a high-quality, interactive website or web app.

## Critical Overrides

Follow [critical-overrides](../../references/critical-overrides.md).

## User Context

Before starting, load [$user-context](../user-context/SKILL.md) and run its preflight script when local shell access is available.

Use saved product URLs, Figma files, screenshots, reference images, codebase paths, Storybook, tokens, design systems, brand assets, component refs, browser preferences, and share targets as grounding material when relevant.

Do not inspect every saved reference. Inspect only what the current task needs.

## Workflow

CRITICAL: THIS IS NOT GUIDANCE. THIS IS A CHECKLIST TO COMPLETE.

1. Treat the provided image as the design to recreate.

2. If the provided design is a mobile viewport, build a mobile app. If it's unclear, default to desktop.

3. Review the reference design and catalog every image asset in the design. Use the built-in Image Gen tool to create each individual asset. Examples include:

- Hero images including full bleed image backgrounds
- Featured article imagery
- Thumbnails
- Decorative illustrations
- Textures and background motifs
- Logos
- Product images
- Avatars

Rules:

- CRITICAL RULE: Do not create custom div art, CSS art, inline SVGs, handcrafted SVGs, HTML element drawings, div/span shapes, CSS drawings, gradients, emoji, or text glyphs instead of real icons and image assets ever. Use the built-in Image Gen tool for images and the closest matching icon library for icons.
- Do not use generic placeholders where the reference implies custom visual content.
- Generated assets must share the same art direction, palette, rendering style, and design language as the reference mockup.
- The built-in Image Gen tool does not support transparent images; post-process generated assets when transparency is required.

4. Define all sections of the page; for each section meticulously measure the layout and spacing between elements, and the space and sizing of the elements the themselves.

5. Find freely available fonts that match the target design.

6. Find freely available icon library that match the target design; whatever you do don't default to lucide icons. Search for the best match.

Rules:

- CRITICAL RULE: Do not create custom inline SVGs, handcrafted SVGs, HTML element drawings, div/span shapes, CSS drawings, gradients, emoji, or text glyphs. Use the built-in Image Gen tool to generate assets and use the closest matching icon library for icons.

7. Build the app starting with [local-prototype-preflight](../../references/local-prototype-preflight.md). Build all interactions, ensuring the app is complete functional and interactive: all controls and states activated and functional. For example:

- Header, sidebar, tooltip, modal interactions
- Hover and focus states
- Responsive navigation
- Clickable cards and buttons
- Animated affordances if implied by the design
- Newsletter forms, tags, filters, or navigation elements shown in the mockup
- Bring the thing to life!!! dont deliver a static site; the less you do the more the designer has to add.

Rules:

 - Place every image asset you generated into its position before proceeding. I repeat, replace all placeholders including CSS/SVG placholders before proceeding.
 - Do not leave visible controls as static chrome. Do not create new pages or routes unless the user asks for them.

8. Run the local app.

9. Capture the local app using [browser-order](../../references/browser-order.md).

10. Run [design-qa](../design-qa/SKILL.md).

   - Open the reference image and the latest prototype screenshot before writing the QA report.
   - Compare the same viewport and the same interaction state. If they do not match, capture the missing view first.
   - Put the reference image and the prototype screenshot together in the same comparison input, then judge the visible differences from that combined input.
   - Save the QA report as `design-qa.md` in the project root.
   - Fix the app, capture it again, and repeat until the QA report says `final result: passed`.
   - Do not pass because screenshots were saved, viewed separately, the DOM looks right, or interactions work. The QA report must compare the reference against the build.

11. Handoff the app or website

- Keep the prototype running locally.
- Provide the clickable local URL.
- Briefly describe the work as a designer would.
