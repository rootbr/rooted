---
title: A generic type is written with its type arguments wherever the language allows them to be omitted, and an unknown argument is written explicitly
rule_id: CODE-48
domain: code
step: [implement]
applies_to: [static-types, dynamic-types]
triggers: ['\b(List|ArrayList|LinkedList|Map|HashMap|TreeMap|Set|HashSet|Collection|Iterable|Iterator|Optional|Comparable|Comparator|Class|Queue|Deque|Stream|Future|Supplier|Function|Consumer|Predicate)\s+\w+\s*[=;,()]', '\bnew\s+(ArrayList|LinkedList|HashMap|TreeMap|HashSet|TreeSet)\s*\(', '(:|->)\s*(list|dict|set|frozenset|tuple|type|List|Dict|Set|Tuple|Sequence|Mapping|Iterable|Callable)\s*($|[,)=:\]|])', '\b(extends|implements)\s+(Comparable|Comparator|Iterable|List|Map)\s*[{,]', '[<(,]\s*(List|ArrayList|Map|HashMap|Set|HashSet|Collection|Iterable|Optional|Comparable|Comparator|Class)\s*[>),]', '([\[|]\s*(list|dict|set|frozenset|tuple|type|List|Dict|Set|Tuple|Sequence|Mapping|Iterable|Callable)\s*[\],|)=]|,\s*(list|dict|set|frozenset|tuple|type|List|Dict|Set|Tuple|Sequence|Mapping|Iterable|Callable)\s*\])']
scope: hunk
check_kind: mechanical
severity_default: major
---

# A generic type is written with its type arguments wherever the language allows them to be omitted, and an unknown argument is written explicitly

## Thesis
Every use of a generic type writes its type arguments wherever the language would accept the type without them: as the declared type of a variable, a field, a parameter or a result, in a construction, in a cast, and as a supertype. When an argument is unknown, the use still writes it: as a wildcard with an optional upper or lower bound, or, in a language without wildcards, as the type that is consistent with every type, which is not the root of the type hierarchy.

## Rationale
Where a language accepts a generic type without its type arguments, the omission prevents compile-time type checking for the expressions that use the type parameters. In one kind of language, reading an element back then needs an explicit cast, a run-time type check that may fail, and when it fails the program most likely crashes: a list meant to hold integers accepts a string at compile time, and the read throws a cast exception. In another, each omitted argument is assumed to be the type that is consistent with every type, on which the checker allows all operations and which it lets be assigned to a more constrained type. The annotation then also says less, which makes the contract of the function or variable harder to understand. The omitted arguments are implicit, and at least one checker reports them only when an optional check is enabled. Writing the arguments restores the check: adding an element of the wrong type becomes a compile-time error, and the read needs no cast. A study that mined the history of 40 open-source programs suggests that generics sometimes reduce the number of type casts. A wildcard states what is known of an unknown argument: an unbounded one accepts any instantiation of the type, and one with an upper bound accepts an element type that is the bound or a subtype of it.

## Example
```java
bad:  class Row implements Comparable { ... }
      Integer first(List items) { return (Integer) items.get(0); }
      int count(List rows) { ... }
      Map<String, List> byKey = new HashMap();
good: class Row implements Comparable<Row> { ... }
      Integer first(List<Integer> items) { return items.get(0); }
      int count(List<?> rows) { ... }
      Map<String, List<Row>> byKey = new HashMap<>();
```

## Limits
Where the compiler rejects a generic type used without its type arguments, the rule has nothing to flag: there a generic type must be instantiated wherever it is used.

A type parameter with a declared default that is not the top type may be left out: the omission yields that default, which the checker checks like a written argument.

A construction whose type arguments the checker infers is compliant: from an empty inference marker, or, where the language infers without one, from the declared type of its target or from the constructor's arguments. The checker still rejects an element of the wrong type, and the read needs no cast. Where the checker infers nothing, the construction takes the arguments, written on it or, where the language infers from the target, on the declared type of its target.

A type test that only answers true or false against the run-time type, where the type arguments are erased, is outside the rule. A cast and a type test that binds the value to a name are not exempt: where the run-time check sees only the type without its arguments, they take a wildcard argument, and elsewhere they take the arguments like any other use.

A position where type arguments would not compile is outside the rule, such as an override of a library method declared without them, or an array creation whose element type needs a concrete argument. An array creation whose element type is unknown takes the unbounded wildcard, which compiles there.

A wildcard or the explicit type that is consistent with every type closes the finding but is not always the best argument: in many cases a type parameter might be more appropriate, and this rule does not choose between them.

The project context can reject the finding by stating that the project accepts generic types written without type arguments, a choice that at least one checker leaves to the project by making its check optional.

## Validator
In the hunk, find each added line that names a generic type without type arguments: a standard library type such as a collection or map, an optional, an iterator or iterable, a comparator or comparable, a function type, a future, a stream or a class token, or a project type whose declaration in the hunk shows type parameters. Look for it as the declared type of a variable, field, parameter or result, in a construction, in a cast, in an extends or implements clause, in an annotation, or as an argument of another generic type. Skip a language whose compiler rejects the omission, a construction whose type arguments the checker infers from an empty inference marker or, in a language that infers without one, from the declared type of its target or from the constructor's arguments, an omitted type parameter whose declared default is not the top type, a type test that only answers true or false, and a position where type arguments would not compile, such as an override of a library method declared without them or an array creation whose element type needs a concrete argument. Skip the case where the project context states that the project accepts generic types without type arguments. Validator question: **Does an added line use a generic type without its type arguments in a position where the language accepts the omission and type arguments would compile?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: CODE-48`, severity major, `file`, `symbol`, `code` = the declaration, construction, cast, supertype or annotation that names the generic type without its arguments, quoted verbatim from the diff, `fix` = the same line with the type arguments written, or, where the argument is unknown, with a wildcard, or in a language without wildcards with the type that is consistent with every type, and without any cast the written arguments make unnecessary, in the file's language, `rationale` = the compile-time check the omission turned off, and the cast that may fail at run time or the element the checker no longer checks).
