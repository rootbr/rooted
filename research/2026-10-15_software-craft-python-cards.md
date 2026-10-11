# Design note — the Python language corpus of `software-craft`

The `/software-craft` skill reviews and builds code against the universal craft cards; this corpus adds the rules that hold because of Python itself — the data model, its exception machinery, its typing layer, its standard library and its test runner — as cards of the same schema in a directory of their own, `references/craft-cards-python/`. Both consumers take it as a second `--cards-dir`: the developer agent lists its cards beside the universal ones when the stack is Python, and the pre-pass dispatches a Python card only onto Python files (and onto build and configuration files when the card lists `build-config`). 178 cards across 12 topics, 5 rules waiting in the Python pending map.

This note is the design record of the corpus. Each fact names its runtime owner; where this note and a runtime file differ, the runtime file decides. The universal design is `research/2026-09-26_software-craft-cards.md`; this note states only what the language corpus adds. Paths are relative to `plugins/code-quality/skills/software-craft/` unless they start with `plugins/` or `research/`.

## Layout

```
plugins/code-quality/skills/software-craft/
|-- references/
|   |-- craft-cards/                      # the universal corpus
|   |-- craft-cards-python/               # py-NN--<slug>.md, one Python rule each
|   |-- craft-cards-python-provenance.md  # one line per Python card: citations, fetch status, topic, reception, notes
|   |-- pending-evidence-python.md        # Python rules held back: no separating condition, or no openable source
|   `-- craft-cards-taxonomy.md           # the shared schema; its "Language corpora" section states the three differences
`-- scripts/
    |-- cardlib.py                 # LANGUAGE_PREFIXES, prefix_domain_ok, language_of_card
    |-- validate-craft-cards.py    # --language python: the corpus mode of the validator
    |-- static-craft.py            # repeatable --cards-dir; dispatches_on() keeps a language card on its language's files
    |-- craft-cards.py             # repeatable --cards-dir; one listing over both corpora
    |-- harvest-python-sources.py  # authoring: the catalogs (Ruff, Pylint, SonarSource, Bandit, flake8-bugbear) to items.jsonl + a text cache
    |-- python-corpus.py           # authoring: triage briefs, triage merge, topic args, save-run
    |-- check-python-cards.py      # authoring: validator + ast.parse + trigger hits + locators and quotes resolve, per draft
    |-- python-triage-workflow.js  # authoring: one brief-judge per batch of harvested items
    |-- python-topic-workflow.js   # authoring: spine -> draft packs -> skeptic packs -> closing edit, one topic
    `-- tests/                     # test_harvest_python_sources, test_python_corpus, test_check_python_cards, the validator's language tests
research/
|-- 2026-10-15_software-craft-python-cards.md   # this note
`-- software-craft-python/<topic-slug>.md       # one research note per topic: evidence layer, spine, cards derived, rules held back, cost
```

The universal corpus and the language corpus share one schema, one validator and one pre-pass; the language corpus differs in three facts of its cards (§Schema differences) and in its evidence (§Sources). The authoring scripts and workflows stay in `scripts/` as the universal `research-topic-workflow.js` does: authoring time only, never in a build or a review.

## Schema differences

A Python card follows every rule of `references/craft-cards-taxonomy.md` except three, which the validator's `--language python` mode enforces and the taxonomy's "Language corpora" section states:

| Field | Universal card | Python card |
|--|--|--|
| `rule_id` and filename | `<PREFIX>-NN` with the prefix naming the domain | `PY-NN` (three digits from PY-100) with any craft domain in `domain:` |
| Example fence | one of five languages, rotated across the corpus | `python`, always |
| Thesis and title | names no language | may name Python, its modules and its syntax |
| `applies_to` | a facet list of traits | begins with `python`; further traits follow |

Dispatch: `static-craft.py` loads both directories into one pool (a duplicate `rule_id` across them stops the run), and `dispatches_on(card, file)` lets a card whose `applies_to` begins with a language name run only on files of that language, plus build and configuration files when the card lists `build-config`; a universal card dispatches as before.

## Sources

The evidence is the rule catalogs of the Python analyzers, each an openable text with a stable raw path: Ruff (`uvx ruff rule --all --output-format json`, ruff 0.17.1: 971 rules, 713 harvested after the formatting, docstyle, stub, naming and framework-specific linters are dropped), the Pylint message documentation (444), the SonarSource python rule descriptions (440), Bandit (81) and flake8-bugbear (62) — 1,740 items, cached by `harvest-python-sources.py` beside its index at authoring time. Official documentation (CPython `Doc/`, the PEPs, the typing spec, the mypy and pytest documentation, the Google Python style guide) answers by raw path and is quoted by section. Papers reach the cards relayed, by arXiv id, and never as a card's only anchor. Where the catalogs disagree (flake8-bugbear B006 against SonarSource S5717 on an unmodified mutable default; PEP 8 against SonarSource S5754 on a logging bare except), the card's Limits carry both positions and the condition the sources state.

