const FALLBACK_STREAM = {
  meta: {
    title: "Mood board",
    subtitle: "Choose a few visual cues to shape the first image set."
  },
  items: []
};

const EMBEDDED_STREAM = window.MOODBOARD_STREAM || null;
const baseStorageKey = "for-you-stream-removed";
const feed = document.querySelector("#feed");
const boardTitle = document.querySelector("#boardTitle");
const boardSummary = document.querySelector("#boardSummary");
const template = document.querySelector("#cardTemplate");
const feedStatus = document.querySelector("#feedStatus");
const generateMoreButton = document.querySelector("#generateMore");
const generateMoreButtonLabel = document.querySelector("#generateMoreLabel");
const fullscreenBoard = document.querySelector("#fullscreenBoard");
const selectionActionToolbar = document.querySelector("#selectionActionToolbar");
const selectionAttach = document.querySelector("#selectionAttach");
const selectionDelete = document.querySelector("#selectionDelete");
const selectionClear = document.querySelector("#clearSelection");
const selectionExportActions = document.querySelector("#exportActions");
const selectionExportPrimary = document.querySelector("#exportPrimary");
const selectionExportPrimaryIcon = document.querySelector("#exportPrimaryIcon");
const selectionExportMenuTrigger = document.querySelector("#exportMenuTrigger");
const selectionExportMenu = document.querySelector("#exportMenu");
const selectionExportMenuItems = [...selectionExportMenu.querySelectorAll("[data-export-target]")];
const viewer = document.querySelector("#viewer");
const viewerImage = document.querySelector("#viewerImage");
const viewerStage = document.querySelector(".viewer-stage");
const viewerToolbar = document.querySelector(".viewer-toolbar");
const viewerClose = document.querySelector("#viewerClose");
const viewerPrev = document.querySelector("#viewerPrev");
const viewerNext = document.querySelector("#viewerNext");
const remixPanel = document.querySelector("#viewerRemixPanel");
const remixSlotTabs = document.querySelector("#remixSlotTabs");
const remixOptionList = document.querySelector("#remixOptionList");
const remixStatus = document.querySelector("#remixStatus");
const attachImage = document.querySelector("#attachImage");
const remixImage = document.querySelector("#remixImage");
const viewerExportActions = document.querySelector("#viewerExportActions");
const viewerExportPrimary = document.querySelector("#viewerExportPrimary");
const viewerExportPrimaryIcon = document.querySelector("#viewerExportPrimaryIcon");
const viewerExportMenuTrigger = document.querySelector("#viewerExportMenuTrigger");
const viewerExportMenu = document.querySelector("#viewerExportMenu");
const viewerExportMenuItems = [...viewerExportMenu.querySelectorAll("[data-export-target]")];
const attachImageLabel = attachImage.querySelector(".button-label");
const remixImageLabel = remixImage.querySelector(".button-label");
const reducedMotionQuery = window.matchMedia("(prefers-reduced-motion: reduce)");
const generatedBatchSize = 12;
const actionToast = document.createElement("div");
let actionToastTimeout = null;
let runStateSaveTimeout = null;
let latestAction = null;
let boardAppendTarget = null;
let mcpPayloadApplied = false;
let mcpPageLoadToken = 0;
let loadedBoardSignature = "";
let mcpRefreshIntervalId = null;
let mcpRefreshInFlight = false;
let selectedIntakeOptionIds = new Set();
let expectedMcpMoodboardItemCount = 0;
let autoFullscreenRequested = false;
const mcpRefreshIntervalMs = 5000;

function setIntakeMode(enabled) {
  document.body.classList.toggle("is-intake-mode", enabled);
  updateFullscreenControl();
}

const EXPLORE_ROUTE_PROMPT_CONTRACTS = {
  ads: "$ads-explorer Explore static ad directions for this business visual brief, preserving the provided context and constraints.",
  shots: "$shot-explorer Explore camera shots, crops, and visual routes for this business visual brief, preserving the provided context and constraints.",
  video: "$video-explorer Shape hooks and motion routes for this business visual brief, preserving the provided context and constraints."
};

const DEFAULT_INTAKE_GROUPS = [
  {
    id: "feeling",
    title: "What should it make people feel?",
    options: ["Quiet prestige", "Clear momentum", "Premium focus", "Calm confidence", "Executive trust", "Inventive energy"]
  },
  {
    id: "include",
    title: "What should show up visually?",
    options: ["Work surfaces", "Light trails", "Human decisions", "Glass interfaces", "Editorial product scenes", "Structured systems"]
  },
  {
    id: "lane",
    title: "Which creative lane feels closest?",
    options: ["Restrained luxury", "Warm and useful", "Sharp editorial", "Futurist minimal", "Material detail", "Human-centered"]
  }
];

const DEFAULT_EXPLORE_GROUPS = [
  {
    id: "paths",
    title: "Where should we start?",
    options: [
      { id: "positioning", label: "Positioning", description: "Clarify audience and occasion.", prompt: "$positioning-explorer Help me shape positioning options for this business visual brief. Start with the shared inline mood-board intake gate if needed, then create image-led options that clarify audience, occasion, business goal, proof, and visual implications." },
      { id: "mood-boards", label: "Mood boards", description: "Image-first visual territories.", prompt: "$moodboard-explorer Build an image-first mood board for this business visual brief. Start from the provided context and ask only for missing constraints that block generation." },
      { id: "scenes", label: "Scenes", description: "See the offer in real contexts.", prompt: "$scene-explorer Explore realistic scene directions for this business visual brief, preserving the provided context and constraints." },
      { id: "offers", label: "Offers", description: "Test the core offer across families.", prompt: "$offer-explorer Explore structured offer directions for this business visual brief, preserving the provided context and constraints." },
      { id: "ads", label: "Ads", description: "Explore static ad directions.", prompt: EXPLORE_ROUTE_PROMPT_CONTRACTS.ads },
      { id: "shots", label: "Shots", description: "Try camera angles and crops.", prompt: EXPLORE_ROUTE_PROMPT_CONTRACTS.shots },
    ],
  },
];

actionToast.className = "action-toast";
actionToast.role = "status";
actionToast.setAttribute("aria-live", "polite");
actionToast.hidden = true;
document.body.append(actionToast);

const cropPositions = [
  "50% 50%",
  "38% 50%",
  "62% 50%",
  "50% 36%",
  "50% 64%",
  "28% 42%",
  "72% 58%",
  "42% 34%",
  "58% 68%"
];
const aspectRatios = [
  "0.78 / 1",
  "1 / 1.24",
  "1 / 0.74",
  "0.88 / 1",
  "1 / 1.38",
  "1 / 0.92",
  "0.72 / 1"
];

let streamItems = [];
let currentImage = null;
let currentImageTrigger = null;
let viewerItems = [];
let currentViewerIndex = -1;
let activeColumnCount = 0;
let viewerTransition = null;
let activeVisibleItems = [];
let feedColumns = [];
let generationSeedItems = [];
let isGeneratingMoreImages = false;
let canGenerateMoreImages = true;
let runToken = window.BV_RUN_TOKEN || null;
const annotationGroups = [];
let remixPanelHideTimeout = null;
let remixPanelOpenFrame = null;
let activeAnnotationComposer = null;
const selectedImageIds = new Set();
const exportTargets = {
  finder: {
    icon: "folder",
    iconType: "platform",
    label: "Folder"
  },
  canva: {
    icon: "canva",
    iconType: "brand",
    label: "Canva"
  },
  figma: {
    icon: "figma",
    iconType: "brand",
    label: "Figma"
  }
};
const remixSlots = [
  {
    id: "style",
    label: "Style",
    promptHint: "Apply a different visual treatment while preserving the selected image's intent."
  },
  {
    id: "palette",
    label: "Colors",
    promptHint: "Shift palette and materials without changing the image's core composition."
  },
  {
    id: "scene",
    label: "Location",
    promptHint: "Move the image into a new scene while preserving the selected subject."
  },
  {
    id: "props",
    label: "Props",
    promptHint: "Change supporting context only; keep the image's main subject intact."
  },
  {
    id: "character",
    label: "Character",
    promptHint: "Change the visible person or persona while preserving the overall mood."
  },
  {
    id: "format",
    label: "Format",
    promptHint: "Adapt the image to another crop or channel while preserving the key visual."
  }
];
const remixOptionLibrary = {
  style: [
    {
      id: "editorial-polish",
      label: "Editorial Polish",
      description: "Cleaner lighting, tighter hierarchy, more premium campaign finish.",
      promptHint: "Apply a more polished editorial treatment while preserving the selected image."
    },
    {
      id: "documentary-realism",
      label: "Documentary Realism",
      description: "More candid texture, natural light, and believable lived-in detail.",
      promptHint: "Shift the image toward documentary realism."
    },
    {
      id: "dramatic-contrast",
      label: "Dramatic Contrast",
      description: "Richer blacks, sharper highlights, and more cinematic emphasis.",
      promptHint: "Apply a more dramatic high-contrast treatment."
    }
  ],
  palette: [
    {
      id: "warm-neutrals",
      label: "Warm Neutrals",
      description: "Soft earth tones, warmer highlights, and more tactile materials.",
      promptHint: "Shift supporting colors toward warm neutrals."
    },
    {
      id: "cool-minimal",
      label: "Cool Minimal",
      description: "Crisper whites, cooler grays, and restrained technical contrast.",
      promptHint: "Use cooler minimal accents around the selected image."
    },
    {
      id: "high-contrast-accent",
      label: "High-Contrast Accent",
      description: "A stronger accent color against quieter supporting surfaces.",
      promptHint: "Use a higher-contrast accent palette without changing the subject."
    }
  ],
  scene: [
    {
      id: "studio-hero",
      label: "Studio Hero",
      description: "Cleaner environment, more controlled light, stronger focal emphasis.",
      promptHint: "Move the image into a cleaner studio-hero setting."
    },
    {
      id: "real-world-context",
      label: "Real-World Context",
      description: "More believable usage context with supporting environmental cues.",
      promptHint: "Move the image into a more realistic usage context."
    },
    {
      id: "close-detail",
      label: "Close Detail",
      description: "Tighter scene focused on material, craft, or product detail.",
      promptHint: "Move the image into a tighter close-detail scene."
    }
  ],
  props: [
    {
      id: "minimal-support",
      label: "Minimal Support",
      description: "Reduce supporting objects so the main subject carries more weight.",
      promptHint: "Reduce supporting props and keep the main subject dominant."
    },
    {
      id: "contextual-cues",
      label: "Contextual Cues",
      description: "Add a few believable objects that clarify place or use.",
      promptHint: "Add restrained contextual props without distracting from the subject."
    },
    {
      id: "premium-finish",
      label: "Premium Finish",
      description: "Sharper materials, cleaner surfaces, and more elevated detail.",
      promptHint: "Add premium material cues as supporting context."
    }
  ],
  character: [
    {
      id: "expert-operator",
      label: "Expert Operator",
      description: "More credible craft, authority, and purposeful interaction.",
      promptHint: "Change the visible character to an expert operator."
    },
    {
      id: "everyday-user",
      label: "Everyday User",
      description: "More approachable, relatable, and less stylized human presence.",
      promptHint: "Change the visible character to an everyday user."
    },
    {
      id: "no-human",
      label: "No Human",
      description: "Let the object, place, or composition carry the image without a person.",
      promptHint: "Remove the visible person and keep the subject or environment as the hero."
    }
  ],
  format: [
    {
      id: "portrait-social",
      label: "Portrait Social",
      description: "Tighter vertical crop for social or story placements.",
      promptHint: "Adapt the image to a portrait social crop."
    },
    {
      id: "wide-hero",
      label: "Wide Hero",
      description: "Broader horizontal composition for landing-page or banner use.",
      promptHint: "Adapt the image to a wide hero composition."
    },
    {
      id: "detail-crop",
      label: "Detail Crop",
      description: "Closer inspection of material, surface, or focal subject detail.",
      promptHint: "Create a closer detail crop while preserving the chosen subject."
    }
  ]
};
let activeExportTargetId = "finder";
let activeRemixSlotId = remixSlots[0].id;
let isRemixPanelOpen = false;
const exportSurfaces = [
  {
    root: selectionExportActions,
    primary: selectionExportPrimary,
    icon: selectionExportPrimaryIcon,
    trigger: selectionExportMenuTrigger,
    menu: selectionExportMenu,
    menuItems: selectionExportMenuItems,
  },
  {
    root: viewerExportActions,
    primary: viewerExportPrimary,
    icon: viewerExportPrimaryIcon,
    trigger: viewerExportMenuTrigger,
    menu: viewerExportMenu,
    menuItems: viewerExportMenuItems,
  },
];

async function loadJson(path, fallback) {
  try {
    const response = await fetch(path);
    if (!response.ok) throw new Error(`${path} returned ${response.status}`);
    return await response.json();
  } catch {
    return fallback;
  }
}

function normalizeToolPayload(payload) {
  if (!payload || typeof payload !== "object") return payload;
  if (payload._meta?.widgetData) return payload._meta.widgetData;
  if (payload.structuredContent && (payload.content || payload._meta || payload.isError !== undefined)) {
    return payload.structuredContent;
  }
  return payload;
}

function mcpWidgetPayload() {
  const openai = window.openai || {};
  const metadata = openai.toolResponseMetadata || {};
  return metadata.widgetData || normalizeToolPayload(openai.toolOutput) || null;
}

function appendTargetFromPayload(payload) {
  if (!payload || typeof payload !== "object") return null;
  const source = payload.appendTarget && typeof payload.appendTarget === "object" ? payload.appendTarget : payload;
  const runDirectory = String(source.runDirectory || "").trim();
  if (!runDirectory) return null;
  return {
    action: "append_to_existing_moodboard",
    toolName: "append_moodboard_board_items",
    runDirectory,
    streamPath: String(source.streamPath || payload.streamPath || "").trim(),
    sourcePage: window.location.href
  };
}

function setBoardAppendTarget(payload) {
  const appendTarget = appendTargetFromPayload(payload);
  if (appendTarget) boardAppendTarget = appendTarget;
  return boardAppendTarget;
}

function normalizeStateIdentityPart(value) {
  return String(value || "").trim().replace(/\/+$/, "");
}

