---
name: get-context
description: "Mandatory design-brief gate for Product Design build and design workflows. Use before ideation, prototyping, image-to-code builds, redesigns, or product UI work to clarify missing product, visual, and interactivity context or play back the supplied brief before proceeding."
---

# Get Context

Gather only the context needed for the next design action. This skill resolves or confirms the design brief; it does not implement UI or create durable design artifacts.

Run this skill at the start of Product Design requests that ask to design, build, prototype, clone, redesign, extend, or generate product UI directions.

Use question mode when any of the following are unclear:

- what product, site, feature, workflow, component, or screen is being designed
- what visual source should determine how it looks
- what concrete preferences or avoidances should shape visual exploration when no source exists
- what level of interactivity the user expects

Use playback mode when the user already provided the needed details. In playback mode, do not re-ask answered questions; play back the brief in a pithy format and name the next workflow.

Hard boundary: do not implement UI, scaffold a prototype, start a server, or create files while context is still missing.

## Critical Overrides

- Refer to the Plugin router [$index](../index/SKILL.md) before proceeding.
- Follow [$critical-overrides](../../references/critical-overrides.md).

## User Context

Before starting, load [$user-context](../user-context/SKILL.md) and run its preflight script when local shell access is available.

Use saved product URLs, Figma files, screenshots, reference images, codebase paths, Storybook, tokens, design systems, brand assets, component refs, browser preferences, and share targets as grounding material when relevant.

Do not inspect every saved reference. Inspect only what the current task needs.

## Get Context Script

The following three questions should be answered by the user. Adapt the questions based on what the user has provided so far in the conversation. If some or all fields are already known, skip the questions and summarize the design brief in your own words.

The questions to answer are:

> What do you want the thing to do?

> What existing product, design system, Figma file, screenshot, URL, image, or other visual source should it match? If none, what look are you going for? Mention existing design systems already in user-context if they exist.

> What level of interactivity should the thing have?

One of:

- Full interactivity: all controls and states are completely functional and implemented.
- Static: controls and states are minimally interactive, preferring speed.

After the questions, reply with a pithy design brief that summarizes what you're about to explore. Avoid walls of text at all costs. Be clear and concise.

Example script to follow:

```
Before I build, the Product Design workflow needs a quick design brief.

What should the login page do? Email/password only, magic link, SSO, sign-up link, forgot password?
Do you have an existing design system, app, Figma, or screenshot to match?
If not, what look are you going for?
Interactivity level: full working form states, or a faster mostly-static mock?

```

## Final message

1. Before proceeding to `$ideate`, `$prototype`, `$url-to-code`, or `$image-to-code`, confirm the design brief by explaining it back to the user in a pithy format as a `final` message.

2. Proceed only after the user confirms the design brief, unless the current thread already contains confirmation of that exact brief. If the user provides feedback, continue to refine the design brief with them.

3. After the user confirms the design brief, send one short expectation-setting note before starting an involved app, prototype, clone, redesign, or build. Example confirmation message with expectations setting:

```text
Lovely, brief locked. This kind of build usually takes about 10-15 minutes, and ambitious ones can take longer. Good moment to grab coffee or tend to something else; I'll keep moving and bring the prototype back when it is ready.
```

Do not send this note for tiny static changes, quick audits, simple research, setup-only, or share-only requests.

Done means the user has confirmed the design brief.
