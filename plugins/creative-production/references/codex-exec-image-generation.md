# Codex Exec Image Generation

Creative Production image generation uses Codex exec fanout. Do not ask users for credentials and do not call direct image API endpoints from plugin code.

## Runtime Contract

Generation code writes a JSONL job file where each row includes:

- `id`: stable item id for status and retries.
- `prompt`: the exact prompt for one image.
- `output` or `out`: final PNG filename under the requested output directory.
- optional metadata such as route, group, title, source, size, or quality.

Then call `runtime/codex_exec_image_batch.py` with:

```bash
python3 plugins/creative-production/runtime/codex_exec_image_batch.py \
  --input /path/to/jobs.jsonl \
  --out-dir /path/to/output \
  --workspace /path/to/workspace \
  --max-concurrency 64 \
  --max-attempts 2 \
  --timeout-seconds 600 \
  --preflight-timeout-seconds 300 \
  --poll-interval 0.5
```

The runner starts one `codex exec` preflight before fanout, then starts isolated `codex exec` workers. The preflight has its own timeout, defaulting to 300 seconds, and the parent writes the preflight marker after parsing the child process response. Each worker uses the native `image_gen.imagegen` tool, writes `image.png` and `result.json`, and the parent copies completed images to the requested output names. The parent writes `codex-exec-image-results.json` after every state change so stalled or failed runs can be inspected.

## Behavior

- Default fanout is one worker per uncached requested image, capped at 64 concurrent workers, with 2 attempts, 600 seconds per attempt, and 0.5 second parent polling.
- The preflight returns a small JSON object and aborts before image workers launch if Codex cannot initialize in the current sandbox.
- Worker sessions default to a fast image-worker path: low reasoning effort, approval requests allowed only for sandbox escalation or required file access, ephemeral sessions, ignored user config/plugin loading, ignored execpolicy rules, colorless logs, and a short prompt for prompt-only jobs without source images. Source-image jobs keep the fuller preservation prompt.
- A timeout terminates the worker and retries until attempts are exhausted.
- The final status file is authoritative for complete, failed, and pending items.
- Prompt-only generation is the canonical path. Source images may be copied into output folders and included as metadata, but the plugin must not retain image-edit API calls as a hidden fallback.

## Worker Preflight

The default-on preflight catches runtime initialization failures before spawning a 12-64 worker image batch. It uses the same `--workspace`, `--sandbox`, `--codex-bin`, and worker startup settings as the real workers, but it does not generate an image. It may use only the minimal tools needed to verify local CLI state and write its response, and it should request escalation/outside-sandbox approval immediately when local CLI state or required file writes are blocked by sandbox permissions.

If the preflight reports `readonly database`, `failed to initialize state runtime`, `failed to initialize in-process app-server client`, or `Operation not permitted` while touching `~/.codex`, treat it as a runtime access issue, not a prompt or image-generation issue. Request escalated/outside-sandbox execution for the local generation server and retry the same approved batch with a new idempotency key. Use `--no-preflight` only for local debugging after the worker environment has already been verified.

## Codex Exec Child Process Rule

When launching `codex exec` from any long-running local server, batch runner, or MCP-backed generation path, never let the child inherit an interactive or open parent stdin.

Always launch `codex exec` with stdin closed or redirected to `/dev/null`. A healthy preflight should complete quickly once it receives EOF. If a preflight appears to hang with no marker files and no stderr, first suspect inherited stdin, not slow model startup or prompt quality.

Required behavior:

- Python `subprocess.run(...)`: pass `stdin=subprocess.DEVNULL`.
- Python `subprocess.Popen(...)`: pass `stdin=subprocess.DEVNULL`.
- Node `execFile(...)` wrappers around Python runners: prefer the Python runner enforcing stdin for its own `codex exec` children.
- Do not treat preflight timeout increases as the first recovery step for no-output hangs.
- Only use `--no-preflight` after an equivalent direct preflight command has completed successfully.

## Local App Servers

Mood board, logo, and style local servers should keep their existing review endpoints but route generation through the same runner. Use these environment overrides only when needed:

- `CREATIVE_PRODUCTION_CODEX_EXEC_RUNNER`
- `CREATIVE_PRODUCTION_PYTHON`
- `CREATIVE_PRODUCTION_CODEX_BIN`
- `CREATIVE_PRODUCTION_WORKSPACE`
- `CREATIVE_PRODUCTION_IMAGE_BATCH_LIMIT`
- `CREATIVE_PRODUCTION_IMAGE_MAX_CONCURRENCY`
- `CREATIVE_PRODUCTION_IMAGE_MAX_ATTEMPTS`
- `CREATIVE_PRODUCTION_IMAGE_TIMEOUT_SECONDS`
- `CREATIVE_PRODUCTION_IMAGE_PREFLIGHT_TIMEOUT_SECONDS`
- `CREATIVE_PRODUCTION_CODEX_SANDBOX`

Batch large mood-board requests in chunks of 64 or fewer images per server request; send 64 or fewer approved images in one request, and for larger approved runs, chunk them into groups of 64. Treat the user-approved generation scope for the turn, not the transport batch size, as the approval unit. The mood-board server persists completed outputs into the same saved `runDirectory` and `data/stream.json`; existing inline boards should refresh from that saved run. Use `append_moodboard_board_items` only for externally generated items that were not already persisted by the mood-board server, and do not render a second inline board unless the original board is unavailable or stale. Reduce the request size only after a concrete worker failure, timeout, or transport error.

Mood-board server default timeout budgeting is 300 seconds for preflight and 600 seconds for real image generation up to 12 images. For batches above 12 images, the server adds a proportional 50 seconds per additional image unless `CREATIVE_PRODUCTION_IMAGE_TIMEOUT_SECONDS` is explicitly set.
