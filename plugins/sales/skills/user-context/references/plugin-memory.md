# Sales Plugin Memory

Use this reference for Sales user-context writes: direct remember/save requests, broad future-facing instructions, corrections, Sales Company Research save/review gates, linked-source population, and successful-run learning.

`../SKILL.md` owns when to enter direct context mode. This reference owns how to decide what to save, when to ask a clarification, how to write the memory, and what to tell the user.

## Core Rule

Bias toward saving useful, low-risk, Sales plugin-scoped memory. Infer the category, definition, trigger criteria, usage criteria, source authority, freshness expectation, and exclusions as much as possible from the user's words and available source material.

Ask a concise clarification when the answer would make the memory materially more reliable. Be opinionated about this threshold: ask for the missing audience, workflow, source, exception, freshness rule, or trigger when it would turn a vague memory into a dependable future rule. Skip questions whose answers would merely make the saved text neater.

Whenever a memory is saved, start the user-facing recap with:

```text
Saved Sales Plugin Memory.
```

Exception: during the routine onboarding source setup step, when the user chooses a docs default, accepts source defaults, or skips data enrichment, save the source preference or skip disposition quietly and let `onboarding.md` render only the source-setup transition. Do not show the full `Saved Sales Plugin Memory.` recap or `Saved today` list for that setup housekeeping moment. Sales Company Research uses the research-complete recap in `../../sales-company-research/SKILL.md` instead of the generic saved-memory opener. The full generic recap still applies to plugin-memory introductions, workflow preference saves, explicit remember/save requests, and non-research memory saves.

The first time plugin memory is introduced during onboarding, explain what plugin memory is before saving a reusable workflow-output preference. Treat the save as the first onboarding plugin-memory concept moment whenever onboarding is active, `plugin_memory_intro.status` has not already been recorded as `shown`, `introduced`, or `completed`, and the candidate came from an accepted workflow artifact or user feedback. Earlier source preferences or setup facts can be saved in their owning setup step without teaching the plugin-memory model, and they do not count as `plugin_memory_intro`. When the user has accepted the current artifact, says it looks good, or asks to move on, that acceptance is enough to save a narrow, low-risk workflow preference by default after the intro. Ask before saving only when the candidate is broad, sensitive, ambiguous, high-risk, or likely to affect externally visible write behavior. Use this pattern for the first onboarding workflow-preference memory write:

```md
## Plugin Memory

Plugin memory is how the Sales plugin remembers approved preferences, source-of-truth links, examples, and team conventions for future Sales workflows. You can ask anytime to save things like "use this Notion page as the source of truth," "prefer inline citations," "always include attendee teams," or "answer exec-facing briefs in this style."

Saved Sales Plugin Memory.

Saved today:
- {accepted preference}
```

For later narrow, low-risk Sales-scoped memory saves, use a shorter recap and do not ask for a separate confirmation when the user already accepted the iteration or asked to move on:

```md
Saved Sales Plugin Memory.

Saved today:
- {preference 1}
- {preference 2}
```

Every save recap must name the exact preferences, resources, or source rules that were saved. Plugin memory can include both source-of-truth resources and answer/style preferences. Discovery-derived memory may be saved by default only when it is high-confidence, source-backed, durable, non-obvious, Sales-scoped, and low risk; anything ambiguous, sensitive, broad, lower-confidence, or potentially surprising must be proposed for user review before saving.

First-run state creation remains automated through `../scripts/init_user_context_state.py` when memory needs a destination. The first pure onboarding orientation should not run this initializer just to show the welcome message; `onboarding.md` owns that response-first fast path. For actual saves, the initializer copies the bundled user-context and onboarding-state templates into the user's Sales state directory. In sandboxed local-shell environments, request elevated execution on the first attempt because the initializer writes to `$CODEX_HOME/state/plugins/{marketplace_id}/{plugin_id}`. After that initialization, save Sales memory by directly editing `user-context.md` and any related operational state. Do not use a write utility for ordinary saves, correction capture, proposal saves, or approved Sales Company Research entries. Prefer one batched edit for all approved changes: read the current state once, update every touched category coherently, update `onboarding-state.json` only for changed operational bookkeeping, then validate with `../scripts/sales_preflight.py` afterward. Never run parallel writes against the same Sales state files.

