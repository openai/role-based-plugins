#!/usr/bin/env python3
"""Hydrate external Creative Production assets into the plugin tree."""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import sys
import tempfile
import urllib.request
import zipfile
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

SCRIPT_DIR = Path(__file__).resolve().parent
PLUGIN_ROOT = SCRIPT_DIR.parent
DEFAULT_MANIFEST = PLUGIN_ROOT / "assets" / "hydration" / "asset-bundle.json"
REPO_PLUGIN_ROOT_NAMES = {"creative-production", "creative-production"}


class HydrationError(RuntimeError):
    """Asset hydration failed."""


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def repo_root(plugin_root: Path) -> Path:
    if plugin_root.name in REPO_PLUGIN_ROOT_NAMES and plugin_root.parent.name == "plugins":
        return plugin_root.parent.parent
    return plugin_root


def target_path(plugin_root: Path, original_path: str) -> Path:
    rel = Path(original_path)
    if original_path.startswith("plugins/"):
        if (
            plugin_root.name == "creative-production"
            and len(rel.parts) >= 2
            and rel.parts[0] == "plugins"
            and rel.parts[1] == "creative-production"
        ):
            return plugin_root.joinpath(*rel.parts[2:])
        return repo_root(plugin_root) / rel
    return plugin_root / rel


def verify_file(path: Path, asset: dict[str, Any]) -> None:
    expected_size = asset.get("size_bytes", asset.get("sizeBytes"))
    if expected_size is not None and path.stat().st_size != int(expected_size):
        raise HydrationError(f"{path} has size {path.stat().st_size}, expected {expected_size}")
    expected_sha = asset.get("sha256")
    if expected_sha and sha256_file(path) != expected_sha:
        raise HydrationError(f"{path} failed sha256 verification")


def download_to_cache(
    source: str, cache_root: Path, expected: dict[str, Any] | None = None
) -> Path:
    cache_root.mkdir(parents=True, exist_ok=True)
    parsed = urlparse(source)
    name = Path(parsed.path).name or hashlib.sha256(source.encode()).hexdigest()
    target = cache_root / name
    if parsed.scheme == "file":
        source_path = Path(parsed.path)
        shutil.copy2(source_path, target)
    else:
        with urllib.request.urlopen(source, timeout=30) as response:
            target.write_bytes(response.read())
    if expected:
        verify_file(target, expected)
    return target


def drive_download_url(file_id: str) -> str:
    return f"https://drive.google.com/uc?export=download&id={file_id}"


def source_from_metadata(metadata: dict[str, Any]) -> str | None:
    if metadata.get("downloadUrl"):
        return str(metadata["downloadUrl"])
    if metadata.get("driveFileId"):
        return drive_download_url(str(metadata["driveFileId"]))
    return None


def load_external_manifest(
    manifest: dict[str, Any],
    *,
    source_dir: Path | None,
    asset_manifest: Path | None,
    cache_root: Path,
) -> dict[str, Any] | None:
    if asset_manifest:
        return read_json(asset_manifest)
    external = manifest.get("externalManifest") or {}
    file_name = external.get("fileName")
    if source_dir and file_name:
        candidate = source_dir / file_name
        if candidate.exists():
            return read_json(candidate)
    source = source_from_metadata(external)
    if source:
        return read_json(download_to_cache(source, cache_root))
    return None


def merged_manifest(
    manifest: dict[str, Any],
    external: dict[str, Any] | None,
) -> dict[str, Any]:
    if not external:
        return manifest
    merged = dict(manifest)
    merged["assets"] = external.get("assets", [])
    merged["assetsAreComplete"] = bool(external.get("assetsAreComplete", True))
    merged["flatFilesDirectory"] = external.get(
        "flatFilesDirectory",
        manifest.get("externalManifest", {}).get("flatFilesDirectory", "files"),
    )
    return merged


