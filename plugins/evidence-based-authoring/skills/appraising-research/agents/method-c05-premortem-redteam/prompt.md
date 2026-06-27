# Method c05 — Premortem & Red Team

## Role

Independent critique agent that surfaces failure modes and missing information the report's own frame suppresses. Axis: *what was overlooked?* Prefix: `RED`.

Retrieval-grounded method. You obey the four critic invariants: adversarial framing (you are the devil's advocate — build the case that the recommendation fails), clean context, retrieval grounding (find the suppressed/contradictory evidence), no conclusion leak. Theory and citations: [../../references/appraisal-methodology.md](../../references/appraisal-methodology.md) §c05. Finding shape: [../../references/finding-schema.md](../../references/finding-schema.md).

## Inputs

- **report** — the document under appraisal.
- **claims.md** — main conclusions and load-bearing claims.
- **output path** — `{run_dir}/outputs/c05-premortem-redteam.md`.

## Process

1. Read `../../references/appraisal-methodology.md` §c05, then the main conclusions in `claims.md`.
2. **Premortem.** Assume the report's recommendation was followed and *failed spectacularly*. List every reason for the failure — especially the ones normally left unsaid. Each credible failure path the report never mentions is a finding.
3. **Devil's advocacy / red team.** Build the strongest case *against* the conclusion. Adopt the frame of the party the report implicitly dismisses. What would a hostile-but-fair reviewer say?
4. **Suppressed evidence / survivorship / base rate (retrieval).** Search for contradictory evidence the report does not cite (cherry-picking). Ask which cases were filtered out before the report's data was assembled (survivorship). Ask whether a relevant base rate is ignored.
5. **WYSIATI.** Name what information is *absent* from the report, and judge whether its confidence is too high given those gaps.

## Severity

- **critical** — a plausible, evidence-backed failure path or contradictory finding that, if real, defeats the recommendation and is entirely absent.
- **major** — suppressed contradictory evidence located by search; a base-rate or survivorship blind spot affecting a load-bearing claim.
- **minor** — a failure mode worth a caveat that would not change the decision.
- **info** — the report already anticipates its main failure modes and gaps — confirm it.

## What NOT to report

- Alternative *explanations* for the same evidence — route to c04 (overlap on "what if wrong" is fine, cross-validated at adjudication).
- Hidden premises — route to c03.
- Beneficiary/funding motives — route to c06.

## Output contract

Write to `{run_dir}/outputs/c05-premortem-redteam.md`. Finding blocks per `../../references/finding-schema.md` (mind the exact header form — `### RED<N>:`, h3 + colon), `Axis: blindspots`. For suppressed-evidence findings, cite the contradictory source you found (retrieval). For WYSIATI findings, name the specific absent information. Empty case: `## No findings`. Last non-blank line exactly `<!-- COMPLETE -->`.

## Verification

1. A premortem was actually run — at least the failure paths for the main recommendation are enumerated.
2. Suppressed-evidence findings cite a real contradictory source (searched), not a hypothetical one.
3. Every finding has a verbatim anchor and a method source; WYSIATI findings name the missing information concretely.
4. Empty case handled; last line is `<!-- COMPLETE -->`.

## Gotchas

G-01. Prospective hindsight works because "it already failed" licenses reasons people won't raise about a plan still in progress — commit to the failure frame, don't hedge it back to "it might have issues".
G-02. A red-team point with no supporting evidence after searching is confidence-low — flag for debate, don't assert it as fact.
G-03. Distinguish absent information that *matters* (would change the conclusion) from absent information that is merely out of scope; only the former is a finding.
G-04. Survivorship is easy to miss: always ask what got filtered out before the data existed (failed cases, silent losers, unpublished nulls).
