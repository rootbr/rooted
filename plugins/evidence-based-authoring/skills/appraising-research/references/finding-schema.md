# Finding Schema & Priority Ranking

> The single record shape every critique agent emits, the severity scale, and the priority formula the adjudicator ranks by. One schema across all seven methods so the adjudicator can dedup and rank without reformatting. The whole point of the skill is to surface **what genuinely needs re-checking, ranked** — this file defines "ranked".

## Contents
- §Finding record
- §Axis and prefix table
- §Severity scale
- §Load-bearing test
- §Confidence scale
- §Priority ranking
- §Anchor rule

---

## Finding record

Every finding, from any method agent, uses exactly this block. The header line is **literally** `### <PREFIX><N>: <title>` — an h3 (`###`), the prefix+number, a colon, then the title. Not `##`, not an em-dash separator; the fixed shape is what lets the adjudicator parse every method's output uniformly.

```
### <PREFIX><N>: <one-line title>
- **Axis**: data | assumptions | blindspots | beneficiaries | logic
- **Claim ref**: C<k> (from claims.md) | "main conclusion" | "source: <name>"
- **Anchor**: verbatim quote (≤ 25 words) from the report or a source, that the finding is about
- **Load-bearing**: yes | no
- **Severity**: critical | major | minor | info
- **Flaw**: what is wrong — one to three sentences
- **Why it matters**: the effect on the report's conclusion if the flaw stands
- **Recheck action**: the concrete next step — what to verify, which source to find, what to re-run
- **Confidence**: high | med | low  (confidence that the flaw is real)
- **Method source**: the primary source of the technique that surfaced this (e.g. "Heuer 1999 ACH")
```

`<N>` is sequential within the agent (`EV1`, `EV2`, …). The adjudicator preserves the original prefix; only adjudicator/synthesis-added findings get `ADJ<N>`.

## Axis and prefix table

| Method agent | Axis | Prefix |
|---|---|---|
| c01 evidence-grading | data | `EV` |
| c02 source-integrity | data | `SRC` |
| c03 assumption-excavation | assumptions | `ASM` |
| c04 competing-hypotheses | blindspots | `ACH` |
| c05 premortem-redteam | blindspots | `RED` |
| c06 beneficiary-funding | beneficiaries | `BEN` |
| c07 logic-fallacy | logic | `LOG` |
| adjudicator / synthesis (new) | any | `ADJ` |

## Severity scale

Severity is about the flaw's damage to the report's trustworthiness, not the effort to fix it.

- **critical** — the flaw, if real, breaks the main conclusion: a fabricated or misattributed pivotal source, a causal claim with no causal basis driving the recommendation, a funded source whose undisclosed interest is the recommendation.
- **major** — the flaw materially weakens a load-bearing claim: evidence graded far weaker than presented, an unexamined competing hypothesis that fits the data as well, an unsupported key assumption.
- **minor** — a real but non-load-bearing weakness: a weak secondary citation, a hedge that should be stronger, a missing perspective that would not change the conclusion.
- **info** — an observation worth noting that is not itself a defect (e.g. "this claim is well-supported; no action").

## Load-bearing test

A claim is **load-bearing** if the report's main conclusion or recommendation would not hold were the claim false. The decomposer marks each atomic claim in `claims.md`; method agents inherit that mark and may correct it with justification. Load-bearing is the strongest single driver of priority — a critical flaw in a decorative aside matters less than a major flaw in the keystone.

## Confidence scale

Confidence that the flaw is *real* (distinct from severity, which is its impact):
- **high** — verified against an external source or an internal contradiction that is plainly present.
- **med** — well-argued but not externally confirmed; a debate would settle it.
- **low** — a suspicion worth flagging; needs investigation before it can be trusted.

## Priority ranking

The adjudicator ranks every surviving finding by **priority**, computed from the three axes above. Score each and sum:

| Factor | Value → points |
|---|---|
| Load-bearing | yes = 3 · no = 0 |
| Severity | critical = 3 · major = 2 · minor = 1 · info = 0 |
| Confidence | high = 2 · med = 1 · low = 0 |

`priority = load_bearing + severity + confidence` (0–8). Rank descending. Ties break toward higher severity, then load-bearing. The top of the ranked list is literally "re-check these first". Findings at confidence `low` but load-bearing `yes` and severity `major`+ are the prime candidates for the debate stage — high stakes, unresolved.

**Debate selection rule** (adjudicator): mark `debate: yes` when `load_bearing = yes` AND `severity ∈ {critical, major}` AND `confidence ∈ {med, low}`. These are the findings whose truth most changes the verdict and is least settled. Cap the debate set by depth budget: quick = 3, standard = 6, deep = 10 (log any findings dropped by the cap — never silently truncate).

## Anchor rule

A finding without an **Anchor** — a verbatim quote from the report or a source it is about — is speculation and is rejected at adjudication. "The report probably assumes X" without a quote is not a finding; quote the sentence that carries the assumption. This mirrors the reviewing-java "no diff anchor → no finding" rule: one false positive erodes trust in the whole appraisal.
