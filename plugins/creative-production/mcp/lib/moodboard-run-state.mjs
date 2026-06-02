import { createHash } from "node:crypto";
import { execFile } from "node:child_process";
import { copyFile, mkdir, readFile, stat, writeFile } from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { promisify } from "node:util";

const execFileAsync = promisify(execFile);
const PREVIEW_MAX_EDGE = 720;
const PREVIEW_JPEG_QUALITY = 72;
const PREVIEW_DIR = "mcp-thumbs";
const MAX_INLINE_DATA_URL_LENGTH = 160_000;
const JPEG_DATA_URL_PREFIX = "data:image/jpeg;base64,";
const MAX_INLINE_JPEG_BYTES = Math.floor(
  (MAX_INLINE_DATA_URL_LENGTH - JPEG_DATA_URL_PREFIX.length) * 3 / 4,
);
const PREVIEW_ATTEMPTS = [
  { maxEdge: PREVIEW_MAX_EDGE, quality: PREVIEW_JPEG_QUALITY },
  { maxEdge: 560, quality: 66 },
  { maxEdge: 420, quality: 58 },
  { maxEdge: 320, quality: 50 },
];
const PREVIEW_SCRIPT = path.resolve(
  path.dirname(fileURLToPath(import.meta.url)),
  "../scripts/create_preview_image.py",
);

const imageMimeTypes = new Map([
  [".jpg", "image/jpeg"],
  [".jpeg", "image/jpeg"],
  [".png", "image/png"],
  [".svg", "image/svg+xml"],
  [".webp", "image/webp"],
]);

export async function loadMoodboardRunSnapshot(input = {}, options = {}) {
  const {
    inlineImages = true,
    offset = 0,
    limit = Number.POSITIVE_INFINITY,
  } = options;
  const runDirectory = inferRunDirectory(input);
  if (!runDirectory) return null;

  const streamPath = resolveRunPath(runDirectory, input.streamPath || "data/stream.json");
  const runStatePath = resolveRunPath(runDirectory, input.runStatePath || "run-state.json");
  const latestActionPath = resolveRunPath(runDirectory, input.latestActionPath || "latest-action.json");

  const [stream, runState, latestAction] = await Promise.all([
    readJsonIfExists(streamPath),
    readJsonIfExists(runStatePath),
    readJsonIfExists(latestActionPath),
  ]);

  const sourceItems = Array.isArray(stream?.items) && stream.items.length
    ? stream.items
    : Array.isArray(runState?.items) && runState.items.length
      ? runState.items
      : [];

  const startIndex = Math.max(Number(offset) || 0, 0);
  const pageLimit = Number.isFinite(Number(limit)) ? Math.max(Number(limit) || 0, 0) : Number.POSITIVE_INFINITY;
  const pageItems = sourceItems.slice(startIndex, startIndex + pageLimit);

  return {
    runDirectory,
    streamPath,
    runStatePath,
    latestActionPath,
    stream,
    runState,
    latestAction,
    totalItemCount: sourceItems.length,
    offset: startIndex,
    limit: pageLimit,
    items: await Promise.all(pageItems.map((item) => localizeMoodboardItem(runDirectory, item, { inlineImages }))),
  };
}

export async function appendMoodboardRunItems(input = {}) {
  const runDirectory = inferRunDirectory(input);
  if (!runDirectory) throw new Error("A runDirectory is required to append mood-board images.");

  const streamPath = resolveRunPath(runDirectory, input.streamPath || "data/stream.json");
  const runStatePath = resolveRunPath(runDirectory, input.runStatePath || "run-state.json");
  const latestActionPath = resolveRunPath(runDirectory, input.latestActionPath || "latest-action.json");
  const stream = await readJsonIfExists(streamPath) || { meta: {}, items: [] };
  const existingItems = Array.isArray(stream.items) ? stream.items : [];
  const incomingItems = Array.isArray(input.items) ? input.items.filter((item) => item?.id) : [];
  if (incomingItems.length === 0) {
    throw new Error("At least one mood-board item with an id is required.");
  }

  const normalizedItems = await Promise.all(
    incomingItems.map((item) => normalizeAppendedItemImage(runDirectory, item)),
  );
  const mergedItems = mergeItemsById(existingItems, normalizedItems);
  const nextStream = {
    ...stream,
    items: mergedItems,
  };
  await mkdir(path.dirname(streamPath), { recursive: true });
  await writeFile(streamPath, `${JSON.stringify(nextStream, null, 2)}\n`, "utf8");
  await writeStaticStreamIfPresent(streamPath, nextStream);

  const appendedItemIds = normalizedItems.map((item) => String(item.id));
  const runState = await syncRunStateAfterAppend({
    runDirectory,
    runStatePath,
    streamPath,
    latestActionPath,
    mergedItems,
    appendedItemIds,
  });

  const latestAction = appendLatestAction({
    input,
    runDirectory,
    streamPath,
    runStatePath,
    latestActionPath,
    appendedItemIds,
    itemCount: mergedItems.length,
  });
  await writeFile(latestActionPath, `${JSON.stringify(latestAction, null, 2)}\n`, "utf8");

  return {
    runDirectory,
    streamPath,
    runStatePath,
    latestActionPath,
    latestAction,
    appendedItemIds,
    appendedCount: normalizedItems.length,
    itemCount: mergedItems.length,
    stream: nextStream,
    runState,
  };
}

