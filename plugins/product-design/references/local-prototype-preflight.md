# Local Prototype Preflight

Use this before creating a new local prototype.

- Keep the work self-contained in the new project folder.
- Plugin UI icons live in `../assets/`. Do not put prototype starter code or generated app assets there.
- The bundled Product Design starter lives in `../templates/prototype/`.
- Create the app with the bootstrap script. Resolve the script path relative to this file, then run it with an absolute path:

```bash
node /absolute/path/to/plugins/product-design/scripts/bootstrap-prototype.mjs --dest /absolute/path/to/new-prototype
```

- Run `npm install` from the generated project root. The generated app includes its own `.npmrc`.
- Do not replace the starter with static HTML because package install is slow. If install is genuinely blocked, report the blocker.
- Do not start a server until the route is ready to build.
