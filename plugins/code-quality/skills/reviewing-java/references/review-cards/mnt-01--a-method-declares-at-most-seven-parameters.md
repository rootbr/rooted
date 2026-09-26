---
title: A method declares at most seven parameters, and a longer list becomes a parameter object
rule_id: MNT-01
domain: maintainability
triggers: ['\((?:[^,()]*,){7,}[^,()]*\)', '^\s*(?:public|protected|private|static|final|\s)*[\w<>\[\], ?]+\s+\w+\s*\(\s*$', '(?:[\w<>\[\]]+\s+\w+\s*,\s*){3,}', 'record \w+\(']
scope: hunk
check_kind: mechanical
severity_default: minor
---

# A method declares at most seven parameters, and a longer list becomes a parameter object

## Thesis
A method or constructor the diff adds or changes declares at most seven parameters; a longer list is grouped into a parameter object — a record holding the values that travel together — or the method is split by responsibility.

## Rationale
Callers match arguments to parameters by position; past a handful the mapping is read off the declaration, and adjacent parameters of one type invite a swap the compiler cannot see. A long list signals that the method does too many things or that related values have not been grouped, and SonarSource and Checkstyle report at seven. A parameter object names the group once, carries its invariants, and shrinks every signature that passes it along; a class whose constructor takes a long list has too many responsibilities, which the same refactoring exposes.

## Example
```java
bad:  Transfer make(String from, String to, long cents, String ccy,
                    LocalDate when, String memo, String channel, String reason) { ... }
good: record TransferRequest(Account from, Account to, Money amount,
                             LocalDate when, Memo memo, Channel channel) {}
      Transfer make(TransferRequest request) { ... }
```

## Limits
A constructor of an injected bean (`@Autowired`, `@Inject`), a web handler method (`@RequestMapping` and its shortcuts, JAX-RS), and a `@JsonCreator` factory take their parameters from a framework and are not flagged. A limit declared in the project context replaces seven. A parameterized test method with many inputs is out of scope.

## Validator
On the triggered hunk count the parameters of each added or changed method or constructor declaration, following a multi-line declaration across its lines. Exclude the framework-driven declarations named in the Limits. Validator question: **does this declaration carry more than seven parameters without a framework reason?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: MNT-01`, severity minor, `file`, `symbol`, `code` = the declaration quoted verbatim from the diff, `fix` = the record type and the shortened signature, `rationale` naming positional matching and the swap risk).

## Source
SonarSource `java:S107` "Methods should not have too many parameters" — "A long parameter list can indicate that a new structure should be created to wrap the numerous parameters or that the function is doing too many things"; exceptions for `@RequestMapping` handlers, JAX-RS methods, `@Autowired`/`@Inject` constructors and `@JsonCreator` (rule text from the `sonar-java` 6.15.1 plugin resources; the default maximum of 7 for methods and for constructors is `TooManyParametersCheck.DEFAULT_MAXIMUM` in the `sonar-java` check source). Checkstyle `ParameterNumber` — `DEFAULT_MAX_PARAMETERS = 7`. PMD `ExcessiveParameterList` — "When parameters share similar datatypes, they become prone to mix-ups during refactoring or when calling the method with positional arguments"; its default report level is 10. Spring Framework reference, Dependency Injection → Constructor-based DI — "a large number of constructor arguments is a bad code smell, implying that the class likely has too many responsibilities".
