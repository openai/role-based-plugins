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

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const WIDGET_URI = "ui://widget/style-intake-v2.html";

const keywordOptionSchema = z.union([
  z.string().trim().min(1),
  z
    .object({
      id: z.string().trim().optional(),
      label: z.string().trim().min(1).optional(),
      title: z.string().trim().min(1).optional(),
      value: z.string().trim().optional(),
    })
    .passthrough(),
]);

const keywordGroupSchema = z
  .object({
    id: z.string().trim().optional(),
    title: z.string().trim().min(1).optional(),
    label: z.string().trim().min(1).optional(),
    helper: z.string().trim().optional(),
    description: z.string().trim().optional(),
    options: z.array(keywordOptionSchema).max(16).optional(),
    keywords: z.array(keywordOptionSchema).max(16).optional(),
    items: z.array(keywordOptionSchema).max(16).optional(),
  })
  .passthrough();

const styleIntakeInputSchema = {
  title: z.string().trim().optional(),
  summary: z.string().trim().optional(),
  context: z
    .object({
      business: z.string().trim().optional(),
      location: z.string().trim().optional(),
      objective: z.string().trim().optional(),
      audience: z.string().trim().optional(),
    })
    .passthrough()
    .optional(),
  groups: z.array(keywordGroupSchema).max(8).optional(),
  categories: z.array(keywordGroupSchema).max(8).optional(),
  selected: z.array(z.string().trim()).max(32).optional(),
  defaultSelected: z.array(z.string().trim()).max(32).optional(),
  actionLabel: z.string().trim().optional(),
};

const styleIntakeOutputSchema = {
  version: z.literal(2),
  widget: z.literal("style-intake"),
  title: z.string(),
  summary: z.string(),
  groupCount: z.number().int().nonnegative(),
  selectedCount: z.number().int().nonnegative(),
  context: z
    .object({
      business: z.string(),
      location: z.string(),
      objective: z.string(),
      audience: z.string(),
    })
    .passthrough(),
};

export function registerStyleIntakeWidget(server) {
  const html = inlineWidget({
    html: readText(__dirname, "../../widget-assets/style-intake/widget.html"),
    css: readText(__dirname, "../../widget-assets/keyword-intake/widget.css"),
    js: readText(__dirname, "../../widget-assets/keyword-intake/widget.js"),
    cssPlaceholder: "/* __KEYWORD_INTAKE_WIDGET_CSS__ */",
    jsPlaceholder: "/* __KEYWORD_INTAKE_WIDGET_JS__ */",
  });

  registerWidgetResource(server, {
    name: "style-intake-widget",
    uri: WIDGET_URI,
    title: "Style Intake Widget",
    description:
      "Compact keyword picker for qualifying reusable Creative Production style routes before generation.",
    html,
  });

  registerAppTool(
    server,
    "render_style_intake_widget",
    {
      title: "Render Style Intake Widget",
      description:
        "Render a compact keyword picker that qualifies the taste, visual language, typography, palette, and avoids for style-route generation.",
      inputSchema: styleIntakeInputSchema,
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
        "openai/toolInvocation/invoking": "Opening style intake...",
        "openai/toolInvocation/invoked": "Style intake ready",
      },
    },
    async (input) => {
      const intake = normalizeStyleIntake(input);
      return {
        content: [
          {
            type: "text",
            text: "Rendered style intake.",
          },
        ],
        structuredContent: intake,
        _meta: {
          "openai/outputTemplate": WIDGET_URI,
        },
      };
    },
  );
}

function summarizeStyleIntake(intake) {
  return {
    version: intake.version,
    widget: intake.widget,
    title: intake.title,
    summary: intake.summary,
    groupCount: intake.groups.length,
    selectedCount: intake.selected.length,
    context: intake.context,
  };
}

function normalizeStyleIntake(input = {}) {
  return {
    version: 2,
    widget: "style-intake",
    title: String(input.title || "Style intake"),
    summary: String(input.summary || "Compact style choices before route generation."),
    context: normalizeContext(input.context || {}),
    groups: normalizeGroups(input.groups || input.categories),
    selected: normalizeStringArray(input.selected || input.defaultSelected).slice(0, 32),
    actionLabel: String(input.actionLabel || "Submit"),
  };
}

function normalizeContext(context = {}) {
  return {
    business: String(context.business || "Business"),
    location: String(context.location || ""),
    objective: String(context.objective || ""),
    audience: String(context.audience || ""),
  };
}

function normalizeGroups(groups) {
  const source = Array.isArray(groups) && groups.length ? groups : defaultGroups();
  return source
    .map((group, index) => {
      const title = String(group.title || group.label || `Group ${index + 1}`);
      return {
        id: String(group.id || stableId(`${title}-${index + 1}`, `group-${index + 1}`)),
        title,
        helper: String(group.helper || group.description || ""),
        options: normalizeOptions(group.options || group.keywords || group.items),
      };
    })
    .filter((group) => group.options.length)
    .slice(0, 8);
}

function normalizeOptions(options) {
  return (Array.isArray(options) ? options : [])
    .map((option, index) => {
      if (typeof option === "string") {
        return {
          id: stableId(option, `option-${index + 1}`),
          label: option,
          value: option,
        };
      }
      const label = String(option.label || option.title || option.value || `Option ${index + 1}`);
      return {
        id: String(option.id || stableId(`${label}-${index + 1}`, `option-${index + 1}`)),
        label,
        value: String(option.value || label),
      };
    })
    .slice(0, 16);
}

function defaultGroups() {
  return [
    {
      id: "taste",
      title: "What kind of taste should the style have?",
      options: ["Quiet luxury", "Old-world French", "Editorial modern", "Warm craft", "California fresh", "Wine-cellar dark", "Grand occasion", "Daylight refined"],
    },
    {
      id: "visual_language",
      title: "What should shape the visual language?",
      options: ["Candlelight", "Pressed linen", "Brass", "Marble", "Green banquette", "Copper heat", "Wine glassware", "Market flowers", "Oysters", "Chef hands", "Night exterior", "Daylight booth"],
    },
    {
      id: "typography",
      title: "Which typography lane feels closest?",
      options: ["Editorial serif", "High-contrast fashion serif", "Old-style book serif", "Refined humanist sans", "Condensed craft sans", "Clean modern sans"],
    },
    {
      id: "palette",
      title: "Which palette direction should we explore?",
      options: ["Burgundy cream gold", "Green cream brass", "Dark cellar amber", "Copper ivory charcoal", "Daylight cream sage", "Black gold white"],
    },
    {
      id: "avoid",
      title: "What should the style avoid?",
      options: ["Touristy French cliches", "Fake luxury", "Overly formal", "Generic stock", "Too rustic", "Too sterile", "Trendy neon", "Crowded layouts"],
    },
  ];
}

function normalizeStringArray(value) {
  if (Array.isArray(value)) return value.map(String).filter(Boolean);
  if (value) return [String(value)];
  return [];
}
