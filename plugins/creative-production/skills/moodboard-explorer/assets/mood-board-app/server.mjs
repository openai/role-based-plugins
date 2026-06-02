import { createHash, randomBytes } from "node:crypto";
import { execFile } from "node:child_process";
import { createReadStream } from "node:fs";
import fs from "node:fs/promises";
import http from "node:http";
import path from "node:path";
import { fileURLToPath } from "node:url";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const requestedPort = Number(process.env.PORT || 8794);
const maxPortAttempts = Number(process.env.CREATIVE_PRODUCTION_PORT_ATTEMPTS || 20);
let port = requestedPort;
const runToken = process.env.BV_RUN_TOKEN || randomBytes(24).toString("base64url");
const dataDir = path.join(__dirname, "data");
const runtimeConfigPath = path.join(dataDir, "runtime-config.json");
const runtimeConfig = await readRuntimeConfig();
const pluginRoot = process.env.CREATIVE_PRODUCTION_PLUGIN_ROOT || runtimeConfig.pluginRoot || "";
const codexExecRunner = process.env.CREATIVE_PRODUCTION_CODEX_EXEC_RUNNER || runtimeConfig.codexExecRunner || "";
const pythonBin = process.env.CREATIVE_PRODUCTION_PYTHON || "python3";
const codexBin = process.env.CREATIVE_PRODUCTION_CODEX_BIN || "codex";
const codexWorkspace = process.env.CREATIVE_PRODUCTION_WORKSPACE || runtimeConfig.codexWorkspace || __dirname;
const imageMaxConcurrency = positiveInteger(process.env.CREATIVE_PRODUCTION_IMAGE_MAX_CONCURRENCY, 64);
const imageBatchLimit = positiveInteger(process.env.CREATIVE_PRODUCTION_IMAGE_BATCH_LIMIT, 64);
const imageMaxAttempts = process.env.CREATIVE_PRODUCTION_IMAGE_MAX_ATTEMPTS || "2";
const baseImageTimeoutSeconds = 600;
const imageTimeoutScaleAfterCount = 12;
const imageTimeoutSecondsOverride = process.env.CREATIVE_PRODUCTION_IMAGE_TIMEOUT_SECONDS || "";
const imagePreflightTimeoutSeconds = process.env.CREATIVE_PRODUCTION_IMAGE_PREFLIGHT_TIMEOUT_SECONDS || "300";
const codexSandbox = process.env.CREATIVE_PRODUCTION_CODEX_SANDBOX || "workspace-write";
const generatedDir = path.join(__dirname, "generated");
const mcpPreviewDirName = "mcp-thumbs";
const mcpPreviewDir = path.join(generatedDir, mcpPreviewDirName);
const previewScriptPath = process.env.CREATIVE_PRODUCTION_PREVIEW_IMAGE_SCRIPT
  || (pluginRoot ? path.join(pluginRoot, "mcp", "scripts", "create_preview_image.py") : "");
const maxInlineDataUrlLength = 160000;
const jpegDataUrlPrefix = "data:image/jpeg;base64,";
const maxInlineJpegBytes = Math.floor((maxInlineDataUrlLength - jpegDataUrlPrefix.length) * 3 / 4);
const previewAttempts = [
  { maxEdge: 720, quality: 72 },
  { maxEdge: 560, quality: 66 },
  { maxEdge: 420, quality: 58 },
  { maxEdge: 320, quality: 50 },
];
const staticStreamPath = path.join(dataDir, "stream-static.json");
const staticHtmlPath = path.join(__dirname, "mood-board.html");
const runStatePath = path.join(__dirname, "run-state.json");
const latestActionPath = path.join(__dirname, "latest-action.json");
const pendingActionsPath = path.join(__dirname, "pending-actions.jsonl");
const generationJobs = new Map();
const clipboardCommand = process.env.CREATIVE_PRODUCTION_CLIPBOARD_COMMAND || "osascript";

