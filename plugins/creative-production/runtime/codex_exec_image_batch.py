#!/usr/bin/env python3
"""Generate image batches by delegating one prompt per ``codex exec`` worker."""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

RESULT_FILE = "result.json"
IMAGE_FILE = "image.png"
LAST_MESSAGE_FILE = "last-message.txt"
STDOUT_FILE = "stdout.log"
STDERR_FILE = "stderr.log"
STATE_FILE = "state.json"
TERMINAL_STATES = {"complete", "failed"}
PREFLIGHT_FILE = "preflight-result.json"
PREFLIGHT_DEFAULT_TIMEOUT_SECONDS = 300
WORKER_DEFAULT_TIMEOUT_SECONDS = 600
PREFLIGHT_ERROR_HINTS = (
    "readonly database",
    "failed to initialize state runtime",
    "failed to initialize in-process app-server client",
    "operation not permitted",
)
SOURCE_IMAGE_KEYS = {
    "base_asset",
    "base_asset_path",
    "filePath",
    "file_path",
    "imagePath",
    "image_path",
    "localPath",
    "local_path",
    "sourcePath",
    "source_path",
}
SOURCE_CONTAINER_KEYS = {
    "baseAsset",
    "reference",
    "referenceImage",
    "referenceImages",
    "source",
    "sourceImage",
    "sourceImages",
}


@dataclass(frozen=True)
class Job:
    id: str
    prompt: str
    output: str
    context: dict[str, Any]


@dataclass
class RunningWorker:
    job: Job
    attempt: int
    item_dir: Path
    process: subprocess.Popen[str]
    started_at: float


def slugify(value: str) -> str:
    slug = "".join(char.lower() if char.isalnum() else "-" for char in value)
    return "-".join(part for part in slug.split("-") if part)[:80] or "image"


def load_jobs(path: Path) -> list[Job]:
    jobs: list[Job] = []
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        payload = json.loads(line)
        prompt = str(payload.get("prompt") or "").strip()
        output = str(payload.get("output") or payload.get("out") or "").strip()
        job_id = str(
            payload.get("id") or payload.get("item_id") or payload.get("shot_id") or output
        ).strip()
        if not job_id or not prompt or not output:
            raise ValueError(f"Job line {line_number} needs id, prompt, and output.")
        context = {
            key: value
            for key, value in payload.items()
            if key not in {"id", "item_id", "shot_id", "prompt", "output", "out"}
        }
        jobs.append(Job(id=job_id, prompt=prompt, output=output, context=context))
    return jobs


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def collect_source_image_paths(value: Any) -> list[str]:
    paths: list[str] = []
    if isinstance(value, dict):
        for key, nested in value.items():
            if key in SOURCE_IMAGE_KEYS and isinstance(nested, str) and nested.strip():
                paths.append(nested.strip())
            elif key in SOURCE_CONTAINER_KEYS:
                paths.extend(collect_source_image_paths(nested))
            elif isinstance(nested, (dict, list)):
                paths.extend(collect_source_image_paths(nested))
    elif isinstance(value, list):
        for nested in value:
            paths.extend(collect_source_image_paths(nested))
    return list(dict.fromkeys(paths))


def source_image_prompt(job: Job) -> str:
    paths = collect_source_image_paths(job.context)
    if not paths:
        return ""
    lines = "\n".join(f"- {path}" for path in paths)
    return f"""Source image files to preserve as visual references:
{lines}

Before generation, inspect these local image files and use them as source/reference images with `image_gen.imagegen` when supported. Preserve the supplied product, subject, identity, and layout constraints; do not treat these paths as text-only metadata.
"""


def write_worker_state(worker: RunningWorker, status: str) -> None:
    write_json(
        worker.item_dir / STATE_FILE,
        {
            "id": worker.job.id,
            "status": status,
            "attempt": worker.attempt,
            "pid": worker.process.pid,
            "startedAt": datetime.fromtimestamp(worker.started_at, timezone.utc).isoformat(),
            "lastHeartbeatAt": now_iso(),
        },
    )


