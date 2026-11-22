# Tessellate-Modding

The source repository for Tessellate's modding documentation.

The wiki currently covers the modding systems that exist today: **LuaJ** and **custom commands**. Future systems will be documented when they exist and their behavior is confirmed.

## Aizo

Tessellate's documentation can use TingleDoculate's HTMD color tags: <color="FF00FF">Aizo</color>.

## Documentation

- `docs/` contains the Markdown source for the wiki.
- `tingledoculate.toml` configures the documentation site.
- `site/` is generated output and is not committed.

## Build the documentation

Requires Python 3.11 or newer.

Install [TingleDoculate](https://github.com/alert-bake/TingleDoculate), the standalone static-site generator:

```sh
python -m pip install "git+https://github.com/alert-bake/TingleDoculate.git"
tingledoculate build
```

Preview locally:

```sh
tingledoculate serve
```

TingleDoculate's source code, tests, usage guide, and issue tracker live in its [own repository](https://github.com/alert-bake/TingleDoculate).

The published modding wiki is available at:
https://alert-bake.github.io/Tessellate-Modding/
