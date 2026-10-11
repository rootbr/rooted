---
title: An import or dependency ban that a change adds to an analyzer or dependency-check configuration names the replacement where the project chose one, and otherwise carries a message stating why the dependency is banned or linking the decision record
rule_id: ARCH-44
domain: architecture
step: [implement, review]
applies_to: [build-config]
triggers: ['(?i)no-restricted-(imports|modules|paths)\b|banned[-_]?api\b|\bTID251\b|\bdepguard\b|\bgomodguard\b|^\s*-\s*(pkg|module)\s*:|[.]msg\s*=\s*\x22|^\s*deny\s*=\s*\[|\buse-instead\b|^\s*\[bans\]|\bdeny\s*=\s*\[\s*[{\x22]|\{\s*crate\s*=\s*\x22|^\s*\x22?(forbidden|allowed)\x22?\s*:\s*\[|\bpathNot\b']
scope: hunk
check_kind: mechanical
severity_default: suggestion
---

# An import or dependency ban that a change adds to an analyzer or dependency-check configuration names the replacement where the project chose one, and otherwise carries a message stating why the dependency is banned or linking the decision record

## Thesis
An entry that a change adds to an analyzer or dependency-check configuration to ban an import, a module or package, or a dependency between modules states why the dependency is banned. Where the project has chosen another component for that functionality, the entry names that component, in the tool's replacement field where it has one or in the message, and that name states the reason. Where the project has chosen none, the entry fills its reason, message or comment field with why the dependency is banned, as text or as a link such as one to the decision record.

## Rationale
Where the tool surfaces the reason in its diagnostic output or appends the message to the lint error, the developer whose dependency the check rejects does not have to dig through history or ask the maintainers why the dependency is banned. Without a reason or a replacement, that developer receives the rule's default error alone. One dependency-check tool calls its replacement field a shorthand for the most common case for banning a package, that the project has chosen another component for that functionality, so the replacement's name states the reason. A restricted-import rule's documentation adds the cost of leaving the alternative in use: a second component would bloat the project and cost the maintenance of two dependencies where one would suffice. Several tools carry the replacement in a field of its own, such as a use-instead value, a list of alternative modules to suggest in the lint error, or a deny map whose value is a suggestion on what to use instead. A boundary tool that forbids dependencies between modules provides a comment field to document why the rule is there, though no rule logic reads it.

## Example
```rust
bad:  // deny.toml
      // [bans]
      // deny = [{ crate = "legacy-tls" }]
good: // deny.toml
      // [bans]
      // deny = [{ crate = "legacy-tls", use-instead = "chosen-tls", reason = "one TLS stack: docs/decisions/0007-tls-backend.md" }]
```

## Limits
The replacement half applies only where the project chose another component for that functionality; a ban with no replacement, such as a family of packages none of which is permitted or old versions with a known bug, carries the reason alone. A tool whose ban entry has no reason, message, comment or replacement field is outside the rule. The rule reaches the entries the hunk adds; an existing entry the change leaves untouched is outside it. A ban added to fence a migration off an old path while its callers move is governed by the migration rules of the change domain.

## Validator
Grep the hunk for added lines in a lint, analyzer or dependency-check configuration that ban an import, a module, a package or a dependency between modules: restricted-import entries, banned-API maps, deny lists of packages, blocked-module lists, forbidden dependency rules. For each added entry, read the fields it sets within the hunk. An entry that names a replacement component in its replacement field or message states why. For an entry that names none, check whether its reason, message or comment field states why the dependency is banned, as text or as a link; a field that only restates the ban, such as "X is banned", states no reason. Then check whether the hunk itself shows a component the project chose instead, such as a comment or a neighbouring ban entry in the hunk that names it, and whether the added entry names it in its replacement field or message. Validator question: **Does an entry this hunk adds to a ban or boundary configuration name no replacement while its reason, message or comment field is empty or restates the ban, or omit a replacement the hunk shows the project chose?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: ARCH-44`, severity suggestion, `file`, `symbol` = the banned module, package or dependency, `code` = the added ban entry quoted verbatim from the diff, `fix` = the same entry in the configuration's own syntax with its replacement field or message naming the chosen component, or, where the project chose none, its reason or message field stating why or linking the decision record, `rationale` = names the banned dependency and that the rejecting diagnostic otherwise reaches the developer without the reason or the replacement).

## Source
- cargo-deny, `[bans]` section, `deny.reason` and `deny.use-instead` (EmbarkStudios/cargo-deny, docs/src/checks/bans/cfg.md) (fetched): "This field provides the reason the crate is banned as a string (eg. a simple message or even a url) that is surfaced in diagnostic output so that the user does not have to waste time digging through history or asking maintainers why this is the case." … `deny = [{ crate = "openssl", use-instead = "rustls"}]` … "This is a shorthand for the most common case for banning a particular crate, which is that your project has chosen to use a different crate for that functionality."
- ESLint `no-restricted-imports` (eslint/eslint, docs/src/rules/no-restricted-imports.md) (fetched): "Your project may have standardized on a module. You want to make sure that the other alternatives are not being used as this would unnecessarily bloat the project and provide a higher maintenance cost of two dependencies when one would suffice." … "(The custom message is appended to the default error message from the rule.)"
- gomodguard, configuration reference (ryancurrah/gomodguard, README.md) (fetched): "`recommendations` … Alternative modules to suggest in the lint error." "`reason` … Human-readable explanation appended to the lint error." Examples: `reason: "No badcompany packages are permitted."`, `reason: "old versions have a known bug."`
- depguard v2, § Config, Deny (OpenPeeDeeP/depguard, README.md) (fetched): "Deny is a map where the key is a prefix of the package to deny, and the value is a suggestion on what to use instead."
- Ruff TID251 `banned-api` (astral-sh/ruff, crates/ruff_workspace/src/options.rs) (fetched): "Specific modules or module members that may not be imported or accessed." `value_type = r#"dict[str, { "msg": str }]"#` … `"typing.TypedDict".msg = "Use typing_extensions.TypedDict instead."`
- dependency-cruiser rules reference, `comment` and `name` (sverweij/dependency-cruiser, doc/rules-reference.md) (fetched): "You can use this field to document why the rule is there. It's not used in any rule logic." … "'not-to-core' for a rule forbidding dependencies on core modules".
- Caveat: the evidence is tool documentation defining these fields and their purpose; it carries no measurement of the time a reason saves.