function currentBoardStateIdentity() {
  const runDirectory = normalizeStateIdentityPart(boardAppendTarget?.runDirectory || window.MOODBOARD_RUN_DIRECTORY || "");
  const streamPath = normalizeStateIdentityPart(boardAppendTarget?.streamPath || "");
  const fallbackKey = normalizeStateIdentityPart(window.location.pathname || currentStream.meta?.title || "moodboard");
  const boardStateKey = runDirectory || streamPath || fallbackKey;
  return {
    boardStateKey,
    runDirectory,
    streamPath,
  };
}

function savedStateMatchesCurrentBoard(savedState) {
  const current = currentBoardStateIdentity();
  const savedRunDirectory = normalizeStateIdentityPart(savedState.runDirectory || "");
  const savedStreamPath = normalizeStateIdentityPart(savedState.streamPath || savedState.paths?.streamPath || "");
  const savedBoardStateKey = normalizeStateIdentityPart(savedState.boardStateKey || "");

  if (savedBoardStateKey) return savedBoardStateKey === current.boardStateKey;
  if (savedRunDirectory) return savedRunDirectory === current.runDirectory;
  if (savedStreamPath) return savedStreamPath === current.streamPath;

  // Older widget state did not include an identity, so do not apply it to MCP
  // renders where it can leak deletions between separate board instances.
  return !mcpHostAvailable();
}

function scopedStorageKey() {
  return `${baseStorageKey}:${currentBoardStateIdentity().boardStateKey}`;
}

function itemIdsFromPayload(payload) {
  const stream = streamFromMcpPayload(payload);
  return (stream?.items || []).map((item) => String(item.id || item.title || item.imageUrl || "")).filter(Boolean);
}

function latestActionSignature(action) {
  if (!action || typeof action !== "object") return "";
  return [
    action.id,
    action.createdAt || action.timestamp,
    action.itemCount,
    Array.isArray(action.appendedItemIds) ? action.appendedItemIds.join(",") : ""
  ].filter((value) => value !== undefined && value !== null && value !== "").join("@");
}

function boardSignature(payload = {}) {
  if (!payload || typeof payload !== "object") return "";
  const itemIds = Array.isArray(payload.itemIds) && payload.itemIds.length
    ? payload.itemIds.map(String)
    : itemIdsFromPayload(payload);
  const itemCount = Number(
    payload.totalItemCount
    || payload.itemCount
    || itemIds.length
    || streamItems.length
    || 0
  );
  return [
    payload.runDirectory || boardAppendTarget?.runDirectory || "",
    payload.streamPath || boardAppendTarget?.streamPath || "",
    itemCount,
    payload.streamVersion || itemIds.join(","),
    latestActionSignature(payload.latestAction || latestAction)
  ].join("|");
}

function updateLoadedBoardSignature(payload = {}) {
  const signature = boardSignature(payload);
  if (signature) loadedBoardSignature = signature;
  return loadedBoardSignature;
}

function boardSignatureChanged(payload = {}) {
  const signature = boardSignature(payload);
  return Boolean(signature && signature !== loadedBoardSignature);
}

function explicitItemCountFromPayload(payload = {}) {
  const explicitCount = Number(payload.totalItemCount || payload.itemCount || 0);
  if (explicitCount > 0) return explicitCount;
  return itemIdsFromPayload(payload).length;
}

function shouldApplyMcpGlobalsPayload(payload = {}) {
  if (!mcpPayloadApplied) return true;
  if (!payload || typeof payload !== "object") return false;
  const incomingCount = explicitItemCountFromPayload(payload);
  const currentCount = streamItems.length;
  const incomingActionSignature = latestActionSignature(payload.latestAction);
  if (incomingActionSignature && incomingActionSignature !== latestActionSignature(latestAction)) return true;
  if (payload.streamVersion && boardSignatureChanged(payload)) return true;
  if (incomingCount > currentCount) return true;
  if (incomingCount > 0 && incomingCount < currentCount) return false;
  return incomingCount > 0 && boardSignatureChanged(payload);
}

function streamFromMcpPayload(payload) {
  if (!payload || typeof payload !== "object") return null;
  const stream = payload.stream && typeof payload.stream === "object" ? payload.stream : {};
  const meta = {
    ...(stream.meta || {}),
    ...(payload.meta || {}),
  };
  if (payload.title && !meta.title) meta.title = payload.title;
  if (payload.summary && !meta.subtitle) meta.subtitle = payload.summary;
  const items = Array.isArray(payload.items)
    ? payload.items
    : Array.isArray(payload.routes)
      ? payload.routes
      : Array.isArray(stream.items)
        ? stream.items
        : [];
  return {
    ...stream,
    meta,
    intake: normalizeIntakePayload(payload.intake || stream.intake || payload),
    items,
  };
}

function applyMcpPayload(payload = mcpWidgetPayload()) {
  const stream = streamFromMcpPayload(payload);
  if (!stream) return false;
  setBoardAppendTarget(payload);
  expectedMcpMoodboardItemCount = explicitItemCountFromPayload(payload);
  currentStream = stream;
  streamItems = stream.items || FALLBACK_STREAM.items;
  refreshGenerationSeedItems();
  applySavedRunState(payload.restoredState);
  applyMcpWidgetState();
  setLatestAction(payload.latestAction || null);
  mcpPayloadApplied = true;
  updateLoadedBoardSignature(payload);
  renderFeed();
  void syncMoodboardDisplayMode();
  void loadMcpMoodboardPages(payload);
  startMcpBoardRefreshLoop();
  return true;
}

function mcpDisplayBridgeAvailable() {
  return Boolean(window.creativeProductionMcp?.requestDisplayMode);
}

function mcpHostAvailable() {
  return Boolean(window.creativeProductionMcp) && !window.BV_RUN_TOKEN;
}

function mcpServerToolCaller() {
  if (window.creativeProductionMcp && typeof window.creativeProductionMcp.callServerTool === "function") {
    return window.creativeProductionMcp.callServerTool.bind(window.creativeProductionMcp);
  }
  return null;
}

function payloadFromServerToolResult(result) {
  if (!result || typeof result !== "object") return null;
  return result._meta?.widgetData || normalizeToolPayload(result) || null;
}

function refreshGenerationSeedItems() {
  generationSeedItems = streamItems.filter((item) => item.source !== "Generated continuation.");
  if (generationSeedItems.length === 0) generationSeedItems = [...streamItems];
}

function mergeItemsById(existingItems, incomingItems) {
  const merged = new Map();
  existingItems.forEach((item) => merged.set(item.id, item));
  incomingItems.forEach((item) => {
    if (!item?.id) return;
    merged.set(item.id, {
      ...(merged.get(item.id) || {}),
      ...item,
    });
  });
  return [...merged.values()];
}

async function loadMcpMoodboardPages(payload) {
  const callServerTool = mcpServerToolCaller();
  if (!payload?.runDirectory || !callServerTool) return false;

  const pageToken = ++mcpPageLoadToken;
  const limit = 30;
  let offset = 0;
  let total = Number(payload.itemCount || payload.totalItemCount || streamItems.length || 0);
  expectedMcpMoodboardItemCount = Math.max(expectedMcpMoodboardItemCount, total);
  let loadedItems = [];
  let loadedMeta = {};
  let loadedState = null;
  let loadedLatestAction = payload.latestAction || latestAction;
  if (streamItems.length === 0) feedStatus.textContent = "Loading mood board images.";

  try {
    do {
      const result = await callServerTool({
        name: "get_moodboard_board_page",
        arguments: {
          runDirectory: payload.runDirectory,
          streamPath: payload.streamPath || "",
          runStatePath: payload.runStatePath || "",
          latestActionPath: payload.latestActionPath || "",
          offset,
          limit,
        },
      });
      if (pageToken !== mcpPageLoadToken) return false;

      const page = payloadFromServerToolResult(result);
      setBoardAppendTarget(page);
      const pageStream = streamFromMcpPayload(page);
      const pageItems = pageStream?.items || [];
      if (pageItems.length === 0) break;

      total = Number(page?.totalItemCount || total || pageItems.length);
      loadedItems = mergeItemsById(loadedItems, pageItems);
      loadedMeta = {
        ...loadedMeta,
        ...(pageStream?.meta || {}),
      };
      loadedState = page?.restoredState || loadedState;
      loadedLatestAction = page?.latestAction || loadedLatestAction;

      offset = Number(page?.offset || offset) + pageItems.length;
    } while (offset < total);

    if (loadedItems.length > 0) {
      currentStream = {
        ...currentStream,
        meta: {
          ...(currentStream.meta || {}),
          ...loadedMeta,
        },
        items: loadedItems,
      };
      streamItems = currentStream.items;
      refreshGenerationSeedItems();
      applySavedRunState(loadedState);
      setLatestAction(loadedLatestAction);
      renderFeed();
      void syncMoodboardDisplayMode();
    }

    updateLoadedBoardSignature({
      ...payload,
      totalItemCount: total,
      itemCount: total,
      itemIds: loadedItems.map((item) => item.id),
      latestAction: loadedLatestAction,
    });
    statusForLoadedImages();
    startMcpBoardRefreshLoop();
    return true;
  } catch {
    feedStatus.textContent = "Could not load the saved mood board images from the MCP server.";
    return false;
  }
}

async function refreshMcpBoardIfChanged() {
  if (!mcpHostAvailable() || !boardAppendTarget?.runDirectory || mcpRefreshInFlight) return false;
  const callServerTool = mcpServerToolCaller();
  if (!callServerTool) return false;

  mcpRefreshInFlight = true;
  try {
    const result = await callServerTool({
      name: "get_moodboard_board_status",
      arguments: {
        runDirectory: boardAppendTarget.runDirectory,
        streamPath: boardAppendTarget.streamPath || "",
        latestActionPath: boardAppendTarget.latestActionPath || "",
      },
    });
    const status = payloadFromServerToolResult(result);
    if (!status) return false;
    setBoardAppendTarget(status);
    if (!boardSignatureChanged(status)) return false;
    return await loadMcpMoodboardPages(status);
  } catch {
    return false;
  } finally {
    mcpRefreshInFlight = false;
  }
}

function startMcpBoardRefreshLoop() {
  if (!mcpHostAvailable() || !boardAppendTarget?.runDirectory || mcpRefreshIntervalId) return;
  mcpRefreshIntervalId = window.setInterval(() => {
    void refreshMcpBoardIfChanged();
  }, mcpRefreshIntervalMs);
}

function updateFullscreenControl() {
  if (!fullscreenBoard) return;
  fullscreenBoard.hidden = document.body.classList.contains("is-intake-mode")
    || !mcpDisplayBridgeAvailable()
    || window.openai?.displayMode === "fullscreen";
}

function shouldShowSavedMoodboardLoading() {
  return streamItems.length === 0 && Boolean(boardAppendTarget?.runDirectory) && expectedMcpMoodboardItemCount > 0;
}

function shouldFullscreenMoodboard() {
  return streamItems.length > 0 || shouldShowSavedMoodboardLoading();
}

async function syncMoodboardDisplayMode() {
  if (!mcpDisplayBridgeAvailable()) {
    updateFullscreenControl();
    return;
  }
  if (!shouldFullscreenMoodboard()) {
    updateFullscreenControl();
    return;
  }
  if (autoFullscreenRequested || window.openai?.displayMode === "fullscreen") {
    updateFullscreenControl();
    return;
  }
  autoFullscreenRequested = true;
  try {
    await window.creativeProductionMcp.requestDisplayMode({ mode: "fullscreen" });
  } catch {
    autoFullscreenRequested = false;
    // Keep the inline board usable if the host declines fullscreen.
  }
  updateFullscreenControl();
}

async function requestFullscreenBoard() {
  if (!mcpDisplayBridgeAvailable()) return;
  try {
    await window.creativeProductionMcp.requestDisplayMode({ mode: "fullscreen" });
    fullscreenBoard.hidden = true;
  } catch {
    feedStatus.textContent = "Fullscreen is unavailable in this host.";
  }
}

function notifyHostResize() {
  window.creativeProductionMcp?.notifyResize?.();
}

function showToast(message) {
  window.clearTimeout(actionToastTimeout);
  actionToast.textContent = message;
  actionToast.hidden = false;
  actionToast.classList.add("is-visible");
  actionToastTimeout = window.setTimeout(() => {
    actionToast.classList.remove("is-visible");
    actionToast.hidden = true;
  }, 2600);
}

function escapeHtml(value) {
  return String(value)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");
}

function closeAnnotationComposer() {
  activeAnnotationComposer?.remove();
  activeAnnotationComposer = null;
  document.querySelectorAll(".tile.is-annotating").forEach((tile) => tile.classList.remove("is-annotating"));
}

function annotationComposerMarkup(placeholder, submitLabel) {
  return [
    '<span class="annotation-marker" aria-hidden="true"></span>',
    '<div class="annotation-bubble">',
    '<span class="annotation-leading-icon" data-platform-icon="annotate"></span>',
    `<input class="annotation-input" type="text" autocomplete="off" placeholder="${escapeHtml(placeholder)}" />`,
    '<button class="annotation-cancel" type="button" aria-label="Cancel">',
    '<span data-platform-icon="x"></span>',
    '</button>',
    `<button class="annotation-submit" type="submit" aria-label="${escapeHtml(submitLabel)}">`,
    '<span data-platform-icon="chevron-right"></span>',
    '</button>',
    '</div>'
  ].join("");
}

function appendTargetForAction(action, details = {}) {
  if (!boardAppendTarget?.runDirectory) return null;
  const idempotencySource = [
    action,
    details.sourceImageId,
    details.slotId,
    details.optionId,
    details.annotationPoint?.x,
    details.annotationPoint?.y,
    details.requestedCount
  ].filter((value) => value !== undefined && value !== null && value !== "").join("-");
  return {
    ...boardAppendTarget,
    sourceAction: action,
    idempotencyKey: stableIntakeId(idempotencySource, `${action}-append`)
  };
}

function appendTargetSummary(appendTarget) {
  if (!appendTarget) return [];
  return [
    `- Tool: ${appendTarget.toolName || "append_moodboard_board_items"}`,
    appendTarget.runDirectory ? `- Run directory: ${appendTarget.runDirectory}` : "",
    appendTarget.streamPath ? `- Stream path: ${appendTarget.streamPath}` : "",
    appendTarget.sourceAction ? `- Source action: ${appendTarget.sourceAction}` : "",
    appendTarget.idempotencyKey ? `- Idempotency key: ${appendTarget.idempotencyKey}` : ""
  ].filter(Boolean);
}

