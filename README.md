# Role-Based Plugins

Role-based plugins make Codex easier to customize for a team's day-to-day work.
These templates package domain-specific skills, connector bindings, and starter
assets so teams can adapt Codex for roles like sales, data analytics, product
design, and financial markets. They were built with OpenAI subject matter
experts around workflows that are already helping teams move faster internally
and with alpha partners. Over the coming weeks, we'll continue expanding this
collection with more roles, workflows, and examples.

The plugins are intended to be customized before use. Connector-backed plugins
may include placeholder app and connector ids that must be replaced with ids
available to the target workspace.

## Included Plugins

| Plugin | Description | Connectors |
| --- | --- | --- |
| [Sales](./plugins/sales) | Prepare for meetings, follow up after calls, review pipeline, find account context, and build deal plans. | Salesforce, HubSpot, Slack, Google Drive, Gmail, Outlook, Outreach, Clay, ZoomInfo, and other sales tools |
| [Data Analytics](./plugins/data-analytics) | Query, visualize, explain, and validate datasets; build dashboards; and investigate metrics. | Databricks, Snowflake, BigQuery, Omni, Hex, Amplitude, Mixpanel, Statsig, Metabase, ThoughtSpot, Google Drive, Slack, Microsoft 365, and more |
| [Product Design](./plugins/product-design) | Create product specs, prototypes, UI critiques, and product design artifacts. | Sites |
| [Financial Markets](./plugins/financial-markets) | Build public-equity research, earnings analysis, valuation work, model updates, long/short pitches, risk reviews, dashboards, and investment memos. | FactSet, LSEG, Morningstar, Daloopa, Quartr, S&P, PitchBook, Slack, Google Drive, Gmail, SharePoint, Teams, and more |

## Repository Layout

```text
.
|-- .agents/plugins/marketplace.json
`-- plugins/
    |-- sales/
    |-- data-analytics/
    |-- product-design/
    `-- financial-markets/
```

Each plugin generally follows this structure:

```text
plugins/plugin-name/
|-- .codex-plugin/plugin.json   # Plugin manifest and display metadata
|-- .app.json                   # App and connector bindings, when needed
|-- .mcp.json                   # MCP server configuration, when needed
|-- skills/                     # Workflow instructions and domain context
|-- assets/                     # Icons, templates, and examples
`-- README.md                   # Plugin-specific notes, when present
```

## Configure Connectors

Connector-backed plugins declare app bindings in `.app.json`. Some bindings use
placeholder ids:

```json
{
  "apps": {
    "salesforce": {
      "id": "REPLACE_WITH_SALESFORCE_APP_OR_CONNECTOR_ID"
    }
  }
}
```

Before installing a connector-backed plugin, replace each placeholder with a
matching app or connector id available to your workspace.

| Placeholder | Replace with |
| --- | --- |
| `REPLACE_WITH_SALESFORCE_APP_OR_CONNECTOR_ID` | Salesforce or Agentforce Sales |
| `REPLACE_WITH_SITES_APP_OR_CONNECTOR_ID` | Sites |

Canonical shared platform connector ids and existing `templated_apps_*` template
registry ids are portable bindings and should be left unchanged. Do not copy
other app or connector ids from another workspace unless their availability
across workspaces is documented.

If a plugin lists an optional app that your workspace does not use, remove that
app binding before installing the plugin.

## Development

Most plugin content is markdown and JSON. Some plugins include JavaScript or
Python helper code for MCP servers, widgets, validation, or asset generation.

Plugins with Node.js dependencies require `npm ci` before local MCP-backed
development:

```sh
cd plugins/data-analytics && npm ci
```

Financial Markets is packaged as `financial-markets`, but some skill names and
bundled support playbook paths still use `public-equity-investing`.

## Contributing

Fork the repository, make focused changes, and open a pull request.

## License

This repository is licensed under the MIT License. See [LICENSE](./LICENSE).
