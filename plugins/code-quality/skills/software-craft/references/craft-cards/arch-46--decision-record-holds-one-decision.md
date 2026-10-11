---
title: A decision record holds one decision, so a change that records two decisions that could each be accepted, rejected or superseded without the other puts them in separate records
rule_id: ARCH-46
domain: architecture
step: [design, document]
applies_to: [prose]
triggers: ['signal:added_file', '(?i)^\s*#{2,3}\s+(status|context( and problem statement)?|decision( outcome)?|considered options|consequences)\s*$', '(?i)^\s*#\s+(ADR[-\s]?\d*|\d{1,4}[.:]?)\s*\S']
scope: file
check_kind: semantic
severity_default: suggestion
---

# A decision record holds one decision, so a change that records two decisions that could each be accepted, rejected or superseded without the other puts them in separate records

## Thesis
Each decision record that a change adds details a single architectural decision and its rationale: one problem whose scope the record makes explicit, the options considered for it, and one chosen option with its justification. Two choices that each answer a problem of their own and could each be accepted, rejected or later superseded without the other go in two records, which may link to each other; adopting a message broker and choosing the serialization format of its messages are one such pair. When and how the one decision is realized stays in its record.

## Rationale
An architectural decision is a justified design choice that addresses a functional or non-functional requirement of architectural significance, and its record carries at most one status, such as proposed, rejected, accepted, deprecated, or superseded by a named later record. Two decisions that share a record share that status, so the log cannot mark one of them superseded while the other stays accepted: reversing either choice retires the record of both, or leaves the reversed choice marked as current. With one decision per record, each record gives the reasons for its chosen decision along with its trade-offs and consequences, and the statuses across the project's decision log tell which decisions are accepted and which are superseded.

## Example
```python
bad:  ADR_7 = """
      # 7. Adopt a message broker and a binary schema format
      ## Decision Outcome
      Chosen options: a broker, because ...; a binary format, because ..."""
good: ADR_7 = """# 7. Adopt a message broker for service events
      ## Decision Outcome
      Chosen option: a broker, because ... Message format: ADR 8."""
      ADR_8 = """# 8. Serialize broker messages in a binary schema format
      ## Decision Outcome
      Chosen option: a binary format, because ... Builds on ADR 7."""
```

## Limits
A record that lists several considered options, its decision drivers, the pros and cons of each option, the consequences and the confirmation of its one chosen option holds one decision; the options it does not choose are part of that decision's rationale. The definition of when and how the decision is realized, and links to other decisions, belong in its record. The rule reaches the records a change adds to a project's decision log, the collection of records the project creates and maintains, including a log that extends the record format beyond architecture to design and other decisions; a project that keeps no decision log has no record to split.

## Validator
Grep the hunk for an added decision record: a heading of the form `# ADR-N` or `# N. Title`, or the record's section headings (status, context and problem statement, considered options, decision outcome, consequences). Open the record whole. List every chosen option its title and decision outcome state, and for each name the problem it answers, the options weighed for it and its justification. Trace each further choice: it is a decision of its own when it answers a problem of its own, carries its own options or justification, and could be accepted, rejected or superseded while the first choice stands; it belongs to the first decision when it only states when and how that choice is realized. Validator question: **Does an added decision record state two or more chosen options that each answer a problem of their own and could each be accepted, rejected or superseded without the other?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: ARCH-46`, severity suggestion, `file`, `symbol`, `code` = the record's title line and the decision-outcome sentence that names the second chosen option, `fix` = the record split in two, each with its own title, problem statement, decision outcome and status and a link from one to the other, in the file's own format, `rationale` = the single status a record carries, which two separable decisions would have to share).

## Source
- MADR documentation, `adr/madr` docs/index.md, introduction (fetched): "An Architectural Decision (AD) is a justified software design choice that addresses a functional or non-functional requirement of architectural significance. This decision is documented in an Architectural Decision Record (ADR), which details a single AD and its underlying rationale."
- MADR template, `adr/madr` template/adr-template.md (fetched): "These are optional metadata elements. Feel free to remove any of them."; `status: "{proposed | rejected | accepted | deprecated | … | superseded by ADR-0123}"`; "Make the scope of the decision explicit"; sections "Decision Drivers", "Considered Options", "Pros and Cons of the Options", "Consequences", "Confirmation"; "Chosen option: "{title of option 1}", because {justification. …}"; More Information: "define when/how this decision the decision should be realized … Links to other decisions and resources might appear here as well."
- ADR organisation, `adr/adr.github.io` index.md, § Motivation and Definitions (fetched): "An *Architectural Decision Record (ADR)* captures a single AD and its rationale"; "ADR can help you understand the reasons for a chosen architectural decision, along with its trade-offs and consequences. The collection of ADRs created and maintained in a project constitute its *decision log*."; "ADR usage can be extended to design and other decisions".
- Caveat: the sources fix one decision per record; the separability test (each choice could take its own status) is the card's reading of the single, optional status field the template gives a record.