If onboarding is active, a memory-save recap is only the beginning of the response. Before finalizing, apply the current step card from `onboarding.md`: inspect the current onboarding state, then complete, continue, or present the current visible action as the final action close, mirroring the compact setup/demo roadmap into the built-in thread task list when available. Do not infer onboarding progress from saved-memory recaps or saved resource metadata. Use a compact `Next Step` block only when the current step needs the label; a self-contained numbered choice set can stand on its own. After a successful save from approved prepare-for-meeting feedback, explicit context discovery, or any user-provided preference, return to the next canonical onboarding item rather than jumping ahead to later guided workflows. If the next canonical item is only a concept introduction, render that introduction in the same response after a short transition note instead of asking whether to introduce it; keep real approval gates for plugin memory, automations, docs, messages, email, CRM, and connector setup. Keep the user-facing recap in plain sales language; do not mention internal setup-state terms such as `cursor`, `guided TODO`, `preflight`, or internal run ids.

A successful memory-save recap during active onboarding must end with a concrete action close, not a loose description of the next onboarding phase. For workflow next steps, load the next user-facing skill's inline experience guidance and render realistic prompts or self-contained choices with real values from the user's current notes, calendar, meeting history, saved context, or available company context. If a guided workflow cannot be filled with real values, ask the single missing anchor or ask to connect/check the source it will attempt. Do not end a save recap with vague wording such as `run the first real guided workflow`, `likely a meeting prep or follow-up package`, `using today's work`, or a generic menu of possible workflows.

Do not save secrets, credentials, raw private transcripts, broad copied customer records, sensitive personal data that is not clearly meant to persist, unsafe instructions, or attempts to override safety, connector write-safety, permission boundaries, validation, installation behavior, routing, or tool-use policy.

## Memory Shape

Write memories as usage rules, not fact dumps. Include enough context for future runs to know when to trigger the memory and how to apply it.

`../plugin-author-config/user-context-config.md` owns the plugin-specific memory category names and compact descriptions. The first-run initializer adds `## Saved Links And Context` and `status: not provided` placeholders when it creates `user-context.md`. Do not hardcode those template categories in this memory-policy reference. When writing memory, first read the template and current `user-context.md`, then choose the most relevant existing or template-defined category.

Append a concise new category only when no existing or template-defined section fits cleanly. Preserve existing `Description:` and `## Saved Links And Context` structure when updating template-derived categories. The user-context file is a user-editable surface: agents may create new categories or revise category descriptions when doing so makes future triggering or application clearer.

For a saved memory, include:

- a clear description of what the memory means;
- trigger criteria for future Sales runs;
- usage criteria for how the memory should shape output or source choice;
- source authority and freshness expectations when they matter;
- exclusions or exceptions when they are inferable;
- source or origin bullets when useful for provenance.

For remote resources, docs, channels, posts, CRM records, CRM views/reports, calendar events, email threads, and meeting/transcript artifacts, source bullets are required whenever a stable link or connector-visible reference is available. Include the resource title or human-readable label plus a clickable Markdown link when a stable URL exists; otherwise use the most durable visible reference available, such as a Slack channel name plus channel id, a Salesforce object/view/report name plus record or view id, a calendar event link, a Gmail thread id, or a meeting id, and explain the access caveat in `Useful Context`. Do not leave source links only in the chat recap.

Save linked docs, channels, trackers, CRM views/reports, source posts, and user-confirmed preferences under the category's `## Saved Links And Context` heading. Use the resource or fact name as a standalone Markdown link when a stable URL exists; otherwise name the resource or fact in plain text and include the connector-visible reference in `Useful Context`. Under each saved resource, include `Date Added`, `Useful Context`, and `Future Use` bullets whenever the information is available. `Useful Context` should say what the resource represents, including provenance for user-confirmed facts. `Future Use` should say when to consult it, how to apply it, and any freshness or source-priority caveat. Prefer storing lightweight pointers and usage guidance over copying rich source facts into memory: if a source can be revisited, save the link/reference and a concise description of when to read it rather than a long summary. For user-provided preferences with no external link, use a named standalone fact such as `Meeting Notes Provider Preference` and put the confirmation/source note in `Useful Context`. Do not use wrapper labels such as `Saved Information`, `Saved Context`, or `User-provided context`.

