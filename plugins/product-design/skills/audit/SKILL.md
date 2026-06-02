---
name: audit
description: "Audit or critique a product flow, journey, workflow, funnel, onboarding path, checkout path, settings path, screen, or multi-step product experience by capturing screenshots first, placing them in Figma or a local folder, then reporting UX, design, and accessibility findings from that evidence. Use when the user asks to audit, critique, review, inspect, assess, or evaluate a product experience."
---

# Audit

Use this skill when the user wants to audit or critique a product flow, journey, funnel, onboarding path, checkout path, settings path, screen, or other product experience.

The output is not a loose opinion. The output is:

- Screenshots of the flow
- Those screenshots placed in the chosen destination
- A numbered step list
- UX and design findings tied to steps or screenshots
- Accessibility risks tied to steps or screenshots
- Clear limits on what could not be checked from screenshots alone

## Critical Overrides

- Refer to the Plugin router [$index](../index/SKILL.md) before proceeding.
- Follow [$critical-overrides](../../references/critical-overrides.md).

## User Context

Before starting, load [$user-context](../user-context/SKILL.md) and run its preflight script when local shell access is available.

Use saved product URLs, Figma files, screenshots, reference images, codebase paths, Storybook, tokens, design systems, brand assets, component refs, browser preferences, and share targets as grounding material when relevant.

Do not inspect every saved reference. Inspect only what the current task needs.

## Route

Before auditing:

1. Identify the product or surface.
2. Identify the flow or task.
3. Identify the destination.
4. Choose the capture tool.
5. Capture the flow.
6. Save, inspect, place, and annotate each screenshot.

Destination rules:

- If the user names Figma, use Figma.
- If the user names a local folder, use that folder.
- If the destination is missing, ask one question: "Should I put this in Figma or a local folder?"

Capture rules:

- Use the Codex in-app Browser first.
- If Browser cannot access, control, or screenshot the target, use Chrome [Internal].
- If Browser and Chrome cannot complete the capture, ask before using Playwright as the fallback.
- If none of those can capture valid screenshots or control the flow, stop and report the blocker.

Browser capture order:

1. Load the Browser skill before browser work.
2. Connect to the browser and use the current tab when it already shows the target.
3. Do not reload or navigate away unless the audit needs a fresh start.
4. Observe the visible state before acting.
5. Before each click, type, or key press, use the latest DOM snapshot to target one clear control.
6. After each action, take the cheapest fresh check that proves what changed: DOM for structure, screenshot for visual state.
7. Save and inspect the accepted screenshot before using it as audit evidence.

Figma rules:

- If Figma is the destination, load the required Figma skills before creating or editing the file.
- Keep a local copy of every screenshot even when Figma succeeds.
- Do not upload a screenshot to Figma until the saved local file has been inspected and accepted.
- Figma is not done until the screenshots are visibly placed in the Figma output.
- After placing screenshots in Figma, render or inspect the board and confirm every flow step has the correct screenshot visible in the correct card.
- If an image is missing, misplaced, blank, or only uploaded as an unused asset, fix it before handoff.
- If Figma tools cannot create files or place images, save the audit locally and explain the missing Figma capability.

Evidence rules:

- Use only evidence captured in the current audit run.
- Do not use memory, prior chats, old traces, cached screenshots, or prior generated artifacts as audit evidence unless the user explicitly provides them.
- Do not audit until the product, flow, destination, and capture tool are known.
- Do not claim full accessibility compliance from screenshots alone.

## Capture And Audit The Flow

You are an expert design, UX, and accessibility auditor. For each step in the flow, capture what the user sees, observe how the screen behaves, inspect the screenshot, and write audit notes before moving on.

Follow [references/design-audit-framework.md](references/design-audit-framework.md) when deciding what to inspect and how to describe strengths, UX issues, accessibility risks, limits, and recommendations.

Screenshot source rule:

- Use the screenshot you actually saw.
- Save that exact screenshot to the local audit folder.
- Open or inspect the saved file before accepting it.
- If the saved file shows the wrong window, wrong state, blank page, crop, or loading screen, reject it and capture again.
- When Figma is the destination, upload that accepted local file.
- After upload, verify the Figma board shows the same step.
- Do not replace a Browser, Chrome, or Computer Use screenshot with an OS screenshot unless you first prove the saved file shows the same window and state.

For every step:

1. Move to the next step in the requested flow.
2. Wait until the screen is loaded and visually stable.
3. Check for loading spinners, blank areas, login walls, error pages, blocked states, cookie dialogs, and half-rendered content.
4. Capture the screenshot.
5. Inspect the screenshot before accepting it.
6. Reject the screenshot if it is blank, loading, cropped, blocked, or showing the wrong state.
7. Observe behavior that matters for the audit, such as navigation, focus, loading, validation, error handling, empty states, motion, and whether the next action is clear.
8. Write notes for that step.
9. In the notes, report strengths, UX issues, accessibility risks, and any limits that made the step difficult to audit.
10. Save accepted screenshots with numbered names, such as `01-start.png`, `02-form-filled.png`, and `03-confirmation.png`.
11. Inspect the saved screenshot file before upload or handoff.
12. Add each accepted screenshot to the chosen destination immediately.
13. Add the notes for that step to the chosen destination immediately.

If the destination is a local folder:

- Save screenshots in that folder.
- Save the notes in a file that can be shared at the end.

If the destination is Figma:

- Place screenshots in order, left to right on the same row, with 200px between each one. Go to a new row every 15 screenshots, and separate those rows by 600px.
- Underneath the screenshot, add text with the Step number and its name, and notes.
- Keep a local folder copy even when Figma succeeds.
- When you are done, wrap all of the assets you added in a Section and title the section.

Acceptance checks:

- Every important step in the requested flow has a valid screenshot or a named blocker.
- Screenshots are saved in order.
- Screenshots are placed in the chosen destination as they are captured.
- Notes are placed in the chosen destination as they are written.
- Every note points to the screenshot or step it describes.
- Notes explain strengths, UX issues, accessibility risks, and evidence limits when those apply.
- Accessibility risks say what can be seen from screenshots and what still needs testing.
- The final screenshot set and notes are enough to support the requested audit.

Blockers:

- The flow cannot be completed.
- A required step cannot be screenshotted.
- The source changes in a way that makes the flow unclear.
- Screenshots cannot be saved or placed in the destination.
- Notes cannot be written or placed in the destination.
- The requested claim would require evidence that screenshots cannot provide.

## Final Response

After the flow is captured and notes are written, list every step in the final response.

The final step list MUST include:

- step number
- short description of the step
- general health of that step

Also include where the full output was saved or placed.

Keep the language direct. Do not use broad design jargon when a plain phrase works.
