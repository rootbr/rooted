# Validation Protocol

> The skill is only useful if it reproduces the breadth of expert-authored reference material. Eval corpus = a mix of in-repo checklists, public syllabi, and domain overviews, chosen to span technical / scientific / regulatory / humanities / practical-craft topics so evaluation is not biased toward one field. Success = ≥ 90 % sub-theme / question / source coverage against a reference, with no fabricated sources.

## Contents
- §Eval corpus
- §Coverage metric
- §reliable@10 description-trigger evals
- §Iteration loop
- §Quality gate before commit
- §Novel-topic gate
- §Regression watch

---

## Eval corpus

The corpus deliberately mixes domains so breadth is tested across fields, not a single one.

| Eval topic | Reference (what coverage is compared against) | Domain |
|--|--|--|
| HTTP caching | RFC 9111 + Mark Nottingham's *Web Caching* (O'Reilly) | Technical (standards-body) |
| Spring Framework | `plugins/code-quality/skills/reviewing-java/agents/spring-reviewer/references/checklist.md` | Technical (framework) |
| Java concurrency | `plugins/code-quality/skills/reviewing-java/agents/concurrency-reviewer/references/checklist.md` | Technical |
| Java performance | `plugins/code-quality/skills/reviewing-java/agents/performance-reviewer/references/checklist.md` | Technical |
| Java security | `plugins/code-quality/skills/reviewing-java/agents/security-reviewer/references/checklist.md` | Technical |
| Java reliability | `plugins/code-quality/skills/reviewing-java/agents/reliability-reviewer/references/checklist.md` | Technical |
| Java maintainability | `plugins/code-quality/skills/reviewing-java/agents/maintainability-reviewer/references/checklist.md` | Technical |
| Java invariants | `plugins/code-quality/skills/reviewing-java/references/java-invariants-review-checklist.md` | Technical |
| Psychoanalysis (topic: transference) | PDM-2 syllabus + Laplanche & Pontalis *Vocabulaire de la psychanalyse* | Humanities (multilingual canon) |
| Container horticulture (topic: tomatoes in 15 L pots) | RHS grow-guides + Bayerische Landesanstalt für Landwirtschaft extension bulletins | Practical / craft |

When a new domain is added to the skill's expected scope, extend the corpus rather than re-using the same Java-heavy sample — corpus composition directly drives which non-obvious questions get scored as misses.

---

## Coverage metric

For each eval topic:
1. Run the skill against the bare topic name with no hints about the reference.
2. Extract every distinct sub-theme / question / rule / misconception / source / expert from the skill's output (the coverage map).
3. Load the reference; extract the same items.
4. **Recall** = (items in reference AND in output) / (items in reference). Target ≥ 0.90.
5. **Hallucination rate** = (items in output with sources that fail verification) / (items in output with sources). Target ≤ 0.02.

Reference items not in output → **miss**. Cluster misses by category (non-obvious questions / rules / misconceptions / sources / experts / sub-themes) before iterating the skill.

A dense map that passes recall but thin in §2 (non-obvious questions) is a *partial pass* — note the §2 gap as a skill-edit candidate even if recall crosses 0.90.

---

## reliable@10 description-trigger evals

### should-trigger (all 10 must route to `discovering-subtopics`)

1. Help me build a full question map for Kubernetes operators.
2. I'm planning a project around GraphQL — what should I research before committing?
3. Map out every subtopic I should cover for database transaction isolation.
4. What questions should I ask about Rust async runtime internals before choosing one?
5. Give me the body of knowledge for distributed consensus algorithms.
6. I'm starting to learn psychoanalysis — what are the main themes, blind spots, and canonical sources?
7. Brainstorm the full space of questions for growing tomatoes in containers.
8. Produce a coverage map for payment card industry compliance.
9. What are the canonical books, papers, conferences, and recognized experts for information retrieval?
10. Break down TLS 1.3 into the questions an expert would ask — including the non-obvious ones.

### should-not-trigger (all 10 must NOT route to `discovering-subtopics`)

1. Search for the latest documentation on X. → single-lookup retrieval
2. Is Y worth using in 2026? → opinion query
3. Review this file for bloat. → file audit
4. Is my document too long? → file audit
5. What does regulation §N.N require? → single factual lookup
6. Find me a good place to eat in city Z. → local lookup
7. Optimize this prompt for better routing. → prompt optimization
8. Review this pull request for bugs. → code review
9. Explain what a data structure is. → single definition
10. Find me the X-awesome list on a code host. → single retrieval

Failure modes to watch: false-trigger on #1/#2/#5/#9 (retrieval-only asks), overlap with #3/#4/#7 (single-artifact audits), overlap with #8 (review).

---

## Iteration loop

1. Generate a coverage map for each eval topic — dispatch one background agent per topic.
2. Dispatch `coverage-gap-auditor` per topic: inputs = `{generated_map, reference_path}`; outputs = miss list + hallucination list.
3. Batch cap: 4 parallel agents per message (prevents session-quota exhaustion).
4. Aggregate all auditor reports → single gap report grouped by miss category.
5. Each miss category → one targeted edit to `SKILL.md` or a reference file. Avoid global rewrites; token-economy evidence (Zhang §2.2) shows full-rewrite compression drops accuracy ~9.6 pp.
6. Re-run from step 1 until all topics ≥ 0.90 recall and ≤ 0.02 hallucination, OR 3 iterations (whichever first).
7. On stall (coverage plateaus below target after 3 iterations): document residual misses in `SKILL.md §Gotchas` rather than over-fit the workflow.

---

## Quality gate before commit

Per `/Users/aleksei/projects/claude-skills/CLAUDE.md`:
- Run `/auditing-ai-context` on `SKILL.md` and each reference file.
- MUST pass the self-review checklist and the reliable@10 description eval.
- Every rule in every file MUST cite a primary source (academic / technical standard / verified hands-on). Brainstormed-only rules MUST be cut or marked provisional.

Fail any of the above → block commit, iterate, re-run gate.

---

## Novel-topic gate (no reference available)

When no expert-authored reference exists, recall cannot be measured directly. Substitute:

1. **Two-runs-and-diff**: dispatch the skill twice in two fresh agents with identical inputs. Items present in only one run are the weak edge of discovery — promote to §7 meta open questions.
2. **Adversarial-expert lens**: ask "what would an expert in this field say this map misses?" — each plausible complaint is an open question in §0c.
3. **Density floor**: every §1 sub-theme MUST have ≥ 3 items across §2 (non-obvious Qs) / §3 (knowledge) / §5 (sources). A sub-theme falling below → cut it or mark as open.
4. **§2 floor**: every sub-theme MUST have at least one non-obvious question from Phase 4; a §1 leaf without any §2 row signals Phase 4 wasn't run for that branch.
5. **Hallucination gate**: re-verify every citation and every named expert before ship; make this a distinct final pass, not continuous.

---

## Regression watch

After the initial skill lands, re-run the eval when:
- A new reference is added to the corpus in any domain.
- A new Phase 4 lens is added to the skill — verify §2 coverage improves rather than merely shifts.
- A user reports a topic where the coverage map was thin — add that topic to the corpus (and note which domain it expands).

Pin model version in eval runs (Yang §3.3 — unspecified requirements ~2× more likely to regress across models). Re-run on every model upgrade.