function generatedSourceImagePath(item) {
  const runDirectory = boardAppendTarget?.runDirectory || window.MOODBOARD_RUN_DIRECTORY || "";
  const cleanRunDirectory = String(runDirectory || "").replace(/\/+$/, "");
  const sourceImageUrl = String(item?.sourceImageUrl || item?.url || item?.path || item?.imageUrl || "");
  if (!cleanRunDirectory || !sourceImageUrl.startsWith("/generated/")) return "";
  return `${cleanRunDirectory}/generated/${sourceImageUrl.split("/").pop()}`;
}

function sourceImageDimensions(item) {
  const width = Number(item?.sourceImageWidth || item?.width || item?.naturalWidth);
  const height = Number(item?.sourceImageHeight || item?.height || item?.naturalHeight);
  if (Number.isFinite(width) && width > 0 && Number.isFinite(height) && height > 0) {
    return `${Math.round(width)}x${Math.round(height)}`;
  }
  const renderedImage = currentImage?.id === item?.id && viewerImage?.naturalWidth
    ? viewerImage
    : imageForTrigger(triggerForImage(item?.id));
  if (renderedImage?.naturalWidth && renderedImage?.naturalHeight) {
    return `${renderedImage.naturalWidth}x${renderedImage.naturalHeight}`;
  }
  return "";
}

function sourceImageLines(item) {
  const lines = [];
  const sourcePath = generatedSourceImagePath(item);
  const dimensions = sourceImageDimensions(item);
  if (sourcePath) lines.push(`  Original source image path: ${sourcePath}`);
  if (item.sourceImageUrl) lines.push(`  Original source image URL: ${item.sourceImageUrl}`);
  if (item.imageUrl && item.imageUrl !== item.sourceImageUrl) lines.push(`  Preview image URL: ${item.imageUrl}`);
  if (dimensions) lines.push(`  Original dimensions: ${dimensions}`);
  return lines;
}

function annotationEditGuidanceLines(kind, annotationLines) {
  const isAnnotationContext = kind === "creative-production-moodboard-annotation" || annotationLines.length > 0;
  if (!isAnnotationContext) return [];
  return [
    "Annotation edit behavior:",
    "- Treat spot annotations as requests against the exact original image asset, not as prompt-only replacements.",
    "- For remove, erase, clean up, fix this spot, replace, crop, or preserve-composition notes, use the original source image path for an image-edit/inpaint-style revision when available.",
    "- Preserve the original canvas size, aspect ratio, composition, lighting, camera, and style by default; modify only the annotated region unless the user says otherwise.",
    "- If the note asks to explore, remix, make another version, or try a new direction, create a new variation instead of a localized source edit.",
    "- Add source lineage to any revised item: parentItemId, sourceImagePath, annotation, annotationPoint, and editMode: localized-source-edit."
  ];
}

function resultPlacementContextLines(extra = {}) {
  const appendTarget = extra.appendTarget || extra.resultPlacement?.appendTarget || null;
  if (!appendTarget) return [];
  return [
    "Default result handling:",
    "- If this follow-up creates any new, revised, or generated images, add them to this existing mood board by default.",
    "- If the mood-board server already saved the generated images into the run directory, do not append duplicates; otherwise use append_moodboard_board_items with the generated image files.",
    "- Do not render a separate mood board unless the user explicitly asks for one.",
    "Append target:",
    ...appendTargetSummary(appendTarget)
  ];
}

function remixFollowUpPrompt({ item, slot, option, appendTarget }) {
  const direction = option.promptHint || slot.promptHint || option.description || option.label;
  return [
    "Create a mood-board remix of the attached image.",
    "",
    "Source image:",
    `- Title: ${item.title || "Untitled mood-board image"}`,
    `- Image ID: ${item.id}`,
    item.caption ? `- Caption: ${item.caption}` : "",
    "",
    "Remix direction:",
    `- Category: ${slot.label}`,
    `- Option: ${option.label}`,
    `- Instruction: ${direction}`,
    "",
    "Keep the broader mood-board style. Preserve the source image's strongest visual cues while applying the selected direction, and make the result feel like a new image from the same campaign rather than an isolated edit.",
    "",
    "After generating one revised image, append it back to the existing mood board using append_moodboard_board_items.",
    "",
    "Append target:",
    ...appendTargetSummary(appendTarget)
  ].filter(Boolean).join("\n");
}

async function attachItems(items, { viewerMode = false } = {}) {
  const targetItems = items.filter(Boolean);
  if (targetItems.length === 0) {
    showToast("Select images before attaching.");
    return false;
  }

  closeAnnotationComposer();
  const attachedImageIds = targetItems.map((item) => item.id);
  feedStatus.textContent = `Attaching ${selectedImageCountLabel(targetItems.length)} as context.`;

  try {
    await sendMoodboardReferences({
      action: "attach",
      items: targetItems,
      structuredKind: "creative-production-moodboard-attachment",
      structuredContent: {
        kind: "creative-production-moodboard-attachment",
        attachmentMode: "context",
        attachedImageIds
      },
      successMessage: `Attached ${selectedImageCountLabel(targetItems.length)} as image context.`
    });
  } catch (error) {
    showMoodboardReferenceFailure(error);
    return false;
  }

  if (!viewerMode) {
    renderSelectionState();
    scheduleRunStateSave({ interaction: "attach-selection" });
  }

  return true;
}

function attachCurrentImage() {
  if (!currentImage) return false;
  return attachItems([currentImage], { viewerMode: true });
}

function attachSelectedImages() {
  return attachItems(selectedItems(), { viewerMode: false });
}

function attachCurrentImageToThreadComposer() {
  return attachCurrentImage();
}

function attachSelectedImagesToThreadComposer() {
  return attachSelectedImages();
}

function clamp(value, min, max) {
  return Math.min(Math.max(value, min), max);
}

function clamp01(value) {
  return clamp(value, 0, 1);
}

function viewerImageAnnotationPoint(triggerEvent) {
  const rect = viewerImage.getBoundingClientRect();
  if (!rect.width || !rect.height) return null;
  const clientX = triggerEvent ? triggerEvent.clientX : rect.left + rect.width / 2;
  const clientY = triggerEvent ? triggerEvent.clientY : rect.top + rect.height / 2;
  return {
    x: clamp01((clientX - rect.left) / rect.width),
    y: clamp01((clientY - rect.top) / rect.height),
    clientX: clamp(clientX, rect.left, rect.right),
    clientY: clamp(clientY, rect.top, rect.bottom)
  };
}

function normalizedAnnotationPoint(point) {
  if (!point) return null;
  const x = Number(point.x);
  const y = Number(point.y);
  if (!Number.isFinite(x) || !Number.isFinite(y)) return null;
  return {
    x: clamp01(x),
    y: clamp01(y)
  };
}

function openViewerAnnotationComposer(item, triggerEvent) {
  triggerEvent?.preventDefault();
  triggerEvent?.stopPropagation();
  if (!item || viewerTransition || !viewer.classList.contains("active")) return;

  const point = viewerImageAnnotationPoint(triggerEvent);
  if (!point) return;

  closeAnnotationComposer();

  const composer = document.createElement("form");
  composer.className = "annotation-composer viewer-image-annotation-composer";
  composer.setAttribute("aria-label", "Annotate image point");
  composer.innerHTML = annotationComposerMarkup("Annotate this spot...", "Attach annotation");

  const composerWidth = Math.min(420, window.innerWidth - 48);
  const localX = clamp(point.clientX, 28, window.innerWidth - 28);
  const localY = clamp(point.clientY, 28, window.innerHeight - 28);
  const wouldOverflowRight = localX + composerWidth - 20 > window.innerWidth - 12;
  composer.classList.toggle("is-edge-aligned", wouldOverflowRight);
  composer.style.setProperty("--annotation-x", `${localX}px`);
  composer.style.setProperty("--annotation-y", `${localY}px`);

  composer.addEventListener("click", (event) => event.stopPropagation());
  composer.querySelector(".annotation-cancel").addEventListener("click", closeAnnotationComposer);
  composer.addEventListener("submit", (event) => {
    event.preventDefault();
    const input = composer.querySelector(".annotation-input");
    const note = input.value.trim();
    if (!note) {
      input.focus();
      return;
    }
    closeAnnotationComposer();
    const annotationPoint = normalizedAnnotationPoint(point);
    const annotationGroup = createAnnotationGroup({
      kind: "annotate",
      imageIds: [item.id],
      annotation: note,
      point: annotationPoint
    });
    const appendTarget = appendTargetForAction("annotate-image", {
      sourceImageId: item.id,
      annotationPoint
    });
    void sendMoodboardReferences({
      action: "annotate-image",
      items: [item],
      structuredKind: "creative-production-moodboard-annotation",
      structuredContent: {
        kind: "creative-production-moodboard-annotation",
        sourceImageId: item.id,
        sourceImage: attachmentMetadata(item),
        annotation: note,
        annotationPoint,
        annotations: annotationsForImage(item.id),
        currentAnnotationId: annotationGroup?.groupId || "",
        coordinateSystem: "normalized_image_top_left",
        resultPlacement: {
          mode: "append_to_existing_moodboard",
          toolName: "append_moodboard_board_items",
          appendTarget
        },
        appendTarget
      },
      successMessage: "Attached annotation for 1 mood board image."
    }).catch((error) => {
      removeAnnotationGroup(annotationGroup?.groupId);
      showMoodboardReferenceFailure(error);
    });
  });

  document.body.append(composer);
  window.installPlatformIcons?.(composer);
  activeAnnotationComposer = composer;
  requestAnimationFrame(() => composer.querySelector(".annotation-input").focus());
}

function localHttpActionsAvailable() {
  return Boolean(runToken && /^https?:$/.test(window.location.protocol));
}

async function refreshRunToken() {
  const session = await loadJson("/api/session", null);
  if (session?.runToken) runToken = session.runToken;
  return runToken;
}

async function localApi(path, options = {}, retry = true) {
  if (!runToken) await refreshRunToken();
  const headers = {
    ...(options.headers || {}),
    "x-bv-run-token": runToken || ""
  };
  const response = await fetch(path, { ...options, headers });
  if (response.status === 403 && retry) {
    await refreshRunToken();
    return localApi(path, options, false);
  }
  return response;
}

function itemRecord(item) {
  const record = {
    ...attachmentMetadata(item),
    imageUrl: item.imageUrl || "",
    previewImageUrl: item.previewImageUrl || "",
    sourceImageUrl: item.sourceImageUrl || "",
    prompt: item.prompt || ""
  };
  if (item.remixSuggestions) record.remixSuggestions = item.remixSuggestions;
  return record;
}

function currentRunState(extra = {}) {
  const hidden = [...removedIds()];
  return {
    meta: currentStream.meta || {},
    ...currentBoardStateIdentity(),
    selectedImageIds: [...selectedImageIds],
    annotationGroups: annotationGroups.map(annotationGroupRecord),
    hiddenImageIds: hidden,
    activeExportTargetId,
    activeRemixSlotId,
    isRemixPanelOpen,
    currentImageId: currentImage?.id || null,
    visibleItemIds: activeVisibleItems.map((item) => item.id),
    itemCount: streamItems.length,
    items: streamItems.map(itemRecord),
    ...extra
  };
}

function compactWidgetState(extra = {}) {
  return {
    ...currentBoardStateIdentity(),
    selectedImageIds: [...selectedImageIds],
    annotationGroups: annotationGroups.map(annotationGroupRecord),
    hiddenImageIds: [...removedIds()],
    activeExportTargetId,
    activeRemixSlotId,
    isRemixPanelOpen,
    currentImageId: currentImage?.id || null,
    ...extra
  };
}

function saveMcpWidgetState(extra = {}) {
  if (typeof window.openai?.setWidgetState !== "function") return;
  window.openai.setWidgetState(compactWidgetState(extra));
}

function applyMcpWidgetState() {
  const savedState = window.openai?.widgetState;
  if (savedState && typeof savedState === "object" && !savedStateMatchesCurrentBoard(savedState)) return;
  if (savedState && typeof savedState === "object") applySavedRunState(savedState);
}

function applySavedRunState(savedState) {
  if (!savedState || typeof savedState !== "object") return;
  if (!savedStateMatchesCurrentBoard(savedState)) return;

  if (exportTargets[savedState.activeExportTargetId]) {
    activeExportTargetId = savedState.activeExportTargetId;
  }

  if (remixSlots.some((slot) => slot.id === savedState.activeRemixSlotId)) {
    activeRemixSlotId = savedState.activeRemixSlotId;
  }

  if (Array.isArray(savedState.hiddenImageIds)) {
    const availableIds = new Set(streamItems.map((item) => item.id));
    saveRemoved(new Set(savedState.hiddenImageIds.map(String).filter((id) => availableIds.has(id))));
  }

  selectedImageIds.clear();
  const availableIds = new Set(streamItems.map((item) => item.id));
  if (Array.isArray(savedState.selectedImageIds)) {
    savedState.selectedImageIds.forEach((imageId) => {
      const id = String(imageId);
      if (availableIds.has(id)) selectedImageIds.add(id);
    });
  }

  annotationGroups.splice(0, annotationGroups.length);
  if (Array.isArray(savedState.annotationGroups)) {
    savedState.annotationGroups.forEach((group) => {
      if (!group || typeof group !== "object") return;
      const imageIds = Array.isArray(group.imageIds) ? group.imageIds.map(String).filter(Boolean) : [];
      const annotation = String(group.annotation || "").trim();
      if (imageIds.length === 0 || !annotation) return;
      annotationGroups.push({
        groupId: String(group.groupId || makeAnnotationGroupId()),
        imageIds,
        annotation,
        kind: group.kind === "remix" ? "remix" : "annotate",
        createdAt: String(group.createdAt || new Date().toISOString()),
        point: normalizedAnnotationPoint(group.point || group.annotationPoint),
        remix: group.remix && typeof group.remix === "object" ? { ...group.remix } : null
      });
    });
  }

  renderRemixOptions();
}

async function saveRunState(extra = {}) {
  if (!localHttpActionsAvailable()) return null;
  const response = await localApi("/api/state", {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify({ state: currentRunState(extra) })
  });
  const payload = await response.json().catch(() => ({}));
  if (!response.ok) throw new Error(payload.error || "Could not save mood board state.");
  return payload;
}

