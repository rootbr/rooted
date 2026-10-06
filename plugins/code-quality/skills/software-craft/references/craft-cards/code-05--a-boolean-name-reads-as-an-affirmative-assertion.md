---
title: A boolean's name reads as an affirmative assertion that is true or false, never as a bare noun or a negation
rule_id: CODE-05
domain: code
step: [design, implement, refactor]
applies_to: [universal]
triggers: ['(\b|_)([Nn]ot|[Nn]o|[Cc]annot|[Cc]ant|[Dd]ont)(_|[A-Z])|[a-z](Not|No|Cannot|Cant|Dont)[A-Z_]', '\b(bool|Bool|boolean|Boolean|BOOL)\b', '\w+\s*:?=\s*(true|false|True|False)\b', '\b([Ff]lag|[Ss]tatus|[Ss]tate|[Mm]ode|[Rr]esult)\s*(:\s*\w+\s*)?:?=[^=]']
scope: file
check_kind: mechanical
severity_default: suggestion
---

# A boolean's name reads as an affirmative assertion that is true or false, never as a bare noun or a negation

## Thesis
A boolean local variable, field or property, and a routine that returns a boolean without changing state, is named so that each use reads as an assertion about its subject, true when the assertion holds: found, isEmpty, canSeek, intersects(other), each in the language's casing convention. The phrase names the proposition and not only the subject (sourceFound or isOpen rather than status or flag). The name of a variable, field or property is an affirmative phrase that carries no negation word such as not, no, cannot, cant, dont or doesNot (canSeek rather than cantSeek, found rather than notFound, isValid rather than isNotValid). Where the language's convention names accessors with a get prefix, a boolean accessor takes the predicate form (isReady, hasValues, canCommit) in place of get. An is, can or has prefix is optional where the phrase already reads as an assertion.

## Rationale
A boolean has two values, and its name is where a reader first learns which state true stands for. An assertion-shaped name makes each test read as the statement it checks: a condition on found holds exactly when the thing was found, a call such as line.intersects(other) reads as a sentence about its subject, and a caller knows at a glance what a routine answers before reading its documentation. A bare noun names the subject without the proposition, so the reader opens the assignment to learn whether true means open or closed, passed or failed. A negation word inverts the reading: true stands for an absence, the test for presence becomes a double negation such as !notFound that the reader resolves by hand, while the affirmative name writes the same test with no negation and the opposite test with one. A get prefix, in a language whose accessors take one, presents a yes-or-no answer as a retrieved value, and the predicate form tells the reader the result is boolean. The reading as an assertion applies to uses that leave state unchanged; a routine with side effects reads as an imperative verb phrase naming its action, whatever it returns.

## Example
```rust
bad:  let flag = items.iter().any(|item| item.expired);
      let mut not_found: bool = true;
      if cache.contains_key(&key) { not_found = false; }
      if !not_found && flag { ... }
good: let any_expired = items.iter().any(|item| item.expired);
      let found = cache.contains_key(&key);
      if found && any_expired { ... }
```

## Limits
A routine that changes state and returns a boolean reporting its outcome, such as whether an insert added the element or a lock was acquired, is named for its action as an imperative verb phrase and meets the rule. A state-preserving routine is judged on the bare-noun and get-prefix forms only: a negated predicate such as isNotEmpty, declared beside isEmpty, is a complement a caller uses in place of a negation operator. A name fixed outside the change, by the inherited declaration of an overriding or implementing routine, a serialized field or column, or an external option such as a command-line flag, is judged where it was declared, and a constant is outside the rule. A plain routine parameter is outside the rule. An adjective or participle that carries no negation word, such as empty, missing, disabled or hidden, is outside this rule's check, which targets a negation word in the name. A predicate-shaped name on a value that is not boolean, such as isValid returning a number, is a different defect and outside this rule. Where the project context configures a required prefix list for boolean names (for example is, has, can, should, did, will), that list decides the prefix; without one, the prefix is optional.

