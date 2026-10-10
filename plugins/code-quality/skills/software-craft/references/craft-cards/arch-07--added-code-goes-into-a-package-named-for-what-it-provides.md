---
title: Code a change adds goes into a package or module named for what it provides, not into a catch-all such as util, common, misc, helpers or a single api or types package that collects unrelated code
rule_id: ARCH-07
domain: architecture
step: [design, implement, review]
applies_to: [universal]
triggers: ['^\s*package\s+([\w]+[.])*(utils?|common|commons|misc|helpers?|shared|api|types|interfaces)\s*;?\s*$', '\bfrom\s+([.]+|[\w.]+[.])?(utils?|common|misc|helpers?|shared)\s+import\b|^\s*(from\s+[\w.]+\s+import\s+(\w+\s*,\s*)*|import\s+(\w+[.])*)(utils?|common|misc|helpers?|shared)(\s*,|\s+as\s|\s*#|\s*$)', '\b(from|require\()\s*["''][.]{1,2}/([\w.-]+/)*(utils?|common|misc|helpers?|shared)(/|["''])', '^\s*(pub(\([\w:]+\))?\s+)?(mod|use\s+crate::)\s*(utils?|common|misc|helpers?|shared)\b', '^\s*(import\s+)?(\w+\s+)?"[\w.-]+/([\w.-]+/)*(utils?|common|misc|helpers?|shared)"\s*$']
scope: file
check_kind: semantic
severity_default: minor
---

# Code a change adds goes into a package or module named for what it provides, not into a catch-all such as util, common, misc, helpers or a single api or types package that collects unrelated code

## Thesis
The package or module that receives the code a change adds is named for what it provides. A package named only with a generic word such as util, common, misc or helper, or a single package named api, types or interfaces that holds all the interfaces a program exposes, is broken up: types and functions with common name elements move into their own package, under a name that fits their contents.

## Rationale
The name of a package is a critical piece of its design. A package named util, common or misc gives its clients no sense of what it contains, which makes it harder for clients to use and harder for maintainers to keep focused. Over time such a package accumulates dependencies; where clients are compiled against a package together with its dependencies, these can make compilation significantly and unnecessarily slower, especially in large programs. Naming a package just util, helper, common or similar is usually a poor choice: uninformative names make the code harder to read. Where clients refer to a package by its short name, a generic name is also more likely to collide with other packages a client imports, forcing the client to invent names to tell them apart, and used too broadly it is liable to cause needless import conflicts. A single package of all the interfaces, named api, types or interfaces, suffers the same problems — it grows without bound, gives users no guidance, accumulates dependencies and, where clients refer to it by its short name, collides with other imports. Where clients refer to a package by its short name, a name that fits the contents lets that short name and the exported name work together as one meaningful identifier, as stringset.New does in place of util.NewStringSet.

## Example
```python
bad:  # app/utils.py
      def new_string_set(*items): ...
      # caller
      from app.utils import new_string_set
good: # app/stringset.py
      def new(*items): ...
      # caller
      from app import stringset
      names = stringset.new("c", "a")
```

## Limits
A generic word may still appear as part of a package name; the rule reaches a name that consists of the generic word alone. When a client must import two packages to use either in any meaningful way, combining them is usually the right thing to do, and a few related types whose implementation is tightly coupled can share one package without exposing those details in its public interface. The rule judges which package receives added code and what that package is called; how one class or routine inside a well-named package is divided lies outside it.

## Validator
Grep the hunk for a created or modified file, directory, package declaration or import whose last name segment is only a generic word — util, utils, common, misc, helper, helpers, shared or a similar word — or that names a package api, types or interfaces. Open the receiving package at scope file and list the top-level definitions the change adds to it. For each addition, name what it provides, then check whether a package named for that purpose already exists or whether the addition shares a name element with its neighbours that a package of its own could carry. Pass a name in which the generic word is one part of a name that says what the package provides. Validator question: **Does the change add a definition to, or create, a package or module whose name is only a generic word, or a single api, types or interfaces package collecting the interfaces of the program, when the added code could live in a package named for what it provides?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: ARCH-07`, severity minor, `file`, `symbol`, `code` = the added definition or import line that places code in the generic package, quoted verbatim from the diff, `fix` = the definition moved into a package or module named for what it provides, with the caller's import rewritten, in the file's language, `rationale` = what the generic name fails to tell clients, the dependencies a catch-all package accumulates, and the import collisions its name invites where clients refer to packages by their short names).
