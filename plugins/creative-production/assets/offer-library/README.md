# Creative Production Offer Library

Hydratable JSON-first reusable offer and product-advertising archetypes for Creative Production workflows.

Run `python plugins/creative-production/scripts/hydrate_assets.py --check` before reading packs. If assets are missing, hydrate from the Drive upload payload with `--source-dir`.

Use `registry-index.json` to discover active packs. Packs live under `packs/` and should describe reusable archetypes, prompts, placeholders, constraints, and default instantiations without bundling rendered example media.

Rendered examples belong in `outputs/`, team docs, or an external approved media source rather than the launch plugin package.
