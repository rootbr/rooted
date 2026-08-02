---
title: A magnitude row carries its printed number
rule_id: S-21
applies_to_target: [answer, doc]
check_kind: semantic
severity_default: medium
---

# A magnitude row carries its printed number

## Thesis
Every row of a bar block prints the value it encodes, on the same row as the bar. The drawn length carries the comparison between rows; the digits carry the quantity.

## Rationale
Reading a quantity off a bar is a length judgment, and a length is judged less accurately than a position along a common scale. Measured over 51 usable subjects on five bar-chart forms, "the average errors for length judgments are 40%-250% larger than those for position judgments", and gross errors concentrate on the length judgments at 5.3 times the position rate. A printed number is not judged at all — it is read — so stating it removes that error class outright while the bar keeps the at-a-glance ranking it is good at.

## Example
```
bad:  rent   ▆▆▆▆▆▆
good: rent   ▆▆▆▆▆▆  1,240 €
```

## Limits
The six-rank ordering of perceptual tasks that places length below position is hypothesized, not measured: it is offered as "an ordering of the 10 elementary perceptual tasks on the basis of the accuracy with which people can extract quantitative information by using them", and only position against length and position against angle were ever put in front of a subject, on bar and pie charts, 51 usable subjects each. The guideline drawn from that ordering — "Graphs should employ elementary tasks as high in the ordering as possible" — is bounded where it is stated: "The ordering of the perceptual tasks does not provide a complete prescription for how to make a graph", and is to be "used with judgment". A row that encodes no magnitude — a label, a status, a category — has no number to print and is out of scope.

## Validator
Find every fenced block whose rows carry bar glyphs (`▁▂▃▄▅▆▇█`) or a repeated fill character standing for a quantity. For each such row, check whether a digit appears on the same row. Flag a row whose magnitude reaches the reader only as drawn length. Validator question: can the reader state this row's value without measuring its bar?

## Patch output
When auditing a target whose magnitude row draws a bar with no printed value, emit one patch (`rule_id: S-21`, `location.section` + `line_hint`, severity medium) proposing that the value be printed on the row. The quantity the bar encodes is not recoverable from the rendered text, so set `proposed: null` and `needs_human: true`.

## Source
Cleveland & McGill 1984, *JASA* 79(387):531–554, doi:10.1080/01621459.1984.10478080 — p. 541 (length errors 40%-250% larger than position), p. 542 (gross errors at 5.3 times the position rate), pp. 539–542 (two experiments, 51 usable subjects each, bar and pie charts), p. 536 (the six-rank ordering is hypothesized, not measured; length sits at rank 3, position along a common scale at rank 1), p. 531 and p. 552 (the guideline and its bound). Read first-hand from page images.