function positiveInteger(value, fallback) {
  const parsed = Number(value);
  if (Number.isInteger(parsed) && parsed > 0) return parsed;
  return fallback;
}

function effectiveImageTimeoutSeconds(imageCount) {
  if (imageTimeoutSecondsOverride) return imageTimeoutSecondsOverride;
  const extraImages = Math.max(0, Number(imageCount) - imageTimeoutScaleAfterCount);
  const perExtraImageSeconds = baseImageTimeoutSeconds / imageTimeoutScaleAfterCount;
  return String(Math.ceil(baseImageTimeoutSeconds + extraImages * perExtraImageSeconds));
}

function generatedUrlToPath(imageUrl) {
  const cleanUrl = String(imageUrl || "").replace(/^\/+/, "");
  if (!cleanUrl.startsWith("generated/")) return "";
  const resolved = path.resolve(__dirname, cleanUrl);
  const generatedRoot = `${path.resolve(generatedDir)}${path.sep}`;
  return resolved.startsWith(generatedRoot) ? resolved : "";
}

function shouldCreateWidgetPreview(imageUrl) {
  const cleanUrl = String(imageUrl || "").replace(/^\/+/, "");
  if (!cleanUrl.startsWith("generated/")) return false;
  return !cleanUrl.startsWith(`generated/${mcpPreviewDirName}/`);
}

function isPreviewableImage(filePath) {
  return [".jpg", ".jpeg", ".png", ".webp"].includes(path.extname(filePath).toLowerCase());
}

async function readRuntimeConfig() {
  try {
    return JSON.parse(await fs.readFile(runtimeConfigPath, "utf8"));
  } catch (error) {
    if (error.code === "ENOENT") return {};
    throw error;
  }
}

await fs.mkdir(generatedDir, { recursive: true });

const mimeTypes = new Map([
  [".html", "text/html; charset=utf-8"],
  [".css", "text/css; charset=utf-8"],
  [".js", "text/javascript; charset=utf-8"],
  [".json", "application/json; charset=utf-8"],
  [".jpg", "image/jpeg"],
  [".jpeg", "image/jpeg"],
  [".png", "image/png"],
  [".svg", "image/svg+xml; charset=utf-8"],
  [".webp", "image/webp"]
]);

function corsHeaders(req) {
  const origin = req.headers.origin;
  const allowedOrigins = new Set([
    `http://127.0.0.1:${port}`,
    `http://localhost:${port}`,
  ]);
  if (!origin || !allowedOrigins.has(origin)) return {};
  return {
    "Access-Control-Allow-Origin": origin,
    "Access-Control-Allow-Headers": "content-type,x-bv-run-token",
    "Access-Control-Allow-Methods": "GET,POST,OPTIONS",
    "Vary": "Origin",
  };
}

function hostIsAllowed(req) {
  const host = req.headers.host;
  return !host || host === `127.0.0.1:${port}` || host === `localhost:${port}`;
}

function originIsAllowed(req) {
  const origin = req.headers.origin;
  return !origin || origin === `http://127.0.0.1:${port}` || origin === `http://localhost:${port}`;
}

function rejectUnsafeRequest(req, res) {
  if (!hostIsAllowed(req) || !originIsAllowed(req)) {
    sendJson(req, res, 403, { error: "Request origin is not allowed." });
    return true;
  }
  return false;
}

function requireRunToken(req, res) {
  if (req.headers["x-bv-run-token"] !== runToken) {
    sendJson(req, res, 403, { error: "Missing or invalid Creative Production run token." });
    return false;
  }
  return true;
}

function injectRunToken(html) {
  const script = `<script>window.BV_RUN_TOKEN=${JSON.stringify(runToken)};</script>`;
  if (html.includes("</head>")) return html.replace("</head>", `  ${script}\n</head>`);
  return `${script}\n${html}`;
}

function send(req, res, status, body, contentType = "text/plain; charset=utf-8") {
  res.writeHead(status, {
    "Content-Type": contentType,
    ...corsHeaders(req),
  });
  res.end(body);
}

