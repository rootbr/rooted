---
title: A stub makes a replaced call return or throw only what the real dependency's contract allows
rule_id: TST-03
domain: tests
step: [test]
applies_to: [tests]
triggers: ['[.]then(Return|Throw|Answer|Resolve|Reject|Call)\(|\b(do|will)(Return|Throw|Answer)\w*\(', '\b(return_value|side_effect)\s*=', '[.]mock(Return|Resolved|Rejected)Value\w*\(|[.]mockImplementation\w*\(', '[.]\w*Returns?(Async)?\(|[.]Throws?(Async)?[(<]|[.](returning|returns?|return_const|return_once|return_var|throws?|resolves|rejects)(_st)?\(', '[.]and_(return|raise|throw)\b|\}\s*(returns|throws|answers)\b']
scope: callers
check_kind: semantic
severity_default: minor
---

# A stub makes a replaced call return or throw only what the real dependency's contract allows

## Thesis
A stubbed call returns only values, and raises only errors, that the real dependency can produce for that call. Each error a stub raises is one the real method's signature can raise — for a checked error, a type the method's declared error list covers — and each value or error it produces is the one the method's documented contract gives for the stubbed situation: a present value where the contract guarantees one, the documented normal result (an empty collection, an absent optional) where the contract gives that instead of an error, a value inside any documented range or format. Where the signature and the documentation are silent, every value of the declared type and every error the signature admits is within the contract.

## Rationale
Inside the test the stub is the dependency's only behaviour, so the code under test is exercised on exactly what the stub produces. Where the code under test handles the stubbed result apart from the one the contract gives, a value or error outside the real contract drives it down a branch production never reaches, and the test leaves the branch production does reach unexercised; the test passes and says nothing about the production path. The stub restates, from the test author's belief, how the dependency behaves, and nothing in the test checks that belief: a stub that was wrong from the start, or that a later change to the dependency made wrong, keeps passing. In a study that manually analysed more than 2,000 test dependencies in three open-source systems and one industrial system and surveyed more than 100 professionals, developers named keeping a mock's behaviour compatible with the original class a key challenge of mocking, together with the coupling mocking adds between test and production code. For a double to be useful, its behaviour should resemble the real object's as closely as possible. Where the contract is in the type system, tools enforce the rule: a mainstream mocking framework rejects, when the stub is set up, a checked error that matches none of the checked errors in the method signature, and a compile-time static check reports the same stub as an exception the mocked method cannot throw. Keeping every stub inside the contract restores the property a double exists for: what the code under test meets in the test is what it can meet in production.

## Example
```rust
bad:  // Repo::find: Ok(None) for an unknown id, Err(RepoError::Io) on a failed read
      repo.expect_find().returning(|_| Err(RepoError::NotFound));
      assert_eq!(Profiles::new(repo).name(7), "guest");
good: // Repo::find: Ok(None) for an unknown id, Err(RepoError::Io) on a failed read
      repo.expect_find().returning(|_| Ok(None));
      assert_eq!(Profiles::new(repo).name(7), "guest");
```

## Limits
A stub that injects an error or a value the contract admits but a test running the full stack can hardly or never produce — a timeout, a failed write, a full disk, an empty page — is the ordinary use of a double: how rare the case is, or how hard to provoke, does not matter, only whether the contract admits it. A dependency the project context declares untrusted, such as a plugin or a remote peer whose responses the code under test validates, gives no contract the code under test may rely on, so a stub feeding it an out-of-documentation response is correct there. Where the real dependency's declaration and documentation are out of the repository's reach, the finder decides on the signature alone, and a value the signature admits is no finding. Where the double is typed against the real interface, a stubbed value of the wrong type fails to compile, or fails the test when the stub is set up or called, so the finding there is a checked error outside the declared error list or a value or error the documentation excludes; where the double is untyped — in a dynamically typed language, or cast past the type checker — a stub can also return a value of a type the method never returns. Whether the stubbed method exists on the real type, and what the test asserts or verifies, are outside this rule.

## Validator
Grep the hunk's added lines for stubbing calls: a then-return, then-throw, then-answer, then-resolve, then-reject or then-call; a do- or will- return, throw or answer; an assignment to a double's return value or side effect; a mocked return, resolved or rejected value or implementation; a return, returning, returns, return-const, return-once, return-var, throw, throws, resolves or rejects call, with or without an async or single-thread suffix; an and-return, and-raise or and-throw; a returns, throws or answers written after a stubbed block. For each, name the replaced call — the real type the double stands for and the method stubbed — and the value or error the stub makes it produce. Open the real type's declaration in the repository and read the method's signature (return type, nullability or optional marker, declared error types or error variants) and its doc-comment (what it returns for an unknown key, an empty input or a failure; which errors it raises, and when). Match the stub against both, for the situation the test sets up: a checked error type that no type in the declared error list covers, an error the documentation assigns to another situation or never raises, an absent or null value where a value is guaranteed, a value outside a documented range or format, a value of a type the method never returns. Validator question: **Does a stub in the hunk make the replaced call return a value or raise an error that the real method's signature or documented contract excludes for the situation the test sets up?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: TST-03`, severity minor, `file`, `symbol`, `code` = the stubbing line verbatim from the diff, `fix` = the stub rewritten to return or raise what the real method's contract gives for the test's situation, in the file's language, `rationale` = the excluded value or error and the signature or doc-comment line of the real method that excludes it).

## Source
- Error Prone bug pattern `MockIllegalThrows` (google/error-prone, `core/src/main/java/com/google/errorprone/bugpatterns/MockIllegalThrows.java`): "This exception can't be thrown by the mocked method."; "%s is not throwable by this method; only unchecked exceptions can be thrown." (fetched)
- Mockito `OngoingStubbing#thenThrow` Javadoc (mockito/mockito, `mockito-core/src/main/java/org/mockito/stubbing/OngoingStubbing.java`): "If throwables contain a checked exception then it has to match one of the checked exceptions of method signature."; the violation raises "Checked exception is invalid for this method!" (`internal/exceptions/Reporter.java`) (fetched)
- DOI 10.1109/MSR.2017.61, abstract: "collect data from three OSS projects and one industrial system [...] we manually analyze how more than 2,000 test dependencies are treated [...] a structured survey with more than 100 professionals [...] developers report that maintaining the behavior of the mock compatible with the behavior of original class is hard and that mocking increases the coupling between the test and the production code." (fetched)
- arXiv:2208.01321, §1: "for it to be useful, the behavior of the mock should resemble, as closely as possible, that of a real object" (fetched)
- mockall README (asomers/mockall), Overview: "They can be used [...] to inject edge and error cases that would be difficult or impossible to create when using the full stack." (fetched)

Caveat: the two tool checks reach only a checked error outside a declared list; a value, and an error the documentation excludes, rest on the two studies — one reports keeping a mock's behaviour compatible with the original class as a key challenge, the other states that, to be useful, a mock's behaviour should resemble the real object's as closely as possible — and neither counts defects caused by an out-of-contract stub.
