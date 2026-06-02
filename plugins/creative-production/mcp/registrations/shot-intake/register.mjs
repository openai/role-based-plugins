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
const WIDGET_URI = "ui://widget/shot-intake-v2.html";

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

const shotIntakeInputSchema = {
  title: z.string().trim().optional(),
  summary: z.string().trim().optional(),
  context: z
    .object({
      business: z.string().trim().optional(),
      source: z.string().trim().optional(),
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

export function registerShotIntakeWidget(server) {
  const html = inlineWidget({
    html: readText(__dirname, "../../widget-assets/shot-intake/widget.html"),
    css: readText(__dirname, "../../widget-assets/keyword-intake/widget.css"),
    js: readText(__dirname, "../../widget-assets/keyword-intake/widget.js"),
    cssPlaceholder: "/* __KEYWORD_INTAKE_WIDGET_CSS__ */",
    jsPlaceholder: "/* __KEYWORD_INTAKE_WIDGET_JS__ */",
  });

  registerWidgetResource(server, {
    name: "shot-intake-widget",
    uri: WIDGET_URI,
    title: "Shot Intake Widget",
    description:
      "Compact keyword picker for selecting Creative Production shot directions before image-edit generation.",
    html,
  });

  registerAppTool(
    server,
    "render_shot_intake_widget",
    {
      title: "Render Shot Intake Widget",
      description:
        "Render a compact picker that lets the user choose camera angles, crop options, and detail shots before generating shot variants.",
      inputSchema: shotIntakeInputSchema,
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
        "openai/toolInvocation/invoking": "Opening shot intake...",
        "openai/toolInvocation/invoked": "Shot intake ready",
      },
    },
    async (input) => {
      const intake = normalizeShotIntake(input);
      return {
        content: [
          {
            type: "text",
            text: "Rendered shot intake.",
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

function normalizeShotIntake(input = {}) {
  return {
    version: 2,
    widget: "shot-intake",
    title: String(input.title || "Shot intake"),
    summary: String(input.summary || "Choose the shot directions to generate."),
    context: normalizeContext(input.context || {}),
    groups: normalizeGroups(input.groups || input.categories),
    selected: normalizeStringArray(input.selected || input.defaultSelected).slice(0, 32),
    actionLabel: String(input.actionLabel || "Submit"),
  };
}

function normalizeContext(context = {}) {
  return {
    business: String(context.business || "Business"),
    source: String(context.source || ""),
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
      id: "angles",
      title: "Which angles should we generate?",
      options: [
        { id: "overhead", label: "Overhead", value: "overhead" },
        { id: "side-profile", label: "Side profile", value: "side-profile" },
        { id: "three-quarter-front", label: "Three-quarter front", value: "three-quarter-front" },
        { id: "low-hero", label: "Low hero angle", value: "low-hero" },
        { id: "back", label: "Back view", value: "back" },
      ],
    },
    {
      id: "crops",
      title: "Which crops or pans matter?",
      options: [
        { id: "pan-left", label: "Pan left", value: "pan-left" },
        { id: "pan-right", label: "Pan right", value: "pan-right" },
        { id: "zoom-in", label: "Zoom in", value: "zoom-in" },
        { id: "wide-context", label: "Wide context", value: "wide-context" },
      ],
    },
    {
      id: "details",
      title: "Which details should we inspect?",
      options: [
        { id: "macro-detail", label: "Macro detail", value: "macro-detail" },
        { id: "material-edge", label: "Material edge", value: "material-edge" },
        { id: "surface-texture", label: "Surface texture", value: "surface-texture" },
        { id: "surprise-angle", label: "Surprise commercial angle", value: "surprise-angle" },
      ],
    },
  ];
}

function normalizeStringArray(value) {
  if (Array.isArray(value)) return value.map(String).filter(Boolean);
  if (value) return [String(value)];
  return [];
}
