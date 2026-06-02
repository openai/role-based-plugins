# Image Ad Library

Hydratable reusable Creative Production image-ad packs live here.

Run `python plugins/creative-production/scripts/hydrate_assets.py --check` before reading packs. If assets are missing, hydrate from the Drive upload payload with `--source-dir`.

Image-ad packs define high-level advertising formats and visual grammars for placing a supplied product, service, venue, offer, or business asset into campaign-ready image directions. They are broader than product-context archetypes: some are UGC thumbnails, some are surreal 3D renders, some are OOH posters, some are ecommerce modules, and some are proof-led or demo-led ad systems.

Use this library when the user wants a diverse ad exploration before selecting scenes, styles, layouts, or final production polish.

Current packs:

- `packs/diverse-image-ad-archetypes.json`: 25 reusable ad families spanning UGC, surreal 3D, premium still life, demo, comparison, OOH, retail, ecommerce, proof, launch, editorial, meme-native, and immersive ad formats.

Example from the workspace root:

```bash
python3 plugins/creative-production/skills/offer-explorer/scripts/build_offer_explorer.py \
  --offer-name "<subject name>" \
  --subject-kind product \
  --offer-brief "<facts to preserve, supplied copy, audience, palette, and avoid list>" \
  --expansion-map plugins/creative-production/assets/image-ad-library/packs/diverse-image-ad-archetypes.json \
  --pack diverse-image-ad-archetypes \
  --scale family \
  --out-dir outputs/imagegen/<subject-slug>-diverse-image-ads
```

Text handling:

- Use exact supplied copy only.
- Keep generated readable text short.
- For long copy, create clear placement zones or placeholder blocks for deterministic layout later.
- Treat logos, labels, packaging text, claims, contact details, and prices as high-risk fidelity areas.
