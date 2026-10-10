---
title: Text added to a user-facing document states what users do and see in their terms and leaves implementation detail meant for maintainers to a separate document
rule_id: DOC-14
domain: docs
step: [document]
applies_to: [prose]
triggers: ['(?i)\b(refactor(ed|ing|s)?|internal(ly)?|under the hood|implementation detail)\b', '\b[A-Z][a-z]\w*?(Impl|Manager|Helper|Utils?|Factory|Internal)\b']
scope: callers
check_kind: semantic
severity_default: suggestion
---

# Text added to a user-facing document states what users do and see in their terms and leaves implementation detail meant for maintainers to a separate document

## Thesis
Text added to a document whose readers are the code's users — a README or getting-started page, a tutorial, a how-to or installation guide, a release note or changelog entry — states what users do and see, and for a release note or changelog entry the user-visible effect of the change, in the names those users meet, and implementation detail meant for maintainers — internal class names, implementation steps, refactoring notes — stays out of it, kept where maintainers need it in a design, contributor or maintainer document, with a pointer from the user document where users need the detail; a strictly internal change with no user-visible effect takes no changelog entry.

## Rationale
Of 878 documentation-related artifacts mined from mailing lists, question-and-answer site discussions, issue repositories and pull requests, 107 concerned readability, and abstract, too technical and too verbose or noisy information were among the main reasons for poor readability. Information that looks clear from the developers' perspective is not always easy for the system's users to digest. In a survey of 78 practitioners on documentation issues, documentation clarity was the readability issue perceived as most important, by 88% of them; their first remedy was that writers keep the actual documentation users and their needs in mind, and their second that someone with little domain knowledge test the document — for an installation guide, users of the system rather than a development team member. In one project's changelog policy, the changelog's intended audience is mainly users, not core developers and contributors, so an entry describes the user-visible effects of the change succinctly and accurately, without long technical elaborations or digressions, and without requiring the reader to have read the diff. One project's NEWS policy exempts strictly internal changes with no user-visible effects from the changelog. Maintainer material has readers of its own: practitioners perceive different documentation types as useful for different tasks, and a contribution guideline — workflows, CI pipelines, release processes — was rated practical for testing and quality assurance by 64% of participants and for programming by 45%. Where users need more, a pointer carries them there: developers answered findability issues by giving users pointers to the documentation needed. In a study of over 440 professional developers learning new APIs, some of the most severe obstacles pertained to documentation, and matching the API with scenarios was one of five factors to consider when designing API documentation.

## Example
```java
bad:  // CHANGELOG.md
      // - Refactored OrderManagerImpl to cache orders in a ConcurrentHashMap
good: // CHANGELOG.md
      // - Reopening an order no longer waits for it to load again
      // docs/design/order-cache.md
      // - OrderManagerImpl caches loaded orders in a ConcurrentHashMap
```

## Limits
When the code's users are developers, as with a library, the public names they call are their terms, and in a changelog entry an inline reference to such a name can help readers find more information. A document whose readers are maintainers or contributors — a contributor guide, a design or maintainer document — is where implementation detail belongs, and the rule does not reach it. Text inside the source — comments, doc comments, the contract an API reference states — and end-user manuals or product copy are outside the rule.

## Validator
Open each file in the hunk whose readers are the code's users: a README or getting-started page, a tutorial, a how-to or installation guide, a release note or changelog. Grep its added lines for internal type names (an Impl, Manager, Helper, Utils, Factory or Internal suffix) and for refactoring, internal and under-the-hood wording. For each hit, trace the name to the code: a public type, function, command or setting that users call or see is their term; a name or step only maintainers meet is implementation detail. Check whether the added text states what users do or see, and for a release note or changelog entry what they do or see differently after the change. Validator question: **Does text added to a user-facing document carry an internal name, an implementation step or a refactoring note that the document's users never meet?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: DOC-14`, severity suggestion, `file`, `symbol`, `code` = the added document line that carries the internal name or implementation note, verbatim, `fix` = the line rewritten as the user-visible effect in the document's own markup, or the line deleted when the change is strictly internal with no user-visible effect, with any detail maintainers need kept in a design or contributor document and a pointer to it where users need it, `rationale` = names the document's readers and the internal term they never meet).
