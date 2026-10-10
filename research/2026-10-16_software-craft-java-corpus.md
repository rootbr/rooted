# Design note — the Java language corpus of `software-craft`

The `reviewing-java` skill dissolves into `software-craft`, because its six-phase review was this skill's review path forked and this skill already carries a language corpus per language: its 231 Java cards — the rules that hold because of Java and its ecosystem: the memory model and `java.util.concurrent`, the JDK collections and I/O, Spring, Spring Security, JPA and Hibernate, Jackson, Resilience4j — are the Java language corpus `references/craft-cards-java/`, cards of the same schema; its nine `META-` cards that audit a project's `config.md` join the universal corpus under the `meta` domain; the skill and its two agent types leave the plugin. Both consumers take the Java corpus as a third `--cards-dir`: the developer agent lists its cards when the stack is Java, and the pre-pass dispatches a Java card only onto Java files (and onto build and configuration files when the card lists `build-config`).

This note is the design record of the corpus and of the dissolution. Each fact names its runtime owner; where this note and a runtime file differ, the runtime file decides. The universal design is `research/2026-09-26_software-craft-cards.md`, the Python corpus `research/2026-10-15_software-craft-python-cards.md`, the original record of the Java cards `research/2026-09-25_reviewing-java-rule-cards.md`. Paths are relative to `plugins/code-quality/skills/software-craft/` unless they start with `plugins/` or `research/`.

## Layout

