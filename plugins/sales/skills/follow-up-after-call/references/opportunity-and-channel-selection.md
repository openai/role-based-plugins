# Opportunity And Channel Selection

## `crm` opportunity selection

Goal: choose the most relevant opportunity for the one-sentence next-steps text.

### Step 1: infer deal intent from the call

Choose one:

- `renewal`
- `expansion`
- `cross_sell`
- `pilot`
- `support`

Support the choice with 1 to 2 direct-evidence bullets.

### Step 2: gather candidates

Priority:

1. user-provided opportunity name or link
2. `crm` opportunity context or `document_store` account notes if available
3. user clarification when candidates remain unclear

### Step 3: rank candidates

Score each candidate 0 to 3 on:

- intent match
- timing match
- business priority

Choose the top candidate.

If the top two are still plausibly tied:

- present the top two with one-line rationale each
- ask the user to choose

If no credible candidate exists:

- still draft the sentence
- append `(paste into the relevant opp)`

## `internal_messaging` channel selection

User preference: `internal_messaging` channel search first, with a linked channel recommendation when a safe channel can be resolved.

Priority:

1. user-provided channel
2. channel search by account name and aliases
3. channel search by call title, launch/workstream name, product/topic keywords, and attendee team context
4. account mapping if available

Internal-only rules:

- reject channels with metadata indicating external or shared status
- reject channels whose name, topic, or purpose suggests external sharing in the selected `internal_messaging` App
- if safety is unclear, return draft text only and include a warning to verify the channel before posting

Link rules:

- Prefer the selected App's stable channel URL, channel permalink, or connector-provided web URL.
- If the App exposes a channel id and display name but no useful URL, render the channel name and say `(no useful channel link available)`.
- Never invent Slack URLs from channel ids, names, or guessed workspace paths.
- If no channel search/read path is available, suggest a best-effort internal channel description from the call evidence and mark the link as unverified.

Default behavior:

- always return a draft
- never post or send
- if a later workflow sends the recap, show it locally or in the user's test private channel before any target-channel post