function sendJson(req, res, status, body) {
  send(req, res, status, JSON.stringify(body), "application/json; charset=utf-8");
}

async function readJson(req) {
  let body = "";
  for await (const chunk of req) body += chunk;
  return JSON.parse(body || "{}");
}

async function fileExists(filePath) {
  try {
    await fs.access(filePath);
    return true;
  } catch {
    return false;
  }
}

function cacheName(item) {
  const key = createHash("sha256")
    .update(JSON.stringify({
      id: item.id,
      prompt: item.prompt
    }))
    .digest("hex")
    .slice(0, 32);
  return `${key}.png`;
}

function safeStem(value) {
  return String(value || "moodboard-image")
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, "-")
    .replace(/^-|-$/g, "")
    .slice(0, 48) || "moodboard-image";
}

async function createWidgetPreview(item, sourceImageUrl) {
  if (!shouldCreateWidgetPreview(sourceImageUrl)) return sourceImageUrl;
  const sourcePath = generatedUrlToPath(sourceImageUrl);
  if (!sourcePath || !isPreviewableImage(sourcePath)) return sourceImageUrl;
  if (!previewScriptPath || !(await fileExists(previewScriptPath)) || !(await fileExists(sourcePath))) {
    return sourceImageUrl;
  }

  const previewFilename = `${safeStem(item.id || item.title || path.basename(sourcePath, path.extname(sourcePath)))}.jpg`;
  const previewPath = path.join(mcpPreviewDir, previewFilename);
  const previewUrl = `/generated/${mcpPreviewDirName}/${previewFilename}`;
  const sourceStats = await fs.stat(sourcePath);
  const previewStats = await fs.stat(previewPath).catch(() => null);
  if (
    previewStats
    && previewStats.mtimeMs >= sourceStats.mtimeMs
    && previewStats.size > 0
    && previewStats.size <= maxInlineJpegBytes
  ) {
    return previewUrl;
  }

  await fs.mkdir(mcpPreviewDir, { recursive: true });
  let lastError = null;
  for (const attempt of previewAttempts) {
    try {
      await new Promise((resolve, reject) => {
        execFile(
          pythonBin,
          [
            previewScriptPath,
            sourcePath,
            previewPath,
            "--max-edge",
            String(attempt.maxEdge),
            "--quality",
            String(attempt.quality),
          ],
          (error) => {
            if (error) {
              reject(error);
              return;
            }
            resolve();
          }
        );
      });
      const stats = await fs.stat(previewPath);
      if (stats.size > 0 && stats.size <= maxInlineJpegBytes) return previewUrl;
    } catch (error) {
      lastError = error;
    }
  }
  if (lastError) throw lastError;
  throw new Error(`Widget preview remained too large for inline mood-board rendering: ${previewPath}`);
}

async function withWidgetPreview(item) {
  const imageUrl = String(item.imageUrl || "");
  if (!shouldCreateWidgetPreview(imageUrl)) return item;
  const previewUrl = await createWidgetPreview(item, imageUrl);
  if (previewUrl === imageUrl) return item;
  return {
    ...item,
    imageUrl: previewUrl,
    sourceImageUrl: imageUrl,
  };
}

function workerSlug(value) {
  return String(value || "image")
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, "-")
    .split("-")
    .filter(Boolean)
    .join("-")
    .slice(0, 80) || "image";
}

async function copyTextToClipboard(text) {
  const args = clipboardCommand === "osascript"
    ? ["-e", `set the clipboard to ${JSON.stringify(text)}`]
    : [text];
  await new Promise((resolve, reject) => {
    execFile(clipboardCommand, args, (error) => {
      if (error) {
        reject(error);
        return;
      }
      resolve();
    });
  });
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
    })
  };
}