def worker_result_contract(job: Job, image_path: Path, result_path: Path) -> str:
    return f"""Save the final PNG exactly here:
{image_path}

Then write this minimal worker result JSON exactly here:
{result_path}

Required JSON shape:
{{
  "id": "{job.id}",
  "status": "complete",
  "image_path": "{image_path}",
  "error": null,
  "caveats": ""
}}

If native image generation is unavailable or the image cannot be saved, write the same JSON shape with "status": "failed", "image_path": null, and a concise "error"."""


def fast_worker_prompt(job: Job, image_path: Path, result_path: Path) -> str:
    return f"""Generate exactly one PNG image with the native `image_gen.imagegen` tool.

Image prompt:
{job.prompt}

{worker_result_contract(job, image_path, result_path)}

Rules:
- Use `image_gen.imagegen`; do not call direct image APIs.
- Use only the native image generation tool and the file writes required for the final PNG/result JSON.
- If local CLI state or output-file writes are blocked by sandbox permissions, request escalation/outside-sandbox approval immediately.
- Do not request approvals for unrelated tools, network calls, or direct image APIs.
- Do not ask questions.
- Do not create placeholder art with Python, PIL, SVG, canvas, HTML, or screenshots.
"""


def robust_worker_prompt(job: Job, image_path: Path, result_path: Path) -> str:
    context = json.dumps(job.context, indent=2, sort_keys=True)
    source_images = source_image_prompt(job)
    return f"""You are a Creative Production image worker.

Do exactly one task.

Use the built-in native image generation tool `image_gen.imagegen` to generate exactly one PNG image for this prompt:

{job.prompt}

Context metadata, if useful:
{context}

{source_images}
{worker_result_contract(job, image_path, result_path)}

Rules:
- Use `image_gen.imagegen`; do not call direct image APIs.
- Use only the native image generation tool, source-image inspection when source files were provided, and the file writes required for the final PNG/result JSON.
- If local CLI state, source-image inspection, or output-file writes are blocked by sandbox permissions, request escalation/outside-sandbox approval immediately.
- Do not request approvals for unrelated tools, network calls, or direct image APIs.
- Generate exactly one image.
- Do not use Python, PIL, SVG, canvas, HTML, screenshots, or procedural placeholders to fake success.
- Do not ask the user questions.
- If native image generation is unavailable or the image cannot be saved, write the same JSON shape with "status": "failed", "image_path": null, and a concise "error".
- Do not write any other durable files except temporary files needed to complete this task.
"""


def worker_prompt(job: Job, image_path: Path, result_path: Path, fast_worker: bool) -> str:
    if fast_worker and not collect_source_image_paths(job.context):
        return fast_worker_prompt(job, image_path, result_path)
    return robust_worker_prompt(job, image_path, result_path)


def preflight_prompt(result_path: Path) -> str:
    return f"""You are a Creative Production image worker preflight.

Do not generate an image.
Use only the minimal tools needed to verify this Codex exec worker can access local CLI state and write this exact JSON file:
{result_path}

Required file contents:
{{
  "status": "ok"
}}

If local CLI state or output-file writes are blocked by sandbox permissions, request escalation/outside-sandbox approval immediately.
Do not request approvals for unrelated tools, network calls, direct image APIs, or image generation.
After the file exists with the required contents, reply with only this JSON object and no other text:

{{
  "status": "ok"
}}
"""


def parse_preflight_payload(*values: str) -> dict[str, Any] | None:
    for value in values:
        text = str(value or "").strip()
        if not text:
            continue
        try:
            payload = json.loads(text)
        except json.JSONDecodeError:
            continue
        if payload == {"status": "ok"}:
            return payload
    return None


def progressive_preflight_error(stderr: str, stdout: str) -> str:
    output = "\n".join(part for part in [stderr.strip(), stdout.strip()] if part)
    lowered = output.lower()
    if any(hint in lowered for hint in PREFLIGHT_ERROR_HINTS):
        return (
            "Codex exec preflight failed before image generation. "
            "The worker could not initialize its local Codex state, likely because "
            "~/.codex is not writable from the current sandbox. Rerun the local "
            "generation server with escalated permissions, then retry the same image batch."
        )
    if output:
        return f"Codex exec preflight failed before image generation:\n{output}"
    return "Codex exec preflight failed before image generation without stderr/stdout."


