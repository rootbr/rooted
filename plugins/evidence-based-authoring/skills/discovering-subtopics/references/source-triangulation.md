# Source Triangulation by Topic Type

> **Load-bearing rule:** the question map is worthless without canonical sources grounding its non-obvious claims. Every slot that applies to the topic names at least one source (book / paper / conference / spec / community / talk / recognized expert). Unverified recall of a title, author, or expert counts as a hallucination — search before stating.

## Contents
- §Topic-type classifier
- §Per-slot source ladders (books / papers / conferences / specs / communities / talks / recognized experts)
- §Search phrasing
- §Language strategy
- §Verification discipline
- §Anti-patterns

---

## Topic-type classifier

| Type | Examples | Primary pools |
|--|--|--|
| Technical | Programming languages, protocols, frameworks, operations practices | Specs, RFCs, official docs, curated practitioner lists, conference talks, community Q&A |
| Scientific (research) | Consensus theories, open problems, active subfields | Foundational papers, surveys, top conferences, arXiv / PubMed / SSRN, scholarly graphs |
| Regulatory / bureaucratic | Standards, compliance, law, taxation | Official standard body, regulator site, practitioner commentary |
| Consumer / product | Product categories, services, healthcare / financial choices | Verified-purchase reviews, specialist forums, first-person experience reports |
| Professional (domain-specific) | Medical condition, financial instrument, legal doctrine, clinical psychology | Professional BOK, peer-reviewed journals, practice guidelines |
| Humanities | Literature, philosophy, history, art, music theory | Critical editions, PhD qualifying-exam reading lists, academic monographs, multilingual primary canons |
| Practical / craft | Gardening, cooking, fermentation, winemaking, woodworking | Extension services, guild / society publications, regional tradition literature |

Mixed topics draw from multiple pools; classify into the dominant two and run both.

---

## Per-slot source ladders

### Canonical books

Include **one practitioner-level text** AND **one academic / graduate-level text** — they cover disjoint material. Practitioner texts give applied pitfalls and patterns; academic texts give theoretical foundations, consensus hierarchies, and invariants that practitioners treat as implicit. A map citing only one type has a systematic blind spot.

| Topic type | Practitioner text via | Academic / graduate text via |
|--|--|--|
| Technical | Conference speaker bibliographies; official docs' further-reading sections; top-cited titles in the field | Top-university syllabi and reading lists; seminal papers' preferred textbook citations |
| Scientific | — | Top-5 university PhD qualifying-exam reading lists |
| Regulatory | Official standard + practitioner commentary (rare to have books) | Regulatory-law academic treatises |
| Professional | Certification BOK recommended reading (CFA, PMP, HIMSS, ABIM) | Discipline's university textbook (medical / law school) |
| Humanities | Practitioner-oriented monographs, critical editions with editorial apparatus | PhD qualifying-exam reading lists; Companion / Handbook series (Cambridge, Oxford, Blackwell) |
| Practical / craft | Extension-service publications; guild manuals; master-practitioner books | Agricultural / food-science / ergonomics academic texts |

### Foundational + recent papers
- **Foundational**: "most cited" on Google Scholar over all time. Usually 1970s–2000s for modern fields; centuries for humanities.
- **Recent overview**: filter last 3 years + "survey" OR "review" OR "state of the art" OR "handbook" in title.
- If no overview exists, sample the 10 most-cited works of the last 2 years and note the absence as an open question.

### Conferences / venues
Identify the venues the field itself recognizes. For indexed disciplines, consult the relevant classification (ACM CCS for computing, BISAC for publishing, MeSH for medicine) to find where a niche topic files.

