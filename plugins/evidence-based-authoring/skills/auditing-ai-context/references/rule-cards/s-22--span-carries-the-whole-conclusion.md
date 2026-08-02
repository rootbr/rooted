---
title: The span carries the whole conclusion; the screen keeps what cannot be heard — code, tables, paths, formulas
rule_id: S-22
applies_to_target: [answer]
check_kind: semantic
severity_default: medium
---

# The span carries the whole conclusion; the screen keeps what cannot be heard — code, tables, paths, formulas

## Thesis
A spoken span states the conclusion whole — the same conclusion the printed reply delivers, not a pointer into it. Material a listener cannot receive stays on screen alone: code, commands, tables, file paths, identifiers, formulas.

## Rationale
Carrying the conclusion in both channels costs nothing where nothing else competes for the visual channel. Hearing an explanation while reading identical printed text beat hearing it alone on every measure over 74 college students, with no concurrent animation present: "the redundancy effect sizes were 0.78 for the retention test, 1.62 for the transfer test, and 0.39 for the matching test", "provided there was no other concurrent visual material". A span that names its conclusion instead of stating it hands the listener a pointer into a channel he is not reading; a path or a formula spoken aloud arrives as characters no listener can reassemble, and it displaces the conclusion from the one span available.

## Example
```
bad:  spoken "Done — the details are in the table above."
good: spoken "The lease renews in March; the three dates sit in the table."
```

## Limits
The measured comparison is graphics-free — narration against narration plus identical on-screen text, no animation — which is the configuration of a printed reply carrying a spoken span. It does not transfer to words set beside a picture: there, duplicating the narration on screen lost in 16 of 16 tests, median d = 0.86 on problem-solving transfer, range 0.19 to 1.91. That boundary is stated where the effect is: it "can be eliminated or even reversed when the learners are experienced, the on-screen text is short, or the material lacks graphics", the last case holding "because there is no other material to process in the visual channel". A target that carries no spoken channel has no span to check.

## Validator
Locate the spoken span. Read it alone, with the printed reply hidden, and ask whether the conclusion it delivers is complete — the answer plus any caveat that would change the reader's decision. Flag a span that names the conclusion instead of stating it ("as shown below", "see the table", "done"), and flag a span that speaks material only the screen can carry: code, commands, table rows, paths, identifiers, formulas. Validator question: heard alone, does the span deliver the same conclusion the screen delivers?

## Patch output
When auditing an answer whose span carries less than the printed conclusion, or speaks material only the screen can carry, emit one patch (`rule_id: S-22`, `location.section` + `line_hint`, severity medium) proposing a span that states the conclusion whole and leaves the unspeakable material on screen. Identifying the conclusion requires reading the whole reply, so set `proposed: null` and `needs_human: true`.

## Source
Moreno & Mayer 2002, *J. Educational Psychology* 94(1):156–163, doi:10.1037/0022-0663.94.1.156, p. 158 — 74 college students aged 18–26 heard a lightning explanation as narration alone or as narration plus identical on-screen text, no concurrent animation; d = 0.78 retention, 1.62 transfer, 0.39 matching, all favouring the duplicated presentation. Mayer & Fiorella 2014, *Cambridge Handbook of Multimedia Learning* 2nd ed., ch. 12, doi:10.1017/CBO9781139547369.015 — pp. 279 and 297 (16 of 16 tests, median d = 0.86, range 0.19–1.91, the with-graphics case), pp. 299–300 (the stated boundary conditions). Both read first-hand; the effects are defined for multimedia instruction scored by retention and transfer tests.