export async function loadMoodboardRunStatus(input = {}) {
  const runDirectory = inferRunDirectory(input);
  if (!runDirectory) return null;

  const streamPath = resolveRunPath(runDirectory, input.streamPath || "data/stream.json");
  const latestActionPath = resolveRunPath(runDirectory, input.latestActionPath || "latest-action.json");
  const [stream, latestAction] = await Promise.all([
    readJsonIfExists(streamPath),
    readJsonIfExists(latestActionPath),
  ]);
  const items = Array.isArray(stream?.items) ? stream.items : [];
  const itemIds = items.map((item) => String(item.id || "")).filter(Boolean);
  const latestActionId = String(latestAction?.id || "");
  const latestActionTimestamp = String(latestAction?.createdAt || latestAction?.timestamp || "");
  const streamVersion = createHash("sha256")
    .update(JSON.stringify({ itemIds, latestActionId, latestActionTimestamp }))
    .digest("hex")
    .slice(0, 16);

  return {
    runDirectory,
    streamPath,
    latestActionPath,
    totalItemCount: items.length,
    itemIds,
    streamVersion,
    latestAction,
  };
}

function inferRunDirectory(input) {
  if (input.runDirectory) return path.resolve(String(input.runDirectory));
  if (input.streamPath) {
    const streamPath = path.resolve(String(input.streamPath));
    return path.basename(path.dirname(streamPath)) === "data"
      ? path.dirname(path.dirname(streamPath))
      : path.dirname(streamPath);
  }
  if (input.runStatePath) return path.dirname(path.resolve(String(input.runStatePath)));
  if (input.latestActionPath) return path.dirname(path.resolve(String(input.latestActionPath)));
  return "";
}

function resolveRunPath(runDirectory, filePath) {
  const resolved = path.isAbsolute(String(filePath))
    ? path.resolve(String(filePath))
    : path.resolve(runDirectory, String(filePath));
  if (resolved !== runDirectory && !resolved.startsWith(`${runDirectory}${path.sep}`)) {
    throw new Error(`Moodboard path escapes the run directory: ${filePath}`);
  }
  return resolved;
}

async function readJsonIfExists(filePath) {
  try {
    return JSON.parse(await readFile(filePath, "utf8"));
  } catch (error) {
    if (error.code === "ENOENT") return null;
    throw error;
  }
}

function safeItemStem(value) {
  return String(value || "moodboard-image")
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, "-")
    .replace(/^-|-$/g, "")
    .slice(0, 64) || "moodboard-image";
}

function isRunLocalGeneratedImage(imageUrl) {
  return imageUrl.startsWith("/generated/") || imageUrl.startsWith("generated/");
}

async function normalizeAppendedItemImage(runDirectory, item = {}) {
  const id = String(item.id || "").trim();
  const imageUrl = String(item.imageUrl || "").trim();
  const sourceImageUrl = String(item.sourceImageUrl || "").trim();
  const pathValue = String(item.path || "").trim();
  const urlValue = String(item.url || "").trim();
  const selectedImageUrl = sourceImageUrl || imageUrl || urlValue || pathValue;
  const localImagePath = [sourceImageUrl, imageUrl, pathValue, urlValue].find((value) => value && path.isAbsolute(value));

  if (!id) {
    return {
      ...item,
      id,
      imageUrl: selectedImageUrl,
    };
  }

  if (isRunLocalGeneratedImage(selectedImageUrl)) {
    const normalized = await normalizeRunLocalGeneratedItem(runDirectory, item, selectedImageUrl);
    if (pathValue && path.isAbsolute(pathValue)) delete normalized.path;
    if (urlValue && path.isAbsolute(urlValue)) delete normalized.url;
    return normalized;
  }

  if (!localImagePath) {
    return {
      ...item,
      id,
      imageUrl: selectedImageUrl,
    };
  }

  const resolvedLocalImagePath = resolveRunPath(runDirectory, localImagePath);
  const extension = path.extname(resolvedLocalImagePath).toLowerCase() || ".png";
  const generatedDir = path.join(runDirectory, "generated");
  const generatedPath = path.join(generatedDir, `${safeItemStem(id)}${extension}`);
  await mkdir(generatedDir, { recursive: true });
  if (path.resolve(resolvedLocalImagePath) !== path.resolve(generatedPath)) {
    await copyFile(resolvedLocalImagePath, generatedPath);
  }

  const normalized = await normalizeRunLocalGeneratedItem(runDirectory, {
    ...item,
    id,
  }, `/generated/${path.basename(generatedPath)}`);
  if (pathValue && path.isAbsolute(pathValue)) delete normalized.path;
  if (urlValue && path.isAbsolute(urlValue)) delete normalized.url;
  return normalized;
}

