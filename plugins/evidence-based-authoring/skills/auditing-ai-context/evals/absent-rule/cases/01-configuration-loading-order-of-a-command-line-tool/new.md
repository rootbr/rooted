# Configuration loading in tern

Owner: CLI platform team. Status: in force for tern 4.x.

## Purpose

This note describes how the tern command-line tool finds and reads its configuration before any subcommand runs. Every subcommand relies on the outcome described here, and plugin authors read it to learn which settings reach their code.

## Configuration sources

Tern can take settings from five sources, called layers.

- The system file at /etc/tern/config.toml, installed with the package and owned by administrators.
- The user file at ~/.config/tern/config.toml, owned by the person running the tool.
- The project file .tern.toml in the root of the current repository, committed with the code.
- Environment variables whose names start with TERN_ followed by the key in upper case.
- Command-line flags given to the subcommand.

The three files share one format and one set of keys, so any key may appear in any of them. Several tools look for a dotfile in every parent directory up to the filesystem root. Tern stops its search for the project file at the repository root and never reads a dotfile above it.

## How layers combine

Tern reads every file layer that exists, in the order system, user, project, and merges them key by key. A key set in a later layer overrides the same key from an earlier one, and a key no layer sets takes its built-in default. There is no winning file any more, and every layer that exists contributes the keys it sets. A layer whose file is missing is skipped silently and never makes the command fail.

| Order | Layer | Overrides |
|-------|-------|-----------|
| 1 | System file | Built-in defaults |
| 2 | User file | System file |
| 3 | Project file | User file |

The repository root is the nearest parent directory that contains a .git directory. When there is no repository, the project layer is empty. Precedence comes from the layer a key was read from, not from when the file was last modified.

## Environment variables and flags

After the files are merged, environment variables are applied on top, key by key. Flags are applied last and override every other layer. Some operators expect an environment variable to beat a flag, because the variable is often set by the deployment. That is not the case in tern, where a flag given on the command line always overrides the matching variable. A variable or flag for an unknown key is reported as an error.

## Consequences for users

Personal settings such as the editor and the colour theme belong in the user file, and project settings belong in the project file. A project file does not have to repeat personal settings such as the editor or the colour theme to keep them in effect. Administrators can set organisation defaults in the system file, and users or projects override them only for the keys they set themselves. Adding a project file never hides the user file or the system file as a whole.

## Values and types

Keys hold strings, integers, booleans or lists. Some tools combine lists by concatenating the values from every layer. Tern does not concatenate, and a list set in a higher layer replaces the lower list entirely. Unknown keys in any file produce a warning and are otherwise ignored.

## Diagnostics

The command tern config show prints every resolved key, its value and the layer it came from. Keys that came from an environment variable or a flag are marked with their source. The command tern config layers prints the path of each file layer and whether it exists, which scripts use to decide which file to edit.

## Plugins

Plugins receive the resolved settings after flags are applied. A plugin reads its own section, named after the plugin, merged across all layers like any other key. Plugins see the merged result as one table rather than a separate copy per layer.

## Errors

A syntax error in any existing file aborts the command with the file path and line number. Every existing file is parsed on each run, so an error anywhere is reported at once. Loading never writes to any configuration file, even when a key falls back to its built-in default.

## Performance

Loading opens at most three files and finishes in about a millisecond on a warm cache. The resolved settings are kept in memory for the life of the process.

## Open questions

- Whether tern config show should also print the value each lower layer held for an overridden key.
- Whether the system file should gain a way to mark keys as locked.