async function writeStaticArtifacts(stream) {
  const staticStream = toStaticStream(stream);
  await fs.mkdir(dataDir, { recursive: true });
  await fs.writeFile(staticStreamPath, `${JSON.stringify(staticStream, null, 2)}\n`, "utf8");

  const indexHtml = await fs.readFile(path.join(__dirname, "index.html"), "utf8");
  const embeddedJson = JSON.stringify(staticStream).replace(/</g, "\\u003c");
  const staticHtml = indexHtml.replace(
    '  <script src="app.js"></script>',
    `  <script>window.MOODBOARD_STREAM = ${embeddedJson};</script>\n  <script src="app.js"></script>`
  );
  await fs.writeFile(staticHtmlPath, staticHtml, "utf8");
}

async function readStoredStream() {
  return JSON.parse(await fs.readFile(path.join(dataDir, "stream.json"), "utf8"));
}

function actionFilePrompt() {
  return `Continue the moodboard action saved at: ${latestActionPath}`;
}

function actionId(action) {
  const safeAction = safeStem(action || "moodboard-action");
  return `${new Date().toISOString().replace(/[:.]/g, "-")}-${safeAction}-${randomBytes(4).toString("hex")}`;
}

async function persistRunState(state = {}) {
  const payload = {
    ...state,
    updatedAt: new Date().toISOString(),
    paths: {
      runStatePath,
      latestActionPath,
      pendingActionsPath,
    },
    runDirectory: __dirname,
    streamPath: path.join(dataDir, "stream.json"),
    appUrl: `http://127.0.0.1:${port}/mood-board.html`,
  };
  await fs.writeFile(runStatePath, `${JSON.stringify(payload, null, 2)}\n`, "utf8");
  return payload;
}

async function readRunState() {
  if (await fileExists(runStatePath)) {
    return JSON.parse(await fs.readFile(runStatePath, "utf8"));
  }
  return await persistRunState({});
}

async function readLatestAction() {
  if (!(await fileExists(latestActionPath))) return null;
  return JSON.parse(await fs.readFile(latestActionPath, "utf8"));
}

async function stageAction(body = {}) {
  const action = String(body.action || "").trim();
  if (!action) {
    const error = new Error("Action staging requires an action.");
    error.statusCode = 400;
    throw error;
  }

  const runState = await persistRunState(body.state || {});
  const payload = {
    id: actionId(action),
    action,
    label: String(body.label || action),
    prompt: String(body.prompt || ""),
    createdAt: new Date().toISOString(),
    runStatePath,
    latestActionPath,
    pendingActionsPath,
    runDirectory: __dirname,
    streamPath: path.join(dataDir, "stream.json"),
    continuationPrompt: actionFilePrompt(),
    selection: body.selection || {},
    payload: body.payload || {},
  };

  await fs.writeFile(latestActionPath, `${JSON.stringify(payload, null, 2)}\n`, "utf8");
  await fs.appendFile(pendingActionsPath, `${JSON.stringify(payload)}\n`, "utf8");

  let copied = false;
  let copyError = "";
  try {
    await copyTextToClipboard(payload.continuationPrompt);
    copied = true;
  } catch (error) {
    copyError = error.message || "Could not copy continuation prompt.";
  }

  return {
    action: payload,
    runState,
    continuationPrompt: payload.continuationPrompt,
    runStatePath,
    latestActionPath,
    pendingActionsPath,
    copied,
    copyError,
  };
}

async function copyLatestActionPrompt() {
  const action = await readLatestAction();
  if (!action?.continuationPrompt) {
    const error = new Error("No staged mood board action is available.");
    error.statusCode = 404;
    throw error;
  }
  await copyTextToClipboard(action.continuationPrompt);
  return action;
}

function mergeUniqueItems(existingItems, nextItems) {
  const mergedItems = new Map((existingItems || []).map((item) => [item.id, item]));
  nextItems.forEach((item) => mergedItems.set(item.id, item));
  return [...mergedItems.values()];
}

