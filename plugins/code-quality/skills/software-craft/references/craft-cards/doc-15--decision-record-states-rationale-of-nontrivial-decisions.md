---
title: A design document or decision record added in a change explains the rationale for each nontrivial decision it records
rule_id: DOC-15
domain: docs
step: [design, document, review]
applies_to: [prose]
triggers: ['signal:added_file', '(?i)^\s*#{2,3}\s+(status|context|decision|consequences|considered options|decision outcome|decision drivers|alternatives( considered)?|rationale)\s*$', '(?i)^\s*#\s+(ADR|RFC|design( doc(ument)?)?)\b']
scope: file
check_kind: semantic
severity_default: suggestion
---

# A design document or decision record added in a change explains the rationale for each nontrivial decision it records

## Thesis
A design document or decision record added in a change gives, for each nontrivial decision it records, an explanation of its rationale; a record that states only what will be implemented, with no explanation of why, falls short of the rule.

## Rationale
The output of design is a set of models and artifacts that record the major decisions taken along with an explanation of the rationale for each nontrivial decision, and recording the rationale enhances the long-term maintainability of the software. Decision records mined from about 550 open-source repositories frequently capture existence, technology and process-related decisions, while alternatives, decision drivers and some quality concerns remain under-documented.

## Example
```python
bad:  RECORD = """
      # ADR 7: Keep cache entries in an embedded database
      ## Decision
      Each host writes its cache entries to one local database file."""
good: RECORD = """
      # ADR 7: Keep cache entries in an embedded database
      ## Decision
      Each host writes its cache entries to one local database file.
      ## Rationale
      Entries must survive restarts, and hosts run no database server."""
```

## Limits
A trivial decision needs no stated rationale: the explanation is owed for each nontrivial decision. The rule asks for the explanation, not a template: the design output it rests on is a set of models and artifacts, with no form prescribed. A record that links to the document holding a decision's reason meets the rule: the rationale belongs to the design output as a whole, a set of models and artifacts. In a comparison of five decision-record templates for comprehension, usability and ease of adoption, two topped an expert screening, and in a controlled experiment with undergraduate students the template that supports concise and objective documentation outperformed, on the overall score, the one that facilitates structural details and specific architectural requirements. That comparison and the mining study are unreviewed preprints. The rule reaches the design documents and decision records a change adds; a decision that appears only in a code comment or in the change description, with no added record stating it, lies outside it.

## Validator
Open each file the change adds that a trigger marks as a design document or decision record: a title beginning ADR, RFC or Design, or headings such as Status, Context, Decision, Consequences, Considered Options, Decision Outcome, Decision Drivers or Alternatives. List the decisions the record states, that is the chosen option under a Decision or Decision Outcome heading and each sentence that commits to a design. Set aside the trivial ones, a choice with no workable alternative and no lasting constraint on later work. For each remaining decision, read the whole record for an explanation of why it was taken: a stated reason, a driver or force, a trade-off, an alternative rejected with its weakness, a context section naming the problem the decision answers, or a link to a named document or section that holds the reason. Validator question: **Does the added record state a nontrivial decision with no explanation of its rationale anywhere in the record?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: DOC-15`, severity suggestion, `file`, `symbol`, `code` = the decision sentence or Decision section quoted verbatim from the added record, `fix` = the same record with a rationale section after that decision, in the record's markup, holding the reason where the change itself states one and otherwise a marked placeholder that asks the author for it, `rationale` = the decision that carries no reason and the long-term maintainability that an unrecorded rationale costs).

## Source
- SWEBOK V3.0, IEEE Computer Society, 2014, ch. 2 'Software Design', §1.3 'Software Design Process', community transcription (fetched): "The output of these two processes is a set of models and artifacts that record the major decisions that have been taken, along with an explanation of the rationale for each nontrivial decision. By recording the rationale, long-term maintainability of the software product is enhanced."
- arXiv:2604.27333, abstract, unreviewed preprint (fetched): "which ADR template best supports comprehension, usability, and ease of adoption [...] a controlled experiment conducted with undergraduate students. Results: In the preliminary screening by experts, the top-performing templates were those of [two of the five] [...] [the first] template outperformed [the second] in terms of the Overall Score. [...] [the first] supports concise and objective documentation, while [the second] facilitates structural details and specific architectural requirements."
- arXiv:2609.07375, abstract, unreviewed preprint (fetched): "a dataset of ADRs extracted from ~550 open-source repositories [...] ADRs frequently capture existence, technology, and process-related decisions, while alternatives, decisions drivers, and some quality concerns remain under-documented."
- Caveat: the normative anchor is the body-of-knowledge text, whose V4.0 wording was not verified; both papers are preprints read through their abstracts, and the template experiment's participants were undergraduate students.
