import { readFileSync } from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

import { registerAppTool } from "@modelcontextprotocol/ext-apps/server";
import { z } from "zod";

import {
  inlineWidget,
  readText,
  registerWidgetResource,
  stableId,
} from "../../lib/widget-resource.mjs";
import { appendMoodboardRunItems, loadMoodboardRunSnapshot, loadMoodboardRunStatus } from "../../lib/moodboard-run-state.mjs";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const WIDGET_URI = resolveWidgetUri();
const MOODBOARD_APP_DIR = path.resolve(__dirname, "../../../skills/moodboard-explorer/assets/mood-board-app");
const MAX_PAGE_LIMIT = 30;
const MAX_APPEND_ITEMS = 64;
const DEFAULT_PAGE_LIMIT = MAX_PAGE_LIMIT;
const LARGE_DATA_URL_LIMIT = 160_000;

function resolveWidgetUri() {
  const manifestPath = path.resolve(__dirname, "../../../.codex-plugin/plugin.json");
  try {
    const manifest = JSON.parse(readFileSync(manifestPath, "utf8"));
    const pluginName = typeof manifest.name === "string" ? manifest.name.trim() : "";
    if (pluginName) return `ui://widget/${pluginName}/moodboard-board-20260530.html`;
  } catch {
    // Fall through to the source-plugin URI when plugin metadata is unavailable.
  }
  return "ui://widget/creative-production/moodboard-board-20260530.html";
}

const moodboardItemSchema = z
  .object({
    id: z.string().trim().optional(),
    title: z.string().trim().optional(),
    label: z.string().trim().optional(),
    caption: z.string().trim().optional(),
    tone: z.string().trim().optional(),
    family: z.string().trim().optional(),
    bestFor: z.string().trim().optional(),
    best_for: z.string().trim().optional(),
    prompt: z.string().trim().optional(),
    imageUrl: z.string().trim().optional(),
    previewImageUrl: z.string().trim().optional(),
    sourceImageUrl: z.string().trim().optional(),
    url: z.string().trim().optional(),
    path: z.string().trim().optional(),
  })
  .passthrough();

const moodboardBoardInputSchema = {
  title: z.string().trim().optional(),
  summary: z.string().trim().optional(),
  runDirectory: z.string().trim().optional(),
  streamPath: z.string().trim().optional(),
  runStatePath: z.string().trim().optional(),
  latestActionPath: z.string().trim().optional(),
  paths: z
    .object({
      runStatePath: z.string().trim().optional(),
      latestActionPath: z.string().trim().optional(),
    })
    .passthrough()
    .optional(),
  meta: z
    .object({
      title: z.string().trim().optional(),
      summary: z.string().trim().optional(),
      subtitle: z.string().trim().optional(),
    })
    .passthrough()
    .optional(),
  stream: z
    .object({
      meta: z.record(z.unknown()).optional(),
      items: z.array(moodboardItemSchema).max(60).optional(),
    })
    .passthrough()
    .optional(),
  items: z.array(moodboardItemSchema).max(60).optional(),
  routes: z.array(moodboardItemSchema).max(60).optional(),
  intake: z.record(z.unknown()).optional(),
  groups: z.array(z.record(z.unknown())).max(8).optional(),
  categories: z.array(z.record(z.unknown())).max(8).optional(),
  selected: z.array(z.string().trim()).max(32).optional(),
  defaultSelected: z.array(z.string().trim()).max(32).optional(),
  suggestedSelected: z.array(z.string().trim()).max(32).optional(),
  actionLabel: z.string().trim().optional(),
};

const moodboardBoardPageInputSchema = {
  runDirectory: z.string().trim(),
  offset: z.number().int().min(0).optional(),
  limit: z.number().int().min(1).max(MAX_PAGE_LIMIT).optional(),
  streamPath: z.string().trim().optional(),
  runStatePath: z.string().trim().optional(),
  latestActionPath: z.string().trim().optional(),
};

const appendMoodboardBoardInputSchema = {
  runDirectory: z.string().trim(),
  streamPath: z.string().trim().optional(),
  runStatePath: z.string().trim().optional(),
  latestActionPath: z.string().trim().optional(),
  sourceActionId: z.string().trim().optional(),
  idempotencyKey: z.string().trim().optional(),
  items: z.array(moodboardItemSchema).min(1).max(MAX_APPEND_ITEMS),
};

