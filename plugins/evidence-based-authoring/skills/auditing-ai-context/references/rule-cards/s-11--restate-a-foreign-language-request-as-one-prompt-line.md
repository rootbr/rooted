---
title: A foreign-language request is restated as one explicit English prompt line before work starts
rule_id: S-11
applies_to_target: [answer]
check_kind: mechanical
severity_default: low
---

# A foreign-language request is restated as one explicit English prompt line before work starts

## Thesis
When the request arrives in a language other than the working one, open the reply with a single line restating it as an explicit English prompt, and do the work from that line.

## Rationale
The line's work is specification, not translation: it puts the interpretation in front of the reader before anything depends on it, so a misreading costs one line to correct instead of being discovered in the finished output. That matters because what is left implicit is recovered badly — a conditional or edge-case requirement that is not spelled out is recovered only 22.9% of the time, against 70.7% for a format default the model can infer. A second and bounded reason: a multilingual transformer's abstract concept space lies closer to English than to other languages, so an English restatement states the request in the terms the model works in.

## Example
```
bad:  a request written in another language, answered directly with no restatement
good: "Prompt: rename the scanned bills by their invoice date." — then the work
```

## Limits
The rule claims no accuracy gain from the change of language, and it does not rest on one: the restatement earns its line by being explicit and correctable, and it holds equally where the model would have read the original correctly. The concept-space finding was measured on a single model family, so its transfer to another model is an extrapolation. A request already in the working language needs no restatement line.

## Validator
Check the language of the request. Where it is not the working language, check that the reply opens with one restatement line in the working language stating what will be done, ahead of any other content. Flag a reply that starts the work with no restatement line, and a restatement that arrives after the work rather than before it.

## Patch output
When auditing a reply to a request in another language that carries no leading restatement line, emit one patch (`rule_id: S-11`, `location` set to the first line, `current` = the reply's opening, `proposed` = the restatement line placed above it, severity low). Presence and position of the line are decidable from the reply itself, so no `needs_human` flag.

## Source
Yang 2505.13360 §3.2 (requirements left implicit are recovered at low rates: conditional and edge-case rules 22.9%, inferable format defaults 70.7%); Wendler 2402.10588 (multilingual transformers pivot through an abstract concept space lying closer to English than to other languages — analysis scoped to the Llama-2 family, so the transfer is an extrapolation).
