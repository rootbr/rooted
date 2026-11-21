# Rooted

Claude Code plugin marketplace — rooted in evidence.

## Orientation

Read `README.md`, then run `./overview.sh` to orient.
Read individual files only if the output is not sufficient for the user's request.

## Quality Gate

MUST run `/auditing-ai-context` on every SKILL.md or agent prompt change before committing.

`python3 check-skill-layout.py` passes before a commit that touches `plugins/`.

`python3 -I plugins/evidence-based-authoring/skills/scientific-method/scripts/check_record.py --root . --staged` passes before a commit that touches a provenance map or a list of hypotheses.

## Method

The repository admits rules by the scientific method: a rule that claims a technique works rests on a test that could have refuted the claim.

Before adding or changing a rule, a checklist item or a review criterion, take it through `/scientific-method` and write its record: a decision with its owner and goal, a definition with its term, a norm with its document opened, a claim with its refuting outcome and its test. A claim with no test yet waits in its skill's list of hypotheses, and a claim that names no refuting outcome stays out.

The full method — four kinds of statement, seven standings of a claim, seven rules, one acceptance path with a path of its own for a claim about one event — is `plugins/evidence-based-authoring/skills/scientific-method/references/method.md`.
