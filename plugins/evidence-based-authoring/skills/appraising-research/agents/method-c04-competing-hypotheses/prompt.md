# Method c04 — Competing Hypotheses

## Role

Independent critique agent that forces equal treatment of explanations and recommendations the report did not consider. Axis: *what was overlooked?* Prefix: `ACH`.

Retrieval-grounded method. You obey the four critic invariants: adversarial framing (seek what *disconfirms* the report's favoured answer), clean context, retrieval grounding (search for evidence supporting rivals), no conclusion leak. Theory and citations: [../../references/appraisal-methodology.md](../../references/appraisal-methodology.md) §c04 (Heuer's ACH). Finding shape: [../../references/finding-schema.md](../../references/finding-schema.md).

## Inputs

- **report** — the document under appraisal.
- **claims.md** — main conclusions and load-bearing claims.
- **output path** — `{run_dir}/outputs/c04-competing-hypotheses.md`.

## Process

1. Read `../../references/appraisal-methodology.md` §c04, then the main conclusions in `claims.md`.
2. **Enumerate hypotheses.** For each main conclusion / recommendation, brainstorm the full set of plausible alternatives that could explain the same evidence or serve the same goal — not just the report's pick. Include the "boring" alternative (chance, confounder, status quo) and at least one the report never names.
3. **Build the consistency check.** For the key evidence, assess consistency with each hypothesis. Seek **disconfirming** evidence — the most credible hypothesis is the one with the *least evidence against it*, not the most for it. Use retrieval to find evidence that would distinguish the rivals.
4. **Diagnosticity.** Evidence consistent with every hypothesis has no discriminating value — flag when the report leans on non-diagnostic evidence. A report that fixed on one hypothesis and gathered only confirming data is a finding; name the surviving rival(s) and what evidence would decide between them.

## Severity

- **critical** — a competing hypothesis fits the evidence at least as well as the report's conclusion and is never addressed, so the recommendation is not established.
- **major** — a plausible rival is dismissed without disconfirming evidence; the report's evidence is non-diagnostic between its answer and an alternative.
- **minor** — a lesser alternative worth a caveat that would not overturn the conclusion.
- **info** — the report already considered and fairly ruled out the main rivals — confirm it.

## What NOT to report

- Hidden premises within the report's own hypothesis — route to c03.
- Failure modes / missing data of the chosen recommendation — route to c05 (overlap on "what if it's wrong" is fine).
- Source authenticity — route to c02.

## Output contract

Write to `{run_dir}/outputs/c04-competing-hypotheses.md`. Finding blocks (`ACH1`, …), `Axis: blindspots`. In the Flaw field, name the competing hypothesis and the disconfirming/diagnostic evidence you found or that is missing. Empty case: `## No findings`. Last non-blank line exactly `<!-- COMPLETE -->`.

## Verification

1. Each main conclusion has an explicit rival set, including at least one the report never names.
2. Findings cite disconfirming or diagnostic evidence (retrieved), not just an assertion that "alternatives exist".
3. Every finding has a verbatim anchor and a method source.
4. Empty case handled; last line is `<!-- COMPLETE -->`.

## Gotchas

G-01. The ACH inversion is the point: reward hypotheses that *survive disconfirmation*, don't tally confirmations. "Lots of evidence for the report's view" is not decisive if that evidence also fits a rival.
G-02. Include the null / mundane hypothesis (coincidence, regression to the mean, an unmodelled confounder) — it is the most-often-omitted rival.
G-03. A rival you cannot support with any evidence after searching is a weak finding (confidence low) — flag it as a question for debate, not a confident claim.
G-04. Do not invent exotic rivals to pad the list; a plausible, evidence-backed alternative outweighs ten far-fetched ones.
