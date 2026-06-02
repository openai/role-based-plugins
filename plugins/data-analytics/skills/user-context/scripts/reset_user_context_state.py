#!/usr/bin/env python3
"""Back up and clear local Data Analytics user-context and onboarding state files."""

from __future__ import annotations

import argparse
import os
import shutil
import sys
from datetime import datetime
from pathlib import Path

STATE_FILENAMES = (
    "user-context.md",
    "onboarding-state.json",
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Move active Data Analytics local state files into a timestamped sibling "
            "backup directory. This leaves Data Analytics ready for fresh onboarding."
        )
    )
    parser.add_argument("--codex-home", type=Path, default=None)
    parser.add_argument("--state-dir", type=Path, default=None)
    parser.add_argument("--backup-dir", type=Path, default=None)
    parser.add_argument("--dry-run", action="store_true")
    return parser.parse_args()


def default_codex_home() -> Path:
    env_home = os.environ.get("CODEX_HOME")
    if env_home:
        return Path(env_home).expanduser()
    return Path.home() / ".codex"


def resolve_paths(args: argparse.Namespace) -> tuple[Path, Path]:
    codex_home = args.codex_home.expanduser() if args.codex_home else default_codex_home()
    state_dir = (
        args.state_dir.expanduser()
        if args.state_dir
        else codex_home / "state/plugins/data-analytics"
    )
    if args.backup_dir:
        backup_dir = args.backup_dir.expanduser()
    else:
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        backup_dir = state_dir.parent / f"{state_dir.name}-backup-{timestamp}"
    return state_dir, backup_dir


def main() -> int:
    args = parse_args()
    state_dir, backup_dir = resolve_paths(args)
    state_files = [state_dir / filename for filename in STATE_FILENAMES]
    existing_state_files = [path for path in state_files if path.exists()]

    if not existing_state_files:
        print(f"No active Data Analytics state files found in: {state_dir}")
        return 0
    if backup_dir.exists():
        print(f"Backup directory already exists: {backup_dir}", file=sys.stderr)
        return 1
    if args.dry_run:
        print(f"Data Analytics state directory: {state_dir}")
        print(f"Backup directory: {backup_dir}")
        for path in existing_state_files:
            print(f"would move: {path.name}")
        print("Dry run only; no files were moved.")
        return 0

    backup_dir.mkdir(parents=True)
    moved: list[str] = []
    for path in existing_state_files:
        shutil.move(str(path), str(backup_dir / path.name))
        moved.append(path.name)

    removed_state_dir = False
    try:
        state_dir.rmdir()
        removed_state_dir = True
    except OSError:
        removed_state_dir = False

    print(f"Data Analytics state directory: {state_dir}")
    print(f"Backup directory: {backup_dir}")
    for filename in moved:
        print(f"moved: {filename}")
    if removed_state_dir:
        print("state directory: removed because it was empty")
    else:
        print("state directory: kept because it still contains other files")
    print("Restore by moving the backed-up files back into the Data Analytics state directory.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
