# Product Design

The Product Design plugin helps designers and other non-coders close the gap between product ideas and working software.

The Product Design plugin equips you with a set of skills to:

- Research ideas and pain points related to your product.
- Conduct product-flow audits.
- Generate distinctly new ideas for your product with ImageGen.
- Clone existing product apps into lightweight prototypes.
- Build lightweight or interactive prototypes to share with your team.

## Plugin structure

- `skills/`: Product Design skills and reference files.
- `skills/user-context/plugin-author-config/`: author-editable user-context knowledge.

## Skills

- `$index`: Routes Product Design requests to the right workflow.
- `$research`: Gathers internal conversations and context, then searches the web for additional information at the start of a project.
- `$user-context`: Saves and reads product URLs, Figma files, screenshots, reference images, codebase paths, Storybook, tokens, design systems, brand assets, preferred tools, and Product Design preferences so future work starts from the right sources.
- `$audit`: Captures screenshots of a product flow, puts them in Figma or a local folder, and reports UX, design, and accessibility findings tied to those screenshots. Use this for user-facing audits, critiques, and reviews.
- `$ideate`: Generates screenshot-style images to help designers quickly explore new ideas.
- `$prototype`: Routes Product Design prototype, redesign, clone, and UI build requests to the right workflow.
- `$get-context`: Gathers the missing product and visual context needed before ideation or prototyping can proceed.
- `$url-to-code`: Generates a 1:1 copy of a URL to kick off a prototype in a safe sandbox. No messing with production code and unnecessary scaffolding.
- `$image-to-code`: Generate interactive prototypes from your favorite or AI generated mocks.
- `$share`: Deploys a runnable prototype and returns a shareable URL.

## Helper skills

- `$design-qa`: Internal prototype QA helper that compares a coded prototype against its visual source before handoff. Use `$audit` for user-facing UX/design critiques, audits, and reviews.
