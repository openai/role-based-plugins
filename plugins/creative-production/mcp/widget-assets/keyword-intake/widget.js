(function () {
  "use strict";

  window.__KEYWORD_INTAKE_WIDGET_LOADED__ = true;

  const DEFAULTS = {
    moodboard: {
      targetSkill: "$moodboard-explorer",
      submitLead: "Continue with this qualified moodboard intake and create the board.",
      completionInstruction:
        "Use these selections as creative constraints. Each moodboard tile should be one single visual reference image, not a mini mood board.",
      sentStatus: "Creative brief sent.",
      readyStatus: "Creative brief ready.",
      groups: [
        {
          id: "feeling",
          title: "What should it make you feel?",
          options: ["Quiet prestige", "Date-night desire", "Insider discovery", "Private-club warmth", "Special-occasion trust", "Elegant appetite", "Local sophistication", "Old-world romance", "Confident celebration"],
        },
        {
          id: "include",
          title: "What elements must be included?",
          options: ["Candlelit tables", "Wine pours", "Chef hands", "Host greeting", "Banquette seating", "Brass and marble", "Fresh oysters", "Dessert finish", "Streetfront arrival", "Private dining", "Handwritten check", "Pressed linens"],
        },
        {
          id: "lane",
          title: "Which creative lane feels closest?",
          options: ["Restrained luxury", "Warm and inviting", "Editorial modern", "Lively social", "Heritage craft", "Minimal", "Theatrical", "Natural light"],
        },
      ],
    },
    style: {
      targetSkill: "$style-explorer",
      submitLead: "Continue with this qualified style intake and create reusable style routes.",
      completionInstruction:
        "Use these selections to create compact style-route tiles with real/generated imagery, route-specific typography, square palette swatches, and immersive style subtitles. Do not include asset types yet.",
      sentStatus: "Style brief sent.",
      readyStatus: "Style brief ready.",
      groups: [
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
      ],
    },
    shot: {
      targetSkill: "$shot-explorer",
      submitLead: "Continue with this qualified shot intake and create the selected shots.",
      completionInstruction:
        "Use these selections to generate only the selected camera angles, crops, and detail shots from the supplied source image. Render the results in the shared Creative Production review gallery.",
      sentStatus: "Shot brief sent.",
      readyStatus: "Shot brief ready.",
      groups: [
        {
          id: "angles",
          title: "Which angles should we generate?",
          options: ["Overhead", "Side profile", "Three-quarter front", "Low hero angle", "Back view"],
        },
        {
          id: "crops",
          title: "Which crops or pans matter?",
          options: ["Pan left", "Pan right", "Zoom in", "Wide context"],
        },
        {
          id: "details",
          title: "Which details should we inspect?",
          options: ["Macro detail", "Material edge", "Surface texture", "Surprise commercial angle"],
        },
      ],
    },
  };

  const app = document.getElementById("app");
  let state = hydrate(readToolOutput());
  window.addEventListener("openai:set_globals", () => {
    state = hydrate(readToolOutput());
    render();
  });

  function readToolOutput() {
    const openai = window.openai || {};
    const metadata = openai.toolResponseMetadata || {};
    return metadata.widgetData || normalizeToolPayload(openai.toolOutput) || {};
  }

  function normalizeToolPayload(payload) {
    if (!payload || typeof payload !== "object") return payload;
    if (payload._meta?.widgetData) return payload._meta.widgetData;
    if (payload.structuredContent && (payload.content || payload._meta || payload.isError !== undefined)) {
      return payload.structuredContent;
    }
    return payload;
  }

  function hydrate(output) {
    const kind = normalizeKind(output.intakeKind || output.kind || output.widget || app?.dataset.intakeKind);
    const defaults = DEFAULTS[kind] || DEFAULTS.moodboard;
    return {
      kind,
      context: normalizeContext(output.context || {}),
      groups: normalizeGroups(output.groups || output.categories || defaults.groups),
      selected: new Set(normalizeStringArray(output.selected || output.defaultSelected)),
      actionLabel: String(output.actionLabel || "Submit"),
      targetSkill: String(output.targetSkill || defaults.targetSkill || ""),
      submitLead: String(output.submitLead || output.submitPrompt || defaults.submitLead),
      completionInstruction: String(output.completionInstruction || output.finalInstruction || defaults.completionInstruction),
      sentStatus: String(output.sentStatus || defaults.sentStatus),
      readyStatus: String(output.readyStatus || defaults.readyStatus),
      status: "",
      fallbackPrompt: "",
    };
  }

  function normalizeKind(value) {
    const normalized = String(value || "moodboard")
      .toLowerCase()
      .replace(/-intake$/, "")
      .replace(/_/g, "-");
    if (normalized.includes("position")) return "positioning";
    if (normalized.includes("style")) return "style";
    if (normalized.includes("shot")) return "shot";
    return "moodboard";
  }

  function normalizeContext(context) {
    return {
      business: String(context.business || "Business"),
      location: String(context.location || ""),
      objective: String(context.objective || ""),
      audience: String(context.audience || ""),
    };
  }

  function normalizeGroups(groups) {
    return (Array.isArray(groups) ? groups : [])
      .map((group, groupIndex) => {
        const title = String(group.title || group.label || `Group ${groupIndex + 1}`);
        return {
          id: String(group.id || slug(title) || `group-${groupIndex + 1}`),
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
      .map((option, optionIndex) => {
        if (typeof option === "string") {
          return {
            id: slug(option) || `option-${optionIndex + 1}`,
            label: option,
            value: option,
          };
        }
        const label = String(option.label || option.title || option.value || `Option ${optionIndex + 1}`);
        return {
          id: String(option.id || slug(label) || `option-${optionIndex + 1}`),
          label,
          value: String(option.value || label),
        };
      })
      .slice(0, 16);
  }

  function render() {
    app.classList.add("keyword-intake");
    app.innerHTML = [
      '<section class="section-grid" aria-label="' + attr(readableKind(state.kind)) + ' qualification keywords">',
      state.groups.map(renderGroup).join(""),
      '</section>',
      '<section class="footer">',
      '<div class="actions">',
      '<button class="secondary-action" type="button" id="clearButton">Clear</button>',
      '<button class="action" type="button" id="submitButton">' + text(state.actionLabel) + '</button>',
      '</div>',
      '</section>',
      '<div class="status" id="status" aria-live="polite">' + text(state.status || "") + '</div>',
      state.fallbackPrompt ? renderFallbackPrompt(state.fallbackPrompt) : "",
    ].join("");

    bindEvents();
    notifyHeight();
  }

  function renderGroup(group) {
    return [
      '<section class="intake-section" data-group-id="' + attr(group.id) + '">',
      '<div class="section-title">',
      '<h2>' + text(group.title) + '</h2>',
      group.helper ? '<p class="section-helper">' + text(group.helper) + '</p>' : "",
      '</div>',
      '<div class="chip-row">',
      group.options.map((option) => renderChip(group, option)).join(""),
      '</div>',
      '</section>',
    ].join("");
  }

  function renderFallbackPrompt(prompt) {
    return [
      '<section class="fallback-panel" id="fallbackPanel" aria-label="Manual chat fallback">',
      '<p>Could not send automatically. Copy this prompt and paste it into chat.</p>',
      '<textarea class="fallback-prompt" id="fallbackPrompt" readonly rows="6">' + text(prompt) + '</textarea>',
      '<button class="secondary-action fallback-copy" type="button" id="copyFallbackButton">Copy prompt</button>',
      '</section>',
    ].join("");
  }

  function renderChip(group, option) {
    const key = keyFor(group.id, option.id);
    const selected = state.selected.has(key);
    return [
      '<button type="button" class="chip' + (selected ? " selected" : "") + '"',
      ' data-key="' + attr(key) + '"',
      ' data-group="' + attr(group.id) + '"',
      ' data-value="' + attr(option.value) + '"',
      ' aria-pressed="' + (selected ? "true" : "false") + '">',
      text(option.label),
      '</button>',
    ].join("");
  }

  function bindEvents() {
    app.querySelectorAll(".chip").forEach((button) => {
      button.addEventListener("click", () => toggleChip(button.getAttribute("data-key")));
    });
    app.querySelector("#clearButton").addEventListener("click", clear);
    app.querySelector("#submitButton").addEventListener("click", submit);
    const copyButton = app.querySelector("#copyFallbackButton");
    if (copyButton) copyButton.addEventListener("click", copyFallbackPrompt);
  }

  function toggleChip(key) {
    if (state.selected.has(key)) state.selected.delete(key);
    else state.selected.add(key);
    render();
  }

  function clear() {
    state.selected.clear();
    state.fallbackPrompt = "";
    render();
  }

  async function submit() {
    const prompt = buildPrompt();
    try {
      const bridge = window.creativeProductionMcp;
      if (!bridge || typeof bridge.sendFollowUpMessage !== "function") {
        throw new Error("Creative Production bridge is unavailable.");
      }
      const result = await bridge.sendFollowUpMessage({ prompt });
      if (!result || result.isError) {
        throw new Error(result?.error || "Host rejected follow-up.");
      }
      state.fallbackPrompt = "";
      setStatus(state.sentStatus);
      render();
    } catch (_error) {
      state.fallbackPrompt = prompt;
      setStatus("Could not send automatically. Copy this prompt and paste it into chat.");
      render();
    }
  }

  async function copyFallbackPrompt() {
    const prompt = state.fallbackPrompt || app.querySelector("#fallbackPrompt")?.value || "";
    if (!prompt) return;
    try {
      await navigator.clipboard.writeText(prompt);
      setStatus("Prompt copied.");
    } catch (_error) {
      const fallback = app.querySelector("#fallbackPrompt");
      if (fallback) {
        fallback.focus();
        fallback.select();
      }
      setStatus("Select the prompt text and copy it.");
    }
  }

  function buildPrompt() {
    const selections = groupedSelections();
    const firstLine = [state.targetSkill, state.submitLead].filter(Boolean).join(" ");
    const lines = [
      firstLine,
      state.context.business ? `Business: ${state.context.business}${state.context.location ? `, ${state.context.location}` : ""}` : "",
      state.context.objective ? `Goal: ${state.context.objective}` : "",
      state.context.audience ? `Audience: ${state.context.audience}` : "",
      ...state.groups.map((group) => selections[group.id]?.length ? `${group.title}: ${selections[group.id].join(", ")}` : ""),
      state.completionInstruction,
    ];
    return lines.filter(Boolean).join("\n");
  }

  function groupedSelections() {
    const result = {};
    app.querySelectorAll(".chip.selected").forEach((chip) => {
      const group = chip.getAttribute("data-group");
      const value = chip.getAttribute("data-value");
      if (!result[group]) result[group] = [];
      result[group].push(value);
    });
    return result;
  }

  function setStatus(message) {
    state.status = message;
    const status = app.querySelector("#status");
    if (status) status.textContent = message;
  }

  function readableKind(kind) {
    if (kind === "style") return "Style";
    if (kind === "positioning") return "Positioning";
    return "Mood board";
  }

  function keyFor(groupId, optionId) {
    return `${groupId}:${optionId}`;
  }

  function normalizeStringArray(value) {
    if (Array.isArray(value)) return value.map(String).filter(Boolean);
    if (value) return [String(value)];
    return [];
  }

  function slug(value) {
    return String(value)
      .toLowerCase()
      .replace(/[^a-z0-9]+/g, "-")
      .replace(/^-|-$/g, "");
  }

  function notifyHeight() {
    if (window.creativeProductionMcp && typeof window.creativeProductionMcp.notifyResize === "function") {
      window.creativeProductionMcp.notifyResize();
    }
  }

  function attr(value) {
    return String(value)
      .replaceAll("&", "&amp;")
      .replaceAll('"', "&quot;")
      .replaceAll("<", "&lt;")
      .replaceAll(">", "&gt;");
  }

  function text(value) {
    return String(value)
      .replaceAll("&", "&amp;")
      .replaceAll("<", "&lt;")
      .replaceAll(">", "&gt;");
  }

  render();
}());