The source policy of the universal note holds unchanged: `fetched` means opened from the authoring environment and quoted; `relayed` the search index's statement with the paper unopened; a trade book or a talk is never a source and never named on a card.

## Workflow

```
harvest (script, once)       --> 1,740 catalog items, texts cached; 16 relayed papers by topic
triage (brief-judge x 18)    --> 495 python-specific-new, 270 universal-instance, 142 duplicate-of,
                                 216 not-a-craft-rule, 144 out-of-scope, 113 formatting, 14 not-checkable
merge (script)               --> 391 candidates in 12 topics
spine (brief-judge, 1/topic) --> at most 10 rules with locators, quotes and an example seed; the rest folded, mapped or held
draft (brief-judge, packs 5) --> card + provenance line; the drafter runs the validator and check-python-cards.py before it returns
skeptic (Fable high, packs 5)--> accept | revise with exact edits | reject; Opus xhigh retried a null result (never needed)
closing edit (brief-worker)  --> the revise edits applied verbatim, re-checked
write (script) + commit      --> write-topic-result.py renumbers from the cards in the tree; one commit per topic
```

The check phase of the brief (§5.5) runs inside the drafter's own calls and again by the session after the run (`check-python-cards.py` over the closing and accepted drafts, the validator in `--language python` mode, the script tests, `worker-zone-check`); a workflow script cannot read files, so a separate check stage would have cost an agent per pack. Four topics ran in parallel from topic 4 on, on the operator's decision.

### Measured cost

Over the 12 topics written, from each run's `workflowProgress`, `run_report.py` on the pilot:

| Phase | Agents | Tokens | Wall-clock | Per agent |
|--|--|--|--|--|
| spine | 22 | 3.66 M | 318 min | 166 k, 14.5 min |
| draft | 42 | 7.00 M | 607 min | 167 k, 14.4 min |
| verify | 42 | 4.82 M | 330 min | 115 k, 7.9 min |
| close | 21 | 2.09 M | 106 min | 99 k, 5.0 min |
| topics in all | 127 | 17.56 M | 954 min of pipelined wall-clock | 1.46 M per topic |

Triage: 18 brief-judges, about 2.6 M tokens (the pilot batch 146 k / 507 s; the 14-batch run 2.01 M / 51 min). Harvest and the two helper developers: about 0.7 M. The close added three audits (SKILL.md and the agent 0.97 M; the cards 3.45 M; the backlog cards 3.42 M) and the attribution sweep (0.29 M). Series in all: about 29 M sub-agent tokens against the brief's 25–30 M for its 70–100 cards, the backlog pass the operator added at the close included, because the catalogs arrive as text a script harvests once and the drafter checks its own pack, so a topic spends six agents where the universal series spent eighty-five.

Yield: a drafter's card reached the skeptic validated, parsed and source-checked, and the skeptic's verdicts split 93 accept / 85 revise / 0 reject over 178 cards; every revise carried exact edits the closing worker applied and re-checked, and no card was rejected.

## Topics