Prefer a small, high-quality set of saved links or facts over comprehensive capture. Before saving or proposing context, dedupe by stable URL, canonical title, channel identity, and functional purpose. Keep the most authoritative, freshest, easiest-to-revisit, and least-obvious resource; merge useful context from weaker duplicates into that resource's `Useful Context` or `Future Use` only when it materially improves future runs. As a default target, keep one to three saved entries per category and put canonical cross-category sources in the most relevant template category instead of repeating the same link in many categories. Repeat a resource in multiple categories only when the category-specific `Future Use` is genuinely different and worth the extra surface area. Drop incidental, redundant, stale, inaccessible, obvious, or merely corroborating sources from saved context, while mentioning them in the chat recap if they helped the current discovery.

Apply a strict non-obviousness and authority bar before proposing or saving any resource. User context should preserve source shortcuts and conventions that future Sales runs would not reliably infer from normal connector reads: CRM update ownership rules, manager or RevOps conventions, approval paths, source-priority rules, hard-to-find account rooms, channel posting norms, tracker semantics, trusted examples, and stale-source warnings. Do not propose or save raw CRM object metadata, ordinary field names, picklist inventories, obvious account owner/book facts, generic search results, account channels that are easy to find by account name, or live status values that should be refreshed from the connector. Random notes, bug-bash docs, feedback threads, incidental meetings, or isolated Slack chatter do not become authoritative resources merely because they mention a workflow; use them only as discovery clues unless the source is explicitly a canonical operating doc, trusted example, tracker, owner guidance, or user-confirmed preference. When the connector can retrieve the fact directly, save only the non-obvious resource that explains how to interpret or act on that fact.

Give an explicit ranking boost to company-unique semantics: sources that explain how this company interprets or operationalizes a common sales concept differently than a generic CRM, sales methodology, or public playbook would. Save authoritative interpretation layers, not raw CRM facts. High-value examples include pipeline stage definitions and exit criteria, forecast category usage, close-date norms, new-logo versus expansion distinctions, AE/AM/CSM/SA/overlay responsibilities, approval ownership for discounting/security/legal/procurement, territory and segment rules, named-account exceptions, priority-account definitions, deal desk or launch-readiness governance, canonical CRM reports/views, and process docs that explain how to interpret CRM values. For CRM-related discovery, prefer the convention, RevOps note, manager guidance, canonical report, process page, or tracker definition that teaches future Sales runs how to interpret values over copied field metadata or live record contents.

For volatile tracker fields, live ownership, status, launch readiness, channels, SMEs, and other values likely to change, prefer saving the tracker/resource and the kinds of facts it contains instead of copying exact values into memory. If exact values are useful enough to save, mark them with an observed date and a refresh-before-use expectation.

## Company-Context Discovery

Route company-context discovery to `sales-company-research` when the user asks Sales to fill in, enrich, audit, infer, propose, or discover missing `user-context.md` setup from available company context. Typical prompts include:

- "search company context for my Sales setup"
- "fill the missing user-context template items"
- "propose the missing Sales setup entries"
- "audit what context you can infer"
- "look through available sources and suggest updates"

During onboarding, there is no separate durable-preferences questionnaire. When the user accepts an iteration and a narrow, low-risk reusable preference emerged, summarize the preference, introduce plugin memory if needed, save the preference by default, and continue the canonical onboarding flow. Broader setup context is handled by the Sales Company Research automation step. When onboarding reaches that step, Sales may kick off one immediate research run in the dedicated pinned `Sales Company Research` automation thread after the Sales automation setup is installed or repaired. If the user explicitly asks Sales to search or discover context outside that Sales automation step, route to `sales-company-research` as a separate user-requested research workflow and continue onboarding only after the save/proposal is resolved or deferred.

This reference owns the save and review gates that `sales-company-research` applies after it finds candidate resources. The research skill owns source discovery, dynamic source-family coverage, candidate ranking, coverage-note wording, output shape, and capped `Where you can help` questions. Keep the automation prompt thin by invoking `sales-company-research` instead of copying those rules into the prompt.

Discovery-derived memory may be saved by default only when it is high-confidence, source-backed, non-obvious, low-risk, and useful for future Sales workflows. Discovery authorization is not blanket save authorization: even when the user says "fill", "apply", "do it", or similar language, do not save candidates that are broad, sensitive, ambiguous, lower-confidence, unsupported by an authoritative source, or likely to surprise the user. Do not write review-only candidates to `user-context.md` until the user has seen them and explicitly says `save`, `apply`, `update`, `keep these`, or otherwise clearly approves writing those entries.

