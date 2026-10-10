---
title: A Python loop over a fixed group of literal values iterates a tuple or list literal rather than a set literal
rule_id: PY-117
domain: performance
step: [implement, review]
applies_to: [python]
triggers: ['^\s*(async\s+)?for\s+.+?\s+in\s+\{[^{}:]+\}\s*:', '\bfor\s+[\w\s,()]+?\s+in\s+\{[^{}:]+\}\s*(if\b|for\b|[\])}])']
scope: hunk
check_kind: mechanical
severity_default: minor
---

# A Python loop over a fixed group of literal values iterates a tuple or list literal rather than a set literal

## Thesis
A Python for loop or comprehension whose iterable is a set literal in which each element is a literal iterates a tuple or list literal of the same values instead.

## Rationale
Iterating over a set is less efficient than iterating over a sequence type such as a list or a tuple. A set also leaves its order to the hashes of its elements. By default the hashes of str and bytes objects are salted with an unpredictable random value: they remain constant within one Python process but are not predictable between repeated invocations of Python, and changing hash values affects the iteration order of sets, an order Python has never guaranteed and one that typically varies between 32-bit and 64-bit builds. Hash randomization is enabled by default: with PYTHONHASHSEED unset or set to random, a random value seeds the hashes of str and bytes objects, and an integer value is used as a fixed seed. A loop over a set literal of strings can therefore print, write or register its values in another order on the next run. A tuple or a list is a sequence, a finite ordered set indexed by non-negative numbers, so it iterates in the order its literal lists.

## Example
```python
bad:  def write_all(config):
          for env in {"dev", "staging", "prod"}:
              config.write_section(env)
good: def write_all(config):
          for env in ("dev", "staging", "prod"):
              config.write_section(env)
```

## Limits
Where the elements are neither str nor bytes and the body's effect does not depend on the order, efficiency is the remaining reason. The rule covers iteration over a set literal in which each element is a literal: a set display used for a membership test, a set comprehension, or a set built from values computed at run time is out of reach. PYTHONHASHSEED set to an integer makes the order repeatable between runs that share the seed, yet it remains an order Python has never guaranteed.

## Validator
Grep the hunk for `for ... in {` whose braces hold comma-separated values and no colon. Check that the braces form a set display, not a dict display or a set comprehension, and that every element is a literal: a string, bytes or number. Read the loop body for output, writes, registrations or other effects whose order a reader or a later run observes, and name them in the finding. Validator question: **Does a for loop or comprehension in the hunk iterate a set display whose every element is a literal?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: PY-117`, severity minor, `file`, `symbol`, `code` = the `for ... in {...}` line verbatim from the diff, `fix` = the same values as a tuple literal in the intended order, such as `for env in ("dev", "staging", "prod"):`, in Python, `rationale` = iterating a set is less efficient than iterating a sequence, and for str or bytes elements the set's iteration order can change between runs because their hashes are salted per process).