For humanities and crafts, substitute venues with:
- Annual scholarly conferences of the relevant learned society
- Trade or guild meetings (e.g. master-gardener congresses, brewers' guild conferences)
- Journal publication patterns within a society's house organ

Always pin the year — fields evolve fast and a "top conference" from 2010 may have migrated or dissolved.

### Authoritative specifications / standards / checklists
- RFC number if the topic has one.
- Official style guide / standard / code of practice.
- Standards-body publications (ISO, IEEE, ANSI, W3C, IETF, NIST, SEI, OWASP) when relevant.
- **Practitioner reference materials** (PRIMARY sources, not secondary): expert-authored reviews, community-maintained checklists, guild-published best-practice bulletins. They codify incident-driven knowledge and are load-bearing for non-obvious questions.
- Curated lists (`awesome-<topic>`, society reading lists) — treat as **directories, not authorities**; follow through to the items they point at.

### Community / practitioner knowledge
- Subject-specific community Q&A sites sorted by all-time votes
- Topical subreddits / forums filtered by best-of-year
- Top comments on high-signal threads aggregating the topic
- Discussion / issues on the canonical project's or society's repository
- Regional practitioner networks (for practical crafts: allotment associations, gardening clubs, local chapters of national guilds)

### Talks / podcasts
- Conference video archives by tag / year
- Topical podcast episodes with canonical practitioners as guests
- Open university lectures (MIT OCW, Stanford Online, Yale Open, Coursera / edX from top institutions)
- Local chapter video archives for "book-club"-style communities (Papers We Love being the canonical software example; similar models exist in medicine, classics, and craft disciplines)

### Recognized experts
Name 2–5 living or historical experts whose work anchors the field. Each entry MUST state:
- **Name + affiliation or era** (e.g. "Dedre Gentner, Northwestern / founder of structure-mapping theory"; "Freud, 1856–1939, founder of psychoanalysis")
- **Why canonical** — in one line: what the expert introduced, codified, corrected, or synthesized that the field cannot be taught without
- **Where to read / hear them** — a link to their bibliography, lecture archive, or key talk

Selection rules:
- Include at least one **founder-era figure** whose work defined the field's vocabulary
- Include at least one **current practitioner** actively shaping the field today
- For multi-generational fields, add one **bridging figure** who carried ideas forward between eras
- If the field has a major non-English tradition, include at least one expert from that tradition
- Verify each expert's name + the attributed contribution via at least one independent source before writing — no recall without retrieval

Empty slot (no recognized expert can be named with confidence) → "no recognized expert identified — open question"; never fabricate.

---

## Search phrasing (both user's wording AND canonical terms)

Retrieval is lexical — run the user's phrasing AND the field's canonical terminology. Different communities index under different terms, and folk and canonical vocabularies often diverge.

Always run both. Missing one community means missing half of the non-obvious questions that community has already worked through.

---

## Language strategy

| Topic type | Languages | Rationale |
|--|--|--|
| Regulatory / government | Local + EN | Official source usually not translated |
| Technical / scientific global | EN | Primary publication language |
| Region-specific product / service | Local + EN | Local forums hold first-hand experience |
| Mature field with major non-English community | EN + community-secondary | Practitioner talks and writing in the secondary language hold material untranslated to EN |
| **Discipline with multilingual PRIMARY canon** | each primary language separately | Canonical works exist only in the original; English translations are secondary |
| **Practical hobby / craft with regional traditions** | EN + regional-tradition language(s) | Extension services, allotment culture, craft societies publish primarily in local language |

**Domain → community-language mapping** (examples; add more as encountered):

- Humanities with multilingual primary canon: psychoanalysis (DE + FR + RU + EN), continental philosophy (DE + FR + EN), classical studies (ancient Greek + Latin + DE for Altertumswissenschaft), Slavic literature (RU + PL + CZ)
- Practical craft: vegetable gardening (DE Kleingarten + RU dacha + NL allotment + EN RHS tradition), traditional fermentation (local-cuisine language), winemaking / brewing (FR viticulture + DE Reinheitsgebot + EN practitioner)
- Technical frameworks with large non-English communities: varies by framework — check the community's primary conference language before defaulting to EN only

For a topic primarily authored in a non-English tradition, search that language first. For a psychoanalysis topic, search DE + FR + RU in parallel — English sources are translations. For terrace potatoes in Bavaria, DE + RU + EN each surface material the others miss.

---

## Verification discipline

- Every author / title / expert named MUST appear in at least one independent search result before writing — no recall without retrieval.
- Every conference name MUST resolve to an active URL in the last 3 years (unless marked as historical).
- Every spec / RFC / standard MUST link to the canonical URL of the issuing body, not a secondary summary.
- Every recognized expert MUST be tied to the specific contribution being cited (not "famous in the field" — *famous for what*).
- If a source cannot be verified, mark the slot "no canonical source found — open question" rather than fabricate.

---

## Anti-patterns (specific to source slots)

| Anti-pattern | Fix |
|--|--|
| Listing an author or expert who "probably worked on this" without search | Search first; cite exact title / contribution + year, or omit |
| Citing a conference / society without year | Always pin the year (fields evolve fast) |
| Pasting the first search hit as "canonical" | A canonical source is referenced by the field's own textbooks; confirm via 2+ independent mentions |
| Listing a curated / awesome-list as the primary source | Curated lists are directories, not authorities; follow through to the items they point at |
| Naming an expert without the specific contribution | "Expert in X" is not a citation; state what they introduced, codified, or corrected |
| Omitting the practitioner community | First-hand knowledge (bug reports, case notes, field journals, extension-service bulletins) is load-bearing for non-obvious questions and typical misconceptions |
