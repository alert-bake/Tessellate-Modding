# TESSELLATE Custom Command API

This page documents the current custom-command implementation in Tessellate. There are two distinct routes:

1. JSON command definitions for data-driven commands.
2. Kotlin `Command` implementations for commands that need custom executable behavior.

Lua mods currently have `Commands.execute`, but **do not** have a `Commands.register` function.

The implementation references are pinned to source commit [23151c1](https://github.com/alert-bake/Tessellate/commit/23151c1effcffb9b355e1dd2ad6c9bf1f7f6b891).

## JSON command definitions

Tessellate loads JSON command definitions from its bundled `assets/content/commands/` directory and from the app-private `files/content/commands/` directory. Only direct `.json` files are loaded. User content definitions are loaded after bundled definitions, and duplicate command names cause registration to fail.

A definition has this shape:

~~~json
{
  "name": "greet",
  "description": "Displays a greeting.",
  "usage": "/greet",
  "action": "greet",
  "response": "Hello from Tessellate."
}
~~~

| Field | Required | Meaning |
| --- | --- | --- |
| `name` | Yes | Command name. A leading slash is removed and the name is lowercased. |
| `description` | No | Description metadata; defaults to an empty string. |
| `usage` | No | Usage text; defaults to `/<name>`. |
| `action` | No | Built-in action key. Defaults to the command name. |
| `response` | No | Message returned by the generic fallback for an unrecognized action. |

### Important: JSON does not define arbitrary executable actions

The current `JsonCommand` implementation maps these action keys to built-in Kotlin behavior:

- `give`
- `clear`
- `spawn`
- `instamine`
- `fly`

An action key outside that list does not execute custom code. It returns a successful result using the non-empty `response` value, or the fallback text `Executed /<name>`.

For example, the `greet` JSON above is a response-only command. It does not create a new Lua callback or run an arbitrary script.

## Kotlin command interface

For executable custom behavior inside the Tessellate application, implement the Kotlin `Command` interface:

~~~kotlin
interface Command {
    val name: String
    val description: String
    val usage: String

    fun execute(context: CommandContext): CommandResult
}
~~~

The execution context and result are:

~~~kotlin
data class CommandContext(
    val worldScene: WorldScene,
    val camera: Camera3D? = null,
    val args: List<String> = emptyList(),
    val rawCommand: String = ""
)

data class CommandResult(
    val success: Boolean,
    val message: String
)
~~~

Example implementation:

~~~kotlin
class GreetCommand : Command {
    override val name = "greet"
    override val description = "Displays a greeting."
    override val usage = "/greet"

    override fun execute(context: CommandContext): CommandResult {
        return CommandResult(
            success = true,
            message = "Hello from Tessellate."
        )
    }
}
~~~

Register the command before the command registry is frozen:

~~~kotlin
RegistryBootstrap.initialize(
    context = context,
    preFreezeHook = {
        CommandRegistry.register(GreetCommand())
    }
)
~~~

`CommandRegistry.register(command)` rejects blank names, duplicate names, and registration after startup has frozen the registry. Names are normalized by trimming whitespace, removing a leading slash, and lowercasing.

The bootstrap pipeline loads JSON definitions, invokes the optional `preFreezeHook`, and then freezes the command registry. If the registry has already been initialized/frozen, a later registration attempt fails.

## Dispatch behavior

Commands are invoked with a leading slash:

~~~text
/greet
/give tessellate:cobblestone 5
~~~

The dispatcher splits input on whitespace. The first token is the command name; remaining tokens become `context.args`. Quoted multi-word arguments are not grouped by the current parser.

The `CommandContext` contains:

- `worldScene`: current world scene.
- `camera`: current camera, or null.
- `args`: tokens after the command name.
- `rawCommand`: normalized command token.

Return a `CommandResult` to indicate success/failure and provide the message shown by the command console.

## Relationship to Lua mods

Lua mods can call:

~~~lua
local result = Commands.execute("/greet")
print(result.success, result.message)
~~~

This call requires the `commands.execute` permission. It executes a command that is already registered; it does not register one.

The Kotlin `Command` interface and `CommandRegistry.register` are application-side extension points. They are not exposed to Lua and are not currently a standalone script-level mod API.

## Implementation references

- [Command.kt](https://github.com/alert-bake/Tessellate/blob/23151c1effcffb9b355e1dd2ad6c9bf1f7f6b891/app/src/main/java/com/nitrous/tessellate/command/Command.kt)
- [CommandRegistry.kt](https://github.com/alert-bake/Tessellate/blob/23151c1effcffb9b355e1dd2ad6c9bf1f7f6b891/app/src/main/java/com/nitrous/tessellate/command/CommandRegistry.kt)
- [RegistryBootstrap.kt](https://github.com/alert-bake/Tessellate/blob/23151c1effcffb9b355e1dd2ad6c9bf1f7f6b891/app/src/main/java/com/nitrous/tessellate/registry/RegistryBootstrap.kt)
- [CommandDefinitionJson](https://github.com/alert-bake/Tessellate/blob/23151c1effcffb9b355e1dd2ad6c9bf1f7f6b891/app/src/main/java/com/nitrous/tessellate/registry/ContentDefinitions.kt)