function scheduleRunStateSave(extra = {}) {
  saveMcpWidgetState(extra);
  if (!localHttpActionsAvailable()) return;
  window.clearTimeout(runStateSaveTimeout);
  runStateSaveTimeout = window.setTimeout(() => {
    void saveRunState(extra).catch(() => {});
  }, 450);
}

async function copyContinuationPrompt(prompt) {
  const clipboard = window.navigator?.clipboard;
  if (!clipboard || typeof clipboard.writeText !== "function") return false;
  await clipboard.writeText(prompt);
  return true;
}

function setLatestAction(action) {
  latestAction = action || null;
}

async function loadLatestAction() {
  if (!localHttpActionsAvailable()) return null;
  const response = await localApi("/api/actions/latest");
  const payload = await response.json().catch(() => ({}));
  if (response.ok && payload.action) setLatestAction(payload.action);
  return payload.action || null;
}

async function stageHttpAction({
  action,
  label,
  prompt,
  selection = {},
  payload = {},
  suppressToast = false,
  toastMessage = "Saved action and copied prompt."
}) {
  if (!localHttpActionsAvailable()) return false;
  const response = await localApi("/api/actions", {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify({
      action,
      label,
      prompt,
      selection,
      payload,
      state: currentRunState({ lastAction: action })
    })
  });
  const result = await response.json().catch(() => ({}));
  if (!response.ok) throw new Error(result.error || "Could not stage action.");

  setLatestAction(result.action);
  const copied = Boolean(result.copied) || await copyContinuationPrompt(result.continuationPrompt).catch(() => false);
  const message = copied ? toastMessage : "Saved action. Clipboard copy is unavailable.";
  feedStatus.textContent = message;
  if (!suppressToast) showToast(message);
  return true;
}

function removedIds() {
  try {
    return new Set(JSON.parse(localStorage.getItem(scopedStorageKey()) || "[]"));
  } catch {
    return new Set();
  }
}

function saveRemoved(ids) {
  localStorage.setItem(scopedStorageKey(), JSON.stringify([...ids]));
}

function visibleStreamItems(hidden) {
  return streamItems.filter((item) => !hidden.has(item.id));
}

function updateBoardChrome(stream) {
  const title = stream.meta?.title || "Mood board";
  const subtitle = stream.meta?.subtitle || "";

  boardTitle.textContent = title;
  boardSummary.textContent = subtitle;
  boardSummary.hidden = subtitle.length === 0;
}

function fallbackSvg(item, index) {
  const palette = item.palette || ["#ffffff", "#edf4f0", "#b8cfc3", "#426554", "#f8fbf9"];
  const [bg, soft, mid, dark, light] = palette;
  const offset = (index % 7) * 44;
  const svg = `
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 900 1100">
      <rect width="900" height="1100" fill="${bg}"/>
      <circle cx="${230 + offset}" cy="260" r="180" fill="${soft}" opacity="0.9"/>
      <circle cx="${680 - offset * 0.6}" cy="820" r="250" fill="${light}" opacity="0.75"/>
      <path d="M120 760 C260 620, 390 820, 520 640 S760 520, 820 650" fill="none" stroke="${dark}" stroke-width="22" opacity="0.28"/>
      <rect x="170" y="340" width="560" height="420" rx="42" fill="${mid}" opacity="0.56"/>
      <rect x="230" y="420" width="160" height="210" rx="28" fill="${light}" opacity="0.72"/>
      <rect x="430" y="400" width="210" height="260" rx="32" fill="${bg}" opacity="0.78"/>
    </svg>
  `;
  return `data:image/svg+xml;charset=utf-8,${encodeURIComponent(svg)}`;
}

function imageSource(item) {
  const previewImageUrl = String(item.previewImageUrl || "");
  const imageUrl = String(item.imageUrl || "");
  if (isUsableImageSource(previewImageUrl)) return previewImageUrl;
  if (isUsableImageSource(imageUrl)) return imageUrl;
  return fallbackSvg(item, item.tileIndex);
}

function isUsableImageSource(url) {
  if (!url) return false;
  if (url.startsWith("data:") || url.startsWith("blob:") || /^https?:/i.test(url)) return true;
  return !mcpHostAvailable();
}

function imageForTrigger(trigger) {
  return trigger?.querySelector("img") || null;
}

function viewportDistance(trigger) {
  const rect = trigger.getBoundingClientRect();
  const viewportCenter = window.innerHeight / 2;
  const triggerCenter = rect.top + rect.height / 2;
  return {
    distance: Math.abs(triggerCenter - viewportCenter),
    visible: rect.bottom > 0 && rect.top < window.innerHeight
  };
}

function triggerForImage(imageId) {
  if (!imageId) return null;
  const candidates = [...feed.querySelectorAll(`.tile-open[data-image-id="${CSS.escape(imageId)}"]`)];
  return candidates.sort((first, second) => {
    const firstState = viewportDistance(first);
    const secondState = viewportDistance(second);
    if (firstState.visible !== secondState.visible) return firstState.visible ? -1 : 1;
    return firstState.distance - secondState.distance;
  })[0] || null;
}

function viewerReturnTrigger() {
  if (currentImageTrigger?.isConnected && currentImageTrigger.dataset.imageId === currentImage?.id) {
    return currentImageTrigger;
  }
  return triggerForImage(currentImage?.id);
}

function buildViewerItems(items) {
  return items.map((item, index) => ({
    ...item,
    src: imageSource({ ...item, tileIndex: index })
  }));
}

function createColumns(columnCount) {
  feed.innerHTML = "";
  feedColumns = Array.from({ length: columnCount }, () => {
    const column = document.createElement("div");
    column.className = "column";
    feed.appendChild(column);
    return column;
  });
}

function tileIndexForItem(item) {
  return activeVisibleItems.findIndex((visibleItem) => visibleItem.id === item.id);
}

function selectedItems() {
  return activeVisibleItems.filter((item) => selectedImageIds.has(item.id));
}

function selectedImageCountLabel(count) {
  return `${count} mood board image${count === 1 ? "" : "s"}`;
}

function stableIntakeId(value, fallback) {
  const slug = String(value || "")
    .toLowerCase()
    .trim()
    .replace(/[^a-z0-9]+/g, "-")
    .replace(/^-+|-+$/g, "");
  return slug || fallback;
}

function normalizeIntakeOption(option, index) {
  if (typeof option === "string") {
    return {
      id: stableIntakeId(option, `option-${index + 1}`),
      label: option,
      value: option,
      description: "",
      prompt: "",
    };
  }
  const label = String(option?.label || option?.title || option?.value || `Option ${index + 1}`);
  return {
    id: String(option?.id || stableIntakeId(label, `option-${index + 1}`)),
    label,
    value: String(option?.value || label),
    description: String(option?.description || option?.summary || option?.bestFor || option?.best_for || ""),
    prompt: String(option?.prompt || option?.nextPrompt || option?.next_prompt || ""),
  };
}

function normalizeIntakeGroups(groups, mode = "moodboard") {
  const defaultGroups = mode === "explore" ? DEFAULT_EXPLORE_GROUPS : DEFAULT_INTAKE_GROUPS;
  const source = Array.isArray(groups) && groups.length ? groups : defaultGroups;
  return source
    .map((group, groupIndex) => {
      const title = String(group?.title || group?.label || `Question ${groupIndex + 1}`);
      const options = group?.options || group?.keywords || group?.items || [];
      return {
        id: String(group?.id || stableIntakeId(title, `group-${groupIndex + 1}`)),
        title,
        options: (Array.isArray(options) ? options : []).map(normalizeIntakeOption).filter((option) => option.label),
      };
    })
    .filter((group) => group.options.length)
    .slice(0, 6);
}

function normalizeIntakePayload(payload = {}) {
  const suggestedSelected = payload.suggestedSelected || payload.selected || payload.defaultSelected;
  return {
    title: String(payload.title || "Shape this mood board"),
    summary: String(payload.summary || "Pick a few cues. I will use them as the creative brief for the first image set."),
    context: payload.context && typeof payload.context === "object" ? payload.context : {},
    mode: String(payload.mode || payload.kind || "moodboard"),
    groups: normalizeIntakeGroups(payload.groups || payload.categories, String(payload.mode || payload.kind || "moodboard")),
    selected: Array.isArray(payload.clickedSelected) ? payload.clickedSelected.map(String) : [],
    suggestedSelected: Array.isArray(suggestedSelected) ? suggestedSelected.map(String) : [],
    actionLabel: String(payload.actionLabel || "Create mood board"),
  };
}

function selectedIntakeOptions(groups) {
  const options = [];
  groups.forEach((group) => {
    group.options.forEach((option) => {
      const optionKey = `${group.id}:${option.id}`;
      if (selectedIntakeOptionIds.has(optionKey)) {
        options.push({
          groupId: group.id,
          groupTitle: group.title,
          id: option.id,
          label: option.label,
          value: option.value,
          description: option.description || "",
          prompt: option.prompt || "",
        });
      }
    });
  });
  return options;
}

function surpriseIntakeSelection(groups, mode) {
  selectedIntakeOptionIds.clear();
  const selectableGroups = groups.filter((group) => group.options.length);
  if (mode === "explore") {
    const options = selectableGroups.flatMap((group) => group.options.map((option) => ({ group, option })));
    const selected = options[Math.floor(Math.random() * options.length)];
    if (selected) selectedIntakeOptionIds.add(`${selected.group.id}:${selected.option.id}`);
    return;
  }
  selectableGroups.forEach((group) => {
    const selected = group.options[Math.floor(Math.random() * group.options.length)];
    if (selected) selectedIntakeOptionIds.add(`${group.id}:${selected.id}`);
  });
}

function moodboardIntakePrompt(intakeState, selections) {
  const grouped = selections.map((selection) => `- ${selection.groupTitle}: ${selection.label}`);
  const contextLines = Object.entries(intakeState.context || {})
    .filter(([, value]) => String(value || "").trim())
    .map(([key, value]) => `- ${key}: ${Array.isArray(value) ? value.join(", ") : value}`);

  if (intakeState.mode === "explore") {
    const selectedWithPrompt = selections.find((selection) => selection.prompt);
    if (selectedWithPrompt) {
      return [
        selectedWithPrompt.prompt,
        contextLines.length ? "" : null,
        contextLines.length ? "Context:" : null,
        ...contextLines,
      ].filter(Boolean).join("\n");
    }
    return [
      "$moodboard-explorer Continue from this Explore intake and route to the selected Creative Production path.",
      "Use the selected path and preserve the provided business context.",
      "",
      "Selected paths:",
      ...(grouped.length ? grouped : ["- Mood boards"]),
      contextLines.length ? "" : null,
      contextLines.length ? "Context:" : null,
      ...contextLines,
    ].filter(Boolean).join("\n");
  }

  if (intakeState.mode === "positioning") {
    return [
      "$positioning-explorer Continue with this qualified brief and create positioning routes.",
      "Use these selections as positioning constraints. Create image-led options that clarify audience, occasion, business goal, proof, and visual implications.",
      "",
      "Selected positioning cues:",
      ...(grouped.length ? grouped : ["- Use the default positioning direction from the brief."]),
      contextLines.length ? "" : null,
      contextLines.length ? "Context:" : null,
      ...contextLines,
    ].filter(Boolean).join("\n");
  }

  return [
    "$moodboard-explorer Continue with this qualified moodboard intake and create the board.",
    "Use these selections as creative constraints. Each moodboard tile should be one single visual reference image, not a mini mood board.",
    "",
    "Selected cues:",
    ...(grouped.length ? grouped : ["- Use the default visual direction from the brief."]),
    contextLines.length ? "" : null,
    contextLines.length ? "Context:" : null,
    ...contextLines,
  ].filter(Boolean).join("\n");
}

async function submitMoodboardIntake(intakeState) {
  const groups = intakeState.groups || [];
  const selections = selectedIntakeOptions(groups);
  const sendFollowUpMessage = followUpSender();
  const prompt = moodboardIntakePrompt(intakeState, selections);
  const structuredContent = {
    kind: intakeState.mode === "explore"
      ? "creative-production-explore-intake"
      : intakeState.mode === "positioning"
        ? "creative-production-positioning-intake"
        : "creative-production-moodboard-setup",
    mode: intakeState.mode,
    selectedCount: selections.length,
    selections,
    context: intakeState.context || {},
  };

  if (!sendFollowUpMessage) {
    await stageHttpAction({
      action: "moodboard-board-intake",
      label: "Moodboard intake",
      prompt,
      selection: { selectedIntake: selections },
      payload: { structuredContent },
      suppressToast: true,
      toastMessage: "Saved mood board intake and copied prompt."
    });
    return;
  }

  const updateModelContext = selectionContextUpdater();
  if (updateModelContext) {
    await updateModelContext({ structuredContent });
  }
  await sendFollowUpMessage({ prompt });
  feedStatus.textContent = "Sent mood board intake.";
}

