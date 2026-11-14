# Rules of the reading contract

A question reaches the addressee only after it has passed the filters of rules 3–9, and every delivered item is written to the addressee's two parameters: what he can open himself and the format in which he receives the text. The addressee is whoever reads and decides: a client, a neighbouring team, a product owner, or the operator of this session. Our documents are everything we already hold: the contract, the specification, the decisions taken, reports, measurements, source files, the session transcript, the decision registry. The rules shape the delivered text; the reasoning that produces it runs first, unconstrained by them. The check scripts name rules by number, so a rule held back keeps its number as a gap. A rule states the limit of its evidence in its own words where that limit narrows its use.

| Parameter | `client` | `operator` |
|--|--|--|
| Opens himself | nothing of ours | the repository's files, commands, the transcript, the decision cards |
| Anchor for a claim about code | none (rule 14) | required under "Where to look" (14), matched by the script |
| Identifiers of runs, registries, agents | barred (14) | barred in prose; a commit hash is allowed as what an approval is bound to |
| Dates, deadlines, effort | barred (15, 16) | barred in the report's prose; time goes to accounting, not into the text |
| Delivery format | a file in the addressee's format, generated from the source (24) | a story with its pictures and the list "Where to look", as text in the chat and, by default for a mechanism or a choice among options, as a page with voice (24); decision cards |
| Internal block | not delivered (9) | not delivered (9): a default decision he may overturn is a sentence of the story, the rest stays in the registry (25) |

## Where candidates come from

1. A candidate for the list is any place where the work runs into someone else's decision or data: an open question from a report, a discrepancy between documents, a missing input. Our own decision is not a candidate. For the operator, "someone else's decision" is his decision and "someone else's data" is what he alone knows; the agent's decision does not enter the list: the agent takes it and writes it to the registry (rule 6).
2. Each candidate is written first as the pair "the fact we know" and "what the answer changes", and only then as a question.

## Checks in order, until the candidate drops out

3. Is the answer already known? We search our documents, the data, the project's ledger of earlier answers (`scripts/records.py ledger find`), and what we can check ourselves in reasonable time: open the file, count, run it. Found or checked, the question closes with the registry line "closed, basis"; the check closes only the questions it answers, and a question about what the addressee alone holds is still asked, since coding agents left without such a prompt almost never ask at all.
4. Does the answer change our work? For each possible answer we name what we would do differently: the scope, the design, the verification protocol, the schedule. If no answer changes anything, the question is dropped, however interesting it is.
5. Is the gap in our own knowledge? If the answer is recoverable from our own material by research we can do ourselves, the research comes first and the question about the decision after it; research in place of a question costs exploration.
6. Can it be decided by default? The decision is reversible, we have a basis, and an error is cheap: we decide ourselves, tell the addressee as a fact and write a registry line (rule 25). Only the irreversible, the costly and what the addressee alone knows is asked. A question that reaches the addressee says why it was not decided by default; the plugin's hook on `AskUserQuestion` (`hooks/hooks.json`, running `scripts/check_question.py --hook`) rejects a question without it.
7. Is it their decision or ours? A question is asked when its answer changes our work; one that changes only their purchase, process or organisation is dropped, except the one decision we need as an input (which option they choose). For the operator: a question that changes only how the agent works (which tool, in which order) is not asked.
8. Is it already asked elsewhere? One topic lives in one item; duplicates merge, and an overlap becomes a cross-reference.
9. Is it internal? Inconsistencies of our own documents, our licences, fallbacks, estimates for our own team go to a separate internal block that is not delivered to the addressee.
10. The filters are independent tests: an item that passes one may fall on another.

## How an item is written

