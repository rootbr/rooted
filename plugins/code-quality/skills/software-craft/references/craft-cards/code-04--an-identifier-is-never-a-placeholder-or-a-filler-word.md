---
title: A declared identifier is never a placeholder such as foo, baz or quux and carries no filler word such as Manager or Wrapper that states no purpose
rule_id: CODE-04
domain: code
step: [design, implement, test, refactor]
applies_to: [universal]
triggers: ['(?i)\b(foo|bar|baz|qux|quux|toto|tutu|tata)\b', '(?<![\w.])_+[0-9][0-9_]*\b', '(?i)(manager|wrapper)']
scope: hunk
check_kind: mechanical
severity_default: suggestion
---

# A declared identifier is never a placeholder such as foo, baz or quux and carries no filler word such as Manager or Wrapper that states no purpose

## Thesis
Each identifier a change declares or renames — a variable, constant, parameter, field, routine, method, type or module — states the purpose of what it names. The whole name is a word or phrase with a meaning in the code, not a metasyntactic placeholder such as foo, baz, qux or quux, nor bar, toto, tutu or tata where they stand in as placeholders, each in any casing, and not a string of underscores and digits such as _1 or __1___2. The words of the name say what the entity is or does, so a filler word that states no purpose, such as Manager or Wrapper, gives way to the word for that purpose: a type named for what it is, a routine for what it does.

## Rationale
A name is read at every use site, far from the code that gives the entity its purpose. A name that could stand for any entity leaves the reader to reconstruct that purpose from the code each time: it is hard to memorize what a variable means without a descriptive name, and generic names can lead to hard-to-decipher code. Metasyntactic words are usually placeholders, and two linters ship them as a default denylist: one of three names (foo, baz, quux) that leaves bar out because bar has legitimate uses, and one of six (foo, bar, baz, toto, tutu, tata). The first sits in a lint group that warns by default, together with a lint for names made only of underscores and digits. A filler word such as Manager or Wrapper lengthens a name without saying what the entity is or does; one language's official conventions ask that names make the purpose of the entity clear and advise against these words as meaningless. Replacing the name restores what a name is for: a reader can tell from the name alone what the entity holds or does.

## Example
```go
bad:  type CartManager struct{ ... }
      func (m *CartManager) Add(foo Item, _1 int) { ... }
good: type Cart struct{ ... }
      func (c *Cart) Add(item Item, quantity int) { ... }
```

## Limits
A name made only of underscores, such as a blank or discard identifier, is outside the rule; a digit in the name brings it back in. The rule reaches names the change declares: a name the hunk only calls, reads or passes on, such as a field of a library type, is outside it, and so is a name fixed from outside the change — a member that overrides or implements an inherited one, which one static-analysis rule skips, a name an external format, protocol or generated file dictates, or a word a framework or interface the declaration implements puts in the name. Bar, toto, tutu and tata also occur as ordinary words (bar as the bar of a chart, a unit of pressure or a measure of music); only their use as a placeholder is a finding. Manager or Wrapper that names a thing of the code's domain, such as a person's manager in a staffing system, states a purpose and meets the rule. In test code a placeholder bound to an arbitrary sample value is outside the rule, as one of the two placeholder lints leaves test code out. A generic name such as data or callback is outside the rule; a project that disallows such names states its list as its own rule. A placeholder in a comment, a string or a prose document is not an identifier. A documented project tolerance, such as a repository of samples or tutorials that uses placeholders on purpose, rejects the finding. The rule judges whether a name states a purpose, not its length, abbreviation or casing, and not a placeholder that is only one word of a longer name.

## Validator
Grep the added lines for a placeholder word, a run of underscores and digits, and Manager or Wrapper. For each match, read the line in the hunk and keep it only where the line declares or renames the identifier — a variable, constant, parameter, field, routine, method, type or module — rather than calling, reading or passing on a name defined elsewhere. Check the whole declared name against the placeholders (foo, baz, qux, quux; bar, toto, tutu, tata where the hunk gives them no meaning of the domain; each in any casing) and against a name made only of underscores and digits with at least one digit. Check each word of the name for Manager, Wrapper or a word that likewise states no purpose, and decide from the hunk whether that word is a term of the code's domain or one that a framework or interface the declaration implements supplies. Set aside a discard identifier, an override or implementation of an inherited member, a name an external format or a generated file fixes, and a placeholder bound to a sample value in test code: a file the test_file signal marks, or a test routine or test module the hunk shows. Validator question: **Does an added declaration introduce a name that is a placeholder or a string of underscores and digits, or that carries a filler word such as Manager or Wrapper that states no purpose, where nothing outside the change fixes the name?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: CODE-04`, severity suggestion, `file`, `symbol`, `code` = the added declaration line carrying the name, verbatim from the diff, `fix` = the declaration with the name replaced by one that states what the entity holds, is or does, in the file's language, `rationale` = the placeholder, the underscore-and-digit string or the filler word, and the purpose the replacement names).

## Source
- clippy `disallowed_names`, group `style`, warn by default (rust-lang/rust-clippy, `clippy_lints/src/disallowed_names.rs`, test code skipped; configuration `disallowed-names` in `book/src/lint_configuration.md`; group levels in `README.md`): "Checks for usage of disallowed names for variables, such as `foo`. [...] These names are usually placeholder names and should be avoided."; "NB: `bar` is not here since it has legitimate uses. [...] **Default Value:** `["foo", "baz", "quux"]`" (fetched)
- clippy `just_underscores_and_digits`, group `style` (rust-lang/rust-clippy, `clippy_lints/src/non_expressive_names.rs`): "Checks if you have variables whose name consists of just underscores and digits. [...] It's hard to memorize what a variable means without a descriptive name." (fetched)
- Pylint C0104 `disallowed-name`, option `bad-names` (pylint-dev/pylint, `pylint/checkers/base/name_checker/checker.py`): "Used when the name matches bad-names or bad-names-rgxs- (unauthorized names)."; default `("foo", "bar", "baz", "toto", "tutu", "tata")`; a method that overrides a base-class method is skipped (fetched)
- ESLint `id-denylist` (eslint/eslint, `docs/src/rules/id-denylist.md`; `lib/rules/id-denylist.js`, `defaultOptions: []`): "Generic names can lead to hard-to-decipher code. This rule allows you to specify a deny list of disallowed identifier names to avoid this practice."; it "will not catch disallowed identifiers that are: function calls [...] object properties" (fetched)
- Kotlin Coding Conventions, Naming rules → Choose good names (JetBrains/kotlin-web-site, `docs/topics/coding-conventions.md`): "The name of a class is usually a noun or a noun phrase explaining what the class _is_"; "The names should make it clear what the purpose of the entity is, so it's best to avoid using meaningless words (`Manager`, `Wrapper`) in names." (fetched)

Caveat: these are tool rules and one official convention; they document the practice and its reason, not a measured cost, and each default list names the placeholders its tool checks rather than every placeholder.