function renderMoodboardIntake() {
  setIntakeMode(true);
  const intakeState = normalizeIntakePayload(currentStream.intake || {});
  selectedIntakeOptionIds = new Set(intakeState.selected.map(String));
  const suggestedIntakeOptionIds = new Set(intakeState.suggestedSelected.map(String));
  feed.innerHTML = "";
  const panel = document.createElement("section");
  panel.className = `intake-panel ${intakeState.mode === "explore" ? "is-explore" : ""}`;
  panel.setAttribute("aria-label", "Mood board setup");
  const form = document.createElement("form");
  form.className = `intake-form ${intakeState.mode === "explore" ? "is-explore" : ""}`;
  let updateIntakeSubmitState = () => {};

  const header = document.createElement("div");
  header.className = "intake-header";
  const title = document.createElement("h2");
  title.textContent = intakeState.title;
  const summary = document.createElement("p");
  summary.textContent = intakeState.summary;
  header.append(title, summary);
  form.append(header);

  intakeState.groups.forEach((group) => {
    const section = document.createElement("section");
    section.className = "intake-group";
    const heading = document.createElement("h3");
    heading.textContent = group.title;
    const chips = document.createElement("div");
    chips.className = "intake-chip-list";
    group.options.forEach((option) => {
      const optionKey = `${group.id}:${option.id}`;
      const isSuggested = suggestedIntakeOptionIds.has(optionKey);
      const chip = document.createElement("button");
      chip.className = intakeState.mode === "explore" ? "intake-chip intake-path-card" : "intake-chip";
      chip.type = "button";
      chip.dataset.optionKey = optionKey;
      chip.innerHTML = intakeState.mode === "explore"
        ? `<span class="intake-path-title">${escapeHtml(option.label)}</span>${isSuggested ? '<span class="intake-chip-hint">Suggested</span>' : ""}${option.description ? `<span class="intake-path-description">${escapeHtml(option.description)}</span>` : ""}`
        : `${escapeHtml(option.label)}${isSuggested ? '<span class="intake-chip-hint">Suggested</span>' : ""}`;
      if (isSuggested) chip.dataset.suggested = "true";
      chip.setAttribute("aria-pressed", String(selectedIntakeOptionIds.has(optionKey)));
      chip.addEventListener("click", () => {
        if (intakeState.mode === "explore") {
          const wasSelected = selectedIntakeOptionIds.has(optionKey);
          selectedIntakeOptionIds.clear();
          if (!wasSelected) selectedIntakeOptionIds.add(optionKey);
          chips.querySelectorAll(".intake-chip").forEach((candidate) => candidate.setAttribute("aria-pressed", "false"));
        } else if (selectedIntakeOptionIds.has(optionKey)) selectedIntakeOptionIds.delete(optionKey);
        else selectedIntakeOptionIds.add(optionKey);
        chip.setAttribute("aria-pressed", String(selectedIntakeOptionIds.has(optionKey)));
        chip.dataset.suggested = "false";
        chip.querySelector(".intake-chip-hint")?.remove();
        updateIntakeSubmitState();
      });
      chips.append(chip);
    });
    section.append(heading, chips);
    form.append(section);
  });

  const actions = document.createElement("div");
  actions.className = "intake-actions";
  const submit = document.createElement("button");
  submit.className = "intake-submit";
  submit.type = "submit";
  const surprise = document.createElement("button");
  surprise.className = "intake-submit intake-surprise";
  surprise.type = "button";
  surprise.textContent = "Surprise me";
  const updateChipSelectionStates = () => {
    form.querySelectorAll(".intake-chip").forEach((chip) => {
      chip.setAttribute("aria-pressed", String(selectedIntakeOptionIds.has(chip.dataset.optionKey)));
    });
  };
  updateIntakeSubmitState = () => {
    submit.textContent = `Continue with cues (${selectedIntakeOptionIds.size})`;
    submit.disabled = selectedIntakeOptionIds.size === 0;
  };
  updateIntakeSubmitState();
  actions.append(submit, surprise);
  form.append(actions);

  const sendIntake = async (button) => {
    submit.disabled = true;
    surprise.disabled = true;
    button.textContent = "Sending...";
    try {
      await submitMoodboardIntake(intakeState);
    } catch {
      feedStatus.textContent = "Could not send mood board intake.";
      showToast("Could not send mood board intake.");
    } finally {
      submit.disabled = false;
      surprise.disabled = false;
      updateIntakeSubmitState();
      surprise.textContent = "Surprise me";
    }
  };

  form.addEventListener("submit", (event) => {
    event.preventDefault();
    void sendIntake(submit);
  });

  surprise.addEventListener("click", () => {
    surpriseIntakeSelection(intakeState.groups, intakeState.mode);
    updateChipSelectionStates();
    updateIntakeSubmitState();
    void sendIntake(surprise);
  });

  panel.append(form);
  feed.append(panel);
  feed.classList.add("is-intake");
  activeVisibleItems = [];
  viewerItems = [];
  renderSelectionState();
  statusForLoadedImages("Ready for");
  notifyHostResize();
}

function activeExportTarget() {
  return exportTargets[activeExportTargetId];
}

function renderDestinationIcon(node, target) {
  delete node.dataset.brandIcon;
  delete node.dataset.platformIcon;
  node.replaceChildren();
  if (target.iconType === "platform") {
    node.dataset.platformIcon = target.icon;
    window.installPlatformIcons?.(node);
    return;
  }
  node.dataset.brandIcon = target.icon;
  window.installBrandIcons?.(node);
}

function exportMenuIsOpen(surface) {
  return surface.trigger.getAttribute("aria-expanded") === "true";
}

function setExportMenuOpen(surface, isOpen) {
  surface.menu.hidden = !isOpen;
  surface.trigger.setAttribute("aria-expanded", String(isOpen));
  surface.root.classList.toggle("is-open", isOpen);
}

function openExportSurface() {
  return exportSurfaces.find(exportMenuIsOpen) || null;
}

function closeExportMenus(exceptSurface = null) {
  exportSurfaces.forEach((surface) => {
    if (surface !== exceptSurface) setExportMenuOpen(surface, false);
  });
}

function targetIdLabel(target) {
  return `Open in ${target.label}`;
}

function renderExportSurface(surface, { hidden, disabled = false, ariaLabel }) {
  surface.root.hidden = hidden;
  if (hidden) {
    setExportMenuOpen(surface, false);
    return;
  }

  const target = activeExportTarget();
  surface.root.classList.toggle("is-disabled", disabled);
  surface.primary.disabled = disabled;
  surface.trigger.disabled = disabled;
  surface.primary.setAttribute("aria-disabled", String(disabled));
  surface.trigger.setAttribute("aria-disabled", String(disabled));
  if (disabled) setExportMenuOpen(surface, false);
  renderDestinationIcon(surface.icon, target);
  const label = surface.primary.querySelector(".button-label");
  if (label) label.textContent = "Open In";
  surface.primary.setAttribute("aria-label", ariaLabel(target));
  surface.primary.setAttribute("title", targetIdLabel(target));
  surface.menuItems.forEach((item) => {
    const isSelected = item.dataset.exportTarget === activeExportTargetId;
    item.classList.toggle("is-selected", isSelected);
    item.setAttribute("aria-checked", String(isSelected));
  });
}

function renderExportAction() {
  const count = selectedImageIds.size;
  renderExportSurface(exportSurfaces[0], {
    hidden: count === 0,
    disabled: count === 0,
    ariaLabel: (target) => `Open ${selectedImageCountLabel(count)} in ${target.label}`,
  });
  renderExportSurface(exportSurfaces[1], {
    hidden: !currentImage,
    ariaLabel: (target) => `Open current mood board image in ${target.label}`,
  });
}

function setExportTarget(targetId) {
  if (!exportTargets[targetId]) return;
  activeExportTargetId = targetId;
  renderExportAction();
  scheduleRunStateSave({ interaction: "export-target" });
  closeExportMenus();
}

function toggleExportMenu(surface) {
  if (surface.root.hidden || surface.trigger.disabled) return;
  const isOpen = exportMenuIsOpen(surface);
  closeExportMenus();
  setExportMenuOpen(surface, !isOpen);
}

function folderHandoffPaths(items) {
  const runDirectory = boardAppendTarget?.runDirectory || window.MOODBOARD_RUN_DIRECTORY || "";
  const generatedDirectory = runDirectory ? `${runDirectory.replace(/\/+$/, "")}/generated` : "";
  const imagePaths = items
    .map((item) => String(item.sourceImageUrl || item.url || item.path || item.imageUrl || ""))
    .filter((imageUrl) => generatedDirectory && imageUrl.startsWith("/generated/"))
    .map((imageUrl) => `${generatedDirectory}/${imageUrl.split("/").pop()}`);
  return {
    runDirectory,
    generatedDirectory,
    imagePaths
  };
}

async function sendOpenInHandoff(items, targetId) {
  const target = exportTargets[targetId];
  if (!target || items.length === 0) return false;
  const folderPaths = folderHandoffPaths(items);
  const prompt = openInPrompt(items, targetId);

  const sendFollowUpMessage = followUpSender();
  if (!sendFollowUpMessage) {
    try {
      return await stageHttpAction({
        action: `open-in-${targetId}`,
        label: targetIdLabel(target),
        prompt,
        selection: {
          selectedItems: items.map(itemRecord),
          destination: targetId,
          folderPaths
        },
        payload: {
          destination: targetId,
          destinationLabel: target.label,
          attachmentCount: items.length,
          folderPaths
        },
        toastMessage: `Saved ${target.label} handoff and copied prompt.`
      });
    } catch {
      feedStatus.textContent = `Could not save ${target.label} handoff.`;
      return false;
    }
  }

  try {
    await sendFollowUpMessage({ prompt });
    feedStatus.textContent = `Added ${target.label} follow-up prompt for ${selectedImageCountLabel(items.length)} to the composer.`;
    return true;
  } catch {
    feedStatus.textContent = `Could not add ${target.label} follow-up prompt to the composer.`;
    return false;
  }
}

function openInPrompt(items, targetId) {
  const target = exportTargets[targetId];
  const folderPaths = folderHandoffPaths(items);
  const selectedFileLines = items.map((item, index) => {
    const title = item.title || item.id || `Image ${index + 1}`;
    const caption = item.caption ? ` - ${item.caption}` : "";
    const filePath = folderPaths?.imagePaths?.[index] || item.sourceImageUrl || item.imageUrl || "";
    return `${index + 1}. ${title}${caption}${filePath ? ` (${filePath})` : ""}`;
  });
  if (targetId === "finder") {
    return [
      `Open the generated image folder for the selected mood board ${items.length === 1 ? "image" : "images"}.`,
      "Use the file paths below; do not ask the mood-board widget to invoke a local open command.",
      "",
      "Selected files:",
      ...selectedFileLines
    ].join("\n");
  }
  const connectorInstruction = targetId === "figma"
    ? "Use the Figma connector if possible; ask for a target file only if needed."
    : "Use the Canva connector if possible; ask for destination details only if needed.";
  return [
    `Open the selected mood-board ${items.length === 1 ? "image" : "images"} in ${target.label}.`,
    connectorInstruction,
    "",
    "Selected files:",
    ...selectedFileLines
  ].join("\n");
}

function openSelectedImages() {
  const count = selectedImageIds.size;
  if (count === 0) return;
  const items = selectedItems();
  void sendOpenInHandoff(items, activeExportTargetId);
}

function openCurrentImage() {
  if (!currentImage) return;
  void sendOpenInHandoff([currentImage], activeExportTargetId);
}

function updateSelectionStatus(message) {
  const count = selectedImageIds.size;
  if (count === 0) {
    statusForLoadedImages();
    return;
  }
  feedStatus.textContent = `${message} ${selectedImageCountLabel(count)}.`;
}

function updateTileSelection(tile, open, item) {
  const isSelected = selectedImageIds.has(item.id);
  const select = tile.querySelector(".select-button");
  tile.classList.toggle("is-selected", isSelected);
  open.setAttribute("aria-label", `View ${item.title || "image"} large`);
  select?.setAttribute("aria-pressed", String(isSelected));
  select?.setAttribute("aria-label", `${isSelected ? "Deselect" : "Select"} ${item.title || "image"}`);
  select?.setAttribute("title", `${isSelected ? "Deselect" : "Select"} ${item.title || "image"}`);
}

function renderSelectionState() {
  feed.querySelectorAll(".tile").forEach((tile) => {
    const open = tile.querySelector(".tile-open");
    const imageId = open?.dataset.imageId;
    const item = activeVisibleItems.find((visibleItem) => visibleItem.id === imageId);
    if (open && item) updateTileSelection(tile, open, item);
  });
  const count = selectedImageIds.size;
  const attachLabel = selectionAttach?.querySelector(".button-label");
  if (attachLabel) attachLabel.textContent = count > 1 ? `Attach (${count})` : "Attach";
  selectionActionToolbar.hidden = count === 0 || viewer.classList.contains("active");
  selectionActionToolbar.setAttribute("aria-label", count > 0 ? `Actions for ${selectedImageCountLabel(count)}` : "Selected image actions");
  renderExportAction();
  notifyHostResize();
}

function selectionContextUpdater() {
  if (window.creativeProductionMcp && typeof window.creativeProductionMcp.updateModelContext === "function") {
    return window.creativeProductionMcp.updateModelContext.bind(window.creativeProductionMcp);
  }
  if (window.openai && typeof window.openai.updateModelContext === "function") {
    return window.openai.updateModelContext.bind(window.openai);
  }
  return null;
}

function followUpSender() {
  if (window.creativeProductionMcp && typeof window.creativeProductionMcp.sendFollowUpMessage === "function") {
    return window.creativeProductionMcp.sendFollowUpMessage.bind(window.creativeProductionMcp);
  }
  return null;
}

function activeRemixSlot() {
  return remixSlots.find((slot) => slot.id === activeRemixSlotId) || remixSlots[0];
}

function conciseImageFocus(item) {
  const value = item?.caption || item?.title || item?.motif || item?.prompt || "the source image";
  return String(value)
    .replace(/\s+/g, " ")
    .replace(/[.]+$/g, "")
    .trim()
    .slice(0, 120) || "the source image";
}

function remixFocusLabel(item) {
  const title = String(item?.title || "").replace(/\s+/g, " ").trim();
  if (title && !/^image[-\s]*\d*$/i.test(title)) return title.slice(0, 42);
  const fallback = String(item?.motif || item?.caption || item?.prompt || "Selected image");
  const words = fallback.match(/[A-Za-z0-9]+/g) || [];
  const meaningful = words.filter((word) => !["and", "the", "with", "from", "into", "for", "image"].includes(word.toLowerCase()));
  return (meaningful.slice(0, 3).join(" ") || "Selected Image").replace(/\b\w/g, (letter) => letter.toUpperCase());
}

function remixFocusNoun(item) {
  const words = remixFocusLabel(item).match(/[A-Za-z0-9]+/g) || [];
  const meaningful = words.filter((word) => !/^\d+$/.test(word) && !["study", "route", "frame", "image"].includes(word.toLowerCase()));
  return meaningful.at(-1) || "Image";
}

function normalizeRemixOption(option, index, slot) {
  if (typeof option === "string") {
    return {
      id: stableIntakeId(option, `${slot.id}-suggestion-${index + 1}`),
      label: option,
      description: slot.promptHint,
      promptHint: option
    };
  }
  if (!option || typeof option !== "object") return null;
  const label = String(option.label || option.title || option.direction || "").trim();
  if (!label) return null;
  const description = String(option.description || option.summary || option.detail || slot.promptHint || "").trim();
  return {
    id: stableIntakeId(option.id || label, `${slot.id}-suggestion-${index + 1}`),
    label,
    description,
    promptHint: String(option.promptHint || option.prompt || description || label).trim()
  };
}

