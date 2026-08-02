---
title: Structure earns its place by lowering the reader's inference cost, not by holding more content
rule_id: S-20
applies_to_target: [answer, doc]
check_kind: semantic
severity_default: low
---

# Structure earns its place by lowering the reader's inference cost, not by holding more content

## Thesis
A table, diagram, or arrow chain is justified when it indexes the material so that one inference the reader must make becomes cheaper than it would be from the surrounding sentences. Holding more content is not a justification, and a structure whose reader lacks the operators to read it costs more than the prose it replaced.

## Rationale
Two layouts can carry exactly the same information and still cost different amounts to use, because ease is judged over what each states outright: "any inference that can be drawn easily and quickly from the information given explicitly in the one" need not be equally available from what the other states explicitly. The gain of laying material out by position — "A data structure in which information is indexed by two-dimensional location" — is a computational one, arising "not because they contain more information, but because the indexing of this information can support extremely useful and efficient computational processes". Content added without cheapening a needed inference adds reading cost only.

## Example
```
bad:  a 12-row tariff table, because the whole price list fits in it
good: a 2-row table, because the reader must compare exactly those two prices
```

## Limits
The failure conditions are as load-bearing as the rule. A structure is useless to a reader without the conventions for reading it: "If the students lack productions for making physics inferences from diagrams, they may not only fail to 'appreciate' the value of diagrams, but will find them largely useless." It is also useless when built without regard to the inference it should serve — "To be useful a diagram must be constructed to take advantage of these features" — and when the inferences it makes easy are not the ones the problem needs, since "nothing ensures that these inferences must be useful in the problem-solving process". The comparison is not measured on a common scale — "'Easily' and 'quickly' are not precise terms" — and the one published search count, "Total Elements Searched: 138" for the sentence-sequence solution of a worked pulley problem, has no counted counterpart in the laid-out form, so no speedup ratio is derivable.

## Validator
For each table, fenced diagram, or arrow chain, name the single inference the reader must make from it, then compare the steps that inference takes against the steps it would take from the surrounding sentences. Flag the block when its only gain is that more content fits, or when reading it requires a convention the target's reader is never given. Validator question: does this block make one named inference cheaper, or does it only hold more?

## Patch output
When auditing a target whose structure holds content without cheapening a named inference, emit one patch (`rule_id: S-20`, `location.section` + `line_hint`, severity low) proposing either prose or a narrower structure carrying the same claim. Naming which inference the reader must make is a reading call, so set `proposed: null` and `needs_human: true`.

## Source
Larkin & Simon 1987, *Cognitive Science* 11(1):65–100, doi:10.1207/s15516709cog1101_4 — p. 67 (informational vs computational equivalence, ease judged over what is stated explicitly), p. 68 (two-dimensional indexing), p. 99 (the advantage is computational; irrelevant easy inferences), p. 71 (fails without the operators to read it), pp. 98–99 (must be constructed for it), p. 77 Table 2 (138 elements searched sententially; the diagrammatic count is never given). Read first-hand from page images.
