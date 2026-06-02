import { readFileSync } from "node:fs";
import { createRequire } from "node:module";
import path from "node:path";

import {
  RESOURCE_MIME_TYPE,
  registerAppResource,
} from "@modelcontextprotocol/ext-apps/server";

const require = createRequire(import.meta.url);
let cachedMcpAppsGlobalScript = "";

export function readText(...parts) {
  return readFileSync(path.join(...parts), "utf8");
}

export function inlineWidget({
  html,
  css,
  js,
  initialDisplayMode = "",
  cssPlaceholder = "/* __LOGO_REVIEW_WIDGET_CSS__ */",
  jsPlaceholder = "/* __LOGO_REVIEW_WIDGET_JS__ */",
}) {
  return injectMcpHostBridge(html
    .replace(cssPlaceholder, () => css)
    .replace(jsPlaceholder, () => js), { initialDisplayMode });
}

export function registerWidgetResource(
  server,
  {
    name,
    uri,
    title,
    description,
    html,
    prefersBorder = false,
    connectDomains = [],
    resourceDomains = [],
    frameDomains = [],
    redirectDomains = [],
    domain = "",
  },
) {
  const csp = {
    connectDomains,
    resourceDomains,
  };
  if (frameDomains.length) csp.frameDomains = frameDomains;

  const openAiCsp = {
    connect_domains: connectDomains,
    resource_domains: resourceDomains,
  };
  if (frameDomains.length) openAiCsp.frame_domains = frameDomains;
  if (redirectDomains.length) openAiCsp.redirect_domains = redirectDomains;

  const metadata = {
    ui: {
      prefersBorder,
      csp,
      ...(domain ? { domain } : {}),
    },
    "openai/widgetDescription": description,
    "openai/widgetPrefersBorder": prefersBorder,
    "openai/widgetCSP": openAiCsp,
  };

  registerAppResource(
    server,
    name,
    uri,
    {
      title,
      description,
      _meta: metadata,
    },
    async () => ({
      contents: [
        {
          uri,
          mimeType: RESOURCE_MIME_TYPE,
          text: html,
          _meta: metadata,
        },
      ],
    }),
  );
}

export function stableId(title, fallback = "creative-production-widget") {
  return String(title || fallback)
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, "-")
    .replace(/^-|-$/g, "")
    .slice(0, 80) || fallback;
}

function injectMcpHostBridge(html, { initialDisplayMode = "" } = {}) {
  const bridge = [
    '<script id="creativeProductionInitialDisplayMode">',
    `window.__CREATIVE_PRODUCTION_INITIAL_DISPLAY_MODE__=${JSON.stringify(initialDisplayMode)};`,
    "</script>",
    '<script id="creativeProductionMcpAppsBundle">',
    escapeInlineScript(mcpAppsGlobalScript()),
    "</script>",
    '<script id="creativeProductionMcpHostBridge">',
    mcpHostBridgeScript(),
    "</script>",
  ].join("\n");

  if (html.includes("</head>")) {
    return html.replace("</head>", () => `${bridge}\n</head>`);
  }
  return `${bridge}\n${html}`;
}

function mcpAppsGlobalScript() {
  if (cachedMcpAppsGlobalScript) return cachedMcpAppsGlobalScript;

  const sourcePath = require.resolve("@modelcontextprotocol/ext-apps/app-with-deps");
  const source = readFileSync(sourcePath, "utf8");
  const exportStart = source.lastIndexOf("export{");
  if (exportStart === -1) {
    throw new Error("Could not find ext-apps browser export block.");
  }

  const exportBlock = source.slice(exportStart).match(/^export\{([^}]+)\};?\s*$/s);
  if (!exportBlock) {
    throw new Error("Could not parse ext-apps browser export block.");
  }

  const exportMap = parseExportMap(exportBlock[1]);
  const requiredExports = [
    "App",
    "applyDocumentTheme",
    "applyHostFonts",
    "applyHostStyleVariables",
  ];
  for (const name of requiredExports) {
    if (!exportMap.has(name)) {
      throw new Error(`Missing ext-apps browser export: ${name}`);
    }
  }

  cachedMcpAppsGlobalScript = [
    source.slice(0, exportStart),
    ";globalThis.__CREATIVE_PRODUCTION_MCP_APPS__={",
    requiredExports
      .map((name) => `${JSON.stringify(name)}:${exportMap.get(name)}`)
      .join(","),
    "};",
  ].join("");
  return cachedMcpAppsGlobalScript;
}

