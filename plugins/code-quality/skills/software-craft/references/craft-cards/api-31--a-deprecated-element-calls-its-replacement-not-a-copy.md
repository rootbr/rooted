---
title: A deprecated element whose behaviour a call of its replacement reproduces is implemented by calling the replacement rather than by keeping a separate copy of the logic
rule_id: API-31
domain: interface
step: [implement, refactor]
applies_to: [public-api, library]
triggers: ['#\[deprecated\b', '@[Dd]eprecated\b', '^\s*//\s*Deprecated:', 'DeprecationWarning\b|warnings[.]warn\(.*Deprecat|@warnings[.]deprecated\(', 'signal:duplicate_block']
scope: file
check_kind: semantic
severity_default: minor
---

# A deprecated element whose behaviour a call of its replacement reproduces is implemented by calling the replacement rather than by keeping a separate copy of the logic

## Thesis
A deprecated element that has a replacement, and whose behaviour a call of that replacement can reproduce, is implemented by calling the replacement, passing values for any arguments the replacement adds, rather than by keeping its own copy of the logic the replacement carries.

## Rationale
Forwarding the deprecated element to its replacement means that any performance improvement or bug fix made to the replacement's implementation automatically benefits the callers of the deprecated element, and it avoids copying code. The forwarding call passes the arguments the replacement adds, as an old query method passes a background context to the new context-taking method and an old squaring function passes the exponent 2 to a power function. A deprecation policy gives an old function reimplemented in terms of a new, more general one as its example of deprecated behaviour whose expected maintenance overhead and security risk are small, and lets such behaviour stay indefinitely, or until the situation changes. When that call is the whole body, the deprecated element is trivially expressible in terms of its replacement, and an inliner can replace each of its calls with the body: tool documentation recommends expressing the old element in terms of the new one, where possible, to enable automatic migration, and suggests marking a single-statement deprecated element so that its body is inlined into its callers. One such inliner's documentation states that it takes care to avoid behaviour changes, even subtle ones such as a change in the order in which argument expressions are evaluated, and that replacing a call by the forwarded call can have no effect on the program, so its mechanism is a low-risk way to update large numbers of calls.

## Example
```java
bad:  /** @deprecated Use {@link #load(String, Duration)}. */
      @Deprecated Config load(String path) {
          return parse(read(path, DEFAULT_TIMEOUT));
      }
good: /** @deprecated Use {@link #load(String, Duration)}. */
      @Deprecated Config load(String path) {
          return load(path, DEFAULT_TIMEOUT);
      }
```

## Limits
The rule asks for forwarding where it is feasible: a deprecated element whose behaviour no call of its replacement reproduces is outside it. An API whose whole implementation is redone in a new package, with the old API and implementation left in the old location untouched except for their deprecation markers, is outside the rule: the old and new implementations then coexist independently of one another. For a method that subclasses or implementers override, the call runs the other way: when the new method adds an argument, its default implementation calls the old method, so that pre-existing overrides of the old method continue to work and all calls to the old method continue to work; such a method and its replacement are outside the rule whether or not the new method already calls the old one. A deprecated element with no replacement, an API that is being removed rather than given a new function or method for its behaviour, is outside the rule. The rule judges the deprecated element's implementation; the deprecation notice, the warning at the caller's site, the deprecation period and the migration of callers are judged by their own rules.

## Validator
Grep the added lines for a deprecation marker: a deprecated attribute, annotation or decorator, a deprecated doc-comment tag or deprecation paragraph, or a deprecation warning raised on entry. Take a duplicate-block signal as a hint that a replacement was made by copying an existing body. For each deprecated element the diff adds, marks or changes, open the file and find its replacement: the element its notice names, or the new element the diff adds beside it, in the file or in the diff's other hunks. Skip an element with no replacement; an old package or module that the diff leaves untouched apart from its deprecation markers while the whole API is redone in a new one; and a method that subclasses or implementers override, such as a hook documented for overriding or one that an override in the file or the diff redefines, since for it the replacement's default implementation calls the deprecated method rather than the reverse. Compare the two bodies: check whether the deprecated element calls its replacement or repeats the replacement's logic, the same steps and calls, in a body of its own. When it repeats it, check whether one call of the replacement, with fixed or default values for the arguments the replacement adds, would produce the deprecated element's results; when no such call exists, skip. Validator question: **Does the diff leave a deprecated element carrying its own copy of logic its replacement also carries, where one call of the replacement with values for its added arguments would reproduce the deprecated element's behaviour?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: API-31`, severity minor, `file`, `symbol`, `code` = the deprecated element's first added or changed line, verbatim from the diff, `fix` = the deprecated element's body replaced by one call of its replacement that passes values for the replacement's added arguments, in the file's language, `rationale` = names the deprecated element, its replacement and the logic both carry, which a fix made to the replacement would not reach through the copy).