export function registerMoodboardBoardWidget(server) {
  const html = inlineWidget({
    html: moodboardAppHtml(),
    css: "",
    js: "",
    cssPlaceholder: "/* __MOODBOARD_BOARD_UNUSED_CSS__ */",
    jsPlaceholder: "/* __MOODBOARD_BOARD_UNUSED_JS__ */",
  });

  registerWidgetResource(server, {
    name: "moodboard-board-widget",
    uri: WIDGET_URI,
    title: "Moodboard board",
    description:
      "A fullscreen-capable MCP mood-board review surface for selection, preview, edit/remix prompts, and thread handoff.",
    html,
    resourceDomains: ["data:", "blob:"],
  });

  registerAppTool(
    server,
    "render_moodboard_board_widget",
    {
      title: "Render Moodboard Board Widget",
      description:
        "Render the generated mood-board review surface from mood-board images or a saved HTTP runDirectory. Use this for saved/generated mood-board run folders, Explore intake, and inline/fullscreen mood-board review.",
      inputSchema: moodboardBoardInputSchema,
      annotations: {
        readOnlyHint: true,
        destructiveHint: false,
        idempotentHint: true,
        openWorldHint: false,
      },
      _meta: {
        ui: {
          resourceUri: WIDGET_URI,
          visibility: ["model", "app"],
        },
        "openai/outputTemplate": WIDGET_URI,
        "openai/widgetAccessible": true,
        "openai/toolInvocation/invoking": "Opening moodboard board...",
        "openai/toolInvocation/invoked": "Moodboard board ready",
      },
    },
    async (input) => {
      const board = await normalizeMoodboardBoard(input);
      return {
        content: [
          {
            type: "text",
            text: `Rendered ${board.itemCount} mood-board image${board.itemCount === 1 ? "" : "s"}.`,
          },
        ],
        structuredContent: summarizeMoodboardBoard(board),
        _meta: {
          "openai/outputTemplate": WIDGET_URI,
          widgetData: board,
        },
      };
    },
  );

  registerAppTool(
    server,
    "get_moodboard_board_page",
    {
      title: "Get Moodboard Board Page",
      description:
        "App-only method for the mood-board iframe to fetch paged images and saved run state from a validated runDirectory.",
      inputSchema: moodboardBoardPageInputSchema,
      annotations: {
        readOnlyHint: true,
        destructiveHint: false,
        idempotentHint: true,
        openWorldHint: false,
      },
      _meta: {
        ui: {
          visibility: ["app"],
        },
        "openai/widgetAccessible": true,
      },
    },
    async (input) => {
      const limit = clampPageLimit(input.limit);
      const offset = Math.max(Number(input.offset) || 0, 0);
      const runSnapshot = await loadMoodboardRunSnapshot(input, {
        inlineImages: true,
        offset,
        limit,
      });
      const board = await normalizeMoodboardBoard(input, { runSnapshot, inlineImages: true });
      const page = {
        version: 1,
        widget: "moodboard-board-page",
        title: board.title,
        summary: board.summary,
        runDirectory: board.runDirectory,
        streamPath: board.streamPath,
        runStatePath: board.runStatePath,
        latestActionPath: board.latestActionPath,
        offset,
        limit,
        totalItemCount: board.itemCount,
        itemCount: board.items.length,
        latestAction: board.latestAction,
        restoredState: board.restoredState,
        items: board.items,
      };
      return {
        content: [
          {
            type: "text",
            text: `Loaded mood-board images ${offset + 1}-${offset + board.items.length} of ${board.itemCount}.`,
          },
        ],
        structuredContent: {
          version: page.version,
          widget: page.widget,
          title: page.title,
          summary: page.summary,
          offset: page.offset,
          limit: page.limit,
          itemCount: page.itemCount,
          totalItemCount: page.totalItemCount,
          runDirectory: page.runDirectory,
          hasRunState: Boolean(page.runStatePath),
          hasLatestAction: Boolean(page.latestActionPath),
        },
        _meta: {
          widgetData: page,
        },
      };
    },
  );

  registerAppTool(
    server,
    "get_moodboard_board_status",
    {
      title: "Get Moodboard Board Status",
      description:
        "App-only lightweight status method for a mounted mood-board iframe to detect saved runDirectory appends without inlining images.",
      inputSchema: moodboardBoardPageInputSchema,
      annotations: {
        readOnlyHint: true,
        destructiveHint: false,
        idempotentHint: true,
        openWorldHint: false,
      },
      _meta: {
        ui: {
          visibility: ["app"],
        },
        "openai/widgetAccessible": true,
      },
    },
    async (input) => {
      const status = await loadMoodboardRunStatus(input);
      const widgetData = {
        version: 1,
        widget: "moodboard-board-status",
        runDirectory: status?.runDirectory || "",
        streamPath: status?.streamPath || "",
        latestActionPath: status?.latestActionPath || "",
        totalItemCount: Number(status?.totalItemCount || 0),
        itemIds: status?.itemIds || [],
        streamVersion: status?.streamVersion || "",
        latestAction: compactPayload(status?.latestAction || null),
      };
      return {
        content: [
          {
            type: "text",
            text: `Mood-board status: ${widgetData.totalItemCount} item${widgetData.totalItemCount === 1 ? "" : "s"}.`,
          },
        ],
        structuredContent: {
          version: widgetData.version,
          widget: widgetData.widget,
          totalItemCount: widgetData.totalItemCount,
          streamVersion: widgetData.streamVersion,
          runDirectory: widgetData.runDirectory,
          streamPath: widgetData.streamPath,
          hasLatestAction: Boolean(widgetData.latestAction),
        },
        _meta: {
          widgetData,
        },
      };
    },
  );

  registerAppTool(
    server,
    "append_moodboard_board_items",
    {
      title: "Append Moodboard Board Items",
      description:
        "Append newly generated mood-board images to an existing saved mood-board runDirectory. Use this after remix, annotation, or generate-more actions instead of rendering a separate mood-board widget.",
      inputSchema: appendMoodboardBoardInputSchema,
      annotations: {
        readOnlyHint: false,
        destructiveHint: false,
        idempotentHint: true,
        openWorldHint: false,
      },
      _meta: {
        ui: {
          visibility: ["model"],
        },
        "openai/toolInvocation/invoking": "Appending images to moodboard...",
        "openai/toolInvocation/invoked": "Images appended to moodboard",
      },
    },
    async (input) => {
      const normalizedItems = input.items.map((item, index) => normalizeAppendItem(item, index, input));
      const appendResult = await appendMoodboardRunItems({
        ...input,
        items: normalizedItems,
      });
      return {
        content: [
          {
            type: "text",
            text: `Appended ${appendResult.appendedCount} mood-board image${appendResult.appendedCount === 1 ? "" : "s"} to the existing board.`,
          },
        ],
        structuredContent: {
          version: 1,
          widget: "moodboard-board-append",
          runDirectory: appendResult.runDirectory,
          streamPath: appendResult.streamPath,
          runStatePath: appendResult.runStatePath,
          appendedCount: appendResult.appendedCount,
          itemCount: appendResult.itemCount,
          appendedItemIds: appendResult.appendedItemIds,
          latestAction: compactPayload(appendResult.latestAction),
        },
      };
    },
  );
}