## Validator
Grep the added lines for a declaration, field, property or routine signature whose type or return type is boolean, an assignment of a boolean literal, an assignment to one of the bare nouns flag, status, state, mode or result, and a name carrying a negation word (not, no, cannot, cant, dont, doesNot, isNot, hasNo, in any casing convention and at any position in the name). In the hunk and the enclosing file, confirm the name is boolean from its declared type, its initializer (a comparison, a predicate call, a boolean literal) or its use as a whole condition, and read it inside the conditions that test it. Check three forms: a bare noun (status, flag, state, mode, result) that names a subject but not what true asserts; a negation word in the name of a variable, field or property; and, in a language whose accessor convention uses a get prefix, a get-prefixed routine returning a boolean. Skip a routine that changes state, a name fixed by an overridden or implemented declaration, a constant, a serialized field or an external option, a plain routine parameter, and an adjective or participle that carries no negation word (empty, missing, disabled, hidden, visible, enabled, found). Validator question: **Does an added boolean local variable, field or property carry a bare noun or a negation word, or an added state-preserving boolean-returning routine carry a bare noun or a get prefix where the language's accessors take one, in place of a phrase that asserts what true means?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: CODE-05`, severity suggestion, `file`, `symbol`, `code` = the added line declaring the boolean or its accessor, quoted verbatim from the diff, `fix` = the declaration and one of its tests renamed to the affirmative assertion, with each negated test inverted, in the file's language, `rationale` = the name, which form it takes (bare noun, negation word, get prefix) and the assertion that replaces it).

## Source
- .NET design guidelines, Names of Type Members § Names of Properties (dotnet/docs, `docs/standard/design-guidelines/names-of-type-members.md`): "DO name Boolean properties with an affirmative phrase (`CanSeek` instead of `CantSeek`). Optionally, you can also prefix Boolean properties with "Is", "Can", or "Has", but only where it adds value." (fetched)
- IntelliJ IDEA inspection `NegativelyNamedBooleanVariable` (JetBrains/intellij-community, `java/java-impl/resources/inspectionDescriptions/NegativelyNamedBooleanVariable.html`): "Reports negatively named variables, for example: `disabled`, `hidden`, or `isNotChanged`."; "Usually, inverting the `boolean` value and removing the negation from the name makes the code easier to understand."; disabled and hidden, which the inspection also reports, fall outside this rule's check (fetched)
- Swift API Design Guidelines § Strive for Fluent Usage, `#boolean-assertions` and `#name-according-to-side-effects` (swiftlang/swift-org-website, `documentation/api-design-guidelines/index.md`): "Uses of Boolean methods and properties should read as assertions about the receiver when the use is nonmutating, e.g. `x.isEmpty`, `line1.intersects(line2)`."; "Those with side-effects should read as imperative verb phrases" (fetched)
- PMD `BooleanGetMethodName`, category codestyle (pmd/pmd, `pmd-java/src/main/resources/category/java/codestyle.xml`): "Methods that return boolean or Boolean results should be named as predicate statements to denote this. I.e., 'isReady()', 'hasValues()', 'canCommit()', 'willFail()', etc. Avoid the use of the 'get' prefix for these methods."; skips overrides and, by default, methods with parameters (fetched)
- SonarSource S2047 (SonarSource/sonar-java, `sonar-java-plugin/src/main/resources/org/sonar/l10n/java/rules/java/S2047.html`): "Well-named functions can allow the users of your code to understand at a glance what to expect from the function - even before reading the documentation. Toward that end, methods returning a boolean should have names that start with "is" or "has" rather than with "get"."; "Overriding methods are excluded." (fetched)
- detekt `BooleanPropertyNaming` (detekt/detekt, `detekt-rules-naming/src/main/kotlin/dev/detekt/rules/naming/BooleanPropertyNaming.kt`): "Reports boolean property names that do not follow the specified naming convention."; noncompliant `val progressBar: Boolean = true`, compliant `val hasProgressBar: Boolean = true`; default pattern `^(is|has|are)`, constants and overrides skipped (fetched)
- typescript-eslint `naming-convention` § Enforce that boolean variables are prefixed with an allowed verb (typescript-eslint/typescript-eslint, `packages/eslint-plugin/docs/rules/naming-convention.mdx`): `"selector": "variable", "types": ["boolean"]`, `"prefix": ["is", "should", "has", "can", "did", "will"]` (fetched)
- Kotlin standard library `Collection<T>.isNotEmpty()` (JetBrains/kotlin, `libraries/stdlib/src/kotlin/collections/Collections.kt`): "Returns `true` if the collection is not empty."; declared as `public inline fun <T> Collection<T>.isNotEmpty(): Boolean = !isEmpty()` (fetched)
- Caveat: the backing is style guidance and lint rules that are opt-in or off by default; a controlled experiment that varies negation written into variable names (doi:10.1145/3702652.3744213) was located through a search summary that states its design but not its result for names, and none on noun names was found, so the card carries no number.
