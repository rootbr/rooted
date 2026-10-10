---
title: Where the compiler or a static checker reports a match over a closed set of variant types that misses a variant, an operation over the variants is written as a match rather than as a visitor's accept and visit double dispatch
rule_id: DSN-07
domain: design
step: [design, implement, refactor]
applies_to: [universal]
triggers: ['\baccept\s*\(.*[Vv]isitor', '\bvisit_?[A-Z]\w*\s*\(|\bvisit_[a-z]\w*\s*\(', '\b(interface|trait|class|struct|type|impl|implements|extends)\b[^{;]*Visitor\b', '\b(fn|def)\s+visit\w*\s*\(|\bfunc\s+\([^)]*\)\s+Visit\w*\s*\(']
scope: callers
check_kind: semantic
severity_default: minor
---

# Where the compiler or a static checker reports a match over a closed set of variant types that misses a variant, an operation over the variants is written as a match rather than as a visitor's accept and visit double dispatch

## Thesis
When an operation runs over a closed set of variant types declared in one place, and the compiler or a static checker the project runs, a type checker or an exhaustiveness analyzer, reports a match over that set that misses a variant, the operation is written as one match over the variants. Such a set is a sum type, a sealed type whose permitted subtypes are declared with it, or a union of types told apart by class or by a literal tag. The match ends in an arm that asserts the matched value has no variant left, which the checker reports as an error once a variant can reach it, or, where the compiler or checker reports any match over the set that leaves a variant unhandled, has no catch-all arm. The operation is not written as a visitor: an accept method on each variant, a visitor interface that declares one visit method per variant, and the operation as a class that implements that interface. Code that adds this accept and visit machinery for such a set breaks the rule.

## Rationale
A visitor separates an operation from the types it runs over, but only once the types are designed for visitation: every variant carries an accept method, one visitor interface lists a visit method per variant, and each operation is one more visitor class. Such code is bulky, easy to get wrong, annoying to write and annoying to read, and as visitors get more complicated it is common for a single traversal to involve several levels of them. A visitor also selects only on a variant's class, not on the values of its attributes. A match gives the same separation, with the operation independent of the type hierarchy, without the visitor's machinery, and it can also select on attribute values and work directly with built-in types. Where pattern matching is sufficiently powerful, the visitor is almost completely unnecessary. A closed set lets the toolchain check the match: because the permitted variants are declared together, the compiler can enumerate them and analyse a match over them for exhaustiveness and can name the variant a match forgot, and, where the compiler or checker requires every match over the set to handle every variant, adding a variant makes a match with no catch-all arm that does not handle it an error. A catch-all arm forfeits that check, since the compiler can no longer verify that the cases were exhaustively enumerated; a final arm that asserts the value has no type left keeps it, because the checker reports that arm as reachable when a variant is missing. Without the check, a change to the set is easy to miss: when the union or the enumeration changes, it is easy to forget to update the cases. In a controlled maintenance experiment comparing programs designed with and without design patterns, run in a real programming environment with paid professionals from multiple major consultancy companies, the results indicate quite strongly that some patterns are much easier to understand and use than others, and the visitor caused much confusion: patterns are not universally good or bad, and must be used in a way that matches the problem and the people.

## Example
```python
bad:  class Circle:
          def accept(self, visitor): return visitor.visit_circle(self)
      class AreaVisitor:
          def visit_circle(self, c): return math.pi * c.r ** 2
          def visit_square(self, s): return s.side ** 2
good: def area(shape: Shape) -> float:
          match shape:
              case Circle(r=r): return math.pi * r ** 2
              case Square(side=side): return side ** 2
              case _: assert_never(shape)
```

## Limits
- Contested. One side, the design documentation of pattern matching and of exhaustiveness checking in several languages and type checkers, holds that a checked match gives the visitor's separation without its machinery and reports a missed variant. The other side rests on a language that left variant types out because they overlap in confusing ways with interfaces, and that discriminates cases with an interface value and a type switch, and on per-type registration for a set that other code extends. The condition that separates them is whether the set is closed, declared in one place, and checked by the toolchain for a missing case; the rule holds only where all three are true.
- A type switch over an interface value that the compiler does not check for a missing case, one that for a value whose type no case lists executes only the default arm if one is written, meets the condition only where an exhaustiveness analyzer is configured for that interface and the interface is declared to it as a sum type. Without such an analyzer, the rule does not apply.
- Code that no static type checker covers gets no report from an unreachable-assertion arm before it runs, so the condition fails there.
- A set of types that other modules extend is outside the rule. There an operation is a method each type implements or a generic function with one implementation registered per type, since inspecting the received argument's type to decide what to do is brittle and closed to extension, and a user of a library may be unable to change how the library's code treats objects a third party created.
- The rule replaces a visitor and nothing else. Pattern matching does not make inheritance hierarchies and virtual methods wrong, and an operation that is an ideal candidate for including in the hierarchy stays a method on each type.
- A traversal routine that matches each variant and recurses into its children is the matched form the rule asks for, not a visitor: the match supplies the type-driven traversal a visitor offers.

## Validator
Grep the added lines for an accept method that takes a visitor, a visit method named for a variant type, and an interface, trait, class or type that is named as a visitor or implements one. Open the file and name the variant types the visitor dispatches over and the type they share. Search the repository for where that set is declared and for each variant's accept method, and check that the set is closed and declared in one place: a sum type, a sealed type whose permitted subtypes are declared with it, or a union of types told apart by class or by a literal tag. Do not flag a set that other modules extend. Check that the toolchain reports a match over the set that misses a variant, from the language version, the file's type annotations and the type checker or exhaustiveness analyzer the project context names. Do not flag where nothing reports a missed variant, such as a type switch over an interface that the compiler does not check for a missing case and no analyzer is configured for, or code no static type checker covers. Confirm the dispatch is double dispatch, with each variant's accept calling the visit method for its own type, and not a traversal routine that matches each variant, a per-type registration or a method on each variant. Validator question: **Does the change dispatch an operation over a closed set of variant types declared in one place through an accept method on each variant and a visit method per variant type, where the compiler or a static checker the project runs would report a match over that set that misses a variant?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: DSN-07`, severity minor, `file`, `symbol`, `code` = the added accept method, visit method or visitor declaration quoted verbatim from the diff, `fix` = the operation as one function holding a match over the variants, ending in an arm that asserts the matched value has no variant left, which the checker reports as an error once a variant can reach it, or with no catch-all arm only where the compiler or the project's checker reports a match that leaves a variant unhandled, and the accept methods and the visitor interface removed where no unchanged operation still dispatches through them, in the file's language, `rationale` = names the closed variant set and where it is declared, the compiler, type-checker or analyzer check that reports a missed variant, and the accept and visit machinery the match replaces).
