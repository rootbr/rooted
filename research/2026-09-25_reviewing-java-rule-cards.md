# Design note — `reviewing-java` on atomic rule cards

The `/reviewing-java` skill reviews a Java diff through a corpus of atomic rule cards. A deterministic pre-pass matches each card's triggers against the added lines of the diff and writes a dispatch plan; a Workflow script runs one finder per (card × slice) plus one logic pass per slice, aggregates deterministically, and runs one skeptic per finding; a render script turns findings and verdicts into two Markdown reports. Every card rests on an openable source; a rule with no such source is held in `pending-evidence.md` and ships nowhere.

This note is the design record: the layout, the card schema and its controlled vocabulary, the concept-ownership and priority tables, the `plan.json` contract, the workflow contracts, the source policy, the fixture and grading design, and the deviations from the brief that commissioned the rebuild. The runtime owners of the same facts are named in each section; where this note and a runtime file differ, the runtime file decides. Paths are relative to `plugins/code-quality/skills/reviewing-java/` unless they start with `plugins/`.

## Layout

```
plugins/code-quality/
├── agents/
│   ├── review-finder.md              # code-quality:review-finder
│   └── review-verifier.md            # code-quality:review-verifier
└── skills/reviewing-java/
    ├── SKILL.md                      # orchestration; under 500 lines; disallowed-tools: Edit, NotebookEdit
    ├── README.md
    ├── references/
    │   ├── review-cards/             # <prefix>-NN--<slug>.md, one rule each
    │   ├── review-cards-taxonomy.md  # corpus schema, controlled vocabulary, deltas from the base card spec
    │   ├── review-cards-provenance.md# rule_id · full citation · origin section · formulation source · notes
    │   ├── pending-evidence.md       # rules held back for lack of an openable source
    │   ├── gotchas.md                # G-NN, symptom-indexed
    │   └── java-invariants-review-checklist.md   # author-facing guide to writing config.md invariants
    ├── scripts/
    │   ├── static-review.py          # pre-pass: diff + cards + config → review/plan.json, review/plan.log
    │   ├── review-workflow.js        # Find → Aggregate → Verify → Refute
    │   ├── bundle-run.py             # plan + intent + context → review/run.js (the workflow with its arguments embedded)
    │   ├── render-reports.py         # findings.json + verdicts.json → two Markdown reports
    │   ├── validate-review-cards.py  # mechanical corpus validator
    │   └── tests/                    # unit tests for the pre-pass
    └── evals/
        ├── evals.json
        ├── expected.json             # per seed the (rule_id, file, symbol) triple; per control the silent rule_ids
        └── fixture/                  # base/ and head/ Java trees; make-fixture.sh builds a two-commit git repo
```

The plugin-level `agents/` directory holds the two agent types because a Claude Code plugin resolves agent types only from that directory, under the namespace `<plugin>:<name>`; a skill-local `agents/` folder is invisible to the dispatcher.

## Card schema

A review card is a specialization of the base KB card specification (`plugins/evidence-based-authoring/skills/auditing-ai-context/references/kb-card-specification.md`) for one consumption model: the card is dispatched whole to one finder sub-agent that holds only the card, the matching diff hunks and the inventory. The specialization is documented in `references/review-cards-taxonomy.md`, which is the owner of the schema; this section carries the design reasons.

Frontmatter, exactly these keys in this order:

| Field | Values | Role |
|--|--|--|
| `title` | the rule as one complete, checkable declarative claim | the index line and the H1 |
| `rule_id` | `CC-NN` concurrency · `SEC-NN` security · `PF-NN` performance · `REL-NN` reliability · `MNT-NN` maintainability · `META-NN` config.md audit | stable id; a finding is `<rule_id>.<ordinal>` |
| `domain` | `concurrency` · `security` · `performance` · `reliability` · `maintainability` · `meta` | ownership and conflict priority |
| `triggers` | list of Python `re` patterns matched line by line against the added lines of the diff | dispatch facet; `[]` means every diff and is reserved for always-on cards |
| `scope` | `hunk` · `file` · `base-compare` · `callers` | what the finder reads beyond the hunk |
| `check_kind` | `mechanical` · `semantic` | what the finder must establish before it emits; the two values are defined under §Controlled vocabulary |
| `severity_default` | `critical` · `major` · `minor` · `suggestion` | starting severity; the verifier calibrates |