async function normalizeRunLocalGeneratedItem(runDirectory, item, sourceImageUrl) {
  const normalizedSourceImageUrl = sourceImageUrl.startsWith("/")
    ? sourceImageUrl
    : `/${sourceImageUrl}`;
  const previewImageUrl = await previewImageUrlForWidget(runDirectory, item, normalizedSourceImageUrl);
  if (previewImageUrl === normalizedSourceImageUrl) {
    return {
      ...item,
      imageUrl: normalizedSourceImageUrl,
    };
  }
  return {
    ...item,
    imageUrl: previewImageUrl,
    previewImageUrl,
    sourceImageUrl: normalizedSourceImageUrl,
  };
}

async function writeStaticStreamIfPresent(streamPath, stream) {
  if (path.basename(streamPath) !== "stream.json") return;
  const staticStreamPath = path.join(path.dirname(streamPath), "stream-static.json");
  if (staticStreamPath === streamPath) return;
  try {
    await stat(staticStreamPath);
  } catch (error) {
    if (error.code === "ENOENT") return;
    throw error;
  }
  await writeFile(staticStreamPath, `${JSON.stringify(toStaticStream(stream), null, 2)}\n`, "utf8");
}

function toStaticStream(stream) {
  return {
    ...stream,
    items: (stream.items || []).map((item) => {
      const nextItem = { ...item };
      for (const key of ["imageUrl", "previewImageUrl", "sourceImageUrl"]) {
        if (typeof nextItem[key] === "string" && nextItem[key].startsWith("/")) {
          nextItem[key] = nextItem[key].slice(1);
        }
      }
      return nextItem;
    }),
  };
}

function appendLatestAction({ input, runDirectory, streamPath, runStatePath, latestActionPath, appendedItemIds, itemCount }) {
  const idempotencyKey = String(input.idempotencyKey || input.sourceActionId || appendedItemIds.join("-") || "append");
  const id = `append-${safeItemStem(idempotencyKey)}`;
  const timestamp = new Date().toISOString();
  return {
    id,
    action: "append_moodboard_board_items",
    label: "Appended mood-board images",
    createdAt: timestamp,
    timestamp,
    sourceActionId: String(input.sourceActionId || ""),
    idempotencyKey,
    appendedItemIds,
    appendedCount: appendedItemIds.length,
    itemCount,
    runDirectory,
    streamPath,
    runStatePath,
    latestActionPath,
  };
}

async function syncRunStateAfterAppend({
  runDirectory,
  runStatePath,
  streamPath,
  latestActionPath,
  mergedItems,
  appendedItemIds,
}) {
  const existingState = await readJsonIfExists(runStatePath) || {};
  const itemIds = mergedItems.map((item) => String(item.id || "")).filter(Boolean);
  const itemIdSet = new Set(itemIds);
  const hiddenImageIds = Array.isArray(existingState.hiddenImageIds)
    ? existingState.hiddenImageIds.map(String).filter((id) => itemIdSet.has(id))
    : [];
  const hiddenIdSet = new Set(hiddenImageIds);
  const selectedImageIds = Array.isArray(existingState.selectedImageIds)
    ? existingState.selectedImageIds.map(String).filter((id) => itemIdSet.has(id))
    : [];
  const visibleItemIds = itemIds.filter((id) => !hiddenIdSet.has(id));
  const currentImageId = itemIdSet.has(String(existingState.currentImageId || ""))
    ? String(existingState.currentImageId)
    : lastExistingId(appendedItemIds, itemIdSet) || lastExistingId(itemIds, itemIdSet) || "";
  const timestamp = new Date().toISOString();
  const runState = {
    ...existingState,
    version: Number(existingState.version || 1),
    runDirectory,
    streamPath,
    runStatePath,
    latestActionPath,
    paths: {
      ...(existingState.paths && typeof existingState.paths === "object" ? existingState.paths : {}),
      streamPath,
      runStatePath,
      latestActionPath,
    },
    itemCount: mergedItems.length,
    items: mergedItems,
    visibleItemIds,
    hiddenImageIds,
    selectedImageIds,
    currentImageId,
    appendedItemIds,
    updatedAt: timestamp,
  };
  await mkdir(path.dirname(runStatePath), { recursive: true });
  await writeFile(runStatePath, `${JSON.stringify(runState, null, 2)}\n`, "utf8");
  return runState;
}

