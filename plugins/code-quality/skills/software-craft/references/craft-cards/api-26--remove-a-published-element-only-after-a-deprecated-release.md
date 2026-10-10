---
title: A published element whose callers the author cannot change is removed or renamed only after at least one release in which it still worked and was marked deprecated
rule_id: API-26
domain: interface
step: [refactor, review]
applies_to: [public-api, library]
triggers: ['(?i)\bBREAKING[ _-]?CHANGES?\b', '(?i)\b(remove[sd]?|delete[sd]?|drop(s|ped)?|rename[sd]?)\b.*\b(deprecated|API|function|method|class|field|parameter)\b', '^\s*(pub(\([^)]*\))?\s+)?(async\s+)?(fn|func|def|class|interface|trait|struct|enum|type)\s+(\([^)]*\)\s*)?\w+', '^\s*export\s+(default\s+)?(async\s+)?(function|class|const|interface|type)\b', '^\s*(public|protected)\s', '(?i)^\W*(removed|deleted|renamed)\b']
scope: base-compare
check_kind: semantic
severity_default: major
---

# A published element whose callers the author cannot change is removed or renamed only after at least one release in which it still worked and was marked deprecated

## Thesis
An element of a published interface whose callers the author cannot change, such as a public function, method, type, field or constant of a released library that code outside its repository may call, is removed or renamed only in a release that follows at least one release in which the element still worked as documented and was marked deprecated. The removal also waits until the deprecation period stated by the project's compatibility policy has passed.

## Rationale
The callers of a published interface are open-ended, and the author cannot know which parts of it they rely on. The safe assumption is that every element matters to some caller, so deleting one breaks that caller. Renaming an element removes it under its old name, and a published set of breaking-change rules lists removing or renaming a member as a disallowed change. A release in which the old element still works and is marked deprecated lets callers move to the new interface before the break. In some languages the compiler warns when code that is not itself deprecated uses an element that carries the deprecation mark, and a runtime deprecation warning can be raised whenever the element is entered. Under semantic versioning, the deprecation should ship in a new minor release, and there should be at least one minor release that contains it before the major release that removes the element. Callers need time to react to the notice. A widely used library's policy observes that most of its users do not notice deprecation warnings and that users sometimes wait more than one or two years before upgrading. Published policies set the period differently. One waits until the warning has appeared in at least two minor releases of the same major version, or in one minor release of an older major version. With yearly releases that means at least two years, and that policy prefers five years before removal. Another removes only after at least two releases on a six-monthly cycle, or after at least one year between deprecation and removal if the cycle changes. A study of the Maven repository found that methods are commonly deleted without deprecation tags being applied.

## Example
```java
bad:  public final class Config {                 // 2.0.0: removed parse(String); never deprecated
          public static Config load(String text) { ... }
      }
good: public final class Config {                 // 1.4.0: parse kept working, deprecated
          /** @deprecated use {@link #load(String)}; removed in 2.0.0 */
          @Deprecated(since = "1.4.0", forRemoval = true)
          public static Config parse(String text) { return load(text); }
          public static Config load(String text) { ... }
      }
```

## Limits
The rule reaches only elements whose callers the author cannot change, and that condition separates it from the opposite practice. Where every caller of an interface lives in the same source tree, one project reworks the interface without keeping its old form. Function names may change and parameters may be reworked, and every use of the interface in the tree is fixed up at the same time. That project deletes an interface no one uses, while the interface that outside programs call stays very stable and will not break. An element that a project documents as internal, outside its public interface, may change or be removed without notice. Under semantic versioning, a library at major version zero is in initial development, and anything may change at any time. A policy may shorten the period in extreme cases, such as a dangerously broken or insecure feature or one no one could reasonably depend on. Another policy exempts fixes for clear bugs. A project context that states such an exception rejects the finding. The rule limits when an element may be removed and does not require that it ever is. Policies differ here. One lets a deprecated element whose upkeep and security risk are small stay indefinitely. Another deprecates only what it intends to remove and discourages the rest with a note in its documentation. The study of the Maven repository found that methods with deprecation tags are never deleted.

## Validator
Grep the hunk for an added public declaration, or a changelog or release-note line that records a breaking change, a removal or a rename. List the files the diff under review changes (`git diff --stat`), and for each source file with removed lines open the base version with `git show <base_sha>:<path>`. List the public functions, methods, types, fields and constants present at base that are missing at HEAD under the same name; a renamed element counts as missing under its old name. Drop elements that are private, unexported, or documented as internal or outside the public interface. Decide from the manifest, the module path and the project context whether the library is published for code outside its repository to depend on. A library whose released version is below 1.0.0 under semantic versioning is outside the rule. So is an element whose callers, by the project context, all live in the repository and are fixed in this diff. At base, look for a deprecation mark on each missing element: a deprecation annotation, attribute or decorator, a deprecation paragraph or tag in its doc comment, or a deprecation warning raised on entry. Where a mark exists, compare the version it names, or the release in which the changelog records it, with the version this diff releases. Read any removal release or period that the notice or the project's policy states. Validator question: **Does the diff remove or rename a public element of a published library that outside code may call, when at base the element carried no deprecation mark, or no release has yet shipped with that mark, or the removal comes before the release or period that its notice or the project's policy states?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: API-26`, severity major, `file`, `symbol`, `code` = the added line of the slice that carries the change, quoted verbatim: the declaration under its new name for a rename, or else the changelog or release-note line that records the removal or rename, or else the added public declaration that matched the trigger, such as the replacement's, `fix` = in the language of the file that declared the element at base (for a changelog or release-note anchor, naming that file), the element restored so that it keeps working as documented, delegating to its replacement where one exists, and marked with the language's deprecation mechanism naming the replacement and the release planned for its removal, with the removal moved to a release after the deprecation period, `rationale` = names the element and its replacement, states that callers outside the repository break on upgrade with no release in which both names work, and names the deprecation period the project's policy sets).