When research saves high-confidence entries or the user approves review-only entries, save all eligible or approved entries with one direct state edit whenever practical. Update `user-context.md` by replacing `status: not provided` only in touched scaffold categories, appending or merging resources under `## Saved Links And Context`, and preserving each category's `Description:` metadata. Update `onboarding-state.json` only for operational bookkeeping that changed, such as discovery status, timestamps, or pinned-thread references. Do not copy saved resource lists, saved category lists, source URLs, or save-count manifests into onboarding state; `user-context.md` is the source of truth for saved memory. After the edit, run `sales_preflight.py --workflow onboarding` or the relevant workflow preflight to confirm the saved context and onboarding state read back cleanly.

When reporting only unsaved review candidates, start with:

```text
Proposed plugin memory.
```

Then use this user-facing output shape by default:

```text
Proposed plugin memory.

I found a few useful setup entries that would make future Sales runs sharper. I have not saved these yet.

## What I Found

**{Target Category}**

{Source title}
Source: {stable URL or connector-visible reference}

Why useful: {what would change in future Sales behavior, including limits such as "do not treat this as a customer-facing escalation path" when needed}
Why this surfaced: {non-obvious route, authority signal, or why this beat more obvious alternatives}
Rank: {Top candidate | Also useful}, Confidence: {High | Medium}

## What I Need From You

1. **{Unresolved Category}**
   I did not find {specific source category or convention}.
   What would help: {specific link, channel, tracker, report, owner, or example}. This matters because {short downstream risk or value}.

Say "save these" to save only the "What I Found" entries, or reply with numbers like "2 is go/team-book" and I will fold those into the proposal.
```

For exact-save previews, anchor source links or connector-visible references inside the candidate memory entries, not only in a separate evidence list. Render the candidate entries as normal Markdown in the chat response; do not wrap the proposed memory content in fenced code blocks or inline backticks. Each candidate should look like the content that would be saved to `user-context.md`, using the target template category and preserving useful template metadata:

# {Target Category}

- Description: {what this category is or does and when future Sales runs should apply it}

## Saved Links And Context

{source title} (use a real Markdown link when a stable URL is available; otherwise use a connector-visible reference in plain text)
- Date Added: YYYY-MM-DD.
- Useful Context: {what this source represents, plus owner/location and access caveat when useful}
- Future Use: {specific saved rule, source priority, workflow hint, owner, channel, or convention inferred from it; prefer telling future runs when to reread the source over copying volatile details}

{user-provided fact or preference name, when no external source exists}
- Date Added: YYYY-MM-DD.
- Useful Context: {what the preference means and who confirmed it}
- Future Use: {when future Sales runs should apply it}

If several sources support one memory, save only the tightest set of resources needed to make the memory reliable. Usually this means one canonical resource, occasionally two or three when they cover distinct authority lanes such as workflow semantics, live status, and support routing. If the candidate includes user-provided context with no external source, add a named standalone fact or preference instead of a fake source link. After the proposed save block, add `Confidence:` and `Open question:` lines only when they help the user decide whether to save. A top-level `Source Links` section may still be included as a navigation aid, but it must not be the only place links appear. If template categories still need user-provided sources, include them as numbered `What I Need From You` asks rather than an unnumbered pointer list.

End unsaved review-candidate results with one direct approval prompt. When there are good review-only entries and no `What I Need From You` asks, use wording such as `Say "save these", or tell me which entries to edit or remove.` When `What I Need From You` asks remain, ask for the missing numbered pointers before or alongside save approval, such as `Send any of those numbered pointers, or say "save these" to keep the current proposals as-is.` Do not use `Saved Sales Plugin Memory.` until a write actually succeeds.

## Iteration Acceptance Learning

When the user iterates on any Sales artifact and then accepts it, says it looks good, asks to move on, or asks to create the next artifact from the revised version, inspect the accepted change for reusable plugin memory. This applies across Sales workflows, not just onboarding.

Reusable iteration signals include recurring output structure, tone, audience, artifact naming, section order, source priority, internal versus external messaging conventions, CRM-update rules, evidence standards, next-step style, doc/share preferences, or channel/email drafting preferences. Do not save one-off content changes, private transcript details, temporary deal facts, or corrections that only apply to the current artifact.

