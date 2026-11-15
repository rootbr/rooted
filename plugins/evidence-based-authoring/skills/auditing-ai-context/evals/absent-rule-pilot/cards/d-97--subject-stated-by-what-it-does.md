---
title: A subject is stated by what it is and does; what it is not is named only as the subject of a present-tense fact
rule_id: D-97
applies_to_target: [doc, code, context-file, skill, agent-prompt]
check_kind: semantic
severity_default: medium
---

# A subject is stated by what it is and does; what it is not is named only as the subject of a present-tense fact

## Thesis
A sentence that describes a design, a rule or a concept says what its subject is and does. A thing the subject is not — an alternative the design does not use, a requirement it does without, a reading it rejects — may be named where that thing is the subject of a present-tense fact a reader can check today: "the built-in slider tracking is inert inside an open menu". It may not be named as the foil the subject is defined against: "manual tracking, not the built-in action", "the cache is neither a write-through buffer nor a replacement for the index", "a job of our own needs no ticket".

## Rationale
A blocking fact is true independently of the decision. A maintainer reaching for the obvious approach is stopped by it, and a reader who never saw the decision being taken can still check it against the environment today. A foil is true only relative to a choice or a dispute: it parses only for someone who was in the discussion. The reader of the file was never told that anyone holds the denied view or uses the denied option, so the sentence argues with a party absent from the page, tells the reader that a comparison happened without telling them what governs it, and says nothing about the subject. Rewriting the foil as what the subject does, or as the fact that blocks the alternative, keeps what the reader needs and drops what only narrates the path taken.

## Example
```
bad:  # We track the drag manually instead of using the built-in slider action.
good: # Built-in slider tracking is inert inside an open menu — track the drag manually.

bad:  The cache is neither a write-through buffer nor a replacement for the index.
good: The cache holds the last result of each query for `ttl` seconds.
```

## Limits
Covers how a thing the subject is not gets named, not whether it may be mentioned: the same thing passes as the subject of a checkable fact and fails as a foil, so this is a rewrite test rather than a deletion test. A comparison between two live options the reader must themselves choose between is a present decision, not a foil. A denial is kept where the file itself, outside the sentence, presents the denied thing to its reader as an option, a rule in force or a view someone holds: the denial then corrects something the reader has been shown. A prohibition or a constraint that the reader must obey or can check — "the hook never blocks a write", "a card carries no source block" — states a present fact about the subject and is kept, as is a negative trigger in a frontmatter `description`. A sentence that reports what a source found, the comparison the source made included, is a fact about that source. Where no fact blocks the denied thing and the file never presents it, the sentence is rewritten as what the subject does, or goes.

## Validator
Find each sentence that says what its subject is not, lacks or does without, or that sets it against something else — search for "not", "no", "never", "neither … nor", "instead", "in place of", "rather than", "unlike", "only", "we switched", "we chose", "X, not Y", and comparatives standing beside a named alternative. On a `doc`, `context-file`, `skill` or `agent-prompt` target scan the whole file. On a `code` target scan only the comment and doc-comment spans the static pre-pass extracts for that file's language; the surrounding source is not Markdown and is not prose. Where the inventory lists `contrast_candidates` for the target, a script has already found those sentences: judge every one of them, each on its own, before scanning for others, so that none is passed over unread. For each hit name the denied or contrasted thing, then ask two binary questions in order. (1) **Is that thing the grammatical subject of a fact about the environment that a reader could check today without knowing a decision or a discussion ever took place?** Yes → keep. (2) **Does the file itself, outside this sentence, present that thing to its reader as an option, a rule in force or a view someone holds — can you quote the sentence that does?** A quote → keep. No quote → flag. Where the inventory lists statements that the change under audit deleted, a thing those statements asserted counts as never presented: the reader of the file cannot see what was deleted.

## Patch output
When a sentence defines its subject against a thing the file never presents, emit one patch (`rule_id: D-97`, `location.section` + `line_hint`, `current` = the sentence, `proposed: null`, severity medium, `needs_human: true`) whose justification names the denied thing and says that no sentence of the file presents it, and proposes the statement of what the subject does, the fact that blocks the alternative, or the sentence's removal. Which fact blocks it is domain knowledge a reader holding only this file does not have.
