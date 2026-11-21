from __future__ import annotations

import hashlib
import json
import re
import shutil
import tomllib
from pathlib import Path, PurePosixPath

from .parser import make_markdown_parser, page_title, plain_text, rewrite_markdown_links
from .theme import CSS, JS, render_page


CACHE_VERSION = 1


def _digest(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _output_path(relative: Path) -> Path:
    posix = PurePosixPath(relative.as_posix())
    if posix.name.lower() == "index.md":
        return Path(*posix.parts[:-1], "index.html")
    return Path(*posix.with_suffix(".html").parts)


def _load_config(config_path: Path) -> dict:
    if not config_path.exists():
        return {"site": {"title": "Documentation", "description": "", "source": "docs", "output": "site"}, "build": {"incremental": True}}
    with config_path.open("rb") as handle:
        return tomllib.load(handle)


def _navigation(pages: list[tuple[Path, Path, str, str]]) -> list[dict[str, str]]:
    items = []
    for source, output, title, _ in pages:
        depth = max(0, len(source.parts) - 1)
        items.append({"title": title, "url": "/" + output.as_posix(), "depth": str(depth)})
    return items


def build(root: Path, config_path: Path | None = None, force: bool = False) -> dict[str, int]:
    root = root.resolve()
    config_path = (config_path or root / "tingledoculate.toml").resolve()
    config = _load_config(config_path)
    site_config = config.get("site", {})
    build_config = config.get("build", {})
    source_dir = (root / site_config.get("source", "docs")).resolve()
    output_dir = (root / site_config.get("output", "site")).resolve()
    cache_dir = root / ".tingledoculate"
    cache_path = cache_dir / "cache.json"

    if not source_dir.is_dir():
        raise FileNotFoundError(f"Documentation source directory does not exist: {source_dir}")

    source_files = sorted(p for p in source_dir.rglob("*.md") if not any(part.startswith(".") for part in p.relative_to(source_dir).parts))
    parser = make_markdown_parser()
    pages: list[tuple[Path, Path, str, str]] = []
    for source in source_files:
        relative = source.relative_to(source_dir)
        markdown = source.read_text(encoding="utf-8")
        title = page_title(markdown, source.stem)
        html = rewrite_markdown_links(parser.render(markdown))
        pages.append((relative, _output_path(relative), title, html))

    nav = _navigation(pages)
    global_fingerprint = _digest(
        (json.dumps({"site": site_config, "nav": nav}, sort_keys=True) + CSS + JS).encode("utf-8")
    )
    old_cache = {}
    if build_config.get("incremental", True) and cache_path.exists() and not force:
        try:
            old_cache = json.loads(cache_path.read_text(encoding="utf-8"))
            if old_cache.get("version") != CACHE_VERSION:
                old_cache = {}
        except (OSError, json.JSONDecodeError):
            old_cache = {}

    output_dir.mkdir(parents=True, exist_ok=True)
    assets_dir = output_dir / "assets"
    assets_dir.mkdir(parents=True, exist_ok=True)
    (assets_dir / "tingledoculate.css").write_text(CSS, encoding="utf-8")
    (assets_dir / "tingledoculate.js").write_text(JS, encoding="utf-8")

    site_title = str(site_config.get("title", "Documentation"))
    description = str(site_config.get("description", ""))
    new_cache: dict[str, str] = {}
    search_pages = []
    rendered = skipped = 0

    for relative, output_relative, title, body in pages:
        source = source_dir / relative
        key = relative.as_posix()
        source_hash = _digest(source.read_bytes())
        page_fingerprint = _digest((source_hash + global_fingerprint).encode("utf-8"))
        destination = output_dir / output_relative
        new_cache[key] = page_fingerprint
        if (
            build_config.get("incremental", True)
            and not force
            and old_cache.get("pages", {}).get(key) == page_fingerprint
            and destination.exists()
        ):
            skipped += 1
        else:
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_text(
                render_page(title, site_title, description, body, nav),
                encoding="utf-8",
            )
            rendered += 1
        search_pages.append({
            "title": title,
            "url": "/" + output_relative.as_posix(),
            "text": plain_text(body),
        })

    # Copy user-provided static assets without putting them through the Markdown pipeline.
    user_assets = source_dir / "assets"
    if user_assets.is_dir():
        for asset in user_assets.rglob("*"):
            if asset.is_file():
                target = output_dir / "assets" / asset.relative_to(user_assets)
                target.parent.mkdir(parents=True, exist_ok=True)
                if not target.exists() or asset.stat().st_mtime_ns > target.stat().st_mtime_ns:
                    shutil.copy2(asset, target)

    (output_dir / "search-index.json").write_text(
        json.dumps(search_pages, ensure_ascii=False, separators=(",", ":")),
        encoding="utf-8",
    )
    cache_dir.mkdir(parents=True, exist_ok=True)
    cache_path.write_text(
        json.dumps({"version": CACHE_VERSION, "pages": new_cache}, separators=(",", ":")),
        encoding="utf-8",
    )
    return {"pages": len(pages), "rendered": rendered, "skipped": skipped}
