from __future__ import annotations

import re
from pathlib import PurePosixPath

from markdown_it import MarkdownIt


_MARKDOWN_LINK = re.compile(r'(?P<prefix>href=["\'])(?P<url>[^"\']+\.md)(?P<suffix>(?:#[^"\']*)?["\'])', re.IGNORECASE)
_TAGS = re.compile(r"<[^>]+>")
_WHITESPACE = re.compile(r"\s+")


def make_markdown_parser() -> MarkdownIt:
    """Create the single Markdown parser configuration used by every page."""
    return MarkdownIt("default", {"html": False, "linkify": False, "typographer": False})


def rewrite_markdown_links(rendered_html: str) -> str:
    """Point rendered links at the generated .html pages instead of source .md files."""
    def replace(match: re.Match[str]) -> str:
        url = match.group("url")
        suffix = match.group("suffix")
        path = PurePosixPath(url)
        target = path.with_suffix(".html").as_posix()
        if target.endswith("/index.html") and target.startswith("./"):
            target = target[2:]
        return f'{match.group("prefix")}{target}{suffix}'

    return _MARKDOWN_LINK.sub(replace, rendered_html)


def plain_text(rendered_html: str) -> str:
    """Extract compact searchable text from rendered HTML."""
    text = _TAGS.sub(" ", rendered_html)
    text = re.sub(r"&(?:amp|lt|gt|quot|#39);", " ", text)
    return _WHITESPACE.sub(" ", text).strip()


def page_title(markdown: str, fallback: str) -> str:
    """Use the first Markdown H1 as the page title, falling back to its filename."""
    for line in markdown.splitlines():
        match = re.match(r"^#\s+(.+?)\s*#*\s*$", line)
        if match:
            return match.group(1).strip()
    return fallback.replace("-", " ").replace("_", " ").title()