async function persistGeneratedItems(items) {
  if (items.length === 0) return [];
  const widgetItems = await Promise.all(items.map((item) => withWidgetPreview(item)));
  const stream = await readStoredStream();
  const nextStream = {
    ...stream,
    items: mergeUniqueItems(stream.items, widgetItems)
  };
  await fs.writeFile(path.join(dataDir, "stream.json"), `${JSON.stringify(nextStream, null, 2)}\n`, "utf8");
  await writeStaticArtifacts(nextStream);
  return widgetItems;
}

function generationRequestSignature(images) {
  return createHash("sha256")
    .update(JSON.stringify(images.map((image) => ({
      id: image.id,
      prompt: image.prompt
    }))))
    .digest("hex");
}

function rememberGenerationJob(idempotencyKey, job) {
  generationJobs.set(idempotencyKey, job);
  while (generationJobs.size > 24) {
    generationJobs.delete(generationJobs.keys().next().value);
  }
}

async function generateImages(images) {
  const jobs = [];
  const cached = [];
  for (const item of images) {
    if (!item?.id || !item?.prompt) {
      throw new Error("Each image item needs an id and prompt.");
    }
    const filename = cacheName(item);
    const filePath = path.join(generatedDir, filename);
    if (await fileExists(filePath)) {
      cached.push({ id: item.id, url: `/generated/${filename}` });
    } else {
      jobs.push({ id: item.id, prompt: item.prompt, output: filename });
    }
  }

  const generated = jobs.length > 0 ? await runCodexExecBatch(jobs) : [];
  const byId = new Map([...cached, ...generated.filter((item) => item.url)].map((item) => [item.id, item]));
  const persistedItems = await persistGeneratedItems(images.flatMap((item) => {
    const result = byId.get(item.id);
    return result?.url ? [{ ...item, imageUrl: result.url }] : [];
  }));
  const persistedById = new Map(persistedItems.map((item) => [item.id, item]));
  await readStreamWithCachedImages();
  return {
    images: images.map((item) => {
      const result = byId.get(item.id);
      const persisted = persistedById.get(item.id);
      if (result?.url) {
        return {
          id: item.id,
          url: persisted?.imageUrl || result.url,
          sourceImageUrl: persisted?.sourceImageUrl || result.url,
        };
      }
      return {
        id: item?.id,
        error: result?.error || "Image generation failed."
      };
    })
  };
}

async function runCodexExecBatch(jobs) {
  if (!codexExecRunner) {
    const error = new Error(`Image generation is not configured. Missing ${runtimeConfigPath}.`);
    error.statusCode = 500;
    throw error;
  }
  if (!(await fileExists(codexExecRunner))) {
    const error = new Error(`Configured Codex exec runner does not exist: ${codexExecRunner}`);
    error.statusCode = 500;
    throw error;
  }
  const batchId = createHash("sha256").update(JSON.stringify(jobs)).digest("hex").slice(0, 16);
  const batchDir = path.join(generatedDir, ".codex-exec", batchId);
  await fs.mkdir(batchDir, { recursive: true });
  const jobFile = path.join(batchDir, "jobs.jsonl");
  await fs.writeFile(jobFile, `${jobs.map((job) => JSON.stringify(job)).join("\n")}\n`, "utf8");
  const effectiveImageMaxConcurrency = Math.min(jobs.length, imageMaxConcurrency);
  const imageTimeoutSeconds = effectiveImageTimeoutSeconds(jobs.length);

  const execResult = await new Promise((resolve) => {
    execFile(
      pythonBin,
      [
        codexExecRunner,
        "--input", jobFile,
        "--out-dir", batchDir,
        "--workspace", codexWorkspace,
        "--max-concurrency", String(effectiveImageMaxConcurrency),
        "--max-attempts", imageMaxAttempts,
        "--timeout-seconds", imageTimeoutSeconds,
        "--preflight-timeout-seconds", imagePreflightTimeoutSeconds,
        "--codex-bin", codexBin,
        "--sandbox", codexSandbox,
      ],
      { cwd: pluginRoot || process.cwd() },
      (error, stdout, stderr) => {
        resolve({ error, stdout, stderr });
      }
    );
  });

  const summaryPath = path.join(batchDir, "codex-exec-image-results.json");
  if (!(await fileExists(summaryPath))) {
    const recovered = await recoverExistingBatchImages(jobs, batchDir);
    if (recovered.some((item) => item.url)) return recovered;
    const message = execResult.stderr || execResult.stdout || execResult.error?.message || "Image generation failed before writing a batch summary.";
    throw new Error(message);
  }
  const summary = JSON.parse(await fs.readFile(summaryPath, "utf8"));
  return await Promise.all((summary.results || []).map(async (result) => {
    if (result.status !== "complete" || !result.image_path) {
      return { id: result.id, error: result.error || "Image generation failed." };
    }
    const job = jobs.find((item) => item.id === result.id);
    const filename = job?.output || path.basename(result.image_path);
    await fs.copyFile(result.image_path, path.join(generatedDir, filename));
    return { id: result.id, url: `/generated/${filename}` };
  }));
}