11. One claim per sentence, without nested clauses. The fact with its decisive number first, then the request or the question. As many sentences as carry the conclusion whole, and not one more.
12. A fact the addressee does not know is explained in one sentence before it is relied on. A code, an abbreviation or an internal term is spelled out at its first mention in the addressee's words.
13. The addressee's words: a term that grates on him is replaced by his familiar, short word.
14. The item names the fact itself in the addressee's words; references to document sections, identifiers of our runs, registries and files, "as in the contract", procedural promises and the account of how we measured it stay in our source. For the operator the same rule turns over: he opens the file himself, so a claim about code has a `path:line` anchor and the fragment of that line under "Where to look", while the story names the thing by its role, and identifiers of runs, workflows and agents leave the prose.
15. A dependency is named in words — "we send it once the rules are agreed" — and dates and deadlines stay in our source.
16. A request reads "we will send it, and it will need checking" or "please send us this"; requests to assign people or hours and our effort estimates stay in our source.
17. One number per claim; the other figures stay in the full report (rule 24). The decisive number is the one the question turns on, because leaving figures out moves the decision as well as the comprehension.
18. Options we offer are keyed by the addressee's condition ("if the result is needed by morning", "if such a ban applies"), without prices and without what only we know. The operator's decision card opens with one or two sentences in plain words that say what the matter is, with one concrete instance of it, before any identifier. On that card the consequence and the cost of error stand inside every option's description, and the recommendation stands as its own line with its basis, because where advice sits and what confidence it carries change how far it pulls the choice. For an irreversible decision the answer comes as typed input, and the agent repeats the chosen consequence before acting; the read-back catches an error only when the operator compares the repeated consequence with what he meant.
19. An item has one question, and it stands at its end. An item without a question is a message: it gains a question, leaves the list, or goes to the decision registry.
20. Options left over from a cancelled scheme leave with it: the `D-01` card of `auditing-ai-context`.
21. The procedure we propose is the simplest one compatible with the contract; a procedure with roles and arbiters is an example of what to simplify.

## Order and form

22. Order by dependency: an explanation before its use, with process steps and attributes in their order as instances of it; cross-references between items stand in brackets. In a report to the operator the opening names the problem he has to act on, and the parts after it follow the order in which he needs the ideas: how the thing works, what went wrong, what is his to decide, then the list of where to look (`references/explaining.md` § The story has the rules of each part).
23. A date line and a signature stay out, since provenance belongs to git: the `D-01` card of `auditing-ai-context`; a framing introduction stays out: its `R-25` card.
24. The addressee receives a file in his usual format, generated from the source; the source stays with us together with the internal block. For the operator the report is a story with its pictures, closed by the list "Where to look", where the checks that ran stand with their exit codes taken from their output, not from prose (`references/report-template.md`); it goes out as text in the chat, and as a page with voice where `references/media.md` says.

## Record

25. Every closure and every default decision is a registry line: the decision, its basis, what overturns it. The registry is the project's ledger (`scripts/records.py ledger`), beside the store of the decision cards where the project has one, and is never delivered. A line carries its date and what it applies to, and a line that a later one replaces is marked superseded. The line stays short, since a full rationale per decision does not pay.

## What the research adds

- A claim travels with its evidence and a counter-argument. Judges were more accurate with two debating models than with a single consultant arguing one side (88 % of human and 76 % of LLM judges against 78 % and 54 %, on reading-comprehension questions about fiction passages), and a convincing wrong explanation alone lowered fact-checkers' accuracy to 0.35, against 0.54 with the retrieved evidence. A counter-argument does not replace the evidence: a contrastive explanation (0.56) did not beat the retrieved evidence.
- Questions are batched at the boundary of a task. The boundary is measured: in a field study of deferrable alert notifications, a switch cost about ten minutes and another ten to fifteen passed before the return to the disrupted task; in one laboratory study the same peripheral task cost 3 to 27 % more time and twice the errors inside a primary task than at its boundary; in another an interruption between two subtasks drew less annoyance and more perceived respect than one inside a subtask, at unchanged task time. Asking several questions together was tested in none of the three: it follows from the cost of each switch. Questions that block the work were not measured.
- A self-report of the agent is not evidence; `references/evidence.md` lists what is. An exit code counts only from a process outside the agent's write zone.
- The prose of a report carries what the diff and the tests cannot show: the motive, the decisions, what is unverified. Pull requests are 12–20 % more likely to be merged when their description explains the code changes, so an explanation of the change belongs in the report.
- A class of caveats is switched off when the addressee's "not useful" marks on it, counted against his "fix" marks, exceed 10 %. The threshold is a team policy from practice rather than a tested value, and a blocking channel warrants a lower bar.

Sentence-level style — word choice, sentence length, voice — belongs to the rule cards of `auditing-ai-context`.
