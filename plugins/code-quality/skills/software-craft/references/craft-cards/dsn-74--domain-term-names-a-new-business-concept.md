---
title: In code that implements significant business rules, a type, operation or module added for a business concept the codebase does not yet name takes the term that the project's glossary, requirements or product documentation uses for it within its bounded context, not a generic, CRUD or framework word or a coined synonym
rule_id: DSN-74
domain: design
step: [design, implement]
applies_to: [universal]
triggers: ['\b(class|struct|interface|record|enum|trait|type|object|module|namespace)\s+\w*(Create|Update|Delete|Insert|Upsert|Crud|CRUD|Record|Entity|Entry|Item|Data|Info|Dto|DTO)\w*', '\b(def|func|fn|function|sub)\s+(\([^)]*\)\s*)?(create|update|delete|insert|upsert|save|set|process|handle|do|Create|Update|Delete|Insert|Upsert|Save|Set|Process|Handle)(_|[A-Z]|\b)\w*\s*[(<]', 'signal:added_file']
scope: callers
check_kind: semantic
severity_default: minor
---

# In code that implements significant business rules, a type, operation or module added for a business concept the codebase does not yet name takes the term that the project's glossary, requirements or product documentation uses for it within its bounded context, not a generic, CRUD or framework word or a coined synonym

## Thesis
In code that implements a domain's significant business rules, a type, operation or module that a change adds for a business concept the codebase does not yet name takes the business term that the domain's recorded vocabulary uses for that concept within the bounded context the code belongs to. The recorded vocabulary is the shared vocabulary the team keeps in its documentation, such as a glossary, the related high-level artifacts such as the requirement or change description, the names in the product's user interface and user documentation, and the industry standards the domain follows. An operation that changes a domain entity is named in that vocabulary for the change it performs. A generic, CRUD, storage or framework word, or a synonym of the author's own, standing where the recorded vocabulary has a term for the concept is the finding.

## Rationale
Readers of a program have two main sources of domain information, identifier names and comments, and where a function is uncommented, comprehension is almost exclusively dependent on the identifier names. Programmers often learn the domain from external sources such as books and articles and are likely to search the source code with the terms commonly known in the domain literature, which is why those terms belong in identifiers and comments. A case study of software from one problem domain found that on average 42% of the domain terms were used in the source code, and of the domain terms used there, 23% were present in comments only and 11% in identifiers alone. When the same terms mean the same thing in conversations, documentation and code, teams reduce misunderstandings and produce domain models that accurately reflect business intent. The quality of identifiers and comments has been measured as their consistency with high-level artifacts, and in two controlled experiments with students, showing developers the textual similarity between their code and the related high-level artifacts helped to improve the quality of the source code lexicon.

## Example
```typescript
bad:  // glossary: "an order is placed on hold pending a credit check"
      class OrderData { flag = false; }
      function updateOrderFlag(order: OrderData) { order.flag = true; }
good: // glossary: "an order is placed on hold pending a credit check"
      class Order {
        private onHold = false;
        placeOnHold() { this.onHold = true; }
      }
```

## Limits
The rule reaches code with significant business rules: simpler responsibilities, such as a CRUD service, can be managed with simpler approaches, and their create, read, update and delete names pass. Each bounded context can have its own language, so the same word can mean different things in different contexts and the same entity can carry different names, a User in a user-profile context and a Buyer in an ordering context; the terms are not unified across contexts, and a name that differs from another context's word is no finding. A technical construct with no business meaning takes the established programming term that most programmers are familiar with, as a contiguous data structure is named Array. Where the recorded vocabulary itself speaks of creating, updating or deleting the thing, that word is the business term and passes. The rule reaches only a concept the codebase does not yet name; where it already has a name, the question is consistency with that existing vocabulary, which this rule does not decide. Naming guidance holds two positions here. One prefers the domain's precedented term, so that within a programming domain such as mathematics sin(x) is preferable to an explanatory phrase, and favours names in the product user interface and industry standards. The other keeps terms of art for crucial meaning that a more common word would lose, skin over epidermis, and asks for names whose purpose or intent is understandable to a new reader, even someone on a different team than the owners; on that side an experiment with 158 programmers found that longer names from production code took more time to process and reduced correctness in a recall task, evaluated the advantage of identifiers tied to a programmer's persistent memory, and concluded that good naming limits length and reduces the need for specialized vocabulary. The separating condition is whether the term belongs to the recorded vocabulary of the code's bounded context. A term that vocabulary establishes is the domain's precedent, which its developers and domain experts share in conversations, documentation and code, so the rule asks for it in its established meaning even where a beginner would grasp a more common word more easily. A term of art that the recorded vocabulary does not use, where a more common word conveys the meaning just as well, is the obscure term the other position warns against, and the rule never asks for it.

## Validator
Grep the hunk for added declarations of types, modules and routines whose names carry a generic, CRUD, storage or framework word (Data, Info, Item, Record, Entity, Dto, Manager, create, update, delete, save, set, process, handle) or an unfamiliar coined word. Open the module and its callers to establish whether the code implements significant business rules, which business concept the declaration stands for, and which bounded context, service or module boundary it belongs to; stop when it is a CRUD service with simpler responsibilities or a technical construct with no business meaning. Grep the codebase for an existing name of that concept and stop when one exists. Open the recorded vocabulary of that context, the glossary, the change description or linked requirement, the user-interface strings, the user documentation and the industry standards the domain follows, and find the term it uses for the concept or for the change an entity-changing routine performs. Validator question: **Does a type, operation or module that this change adds for a business concept in business-rule code carry a generic, CRUD, storage or framework word or a coined synonym where the recorded vocabulary of its bounded context establishes a different term for that concept or change?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: DSN-74`, severity minor, `file`, `symbol`, `code` = the added declaration line carrying the generic or coined name, quoted verbatim from the diff, `fix` = the declaration renamed to the recorded term, or the entity-changing routine renamed for the business change it performs, in the file's language, `rationale` = the business concept, the recorded term with the place it is recorded in, and the word the change used in its place).