function imageProvidedRemixOptions(item, slot) {
  const source = item?.remixSuggestions || item?.remix_suggestions || item?.variationSuggestions || item?.variation_suggestions;
  if (!source) return [];
  const rawOptions = Array.isArray(source)
    ? source.filter((option) => !option?.slotId || option.slotId === slot.id)
    : source[slot.id];
  if (!Array.isArray(rawOptions)) return [];
  return rawOptions
    .map((option, index) => normalizeRemixOption(option, index, slot))
    .filter(Boolean)
    .slice(0, 4);
}

function contextualRemixLabel(slot, option, focusNoun) {
  if (slot.id === "style") {
    const styleLead = option.id === "documentary-realism" ? "Documentary" : option.id === "dramatic-contrast" ? "Dramatic" : "Editorial";
    return `${styleLead} ${focusNoun}`;
  }
  if (slot.id === "palette") {
    if (option.id === "warm-neutrals") return `Warm ${focusNoun}`;
    if (option.id === "cool-minimal") return `Cool ${focusNoun}`;
    return `Accent ${focusNoun}`;
  }
  if (slot.id === "scene") {
    if (option.id === "studio-hero") return `${focusNoun} Studio`;
    if (option.id === "real-world-context") return `${focusNoun} In Use`;
    return `${focusNoun} Detail`;
  }
  if (slot.id === "format") {
    if (option.id === "portrait-social") return `Portrait ${focusNoun}`;
    if (option.id === "wide-hero") return `Wide ${focusNoun}`;
    return `${focusNoun} Crop`;
  }
  return option.label;
}

function contextualRemixDescription(slot, option, focus) {
  if (slot.id === "palette") return `${option.description} Tune the color shift around ${focus}.`;
  if (slot.id === "scene") return `${option.description} Keep ${focus} as the recognizable anchor.`;
  if (slot.id === "props") return `${option.description} Let the supporting cues reinforce ${focus}.`;
  if (slot.id === "character") return `${option.description} Preserve the mood and composition around ${focus}.`;
  if (slot.id === "format") return `${option.description} Protect the key read of ${focus}.`;
  return `${option.description} Keep ${focus} recognizable.`;
}

function contextualRemixPromptHint(slot, option, focus) {
  return `${option.promptHint || option.description || slot.promptHint} Preserve the source image's core cue: ${focus}.`;
}

function dynamicRemixOptionsForSlot(slot, item) {
  const focus = conciseImageFocus(item);
  const focusNoun = remixFocusNoun(item);
  return (remixOptionLibrary[slot.id] || []).map((option) => {
    const label = contextualRemixLabel(slot, option, focusNoun);
    return {
      ...option,
      label,
      id: option.id || stableIntakeId(label, `${slot.id}-suggestion`),
      description: contextualRemixDescription(slot, option, focus),
      promptHint: contextualRemixPromptHint(slot, option, focus)
    };
  });
}

function dynamicRemixSuggestions(item) {
  return Object.fromEntries(
    remixSlots.map((slot) => [slot.id, dynamicRemixOptionsForSlot(slot, item)])
  );
}

function remixOptionsForImage(slot, item) {
  const providedOptions = imageProvidedRemixOptions(item, slot);
  if (providedOptions.length > 0) return providedOptions;
  return dynamicRemixOptionsForSlot(slot, item);
}

function remixVariationRecord(slot, option) {
  return {
    slotId: slot.id,
    slotLabel: slot.label,
    slotPromptHint: slot.promptHint || "",
    option
  };
}

function setRemixStatus(message) {
  remixStatus.textContent = message;
  remixStatus.hidden = !message;
  if (isRemixPanelOpen && viewer.classList.contains("has-remix-panel") && !remixPanel.hidden) {
    requestAnimationFrame(syncViewerRemixLayout);
  }
}

function syncViewerRemixToolbarClearance() {
  const toolbarRect = viewerToolbar.getBoundingClientRect();
  const clearance = Math.max(window.innerHeight - toolbarRect.top + 8, 0);
  viewer.style.setProperty("--viewer-remix-toolbar-clearance", `${clearance}px`);
  return toolbarRect;
}

function syncViewerRemixLayout() {
  syncViewerRemixToolbarClearance();
  if (remixPanel.hidden) return;

  const panelHeight = remixPanel.scrollHeight;
  remixPanel.style.setProperty("--viewer-remix-panel-height", `${panelHeight}px`);
  viewer.style.setProperty("--viewer-remix-image-shift", `${-Math.max(Math.round(panelHeight / 2) - 8, 0)}px`);
}

function measureViewerRemixLayout() {
  syncViewerRemixLayout();
}

function cancelRemixPanelHide() {
  if (remixPanelHideTimeout === null) return;
  window.clearTimeout(remixPanelHideTimeout);
  remixPanelHideTimeout = null;
}

function hideRemixPanel() {
  cancelRemixPanelHide();
  if (remixPanelOpenFrame !== null) {
    window.cancelAnimationFrame(remixPanelOpenFrame);
    remixPanelOpenFrame = null;
  }
  remixPanel.hidden = true;
  remixPanel.style.removeProperty("--viewer-remix-panel-height");
  viewer.style.removeProperty("--viewer-remix-image-shift");
}

function setActiveRemixSlot(slotId) {
  activeRemixSlotId = slotId;
  renderRemixPanel();
  scheduleRunStateSave({ interaction: "remix-slot" });
}

function focusRemixSlotTab(index) {
  const nextIndex = (index + remixSlots.length) % remixSlots.length;
  setActiveRemixSlot(remixSlots[nextIndex].id);
  remixSlotTabs.querySelector(`[data-remix-slot-id="${remixSlots[nextIndex].id}"]`)?.focus();
}

function renderRemixSlotTabs() {
  remixSlotTabs.replaceChildren(
    ...remixSlots.map((slot, index) => {
      const selected = slot.id === activeRemixSlotId;
      const tab = document.createElement("button");
      tab.className = "viewer-remix-slot-tab";
      tab.type = "button";
      tab.dataset.remixSlotId = slot.id;
      tab.id = `remix-slot-tab-${slot.id}`;
      tab.role = "tab";
      tab.setAttribute("aria-controls", "remixOptionList");
      tab.setAttribute("aria-selected", String(selected));
      tab.tabIndex = selected ? 0 : -1;
      tab.textContent = slot.label;
      tab.addEventListener("click", () => setActiveRemixSlot(slot.id));
      tab.addEventListener("keydown", (event) => {
        if (event.key === "ArrowLeft") {
          event.preventDefault();
          focusRemixSlotTab(index - 1);
        } else if (event.key === "ArrowRight") {
          event.preventDefault();
          focusRemixSlotTab(index + 1);
        } else if (event.key === "Home") {
          event.preventDefault();
          focusRemixSlotTab(0);
        } else if (event.key === "End") {
          event.preventDefault();
          focusRemixSlotTab(remixSlots.length - 1);
        }
      });
      return tab;
    })
  );
  remixOptionList.setAttribute("aria-labelledby", `remix-slot-tab-${activeRemixSlot().id}`);
}

function renderRemixOptions() {
  remixOptionList.replaceChildren();
  if (!currentImage) return;
  const slot = activeRemixSlot();
  remixOptionsForImage(slot, currentImage).forEach((option) => {
    const row = document.createElement("button");
    row.className = "viewer-remix-option";
    row.type = "button";
    row.addEventListener("click", () => submitCurrentImageRemix(slot, option));

    const copy = document.createElement("span");
    copy.className = "viewer-remix-option-copy";
    const label = document.createElement("strong");
    label.textContent = option.label;
    const description = document.createElement("p");
    description.textContent = option.description;
    copy.append(label, description);
    row.append(copy);
    remixOptionList.append(row);
  });
}

function renderRemixPanel() {
  if (!currentImage) return;
  setRemixStatus("");
  renderRemixSlotTabs();
  renderRemixOptions();
  if (isRemixPanelOpen && viewer.classList.contains("has-remix-panel") && !remixPanel.hidden) {
    requestAnimationFrame(syncViewerRemixLayout);
  }
}

function setRemixPanelOpen(isOpen, { immediate = false } = {}) {
  if (isOpen) closeAnnotationComposer();
  isRemixPanelOpen = isOpen;
  scheduleRunStateSave({ interaction: "remix-panel" });
  remixImage.setAttribute("aria-expanded", String(isOpen));
  remixPanel.setAttribute("aria-hidden", String(!isOpen));

  if (isOpen) {
    cancelRemixPanelHide();
    remixPanel.hidden = false;
    renderRemixPanel();
    measureViewerRemixLayout();
    if (remixPanelOpenFrame !== null) window.cancelAnimationFrame(remixPanelOpenFrame);
    remixPanelOpenFrame = window.requestAnimationFrame(() => {
      remixPanelOpenFrame = null;
      if (!isRemixPanelOpen) return;
      viewer.classList.add("has-remix-panel");
    });
    return;
  }

  if (remixPanelOpenFrame !== null) {
    window.cancelAnimationFrame(remixPanelOpenFrame);
    remixPanelOpenFrame = null;
  }
  viewer.classList.remove("has-remix-panel");
  if (immediate || reducedMotionQuery.matches) {
    hideRemixPanel();
    return;
  }
  cancelRemixPanelHide();
  remixPanelHideTimeout = window.setTimeout(() => {
    remixPanelHideTimeout = null;
    if (!isRemixPanelOpen) hideRemixPanel();
  }, 360);
}

function toggleRemixPanel() {
  setRemixPanelOpen(!isRemixPanelOpen);
}

async function blobForImage(item) {
  const response = await fetch(imageSource({ ...item, tileIndex: tileIndexForItem(item) }));
  if (!response.ok) throw new Error("Could not read image.");
  return await response.blob();
}

async function pngBlobForImage(item) {
  const blob = await blobForImage(item);
  if (blob.type === "image/png") return blob;

  const url = URL.createObjectURL(blob);
  try {
    const image = new Image();
    image.decoding = "async";
    image.src = url;
    await image.decode();

    const canvas = document.createElement("canvas");
    canvas.width = image.naturalWidth || 1024;
    canvas.height = image.naturalHeight || 1024;
    const context = canvas.getContext("2d");
    context.drawImage(image, 0, 0);

    return await new Promise((resolve, reject) => {
      canvas.toBlob((pngBlob) => {
        if (pngBlob) resolve(pngBlob);
        else reject(new Error("Could not convert image."));
      }, "image/png");
    });
  } finally {
    URL.revokeObjectURL(url);
  }
}

function base64FromBytes(bytes) {
  const chunkSize = 0x8000;
  let binary = "";
  for (let index = 0; index < bytes.length; index += chunkSize) {
    binary += String.fromCharCode(...bytes.subarray(index, index + chunkSize));
  }
  return btoa(binary);
}

async function imageContentBlock(item) {
  const blob = await pngBlobForImage(item);
  return {
    type: "image",
    data: base64FromBytes(new Uint8Array(await blob.arrayBuffer())),
    mimeType: "image/png"
  };
}

function attachmentMetadata(item) {
  const sourceImagePath = generatedSourceImagePath(item);
  const originalDimensions = sourceImageDimensions(item);
  return {
    id: item.id,
    title: item.title || "",
    caption: item.caption || "",
    source: item.source || "",
    sourceImageUrl: item.sourceImageUrl || "",
    sourceImagePath,
    previewImageUrl: item.previewImageUrl || "",
    originalDimensions,
    runDirectory: boardAppendTarget?.runDirectory || window.MOODBOARD_RUN_DIRECTORY || "",
    streamPath: boardAppendTarget?.streamPath || "",
    prompt: item.prompt || ""
  };
}

function promptAttachmentMetadata(item) {
  const metadata = {
    id: item.id,
    title: item.title || "",
    caption: item.caption || "",
    sourceImageUrl: item.sourceImageUrl || "",
    sourceImagePath: generatedSourceImagePath(item),
    previewImageUrl: item.previewImageUrl || item.imageUrl || "",
    originalDimensions: sourceImageDimensions(item),
    runDirectory: boardAppendTarget?.runDirectory || window.MOODBOARD_RUN_DIRECTORY || "",
    streamPath: boardAppendTarget?.streamPath || ""
  };
  Object.keys(metadata).forEach((key) => {
    if (metadata[key] === "") delete metadata[key];
  });
  return metadata;
}

async function fileForMoodboardItem(item) {
  const blob = await pngBlobForImage(item);
  const safeId = String(item?.id || "moodboard-image")
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, "-")
    .replace(/^-|-$/g, "")
    || "moodboard-image";
  return new File([blob], `${safeId}.png`, { type: "image/png" });
}

function moodboardUploadId(upload) {
  return upload?.fileId || "";
}

function openaiMoodboardMethod(name) {
  const method = window.openai?.[name];
  return typeof method === "function" ? method.bind(window.openai) : null;
}

function creativeProductionMcpMethod(name) {
  const method = window.creativeProductionMcp?.[name];
  return typeof method === "function" ? method.bind(window.creativeProductionMcp) : null;
}

function moodboardReferenceRecord(item, upload) {
  const fileId = moodboardUploadId(upload);
  if (!fileId) throw new Error("Could not add mood board images to context.");
  return {
    item,
    upload,
    fileId,
    metadata: {
      ...promptAttachmentMetadata(item),
      uploadedFileId: fileId
    }
  };
}

function moodboardMcpReferenceRecord(item) {
  return {
    item,
    upload: null,
    fileId: "",
    metadata: promptAttachmentMetadata(item)
  };
}