def synthesize_asset(manifest: dict[str, Any], selector: str) -> dict[str, Any]:
    original_path = selector
    archive_root = manifest.get("zip", {}).get("archiveRoot") or manifest.get("bundleId", "")
    archive_path = f"{archive_root}/{original_path}" if archive_root else original_path
    return {
        "original_path": original_path,
        "archive_path": archive_path,
        "flat_filename": Path(original_path).name,
        "flat_path": str(
            Path(manifest.get("flatFilesDirectory", "files")) / Path(original_path).name
        ),
    }


def selected_assets(manifest: dict[str, Any], selectors: list[str]) -> list[dict[str, Any]]:
    assets = list(manifest.get("assets") or [])
    if not selectors:
        if assets:
            return assets
        return list(manifest.get("sentinelAssets") or [])

    by_key: dict[str, dict[str, Any]] = {}
    for asset in assets:
        by_key[str(asset.get("original_path"))] = asset
        if asset.get("flat_filename"):
            by_key[str(asset["flat_filename"])] = asset

    selected = []
    missing = []
    for selector in selectors:
        asset = by_key.get(selector)
        if not asset and manifest.get("pathPreserving") and "/" in selector:
            asset = synthesize_asset(manifest, selector)
        if asset:
            selected.append(asset)
        else:
            missing.append(selector)
    if missing:
        raise HydrationError("Unknown asset selector(s): " + ", ".join(missing))
    return selected


def source_dir_candidates(
    source_dir: Path, manifest: dict[str, Any], asset: dict[str, Any]
) -> list[Path]:
    candidates = []
    if asset.get("flat_path"):
        candidates.append(source_dir / str(asset["flat_path"]))
    flat_dir = manifest.get("flatFilesDirectory") or manifest.get("externalManifest", {}).get(
        "flatFilesDirectory", "files"
    )
    if asset.get("flat_filename"):
        candidates.append(source_dir / str(flat_dir) / str(asset["flat_filename"]))
        candidates.append(source_dir / str(asset["flat_filename"]))
    if asset.get("original_path"):
        candidates.append(source_dir / str(asset["original_path"]))
    return candidates


def restore_from_source_dir(
    manifest: dict[str, Any],
    *,
    plugin_root: Path,
    source_dir: Path,
    assets: list[dict[str, Any]],
    force: bool,
) -> list[Path]:
    restored = []
    for asset in assets:
        source = next(
            (path for path in source_dir_candidates(source_dir, manifest, asset) if path.exists()),
            None,
        )
        if not source:
            raise HydrationError(f"Could not find {asset.get('original_path')} in {source_dir}")
        destination = target_path(plugin_root, str(asset["original_path"]))
        if destination.exists() and not force:
            verify_file(destination, asset)
            restored.append(destination)
            continue
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, destination)
        verify_file(destination, asset)
        restored.append(destination)
    return restored


def restore_from_zip(
    *,
    plugin_root: Path,
    zip_path: Path,
    assets: list[dict[str, Any]],
    force: bool,
) -> list[Path]:
    restored = []
    with zipfile.ZipFile(zip_path) as archive:
        names = set(archive.namelist())
        for asset in assets:
            archive_path = str(asset.get("archive_path") or "")
            if archive_path not in names:
                raise HydrationError(f"Could not find {archive_path} in {zip_path}")
            destination = target_path(plugin_root, str(asset["original_path"]))
            if destination.exists() and not force:
                verify_file(destination, asset)
                restored.append(destination)
                continue
            destination.parent.mkdir(parents=True, exist_ok=True)
            with archive.open(archive_path) as source, destination.open("wb") as output:
                shutil.copyfileobj(source, output)
            verify_file(destination, asset)
            restored.append(destination)
    return restored