Body blocks in this order: `## Thesis` → `## Rationale` → `## Example` → `## Limits` → `## Validator` → `## Finding output` → `## Source`.

Design reasons behind the deltas from the base specification:

- **Triggers replace retrieval facets.** No agent greps a pool of cards; the pre-pass selects cards by matching their triggers against the diff. A trigger is a coarse net: a false trigger costs one finder run that returns an empty array, a missed trigger costs a missed defect, so triggers err broad. A card with `[]` triggers runs on every diff; the corpus keeps that set to a handful, because each always-on card is one finder per slice on every review.
- **`scope` declares the reading budget.** A `hunk` card decides from the added lines alone; a `file` card reads the whole file at HEAD; a `base-compare` card also reads the base version through `git show <base_sha>:<file>`; a `callers` card also greps usages across the repository. The finder prompt states the card's scope so the agent neither under-reads a semantic card nor over-reads a mechanical one.
- **`## Validator` is a corpus-local block.** A review rule has an operative check distinct from its rationale: what to grep, what to trace, and one binary question in bold whose "yes" is the finding.
- **`## Finding output` is the consumer block**, one name across the corpus. It states what the finder emits and with which fields, so the card and the workflow's `FINDINGS` schema agree by construction.
- **`## Example` is Java of up to about eight lines**, a `bad:` / `good:` pair with generic names. The base specification's three-line everyday-domain pair does not carry a Java defect; the reader of a review card is a Java reviewer and the domain is the card's own.
- **`## Source` stays in the card as a compact locator** while the full citation, the origin section and the formulation source live in `references/review-cards-provenance.md`. The finder does not fetch sources at runtime; the locator serves the human reading a finding and the verifier calibrating it. Prose blocks stay attribution-free.
- **No `links`, `tags`, `confidence`, `defines`, `uses`.** Cards are dispatched, never traversed or grepped; evidence strength is a note in the provenance map; a card defines its terms inline where the Thesis needs them.

Self-containment is strict: a card names no sibling card id, no "the skill", no "the checklist", no "see above". Its reader holds only the card, the hunks and the inventory.

### Numbering

Ids are assigned per domain in the order of the domain's review-checklist spine, counting shipped cards only, so the provenance map reads in source order:

| Domain | Spine | Folded in | Appended after the spine |
|--|--|--|--|
| concurrency | checklist sections 5.1–5.18 in order | sections 1–4 supply rationale and the `bad:`/`good:` pairs of the matching section-5 item; section 7 folds into the virtual-thread items of 5.13 | a rule stated only in sections 2–4 with no section-5 item, in section order |
| security | checklist sections 16.1–16.13 in order | section-15 `bad:`/`good:` pairs fold into the matching section-16 item; sections 1–13 supply rationale | a rule stated only in sections 1–13 or 15, in file order |
| performance | file order, sections 1 to 7: the "What to look for" bullets, the section-4 patterns, the section-5 review items, the section-7 anti-patterns | a rule stated twice keeps its first statement | none |
| reliability | checklist sections 8.1–8.7 in order | sections 1–7 supply rationale and the pairs | a rule stated only in sections 1–7, in file order |
| maintainability | checklist sections 5.1–5.11 in order | section-4 patterns fold into the matching section-5 item; sections 1–3 supply rationale | a rule stated only in sections 4 or 7, in file order |
| meta | section 2, the anatomy of an invariant (parts 3–5 each a card), then anti-patterns 3.1–3.8 | section 1 supplies rationale | none |

A rule stated in two sections of one checklist is one card whose provenance line names both origins. A rule that two checklists state is one card in the domain the concept-ownership table names, with the other checklist's section recorded as a second origin.

## Controlled vocabulary

`review-cards-taxonomy.md` owns the allowed values.

