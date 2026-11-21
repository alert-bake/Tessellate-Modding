# TingleDoculate

TingleDoculate is a small, Python-based static documentation generator inspired by the useful parts of MkDocs.

It is designed to live in the Tessellate-Modding repository and build the repository's Markdown documentation into ordinary static HTML, CSS, and JavaScript.

## Current status

Early implementation. The first version focuses on the core pipeline:

- Markdown files to static HTML pages
- Filesystem-derived navigation
- Relative Markdown links rewritten to HTML links
- A generated, client-side search index
- Incremental page rendering
- No server-side runtime in the generated site

TingleDoculate is intentionally independent of Tessellate's modding APIs. It does not assume that TCP or any future modding interface exists.

## Requirements

- Python 3.11+
- Dependencies installed from the repository's `pyproject.toml`

## Usage

From the repository root:

```sh
python -m pip install -e .
tingledoculate build
```

The generated website is written to `site/`.

Useful commands:

```sh
tingledoculate build
tingledoculate clean
tingledoculate serve
```

## Configuration

Edit `tingledoculate.toml`:

```toml
[site]
title = "Tessellate Modding"
description = "Documentation for modding Tessellate."
source = "docs"
output = "site"

[build]
incremental = true
```

## Design goals

1. Keep the build pipeline understandable.
2. Keep runtime dependencies out of the generated website.
3. Avoid rebuilding unchanged pages.
4. Prefer predictable filesystem conventions over a large plugin system.
5. Measure performance before making optimization claims.

## License

The repository owner should choose and add the project's license before distribution.
