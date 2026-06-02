# Public Equity Investing Invocation Policy

## Entry Gate

Activate this plugin only when at least one of these conditions is satisfied:

1. **Explicit invocation.** The user tags or names Public Equity Investing,
   uses `@public-equity-investing`, supplies its plugin link, or explicitly invokes one of its skills.
2. **Perfect-fit mandate.** The prompt unambiguously asks for investment work on a listed equity or publicly traded security from an equity-investor perspective.

When a prompt could just as reasonably be ordinary research, corporate finance, banking, private investing, or document creation, do not activate this plugin.

## Perfect-Fit Signals

The untagged prompt must tie a listed issuer, ticker, equity position, or public security directly to a public-equity workflow, such as:

- an earnings preview/deep dive, public-equity investment thesis, initiation,
  long/short pitch, catalyst calendar, or thesis tracker;
- a common-equity DCF/comps/model update, price-target debate, risk sizing,
  hedge view, or add/trim/exit decision;
- listed-equity event, ETF/index constituent, or benchmark-relative equity diligence for an investment team.

## Non-Triggers

Do not invoke Public Equity Investing automatically for generic requests to research a company, explain a share-price move, create a report or document,
build a model, value a business, summarize earnings, clean a workbook, or prepare a meeting brief unless the listed-equity investment mandate is unmistakable. A public company name by itself is not sufficient.

## After Activation

Once this gate is met, the router selects the owning workflow from user intent and focused skill descriptions. The selected lead workflow, not the router, applies `final-deliverable-framework.md` and reads `deliverable-intake-policy.md` before a new standalone reader-facing artifact begins to resolve presentation choices. Support and presentation skills inherit this activation decision rather than extending the implicit scope.
