# Creative Production MCP Layout

The MCP folder separates runtime ownership from browser assets:

- `server.mjs`: single Creative Production MCP server that registers all stable widget tools and resources.
- `registrations/`: Apps SDK widget registrations. These files expose tools/resources and point to browser assets.
- `widget-assets/`: browser HTML/CSS/JS only. Shared widget code, such as keyword intake, lives here.
- `previews/`: local browser previews for visual QA; these are not the source of MCP registration.
- `lib/`: shared server-side helpers.

Keep new widgets in this same split: register them in `registrations/`, put browser files in `widget-assets/`, and expose them through `server.mjs`.