| Facet | Value | Meaning at runtime |
|--|--|--|
| `scope` | `hunk` | the finder reads the added lines and their hunk context only |
| | `file` | plus the whole file at HEAD |
| | `base-compare` | plus the base version of the file (`git show <base_sha>:<path>`) |
| | `callers` | plus usages of the changed symbols across the repository (`grep`) |
| `check_kind` | `mechanical` | the pattern is the finding once one light context question is confirmed (hot path? user input? shared field?); routed to the `mechanical` tier |
| | `semantic` | the finder traces a chain (happens-before, taint, a query inside a loop, an API contract); routed to the `semantic` tier |
| `severity_default` | `critical` | data loss, a security breach (remote code execution, injection, auth bypass), data corruption under normal operation |
| | `major` | a correctness bug, a resource leak that degrades over time, a concurrency defect that yields wrong results, a security defect needing specific conditions |
| | `minor` | a performance cost, a clarity problem, missing error handling for an unlikely scenario |
| | `suggestion` | style, documentation, naming |

The four severity definitions are the verifier's calibration scale; `agents/review-verifier.md` is their runtime owner.

## Concept ownership and priority

Two mechanisms keep one defect from surfacing twice. At carding time a concept has one owning domain, so the sibling checklist's statement of the same rule folds into the owner's card and no second card exists. At aggregation time, when two cards still flag one span, a rule-level defer map and a domain-priority order decide.

Concept ownership at carding time:

| Concept | Owner | Folded from |
|--|--|--|
| Resource leak: `AutoCloseable`, streams, JDBC objects, HTTP responses, `ThreadLocal` entries, direct buffers, listeners, class-loader roots | reliability | performance 4.7 buffer-per-request keeps its performance framing; maintainability defers |
| Executor and thread lifecycle: creation, bounding, shutdown, saturation, rejection, backpressure | concurrency | reliability 1.4 and 8.1 executor bullets; performance 4.6 |
| Lock scope, lock object, lock ordering, alien calls under a lock | concurrency | performance section-3 lock-cost bullets fold in as a note |
| Data race, visibility, atomicity, safe publication, `ThreadLocal` on pooled carriers | concurrency | — |
| Thread-safety of a shared library object (`SimpleDateFormat`, `HashMap`) | concurrency | performance 4.3 keeps the per-call construction cost only |
| Untrusted input reaching a sink, cryptography, secrets, deserialization, headers, session and token handling | security | reliability 5.5 request-validation bullets that concern injection |
| Silent failure: a swallowed exception, a dropped cause, an unobserved `Future` | reliability | concurrency 5.8 `Runnable` and `CompletableFuture` items fold in; maintainability 4.8 |
| Double logging, exception translation at a layer boundary, exception-for-control-flow | maintainability | performance 4.11 keeps the hot-path cost |
| Leaking internals in an error response or a log line | security | — |
| Allocation, collection choice, hash quality, JIT shape, cache layout, I/O buffers, hot-path anti-patterns | performance | — |
| Timeouts, retries, circuit breakers, bulkheads, fallbacks on remote calls | reliability | concurrency 5.18 retry-amplification and monotonic-policy items |
| Transactions, JPA, N+1, connection-pool sizing | reliability | performance defers on N+1 |
| REST status codes, idempotency, pagination, versioning, backward compatibility, graceful shutdown | reliability | — |
| Function shape, naming, complexity, SOLID, API design, testability, documentation, logging style, DI style, project structure, configuration | maintainability | — |
| Quality of `config.md` invariants | meta | — |

