import { readFileSync } from "node:fs";

import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";

import { registerMoodboardBoardWidget } from "./registrations/moodboard-board/register.mjs";
import { registerShotIntakeWidget } from "./registrations/shot-intake/register.mjs";
import { registerStyleIntakeWidget } from "./registrations/style-intake/register.mjs";

const pluginManifestPath = new URL("../.codex-plugin/plugin.json", import.meta.url);
const pluginManifest = JSON.parse(readFileSync(pluginManifestPath, "utf8"));

const server = new McpServer(
  {
    name: "creative-production",
    version: pluginManifest.version,
  },
  {
    instructions:
      "Expose Creative Production app widgets. Skills own workflow decisions and payload construction; this server only registers stable widget tools and resources for in-chat rendering.",
  },
);

registerMoodboardBoardWidget(server);
registerShotIntakeWidget(server);
registerStyleIntakeWidget(server);

const transport = new StdioServerTransport();
await server.connect(transport);