When the accepted preference is narrow, low-risk, and Sales plugin-scoped, summarize it back to the user, save it to plugin memory without a separate confirmation question, and say it was saved for future use. During onboarding, if plugin memory has not already been introduced, first render the `## Plugin Memory` explanation from this reference, then save the accepted narrow preference in the same response. Ask before saving only when the accepted preference is broad, sensitive, ambiguous, high-risk, or likely to affect externally visible write behavior. If the user declines a save prompt, continue the workflow without saving and do not keep asking about the same preference in that session.

When a preference or source shortcut is only a possible learning from the run, do not let the memory question replace the workflow's main next step. Use a brief save hint before the final action close, such as `_Save hint: if this format or source route should be reused, I can remember it after you confirm._` The hint should be one sentence, name the specific possible memory when helpful, and avoid asking broad setup questions. Do not show this hint when a save already happened, when the user asked for no next step, when the answer is clarification-only, or when it would distract from a sensitive or high-pressure response.

Ask only questions whose answers would materially improve the saved context. Number every question and tie it to an unresolved setup category or missing source authority. Include every unresolved template category from `../plugin-author-config/user-context-config.md` unless the user scoped discovery more narrowly; group adjacent categories only when one concrete pointer would answer the same question for all of them. If the user opts out, explicitly move forward with the current confidence level and avoid repeatedly asking the same setup question.

## Broad Instruction Capture

When the user provides a broad future-facing instruction during or immediately after a Sales interaction, identify whether it is reusable Sales user context before ending the turn.

Treat a follow-up instruction as Sales plugin-scoped when it refers to the current sales workflow, customer-facing output, source choice, process convention, internal or external messaging, evidence source, review path, audience definition, operating norm, output format, or connector use.

Common signals include `always`, `never`, `for customer`, `for security`, `for future`, `from now on`, `next time`, `before drafting`, `double check`, `use this source`, `prefer`, `don't`, and `please make sure`.

Reusable drafting preferences are especially likely to be saveable after Sales has produced a message draft: preferred signoffs, greetings, casing, tone, structure, evidence labels, subject-line style, and customer/internal audience conventions.

If the likely scope is Sales but the exact trigger, audience, or output surface is unclear, infer the narrowest reasonable scope and save unless one missing detail would materially improve future triggering or usage.

## Correction Capture

When the user corrects a Sales answer, first apply the correction in the current response. Then decide whether the correction is reusable Sales user context.

Treat a correction as saveable when it expresses a future-facing preference, convention, source priority, terminology rule, audience nuance, workflow-specific rule, messaging norm, escalation path, output format preference, or operating context.

Common signals include `actually`, `not X, Y`, `we call that`, `for us`, `next time`, `prefer`, `always`, `don't`, `that's not how we`, or repeated correction of the same pattern.

Do not save one-off factual corrections that only fix the current artifact. For ambiguous corrections, infer the narrowest reasonable scope and save unless a clarification would significantly improve triggering or usage.

Save correction-captured entries only in `user-context.md`, not `onboarding-state.json`, unless the user explicitly asks to update onboarding state too.

## Successful-Run Learning

Even when Sales successfully answers the user's request, inspect whether the workflow would have been faster, more complete, or more accurate if a durable source hint had been known earlier.

Good candidates include an authoritative channel, internal doc, document folder, system view, saved report, mapping, workspace, source-of-truth owner, search query pattern, or preferred evidence route discovered during the run.

Save successful-run learning when the source is clearly authoritative or repeatedly useful, when finding it consumed meaningful effort, when it materially improved answer confidence, or when future runs are likely to need the same route. Include when the source should be checked, what it should and should not override, and any freshness or permission caveat that matters.

Do not save transient search results, raw private records, broad customer dumps, sensitive transcript content, secrets, or sources the user did not have permission to use.

## Linked Resources

If the user provides a linked resource as a context source, or Sales Company Research finds a remote resource or doc, read it through an available connector or explicit local API before writing derived context.

Infer the memory definition, trigger criteria, usage criteria, source authority, and freshness expectation from the source material as much as possible before saving. Add the remote resource or doc link to the saved memory entry whenever a stable link is available, and write a clear description of what the source establishes and how Sales should use it.

If the resource is inaccessible, save only user-provided metadata or a user-supplied summary and say the source was not read.