function parseExportMap(body) {
  const exportMap = new Map();
  for (const rawEntry of body.split(",")) {
    const entry = rawEntry.trim();
    if (!entry) continue;
    const parts = entry.split(/\s+as\s+/);
    const local = parts[0]?.trim();
    const exported = (parts[1] || parts[0])?.trim();
    if (local && exported) exportMap.set(exported, local);
  }
  return exportMap;
}

function escapeInlineScript(source) {
  return source
    .replaceAll("</script", "<\\\\/script")
    .replaceAll("</SCRIPT", "<\\\\/SCRIPT");
}

function mcpHostBridgeScript() {
  return `(() => {
  "use strict";

  const apps = globalThis.__CREATIVE_PRODUCTION_MCP_APPS__;
  if (!apps || typeof apps.App !== "function") return;

  let mcpApp = null;

  function publishHostGlobals(globals) {
    window.openai = Object.assign(window.openai || {}, globals);
    window.dispatchEvent(new CustomEvent("openai:set_globals", {
      detail: { globals: window.openai },
    }));
  }

  function applyHostContext(context) {
    if (!context) return;
    try {
      if (context.theme && typeof apps.applyDocumentTheme === "function") {
        apps.applyDocumentTheme(context.theme);
      }
      if (context.styles?.variables && typeof apps.applyHostStyleVariables === "function") {
        apps.applyHostStyleVariables(context.styles.variables);
      }
      if (context.styles?.css?.fonts && typeof apps.applyHostFonts === "function") {
        apps.applyHostFonts(context.styles.css.fonts);
      }
    } catch (_error) {
      // Host styling is progressive enhancement; payload rendering should continue.
    }

    publishHostGlobals({
      hostContext: context,
      displayMode: context.displayMode,
      availableDisplayModes: context.availableDisplayModes,
      widgetInstanceId: context.widgetInstanceId || context.widgetId,
    });
  }

  function normalizeDisplayModeRequest(request) {
    if (typeof request === "string") return { mode: request };
    if (request && typeof request === "object") return request;
    return { mode: "inline" };
  }

  function promptFromMessage(message) {
    if (typeof message === "string") return message;
    if (message?.prompt) return String(message.prompt);
    if (typeof message?.content === "string") return message.content;
    return "";
  }

  function contentFromMessage(message, prompt) {
    if (message && Array.isArray(message.content)) return message.content;
    return [{ type: "text", text: prompt }];
  }

  function currentSize() {
    const root = document.documentElement;
    const body = document.body;
    return {
      width: Math.ceil(window.innerWidth || root.clientWidth || 0),
      height: Math.ceil(Math.max(
        root.scrollHeight || 0,
        root.offsetHeight || 0,
        body?.scrollHeight || 0,
        body?.offsetHeight || 0,
      )),
    };
  }

  function sendCurrentSize() {
    if (!mcpApp || typeof mcpApp.sendSizeChanged !== "function") return;
    try {
      mcpApp.sendSizeChanged(currentSize());
    } catch (_error) {
      // Hosts without size notifications can keep the default iframe height.
    }
  }

  function toBridgeError(error) {
    if (error instanceof Error) return error;
    return new Error(String(error || "Unable to send follow-up message."));
  }

  function withTimeout(promise, ms, label) {
    let timer;
    const timeout = new Promise((_, reject) => {
      timer = setTimeout(() => reject(new Error(label)), ms);
    });
    return Promise.race([promise, timeout]).finally(() => clearTimeout(timer));
  }

  function installCreativeProductionApi(app) {
    const api = window.creativeProductionMcp || {};
    window.creativeProductionMcp = api;

    api.sendFollowUpMessage = async (message) => {
      try {
        const prompt = promptFromMessage(message);
        if (!prompt) throw new Error("Missing follow-up prompt.");
        if (!app || typeof app.sendMessage !== "function") throw new Error("Host bridge is unavailable.");
        if (app.ready) await withTimeout(app.ready, 4000, "Host bridge did not become ready.");
        if (globalThis.__CREATIVE_PRODUCTION_MCP_HOST_ERROR__) {
          throw toBridgeError(globalThis.__CREATIVE_PRODUCTION_MCP_HOST_ERROR__);
        }
        const result = await withTimeout(app.sendMessage({
          role: "user",
          content: contentFromMessage(message, prompt),
        }), 8000, "Host did not accept the follow-up message.");
        if (result?.isError) throw new Error("Host rejected the follow-up message.");
        return result || {};
      } catch (error) {
        throw toBridgeError(error);
      }
    };

    api.updateModelContext = async (context) => {
      try {
        if (!app || typeof app.updateModelContext !== "function") throw new Error("Host bridge is unavailable.");
        if (app.ready) await withTimeout(app.ready, 4000, "Host bridge did not become ready.");
        if (globalThis.__CREATIVE_PRODUCTION_MCP_HOST_ERROR__) {
          throw toBridgeError(globalThis.__CREATIVE_PRODUCTION_MCP_HOST_ERROR__);
        }
        const result = await withTimeout(app.updateModelContext(context || {}), 8000, "Host did not accept the model context update.");
        if (result?.isError) throw new Error("Host rejected the model context update.");
        return result || {};
      } catch (error) {
        throw toBridgeError(error);
      }
    };

    api.getHostCapabilities = () => {
      if (!app || typeof app.getHostCapabilities !== "function") return {};
      return app.getHostCapabilities() || {};
    };

    api.requestDisplayMode = (request) =>
      app.requestDisplayMode(normalizeDisplayModeRequest(request));
    api.callServerTool = async (request) => {
      try {
        if (!request || typeof request !== "object") throw new Error("Missing tool request.");
        if (!request.name) throw new Error("Missing tool name.");
        if (!app || typeof app.callServerTool !== "function") throw new Error("Host bridge is unavailable.");
        if (app.ready) await withTimeout(app.ready, 4000, "Host bridge did not become ready.");
        if (globalThis.__CREATIVE_PRODUCTION_MCP_HOST_ERROR__) {
          throw toBridgeError(globalThis.__CREATIVE_PRODUCTION_MCP_HOST_ERROR__);
        }
        const result = await withTimeout(app.callServerTool({
          name: String(request.name),
          arguments: request.arguments && typeof request.arguments === "object" ? request.arguments : {},
        }), 12000, "Host did not return the server tool result.");
        if (result?.isError) throw new Error("Host returned an error from the server tool.");
        return result || {};
      } catch (error) {
        throw toBridgeError(error);
      }
    };
    api.notifyResize = sendCurrentSize;
  }

  function payloadFromToolResult(result) {
    const metadata = result && typeof result === "object" ? result._meta || {} : {};
    const payload = metadata.widgetData || result?.structuredContent || result || {};
    return { metadata, payload };
  }

  function handleToolResult(result) {
    const { metadata, payload } = payloadFromToolResult(result);
    publishHostGlobals({
      rawToolResult: result,
      toolOutput: payload,
      toolResponseMetadata: metadata,
    });
    sendCurrentSize();
  }

  window.addEventListener("message", (event) => {
    const result = event.data?.params?.result;
    if (event.data?.method === "ui/notifications/tool-result" && result) {
      handleToolResult(result);
    }
  });

  try {
    mcpApp = new apps.App(
      { name: "creative-production-widget", version: "0.1.0" },
      { availableDisplayModes: ["inline", "fullscreen"] },
      { autoResize: true },
    );
    globalThis.__CREATIVE_PRODUCTION_MCP_APP__ = mcpApp;
    installCreativeProductionApi(mcpApp);

    mcpApp.addEventListener("hostcontextchanged", applyHostContext);
    mcpApp.addEventListener("toolresult", handleToolResult);

    mcpApp.ready = mcpApp.connect()
      .then(() => {
        installCreativeProductionApi(mcpApp);
        applyHostContext(mcpApp.getHostContext && mcpApp.getHostContext());
        const initialMode = window.__CREATIVE_PRODUCTION_INITIAL_DISPLAY_MODE__;
        if (initialMode === "fullscreen" && typeof mcpApp.requestDisplayMode === "function") {
          mcpApp.requestDisplayMode({ mode: "fullscreen" }).catch(() => {});
        }
        sendCurrentSize();
      })
      .catch((error) => {
        globalThis.__CREATIVE_PRODUCTION_MCP_HOST_ERROR__ = error;
      });
  } catch (error) {
    globalThis.__CREATIVE_PRODUCTION_MCP_HOST_ERROR__ = error;
  }
})();`;
}