function moodboardAppHtml() {
  return readText(MOODBOARD_APP_DIR, "index.html")
    .replace('<script src="theme.js"></script>', () => scriptTag(readText(MOODBOARD_APP_DIR, "theme.js")))
    .replace('<link rel="stylesheet" href="codex-theme.css" />', () => styleTag(readText(MOODBOARD_APP_DIR, "codex-theme.css")))
    .replace('<link rel="stylesheet" href="styles.css" />', () => styleTag(readText(MOODBOARD_APP_DIR, "styles.css")))
    .replace('<script src="platform-icons.js"></script>', () => scriptTag(readText(MOODBOARD_APP_DIR, "platform-icons.js")))
    .replace('<script src="app.js"></script>', () => scriptTag(readText(MOODBOARD_APP_DIR, "app.js")));
}

function styleTag(source) {
  return `<style>\n${source}\n</style>`;
}

function scriptTag(source) {
  return `<script>\n${source.replaceAll("</script", "<\\/script").replaceAll("</SCRIPT", "<\\/SCRIPT")}\n</script>`;
}

async function normalizeMoodboardBoard(input = {}, options = {}) {
  const inlineImages = options.inlineImages === true;
  const shouldInlineRunDirectoryImages = Boolean(input.runDirectory || input.streamPath)
    && !input.items?.length
    && !input.routes?.length
    && !input.stream?.items?.length;
  const runSnapshot = options.runSnapshot || await loadMoodboardRunSnapshot(input, {
    inlineImages: shouldInlineRunDirectoryImages,
    limit: shouldInlineRunDirectoryImages ? DEFAULT_PAGE_LIMIT : Number.POSITIVE_INFINITY,
  });
  const rawItems = Array.isArray(input.items) && input.items.length
    ? input.items
    : Array.isArray(input.routes) && input.routes.length
      ? input.routes
      : Array.isArray(input.stream?.items) && input.stream.items.length
        ? input.stream.items
        : Array.isArray(runSnapshot?.items) && runSnapshot.items.length
          ? runSnapshot.items
        : [];
  const meta = input.meta || input.stream?.meta || runSnapshot?.stream?.meta || {};
  return {
    version: 1,
    widget: "moodboard-board",
    title: String(input.title || meta.title || "Moodboard board"),
    summary: String(input.summary || meta.summary || meta.subtitle || "Review, select, and hand off mood-board images inside Codex."),
    runDirectory: String(input.runDirectory || runSnapshot?.runDirectory || ""),
    streamPath: String(input.streamPath || runSnapshot?.streamPath || ""),
    runStatePath: String(input.runStatePath || input.paths?.runStatePath || runSnapshot?.runStatePath || ""),
    latestActionPath: String(input.latestActionPath || input.paths?.latestActionPath || runSnapshot?.latestActionPath || ""),
    itemCount: Number(runSnapshot?.totalItemCount || rawItems.length || 0),
    latestAction: compactPayload(runSnapshot?.latestAction || null),
    restoredState: compactPayload(runSnapshot?.runState || null),
    intake: normalizeMoodboardIntake(input),
    items: rawItems.map((item, index) => normalizeItem(item, index, {
      inlineImages: inlineImages || shouldInlineRunDirectoryImages,
    })).slice(0, 60),
  };
}

