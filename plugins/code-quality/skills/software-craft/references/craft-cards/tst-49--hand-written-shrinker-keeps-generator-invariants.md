---
title: A hand-written shrinker proposes only smaller values that still satisfy every invariant the generator guarantees
rule_id: TST-49
domain: tests
step: [test]
applies_to: [tests]
triggers: ['(?i)shrink\w*\s*\(', '\bdoShrink\b|\bShrinker\b|\bfn\s+(?:shrink|simplify|complicate)\b|\bimpl\b.*\b(?:Arbitrary|ValueTree)\b|\binstance\s+Arbitrary\b']
scope: file
check_kind: semantic
severity_default: minor
---

# A hand-written shrinker proposes only smaller values that still satisfy every invariant the generator guarantees

## Thesis
Where the framework asks the test author for a shrinker for a custom generator, every smaller candidate the shrinker returns satisfies every invariant the generator guarantees, the range it draws from included.

## Rationale
A shrinker reduces a large failing value, such as a string, a list or a more complex data structure, to a smaller one that triggers the same failure. It is easy to write a shrinker that accidentally does not preserve some invariant, and that makes the test fail. Reduction of this kind requires the user to specify a validity check to avoid invalid test cases; writing a correct validity check is difficult, and writing reducers that work well for a problem domain is a specialised skill that few people have or want to acquire. Shrinking that uses the generator itself always produces valid values, which is difficult to achieve otherwise; it never shrinks a value outside the range the generator describes, so an integer drawn from a range starting at 100 shrinks toward zero but stops at 100, the minimum value. In a framework whose shrinking derives from its generators, a custom generator assembled from the framework's own generators and mapped into the desired form gets that shrinking automatically, with no hand-written shrinker to keep in range.

## Example
```java
bad:  // the generator yields only non-empty lists
      public List<List<Integer>> doShrink(SourceOfRandomness r, List<Integer> larger) {
          return List.of(larger.subList(0, larger.size() / 2)); }
good: public List<List<Integer>> doShrink(SourceOfRandomness r, List<Integer> larger) {
          return larger.size() < 2 ? List.of()
              : List.of(larger.subList(0, larger.size() / 2)); }
```

## Limits
A custom generator that comes with no hand-written shrinker is outside the rule. A shrinker that builds candidates freely and then keeps only those that pass the generator's invariants meets the rule, since that filter is the validity check reduction needs. The rule governs the shrinker the test author writes, not a framework's choice between shrinking by type and shrinking through its generators.

## Validator
Grep the hunk for a shrinker the author defines: a method or function named shrink, simplify or complicate, or an implementation of the framework's shrinking interface for a custom type. Open the file and find the generator whose values that shrinker reduces; list what the generator guarantees, such as the bounds it draws from, a minimum size, an ordering, a relation between fields or a filter it applies. Trace each candidate the shrinker builds, starting from a larger value at the generator's edge, such as the minimum size or the bound itself, and check whether the candidate still meets each guarantee or is filtered by it. Validator question: **Can the shrinker return a candidate that breaks an invariant the generator it shrinks for guarantees?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: TST-49`, severity minor, `file`, `symbol`, `code` = the candidate expression in the shrinker that can leave the generator's range, quoted verbatim from the diff, `fix` = the shrinker with that candidate guarded or filtered by the generator's invariant, or, in a framework whose shrinking derives from its generators, the generator rebuilt from the framework's own generators so its shrinking derives from them, in the file's language, `rationale` = names the invariant the candidate breaks and the generator line that guarantees it).
