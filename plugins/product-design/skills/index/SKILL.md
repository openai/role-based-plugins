---
name: index
description: "Use to discover specific skills for the Product Design plugin, when it is at-mentioned directly, or for any mentions of potentially relevant work, including: UX research; product, screen, or flow audits; visual ideation; app or interface design, redesign, cloning, prototyping, or implementation from ideas, URLs, images, Figma, or code; design QA; and prototype sharing or deployment."
---

# Skill Purpose

Route Product Design requests to the right Product Design skill. Treat an `@Product Design` mention, direct Product Design invocation, or broad request like "design this app", "build a prototype", "audit this flow", "research this product", or "share this prototype" as intent to use this plugin.

# Plugin Purpose

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

- Follow [$critical-overrides](../../references/critical-overrides.md).

## Router Only

This index routes Product Design requests; it does not satisfy focused workflows itself.

When a request matches `$user-context`, `$get-context`, `$research`, `$ideate`, `$prototype`, `$image-to-code`, `$url-to-code`, `$audit`, `$design-qa`, or `$share`, load the focused skill and follow it.

For visual ideation requests, load `$get-context` first, then `$ideate`.

## No Visual Target, No Build

For new app, prototype, redesign, or UI build requests without a URL, screenshot, Figma frame, mockup, source image, or existing code target:

- Run `$get-context`.
- After the brief is approved, route to `$ideate`.
- Show exactly three visual options and wait for the user to choose one.
- Do not scaffold, edit files, or start a server before a visual option is selected.

`Full working version`, `no refs`, `go for it`, `make an assumption`, or a confirmed brief do not waive this.

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

## Browser Annotation Updates

Treat annotations as scoped edits to the current prototype.

Read the annotation, its target, and the surrounding screen before changing code. Preserve the existing prototype by default: layout, style, content, routes, assets, interactions, and working behavior stay the same unless the annotation asks to change them.

Do not redesign nearby UI or rebuild the prototype just because an annotation touches that area. If the annotation is ambiguous and the choice would materially change the prototype, ask first.

## Skills

Use this as the root routing guidance for Product Design plugin work. If several focused skills apply, sequence them in the order that creates the most useful design workflow. Keep this index as a router; do not perform focused workflow logic here.

### $user-context

Preflight, save, or answer from Product Design setup context. Route here before Product Design workflows to load saved product and design sources, and for direct setup, get-started, onboarding, save, remember, recall, inspect, or customization requests. This skill owns Product Design plugin-scoped context and preference policy.

### $get-context

Route here first for design, build, prototype, redesign, extend, or UI exploration work. If details are missing, ask only for the missing product, visual, or interactivity context; if details are already present, play back the brief before proceeding. Confirm the design brief back to the user before Product Design ideation or implementation.

### $research

Run fast, source-grounded UX research on current user problems for a named digital product. Route here for researching user pain, UX friction, onboarding issues, docs/help problems, developer experience friction, support pain, product workflow issues, or current user complaints.

### $audit

Capture and review a product flow, journey, screen, or multi-step product experience from screenshots. Route here for user-facing audit, critique, review, inspect, assess, or UI evaluation requests. It reports UX, design, and accessibility findings tied to captured evidence; do not use `design-qa` for user-facing audits.

### $ideate

Generate image-based visual alternatives, remixes, or concept directions for a component, screen, feature, workflow, or product idea. Route here after `get-context` has confirmed the design brief and the user needs visual exploration, design variants, alternatives to an existing design, or idea discovery before choosing a visual target. Prefer this over prose-only ideation unless the user asks for prose.

### $prototype

Route coded prototype, redesign, clone, and UI build requests to the right Product Design workflow. Route here after `get-context` has confirmed the design brief and the user asks to build from a URL, image, mockup, Figma source, existing codebase, or product idea.

### $url-to-code

Clone a live URL as a runnable frontend-only local app using Browser or Chrome source evidence. Route here after `get-context` has confirmed the brief and the user provides a production URL for a faithful local prototype or clone. It should not modify production code; use `prototype` first when source selection is still unclear.

### $image-to-code

Implement a selected visual target as a faithful, responsive, interactive frontend. Route here after `get-context` has confirmed the brief and the user has chosen an ImageGen mock, screenshot, Figma frame, mockup, reference image, or other visual source. Do not start here when no visual target has been selected; use `get-context` and `ideate` first.

### $share

Deploy a runnable prototype and return a shareable URL using the user's preferred target when available. Route here when the user asks to share, deploy, publish, host, create a link, or make a prototype shareable with `@Sites`, `@Vercel`, or another deployment tool.

### $design-qa

Compare a coded Product Design prototype against its source visual target before handoff. Route here only as an internal helper after a prototype, URL-to-code build, or image-to-code build has both a source visual and rendered implementation. Do not route broad UX critiques, audits, or product-flow reviews here; use `audit` instead.
