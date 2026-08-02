# Rooted

Claude Code plugin marketplace — rooted in evidence.

## Orientation

Read `README.md`, then run `./overview.sh` to orient.
Read individual files only if the output is not sufficient for the user's request.

## Evidence-Based Rule

Before adding any rule, checklist item, or review criterion — verify it traces to one of:

| Source | Examples |
|---|---|
| Academic research | arxiv.org, peer-reviewed papers, Google Scholar, PubMed |
| Technical standards | RFCs, official specifications, language/framework docs |
| Verified hands-on experience | Author's real-world usage, confirmed through practice |

No traceable source → do not add.

Cite the form anyone can open — an arXiv ID or DOI, an RFC number or spec URL, a linked commit or gist. A source nobody can fetch cannot be re-verified by a reader, a reviewer, or the audit itself.

A trade book is not a source class. When a rule's wording comes from a practitioner text — a book, a blog, a conference talk — find the research that backs the claim itself and rest the rule on that; the practitioner text may then be named in `rule-cards-provenance.md` as the formulation the rule follows, never in the card and never as its evidence. Where an openable source carries the same formulation, drop the unopenable one instead of keeping both.

## Quality Gate

MUST run `/auditing-ai-context` on every SKILL.md or agent prompt change before committing.
