---
title: A @Deprecated element states since and a @deprecated tag naming the replacement, with forRemoval = true when removal is announced
rule_id: REL-27
domain: reliability
triggers: ['@Deprecated', '@deprecated']
scope: hunk
check_kind: mechanical
severity_default: suggestion
---

# A @Deprecated element states since and a @deprecated tag naming the replacement, with forRemoval = true when removal is announced

## Thesis
A newly deprecated class, method, field or constructor carries `@Deprecated(since = "<version>")` together with a Javadoc `@deprecated` tag that says why and names the replacement or says none exists, and `forRemoval = true` when the tag announces removal; the annotation and the tag appear together.

## Rationale
Deprecation is a message to callers whose only channel is the declaration itself. `since` tells a caller how long the warning has stood; `forRemoval = true` "indicates intent to remove the annotated program element in a future version" and makes the compiler emit a removal warning, where the default is a discouragement with no removal planned, so a tag that announces removal without it leaves the compiler saying the opposite; the `@deprecated` tag is where the reason and the replacement live, and a replacement "often has subtly different semantics" a caller has to be told about. A bare `@Deprecated` gives the caller a warning and no way to act on it, so the old member is used until the release that deletes it.

## Example
```java
bad:  @Deprecated
      public Order find(long id) { ... }
good: /**
       * @deprecated since 2.4, removed in 3.0; use {@link #lookup(long)}, which returns an empty Optional instead of null.
       */
      @Deprecated(since = "2.4", forRemoval = true)
      public Order find(long id) { return lookup(id).orElse(null); }
```

## Limits
A deprecation inherited from an overridden method or an interface needs no repeated tag on the override. A private or package-private member deprecated for internal housekeeping may omit `since`. A project context that states the release version is not tracked in annotations rejects the `since` half.

## Validator
On the triggered hunk find each added `@Deprecated`. Check for the `since` element, a `@deprecated` Javadoc tag on the same element that names or links a replacement (or states that none exists), and, where the tag announces removal, `forRemoval = true`. Validator question: **does this deprecation leave the caller without the version or the replacement, or announce a removal the annotation does not carry?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: REL-27`, severity suggestion, `file`, `symbol`, `code` = the `@Deprecated` declaration quoted verbatim from the diff, `fix` = `@Deprecated(since)` with a `@deprecated` tag linking the replacement, and `forRemoval = true` where removal is announced, `rationale` naming what the caller cannot learn from the bare annotation).

## Source
`java.lang.Deprecated` Javadoc, Java SE 21 — "It is strongly recommended that the reason for deprecating a program element be explained in the documentation, using the @deprecated javadoc tag. The documentation should also suggest and link to a recommended replacement API, if applicable. A replacement API often has subtly different semantics, so such issues should be discussed as well"; "It is recommended that a since value be provided with all newly annotated program elements"; `forRemoval` — "A value of true indicates intent to remove the annotated program element in a future version"; "The @Deprecated annotation should always be present if the @deprecated javadoc tag is present, and vice-versa". JEP 277 "Enhanced Deprecation" (unfetched; the Javadoc above is its normative form).