Rule-level `DEFER_TO` map (the workflow's mirror is in `scripts/review-workflow.js`): populated after the series from the pairs the reviewers find still overlapping; each entry names a deferring `rule_id` and its owner. A finding drops when its owner also flagged the same span.

Domain priority for a genuine conflict (same span, incompatible fixes):

| Priority | Domain |
|--|--|
| 0 | security |
| 1 | concurrency, reliability |
| 2 | performance |
| 3 | maintainability |
| 3 | meta |

A tie at the top priority keeps both findings and flags them for the author. Two fixes are compatible when one fix's code, whitespace-normalized, is a substring of the other, or the two are equal; the higher-priority finding is kept and the other's `rule_id` is appended as "also <rule_id>". Two fixes that differ are a conflict. `SKILL.md` §Aggregation is the runtime owner of these definitions.

## Pre-pass contract — `review/plan.json`

`scripts/static-review.py` reads `git diff -U0 <diff_ref> -- '*.java' [path_filter]`, every card's frontmatter, and `.claude/reviewing-java/config.md`; it writes `review/plan.json` and `review/plan.log` and nothing else. Standard library only, no network.

```
{
  "inventory": {
    "diff_ref": "<base_sha>...<head_sha>",  "base_sha": "...", "head_sha": "...",
    "path_filter": "",
    "size_class": "SMALL" | "MEDIUM" | "LARGE",       // 1–19 · 20–49 · 50+ changed Java files
    "file_count": N,
    "files": [ { "path": "src/main/java/a/b/C.java", "package": "a.b", "top_package": "a",
                 "status": "added" | "modified" | "renamed",
                 "hunks": [ { "start": 42, "lines": [ { "no": 42, "text": "..." } ] } ],
                 "added_lines": N } ],
    "build_files": [ "pom.xml" ],
    "config_path": ".claude/reviewing-java/config.md" | null,
    "config_changed": true | false,
    "config": { "project_name": "...", "base_branch": "...", "review_output": "...", ... } | null
  },
  "cards": [ { "rule_id": "CC-14", "path": "/abs/.../cc-14--....md", "title": "...", "domain": "concurrency",
               "triggers": ["..."], "scope": "file", "check_kind": "semantic", "severity_default": "major" } ],
                                                    // the dispatched cards only: every rule_id a job or a candidate names
  "jobs": [ { "id": "CC-14:core", "rule_id": "CC-14",
              "slice": { "name": "core",
                         "files": [ { "path": "...", "hunks": [ 0, 2 ], "added_lines": N } ],   // indices into inventory.files[path].hunks: the matching hunks only
                         "added_lines": N } } ],
  "slices": [ { "name": "core", "packages": ["a.core"], "files": ["..."], "added_lines": N } ],
  "candidates": [ { "id": "pattern-compile-in-method", "rule_id": "PF-NN" | null, "file": "...", "line": 17,
                    "text": "...", "status": "needs_verification" } ],
  "project_cards": { "cards": [ { "rule_id": "PROJ-1", "title": "...", "thesis": "...", "validator": "...",
                                  "rationale": "..." } ],
                     "card_paths": [ ".claude/reviewing-java/cards/x.md" ] },
  "meta_run": true | false            // META cards run: config.md changed in the diff, or --meta was passed
}
```

Job construction: for each card, the slice is the set of files whose added lines match any trigger, carrying only the matching hunks, each named by its index in the file's inventory record so that no hunk text is repeated across jobs and the plan stays small enough to travel verbatim as the workflow's arguments (a `META-` card's file is `inventory.config_file`). A card with `[]` triggers matches every file. One card's slice stays one job while its added lines total at most 400; above that it splits by the package prefix one segment below the changed files' common root, or by the module boundaries the config's optional `modules:` frontmatter key names (`modules: [{name, packages: [..]}]`). The total job count is capped at 96, and every action the cap forces is written to `review/plan.log`:

1. the jobs of the card with the most jobs are merged back into one, repeated while any card holds more than one job;
2. then the smallest job of a `suggestion` card is dropped;
3. then the smallest job of a `minor` card;
4. a `major` or `critical` job is never dropped: the log records by how much the cap is exceeded and every job is kept.

Logic-pass slices: files grouped by module boundary where the config names one, else by top-level package; the group count is held between 3 and 8 for every size class by merging the smallest groups upward or splitting the largest by sub-package downward; with fewer than three changed files, one slice per file.

Candidates are mechanical hits the regexes can name outright, tagged `needs_verification` so the finder confirms instead of searching:

- `Pattern.compile(` inside a method body (an added line without `static`);
- `new SimpleDateFormat(`;
- `Runtime.getRuntime().exec(`;
- `MessageDigest.getInstance("MD5")`, `("SHA1")` or `("SHA-1")`;
- `enableDefaultTyping(` or `activateDefaultTyping(`;
- `new Random(` within five added lines of `token`, `secret`, `password`, `nonce`, `salt` or `otp`;
- `Collections.synchronized*(new Concurrent…`;
- `.printStackTrace()`;
- `catch (…) {` followed by an empty block.

Project cards: the numbered invariants in the Markdown body of `config.md` — `N. **Title**: rule. Violation: consequence.` — become synthetic `PROJ-N` cards: title from the bold title, Thesis from the rule text, Validator from the sentence after "Violation:", Rationale from any scale numbers in the same item. Each becomes one job per logic slice at the `semantic` tier. Files under `.claude/reviewing-java/cards/*.md` are taken as written and indexed like shipped cards.

## Workflow contracts

`scripts/review-workflow.js`, run as a bundle: `scripts/bundle-run.py` embeds the run's arguments (`root`, `stage`, `plan`, `design_intent`, `project_context`, `findings`, `tiers`, `agentTypes`) as `const EMBEDDED_ARGS` after the script's `meta` block and writes `review/run.js`, which the orchestrator calls through `Workflow({ scriptPath })` with no `args`. The plan of a real diff is hundreds of kilobytes, and a Workflow argument is typed into the tool call by the orchestrating model; the bundle carries the plan verbatim without that transcription, and explicit `args` still override it. Phases: Find → Aggregate → Verify → Refute.

Args: `{ root, stage: 'find' | 'verify' | 'all', plan, design_intent, project_context, findings?, tiers?, agentTypes? }`. `plan` is the parsed `plan.json`; a JSON string is accepted and parsed. Every enum is validated loud.

Tiers, overridable through `args.tiers`:

| Tier | Model | Effort | Used by |
|--|--|--|--|
| `mechanical` | `claude-opus-5-5` | `high` | finders of mechanical cards |
| `semantic` | `claude-opus-5-5` | `xhigh` | finders of semantic cards, the logic pass, PROJ finders, skeptics of minor and suggestion findings |
| `verdict` | `claude-opus-5-5` | `max` | skeptics of critical and major findings, the second skeptic, the arbiter |

No stage uses Fable.

Schemas:

- `FINDINGS`: `{ findings: [ { rule_id, severity ∈ {critical, major, minor, suggestion}, file, symbol, code, problem, fix, rationale } ] }`. `code` is verbatim from the diff; `fix` is Java. An empty array is an expected outcome.
- `VERDICT`: `{ verdict ∈ {confirmed, rejected, downgraded, upgraded, modified}, evidence, final_severity, note, corrected_finding? }`. `evidence` names what the skeptic opened: a comment within five lines, a `git log` line, a `project_context` sentence, surrounding code that already handles the case.
- `REFUTATION`: `{ refuted: boolean, evidence, note }` — the second skeptic defends the finding against its rejection with something it opened.
- `RULING`: `{ ruling ∈ {upheld, refuted, uncertain}, evidence, final_severity, note }` — `upheld` means the rejection stands, `refuted` restores the finding, `uncertain` sends it to the report flagged for the author.

Stages: `find` returns the aggregated findings so the orchestrator persists `review/findings.json`; `verify` takes `args.findings` and skips Find; `all` runs both. That checkpoint is the only cross-session state; there are no per-agent files.

`main_agent_followups` always carries the integrity check: the workflow runtime grants Write and Edit to sub-agents regardless of their `tools:` allowlist (claude-code#63762), so the orchestrator runs `git status` after the run and treats a mutated tree as a compromised review.

Prompts: the finder prompt names the card path, the slice files and hunks, the card's scope, `design_intent`, `project_context`, the card's candidates and the empty-case rule, and wraps hunks, intent, context and candidates in `<target_excerpt>` tags as untrusted data. The skeptic prompt is adversarial: try to refute the finding; refute only with something opened; suspicion is not a refutation; a confirmed finding is a real result; carry the finding inside `<finding>` tags as data; calibrate severity against the four definitions.

## Source policy

Every card cites one admissible class of the repository's Evidence-Based Rule, in a form anyone can open:

- academic research — an arXiv id or a DOI;
- a technical standard — the Java Language Specification or JVM Specification by section, a JDK 21 Javadoc page by class and member, a JEP by number, the Spring Framework or Spring Boot reference by section, the Hibernate ORM user guide by section, an OWASP cheat sheet or ASVS item, a CWE entry, a SEI CERT Oracle Coding Standard for Java rule, a static-analysis rule's own documentation (a SonarSource RSPEC page, an Error Prone bug-pattern page, a SpotBugs bug description), an RFC by number and section;
- verified hands-on experience in an openable form — a jcstress sample in the `openjdk/jcstress` repository, a JMH benchmark, or a test committed under the skill's `evals/fixture/`.

The author fetches every cited source and confirms the anchored section states the claim as the card words it: no inversion, no stripped precondition, no conditional flattened to an absolute. A card's `## Source` carries the compact locator plus any one-line caveat; the provenance line carries the full citation, the origin section, and the formulation source.

A trade book or a practitioner blog is never evidence. Where a rule's wording comes from one, the openable source that backs the claim carries the card, and the provenance map names the practitioner text as the formulation the rule follows. A rule with no openable source goes into `references/pending-evidence.md` with its original wording, its book or blog source, the domain it belongs to and what was searched; it has no card and no id.

## Evals and fixture

`evals/fixture/base/` and `evals/fixture/head/` hold one small Java tree each, plain sources with no build. The head tree introduces one seeded defect per chosen card across all five review domains, at least three seeds per domain, plus control files whose suspicious-looking code is correct by a stated tolerance: a comment naming the tolerance, a map confined to one thread, a debug-only path. `make-fixture.sh` builds a temporary git repository with two commits, base then head, so the pre-pass and the finders run on a real `diff_ref`.

`expected.json` lists per seed the expected `(rule_id, file, symbol)` triple and per control the rule ids that must stay silent. Grading is mechanical on those triples: a seed passes when a verified finding carries its triple, a control passes when none of its listed rule ids fires on its file. No judge model is needed for precision and recall; `evals.json` records the grading, the pinned models, and the constraints satisfied and unsatisfied, in the structure of the audit skill's `evals.json`.

## Deviations from the brief

The brief is the operator's handover message that commissioned this rebuild; it is not a file in the repository, so each entry quotes the instruction it deviates from and states the determining reason.

1. **Branch.** The brief says "Work on branch `feat/reviewing-java-rule-cards`". The work is committed on that branch, and every push mirrors the same commits to the branch the session environment designates for its pushes, because that environment binds pushes to its designated branch and the operator follows it in the session view.
2. **`modules:` config key.** The brief says "`config.md` frontmatter keys keep their meaning" and lists seven keys. One optional key `modules: [{name, packages}]` is added, because the pre-pass has no LLM and cannot read module boundaries out of the prose body; without the key it splits by package prefix.
3. **Executor lifecycle ownership.** The brief's pilot section, reliability 8.1, carries `ExecutorService.shutdown()`, and the concurrency checklist's section 5.7 carries nine items on the same lifecycle. Concurrency owns executor and thread lifecycle and the reliability bullets fold into those cards, because one owner per concept is what keeps a span from being flagged twice.
4. **Six pilot cards.** The brief says "five cards from two adjacent sections". Six were written, because the stream-closing rule split from the `AutoCloseable` rule on its own trigger and source, and a finder needs the split to tell a collection stream from a file stream.
5. **Two concurrency drafts folded into performance cards.** The brief says "every checklist item of a domain becomes a card of that domain". The concurrency checklist's mutable-key-in-a-concurrent-map item and its false-sharing item are carried by the performance cards for mutable hash keys and for cache-line padding, because both state one concept the performance domain owns, and one owner per concept is what keeps a span from being flagged twice; the provenance map records each fold.
6. **One sourced rule without a card.** The brief says "a rule with a source gets a card; a rule without one goes to `pending-evidence.md`". The security checklist's Thymeleaf `th:utext` item has an openable source and no card, because the pre-pass diffs `*.java` files only, so no finder would ever see a template; it sits in the provenance map's "Rules without cards" table with that reason, and a template-file pass is an open question for the operator.
7. **Removals never dispatch.** The brief's pre-pass contract says "a card runs on a file when any trigger matches any added line". A `base-compare` card whose defect is a pure removal (a public member deleted without a deprecation cycle) therefore never runs, because a removal adds no line; the card's Limits say so, and a removed-line channel for `base-compare` cards is recorded as an open question, not implemented.
8. **Agent names.** The brief names the agent types `code-quality:review-finder` and `code-quality:review-verifier`. The audit's naming rule asks for a verb and an object in an agent name; the brief's names stay, because the workflow script, the skill and the fallback path all address the agents by them, and the descriptions carry the verb, the object and the "use when" trigger.
9. **Complementary fixes on one span.** The brief's aggregation contract folds compatible fixes and resolves incompatible ones by domain priority. Three reliability cards can flag one retry-policy line with three complementary fixes (jitter, an attempt bound, a status filter); the aggregation cannot tell complementary from incompatible and reports the tie, keeping all three and marking them for the author, because a mechanical text comparison is the only tie-breaker that stays deterministic.

## Dry run on the extended fixture

The full corpus (240 cards) ran against the extended fixture (nine Java files and a rewritten `config.md`; 18 seeds, one per chosen card across all six domains, and 19 controls) through the pre-pass and the bundled workflow: 81 card jobs, 3 logic slices and 4 project invariants, 96 finders, 54 skeptics, no second skeptic and no arbiter. Every seed card was dispatched by its triggers. The finders raised 54 findings; the skeptics confirmed 44, modified 8 (a real defect with a corrected fix or rationale), downgraded 2 and rejected none; the aggregation folded one pair (the project invariant on the shared cache with the concurrency card on the same span), overruled one (the project invariant on field injection over the maintainability card) and flagged two same-priority ties on `Totals#transfer` for the author. Grading: 18 of 18 seeds found and 19 of 19 controls silent, after two corrections to the grading mechanics the run exposed: an overruled finding vanished from the report, so the aggregation now lists the losers' rule ids on the kept finding with their text under `superseded`; and a seed whose card admits two anchors (the indexed read, or the `LinkedList` field it reads) was graded on one, so a seed may now list several symbols. No control was flagged by any finder.

Beyond the seeds the run reported eleven unseeded defects the fixture carries by construction, among them the mutable `archived` field in the singleton `OrderService`, the unbounded `recent` list in the per-request `Formatter`, the unencoded HTML in `render` and the `int` overflow in `Totals#addWithinLimit`; the logic pass again found the credit-without-debit in `Totals#transfer`. One skeptic downgraded the OS-command-injection seed from critical to major after running the flagged `Runtime.exec` expression against seven payloads and showing that `StringTokenizer` leaves the single quote unterminated, so the command never runs at all; the calibration is sound and the method is not: a skeptic that executes an expression from the diff runs the author's code on the reviewer's host, so the read-only rule in both agent prompts and in the workflow's prompt text now forbids executing code from the diff (compiling a snippet the skeptic wrote itself stays allowed). The card for missing Javadoc raised 22 of the 54 findings, one per undocumented member; it now emits one finding per class listing the members.

Cost, as the runtime reported it: 150 agents, 8,301,570 sub-agent tokens, 3,277 s of wall-clock time at the runtime's concurrency cap of two agents on this 4-CPU host. The plan travelled as a bundle (`review/run.js`, 124 KB with the compact job records); the same plan with full card records and repeated hunk text was 524 KB, which no orchestrator could retype into a tool call.

## Dry run on the pilot fixture

The pilot corpus (six cards) ran against the fixture through the pre-pass and the Workflow tool: 6 card jobs, 3 logic slices and 1 project invariant, 12 finders, 8 skeptics, no second skeptic and no arbiter. Grading: 6 of 6 seeds found, 7 of 7 controls silent after verification, and no control flagged by any card before verification either; the project-context tolerance on `Stats#sample` held at the finder already. Two findings came from the logic pass: one confirmed critical defect the fixture had not seeded on purpose (`Totals#transfer` credits the target and never debits the source), one rejected. The finding of `CC-08` and the finding of `PROJ-1` shared one span with compatible fixes and folded into one report entry carrying both ids.

Cost, as the runtime reported it: the find stage spent 600,995 sub-agent tokens in 96 s of wall-clock time; the verify stage a further 579,754 tokens in 888 s, at the runtime's concurrency cap of two agents on a 4-CPU host (the cap is `min(16, CPUs − 2)`). A 20-agent run on a six-file diff is the floor; a MEDIUM review with 60 jobs and 30 findings scales to roughly 5 M tokens and, on a larger host, tens of minutes.
