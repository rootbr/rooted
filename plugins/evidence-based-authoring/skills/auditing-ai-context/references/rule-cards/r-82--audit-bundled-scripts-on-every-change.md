---
title: Bundled scripts and binaries must be audited each time the skill changes
rule_id: R-82
applies_to_target: [skill]
check_kind: mechanical
severity_default: medium
---

# Bundled scripts and binaries must be audited each time the skill changes

## Thesis
For any script under `scripts/`, `bin/`, or referenced via `Bash` in the skill, the skill body must declare four things: what the script does (one-line summary), what inputs it reads, what outputs it writes, and what privileges it requires. The script must be re-reviewed on every skill update, and its dependencies pinned to immutable hashes rather than version ranges, since an automatic update is an unconsented content change.

## Rationale
Skills that bundle executable scripts are 2.12× more vulnerable than text-only skills. A required documentation gate — summary, inputs, outputs, privileges — makes the script's behavior auditable and prevents silent drift, where a script's effect changes without any visible change to the prose a reviewer reads.

## Example
```
bad:  "Run scripts/process.sh on the input."
good: "scripts/process.sh: normalizes the input file (reads $1, writes
      stdout, no network/root). Pinned dep sha256:…; re-audit on bump."
```

## Limits
Applies to skills that reference or bundle executable scripts or binaries. A text-only skill with no script reference is out of scope. The four-item declaration is the minimum; it documents behavior but does not by itself verify the script is safe.

## Validator
Inventory all scripts referenced from the skill (`scripts/`, `bin/`, or any `Bash` invocation). For each, check whether the body documents the four items: summary, inputs, outputs, privileges. Any missing item, or a dependency pinned to a version range rather than an immutable hash, is flagged. Validator question: for every bundled script, can a reviewer learn its behavior and privileges from the body alone, and are its dependencies hash-pinned?

## Patch output
When auditing an undocumented or range-pinned script reference, emit one patch (`rule_id: R-82`, `location.script_path` = path, severity medium) proposing the four-item declaration added to the skill and re-audit on each version bump.

## Source
Liu 2601.10338 §1 (script-bundling skills 2.12× more vulnerable, OR=2.12, p<0.001); OWASP Agentic Skills Top 10 v1.0 AST07 (dependencies pinned to immutable hashes).