function moodboardContextText(items, kind = null, extra = {}) {
  const itemIds = new Set(items.map((item) => item.id));
  const itemLines = items.map((item, index) => {
    const title = item.title || item.id || `Image ${index + 1}`;
    const caption = item.caption ? ` - ${item.caption}` : "";
    return [
      `${index + 1}. ${title}${caption} (id: ${item.id})`,
      ...sourceImageLines(item)
    ].join("\n");
  });
  const includedGroups = annotationGroups
    .filter((group) => group.imageIds.some((imageId) => itemIds.has(imageId)))
    .map(annotationGroupRecord);
  const explicitAnnotations = Array.isArray(extra.annotations)
    ? extra.annotations.filter((annotation) => annotation && typeof annotation === "object")
    : [];
  const annotationLines = [];
  if (explicitAnnotations.length) {
    explicitAnnotations.forEach((annotation, index) => {
      annotationLines.push(`- Annotation ${index + 1}: ${annotation.annotation}`);
      if (annotation.point || annotation.annotationPoint) {
        const annotationPoint = normalizedAnnotationPoint(annotation.point || annotation.annotationPoint);
        annotationLines.push(`  Spot: x=${annotationPoint.x}, y=${annotationPoint.y} in normalized image coordinates from the top-left.`);
      }
    });
  } else if (extra.annotation) {
    annotationLines.push(`- Current annotation: ${extra.annotation}`);
    if (extra.annotationPoint) {
      annotationLines.push(`- Current annotated spot: x=${extra.annotationPoint.x}, y=${extra.annotationPoint.y} in normalized image coordinates from the top-left.`);
    }
  }
  includedGroups.forEach((group, index) => {
    annotationLines.push(`- Saved annotation ${index + 1}: ${group.annotation}`);
    if (group.point) {
      annotationLines.push(`  Spot: x=${group.point.x}, y=${group.point.y} in normalized image coordinates from the top-left.`);
    }
  });
  const resultPlacementLines = resultPlacementContextLines(extra);
  const annotationEditLines = annotationEditGuidanceLines(kind, annotationLines);
  return [
    "Mood-board images have been attached as context.",
    `Context kind: ${kind || (annotationLines.length > 0 ? "creative-production-moodboard-annotated-context" : "creative-production-moodboard-selection")}.`,
    "",
    "Attached images:",
    ...itemLines,
    annotationLines.length ? "" : null,
    annotationLines.length ? "Annotations:" : null,
    ...annotationLines,
    annotationEditLines.length ? "" : null,
    ...annotationEditLines,
    resultPlacementLines.length ? "" : null,
    ...resultPlacementLines,
    "",
    "Use the attached image content for visual understanding. Use the text above to identify selected images, annotations, and annotated spots."
  ].filter(Boolean).join("\n");
}

async function sendMoodboardReferences({
  action,
  items,
  structuredKind,
  structuredContent = {},
  successMessage
}) {
  const targetItems = items.filter(Boolean);
  if (targetItems.length === 0) throw new Error("Select images before adding context.");

  const mcpUpdateModelContext = creativeProductionMcpMethod("updateModelContext");
  if (mcpUpdateModelContext) {
    const records = targetItems.map(moodboardMcpReferenceRecord);
    const imageBlocks = await Promise.all(targetItems.map(imageContentBlock));
    const textBlock = { type: "text", text: moodboardContextText(targetItems, structuredKind, structuredContent) };
    await mcpUpdateModelContext({
      content: [textBlock, ...imageBlocks],
      structuredContent: moodboardStructuredContent(targetItems, structuredKind, {
        action,
        ...structuredContent,
        attachments: records.map((record) => record.metadata)
      })
    });
    feedStatus.textContent = successMessage;
    showToast(successMessage);
    scheduleRunStateSave({ interaction: action });
    return records;
  }

  const uploadFile = openaiMoodboardMethod("uploadFile");
  const updateModelContext = openaiMoodboardMethod("updateModelContext");
  if (!uploadFile || !updateModelContext) {
    throw new Error("Could not add mood board images to context.");
  }

  const records = await Promise.all(targetItems.map(async (item) => {
    const file = await fileForMoodboardItem(item);
    const upload = await uploadFile(file);
    return moodboardReferenceRecord(item, upload);
  }));
  const uploadedFileIds = records.map((record) => record.fileId).filter(Boolean);
  const imageBlocks = await Promise.all(targetItems.map(imageContentBlock));
  const textBlock = { type: "text", text: moodboardContextText(targetItems, structuredKind, structuredContent) };

  await updateModelContext({
    content: [textBlock, ...imageBlocks],
    structuredContent: moodboardStructuredContent(targetItems, structuredKind, {
      action,
      ...structuredContent,
      uploadedFileIds,
      uploadedFiles: records.map((record) => record.metadata)
    })
  });
  feedStatus.textContent = successMessage;
  showToast(successMessage);
  scheduleRunStateSave({ interaction: action });
  return records;
}

async function sendMoodboardFollowUp({
  action,
  items,
  prompt,
  successMessage
}) {
  const targetItems = items.filter(Boolean);
  if (targetItems.length === 0) throw new Error("Select images before sending a follow-up.");
  const resolvedPrompt = typeof prompt === "function" ? prompt() : String(prompt || "");
  if (!resolvedPrompt) throw new Error("Missing follow-up prompt.");

  const imageBlocks = await Promise.all(targetItems.map(imageContentBlock));
  const mcpSendFollowUpMessage = creativeProductionMcpMethod("sendFollowUpMessage");
  if (mcpSendFollowUpMessage) {
    await mcpSendFollowUpMessage({
      prompt: resolvedPrompt,
      content: [
        { type: "text", text: resolvedPrompt },
        ...imageBlocks
      ]
    });
    feedStatus.textContent = successMessage;
    showToast(successMessage);
    scheduleRunStateSave({ interaction: action });
    return;
  }

  const sendFollowUpMessage = openaiMoodboardMethod("sendFollowUpMessage");
  const uploadFile = openaiMoodboardMethod("uploadFile");
  if (!sendFollowUpMessage || !uploadFile) {
    throw new Error("Could not send mood board follow-up.");
  }

  const uploadedFileIds = await Promise.all(targetItems.map(async (item) => {
    const file = await fileForMoodboardItem(item);
    const upload = await uploadFile(file);
    return moodboardUploadId(upload);
  }));
  await sendFollowUpMessage({
    prompt: resolvedPrompt,
    content: [
      { type: "text", text: resolvedPrompt },
      ...imageBlocks
    ],
    uploadedFileIds: uploadedFileIds.filter(Boolean)
  });
  feedStatus.textContent = successMessage;
  showToast(successMessage);
  scheduleRunStateSave({ interaction: action });
}

function showMoodboardReferenceFailure(error) {
  const message = error?.message || "Could not add mood board images to context.";
  feedStatus.textContent = message;
  showToast(message);
}

function makeAnnotationGroupId() {
  const random = Math.random().toString(36).slice(2, 8);
  return `anno_${Date.now().toString(36)}_${random}`;
}

function annotationGroupRecord(group) {
  const record = {
    groupId: group.groupId,
    kind: group.kind,
    annotation: group.annotation,
    imageIds: [...group.imageIds],
    attachmentIds: [...group.imageIds],
    createdAt: group.createdAt
  };
  if (group.point) record.point = normalizedAnnotationPoint(group.point);
  if (group.remix) record.remix = { ...group.remix };
  return record;
}

function createAnnotationGroup({ kind, imageIds, annotation, point = null, remix = null }) {
  const cleanImageIds = [...new Set(imageIds.map(String).filter(Boolean))];
  const cleanAnnotation = String(annotation || "").trim();
  if (cleanImageIds.length === 0 || !cleanAnnotation) return null;
  const group = {
    groupId: makeAnnotationGroupId(),
    imageIds: cleanImageIds,
    annotation: cleanAnnotation,
    kind,
    createdAt: new Date().toISOString(),
    point: normalizedAnnotationPoint(point),
    remix
  };
  annotationGroups.push(group);
  scheduleRunStateSave({ interaction: `${kind}-group` });
  return group;
}

function removeAnnotationGroup(groupId) {
  if (!groupId) return false;
  const index = annotationGroups.findIndex((group) => group.groupId === groupId);
  if (index < 0) return false;
  annotationGroups.splice(index, 1);
  scheduleRunStateSave({ interaction: "remove-annotation-group" });
  return true;
}

function annotationsForImage(imageId) {
  const id = String(imageId || "");
  return annotationGroups
    .filter((group) => group.kind === "annotate" && group.imageIds.includes(id))
    .map((group) => {
      const record = annotationGroupRecord(group);
      return {
        id: record.groupId,
        annotation: record.annotation,
        annotationPoint: record.point || null,
        point: record.point || null,
        imageId: id,
        createdAt: record.createdAt
      };
    });
}

function moodboardStructuredContent(items, kind = null, extra = {}) {
  const itemIds = new Set(items.map((item) => item.id));
  const includedAnnotationGroups = annotationGroups.filter((group) => (
    group.imageIds.some((imageId) => itemIds.has(imageId))
  ));
  return {
    kind: kind || (includedAnnotationGroups.length > 0 ? "creative-production-moodboard-annotated-context" : "creative-production-moodboard-selection"),
    attachmentCount: items.length,
    attachments: items.map(promptAttachmentMetadata),
    annotationGroups: includedAnnotationGroups.map((group) => ({
      ...annotationGroupRecord(group),
      includedImageIds: group.imageIds.filter((imageId) => itemIds.has(imageId))
    })),
    annotationInstruction: includedAnnotationGroups.length > 0
      ? "Images are associated with annotations in background metadata. Only annotation groups for the current image context are included."
      : "",
    ...extra
  };
}

function submitCurrentImageRemix(slot, option) {
  if (!currentImage) return;
  setRemixStatus("");
  const item = currentImage;
  const appendTarget = appendTargetForAction("remix-image", {
    sourceImageId: item.id,
    slotId: slot.id,
    optionId: option.id
  });
  void sendMoodboardFollowUp({
    action: "remix-image",
    items: [item],
    prompt: () => remixFollowUpPrompt({ item, slot, option, appendTarget }),
    successMessage: "Sent remix request with source image context."
  }).then(() => {
    createAnnotationGroup({
      kind: "remix",
      imageIds: [item.id],
      annotation: option.promptHint || slot.promptHint || option.description || option.label,
      remix: {
        slotId: slot.id,
        slotLabel: slot.label,
        optionId: option.id,
        optionLabel: option.label
      }
    });
  }).catch((error) => {
    showMoodboardReferenceFailure(error);
  });
}

function toggleImageSelection(item) {
  if (selectedImageIds.has(item.id)) {
    selectedImageIds.delete(item.id);
  } else {
    selectedImageIds.add(item.id);
  }
  renderSelectionState();
  scheduleRunStateSave({ interaction: "selection" });
}

function clearImageSelection({ silent = false } = {}) {
  if (selectedImageIds.size === 0) return;
  selectedImageIds.clear();
  renderSelectionState();
  if (!silent) feedStatus.textContent = "Selection cleared.";
  scheduleRunStateSave({ interaction: "selection-clear" });
}

function deleteSelectedImages() {
  if (selectedImageIds.size === 0) return;
  const hidden = removedIds();
  const deletedImageIds = [...selectedImageIds];
  deletedImageIds.forEach((imageId) => hidden.add(imageId));
  selectedImageIds.clear();
  saveRemoved(hidden);
  renderFeed();
  feedStatus.textContent = "Selected images deleted.";
  showToast("Selected images deleted.");
  scheduleRunStateSave({ interaction: "delete-selected" });
}

function pruneSelectedImages(hidden) {
  let changed = false;
  selectedImageIds.forEach((imageId) => {
    if (hidden.has(imageId) || !streamItems.some((item) => item.id === imageId)) {
      selectedImageIds.delete(imageId);
      changed = true;
    }
  });
  return changed;
}

function appendItems(items) {
  items.forEach((item) => {
    const tile = template.content.firstElementChild.cloneNode(true);
    const open = tile.querySelector(".tile-open");
    const select = tile.querySelector(".select-button");
    const img = tile.querySelector("img");
    const remove = tile.querySelector(".remove-button");
    const tileIndex = tileIndexForItem(item);
    const renderItem = { ...item, tileIndex };
    const src = imageSource(renderItem);

    window.installPlatformIcons?.(tile);
    img.src = src;
    img.alt = item.title || "";
    img.loading = tileIndex < 12 ? "eager" : "lazy";
    img.decoding = "async";
    img.style.objectPosition = cropPositions[tileIndex % cropPositions.length];
    tile.style.aspectRatio = aspectRatios[tileIndex % aspectRatios.length];
    open.dataset.imageId = item.id;
    updateTileSelection(tile, open, item);
    select.setAttribute("aria-label", `${selectedImageIds.has(item.id) ? "Deselect" : "Select"} ${item.title || "image"}`);
    select.setAttribute("title", `${selectedImageIds.has(item.id) ? "Deselect" : "Select"} ${item.title || "image"}`);
    open.addEventListener("click", () => openViewer(renderItem, src, open));
    select.addEventListener("click", (event) => {
      event.stopPropagation();
      toggleImageSelection(renderItem);
    });
    remove.addEventListener("click", (event) => {
      event.stopPropagation();
      const hidden = removedIds();
      hidden.add(item.id);
      selectedImageIds.delete(item.id);
      saveRemoved(hidden);
      renderFeed();
      feedStatus.textContent = "Image deleted.";
      scheduleRunStateSave({ interaction: "remove-image" });
      if (currentImage?.id === item.id) closeViewer();
    });

    feedColumns[tileIndex % feedColumns.length].appendChild(tile);
  });
}

function statusForLoadedImages(message = "Loaded") {
  if (streamItems.length === 0) {
    feedStatus.textContent = `${message} mood board intake.`;
    return;
  }
  feedStatus.textContent = `${message} ${activeVisibleItems.length} unique mood board images.`;
}

function updateGenerateMoreControl() {
  if (!generateMoreButton) return;
  generateMoreButton.hidden = true;
  generateMoreButton.disabled = true;
  generateMoreButton.classList.toggle("is-generating", false);
  generateMoreButton.setAttribute("aria-busy", "false");
  if (generateMoreButtonLabel) generateMoreButtonLabel.textContent = "Generate more";
}

function generationPrompt(source, sequence) {
  const sourcePrompt = source.prompt || source.caption || source.title || "A mood board image";
  return `${sourcePrompt} Create a fresh unique continuation image ${sequence} for the same mood board. Use a materially different composition, crop, camera angle, lighting nuance, and subject arrangement from every prior image. Do not duplicate an existing frame, contact sheet, collage, or readable text.`;
}

function generatedItem(source, sequence) {
  const paddedSequence = String(sequence).padStart(3, "0");
  const item = {
    ...source,
    id: `${source.id}-variation-${paddedSequence}`,
    title: `${source.title || "Mood board image"} Study ${sequence}`,
    caption: source.caption || "Generated continuation.",
    source: "Generated continuation.",
    prompt: generationPrompt(source, sequence)
  };
  return {
    ...item,
    remixSuggestions: dynamicRemixSuggestions(item)
  };
}

function nextGeneratedItems() {
  const generatedCount = streamItems.length - generationSeedItems.length;
  return Array.from({ length: generatedBatchSize }, (_, offset) => {
    const sequence = generatedCount + offset + 1;
    const source = generationSeedItems[(sequence - 1) % generationSeedItems.length];
    return generatedItem(source, sequence);
  });
}