async function recoverExistingBatchImages(jobs, batchDir) {
  return await Promise.all(jobs.map(async (job) => {
    const expectedPath = path.join(batchDir, job.output);
    if (await fileExists(expectedPath)) {
      const filename = job.output;
      await fs.copyFile(expectedPath, path.join(generatedDir, filename));
      return { id: job.id, url: `/generated/${filename}` };
    }

    const workerRoot = path.join(batchDir, "workers", workerSlug(job.id));
    for (let attempt = Number(imageMaxAttempts) || 1; attempt >= 1; attempt -= 1) {
      const imagePath = path.join(workerRoot, `attempt-${attempt}`, "image.png");
      if (await fileExists(imagePath)) {
        const filename = job.output;
        await fs.copyFile(imagePath, path.join(generatedDir, filename));
        return { id: job.id, url: `/generated/${filename}` };
      }
    }

    return { id: job.id, error: "Image generation failed before writing a batch summary." };
  }));
}

async function generateImagesIdempotently(idempotencyKey, images) {
  const signature = generationRequestSignature(images);
  const existingJob = generationJobs.get(idempotencyKey);
  if (existingJob) {
    if (existingJob.signature !== signature) {
      const error = new Error("Idempotency key was reused for a different image batch.");
      error.statusCode = 409;
      throw error;
    }
    return await existingJob.promise;
  }

  const promise = generateImages(images).catch((error) => {
    generationJobs.delete(idempotencyKey);
    throw error;
  });
  rememberGenerationJob(idempotencyKey, { signature, promise });
  return await promise;
}

async function readStreamWithCachedImages() {
  const stream = await readStoredStream();
  stream.items = await Promise.all(stream.items.map(async (item) => {
    const filename = cacheName(item);
    const filePath = path.join(generatedDir, filename);
    if (await fileExists(filePath)) {
      return await withWidgetPreview({
        ...item,
        imageUrl: item.sourceImageUrl || `/generated/${filename}`,
      });
    }
    return item;
  }));
  await fs.writeFile(path.join(dataDir, "stream.json"), `${JSON.stringify(stream, null, 2)}\n`, "utf8");
  await writeStaticArtifacts(stream);
  return stream;
}

async function serveFile(req, res, pathname) {
  const normalized = pathname === "/" ? "/index.html" : pathname;
  const safePath = path.normalize(normalized).replace(/^(\.\.[/\\])+/, "");
  const filePath = path.join(__dirname, safePath);

  if (!filePath.startsWith(__dirname) || !(await fileExists(filePath))) {
    send(req, res, 404, "Not found");
    return;
  }

  const ext = path.extname(filePath);
  if (ext === ".html") {
    send(req, res, 200, injectRunToken(await fs.readFile(filePath, "utf8")), mimeTypes.get(ext));
    return;
  }

  res.writeHead(200, {
    "Content-Type": mimeTypes.get(ext) || "application/octet-stream",
    "Cache-Control": normalized.startsWith("/generated/") ? "public, max-age=31536000, immutable" : "no-cache",
    ...corsHeaders(req),
  });
  createReadStream(filePath).pipe(res);
}

