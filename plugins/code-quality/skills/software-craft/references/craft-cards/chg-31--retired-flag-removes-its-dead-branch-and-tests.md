---
title: Retiring a flag that switched between an old and a new path removes the flag's checks, the branch no longer taken, the code only that branch reached and the tests of that branch
rule_id: CHG-31
domain: change
step: [refactor, review]
applies_to: [universal]
triggers: ['(?i)\bfeature[_-]?(?:flag|gate|toggle|switch)', '(?i)\b(?:is|get)?_?(?:feature|flag|toggle)_?(?:enabled|on|active)\s*\(', '(?i)\btoggle', '^\s*(?:\}\s*)?(?:if|elif|else\s+if)\s*\(?\s*(?:true|false|True|False)\s*\)?\s*(?:\{|:|$)', '(?i)\b(?:use|enable)_?new[A-Z_]\w*']
scope: callers
check_kind: semantic
severity_default: minor
---

# Retiring a flag that switched between an old and a new path removes the flag's checks, the branch no longer taken, the code only that branch reached and the tests of that branch

## Thesis
When a flag that selected between an old and a new path is retired because the purpose that introduced it is resolved and it has been rolled out 100% with one value, the retiring change makes the settled branch run unconditionally, deletes the branch no longer taken, deletes the code that becomes unreachable once that branch is gone, deletes the tests set to the dropped value and removes the flag setting from the tests of the settled branch. The flag's declaration, its configuration entries in the repository, and an assignment that stores the flag's value or a routine that returns it are leftovers too, deleted once that value is a constant. Fixing the flag's value in configuration or in a constant while its checks and its old branch stay in the code leaves the flag in place and does not retire it.

## Rationale
A flag whose execution path is the same on every instance still leaves a control path in the code, and that code is dead only because of the value a flag lookup returns, which may query a remote configuration, so compiler dead-code elimination cannot remove it. While the path stays, a corrupted payload from the backend can alter the program's behaviour through it, effort goes into keeping test coverage of a path nobody needs, the dead code and its tests add to build and test time, and every reader has to reason about the obsolete path. In a reported outage, flipping the behaviour of a feature flag made obsolete code live. The cleanup after a flag's goal is accomplished is not always performed; oftentimes the code of obsolete flags is not cleaned up and accumulates as technical debt. The removal is a syntax-level rewrite: each check of the flag becomes its settled constant, each condition on that constant becomes the branch it selects, the flag's declaration goes, assignments and wrapper routines whose value becomes a constant go, and tests set to the dropped value go. The removal usually reaches beyond the file that holds the check, so the reviewer looks for the dead branch, its exclusive code and its tests across the change, not in one file: in one industrial deployment a tool generated cleanup diffs for 1381 flags, around 80% of them touching more than one file, over 85% compiling and passing tests, and 65% landing without any change, with only one of its three variants removing assignments and wrapper routines and only one removing tests.

## Example
```python
bad:  def price(order):  # this diff deleted the "use_new_pricing" registration
          if toggles.is_feature_enabled("use_new_pricing"): return new_price(order)
          return legacy_price(order)
      def refund(order):
          if True: return new_refund(order)
          return legacy_refund(order)
      @feature_flag("use_new_pricing", False)
      def test_price_legacy(): ...
good: def price(order): return new_price(order)
      def refund(order): return new_refund(order)
```

## Limits
Changing a flag's value or rollout share while every lookup of the flag stays is a rollout, not a retirement, and is outside the rule: even when a flag is rolled out, its developer may not yet be ready to eliminate it. A flag that is completely rolled out yet serves as a kill switch whose value can be changed in an emergency, or that controls monitoring or debug information, is not stale, and keeping its checks is correct. A flag not yet rolled out 100% for one value is still used to test multiple behaviours and is outside the rule. Code the deleted branch called stays when another path still reaches it; reachability cannot be decided in a sound and complete manner, so deleting what the branch reached needs a developer to check its other callers. A test that changes the flag's state and also checks functionality that survives keeps that functionality with the state change removed; only a test whose functionality is removed is deleted whole. When the configuration infrastructure requires removal in separate steps, first the conditional, then all configuration settings, and finally the configuration declaration, each going through code review and continuous integration separately, a change that completes one step in that order is a stage of the retirement, and the parts owned by the later steps are not its leftovers. Disabling the flag in the flag management system is part of the same retirement and lies outside the source the rule reads.

## Validator
Grep the hunk for a flag constant, a flag lookup or a configuration entry that the diff deletes or replaces with a fixed value, and for a condition on a literal true or false. When the diff starts retiring a flag, by deleting its declaration, registration or configuration entry or by replacing a check or lookup of it with a literal or constant, open its readers at scope callers: each condition that reads the flag, the branch it no longer takes, routines only that branch calls, and tests that set the flag. When the diff removes a check, trace the deleted branch's callees and the tests that set the flag to the dropped value. Skip a diff that only changes a flag's value or rollout share, a flag its definition documents as a kill switch or a monitoring or debug switch, and a flag still in partial rollout. Validator question: **Does the diff retire a flag, or replace a check or lookup of it with a literal or constant, while a check of that flag, the branch it no longer takes, code only that branch reaches, or a test set to the dropped value stays in the code, or leave the flag's declaration, a configuration entry for it, or an assignment or routine that only stores or returns its value in place while nothing else needs them?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: CHG-31`, severity minor, `file`, `symbol`, `code` = the flag check, constant, configuration line or test that stays, quoted verbatim from the diff or, when it lies outside the diff, from the file read at scope callers, `fix` = the routine with the settled branch inlined and the old branch, its exclusive callees and its tests deleted, in the file's language, `rationale` = the flag's settled value and the branch, code and tests left behind).
