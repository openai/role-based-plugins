# Test Cases

Use these cases to judge whether the workflow is aligned with the rep-focused acceptance criteria.

## Net-new trigger case

- Input: named account with a strong external trigger and a reachable executive in `crm`
- Expectation: account appears in `Work Now` with a source-grounded `Why Now`

## Expansion suppression case

- Input: customer account with product usage but an already-open opportunity
- Expectation: row is suppressed, not drafted

## Weak contact-path case

- Input: strong-fit account with no usable contact in `crm` or fallback lanes
- Expectation: row is blocked or monitored, not pushed into `Work Now`

## Mixed batch triage case

- Input: mixed set of accounts with active motion, weak timing, and one high-confidence target
- Expectation: only the executable account appears in `Work Now`

## Capacity-window case

- Input: ten good candidates, capacity window of three
- Expectation: no more than three `Work Now` rows

## HTML pane output case

- Input: any substantive ranking with `Scope`, `Work Now`, `Monitor`, `Suppress Or Block`, and `Evidence Gaps`
- Expectation: response returns a local HTML pane link first, and the pane renders the same table sections and columns as the Prioritize Accounts package

## Existing-motion protection case

- Input: account with recent external meeting and active seller follow-up
- Expectation: row is suppressed with the motion evidence called out
