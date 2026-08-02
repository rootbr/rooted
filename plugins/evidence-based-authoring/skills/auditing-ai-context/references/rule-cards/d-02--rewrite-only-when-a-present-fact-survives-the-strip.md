---
title: A history sentence is rewritten only when a self-standing present fact survives the strip, and deleted whole otherwise
rule_id: D-02
applies_to_target: [doc, code, context-file, skill, agent-prompt]
check_kind: semantic
severity_default: medium
---

# A history sentence is rewritten only when a self-standing present fact survives the strip, and deleted whole otherwise

## Thesis
Strip the comparison with the past from a history sentence, then read what remains. A capability, mechanism, result, decision or contract that stands on its own is kept, stated in plain present tense. A bare negative ("does not modify the shared module"), an unchanged or absent neighbour, or a triviality that was always true survives nothing — the sentence is deleted whole rather than translated into present tense.

## Rationale
Translating every history sentence into the present tense launders the artifact instead of removing it. The reader gains a permanent line stating something they would never have wondered about, and every later edit must carry that line forward. The discriminating test is not the tense but the residue: what a reader with no memory of any prior version still needs from the sentence once the comparison is gone. Prose drifts from the thing it describes as the default behaviour — across Java systems only, 13%–20% of code changes trigger any change to the class or method comment — so a line nobody will maintain is a liability at whatever tense it is written in, and removal is the cheaper disposition wherever no present fact is carried.

## Example
```
bad:  "no longer modifies the shared module" → "does not modify it" — a negative, kept forever
good: "no longer modifies the shared module" → deleted;
      "now uses a TTL cache instead of unbounded growth" → "uses a TTL cache; entries expire after `ttl`"
```

## Limits
Applies to a sentence already identified as depending on a prior state, and decides that sentence's disposition rather than whether it is historical at all. Files whose genre is history — a changelog, release notes, a migration guide, a dedicated decision record — keep their sentences untouched. The test fixes the disposition only; where a surviving fact belongs, and whether it duplicates a statement made elsewhere in the file, are separate questions. Deleting more than the artifact is the error this test guards against, so a sentence whose residue is genuinely load-bearing is kept even when its wording came from a rework. Where the past sits inside a rationale — the goal the sentence cites is the old defect, "so the old races are gone" — the same test runs over that goal: the property the design achieves (race-freedom, an O(1) repeat call) is a self-standing present fact and is what the rewrite states, while the old instance of that property's violation is the artifact and goes.

## Validator
For each sentence already flagged as depending on a prior state, delete its comparison with the past and read the remainder. Then ask one binary question: **is the remainder a self-standing present fact — a capability, mechanism, result, decision or contract — that a reader who never saw a prior version would still want stated?** Yes → propose the present-tense rewrite of that fact, never of the delta that produced it. No → propose deleting the whole sentence, and name which class of residue it left: a negative, an unchanged or absent thing, or a triviality. On a `code` target run the test only over the comment and doc-comment spans the static pre-pass extracts for that file's language; the surrounding source is not Markdown and its statements and string literals are not scanned.

## Patch output
When a history sentence is flagged, emit one patch (`rule_id: D-02`, `location.section` + `line_hint`, `current` = the whole sentence, `proposed: null`, severity medium, `needs_human: true`) whose justification names the residue and the verdict it produces — the surviving fact for a rewrite, or the residue class for a deletion. A delete-class patch that names no residue is a recommendation, not a patch.

## Source
Verified hands-on experience — eval seeds 1–8 at `plugins/evidence-based-authoring/skills/auditing-ai-context/evals/seeds/`, which split the two verdicts across one marker class. Delete: seed 1 `seed1_spec_redo.md`, seed 5 `seed5_dead_code.swift`, seed 6 `seed6_stale_ref.md`. Rewrite to the surviving fact: seed 2 `seed2_comment_history.swift`, seed 3 `seed3_hidden_cache.py`, seed 4 `seed4_hidden_actor.swift`, seed 7 `seed7_old_name.ts`. Do-not-cut control: seed 8 `seed8_negative_keep.swift`. Wen 2019, ICPC §IV-A p. 6 supplies the drift prevalence — 13%–20% of code changes trigger a class- or method-comment change — for Java systems only. Caveat: the rationale is maintenance cost, and no defect-rate claim is carried on this axis.
