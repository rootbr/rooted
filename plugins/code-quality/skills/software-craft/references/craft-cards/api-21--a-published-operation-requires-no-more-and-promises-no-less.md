---
title: A change to a published operation requires no more of its callers, promises them no less, and asks no more of the code that implements or overrides it
rule_id: API-21
domain: interface
step: [design, implement, review]
applies_to: [public-api, library]
triggers: ['\bassert\b|Preconditions[.]check\w*\(|Objects[.]requireNonNull\(|\bthrow new \w*(Argument|State|Range|Type)\w*(Exception|Error)\b|\braise (ValueError|TypeError)\b|\bwhere\s+\w+\s*:|<\s*\w+\s*:\s*\w+|<\s*\w+\s+extends\s|\b(panic!?|Err)\(|errors[.]New\(|fmt[.]Errorf\(|->\s*(Option|Result)<|\|\s*(null|undefined)\b|Optional[\[<]']
scope: base-compare
check_kind: semantic
severity_default: major
---

# A change to a published operation requires no more of its callers, promises them no less, and asks no more of the code that implements or overrides it

## Thesis
A change to a published operation — one that code outside its own codebase calls, implements or overrides — leaves the outside code written against the previous version valid. For callers, the change adds no precondition on the arguments, rejects or newly fails on no input the previous version accepted and its documentation or declaration admitted, and on no undocumented input where the project's compatibility policy protects undocumented behaviour, adds no type bound to a published generic type, and returns no value outside the range the previous version returned. Accepting a wider range of values for a parameter whose declared type stays the same, and returning a value of a more derived type under the same declared return type, are compatible for callers; so is a new failure on a path that only new parameter values or new state can reach. Where outside code implements or overrides the operation — a callback, an interface method, an overridable member — the directions invert for those implementors: the change widens no range of input they are passed and requires no more of the results they return, while a stronger precondition or a weaker postcondition stays compatible for them. Where outside code plays both roles, both sets of constraints apply.

## Rationale
A contract that now requires more of code written against the previous version, or promises it less, makes formerly legal code wrong without any change on its side: a caller that counted on a non-empty result and reads its first element is in error once an empty result is allowed. The set of outside code is open-ended and nobody knows which aspects of the interface it counts on, so the only safe assumption is that every aspect matters to some of it. Compatibility policies divide on undocumented behaviour: one rule set counts a narrower parse that throws new errors as breaking even where the parsing was never specified, another lets behaviour outside the documented contract change in a minor revision, so the Limits carry that division as a project policy. The reverse change is safe for callers: a contract tightened so that callers may assume more, and the implementation must do more, leaves code written assuming less valid. An added type bound reaches every consumer of the generic type, each of which has to start satisfying it. The roles invert when outside code is the implementor, as with callback interfaces: an implementation written for the old precondition legitimately assumed it, so a wider input range hands it values for which it does not function correctly, and a contract tightened to require implementors to provide more could break existing implementations, while one loosened to require them to provide less leaves implementations written under more stringent rules valid. The compatible direction covers values under unchanged declared types: removing a range check on a parameter is compatible for callers, while a change to a declared parameter or return type is a signature change, which this rule does not judge.

## Example
```java
bad:  public void removeAll(List<Item> items) {  // accepted an empty list before
          if (items.isEmpty()) throw new IllegalArgumentException("no items");
          for (Item item : items) remove(item);
      }
good: public void removeAll(List<Item> items) {  // accepted an empty list before
          if (items.isEmpty()) return;
          for (Item item : items) remove(item);
      }
```

## Limits
A role the owning codebase plays exclusively can change with it: an operation that outside code cannot implement or override carries only the caller-side constraints, and an operation whose callers all live in the codebase the same change updates is not reached. The rule compares the base version with the change, for code written against the previous release, not an override with its supertype within one release. Ecosystems differ on breaking changes, from a policy of never permitting them to one that accepts them when the version number signals them: a project whose stated policy accepts a breaking change released under a new major version, or under a major version zero in which anything may change at any time, rejects the finding when the change carries that signal.

A new failure on input whose handling neither the base version's documentation nor its declaration stated is outside the rule unless the project's stated compatibility policy protects undocumented behaviour, since compatibility policies divide on it.

A release below 1.0.0 is outside the rule, except where the project or its package manager treats the leftmost non-zero version component as the breaking-change indicator, as a caret range does; there a change that keeps that component is in the rule.

A check that rejects at entry an input which the base version's documentation already excluded, or which the base version stored only to fail on it in a later call, makes an existing precondition explicit and adds none; it can change which error reports the violation.

## Validator
Grep the hunk for an added argument check — an assertion, a guard that throws or returns an error, a stricter parse — for an added type bound on a type parameter, and for a return that now admits an absent, empty or out-of-range value. Decide whether the operation is published: exported or public and reachable from code outside its codebase, not a private or internal helper. Open the base version of the file with `git show <base_sha>:<path>` and compare the two versions: the inputs the base version accepted without failing, the results it could return, and both doc-comments. Determine which roles outside code plays: caller only, or also implementor of an interface method, an abstract or overridable member or a callback type. For callers, look for an input the base version accepted that now fails, an added precondition or bound, or a result outside the former range; for outside implementors, look for a wider input range passed to them or a stronger requirement on what they return. Set aside a new failure that only new parameter values or new state can reach, a new failure on input that neither the base documentation nor the declaration admitted unless the project's compatibility policy protects undocumented behaviour, a role the codebase plays exclusively, and a change the project context declares as a signalled breaking release. Validator question: **Does the change make a published operation require more of its outside callers or promise them less than the base version did, or pass its outside implementors more input or require more of their results, on a path existing code can reach?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: API-21`, severity major, `file`, `symbol`, `code` = the added check, bound, failure or return quoted verbatim from the diff, `fix` = the previous contract kept for existing code — the formerly accepted input accepted again, the result kept within its former range, the added bound removed — with any stricter behaviour reachable only through new parameter values, in the file's language, `rationale` = the role outside code plays, the input or result whose range changed against the base version, and the existing code the change makes wrong).
