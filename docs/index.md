# Tessellate Modding Documentation

<color="00FF00">Welcome to the Tessellate modding documentation.</color>

This documentation covers the modding surface currently implemented in Tessellate:

- [LuaJ Modding API](lua-j/index.md): mod layout, sandbox, Lua globals, settings, engine APIs, and permissions.
- [TESSELLATE Custom Command API](custom-commands/index.md): JSON command definitions and the Kotlin command extension interface.

The documentation is intentionally implementation-led. It distinguishes APIs that mod authors can use today from application-side extension points and features that do not exist yet.

## Documentation status

The API is under active development. The reference pages link to the Tessellate source revision they were checked against. If the implementation changes, update the docs from source rather than assuming old examples still work.

## Contributing documentation

Add Markdown files under `docs/`. Directories become navigation groups, and Markdown files become pages.

This wiki is built with [TingleDoculate](https://github.com/alert-bake/TingleDoculate), a separate static documentation generator. Install it and run `tingledoculate build` from the repository root to generate the site.

### Little Disclaimer

I AM A BUM.

**ChatGPT** IS helping me write the docs since I am Not reading 70kb of kotlin when a lot of new modding content is added.