const server = http.createServer(async (req, res) => {
  try {
    if (req.method === "OPTIONS") {
      if (rejectUnsafeRequest(req, res)) return;
      sendJson(req, res, 204, {});
      return;
    }

    const url = new URL(req.url, `http://127.0.0.1:${port}`);

    if (rejectUnsafeRequest(req, res)) return;

    if (req.method === "GET" && url.pathname === "/api/stream") {
      sendJson(req, res, 200, await readStreamWithCachedImages());
      return;
    }

    if (req.method === "GET" && url.pathname === "/api/session") {
      sendJson(req, res, 200, {
        runToken,
        runDirectory: __dirname,
        streamPath: path.join(dataDir, "stream.json"),
      });
      return;
    }

    if (req.method === "GET" && url.pathname === "/api/state") {
      sendJson(req, res, 200, await readRunState());
      return;
    }

    if (req.method === "POST" && url.pathname === "/api/state") {
      if (!requireRunToken(req, res)) return;
      const body = await readJson(req);
      const runState = await persistRunState(body.state || {});
      sendJson(req, res, 200, { saved: true, runStatePath, runState });
      return;
    }

    if (req.method === "POST" && url.pathname === "/api/actions") {
      if (!requireRunToken(req, res)) return;
      const body = await readJson(req);
      sendJson(req, res, 200, { saved: true, ...(await stageAction(body)) });
      return;
    }

    if (req.method === "GET" && url.pathname === "/api/actions/latest") {
      if (!requireRunToken(req, res)) return;
      const action = await readLatestAction();
      sendJson(req, res, 200, { action, hasAction: Boolean(action) });
      return;
    }

    if (req.method === "POST" && url.pathname === "/api/actions/copy-latest") {
      if (!requireRunToken(req, res)) return;
      const action = await copyLatestActionPrompt();
      sendJson(req, res, 200, { copied: true, action, continuationPrompt: action.continuationPrompt });
      return;
    }

    if (req.method === "POST" && url.pathname === "/api/images") {
      if (!requireRunToken(req, res)) return;
      const body = await readJson(req);
      if (body.confirmGenerate !== true) {
        sendJson(req, res, 400, { error: "Image generation requires confirmGenerate: true." });
        return;
      }
      const images = Array.isArray(body.images) ? body.images.slice(0, imageBatchLimit) : [];
      if (images.length === 0) {
        sendJson(req, res, 400, { error: "Expected an images array." });
        return;
      }
      const idempotencyKey = String(body.idempotencyKey || "").trim();
      if (!idempotencyKey) {
        sendJson(req, res, 400, { error: "Image generation requires an idempotencyKey." });
        return;
      }

      const payload = await generateImagesIdempotently(idempotencyKey, images);
      sendJson(req, res, 200, { idempotencyKey, ...payload });
      return;
    }

    if (req.method === "GET") {
      await serveFile(req, res, url.pathname);
      return;
    }

    send(req, res, 405, "Method not allowed");
  } catch (error) {
    sendJson(req, res, error.statusCode || 500, { error: error.message || "Unknown server error." });
  }
});

function logReady() {
  console.log(`For You Stream: http://127.0.0.1:${port}`);
  console.log(codexExecRunner
    ? `Image generation: Codex exec fanout via ${codexExecRunner}`
    : `Image generation: missing ${runtimeConfigPath}`);
}

function listenWithFallback(nextPort = requestedPort, remaining = maxPortAttempts) {
  port = nextPort;
  server.once("error", (error) => {
    if (error.code === "EADDRINUSE" && !process.env.PORT && remaining > 0) {
      console.log(`Port ${port} is occupied; trying ${port + 1}.`);
      listenWithFallback(port + 1, remaining - 1);
      return;
    }
    console.error(error);
    process.exitCode = 1;
  });
  server.listen(port, "127.0.0.1", logReady);
}

listenWithFallback();