function normalizeMoodboardIntake(input = {}) {
  const intake = input.intake && typeof input.intake === "object" ? input.intake : {};
  const suggestedSelected = intake.suggestedSelected || input.suggestedSelected || intake.selected || input.selected || input.defaultSelected;
  return {
    title: String(intake.title || input.title || "Shape this mood board"),
    summary: String(intake.summary || input.summary || "Pick a few cues. I will use them as the creative brief for the first image set."),
    context: intake.context || input.context || {},
    groups: Array.isArray(intake.groups) && intake.groups.length
      ? intake.groups
      : Array.isArray(input.groups) && input.groups.length
        ? input.groups
        : Array.isArray(input.categories) && input.categories.length
          ? input.categories
          : [],
    selected: [],
    suggestedSelected: Array.isArray(suggestedSelected)
      ? suggestedSelected.map(String).slice(0, 32)
      : [],
    actionLabel: String(intake.actionLabel || input.actionLabel || "Create mood board"),
  };
}

function normalizeItem(item, index, { inlineImages = false } = {}) {
  const title = String(item.title || item.label || item.caption || `Mood image ${index + 1}`);
  return {
    id: String(item.id || stableId(title, `mood-image-${index + 1}`)),
    title,
    caption: String(item.caption || ""),
    tone: String(item.tone || item.bestFor || item.best_for || item.family || ""),
    prompt: String(item.prompt || ""),
    imageUrl: imageUrlForPayload(String(item.imageUrl || item.url || item.path || ""), { inlineImages }),
    previewImageUrl: String(item.previewImageUrl || ""),
    sourceImageUrl: String(item.sourceImageUrl || ""),
    imageError: String(item.imageError || ""),
  };
}

function normalizeAppendItem(item, index, input = {}) {
  const title = String(item.title || item.label || item.caption || `Generated mood image ${index + 1}`);
  const fallbackId = stableId(
    `${input.idempotencyKey || input.sourceActionId || "append"}-${title}-${index + 1}`,
    `generated-mood-image-${index + 1}`,
  );
  return {
    ...item,
    id: String(item.id || fallbackId),
    title,
    caption: String(item.caption || ""),
    prompt: String(item.prompt || ""),
    imageUrl: String(item.imageUrl || item.url || item.path || ""),
  };
}

function summarizeMoodboardBoard(board) {
  return {
    version: board.version,
    widget: board.widget,
    title: board.title,
    summary: board.summary,
    itemCount: board.itemCount,
    runDirectory: board.runDirectory,
    hasRunState: Boolean(board.runStatePath),
    hasLatestAction: Boolean(board.latestActionPath),
  };
}

function clampPageLimit(limit) {
  return Math.min(Math.max(Number(limit) || DEFAULT_PAGE_LIMIT, 1), MAX_PAGE_LIMIT);
}

function imageUrlForPayload(imageUrl, { inlineImages = false } = {}) {
  if (!imageUrl.startsWith("data:")) return imageUrl;
  if (inlineImages || imageUrl.length <= LARGE_DATA_URL_LIMIT) return imageUrl;
  return "";
}

function compactPayload(value) {
  if (!value || typeof value !== "object") return value || null;
  if (Array.isArray(value)) return value.map(compactPayload);
  const compacted = {};
  for (const [key, entry] of Object.entries(value)) {
    if ((key === "imageUrl" || key === "imageSrc" || key === "url") && typeof entry === "string") {
      compacted[key] = imageUrlForPayload(entry, { inlineImages: false });
    } else {
      compacted[key] = compactPayload(entry);
    }
  }
  return compacted;
}
