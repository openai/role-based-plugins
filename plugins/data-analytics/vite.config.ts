import path from "node:path";
import { fileURLToPath } from "node:url";

import { defineConfig } from "vite";
import { viteSingleFile } from "vite-plugin-singlefile";

const input = process.env.INPUT ?? "datascience-chart-widget.html";
const isArtifactWidget = input.includes("datascience-artifact-widget");
const pluginRoot = fileURLToPath(new URL(".", import.meta.url));
const reactAliases = isArtifactWidget
  ? [
      { find: /^react$/, replacement: path.join(pluginRoot, "node_modules/react/index.js") },
      {
        find: /^react\/jsx-runtime$/,
        replacement: path.join(pluginRoot, "node_modules/react/jsx-runtime.js"),
      },
      {
        find: /^react\/jsx-dev-runtime$/,
        replacement: path.join(pluginRoot, "node_modules/react/jsx-dev-runtime.js"),
      },
      { find: /^react-dom$/, replacement: path.join(pluginRoot, "node_modules/react-dom/index.js") },
      {
        find: /^react-dom\/client$/,
        replacement: path.join(pluginRoot, "node_modules/react-dom/client.js"),
      },
    ]
  : [];

export default defineConfig({
  root: "src",
  plugins: [viteSingleFile()],
  resolve: {
    alias: reactAliases,
    dedupe: ["react", "react-dom"],
    preserveSymlinks: true
  },
  build: {
    outDir: "../assets",
    emptyOutDir: false,
    minify: isArtifactWidget ? "oxc" : false,
    cssMinify: false,
    rollupOptions: {
      input
    }
  }
});
