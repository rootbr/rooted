---
title: A class name is a noun phrase in UpperCamelCase and a method name a verb phrase in lowerCamelCase, with no prefix or suffix encoding
rule_id: MNT-03
domain: maintainability
triggers: ['^\s*(public|protected|private|static|final|abstract|\s)*(class|interface|enum|record)\s+\w+', '^\s*(public|protected|private|static|final|abstract|synchronized|\s)*[\w<>\[\], ?]+\s+\w+\s*\(', '\b[a-z]\w*_\w*\s*[;=(]', '\b(m|s|k)_?[A-Z]\w*', 'interface\s+I[A-Z]']
scope: hunk
check_kind: mechanical
severity_default: suggestion
---

# A class name is a noun phrase in UpperCamelCase and a method name a verb phrase in lowerCamelCase, with no prefix or suffix encoding

## Thesis
A type added in the diff is named in `UpperCamelCase`, typically with a noun or noun phrase; a method in `lowerCamelCase`, typically with a verb or verb phrase; fields, parameters and locals in `lowerCamelCase`; and no identifier carries a Hungarian, member or interface prefix or suffix such as `mName`, `s_name`, `name_` or `IRepository`.

## Rationale
Case tells the reader the kind of thing a name denotes before its declaration is found — a type, a member, a constant — and a verb on a method separates doing from being: `sendMessage` acts, `Message` is. A prefix repeats what the compiler already knows and moves the meaningful part of the name off its first letter, which is where the eye and the completion list sort it. One convention across the codebase means a name is searchable in one spelling.

## Example
```java
bad:  public class process_order { private List<Item> m_items; public Order Order(Cart c) { ... } }
      public interface IPaymentGateway { }
good: public class OrderProcessor { private List<Item> items; public Order process(Cart cart) { ... } }
      public interface PaymentGateway { }
```

## Limits
A name dictated by an external contract — a JNI symbol, a JSON property mapped by annotation, an overridden method of a library type — keeps its spelling. A JUnit test method may use underscores between logical parts (`transferMoney_deductsFromSource`). A style declared in the project context (a Checkstyle configuration, a different convention) replaces this one. A loop index such as `i` is not in scope. An interface may be named with an adjective or adjective phrase (`Readable`, `Comparable`) instead of a noun.

## Validator
On the triggered hunk read each added type, method, field, parameter and local declaration. Check the case shape (UpperCamelCase type, lowerCamelCase member), the part of speech (typically a noun for a type and a verb for a method — an accessor `size()` or a boolean `isEmpty()` counts as a verb phrase, and an adjective-phrase interface name is within convention), and the absence of prefixes or suffixes. Validator question: **does this declaration break the case shape, the noun-or-verb shape, or carry a prefix or suffix encoding?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: MNT-03`, severity suggestion, `file`, `symbol`, `code` = the declaration quoted verbatim from the diff, `fix` = the renamed declaration, `rationale` naming the convention broken).

## Source
Google Java Style Guide §5.1 "Rules common to all identifiers" — "special prefixes or suffixes are not used. For example, these names are not Google Style: name_, mName, s_name and kName"; §5.2.2 "Class names are written in UpperCamelCase. Class names are typically nouns or noun phrases"; §5.2.3 "Method names are written in lowerCamelCase. Method names are typically verbs or verb phrases"; §5.2.5–5.2.7 non-constant fields, parameters and locals in lowerCamelCase.
