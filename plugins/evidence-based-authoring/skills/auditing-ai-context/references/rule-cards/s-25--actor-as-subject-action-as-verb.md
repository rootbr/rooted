---
title: The actor is the subject and the action a verb, where the agent is known and material
rule_id: S-25
applies_to_target: [answer, doc]
check_kind: semantic
severity_default: low
---

# The actor is the subject and the action a verb, where the agent is known and material

## Thesis
Where the agent is both known and material to the reader's decision, name it as the grammatical subject and state its action as a verb. Under that condition an agentless passive and a noun standing in for an action are both rewritten; where the agent is unknown or irrelevant, leaving it out is the correct form.

## Rationale
A noun that stands in for an action is read more slowly than any other noun. Eye-tracked over 80 readers, nominalisations raised total reading time (β = 0.131, SE = 0.015, t = 8.911) and were skipped far less often than other nouns (β = -0.536, z = -16.087, p < .0001), reversing the general pattern that nouns are read faster than other words; against other word classes on total reading time, nominalisations run β = 0.053, t = 6.80 where finite verbs run β = 0.016, t = 2.55. The saving is in reading effort, and it is spent on every reader every time the sentence is read.

## Example
```
bad:  A decision was made regarding the cancellation of the booking.
good: The office cancelled the booking.
```

## Limits
The measurement is reading time, not understanding: on the same texts, comprehension did not move — "84% of all questions after original excerpts were answered correctly", against 88% for moderately and 87% for strongly rewritten versions — and "Just because some parts of the texts are read considerably slower does not mean that they are not comprehended at all". The reading-time gain from rewriting into verbs is itself fragile: "If the reading times for the baseline models are used, no significant effects can be shown", and at text level only the strong rewrite is read faster (β = -0.157, t = -2.58) while the moderate one is not. The genre is German court decisions read by 80 students with no legal background. On the passive side the trigger is deliberately narrow: "sometimes the agent is not relevant or is unknown, and in these cases, a structure allowing it to be omitted may be useful", so an agentless passive is not itself the defect, and no surface heuristic finds passives reliably — "none of the elements of the heuristic is necessary and all of them are jointly insufficient to reliably identify passives".

## Validator
For each agentless passive, ask two questions in order: is the agent known from the surrounding text, and would the reader's decision change if it stays unnamed? Flag only where both answers are yes. For each noun naming an action, check whether a verb form of the same root states that action with its actor as subject; flag where it does and the actor is available. A grep for `-tion`, `-ment` or `was <participle>` locates candidates but decides nothing. Validator question: is a known, material actor being kept out of the subject position?

## Patch output
When auditing a target that keeps a known, material actor out of the subject position, emit one patch (`rule_id: S-25`, `location.section` + `line_hint`, severity low) proposing the actor-as-subject rewrite. Whether the agent is material, and whether the construction is a passive at all, are reading calls, so set `proposed: null` and `needs_human: true`.

## Source
Wolfer 2016, *Eyetracking and Applied Linguistics* 163–186, doi:10.17169/langsci.b108.298 — Table 3 p. 177 (total reading time β = 0.131, SE = 0.015, t = 8.911; skip probability β = -0.536, z = -16.087), pp. 178–179 (word-class comparison), p. 179 (baseline-model null), p. 182 (comprehension 84% / 88% / 87%); eye-tracking, 80 readers with no legal background, German court decisions — reading time only. Ferreira 2021, *American Psychologist* 76(1):145–153, doi:10.1037/amp0000620 — a review essay carrying no data of its own; p. 17 bounds the trigger to a known, material agent, p. 12 on the unreliability of surface passive detection. Both read first-hand.
