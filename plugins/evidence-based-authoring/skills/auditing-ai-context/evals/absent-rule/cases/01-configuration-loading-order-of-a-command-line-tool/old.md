# Configuration loading in tern

Owner: CLI platform team. Status: in force for tern 3.x.

## Purpose

This note describes how the tern command-line tool finds and reads its configuration before any subcommand runs. Every subcommand relies on the outcome described here, and plugin authors read it to learn which settings reach their code.

## Configuration sources

Tern can take settings from five sources.

- The system file at /etc/tern/config.toml, installed with the package and owned by administrators.
- The user file at ~/.config/tern/config.toml, owned by the person running the tool.
- The project file .tern.toml in the root of the current repository, committed with the code.
- Environment variables whose names start with TERN_ followed by the key in upper case.
- Command-line flags given to the subcommand.

The three files share one format and one set of keys, so any key may appear in any of them.

## Which file is loaded

Tern searches for a file in the order project, user, system, and loads only the first file it finds. That file is called the winning file. The other files are never opened, so none of their keys take effect, even keys the winning file does not mention. A key that the winning file omits takes its built-in default.

| Step | Location | Loaded when |
|------|----------|-------------|
| 1 | Project file | It exists |
| 2 | User file | No project file exists |
| 3 | System file | Neither of the files above exists |

The repository root is the nearest parent directory that contains a .git directory. When there is no repository, the search starts at the user file.

## Environment variables and flags

Once the winning file is read, environment variables are applied on top of it, key by key. Flags are applied last and override both the file and the environment. A variable or flag for an unknown key is reported as an error.

## Consequences for users

A project file must hold every setting the project needs, including personal ones such as the editor and the colour theme, because the user file is ignored once a project file exists. Most teams keep a shared template of personal keys and paste it into each new project file. Administrators who need a setting enforced everywhere cannot rely on the system file, since any user or project file wins over it.

## Values and types

Keys hold strings, integers, booleans or lists. A list in the winning file is used as written. Unknown keys in the winning file produce a warning and are otherwise ignored.

## Diagnostics

The command tern config show prints the path of the winning file followed by every resolved key and its value. Keys that came from an environment variable or a flag are marked with their source. The command tern config path prints only the path of the winning file, which scripts use to decide which file to edit.

## Plugins

Plugins receive the resolved settings after flags are applied. A plugin reads its own section of the winning file, named after the plugin, and cannot see the other files.

## Errors

A syntax error in the winning file aborts the command with the file path and line number. Files that are not loaded are never parsed, so an error in them goes unnoticed until they become the winning file.

## Performance

Loading opens at most one file and finishes in well under a millisecond on a warm cache. The resolved settings are kept in memory for the life of the process.

## Open questions

- Whether tern config show should also list files that were found but not loaded.
- Whether the system file should gain a way to mark keys as locked.