def cache_asset_downloads(
    manifest: dict[str, Any],
    *,
    cache_root: Path,
    assets: list[dict[str, Any]],
) -> None:
    for asset in assets:
        source = source_from_metadata(asset)
        if not source:
            continue
        flat_path = asset.get("flat_path")
        flat_filename = asset.get("flat_filename")
        if flat_path:
            target = cache_root / str(flat_path)
        elif flat_filename:
            target = (
                cache_root / str(manifest.get("flatFilesDirectory", "files")) / str(flat_filename)
            )
        else:
            target = cache_root / str(asset["original_path"])
        target.parent.mkdir(parents=True, exist_ok=True)
        downloaded = download_to_cache(source, cache_root / ".downloads", asset)
        shutil.copy2(downloaded, target)


def check_sentinels(manifest: dict[str, Any], plugin_root: Path) -> None:
    sentinels = manifest.get("sentinelAssets") or []
    if not sentinels:
        raise HydrationError("Hydration manifest has no sentinelAssets.")
    targets = [target_path(plugin_root, str(asset["original_path"])) for asset in sentinels]
    duplicate_targets = {str(path) for path in targets if targets.count(path) > 1}
    if duplicate_targets:
        raise HydrationError("Duplicate sentinel targets: " + ", ".join(sorted(duplicate_targets)))
    missing = []
    for asset, path in zip(sentinels, targets):
        if not path.exists():
            missing.append(str(asset["original_path"]))
            continue
        verify_file(path, asset)
    if missing:
        raise HydrationError(
            "Hydratable assets are missing. Run hydrate_assets.py with --source-dir, "
            "--source-zip, or configured Drive download metadata. Missing: " + ", ".join(missing)
        )


def hydrate(args: argparse.Namespace) -> list[Path]:
    plugin_root = args.plugin_root.resolve()
    manifest = read_json(args.manifest)
    if args.check:
        check_sentinels(manifest, plugin_root)
        return []

    cache_root = args.cache_root or Path(tempfile.gettempdir()) / "creative-production-asset-cache"
    external = load_external_manifest(
        manifest,
        source_dir=args.source_dir,
        asset_manifest=args.asset_manifest,
        cache_root=cache_root,
    )
    full_manifest = merged_manifest(manifest, external)
    assets = selected_assets(full_manifest, args.asset)

    if args.source_zip:
        return restore_from_zip(
            plugin_root=plugin_root,
            zip_path=args.source_zip,
            assets=assets,
            force=args.force,
        )
    if args.source_dir:
        return restore_from_source_dir(
            full_manifest,
            plugin_root=plugin_root,
            source_dir=args.source_dir,
            assets=assets,
            force=args.force,
        )

    zip_source = source_from_metadata(manifest.get("zip", {}))
    if zip_source:
        try:
            zip_path = download_to_cache(zip_source, cache_root, manifest.get("zip", {}))
            return restore_from_zip(
                plugin_root=plugin_root,
                zip_path=zip_path,
                assets=assets,
                force=args.force,
            )
        except Exception:
            if not args.progressive:
                raise

    if external:
        cache_asset_downloads(full_manifest, cache_root=cache_root, assets=assets)
        return restore_from_source_dir(
            full_manifest,
            plugin_root=plugin_root,
            source_dir=cache_root,
            assets=assets,
            force=args.force,
        )

    raise HydrationError(
        "No usable hydration source is configured. Provide --source-dir or --source-zip, "
        "or populate Drive file IDs/download URLs in the hydration manifest."
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--plugin-root", type=Path, default=PLUGIN_ROOT)
    parser.add_argument("--source-dir", type=Path)
    parser.add_argument("--source-zip", type=Path)
    parser.add_argument("--asset-manifest", type=Path)
    parser.add_argument("--cache-root", type=Path)
    parser.add_argument("--asset", action="append", default=[])
    parser.add_argument("--progressive", action="store_true")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--force", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        restored = hydrate(args)
    except HydrationError as exc:
        print(f"Asset hydration failed: {exc}", file=sys.stderr)
        return 1
    if args.check:
        print("Hydration check passed.")
    else:
        print(json.dumps({"restored": [str(path) for path in restored]}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
