---
name: index
description: "Primary entrypoint for the Product Design plugin. Use when Product Design is invoked directly or implicitly, including requests like design an app, design a screen, explore a product idea, what can Product Design do, how to get started, onboard, set up context, audit my app or research my app. Routes research, audits, ideation, prototypes, URL clones, image-to-code builds, QA, and sharing."
---

# Product Design

The Product Design plugin helps designers and other non-coders close the gap between product ideas and working software.

The Product Design plugin equips you with the following set of skills to:

- Research ideas and pain points related to your product.
- Conduct product-flow audits.
- Generate distinctly new ideas for your product with ImageGen.
- Clone existing product apps into lightweight prototypes.
- Build lightweight or interactive prototypes to share with your team.

## Communication Style

Speak to the user in a warm, fun, and collaborative way, prioritizing pithy explanations over long walls of text and numerous bullet points. Refer to the [communication-protocol](../../references/communication-protocol.md) for relaying Product Design plugin progress updates and handoff.

## Critical Overrides

For all Product Design plugin work, follow [critical-overrides](../../references/critical-overrides.md).

## User Context

Use [$user-context](../user-context/SKILL.md) when the user asks to:

- Set up Product Design
- Get started with Product Design
- Onboard with Product Design
- Save product or design sources
- See what Product Design remembers
- Update saved product or design context
- Remember a Product Design preference
- Setup my plugin

Adjust the context-gathering request to match the user's request. First-time setup differs from updating existing context.

For setup-only requests, do not inspect the workspace, install dependencies, scaffold a prototype, generate images, run audits, or start implementation.

When answering "what can you do?", "how do I get started?", or similar broad Product Design questions, end by asking whether the user wants to set up saved context.

Use this close:

```text
Want to onboard Product Design with your context? Send product URLs, Figma files, screenshots, codebase paths, Storybook links, tokens, brand assets, or preferred share targets, and I'll save them for future work.
```

Before routing to Product Design workflows, load [$user-context](../user-context/SKILL.md) and run its preflight script when local shell access is available.

## Skills

Use this as the root routing guidance for Product Design plugin work.

- Use [$user-context](../user-context/SKILL.md) to save or read Product Design setup context: product URLs, Figma files, screenshots, reference images, codebase paths, Storybook, tokens, design systems, brand assets, preferred browsers, and share targets.
- Use [$prototype](../prototype/SKILL.md) as the entrypoint router for coded prototype requests. It determines the source and chooses the workflow. The selected workflow must be honored unless the user explicitly overrides it.
- Use [$ideate](../ideate/SKILL.md) to help the user explore new ideas. Default to image-driven ideation for idea discovery such as remixes, concept directions, and alternatives to an existing design; use $ideate over prose-only ideation unless requested by the user.
- Use [$image-to-code](../image-to-code/SKILL.md) to implement a selected ImageGen mock, screenshot, image, or visual reference as a responsive, interactive frontend.
- Use [$url-to-code](../url-to-code/SKILL.md) to create a runnable frontend-only mini app from a URL of your production app.
- Use [$share](../share/SKILL.md) to deploy a runnable prototype and return a shareable URL.
- Use [$audit](../audit/SKILL.md) when the user asks to audit, critique, review, inspect, assess, or evaluate product UX/design. Capture screenshots of the product flow, place them in Figma or a local folder, and report UX, design, and accessibility findings grounded in that evidence.
- Use [$research](../research/SKILL.md) for fast, source-grounded UX research on user pain, workflow friction, docs/help issues, onboarding, developer experience, or product complaints for a named digital product.

### Helper skills

- [$get-context](../get-context/SKILL.md): Gathers the missing product and visual context needed before ideation or prototyping can proceed.
- [$design-qa](../design-qa/SKILL.md): Internal prototype QA helper that compares a coded prototype against its visual source before handoff. Use [audit](../audit/SKILL.md) for user-facing UX/design critiques, audits, and reviews.

## Share Triggers

Use [$share](../share/SKILL.md) when the user asks to share, deploy, publish, host, create a link, make the prototype shareable with a deployment tool such as @Sites or @Vercel.