function shouldGenerateMoreImages() {
  return canGenerateMoreImages
    && !isGeneratingMoreImages
    && generationSeedItems.length > 0;
}

function generateMorePrompt(items, appendTarget = null) {
  return [
    `Generate ${items.length} more image${items.length === 1 ? "" : "s"} for this mood board.`,
    "Use the existing board as the source direction and generate more images like it. Preserve the strongest visual language, materials, lighting, palette, and composition patterns while creating new original references.",
    "Create the strongest set of new visual references that feel like they belong in the same campaign.",
    "Add the results back to this board by default.",
    "",
    "If the mood-board server already saved the generated images into the run directory, do not append duplicates; otherwise use append_moodboard_board_items with the generated image files.",
    "Do not render a separate mood board unless the user explicitly asks for one.",
    "",
    "Append target:",
    ...appendTargetSummary(appendTarget)
  ].join("\n");
}

async function generateMoreImages() {
  if (!shouldGenerateMoreImages()) return;

  isGeneratingMoreImages = true;
  updateGenerateMoreControl();
  feedStatus.textContent = "Sending request to generate more mood board images.";

  try {
    const requestedItems = nextGeneratedItems();
    const appendTarget = appendTargetForAction("generate-more", {
      requestedCount: requestedItems.length
    });
    const sendFollowUpMessage = followUpSender();
    if (!sendFollowUpMessage) {
      await stageHttpAction({
        action: "generate-more",
        label: "Generate more",
        prompt: generateMorePrompt(requestedItems, appendTarget),
        selection: {
          seedItems: generationSeedItems.slice(0, 4).map(itemRecord)
        },
        payload: {
          requestedCount: requestedItems.length,
          requestedItems: requestedItems.map(itemRecord),
          appendTarget
        },
        toastMessage: "Saved generate-more action and copied prompt."
      });
      return;
    }
    const updateModelContext = selectionContextUpdater();
    if (updateModelContext) {
      const contextSeeds = generationSeedItems.slice(0, 4);
      await updateModelContext({
        content: await Promise.all(contextSeeds.map(imageContentBlock)),
        structuredContent: {
          kind: "creative-production-moodboard-generate-more",
          requestedCount: requestedItems.length,
          requestedItems: requestedItems.map(attachmentMetadata),
          seedCount: contextSeeds.length,
          seeds: contextSeeds.map(attachmentMetadata),
          appendTarget
        }
      });
    }
    await sendFollowUpMessage({ prompt: generateMorePrompt(requestedItems, appendTarget) });
    feedStatus.textContent = "Sent request to generate more mood board images.";
  } catch {
    feedStatus.textContent = "Could not send generate-more request.";
  } finally {
    isGeneratingMoreImages = false;
    updateGenerateMoreControl();
  }
}

function renderFeed() {
  setIntakeMode(false);
  feed.classList.remove("is-intake");
  if (streamItems.length === 0) {
    updateBoardChrome(currentStream);
    if (shouldShowSavedMoodboardLoading()) {
      feed.replaceChildren();
      activeVisibleItems = [];
      viewerItems = [];
      renderSelectionState();
      feedStatus.textContent = "Loading mood board images.";
      updateGenerateMoreControl();
      notifyHostResize();
      return;
    }
    renderMoodboardIntake();
    updateGenerateMoreControl();
    return;
  }
  const hidden = removedIds();
  pruneSelectedImages(hidden);
  let visibleItems = visibleStreamItems(hidden);
  if (visibleItems.length === 0 && streamItems.length > 0) {
    hidden.clear();
    saveRemoved(hidden);
    visibleItems = streamItems;
  }
  activeVisibleItems = visibleItems;
  viewerItems = buildViewerItems(visibleItems);
  updateBoardChrome(currentStream);
  const columnCount = Number.parseInt(getComputedStyle(feed).getPropertyValue("--columns"), 10) || 5;
  createColumns(columnCount);
  appendItems(visibleItems);
  renderSelectionState();
  statusForLoadedImages();
  updateGenerateMoreControl();

  if (currentImage) {
    currentImageTrigger = viewerReturnTrigger();
  }
  notifyHostResize();
}

function setViewerOpen(isOpen) {
  if (isOpen) syncViewerRemixToolbarClearance();
  viewer.classList.toggle("active", isOpen);
  viewer.setAttribute("aria-hidden", String(!isOpen));
  selectionActionToolbar.hidden = isOpen || selectedImageIds.size === 0;
}

function nextFrame() {
  return new Promise((resolve) => requestAnimationFrame(resolve));
}

function visualState(element) {
  const rect = element.getBoundingClientRect();
  const styles = getComputedStyle(element);
  return {
    left: rect.left,
    top: rect.top,
    width: rect.width,
    height: rect.height,
    borderRadius: styles.borderRadius,
    boxShadow: styles.boxShadow,
    objectFit: styles.objectFit,
    objectPosition: styles.objectPosition
  };
}

function hasVisualSize(state) {
  return state.width > 0 && state.height > 0;
}

function transitionFrame(state) {
  return {
    left: `${state.left}px`,
    top: `${state.top}px`,
    width: `${state.width}px`,
    height: `${state.height}px`,
    borderRadius: state.borderRadius,
    boxShadow: state.boxShadow,
    objectFit: state.objectFit,
    objectPosition: state.objectPosition,
    opacity: 1
  };
}

function hideImage(image) {
  if (!image) return () => {};
  const previousVisibility = image.style.visibility;
  image.style.visibility = "hidden";
  return () => {
    image.style.visibility = previousVisibility;
  };
}

function createTransitionImage(src, state) {
  const transitionImage = document.createElement("img");
  transitionImage.className = "viewer-transition-image";
  transitionImage.alt = "";
  transitionImage.setAttribute("aria-hidden", "true");
  transitionImage.src = src;
  Object.assign(transitionImage.style, transitionFrame(state));
  document.body.appendChild(transitionImage);
  return transitionImage;
}

async function animateViewerTransition(sourceImage, targetImage, src, update) {
  if (reducedMotionQuery.matches || !sourceImage?.isConnected || !targetImage?.isConnected) {
    await update();
    return;
  }

  const fromState = visualState(sourceImage);
  if (!hasVisualSize(fromState)) {
    await update();
    return;
  }

  viewerTransition = true;
  viewer.classList.add("transitioning");
  const transitionImage = createTransitionImage(src, fromState);
  const restoreSourceImage = hideImage(sourceImage);
  const restoreTargetImage = sourceImage === targetImage ? () => {} : hideImage(targetImage);
  try {
    await update();
    await nextFrame();

    const toState = visualState(targetImage);
    if (!hasVisualSize(toState)) return;

    const animation = transitionImage.animate(
      [transitionFrame(fromState), transitionFrame(toState)],
      {
        duration: 360,
        easing: "cubic-bezier(0.22, 1, 0.36, 1)",
        fill: "both"
      }
    );
    viewerTransition = animation;
    await animation.finished.catch(() => {});
  } finally {
    transitionImage.remove();
    restoreSourceImage();
    restoreTargetImage();
    viewer.classList.remove("transitioning");
    viewerTransition = null;
  }
}

async function openViewer(item, src, trigger) {
  if (viewer.classList.contains("active") || viewerTransition) return;
  closeExportMenus();
  currentViewerIndex = viewerItems.findIndex((viewerItem) => viewerItem.id === item.id);
  currentImage = currentViewerIndex >= 0 ? viewerItems[currentViewerIndex] : { ...item, src };
  currentImageTrigger = trigger;
  scheduleRunStateSave({ interaction: "viewer-open" });

  await animateViewerTransition(imageForTrigger(trigger), viewerImage, currentImage.src, async () => {
    updateViewerImage();
    setViewerOpen(true);
    await viewerImage.decode().catch(() => {});
  });

  viewerClose.focus({ preventScroll: true });
}

function updateViewerImage() {
  if (!currentImage) return;
  viewerImage.src = currentImage.src;
  viewerImage.alt = "";
  renderExportAction();
  if (isRemixPanelOpen) renderRemixPanel();
}

function navigateViewer(direction) {
  if (!viewer.classList.contains("active") || viewerItems.length === 0 || viewerTransition) return;
  closeAnnotationComposer();
  currentViewerIndex = (currentViewerIndex + direction + viewerItems.length) % viewerItems.length;
  currentImage = viewerItems[currentViewerIndex];
  currentImageTrigger = viewerReturnTrigger();
  updateViewerImage();
  scheduleRunStateSave({ interaction: "viewer-navigate" });
}

function setButtonLabel(buttonLabel, label) {
  buttonLabel.textContent = label;
}

function resetViewerState() {
  closeAnnotationComposer();
  setViewerOpen(false);
  viewerImage.removeAttribute("src");
  currentImage = null;
  currentViewerIndex = -1;
  currentImageTrigger = null;
  setRemixPanelOpen(false, { immediate: true });
  renderSelectionState();
  setButtonLabel(attachImageLabel, "Attach");
  setButtonLabel(remixImageLabel, "Remix");
  setRemixStatus("");
  scheduleRunStateSave({ interaction: "viewer-close" });
}

async function closeViewer() {
  if (!viewer.classList.contains("active") || viewerTransition) return;
  const focusTarget = viewerReturnTrigger();

  await animateViewerTransition(viewerImage, imageForTrigger(focusTarget), currentImage?.src || viewerImage.currentSrc || viewerImage.src, async () => {
    setViewerOpen(false);
  });

  resetViewerState();
  focusTarget?.focus({ preventScroll: true });
}

async function init() {
  const stream = streamFromMcpPayload(mcpWidgetPayload()) || EMBEDDED_STREAM || await loadJson("/api/stream", null) || await loadJson("data/stream-static.json", null) || await loadJson("data/stream.json", FALLBACK_STREAM);
  currentStream = stream;
  streamItems = Array.isArray(stream.items) ? stream.items : FALLBACK_STREAM.items;
  refreshGenerationSeedItems();
  const initialMcpPayload = mcpWidgetPayload();
  if (initialMcpPayload) {
    setBoardAppendTarget(initialMcpPayload);
    applySavedRunState(initialMcpPayload.restoredState);
    applyMcpWidgetState();
    setLatestAction(initialMcpPayload.latestAction || null);
    updateLoadedBoardSignature(initialMcpPayload);
    mcpPayloadApplied = true;
  }
  const localSession = mcpHostAvailable() ? null : await loadJson("/api/session", null);
  if (localSession) setBoardAppendTarget(localSession);
  runToken = window.BV_RUN_TOKEN || localSession?.runToken || null;
  if (localHttpActionsAvailable()) {
    const savedState = await loadJson("/api/state", null);
    applySavedRunState(savedState);
    await loadLatestAction().catch(() => null);
  }
  activeColumnCount = Number.parseInt(getComputedStyle(feed).getPropertyValue("--columns"), 10) || 5;
  renderFeed();
  void syncMoodboardDisplayMode();
  if (initialMcpPayload) void loadMcpMoodboardPages(initialMcpPayload);
  startMcpBoardRefreshLoop();
  updateFullscreenControl();
  scheduleRunStateSave({ interaction: "init" });
}

let currentStream = FALLBACK_STREAM;

viewerClose.addEventListener("click", closeViewer);
viewerPrev.addEventListener("click", () => navigateViewer(-1));
viewerNext.addEventListener("click", () => navigateViewer(1));
viewer.addEventListener("click", (event) => {
  if (event.target === viewer) closeViewer();
});
attachImage.addEventListener("click", attachCurrentImageToThreadComposer);
remixImage.addEventListener("click", toggleRemixPanel);
viewerImage.addEventListener("click", (event) => openViewerAnnotationComposer(currentImage, event));
selectionAttach.addEventListener("click", attachSelectedImagesToThreadComposer);
selectionDelete.addEventListener("click", deleteSelectedImages);
selectionClear.addEventListener("click", () => clearImageSelection());
selectionExportPrimary.addEventListener("click", openSelectedImages);
viewerExportPrimary.addEventListener("click", openCurrentImage);
fullscreenBoard?.addEventListener("click", requestFullscreenBoard);
selectionExportMenuTrigger.addEventListener("click", () => toggleExportMenu(exportSurfaces[0]));
viewerExportMenuTrigger.addEventListener("click", () => toggleExportMenu(exportSurfaces[1]));
generateMoreButton.addEventListener("click", () => {
  void generateMoreImages();
});
[...selectionExportMenuItems, ...viewerExportMenuItems].forEach((item) => {
  item.addEventListener("click", () => setExportTarget(item.dataset.exportTarget));
});
document.addEventListener("click", (event) => {
  if (!exportSurfaces.some((surface) => surface.root.contains(event.target))) closeExportMenus();
});
document.addEventListener("keydown", (event) => {
  if (event.key === "Escape") {
    if (activeAnnotationComposer) {
      closeAnnotationComposer();
      return;
    }
    const openSurface = openExportSurface();
    if (openSurface) {
      closeExportMenus();
      openSurface.trigger.focus({ preventScroll: true });
      return;
    }
    if (!viewer.classList.contains("active")) return;
    if (isRemixPanelOpen) {
      setRemixPanelOpen(false);
      remixImage.focus({ preventScroll: true });
      return;
    }
    closeViewer();
    return;
  }
  if (!viewer.classList.contains("active")) return;
  if (event.key === "ArrowLeft") {
    event.preventDefault();
    navigateViewer(-1);
  }
  if (event.key === "ArrowRight") {
    event.preventDefault();
    navigateViewer(1);
  }
});
window.addEventListener("resize", () => {
  if (viewer.classList.contains("active")) {
    if (isRemixPanelOpen) syncViewerRemixLayout();
    else syncViewerRemixToolbarClearance();
  }
  const nextColumnCount = Number.parseInt(getComputedStyle(feed).getPropertyValue("--columns"), 10) || 5;
  if (nextColumnCount !== activeColumnCount) {
    activeColumnCount = nextColumnCount;
    renderFeed();
  }
});
window.addEventListener("openai:set_globals", () => {
  updateFullscreenControl();
  const nextPayload = mcpWidgetPayload();
  if (nextPayload) {
    setBoardAppendTarget(nextPayload);
    if (shouldApplyMcpGlobalsPayload(nextPayload)) {
      applyMcpPayload(nextPayload);
      return;
    }
    startMcpBoardRefreshLoop();
  } else if (!mcpPayloadApplied) {
    applyMcpPayload();
    return;
  }
  notifyHostResize();
});

init();