def run_preflight(
    *,
    codex_bin: str,
    workspace: Path,
    out_dir: Path,
    sandbox: str,
    preflight_timeout_seconds: float,
    worker_reasoning_effort: str,
    worker_approval_policy: str,
    ephemeral: bool,
    ignore_user_config: bool,
    ignore_rules: bool,
) -> None:
    preflight_dir = out_dir / "preflight"
    preflight_dir.mkdir(parents=True, exist_ok=True)
    result_path = preflight_dir / PREFLIGHT_FILE
    last_message_path = preflight_dir / LAST_MESSAGE_FILE
    command = [
        codex_bin,
        "exec",
        "--cd",
        str(workspace),
        "--skip-git-repo-check",
        "--sandbox",
        sandbox,
    ]
    if ephemeral:
        command.append("--ephemeral")
    if ignore_user_config:
        command.append("--ignore-user-config")
    if ignore_rules:
        command.append("--ignore-rules")
    command.extend(["--config", f'approval_policy="{worker_approval_policy}"'])
    if worker_reasoning_effort:
        command.extend(["--config", f'model_reasoning_effort="{worker_reasoning_effort}"'])
    command.extend(
        [
            "--color",
            "never",
            "--output-last-message",
            str(last_message_path),
            preflight_prompt(result_path),
        ]
    )
    try:
        result = subprocess.run(
            command,
            text=True,
            stdin=subprocess.DEVNULL,
            capture_output=True,
            timeout=preflight_timeout_seconds,
            check=False,
        )
    except subprocess.TimeoutExpired as error:
        raise RuntimeError(
            f"Codex exec preflight timed out after {preflight_timeout_seconds:g} seconds."
        ) from error
    if result.returncode != 0:
        raise RuntimeError(progressive_preflight_error(result.stderr, result.stdout))
    last_message = (
        last_message_path.read_text(encoding="utf-8") if last_message_path.exists() else ""
    )
    file_message = result_path.read_text(encoding="utf-8") if result_path.exists() else ""
    file_payload = parse_preflight_payload(file_message)
    if file_payload != {"status": "ok"}:
        raise RuntimeError(f"Codex exec preflight did not write the expected {PREFLIGHT_FILE}.")
    payload = parse_preflight_payload(last_message, result.stdout)
    if payload != {"status": "ok"}:
        raise RuntimeError("Codex exec preflight did not report the expected status.")


def launch_worker(
    *,
    codex_bin: str,
    workspace: Path,
    out_dir: Path,
    job: Job,
    attempt: int,
    sandbox: str,
    fast_worker: bool,
    worker_reasoning_effort: str,
    worker_approval_policy: str,
    ephemeral: bool,
    ignore_user_config: bool,
    ignore_rules: bool,
) -> RunningWorker:
    item_dir = out_dir / "workers" / slugify(job.id) / f"attempt-{attempt}"
    item_dir.mkdir(parents=True, exist_ok=True)
    image_path = item_dir / IMAGE_FILE
    result_path = item_dir / RESULT_FILE
    prompt = worker_prompt(job, image_path, result_path, fast_worker=fast_worker)
    stdout_path = item_dir / STDOUT_FILE
    stderr_path = item_dir / STDERR_FILE
    stdout = stdout_path.open("w", encoding="utf-8")
    stderr = stderr_path.open("w", encoding="utf-8")
    try:
        command = [
            codex_bin,
            "exec",
            "--cd",
            str(workspace),
            "--skip-git-repo-check",
            "--sandbox",
            sandbox,
        ]
        if ephemeral:
            command.append("--ephemeral")
        if ignore_user_config:
            command.append("--ignore-user-config")
        if ignore_rules:
            command.append("--ignore-rules")
        command.extend(["--config", f'approval_policy="{worker_approval_policy}"'])
        if worker_reasoning_effort:
            command.extend(["--config", f'model_reasoning_effort="{worker_reasoning_effort}"'])
        command.extend(
            [
                "--color",
                "never",
                "--output-last-message",
                str(item_dir / LAST_MESSAGE_FILE),
                prompt,
            ]
        )
        env = os.environ.copy()
        env.setdefault("NO_COLOR", "1")
        process = subprocess.Popen(
            command,
            stdin=subprocess.DEVNULL,
            env=env,
            text=True,
            stdout=stdout,
            stderr=stderr,
        )
    finally:
        stdout.close()
        stderr.close()
    worker = RunningWorker(
        job=job,
        attempt=attempt,
        item_dir=item_dir,
        process=process,
        started_at=time.time(),
    )
    write_worker_state(worker, "running")
    return worker


