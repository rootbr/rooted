---
title: A declaration is widened for tests at most to the package or module level a co-located test needs, not to public, exported or protected visibility
rule_id: DSN-35
domain: design
step: [implement, test]
applies_to: [universal]
triggers: ['(?i)(//|#|/\*|\*|""").*\b(visible|visibility|public|exported?|exposed?|pub|accessible|protected)\b.*\b(for|by|from|in|so)\s+(that\s+)?(the\s+)?(unit\s+)?test(s|ing|ab(le|ility))?\b', '\b\w*(ForTests?|ForTesting|TestOnly|_for_tests?|_for_testing|_test_only)\b', '^\s*(export\s+|pub(\([\w:\s]+\))?\s+|public\s+)?(type|class|struct|interface|func|fn)\s+(New)?(Fake|Mock|Stub|Spy)[A-Z]\w*']
scope: callers
check_kind: semantic
severity_default: minor
---

# A declaration is widened for tests at most to the package or module level a co-located test needs, not to public, exported or protected visibility

## Thesis
A test reaches a hidden member through the public interface, or from a place that already has access to it: a test file in the same package, or a child test module of the module under test. Where a test still needs more, the member is relaxed at most to the package or module level a co-located test needs. A declaration made public, exported or protected only so that a test can reach it, a private-name mark dropped only for a test, and a test-double implementation exported from the production API that consumes its interface break the rule, whatever a comment or an annotation says about who may call it.

## Rationale
A public or protected declaration is open to any code that sees it: a mark saying it exists for tests does not prevent anyone from using it, and experience has shown that other code will. If the widened member breaks the encapsulation of its type, the type's internal representation becomes hard to change. Where privacy is only a naming mark, a name without the mark is a public attribute, one that unrelated clients are expected to use with a commitment to avoid backward-incompatible changes, while a marked name carries no guarantee that it will not change or be removed; making a member public later is easier than making a public member non-public again. A test-double implementation exported beside the real one adds an exported type, every exported type increases the reader's cognitive load, and the reader has to understand the interface, the real implementation and the double, three entities where one would do. A mark on a member relaxed for testing lets tools tell the relaxation from an oversight: a field-visibility check ignores the member because the mark shows that its visibility was purposely relaxed to make the code testable, and an internal-API check reports each use of it from code that is neither a test nor the declaring type, since code that uses a member meant only for its defining library or package can behave incorrectly when that type changes. A co-located test can reach a hidden member with no widening in several ways: a test file in the same package may refer to the package's unexported identifiers; a child test module may access any item of its parent, so internal details can be tested from it; a type checker that keeps private members soft private admits index access to them, which can make them easier to reach from unit tests; and unit tests may read the protected constants of the module under test.

## Example
```go
bad:  // ResetForTesting is exported for tests; production code must not call it.
      func ResetForTesting() { entries = map[string]int{} }
      type FakeClock struct{ Now int64 } // implements the Clock this package consumes; exported for tests
good: func reset() { entries = map[string]int{} }
      // cache_test.go declares package cache, so its tests call the unexported reset;
      // FakeClock moves to package cachetest beside the tests that use it.
      func TestLookupMiss(t *testing.T) {
          reset()
          ...
      }
```

## Limits
- Contested. One position designs the API to be tested through its public interface and defines no back doors only for tests; the other accepts relaxing a member's visibility to make the code testable. The level of the widening separates the cases. Widened to public or protected, a for-testing mark is a fig leaf for bad design that prevents no one from using the declaration, and a test-double implementation is not to be exported from the API that consumes its interface. Relaxed to the package level and marked, the member is ignored by a field-visibility check because the mark shows that its visibility was purposely relaxed to make the code testable, and a child test module reaches every item of its parent, so internal details can be tested with no widening at all. One field-visibility check's default configuration also passes a marked public field; the mark still prevents no one from using it, so a pass under that configuration does not clear the public case, which stays a finding.
- Whether a test should exercise a private routine directly at all is debated; the rule settles only how far visibility is widened for it.
- A declaration in a file or a block that the build compiles only for tests is excluded from regular builds, so its visibility reaches no production caller; it is outside the finding.
- A wider declaration whose calls a restricted-API check prohibits unless the caller carries an allowlist mark is the alternative that the for-testing mark's own documentation names; where the build or the project context shows that check enforced on the declaration, the finding does not apply.
- An interface exported because callers have a material need to substitute implementations, and test doubles offered in a separate test-support package named after the production package, are outside the finding.
- When code other than a test calls the widened member from outside its package or module, the widening is not for tests only and the rule does not decide it; an internal-API check reports a call to a member marked for tests from code that is neither a test nor the declaring type.
- A declaration widened with no test-intent mark and given a doc comment, an example or a changelog entry addressed to other callers is published interface, not a widening for tests; it is outside the finding.

## Validator
Find in the hunk each declaration that carries a test-intent mark: an annotation or doc tag saying it is visible for testing or test-only, a comment saying it is public, exported or exposed for tests, or a name ending in a for-test or for-testing suffix. Find also each public or exported type or constructor named as a fake, mock, stub or spy, and each declaration whose removed line in the hunk shows narrower visibility than its added line, when the change adds a test call that the narrower visibility would not have admitted and gives the declaration no doc comment, example or changelog entry addressed to other callers. Skip a declaration in a file or block the build compiles only for tests, and a declaration in a separate test-support package named after the production package. Classify the declaration's new visibility as public, exported or protected (visible to subclasses), or as package- or module-level; where privacy is only a naming mark, a name that still carries a non-public mark counts as module-level, and only a name stripped of every non-public mark counts as public. Open the usages the scope reaches, list the callers outside the declaring type and its package or module, and decide whether every one of them is a test. Check the build configuration and the project context for a restricted-API check that limits the declaration's callers. For an exported test double, check whether it sits in the production package that consumes its interface rather than in a separate test-support package, and whether a non-test caller substitutes implementations through that interface. Validator question: **Is a declaration outside a separate test-support package made public, exported or protected, its private-name mark dropped, or a test-double implementation exported from the production API that consumes its interface, while every caller outside its own package or module is a test and no enforced restricted-API check limits its callers?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: DSN-35`, severity minor, `file`, `symbol`, `code` = the widened declaration or the exported test-double type, with its test-intent mark when it carries one, quoted verbatim from the diff, `fix` = the declaration back at its narrowest visibility with the test placed in the same package or a child test module, or rewritten through the public interface, or the double moved to a separate test-support package, in the file's language, `rationale` = names the declaration, its visibility before and after, that only tests call it from outside its package or module, and that any other code can depend on it at its new visibility, so it is hard to make non-public again and, where it breaks the encapsulation of its type, the type's internal representation becomes hard to change).
