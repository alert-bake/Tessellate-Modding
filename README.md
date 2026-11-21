# Tessellate-Modding

Modding documentation for Tessellate, and the source repository for **TingleDoculate**, a small static documentation generator inspired by MkDocs.

## Repository layout

- `docs/` — Markdown source for the modding wiki.
- `TingleDoculate/` — TingleDoculate's source code and implementation notes.
- `tingledoculate.toml` — build configuration.
- `site/` — generated website output (not committed).

## Build the documentation

Requires Python 3.11 or newer.

```sh
python -m pip install -e .
tingledoculate build
```

Preview locally:

```sh
tingledoculate serve
```

See [TingleDoculate/README.md](TingleDoculate/README.md) for the generator's current scope and usage.
