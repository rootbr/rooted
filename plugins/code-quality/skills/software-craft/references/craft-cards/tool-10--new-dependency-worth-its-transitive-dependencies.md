---
title: A new dependency is added only when the functionality it supplies is worth the transitive dependencies it brings in
rule_id: TOOL-10
domain: tooling
step: [design, implement]
applies_to: [build-config]
triggers: ['^\s*"[@\w./-]+"\s*:\s*"(\^|~|>=?|<=?|=)?\s*v?\d', '^\s*[\w-]+\s*=\s*("[\^~=<>]?\s*\d+[.]\d+|\{[^}]*\bversion\s*=)', '^\s*["'']?[A-Za-z][\w.-]*(\[[\w,.-]+\])?\s*(==|>=|~=|<=|!=|<|>)\s*\d', '^\s*(require\s+)?[\w.-]+[.][a-z]{2,}/[\w./-]+\s+v\d+[.]\d+', '<artifactId>[^<]+</artifactId>', '\b(implementation|api|compileOnly|runtimeOnly|testImplementation)\s*\(?\s*["''][\w.-]+:[\w.-]+']
scope: callers
check_kind: semantic
severity_default: minor
---

# A new dependency is added only when the functionality it supplies is worth the transitive dependencies it brings in

## Thesis
A package added to the manifest for trivial functionality — a package of at most 35 lines of code and McCabe complexity at most 10 — is taken only when it brings no packages of its own into the project's dependency tree, which the change's lock-file diff shows or, where the project keeps no lock file, the package's own published manifest; otherwise those few lines are written in the project's own code.

## Rationale
Every package the manifest reaches, directly or transitively, becomes part of the implicitly trusted code base, and the risks an added package brings can propagate through multiple levels of dependencies. The transitive count grows faster than the direct count: in one large registry, installing an average package introduces implicit trust in 79 third-party packages and 39 maintainers, and a small, linear increase in direct dependencies leads to a significant, super-linear increase in transitive ones. Typical problems in packaging ecosystems are backward-incompatible package updates and the risk of transitively depending on packages that have become obsolete or inactive; in another large registry, 75.1% of 723,444 dependency relationships are not needed to compile and run the code, and 57% of all relationships are such unneeded transitive dependencies. Trivial packages make up 16.8% of the studied packages of the first registry; only 45.2% of them have tests, though they appear deployment-tested and have test, usage and community interest similar to non-trivial packages, while 11.5% of them have more than 20 dependencies, so the choice of a trivial package needs care. No tooling eliminates the risk involved in reusing code, so the strongest mitigation is a small dependency tree, kept by preferring a bit of copying to adding a new dependency. Where the project keeps a lock file, it describes the exact tree that was generated, and its diff makes the tree changes an added package brings visible in source control.

## Example
```python
bad:  dependencies = [
          "pad-text>=1.0",  # 18 lines, 4 packages of its own
      ]
      from pad_text import pad_left
good: def pad_left(text: str, width: int, fill: str = " ") -> str:
          return text.rjust(width, fill)
```

## Limits
When the package supplies substantial code the project would otherwise write, reuse pays off: libraries that leverage dependencies deliver four times more code than their own while adding only a 4% delay to the time interval between their releases, though libraries with such leverage have 1.6 times higher odds of being vulnerable than libraries with lower leverage. Such a package is selected after its code and tests are evaluated for reuse, since reused software often carries the same or better quality requirements as newly developed software. The separating condition is the size of what the package supplies: a package of at most 35 lines of code and McCabe complexity at most 10 is trivial, and the figures on tests and dependencies were measured on that class. The rule reaches a package the change adds; a declared package the code no longer uses, an imported package left undeclared and a version with a known vulnerability lie outside it.

## Validator
Grep the hunk for a line added to the ecosystem's manifest that declares a new package. Open the lock-file diff of the same change and list the packages that enter with it; where the project keeps no lock file, list the dependencies the package's own published manifest declares. Open the call sites that import the new package and read what the code uses from it; judge from the package's published source or metadata whether it is at most 35 lines of code with McCabe complexity at most 10. Validator question: **Does the change add a package of at most 35 lines of code and McCabe complexity at most 10 that brings packages of its own into the project's dependency tree?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: TOOL-10`, severity minor, `file`, `symbol`, `code` = the added manifest line verbatim, `fix` = the few lines that replace the package at its call site, in the file's language, `rationale` = the package's size and the packages it adds to the project's dependency tree).