function lastExistingId(ids, itemIdSet) {
  for (let index = ids.length - 1; index >= 0; index -= 1) {
    const id = String(ids[index] || "");
    if (itemIdSet.has(id)) return id;
  }
  return "";
}

function mergeItemsById(existingItems, incomingItems) {
  const mergedItems = new Map((existingItems || []).map((item) => [String(item.id), item]));
  incomingItems.forEach((item) => {
    const id = String(item.id || "").trim();
    if (!id) return;
    mergedItems.set(id, {
      ...(mergedItems.get(id) || {}),
      ...item,
      id,
    });
  });
  return [...mergedItems.values()];
}

async function localizeMoodboardItem(runDirectory, item = {}, { inlineImages = true } = {}) {
  const imageUrl = String(item.imageUrl || item.url || item.path || "");
  const displayImageUrl = inlineImages
    ? await previewImageUrlForWidget(runDirectory, item, imageUrl)
    : imageUrl;
  const widgetImageUrl = inlineImages ? await imageUrlForWidget(runDirectory, displayImageUrl) : imageUrl;
  const localized = {
    ...item,
    imageUrl: widgetImageUrl,
  };
  if (displayImageUrl !== imageUrl) {
    localized.sourceImageUrl = imageUrl;
    if (!inlineImages) localized.previewImageUrl = displayImageUrl;
  }
  if (inlineImages && imageUrl && !widgetImageUrl) {
    localized.imageError = "Image could not be inlined for the MCP mood-board widget.";
    localized.sourceImageUrl = localized.sourceImageUrl || imageUrl;
  }
  return localized;
}

async function previewImageUrlForWidget(runDirectory, item, imageUrl) {
  if (!isRunLocalGeneratedImage(imageUrl) || imageUrl.includes(`/${PREVIEW_DIR}/`)) return imageUrl;
  const sourcePath = resolveRunPath(runDirectory, imageUrl.replace(/^\/+/, ""));
  const extension = path.extname(sourcePath).toLowerCase();
  if (!imageMimeTypes.has(extension) || extension === ".svg") return imageUrl;

  const previewPath = path.join(runDirectory, "generated", PREVIEW_DIR, `${safeItemStem(item.id || item.title)}.jpg`);
  try {
    const [sourceStats, previewStats] = await Promise.all([
      stat(sourcePath),
      stat(previewPath).catch(() => null),
    ]);
    if (
      !previewStats
      || previewStats.mtimeMs < sourceStats.mtimeMs
      || previewStats.size === 0
      || previewStats.size > MAX_INLINE_JPEG_BYTES
    ) {
      await createPreviewImageForInlineWidget(sourcePath, previewPath);
    }
    return `/generated/${PREVIEW_DIR}/${path.basename(previewPath)}`;
  } catch {
    return imageUrl;
  }
}

async function createPreviewImageForInlineWidget(sourcePath, previewPath) {
  let lastError = null;
  for (const attempt of PREVIEW_ATTEMPTS) {
    try {
      await createPreviewImage(sourcePath, previewPath, attempt);
      const previewStats = await stat(previewPath);
      if (previewStats.size <= MAX_INLINE_JPEG_BYTES) return;
    } catch (error) {
      lastError = error;
    }
  }
  if (lastError) throw lastError;
}

async function createPreviewImage(sourcePath, previewPath, { maxEdge, quality }) {
  await execFileAsync(
    process.env.CREATIVE_PRODUCTION_PYTHON || "python3",
    [
      PREVIEW_SCRIPT,
      sourcePath,
      previewPath,
      "--max-edge",
      String(maxEdge),
      "--quality",
      String(quality),
    ],
  );
}

async function imageUrlForWidget(runDirectory, imageUrl) {
  if (!imageUrl) return imageUrl;
  if (imageUrl.startsWith("data:")) {
    return imageUrl.length <= MAX_INLINE_DATA_URL_LENGTH ? imageUrl : "";
  }
  if (/^https?:/i.test(imageUrl) || imageUrl.startsWith("blob:")) {
    return imageUrl;
  }

  const filePath = resolveRunPath(runDirectory, imageUrl.replace(/^\/+/, ""));
  const extension = path.extname(filePath).toLowerCase();
  const mimeType = imageMimeTypes.get(extension) || "application/octet-stream";
  const bytes = await readFile(filePath);
  const dataUrl = `data:${mimeType};base64,${bytes.toString("base64")}`;
  return dataUrl.length <= MAX_INLINE_DATA_URL_LENGTH ? dataUrl : "";
}
