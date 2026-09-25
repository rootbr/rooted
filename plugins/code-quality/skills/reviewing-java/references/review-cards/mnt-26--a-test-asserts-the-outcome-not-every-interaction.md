---
title: A test asserts the outcome of the call and does not verify every collaborator interaction or a stubbed call
rule_id: MNT-26
domain: maintainability
triggers: ['verify\(', 'verifyNoMoreInteractions\(', 'verifyNoInteractions\(', 'times\(\d+\)', 'never\(\)']
scope: file
check_kind: mechanical
severity_default: minor
---

# A test asserts the outcome of the call and does not verify every collaborator interaction or a stubbed call

## Thesis
A test's primary assertion is on what the code under test returned, threw, or changed in observable state; `verify(mock).method(...)` is used for an interaction that is itself the behaviour under test — a message sent, an event published, a call that must not happen — and not for every collaborator the implementation happens to call; `verifyNoMoreInteractions()` is not written in every test, and a call the test stubbed is not also verified.

## Rationale
A test that verifies each collaborator call mirrors the implementation: it passes only while the code calls those mocks in that way, so a refactoring that keeps the behaviour — caching a lookup, reordering two calls, merging two repository queries — breaks it, and the failure says nothing about behaviour. Abusing `verifyNoMoreInteractions()` — writing it in every test method — leads to overspecified, less maintainable tests, and a `verify` on each incidental collaborator call has the same effect, by the refactoring argument above; verifying a stubbed invocation is redundant, because if the code cares about the stubbed value something else already breaks when the call is missing. An outcome assertion survives any implementation that produces the outcome.

## Example
```java
bad:  service.place(order);
      verify(repo).findById(order.id()); verify(pricing).priceOf(any()); verify(audit).log(any());
      verifyNoMoreInteractions(repo, pricing, audit);
good: Receipt r = service.place(order);
      assertThat(r.total()).isEqualTo(Money.of(42, EUR));
      verify(mailer).send(orderConfirmation(order));   // the interaction that is the behaviour
```

## Limits
A collaborator whose call is the observable effect — a notification, a publish, a deletion — is verified by design. `never()` and `verifyNoInteractions` on a specific mock express a required absence. A test of a thin adapter whose whole job is to forward a call may verify the forward. The project context may declare an interaction-testing style for a layer.

## Validator
On the triggered hunk count the `verify` calls per test method and check whether the test also asserts a return value, an exception or state; check for `verifyNoMoreInteractions` and for a `verify` on a call that a `when(...)`/`given(...)` in the same test stubs. Validator question: **does this test's correctness rest on which collaborators were called rather than on the outcome, or does it verify a stubbed call or blanket-verify no more interactions?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: MNT-26`, severity minor, `file`, `symbol`, `code` = the verify lines quoted verbatim from the diff, `fix` = the outcome assertion and the one interaction that matters, `rationale` naming the refactoring that would break the test without changing behaviour).

## Source
Mockito `org.mockito.Mockito` class Javadoc — §8 "Finding redundant invocations": `verifyNoMoreInteractions()` "is not recommended to use in every test method … Abusing it leads to overspecified, less maintainable tests"; §2 on stubbing: "Although it is possible to verify a stubbed invocation, usually it's just redundant. If your code cares what get(0) returns, then something else breaks (often before verify() even gets executed). If your code doesn't care what get(0) returns, then it should not be stubbed" (fetched from `mockito-core/src/main/java/org/mockito/Mockito.java`, branch `main`).