def read_worker_result(worker: RunningWorker) -> dict[str, Any] | None:
    result_path = worker.item_dir / RESULT_FILE
    image_path = worker.item_dir / IMAGE_FILE
    if not result_path.exists():
        if image_path.is_file():
            return {
                "id": worker.job.id,
                "status": "complete",
                "image_path": str(image_path),
                "error": None,
                "caveats": "Recovered from existing worker image because result JSON was missing.",
            }
        return None
    try:
        payload = json.loads(result_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        if image_path.is_file():
            return {
                "id": worker.job.id,
                "status": "complete",
                "image_path": str(image_path),
                "error": None,
                "caveats": f"Recovered from existing worker image because result JSON was invalid: {exc}",
            }
        return {
            "id": worker.job.id,
            "status": "failed",
            "image_path": None,
            "error": f"Worker wrote invalid result JSON: {exc}",
        }
    if payload.get("id") != worker.job.id:
        payload["id"] = worker.job.id
    return payload


def copy_completed_image(out_dir: Path, job: Job, payload: dict[str, Any]) -> dict[str, Any]:
    final_path = out_dir / job.output
    if payload.get("status") != "complete":
        return payload
    source_path = str(payload.get("image_path") or "").strip()
    if not source_path:
        return {
            **payload,
            "status": "failed",
            "image_path": None,
            "error": "Worker reported success without image_path.",
        }
    source = Path(source_path)
    if not source.is_file():
        return {
            **payload,
            "status": "failed",
            "image_path": None,
            "error": f"Worker reported success but image is not a file: {source}",
        }
    final_path.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(source, final_path)
    return {**payload, "image_path": str(final_path)}


def summarize(jobs: list[Job], results: dict[str, dict[str, Any]]) -> dict[str, Any]:
    ordered = [results.get(job.id, {"id": job.id, "status": "pending"}) for job in jobs]
    complete = sum(1 for item in ordered if item.get("status") == "complete")
    failed = sum(1 for item in ordered if item.get("status") == "failed")
    return {
        "status": "complete" if complete == len(jobs) else "partial",
        "total": len(jobs),
        "complete": complete,
        "failed": failed,
        "pending": len(jobs) - complete - failed,
        "results": ordered,
    }


def run(args: argparse.Namespace) -> int:
    jobs = load_jobs(args.input)
    args.out_dir.mkdir(parents=True, exist_ok=True)
    workspace = args.workspace.resolve()
    if args.preflight:
        run_preflight(
            codex_bin=args.codex_bin,
            workspace=workspace,
            out_dir=args.out_dir,
            sandbox=args.sandbox,
            preflight_timeout_seconds=args.preflight_timeout_seconds,
            worker_reasoning_effort=args.worker_reasoning_effort,
            worker_approval_policy=args.worker_approval_policy,
            ephemeral=args.ephemeral,
            ignore_user_config=args.ignore_user_config,
            ignore_rules=args.ignore_rules,
        )
    results: dict[str, dict[str, Any]] = {}
    attempts = {job.id: 0 for job in jobs}
    queue = jobs[:]
    running: list[RunningWorker] = []
    summary_path = args.out_dir / "codex-exec-image-results.json"

    def persist() -> None:
        write_json(summary_path, summarize(jobs, results))

    persist()
    while queue or running:
        while queue and len(running) < args.max_concurrency:
            job = queue.pop(0)
            attempts[job.id] += 1
            running.append(
                launch_worker(
                    codex_bin=args.codex_bin,
                    workspace=workspace,
                    out_dir=args.out_dir,
                    job=job,
                    attempt=attempts[job.id],
                    sandbox=args.sandbox,
                    fast_worker=args.fast_worker,
                    worker_reasoning_effort=args.worker_reasoning_effort,
                    worker_approval_policy=args.worker_approval_policy,
                    ephemeral=args.ephemeral,
                    ignore_user_config=args.ignore_user_config,
                    ignore_rules=args.ignore_rules,
                )
            )
            persist()

        now = time.time()
        next_running: list[RunningWorker] = []
        for worker in running:
            timed_out = now - worker.started_at > args.timeout_seconds
            return_code = worker.process.poll()
            if timed_out and return_code is None:
                worker.process.terminate()
                try:
                    worker.process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    worker.process.kill()
                    worker.process.wait(timeout=5)
                return_code = worker.process.returncode

            if return_code is None:
                write_worker_state(worker, "running")
                next_running.append(worker)
                continue

            payload = read_worker_result(worker)
            if payload is None:
                reason = (
                    "Worker timed out." if timed_out else f"Worker exited with code {return_code}."
                )
                payload = {
                    "id": worker.job.id,
                    "status": "failed",
                    "image_path": None,
                    "error": reason,
                }
                write_json(worker.item_dir / RESULT_FILE, payload)
            payload = copy_completed_image(args.out_dir, worker.job, payload)
            write_worker_state(worker, str(payload.get("status") or "failed"))

            if payload.get("status") == "complete":
                results[worker.job.id] = payload
            elif attempts[worker.job.id] < args.max_attempts:
                queue.append(worker.job)
            else:
                results[worker.job.id] = payload
            persist()
        running = next_running
        if running:
            time.sleep(args.poll_interval)

    persist()
    summary = summarize(jobs, results)
    return 0 if summary["failed"] == 0 and summary["pending"] == 0 else 1


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, type=Path, help="JSONL job file.")
    parser.add_argument("--out-dir", required=True, type=Path, help="Batch output directory.")
    parser.add_argument(
        "--workspace", required=True, type=Path, help="Codex exec working directory."
    )
    parser.add_argument("--codex-bin", default="codex")
    parser.add_argument("--sandbox", default="workspace-write")
    parser.add_argument("--max-concurrency", type=int, default=64)
    parser.add_argument("--max-attempts", type=int, default=2)
    parser.add_argument("--timeout-seconds", type=float, default=WORKER_DEFAULT_TIMEOUT_SECONDS)
    parser.add_argument(
        "--preflight-timeout-seconds",
        type=float,
        default=PREFLIGHT_DEFAULT_TIMEOUT_SECONDS,
        help="Timeout for the Codex exec startup probe.",
    )
    parser.add_argument("--poll-interval", type=float, default=0.5)
    parser.add_argument(
        "--fast-worker",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Use a shorter prompt for prompt-only jobs without source images.",
    )
    parser.add_argument(
        "--worker-reasoning-effort",
        default="low",
        help="Codex model_reasoning_effort override for worker sessions.",
    )
    parser.add_argument(
        "--worker-approval-policy",
        default="on-request",
        help="Codex approval_policy override for worker sessions.",
    )
    parser.add_argument(
        "--ephemeral",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Run worker sessions without persisting Codex rollout state.",
    )
    parser.add_argument(
        "--ignore-rules",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Skip user/project execpolicy .rules files inside dumb image-worker sessions.",
    )
    parser.add_argument(
        "--ignore-user-config",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Skip user config/plugin loading for faster native image-worker startup.",
    )
    parser.add_argument(
        "--preflight",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Run one tiny codex exec probe before spawning image workers.",
    )
    args = parser.parse_args()
    raise SystemExit(run(args))


if __name__ == "__main__":
    main()