```
plugins/code-quality/skills/software-craft/
|-- references/
|   |-- craft-cards/                   # the universal corpus, now with meta-01..09 (the config.md audit)
|   |-- craft-cards-java/              # java-NN--<slug>.md, one Java rule each, JAVA-01..JAVA-231
|   `-- craft-cards-python/            # the Python corpus
|-- maintenance/
|   |-- craft-cards-java-provenance.md # one line per Java card: citations, fetch status, origin section, formulation, notes
|   |-- pending-evidence-java.md       # Java rules held back for lack of an openable source
|   `-- java-invariants-review-checklist.md   # the guide to writing a Java project's config.md invariants
|-- evals/
|   |-- fixture-java/                  # base/ and head/ Java trees with .claude/software-craft/config.md; make-fixture.sh
|   |-- expected-java.json             # the seeds and controls of the Java fixture, by Java corpus id
|   `-- runs/fixture-java/             # the graded run's reports
`-- scripts/                           # cardlib.py registers JAVA; static-craft.py dispatches meta cards and Java candidates
research/
|-- 2026-10-16_software-craft-java-corpus.md   # this note
`-- 2026-09-25_reviewing-java-rule-cards.md    # the cards' original design record, kept as history
```

## What the corpus brings to the schema

The Java cards follow `maintenance/craft-cards-taxonomy.md` with the three differences every language corpus has — the `JAVA` prefix with any corpus domain, a `java` Example fence, a Thesis that may name Java, `applies_to` beginning with `java` — and four changes to the shared schema, each a decision the operator took on the recommendations listed under §Deviations from the recommendation:

| Change | Form | Reason |
|--|--|--|
| severity `critical` | a fourth level above `major` in `cardlib.SEVERITIES`, the workflow's scale, the renderer and the report: data loss, a security breach, data corruption under normal operation; the report recommends **Block** when one is confirmed | severity is a property of the finding, not of the language; 17 Java cards carry it, and a universal injection card rated `major` by the three-level scale was under-rated |
| domains `concurrency` and `security` | `cardlib.CORPUS_DOMAINS`; no universal prefix owns them, a language card may take them; `DOMAIN_PRIORITY` ranks `security` with `input` at 0 and `concurrency` with `errors` at 1 | the priority table decides a conflict on one span; folding 52 concurrency cards into `errors` would make it lie |
| domain `meta` | `META-` is a universal prefix; a meta card dispatches onto the project's `config.md` alone, by the meta dispatch of §Pre-pass | the dispatch onto one file needs a marker on the card, and the domain is it; the recommendation named `tooling`, which has no such gate |
| per-corpus job cap | `static-craft.py` applies `--max-jobs` to each cards directory separately | a Java diff now draws jobs from two corpora; one cap would drop the minor jobs of one corpus for the other's |

Two titles lost a colon the validator forbids (JAVA-155, the former REL-24, and JAVA-82, the former SEC-33); one Thesis lost the word "JavaScript" the language check reads as a second language (JAVA-55, the former SEC-06, now "script string" and "script context"); META-02's Thesis names "an added line" where it named "a line of Java". Nothing else in a card's prose changed.

## Facets and overlap

Each card needed three facets the review schema lacked — `domain` for the REL and MNT cards, `step`, `applies_to` — and a verdict on its overlap with the universal corpus. Eight `brief-judge` agents on Opus `xhigh` judged the 231 Java cards in batches by prefix (25, 24, 25, 25, 32, 30, 29, 41 cards), each from one brief holding the batch's titles, Theses, Limits and Validators and, per card, the six universal cards closest by title and thesis; a judge opened a universal card before every `defer` or `drop-java`; the cost sits in §Cost.

| Result | Count |
|--|--|
| relation `none` → keep | 132 |
| `java-form` → defer | 70 |
| `different-bound` → defer | 24 |
| `same-question` → drop, overturned to defer (below) | 5 |

Domains: concurrency 52, security 50, performance 37, errors 36, code 17, design 16, interface 13, tooling 8, tests 2. Steps: implement 206, design 93, handle-errors 54, refactor 13, test 7, document 4, review 1. Fifty-one cards are bound to a framework or library — Spring 18, Spring Security 13, JPA and Hibernate 6, SLF4J 3, Resilience4j 3, and one each for Jackson, gRPC, Jakarta, HikariCP, JSpecify, Mockito, JUnit and Micrometer; they stay in the corpus because their triggers name that framework's API, so a plain-Java diff never dispatches them.

A `defer` means both cards stay and, on a Java file, the Java card owns the span: `DEFER_TO[<universal id>]` lists the Java card, so the universal finding drops when the Java card flagged the same span; on every other language the universal card stands alone. The 99 defers give 71 universal cards a Java owner (`INP-09` nine, `ERR-07` and `INP-11` four each); the 19 intra-Java pairs of the review workflow carry over with their ids remapped, 90 entries in all. `scripts/craft-review-workflow.js` holds the table; `maintenance/README.md` §Deferring pairs lists the universal pairs and points here for the Java ones.

The five `same-question` drops went through the `refute-verdicts` workflow — two skeptics per verdict and an arbiter on each refutation, all on Opus `xhigh`, costed in §Cost — and none stood. Every skeptic found the same gap: a card's **triggers** are part of its coverage. The pre-pass dispatches a card onto a hunk only when one of its trigger patterns matches an added line, and the Java card's patterns name Java APIs — `containsKey(`, `ConcurrentMap<`, `@Retryable`, `getHeader(`, `BigDecimal.doubleValue()` — that the universal card's cross-language patterns never match. A Java hunk that the Java card would check reaches no finder once the card is gone, however closely the two Validators coincide; three of the five also had a Validator scope the universal card lacks (a POST under an existing retry, a lookup stored in a local and dereferenced later, a new literal call into an existing selector method). So a `same-question` relation is a `defer`, and the corpus keeps all 231 cards.

| Overturned drop | Universal card | The gap the skeptics opened |
|--|--|--|
| PF-06 → JAVA-105 a hash or comparison key is not mutated while in the collection | DSN-73 | `containsKey\(` and `ConcurrentMap<` dispatch the Java card and nothing dispatches DSN-73 on those hunks; DSN-73 traces only key types the hunk defines |
| REL-19 → JAVA-150 a POST or PATCH is retried only with an Idempotency-Key | ERR-38 | a POST added under an existing `@Retryable` or client retry, or wrapped in `Retry.decorateSupplier`, dispatches neither ERR-38's triggers nor its Validator, which reads added retries only |
| REL-30 → JAVA-161 a monetary amount is held in BigDecimal or a scaled integer | CODE-84 | camelCase money fields, `BigDecimal.doubleValue()` arithmetic and `Math.round(x*100.0)/100.0` match the Java triggers and not CODE-84's |
| REL-39 → JAVA-170 a value that can be null is checked before dereference | ERR-16 | ERR-16 dispatches on a dereference chained onto the lookup; a `getHeader` or `Map.get` result stored in a local and dereferenced later, the common Java shape, reaches only the Java card |
| MNT-02 → JAVA-192 a boolean selector parameter is replaced by one method per path | CODE-34 | CODE-34 keeps only a routine whose signature or boolean test is among the added lines; a new literal call into an existing selector method is the Java card's alone |

## Numbering

Ids are contiguous in shipping order, two digits to JAVA-99 and three from JAVA-100, assigned in the order of the former domains and their numbers:

| Former prefix | Java ids | Cards | Map |
|--|--|--|--|
| CC (concurrency) | JAVA-01..JAVA-49 | 49 | CC-k → JAVA-k |
| SEC (security) | JAVA-50..JAVA-99 | 50 | SEC-k → JAVA-(49+k) |
| PF (performance) | JAVA-100..JAVA-131 | 32 | PF-k → JAVA-(99+k) |
| REL (reliability) | JAVA-132..JAVA-190 | 59 | REL-k → JAVA-(131+k) |
| MNT (maintainability) | JAVA-191..JAVA-231 | 41 | MNT-k → JAVA-(190+k) |

The fixture's `expected-java.json`, the `DEFER_TO` table, the candidate table and every id inside a provenance line were rewritten through this map by script. The nine `META-` cards keep their ids.

## Pre-pass

`scripts/static-craft.py` gained three things from the review pre-pass. The meta dispatch: `.claude/software-craft/config.md` is denied as an ordinary reviewed file with the reason `review config`, its hunks (or, under `--meta`, the whole file as one hunk with status `unchanged`) form `inventory.config_file`, and a `meta` card's slice is drawn from that record alone; `meta_run` in the plan says whether the META cards ran. The Java candidates: `LANGUAGE_CANDIDATES["java"]` holds the nine mechanical heuristics (`Pattern.compile(` in a method body, `new SimpleDateFormat(`, `Runtime.getRuntime().exec(`, a weak `MessageDigest`, Jackson default typing, `new Random(` near a secret word, a synchronized wrapper on a concurrent map, `printStackTrace()`, an empty catch), run only on Java files, each naming the card that confirms it. The per-corpus cap, with the META jobs capped as a group of their own, so an overflowing universal corpus never drops the config audit. Slicing follows directories, which for Java are packages; the `modules` key of `config.md` takes `paths`, as the universal design states.

## Evals

The Java fixture of the review skill — nine Java files and a `config.md` with four invariants and a tolerance, 18 seeds across the six former domains and 19 controls — moved to `evals/fixture-java/` with the config at `.claude/software-craft/config.md`, and `evals/expected-java.json` names its seeds by Java corpus id. The run through the craft pipeline on the Java corpus and the META cards is the acceptance test of the dissolution: every seed found, every control silent. The universal corpus's jobs were filtered from the plan after the pre-pass, so what the two corpora do on one span — a universal card's deferral to a Java card — is checked by the aggregation's unit tests and not by this run.

The pre-pass over the fixture with all three corpora planned 177 jobs — 96 of the universal corpus at its cap, with 27 of its minor jobs dropped, 72 of the Java corpus and 9 META jobs in their own cap group — plus 3 logic slices and 4 invariants over 3 slices. The universal corpus's jobs were filtered from the plan after the pre-pass, since that corpus is graded on `evals/fixture`; the run dispatched 81 card jobs, 96 finders in all, and 48 skeptics, on Opus at the three tiers, with the plugin's `craft-finder` and `craft-verifier` types. Every finder raised 48 findings; the skeptics confirmed 38, modified 7, upgraded 1, downgraded 2 and rejected none; the fixture tree was unchanged after the run.

The first grading read 32 of 37: two corrections the run exposed, neither a finder's miss. The META seeds named the config file by its former path in `expected-java.json`, a slip of the migration script. And two seeds anchor on a field — the `LinkedList` field `Formatter#recent`, the `@Autowired` field `OrderService#repo` — where the finders wrote the enclosing type as the symbol: the craft symbol rule named a routine or a type and no field, which the review rule had named (`Class#field`). The rule in the finder prompt, the `FINDINGS` schema and `craft-finder.md` now names `Class#field for a field or constant`, and the two jobs ran again with their skeptics (4 agents, 0.25 M tokens): both findings came back anchored on the field and confirmed. Final grading: 18 of 18 seeds found, 19 of 19 controls silent, 30 further verified findings not graded — among them the credit-without-debit in `Totals#transfer` (the logic pass and invariant 4, critical), the unencoded HTML in `OrderService#render` (JAVA-55, critical) and the unbounded `Formatter#remember` list. `evals/evals.json` holds the figures under `fixture_java`; the reports sit in `evals/runs/fixture-java/`.

## Cost

| Step | Agents | Tokens | Wall-clock |
|--|--|--|--|
| facets and overlap judges | 8 | 0.92 M | 5.5 min |
| refute-verdicts on the five drops | 15 | 0.84 M | 3.0 min |
| scripts, validator and tests (one developer dispatch and one follow-up) | 1 | 0.78 M | 22 min |
| documents (one decision-worker) | 1 | 0.33 M | 14 min |
| fixture run: find, verify, the two-job re-run | 148 | 9.28 M | 6.8 min |

## Deviations from the recommendation

The session's analysis of 2026-10-16, from which the operator commissioned the change, recommended seven decisions: `critical` as a fourth severity; `concurrency` and `security` as domains of the language corpus; the framework-bound cards kept, gated by their triggers; the META cards ported with the config dispatch, under the domain `tooling`; `JAVA-NNN` ids with a map to the former ids; keep plus `DEFER_TO` as the default verdict on an overlap, a drop only where the Validators coincide and every drop through `refute-verdicts`; a hard cut to `.claude/software-craft/config.md` and version 8.0.0. The operator took all seven. Three landed otherwise:

1. The META cards take the domain `meta`: the `meta` row of §What the corpus brings to the schema states why, and `tooling`, with `applies_to: [build-config]`, dispatches on every file, so the config audit would run on every Markdown file of a diff.
2. Every card ships. The default was keep plus `DEFER_TO`, with a drop where the Validators coincide; five cards met that condition by the judges' reading, and dispatch runs on trigger patterns against added lines, so a Java card whose patterns name Java APIs is the only finder those hunks reach (§Facets and overlap).
3. Four cards changed a sentence: two titles for the validator's colon rule, two Theses for its language rule (§What the corpus brings to the schema).

## Audit

The Quality Gate ran the audit workflow in gate mode over the SKILL.md, the three agent definitions, this note and the two evidence-based-authoring SKILL.md files whose description names this skill: 104 agents on Opus, 3.77 M tokens, 5.1 min, 63 patches. Thirty-nine were applied: the SKILL.md description names the gh call and the configured report path; `design_intent` travels in `<target_excerpt>` to the finders and in `<task>` to the developer; the fallback names `FINDINGS` and `skepticPrompt` in the workflow script; the verifier's Bash rule and its file rule state the snippet exception as their condition, and its verdict rule names when a finding is `modified`; the finder's meta bullet says every line of the config slice is anchorable; the developer definition carries `tools: Read, Grep, Glob, Edit, Write, Bash`, as SKILL.md states, names the four reserved specialties in its description and sends a self-review fix that would change the brief to an open question; eleven restatements and foils in this note went. Dismissed, each in text this change did not write: the skill's name carries no verb (R-01: a rename breaks the slash command); the descriptions of `appraising-research` and `researching-topics` advertise neither their file writes nor their web calls (R-06, R-77, R-02: those skills' own matter); the pointer to G-17 and the "Why" of Phase 6 (R-47, D-05); the order of Phase 7 and Phase 8 around `craft/verdicts.json` (R-70, a defect of the fix round to take up on its own); the illustrative paths and names in the developer's examples (R-40).

## Open

- Thirty-three Java cards carry more than eight triggers; the validator warns on each. The review corpus's trigger discipline allowed it; a pass that narrows them to the craft form of two to six is authoring work with a fixture check per card.
- The universal `input` cards that state a security rule — `INP-02` SQL binding, `INP-03` output encoding, `INP-06` deserialization — keep `major`; with `critical` in the scale their severity is a re-rating pass over the universal corpus with its own skeptic round.
- The developer agent's smoke task has not been re-run on a Java task.
