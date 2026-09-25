---
title: An empty Javadoc block tag is removed or given a description
rule_id: MNT-30
domain: maintainability
triggers: ['@param \w+\s*$', '@return\s*$', '@throws \w+\s*$', '@param (\w+) the \1\b', '@return the \w+\s*$']
scope: hunk
check_kind: mechanical
severity_default: suggestion
---

# An empty Javadoc block tag is removed or given a description

## Thesis
A `@param`, `@return` or `@throws` tag the diff adds carries a description: a tag whose description is empty is removed or given one. A description that only echoes the name (`@param id the id`, `@return the user`) is tolerated where there really is nothing else worthwhile to say, and is flagged where a typical reader needs more — a unit, a range, a null contract, the condition of the exception, the meaning of a domain term — because the tolerance for "the foo" does not justify omitting what such a reader needs to know.

## Rationale
A block tag without a description adds nothing for a future reader of the code and hides, in a list of tags, the one tag that carried information; the remedy is to remove it or to describe. A description that echoes the name costs the same reading time and, where the term is not obvious to a typical reader (`canonicalName`), leaves that reader without the fact they came for; the remedy is the sentence that carries it.

## Example
```java
bad:  /**
       * Gets the user.
       * @param id
       * @return the user
       */
      User getUser(long id);
good: /** Loads the user by primary key; {@code null} when no such user exists. */
      @Nullable User getUser(long id);
```

## Limits
A `@param` that gives only the unit or the range ("in milliseconds", "1-based") is content. A name echo on a member where there really is nothing else worthwhile to say (`@param id the id` on a trivial getter) is not flagged. A generated file, a license header and an `@inheritDoc` are out of scope.

## Validator
On the triggered hunk read each added block tag and its description. Validator question: **is this tag's description empty, or does it only echo the name where a typical reader needs more?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: MNT-30`, severity suggestion, `file`, `symbol`, `code` = the tag quoted verbatim from the diff, `fix` = the removal of the empty tag, or the description that carries the missing fact, `rationale` naming the information a reader still lacks).

## Source
Error Prone `EmptyBlockTag` — "A block tag (@param, @return, @throws, @deprecated) has an empty description. Block tags without descriptions don't add much value for future readers of the code; consider removing the tag entirely or adding a description". Google Java Style Guide §7.3.1 — Javadoc is optional for a member "if there really and truly is nothing else worthwhile to say but 'the foo'", and "it is not appropriate to cite this exception to justify omitting relevant information that a typical reader might need to know", with the `canonicalName` example whose `@param canonicalName the canonical name` would leave a reader who does not know the term without it. Caveat: §7.3.1 makes the Javadoc optional for such members and does not flag a written "the foo" tag, so the name-echo clause reaches only a tag where a typical reader needs more.
