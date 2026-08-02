---
title: A fragment is cut when the rest still says the same thing and kept when cutting changes truth or scope — never to hit a length target
rule_id: S-06
applies_to_target: [answer, doc, code]
check_kind: semantic
severity_default: medium
---

# A fragment is cut when the rest still says the same thing and kept when cutting changes truth or scope — never to hit a length target

## Thesis
Cut a fragment when what remains still says the same thing; keep it when removing it changes the truth or the scope of the claim. A length target decides neither.

## Rationale
Verbosity is a measured artifact of how the models were trained rather than a stylistic weakness: optimizing for response length accounts for much more of the gain from reinforcement learning on human feedback than was previously thought, a purely length-based reward reproduces most of that downstream improvement over a supervised fine-tuned model, and the reward models are identified as the dominant source of the bias. Removing a filler opener or an echo summary therefore corrects a known bias rather than imposing taste. A length target fails for a separate reason: compression meets a per-question floor — an intrinsic token complexity, the minimal number of tokens required to solve the task — and that floor sits in the reasoning, not in the delivered prose. Unnecessary length is also a calibration failure: longer explanations raise the reader's confidence even where the extra length does not improve accuracy.

## Example
```
bad:  "Great question! In short, and to summarise: yes, it is indeed covered."
good: "Yes — the warranty covers the motor for three years."
```

## Limits
Covers prose fragments, including those written inside comments and doc-comments, not the code beside them. Scopes to the delivered answer, never to the reasoning budget: a brevity instruction that reaches the reasoning spends exactly the tokens the task needs to be solved. Response length is not a success measure, so a cut is justified by what survives it rather than by the count. A fragment carrying a qualification, a boundary, a first-use definition, or the only statement of the conclusion changes scope when removed and is kept.

## Validator
For each candidate cut, restate what would remain and compare it against the original: same claim, same conditions, same scope → cut; any change to truth or scope → keep. Flag any cut proposed against a word or token target rather than against that comparison, and flag filler openers, restated questions, echo summaries and closing offers of further work that survive because no test was applied. On a `code` target the comparison runs inside the comment or doc-comment alone — whether a comment repeats the statement beside it is outside this rule, whose sources measure prose against prose. Validator question: with this fragment gone, does what remains still assert exactly what the original asserted?

## Patch output
When auditing text carrying an unearned fragment, or a cut justified by a length target, emit one patch (`rule_id: S-06`, `location` set to the heading and line hint, `current` = the fragment or the proposed cut, severity medium). Judging whether a fragment is load-bearing is a semantic call and the systematic error runs toward over-cutting, so set `proposed: null` and `needs_human: true`.

## Source
Singhal 2310.03716 (optimizing for response length is a significant factor behind RLHF gains; a purely length-based reward reproduces most downstream improvement over SFT; reward models are the dominant source of the length bias — three settings, no percentage in the abstract); Lee 2503.01141 (universal reasoning-length/accuracy tradeoff arising from a sharp per-question threshold — an intrinsic "token complexity"; adaptive compression is the recommended policy); Steyvers 2401.13835, *Nature Machine Intelligence* (users grow more confident with longer explanations even where the extra length does not improve accuracy — no magnitudes in the abstract).