| # | Topic | Domain | Candidates | Cards (ids) | accept / revise / reject | Held | Pending | Agents / tokens / wall-clock |
|--|--|--|--|--|--|--|--|--|
| 1 | python-data-model-and-idioms | code | 141 | 27 (PY-01..10, PY-143..159) | 15 / 12 / 0 | 114 (51 cap, 26 folded, 4 universal, 4 other) | 0 | 16 / 2.60 M / 117 min |
| 2 | python-exceptions-and-context-managers | errors | 38 | 15 (PY-11..20, PY-170..174) | 5 / 10 / 0 | 23 (8 cap, 9 folded, 2 universal, 1 other) | 1 | 10 / 1.36 M / 88 min |
| 3 | python-typing | code | 31 | 12 (PY-21..30, PY-160..161) | 4 / 8 / 0 | 19 (7 cap, 6 folded, 0 universal, 0 other) | 0 | 10 / 1.34 M / 76 min |
| 4 | python-classes-dataclasses-enums | design | 62 | 22 (PY-61..70, PY-131..142) | 11 / 11 / 0 | 41 (21 cap, 10 folded, 1 universal, 1 other) | 0 | 14 / 2.05 M / 105 min |
| 5 | python-functions-modules-imports | design | 36 | 18 (PY-41..50, PY-162..169) | 6 / 12 / 0 | 18 (11 cap, 1 folded, 1 universal, 2 other) | 2 | 12 / 1.72 M / 89 min |
| 6 | python-strings-bytes-paths-io | code | 59 | 19 (PY-31..40, PY-122..130) | 9 / 10 / 0 | 40 (21 cap, 5 folded, 2 universal, 1 other) | 0 | 12 / 1.74 M / 90 min |
| 7 | python-collections-and-iteration | performance | 103 | 16 (PY-51..60, PY-116..121) | 12 / 4 / 0 | 87 (34 cap, 27 folded, 0 universal, 1 other) | 1 | 12 / 1.50 M / 86 min |
| 8 | python-asyncio-and-threads-idioms | errors | 23 | 13 (PY-85..94, PY-176..178) | 9 / 4 / 0 | 10 (5 cap, 3 folded, 0 universal, 0 other) | 0 | 10 / 1.39 M / 82 min |
| 9 | python-pytest-and-unittest | tests | 35 | 11 (PY-75..84, PY-175) | 8 / 3 / 0 | 24 (5 cap, 10 folded, 4 universal, 1 other) | 1 | 10 / 1.17 M / 62 min |
| 10 | python-packaging-and-project-tooling | tooling | 10 | 11 (PY-71..74, PY-109..115) | 6 / 5 / 0 | 0 (0 cap, 0 folded, 0 universal, 0 other) | 0 | 9 / 1.19 M / 77 min |
| 11 | python-security-hygiene | input | 10 | 6 (PY-95..100) | 2 / 4 / 0 | 4 (0 cap, 2 folded, 2 universal, 0 other) | 0 | 6 / 0.79 M / 46 min |
| 12 | python-logging-and-diagnostics | errors | 12 | 8 (PY-101..108) | 6 / 2 / 0 | 4 (0 cap, 4 folded, 0 universal, 0 other) | 0 | 6 / 0.72 M / 36 min |

Corpus: 178 cards; by domain code 58, design 40, errors 36, performance 16, tooling 11, tests 11, input 6; by check kind mechanical 128, semantic 50; by default severity major 99, minor 70, suggestion 9. The candidates a spine held under its cap of 10 rules — 163 across the series — keep their evidence in each topic's research note under "Rules held back"; a later pass can card them without a new harvest.

## Progress

| Step | Gate | State |
|--|--|--|
| 0 the tree admits a language corpus | tests pass; validator `--language` mode; pre-pass dispatch | done |
| harvest | 1,740 items, 0 fetch failures, texts cached | done |
| triage | 18 batch verdict files, candidates.json, the overlap list in the summary | done |
| topic 1 pilot | 10 cards, three read by the session, two by the operator, cost measured | done |
| topics 2–12 | one commit per topic, validator and check clean, zone check clean | done |
| close | SKILL.md and agent audited, cards audited and the applied patches written, READMEs, 7.1.0, this note | done |

## Deviations from the brief

The brief is the operator's commission for this corpus, a handover message outside the repository; each entry quotes the instruction it deviates from and states the determining reason.

