---
title: A parameter its routine never reads is removed with its arguments when every caller is in the repository and no override, interface, trait or callback type fixes the routine's signature
rule_id: CHG-09
domain: change
step: [implement, refactor, review]
applies_to: [universal]
triggers: ['^\s*(?:async\s+)?def\s+\w+\s*\(', '\bfunction\b\s*\*?\s*\w*\s*\(|\([^()]*\)\s*(?::\s*[^=;{]+)?=>', '^\s*func\s+(?:\([^)]*\)\s*)?\w+\s*[(\[]', '^\s*(?:pub(?:\([^)]*\))?\s+)?(?:(?:async|const|unsafe)\s+)*fn\s+\w+', '^\s*(?:(?:public|protected|private|internal|static|final|synchronized|abstract|override|async)\s+)+(?:<[^>]+>\s+)?(?:[\w<>\[\],.?]+\s+)?\w+\s*\([^)]*\w', '^\s*(?:(?:static|async)\s+)*\*?#\w+\s*\([^)]*\)\s*(?::\s*[^{=;]+)?\{']
scope: callers
check_kind: semantic
severity_default: minor
---

# A parameter its routine never reads is removed with its arguments when every caller is in the repository and no override, interface, trait or callback type fixes the routine's signature

## Thesis
A parameter that its routine's body never reads is removed, together with the corresponding argument at every call site, when both conditions hold: every caller is in the repository, because the routine is private or unexported, or an effectively private member such as a public member of a private class; and nothing outside the routine fixes its parameter list, because the routine overrides or implements no inherited, interface, trait or protocol member, is not an interface default method, and is never used as a value whose function type may require the parameter. A method's receiver, the parameter naming the instance or class the method is called on, is not such a parameter. An argument expression with side effects keeps its effect at the call site when the argument is removed. A parameter kept because its signature is fixed carries the marker that unused-parameter checkers exempt (a blank name, a leading underscore, or a name beginning with unused or ignored) where callers pass it only by position; where a caller may pass it by name, the parameter keeps its declared name, and an override carries the language's override marker. Where a family of implementations and overriders is private to the repository and none of its methods reads a parameter, the parameter is unused across the family and may be removed from every declaration and call.

## Rationale
Whatever value a caller passes for an unread parameter, the routine's behaviour is the same, so the programmer's intention is no longer clearly expressed and the parameter can lead to confusion; an unread parameter may also indicate a bug. A parameter of a private or unexported routine can be removed safely together with the argument each caller in the repository passes for it. Removing one from a public routine can ripple through the code base, and an exported routine may be taken as a value in another package. An override, an implementation of an interface member and a routine used as a value may be required to conform to a signature declared elsewhere, so their parameter lists stay as they are.

## Example
```python
bad:  def _total(items, currency):
          return sum(item.price for item in items)
      amount = _total(cart.items, "EUR")
good: def _total(items):
          return sum(item.price for item in items)
      amount = _total(cart.items)
```

## Limits
An unread parameter may indicate a bug: where the body was meant to read it, the fix is the missing read rather than the removal. A routine whose body is empty or consists only of raising an error or panicking is often a stub, and some checkers leave its parameters unchecked whatever the routine's visibility, so the validator passes it. A routine whose annotation lets a framework call it is reached from the framework's internals, and checkers treat such annotated code as used or exempt annotated methods. A public or exported routine is outside the rule: it may be called or taken as a value in another package, and removing its parameter can ripple through the code base.

## Validator
Grep the hunk for added or changed routine signatures and for changed routine bodies. For each parameter of a touched routine other than a method's receiver, trace whether the body reads it anywhere, a nested closure included. Open the routine's declaration and its references at scope callers: confirm the routine is private, unexported, or a member of a private class; confirm it overrides or implements no inherited, interface, trait or protocol member (a same-named method of an interface in the same package counts), is not an interface default method, carries no framework annotation, and is never referenced as a value rather than called. Pass a parameter with a blank name or an unused marker, and a body that is empty or only raises or panics. Validator question: **Does a routine touched by the hunk, whose body is neither empty nor only raises or panics, declare an unmarked parameter other than a method's receiver that its body never reads while every caller is in the repository and no override, implementation, interface default, framework annotation or use as a value fixes its signature?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: CHG-09`, severity minor, `file`, `symbol`, `code` = the routine's signature line with the unread parameter, verbatim from the diff, `fix` = the signature without the parameter and each call site without its argument, an argument with side effects kept as its own statement, in the file's language, `rationale` = names the unread parameter, the visibility that keeps every caller in the repository, and the absence of any override, implementation or use as a value that fixes the signature).
