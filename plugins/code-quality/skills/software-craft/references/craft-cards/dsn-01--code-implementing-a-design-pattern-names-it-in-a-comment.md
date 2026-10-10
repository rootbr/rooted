---
title: Code that implements a design pattern names the pattern in a comment at or listing each type that takes part in it
rule_id: DSN-01
domain: design
step: [implement, refactor, document]
applies_to: [universal]
triggers: ['\b[Aa]ccept\s*\(.*[Vv]isitor', '\b([Gg]et_?[Ii]nstance|[Ii]nstance)\s*\(\s*(cls\s*)?\)', '\b([Aa]dd|[Rr]emove)_?\w*[Ll]istener\s*\(|\b([Ss]ubscribe|[Nn]otify_?\w*)\s*\(', '[.]_?(delegate|wrapped|wrappee|adaptee|inner|component)\b', '\b(class|interface|trait|struct|type)\s+\w*(Factory|Builder|Strategy|Visitor|Decorator|Adapter|Proxy|Observer|Command|Handler|Composite|Facade|Mediator|Bridge|Prototype|Flyweight|Memento)\b', 'signal:added_file']
scope: file
check_kind: semantic
severity_default: suggestion
---

# Code that implements a design pattern names the pattern in a comment at or listing each type that takes part in it

## Thesis
When added code implements one of the lower-level design patterns — a creational pattern (builder, factory, prototype, singleton), a structural pattern (adapter, bridge, composite, decorator, façade, flyweight, proxy) or a behavioral pattern (command, interpreter, iterator, mediator, memento, observer, state, strategy, template method, visitor) — each type that takes part in the pattern instance has the pattern named in a comment at it or in a comment in the same file that lists it among the pattern's participants. A program that is otherwise well commented still carries the pattern comment: the measured benefit was over well-commented programs that made no explicit reference to the patterns.

## Rationale
A pattern is a common solution to a common problem in a given context, and it furnishes an explicit specification of class and object interactions and their underlying intent; a pattern comment names that specification in the source code. Whether naming the pattern helps beyond ordinary comments was tested against well-commented programs without explicit reference to the patterns: in two controlled experiments, subjects performed maintenance tasks on two programs of 360 to 560 lines including comments, and a conservative analysis supported the hypothesis that pattern-relevant maintenance tasks were completed faster or with fewer errors when pattern comment lines provided this redundant design-pattern information. In a family of four controlled experiments with 88 participants, from Bachelor students to professionals, who comprehended a nontrivial chunk of an open-source system, the results indicate that documenting the pattern instances, as comments in the source or as class diagrams, yields an improvement in the correctness of understanding source code for participants with an adequate level of experience. A systematic review of 50 primary studies found that documentation of patterns, the size of pattern classes and the scattering degree of patterns have a clear impact on quality.

## Example
```java
bad:  class CachingStore implements Store {
          private final Store inner;
          CachingStore(Store inner) { this.inner = inner; }
          public String get(String key) { ... } }
good: // Decorator pattern: CachingStore wraps a Store and adds a cache.
      class CachingStore implements Store {
          private final Store inner;
          CachingStore(Store inner) { this.inner = inner; }
          public String get(String key) { ... } }
```

## Limits
The two-experiment study compared pattern comment lines with a well-commented program without explicit reference to design patterns, and the four-experiment family documented the pattern instances as comments in the source or as class diagrams. The rule therefore does not reach a type whose declaration already names the pattern, in its own name (a ShapeVisitor, an OrderFactory) or in the pattern type it implements, extends or takes as a parameter (an accept method taking a ShapeVisitor). Class diagrams of the pattern instances are the other documented form the four-experiment family measured: a project tolerance that records its pattern instances in such diagrams rejects the finding. The documented instances were made of interacting classes and objects; a pattern realized without a type of its own, such as a function value passed where a strategy or command type would stand, adds no participating type and lies outside the rule. The evidence measured the documentation of patterns already in the code, not whether a pattern fits its problem, and the rule asks only for the comment.

## Validator
Read the added lines for the shape of an instance of any pattern the Thesis lists, for example: an accept method that takes a visitor and calls back one of its visit methods; a creation routine or type that decides which implementation of an interface to construct; a type that implements an interface and holds a field of the same interface to which it forwards calls (a decorator or proxy), or holds an object of another interface whose calls it translates into the one it implements (an adapter); an interface with one operation whose implementations are passed in and swapped (a strategy or command); routines that add or remove listeners or subscribers and notify them (an observer); a get-instance routine that returns one shared object (a singleton). Open the file, identify the types that take part in the instance, and for each added one read its declaration, the comment at it and the file's other comments. Skip a type whose name, or the name of the pattern type it implements, extends or takes as a parameter, already names the pattern; skip a type that a comment elsewhere in the file names as a participant of the instance; skip a pattern realized by a function value with no type of its own; check the project context for a tolerance that records pattern instances in class diagrams. Validator question: **Does the change add a type that takes part in an instance of a named design pattern, with the pattern named neither in its declaration, nor in a comment at it, nor in a comment elsewhere in the file that lists it as a participant?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: DSN-01`, severity suggestion, `file`, `symbol`, `code` = the added declaration line of the participating type, `fix` = that declaration preceded by a comment naming the pattern the type takes part in, in the file's language, `rationale` = the pattern recognised and the lines of the instance that show it).