1. Triage batch size. The brief's §5.2 says batches of 40. The script merges the Ruff reimplementations with their Pylint, bugbear and Bandit originals and drops the Pylint error and fatal classes, so 1,394 items remain; batches of 80 cost 18 agents, where batches of 40 would cost 35, and the pilot batch's 80 verdicts, all read by the session, held the quality.
2. Skeptic pack size. §5.6 names packs of 6; the draft and the skeptic packs both take 5, so a skeptic pack starts as soon as its draft pack returns, with no barrier between the phases.
3. Check stage. §5.5 names a script stage between draft and skeptic; the drafter runs the same checks on its own pack before it returns and the session runs them again after the run, because a workflow script cannot read files.
4. Card id width. The brief writes `PY-NN` and a range of 70–100 cards; twelve topics at up to ten rules each reached 178, so a card id carries three digits from PY-100 on, and the validator, the Python check script and the taxonomy admit two or three digits. Cutting evidence-backed cards or a topic would have lost content the brief commissioned.
5. Per-topic cap. The spine's cap of 10 rules held 163 candidates that have evidence (most in data-model, collections, strings and classes); they sit in the research notes, not in the pending map, because the pending map is for rules lacking evidence. The cap stays: a card costs a finder agent on every diff its triggers match, the corpus already passes the brief's range, and the held candidates are the backlog a later pass cards once review runs show which gaps bite — no new harvest is needed for them.
6. Packaging topic. The brief's §6 gives the packaging topic the PyPA guide and PEPs 517, 518 and 621 as catalogs; the harvest reads analyzer catalogs, which lint code and not `pyproject.toml`, so four candidates reached the topic and four cards shipped (PY-71..74, version gates). A supplementary run of the topic workflow over six hand-listed candidates from the packaging PEPs (517, 518, 621, 508), the PyPA guide and specifications and the setuptools documentation followed at the close, with the texts fetched by url; its cards carry ids from PY-109 and its spine, verdicts and cost are the second part of the topic's research note.
7. Datetime rules. The Ruff DTZ rules name no topic in §6; the triage placed them under strings-bytes-paths-io, and PY-33 (an aware UTC `now`) shipped there. They stay there: a topic names only the research note and the provenance line, dispatch runs on the card's triggers, and the other datetime catalog rules are instances of TOOL-43 and TOOL-46 (a naive `now()` or constructor, a wall-clock date held as an instant), which the universal cards already dispatch onto Python files.
8. Commit timestamps. The repository's weekend-commit hook stamps every commit on a Saturday or Sunday after the last commit on `main`; the series' commits carry those dates.
9. Four topics in parallel. The brief runs two, three when the usage window allows; from topic 4 on four ran at once on the operator's instruction, with no 429 from the Fable skeptic and no Opus fallback used.
10. Audit patches. The audit of SKILL.md and the developer agent (gate mode, 14 cards each) returned 7 patches, every one in text the change did not touch; none was applied: every patch sits in text this corpus did not touch. The quick-rules block of SKILL.md is a summary layer by design, so a value it repeats from a phase section is the summary doing its job, and the four `needs_human` items (the script list, the render write zone against `review_output`, the two statements of the git check, the agent description's stop rule) belong to a pass over SKILL.md as a whole, outside this corpus.
13. Backlog pass. On the operator's decision the 70–100 range and the per-topic cap were lifted: a second run of the topic workflow took every candidate the first runs had held under the cap, with no numeric cap and a quality bar in the brief (a defect a review should report is carded; a redundancy an autofixer removes, a bare idiom preference or a rule whose bad half a reviewer cannot tell from the good half is held with the reason). The spine of a backlog run saw its own topic's first-run cards but not the other topics', so the session checked each pass for cross-topic restatements and dropped two before writing (a data-model rule restating PY-55, another restating PY-54 with PY-90); the later passes carried every corpus title in their brief. The backlog cards sit in each topic's research note under "Backlog pass", with the holds and their reasons. A second card audit at the close (`kb-corpus` over the 178 cards, `kb-card` on PY-121, PY-132, PY-143, PY-170 and PY-175; 112 agents, 3.4 M tokens) found nothing on the corpus and no C-E2 patch on the five cards, the drafter brief now carrying the attribution rule; its 8 patches are dismissed on the same taxonomy rows as before (C-F3 Example length, C-A4 `applies_to` vocabulary), plus C-F2 (the consumer block is `## Finding output`, which the taxonomy names) and C-B1 on PY-175 (a `usefixtures` mark on a fixture and an empty `usefixtures()` are one mechanism, a mark that cannot take effect, and the Validator asks one question).
11. Numbering across topics. `write-topic-result.py` numbers a topic's cards from the highest id in the tree, and it read two-digit ids only, so topic 12 was first written over PY-100; the script reads three digits, the topic was reverted and rewritten as PY-101..108, and a test holds the case.
12. Card audit. The close's audit (`kb-corpus` over the directory, `kb-card` on PY-01, PY-12, PY-57, PY-61 and PY-83; 112 agents, 3.4 M tokens, 133 s) found nothing on the corpus as a whole and 10 patches on the five cards. The four C-E2 patches (a tool, a PEP or "this card follows PEP 8" named as an attribution in Limits or Rationale) are applied, each side of a split now stated without its holder and the Source block carrying the locators. The five C-F3 patches (an Example beyond three lines) and the C-A4 patch (no everyday symptom terms in `applies_to`) are dismissed: the taxonomy documents the Example as a `bad:`/`good:` pair of at most ten lines, which the validator enforces, and `applies_to` is a controlled vocabulary the pre-pass dispatches on, with the title carrying the retrievable claim. A grep after the audit found 33 of the 108 cards naming a catalog, a PEP or a tool in body prose, so the rule is now stated in the taxonomy's "Inline citation" row and applied across the corpus: a name stays where it is the subject of a fact the card depends on — a configuration key the Validator reads (PY-101: a project that disables Ruff G004 or Pylint W1203 has chosen the f-string side), a version floor (PY-71: `target-version`, `py-version`), the documented behaviour of the library the card governs — and goes where it holds a position ("says", "recommends", "raises an issue when", "this card follows"), the positions standing without their holders and the Source block carrying them. Four brief-workers (Opus high, 0.29 M tokens, 4 min) swept the 32 cards: 66 sentences rewritten, 34 names kept, the validator clean, the Source blocks untouched. The universal corpus carries the same pattern in 240 of its 472 cards; that sweep is a separate pass over the universal corpus with its own skeptic round, named here as the follow-up.

### Overlaps with the universal corpus

Two lists, for the operator. First, the Python cards whose rule is the Python form of a universal rule — carded because the Python mechanism (the construct, the default, the library call) is what the card checks, with the universal card named here and not on the card:

- PY-11 `raise ... from` and the `__cause__`/`__context__` difference — ERR-11 (an error carries its cause).
- PY-46 a boolean parameter keyword-only after a bare `*` — CODE-34 (no boolean selecting a code path); PY-47 more than five positional parameters keyword-only — CODE-39.
- PY-61 a class-body mutable default shared by every instance — DSN-72 (a default never one shared mutable object); PY-01 (parameter default) and PY-54 (`dict.fromkeys`) are its sibling forms.
- PY-71 no feature newer than `requires-python` — the general form the typing cards PY-25..27 gate on a version.
- PY-33 an aware UTC `now` — TOOL-43 (a moment held as an aware instant).

Second, the 270 harvested items the triage mapped to a universal card as its Python instance, never carded, grouped by the universal id:

- `API-02` — pylint W0221 arguments-differ; pylint W0222 signature-differs
- `API-05` — ruff RUF018 assignment-in-assert
- `API-07` — ruff B011 assert-false; ruff PLW0129 assert-on-string-literal; ruff PT015 pytest-assert-always-false; sonar S9077 intentional-test-failures-should-use-pytest-fail-with-a-message
- `API-08` — ruff PLW0133 useless-exception-statement; sonar S2201 return-values-from-functions-without-side-effects-should-not-be-ignored; sonar S3984 exceptions-should-not-be-created-without-being-raised
- `API-14` — pylint W1114 arguments-out-of-order
- `API-17` — ruff LOG009 undocumented-warn
- `API-32` — pylint W4901 deprecated-module; pylint W4902 deprecated-method; pylint W4903 deprecated-argument; pylint W4904 deprecated-class; pylint W4905 deprecated-decorator; pylint W4906 deprecated-attribute; ruff G010 logging-warn; ruff UP005 deprecated-unittest-alias; ruff UP019 typing-text-str-alias; ruff UP021 replace-universal-newlines; ruff UP023 deprecated-c-element-tree; ruff UP026 deprecated-mock-import; ruff UP035 deprecated-import; ruff UP051 deprecated-abc-decorator; sonar S9076 deprecated-pytest-yield-fixture-should-be-replaced-with-pytest-fixture
- `CHG-08` — pylint W0238 unused-private-member; sonar S1144 unused-class-private-methods-should-be-removed; sonar S3985 unused-private-nested-classes-should-be-removed; sonar S4487 unread-private-attributes-should-be-removed; sonar S5603 unused-scope-limited-definitions-should-be-removed
- `CHG-09` — pylint W0613 unused-argument; ruff ARG001 unused-function-argument; sonar S1172 unused-function-parameters-should-be-removed
- `CHG-10` — pylint W0611 unused-import; ruff F401 unused-import; sonar S1128 unnecessary-imports-should-be-removed
- `CHG-11` — pylint W0101 unreachable; sonar S1763 all-code-should-be-reachable
- `CHG-32` — pylint W0407 preferred-module; ruff TID251 banned-api
- `CODE-10` — ruff E741 ambiguous-variable-name; sonar S1700 a-field-should-not-duplicate-the-name-of-its-containing-class; sonar S1845 methods-and-field-names-should-not-differ-only-by-capitalization
- `CODE-13` — ruff SIM116 if-else-block-instead-of-dict-lookup
- `CODE-23` — pylint W0621 redefined-outer-name; pylint W0622 redefined-builtin; sonar S5806 builtins-should-not-be-shadowed-by-local-variables
- `CODE-24` — pylint R0204 redefined-variable-type; ruff B020 loop-variable-overrides-iterator
- `CODE-25` — pylint W0612 unused-variable; pylint W0641 possibly-unused-variable; ruff B007 unused-loop-control-variable; ruff F841 unused-variable; ruff F842 unused-annotation; sonar S1481 unused-local-variables-should-be-removed; sonar S1854 unused-assignments-should-be-removed
- `CODE-26` — ruff FURB152 math-constant; ruff PLR2004 magic-value-comparison
- `CODE-31` — ruff PLW0177 nan-comparison; ruff RUF069 float-equality-comparison; sonar S1244 floating-point-numbers-should-not-be-tested-for-equality
- `CODE-36` — ruff PLR0915 too-many-statements; sonar FunctionComplexity cyclomatic-complexity-of-functions-should-not-be-too-high; sonar S138 functions-should-not-have-too-many-lines-of-code
- `CODE-38` — ruff PLW0642 self-or-cls-assignment; sonar S1226 function-parameters-initial-values-should-not-be-ignored
- `CODE-39` — ruff PLR0913 too-many-arguments; sonar S107 functions-methods-and-lambdas-should-not-have-too-many-parameters
- `CODE-46` — ruff ANN401 any-type; sonar S6542 any-should-not-be-used-as-a-type-hint
- `CODE-48` — sonar S6543 type-hints-of-generic-types-should-specify-their-type-parameters
- `CODE-50` — sonar S2757 non-existent-operators-like-should-not-be-used
- `CODE-53` — ruff RUF021 parenthesize-chained-operators
- `CODE-58` — ruff E701 multiple-statements-on-one-line-colon; ruff E702 multiple-statements-on-one-line-semicolon
- `CODE-62` — pylint W0511 fixme; sonar S1134 track-uses-of-fixme-tags; sonar S1707 track-todo-and-fixme-comments-that-do-not-contain-a-reference-to-a-person
- `CODE-64` — sonar S108 nested-blocks-of-code-should-not-be-left-empty; sonar S1186 functions-and-methods-should-not-be-empty
- `CODE-66` — sonar S1720 docstrings-should-be-defined
- `CODE-67` — pylint W9006 missing-raises-doc
- `CODE-72` — ruff ERA001 commented-out-code; sonar S125 sections-of-code-should-not-be-commented-out
- `CODE-76` — sonar S1751 loops-with-at-most-one-iteration-should-be-refactored
- `CODE-79` — pylint R1705 no-else-return; pylint R1720 no-else-raise; pylint R1723 no-else-break; pylint R1724 no-else-continue; ruff RET505 superfluous-else-return; ruff RET506 superfluous-else-raise; ruff RET507 superfluous-else-continue; ruff RET508 superfluous-else-break
- `CODE-80` — pylint R1710 inconsistent-return-statements; ruff RET502 implicit-return-value; ruff RET503 implicit-return; sonar S3801 functions-should-use-return-consistently
- `CODE-81` — sonar S2190 recursion-should-not-be-infinite
- `CODE-82` — pylint R1703 simplifiable-if-statement; pylint R1719 simplifiable-if-expression; pylint R1726 simplifiable-condition; ruff E712 true-false-comparison; ruff SIM103 needless-bool; ruff SIM210 if-expr-with-true-false
- `CODE-84` — ruff RUF032 decimal-from-float-literal
- `CODE-85` — ruff PLR0916 too-many-boolean-expressions
- `CODE-86` — pylint R1260 too-complex; ruff PLR1702 too-many-nested-blocks; ruff SIM102 collapsible-if; sonar S1066 mergeable-if-statements-should-be-combined; sonar S134 control-flow-statements-if-for-while-try-and-with-should-not-be-nested-too-deeply
- `DOC-01` — ruff B005 strip-with-multi-characters; ruff PLE1310 bad-str-strip-call
- `DOC-04` — pylint W9008 redundant-returns-doc; pylint W9010 redundant-yields-doc; pylint W9017 differing-param-doc; pylint W9018 differing-type-doc
- `DSN-10` — pylint R0401 cyclic-import; ruff PLW0406 import-self
- `DSN-14` — pylint R0903 too-few-public-methods
- `DSN-16` — pylint W0246 useless-parent-delegation
- `DSN-21` — pylint R0801 duplicate-code; sonar S4144 functions-and-methods-should-not-have-identical-implementations
- `DSN-22` — sonar S1192 string-literals-should-not-be-duplicated
- `DSN-27` — ruff RUF034 useless-if-else; ruff SIM114 if-with-same-arms; sonar S1871 two-branches-in-a-conditional-structure-should-not-have-exactly-the-same-implementation; sonar S3923 all-branches-in-a-conditional-structure-should-not-have-exactly-the-same-implementation
- `DSN-33` — pylint W0212 protected-access; ruff PLC2701 import-private-name; ruff SLF001 private-member-access
- `DSN-57` — pylint W4801 looping-through-iterator; ruff B031 reuse-of-groupby-generator
- `DSN-60` — bugbear B038 ; pylint W4701 modified-iterating-list; ruff B909 loop-iterator-mutation; ruff PLE4703 modified-iterating-set
- `DSN-61` — ruff PLW0108 unnecessary-lambda
- `ERR-02` — ruff S110 try-except-pass
- `ERR-08` — pylint W0718 broad-exception-caught
- `ERR-09` — pylint W0719 broad-exception-raised; ruff B016 raise-literal; ruff TRY002 raise-vanilla-class; sonar S112 exception-and-baseexception-should-not-be-raised
- `ERR-14` — ruff S101 assert
- `ERR-15` — sonar S5727 comparison-to-none-should-not-be-constant
- `ERR-32` — pylint W3101 missing-timeout; ruff S113 request-without-timeout; sonar S7618 network-calls-in-aws-lambda-functions-shouldn-t-be-made-without-explicit-timeout-parameters
- `ERR-45` — ruff S112 try-except-continue
- `ERR-46` — ruff TRY401 verbose-log-message
- `ERR-47` — ruff PLE1205 logging-too-many-args; ruff PLE1206 logging-too-few-args
- `ERR-52` — pylint W0706 try-except-raise; ruff TRY203 useless-try-except; sonar S2737 except-clauses-should-do-more-than-raise-the-same-issue
- `ERR-53` — pylint W0134 return-in-finally; pylint W0136 continue-in-finally; pylint W0137 break-in-finally; pylint W0150 lost-exception; ruff B012 jump-statement-in-finally; ruff PLE0116 continue-in-finally; ruff SIM107 return-in-try-except-finally; sonar S1143 break-continue-and-return-statements-should-not-occur-in-finally-blocks
- `INP-02` — ruff S608 hardcoded-sql-expression; sonar S2077 sql-queries-should-not-be-dynamically-formatted
- `INP-03` — ruff S308 suspicious-mark-safe-usage; ruff S701 jinja2-autoescape-false; ruff S702 mako-templates; ruff S704 unsafe-markup-use; sonar S5247 auto-escaping-in-html-template-engines-should-not-be-disabled
- `INP-04` — ruff S404 suspicious-subprocess-import; ruff S601 paramiko-call; ruff S603 subprocess-without-shell-equals-true; ruff S609 unix-command-wildcard-injection
- `INP-05` — ruff S102 exec-builtin; ruff S307 suspicious-eval-usage; ruff S612 logging-config-insecure-listen
- `INP-06` — ruff S301 suspicious-pickle-usage; ruff S403 suspicious-pickle-import
- `INP-07` — ruff S104 hardcoded-bind-all-interfaces; sonar S8392 web-servers-should-not-bind-to-all-network-interfaces
- `INP-08` — ruff S103 bad-file-permissions; sonar S2612 file-permissions-should-not-be-set-to-world-accessible-values
- `INP-09` — ruff S323 suspicious-unverified-context-usage; ruff S501 request-with-no-cert-validation; ruff S507 ssh-no-host-key-verification; sonar S4830 server-certificates-should-be-verified-during-ssl-tls-connections; sonar S5527 server-hostnames-should-be-verified-during-ssl-tls-connections
- `INP-10` — ruff S105 hardcoded-password-string; sonar S2068 credentials-should-not-be-hard-coded; sonar S6418 secrets-should-not-be-hard-coded; sonar S7625 long-term-aws-access-keys-should-not-be-used-directly-in-code
- `INP-11` — ruff S304 suspicious-insecure-cipher-usage; ruff S305 suspicious-insecure-cipher-mode-usage; ruff S413 suspicious-pycrypto-import; sonar S2257 custom-cryptographic-algorithms-should-not-be-used
- `INP-12` — ruff S311 suspicious-non-cryptographic-random-usage; sonar S2245 pseudorandom-number-generators-prngs-should-not-be-used-in-security-contexts
- `INP-15` — ruff RUF055 unnecessary-regular-expression; sonar S5361 str-replace-should-be-preferred-to-re-sub
- `INP-16` — sonar S5843 regular-expressions-should-not-be-too-complicated
- `INP-17` — sonar S5850 alternatives-in-regular-expressions-should-be-grouped-when-used-with-anchors
- `INP-18` — sonar S5842 repeated-patterns-in-regular-expressions-should-not-match-the-empty-string; sonar S5855 regex-alternatives-should-not-be-redundant; sonar S5856 regular-expressions-should-be-syntactically-valid; sonar S5868 unicode-grapheme-clusters-should-be-avoided-inside-regex-character-classes; sonar S5869 character-classes-in-regular-expressions-should-not-contain-the-same-character-twice; sonar S5994 regex-patterns-following-a-possessive-quantifier-should-not-always-fail; sonar S5996 regex-boundaries-should-not-be-used-in-a-way-that-can-never-be-matched; sonar S6001 back-references-in-regular-expressions-should-only-refer-to-capturing-groups-that-are-matched-before-the-reference; sonar S6537 octal-escape-sequences-should-not-be-used-in-regular-expressions
- `INP-19` — sonar S5852 regular-expressions-should-not-cause-catastrophic-backtracking; sonar S5857 character-classes-should-be-preferred-over-reluctant-quantifiers-in-regular-expressions; sonar S8786 regular-expressions-should-not-cause-non-linear-backtracking
- `INP-25` — bandit B320 xml_bad_etree; ruff S313 suspicious-xmlc-element-tree-usage; ruff S405 suspicious-xml-etree-import; sonar S2755 xml-parsers-should-not-be-vulnerable-to-xxe-attacks
- `PRF-04` — pylint W1515 forgotten-debug-statement
- `PRF-17` — pylint R1713 consider-using-join
- `PRF-24` — ruff FURB192 sorted-min-max; sonar S8517 sorted-should-not-be-used-with-indexing-to-find-minimum-or-maximum-values
- `TOOL-18` — pylint file-ignored file-ignored; ruff PGH003 blanket-type-ignore; ruff PGH004 blanket-noqa; sonar NoSonar track-uses-of-nosonar-comments
- `TOOL-19` — ruff RUF104 unmatched-suppression-comment
- `TOOL-20` — pylint useless-option-value useless-option-value; pylint useless-suppression useless-suppression; ruff RUF100 unused-noqa
- `TOOL-22` — sonar S1313 ip-addresses-should-not-be-hardcoded; sonar S6262 aws-region-should-not-be-set-with-a-hardcoded-string
- `TOOL-26` — ruff S201 flask-debug-true; sonar S4507 debugging-features-should-not-be-enabled-in-production
- `TOOL-33` — ruff PLW1514 unspecified-encoding
- `TOOL-40` — ruff INT001 f-string-in-get-text-func-call
- `TOOL-47` — bandit B613 trojansource; ruff PLE2502 bidirectional-unicode; ruff PLE2510 invalid-character-backspace; ruff PLE2512 invalid-character-sub; ruff PLE2513 invalid-character-esc; ruff PLE2514 invalid-character-nul; ruff PLE2515 invalid-character-zero-width-space; ruff RUF001 ambiguous-unicode-character-string
- `TST-11` — sonar S9137 mocks-should-be-created-with-autospec
- `TST-18` — ruff PT016 pytest-fail-without-message; ruff PT018 pytest-composite-assertion
- `TST-19` — sonar S5976 similar-tests-should-be-grouped-in-a-single-parameterized-test
- `TST-23` — bugbear B908 ; ruff B017 assert-raises-exception; ruff PT011 pytest-raises-too-broad; ruff PT012 pytest-raises-with-multiple-statements; sonar S5778 only-one-method-invocation-is-expected-when-testing-runtime-exceptions; sonar S5958 tests-should-check-which-exception-is-thrown
- `TST-24` — pylint W1503 redundant-unittest-assert; sonar S5845 assertions-comparing-incompatible-types-should-not-be-made; sonar S5863 assertions-should-not-be-given-twice-the-same-argument; sonar S5914 assertions-should-not-fail-or-succeed-unconditionally
- `TST-25` — ruff PT017 pytest-assert-in-except; sonar S5779 assertions-should-not-be-made-within-the-try-block-of-a-try-except-catching-assertionerror; sonar S5915 assertions-should-not-be-made-at-the-end-of-blocks-expecting-an-exception; sonar S5918 tests-should-be-skipped-explicitly
- `TST-26` — sonar S2187 testcases-should-contain-tests; sonar S5899 test-methods-should-be-discoverable
- `TST-38` — sonar S1607 a-reason-should-be-provided-when-skipping-a-test; sonar S9001 expected-test-failures-should-provide-a-reason
- `TST-39` — sonar S3415 assertion-argument-order-should-be-consistent-within-a-file
