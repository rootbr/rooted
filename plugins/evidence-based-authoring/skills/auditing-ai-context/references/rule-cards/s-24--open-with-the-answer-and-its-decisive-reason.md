---
title: An answer opens with the answer and its decisive reason, switching to premise→conclusion when the conclusion is contestable
rule_id: S-24
applies_to_target: [answer, doc]
check_kind: semantic
severity_default: medium
---

# An answer opens with the answer and its decisive reason, switching to premise→conclusion when the conclusion is contestable

## Thesis
The opening sentence states the answer together with the one reason that decides it, and stands alone — correct and complete if the reader stops there. The order inverts to premise→conclusion only where the conclusion is contestable for this reader, or inseparable from the step before it.

## Rationale
Putting the conclusion first costs nothing that has been measured and spends less of the reader's capacity. Over four newspaper stories of about 300 words, each rewritten into both orders and matched on readability, sentence count and concept count, the conclusion-first version left recognition memory unchanged (F(1,50) = .01, p = .94) and cued recall unchanged (F(1,50) = 1.32, p = .26), trended ahead on comprehension without reaching significance (F(1,49) = 3.20, p = .08), and drew fewer processing resources: responses to a secondary task ran 396.4 ms against 412.7 ms for the sequential order (F(1,44) = 3.92, p = .05).

## Example
```
bad:  We compared three quotes and checked the dates, so the roof is the cheaper fix.
good: Fix the roof first — it is the cheaper job, and the leak is spreading.
```

## Limits
The measurement is a single dissertation in a news-writing context, on printed stories of about 300 words read whole: "No differences emerged for the memory and enjoyment measures, and a marginally significant difference favoring the inverted pyramid structure was observed on the text comprehension measure". No available measurement covers partial reading, so what a reader who stops after the first sentence carries away is asserted here, not measured. The premise→conclusion switch is a house heuristic with no measurement behind it, and the justification once offered for it — that a complex topic is better interpreted when read in sequence — was stated as a hypothesis in the same work and disconfirmed.

## Validator
Read the opening sentence alone. Ask whether it states the answer to the question the target was written to answer, together with the reason that decides it, and whether it survives as a standalone answer. Flag an opening that restates the question, sets up context, or narrates the work done before the answer arrives. Where the opening is premise-first, check that its conclusion is contestable for the stated reader or depends on the immediately preceding step, and flag it where neither holds. Validator question: if the reader stops after sentence one, does he hold the answer and its decisive reason?

## Patch output
When auditing a target whose opening withholds the answer, emit one patch (`rule_id: S-24`, `location.section` + `line_hint`, severity medium) proposing an opening that states the answer and its decisive reason. Which reason is decisive, and whether the conclusion is contestable for this reader, are reading calls, so set `proposed: null` and `needs_human: true`.

## Source
Sternadori 2008, *Cognitive processing of news as a function of structure: a comparison between inverted pyramid and chronology*, PhD dissertation, University of Missouri-Columbia — https://pdfs.semanticscholar.org/f2eb/ad1fa4020d0647314314457ec2c003516087.pdf, p. vii and pp. 48–49 Tables 1–4: recognition F(1,50) = .01, p = .94; cued recall F(1,50) = 1.32, p = .26; comprehension F(1,49) = 3.20, p = .08; secondary-task reaction time F(1,44) = 3.92, p = .05 (396.4 ms against 412.7 ms). Read first-hand. One dissertation, printed news stories, whole-text reading; the premise→conclusion switch is a house heuristic, not a measured one.
