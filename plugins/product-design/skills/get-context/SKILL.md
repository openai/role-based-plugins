---
name: get-context
description: "Gather enough product and visual context to proceed when no usable visual source exists. Use when the user needs help clarifying a product surface, finding references, or selecting a visual truth before ideation or prototyping."
---

# Get Context

Gather only the missing context needed for the next design action. This skill resolves uncertainty; it does not implement UI or create durable design artifacts.

Use this skill when the following is unclear:

- what product, site, feature, workflow, component, or screen is being designed
- what visual source should determine how it looks
- what concrete preferences or avoidances should shape visual exploration when no source exists

Hard boundary: do not implement UI, scaffold a prototype, start a server, or create files while context is still missing.

## Critical Overrides

- Refer to the Plugin [index] before proceeding [$index](../index/SKILL.md).
- Follow [$critical-overrides](../../references/critical-overrides.md).

## User Context

Before starting, load [$user-context](../user-context/SKILL.md) and run its preflight script when local shell access is available.

Use saved product URLs, Figma files, screenshots, reference images, codebase paths, Storybook, tokens, design systems, brand assets, component refs, browser preferences, and share targets as grounding material when relevant.

Do not inspect every saved reference. Inspect only what the current task needs.

## Get Context Script

You must ask the following set of questions:

> What do you want the thing to do?

> Do you have an existing design system you can link me to?

A design system is one or more of the following:

- Existing codebase
- Figma
- Screenshots

If, and only if, the user cannot provide a design system, ask what vibe they're going for:

> What look are you going for?

Reply to the user with a pithy design brief that summarizes what you're about to explore.

> What level of interactivity should the thing have?

One of:

- Full interactivity: all controls and states are completely functional and implemented.
- Static: controls and states are minimally interactive, preferring speed.

Example script:

```
Before I build, the Product Design workflow needs a quick design brief.

What should the login page do? Email/password only, magic link, SSO, sign-up link, forgot password?
Do you have an existing design system, app, Figma, or screenshot to match?
If not, what look are you going for?
Interactivity level: full working form states, or a faster mostly-static mock?

```

## Final message

Before you proceed to the next step, you must confirm the design brief by explaining it back to the user in a pithy format as `final` message.

Proceed only after the user confirms the design brief. If the user provides feedback, continue to refine the design brief with them.

Done means the user has confirmed the design brief.
