# LuaJ Modding API

Tessellate currently embeds **LuaJ 3.0.1** for Lua mods. Each mod runs in its own Lua environment and can register settings and call the engine APIs listed below.

This page documents the implementation in the [Tessellate source](https://github.com/alert-bake/Tessellate/tree/23151c1effcffb9b355e1dd2ad6c9bf1f7f6b891/app/src/main/java/com/nitrous/tessellate/modding). It describes the current implementation, not a promise that every API name is permanently stable.

## Installing a Lua mod

The runtime scans:

~~~text
Android/data/com.nitrous.tessellate/files/mods/
  example_mod/
    init.lua
    helpers.lua
    permissions.yml
~~~

Each immediate subdirectory is treated as one mod. The directory name becomes the mod ID. A directory is ignored if it contains no `.lua` files.

All `.lua` files directly inside the mod directory are read as UTF-8 and concatenated into one source chunk. `init.lua` is placed first when present; the remaining files are sorted by filename. Nested directories are not scanned.

Each mod receives its own LuaJ `Globals` environment. A script's top-level code runs when the mod loads. A Lua error is recorded against that mod and makes its load result unsuccessful.

## Available Lua libraries

The runtime loads LuaJ's base, package, bit32, table, string, coroutine, and math libraries.

The following globals are explicitly removed from the environment:

- `dofile`
- `loadfile`
- `luajava`

The source inspector also flags use of `io.open`, `io.popen`, `io.lines`, `os.execute`, `os.remove`, and `os.rename`. Do not rely on filesystem access, shell access, or Java interop being available.

## Settings API

### `Settings.registerCategory(id, labelOrTable)`

Registers a settings category owned by the current mod.

~~~lua
Settings.registerCategory("example:weather", {
    label = "Weather",
    screen = "settings", -- "settings" or "debug"
    order = 50
})
~~~

You can also pass a plain label string instead of a table. The table fields are:

| Field | Default | Meaning |
| --- | --- | --- |
| `label` | category ID | Text shown for the category |
| `screen` | `"settings"` | `"debug"` or `"debug_options"` places it in Debug Options; other values use Settings |
| `order` | `200` | Ordering value |

### `Settings.register(settingId, config)`

Registers a UI setting. Supported `type` values are `"toggle"`, `"slider"`, `"selector"`, and `"button"`.

A setting must use either an existing `reference`, Lua `get`/`set` callbacks, or an action callback for a button.

~~~lua
local enabled = true
local intensity = 50

Settings.register("example:enabled", {
    type = "toggle",
    label = "Enable weather",
    description = "Turns the weather effect on or off.",
    default = true,
    get = function()
        return enabled
    end,
    set = function(value)
        enabled = value
    end
})

Settings.register("example:intensity", {
    type = "slider",
    label = "Intensity",
    min = 0,
    max = 100,
    step = 5,
    default = 50,
    get = function()
        return intensity
    end,
    set = function(value)
        intensity = value
    end
})
~~~

Supported configuration fields:

| Field | Meaning |
| --- | --- |
| `type` | Required control type: `toggle`, `slider`, `selector`, or `button` |
| `label` | Display label; defaults to the setting ID |
| `description` | Optional description |
| `category` | Category ID; defaults to an automatically created `mod:<modId>` category |
| `screen` | `settings`, `debug`, or `debug_options` |
| `order` | Ordering value; defaults to `200` |
| `default` | Initial value; defaults to false for toggles and the slider minimum (or 0) for sliders |
| `min`, `max`, `step` | Numeric slider configuration |
| `options` | Selector choices, as strings or tables containing `value` and optional `label` |
| `reference` | ID of a previously registered reference |
| `get`, `set` | Lua callbacks used for a property-backed setting |
| `action`, `onClick`, `onPress`, `run`, `call` | Action callback names accepted for button settings and action references |
| `requiresConfirmation` | Whether the setting action requires confirmation |
| `confirmationMessage` | Optional confirmation text |
| `persist` | Whether the setting value is persisted; defaults to true except for buttons |

For a selector, `options` can look like this:

~~~lua
options = {
    { value = "clear", label = "Clear" },
    { value = "rain", label = "Rain" },
    { value = "storm", label = "Storm" }
}
~~~

If a setting omits `category`, the runtime creates a category named `mod:<modId>`. A button needs an action callback or an action reference; property getter/setter callbacks are not valid for buttons.

### `Settings.registerReference(id, definition)`

Registers a reference that a setting can use. The `type` field accepts:

- `"boolean"`, `"bool"`, or `"toggle"` for boolean properties
- `"string"` or `"selector"` for string properties
- `"number"`, `"float"`, `"int"`, or `"slider"` for numeric properties
- `"action"`, `"button"`, or `"command"` for an action

Property references use `get` and/or `set` callbacks. Action references use an action callback. For example:

~~~lua
local mode = "rain"

Settings.registerReference("example:mode_ref", {
    type = "string",
    get = function()
        return mode
    end,
    set = function(value)
        mode = value
    end
})

Settings.register("example:mode", {
    type = "selector",
    label = "Weather mode",
    reference = "example:mode_ref",
    default = "rain",
    options = { "clear", "rain", "storm" }
})
~~~

### `Settings.get(settingId)` and `Settings.set(settingId, value)`

Read or update a registered setting:

~~~lua
local current = Settings.get("example:enabled")
Settings.set("example:enabled", false)
~~~

A mod can update its own settings. Updating a vanilla setting requires the `settings.vanilla.write` permission. A mod cannot update another mod's setting.

## Other exposed APIs

The runtime exposes these global tables in addition to `Settings`.

### `Commands`

- `Commands.execute(commandString)`: executes a slash command and returns a table with `success` and `message` fields.

This requires `commands.execute`. **There is no Lua `Commands.register` function in the current runtime.** Lua mods can execute commands; registering new console commands is a separate Kotlin API described in [TESSELLATE Custom Command API](../custom-commands/index.md).

~~~lua
local result = Commands.execute("/give tessellate:cobblestone 5")
print(result.success, result.message)
~~~

### `Player`

| Function | Permission | Result |
| --- | --- | --- |
| `Player.isFlying()` | None | Current flight state |
| `Player.isInstaMine()` | None | Current instant-mining state |
| `Player.setFlying(boolean)` | `player.cheats` | Sets flight state; returns true |
| `Player.setInstaMine(boolean)` | `player.cheats` | Sets instant-mining state; returns true |
| `Player.giveItem(itemId, count)` | `player.cheats` | Adds items and returns the number actually added; count defaults to 1 and is clamped to at least 1 |

### `World`

| Function | Permission | Result |
| --- | --- | --- |
| `World.getRenderDistance()` | None | Current render distance |
| `World.setBlock(x, y, z, blockId)` | `world.modify` | Returns whether the block was set; returns false for an unknown block ID |
| `World.vaporizeChunk(value)` | `world.modify` | Attempts to remove the currently targeted chunk and returns whether one was removed. The current implementation does not use the argument. |

### `Renderer`

| Function | Permission | Result |
| --- | --- | --- |
| `Renderer.flushGPU()` | `renderer.control` | Requests a safe GPU flush; returns true |
| `Renderer.setHitboxes(boolean)` | `renderer.control` | Shows or hides hitboxes; returns true |

### `System`

| Function | Permission | Result |
| --- | --- | --- |
| `System.clearCache()` | `system.io` | Clears the cache and returns the number of deleted files |
| `System.openAppFolder()` | `system.io` | Opens the app folder and returns whether the operation succeeded |

## Permissions

A mod can include an optional `permissions.yml` next to its Lua files:

~~~yaml
mod_id: example_mod
name: Example Mod
permissions:
  - player.cheats
  - commands.execute
descriptions:
  player.cheats: Allows changing player cheat settings.
  commands.execute: Allows running console commands.
~~~

The runtime reads the mod ID/name metadata and declared permission names. Protected API use is also scanned from the Lua source. The permission names currently enforced are:

| Permission | Protected operations |
| --- | --- |
| `settings.vanilla.write` | Updating vanilla settings |
| `commands.execute` | `Commands.execute` |
| `player.cheats` | `Player.setFlying`, `Player.setInstaMine`, `Player.giveItem` |
| `world.modify` | `World.setBlock`, `World.vaporizeChunk` |
| `renderer.control` | `Renderer.flushGPU`, `Renderer.setHitboxes` |
| `system.io` | `System.clearCache`, `System.openAppFolder` |

Declaring a permission does not grant it. Mods loaded from disk start without automatic approval; protected operations remain blocked until the user approves the requested permissions. A protected API detected in source but missing from `permissions.yml` remains undeclared and is not granted by approving only the declared permissions.

Permission grants are scoped to an individual mod. One mod's approval does not grant permissions to another mod.

The source inspector is a lightweight pattern scan, not a complete security audit. Only install Lua mods you trust.

## Current limitations

- The current Lua API does not expose a general event bus, tick callback, or Lua command-registration function.
- Mods are loaded from direct child folders under the mods directory; nested Lua files are not discovered.
- The exposed API is limited to the tables and functions documented above. Internal Kotlin classes are not available through Java interop.
- The runtime and API may change while Tessellate is in development.

## Implementation references

- [LuaModRuntime.kt](https://github.com/alert-bake/Tessellate/blob/23151c1effcffb9b355e1dd2ad6c9bf1f7f6b891/app/src/main/java/com/nitrous/tessellate/modding/LuaModRuntime.kt)
- [ModPermissions.kt](https://github.com/alert-bake/Tessellate/blob/23151c1effcffb9b355e1dd2ad6c9bf1f7f6b891/app/src/main/java/com/nitrous/tessellate/modding/ModPermissions.kt)
- [Settings models](https://github.com/alert-bake/Tessellate/blob/23151c1effcffb9b355e1dd2ad6c9bf1f7f6b891/app/src/main/java/com/nitrous/tessellate/settings/SettingModels.kt)
