---
title: A class extends another class only when its instances behave as the base type wherever a base-type reference is used, and otherwise holds an instance of it in a field
rule_id: DSN-40
domain: design
step: [design]
applies_to: [object-oriented]
triggers: ['\bclass\s+\w+(\s*<.*>)?\s+extends\s+[\w.]+', '^\s*class\s+\w+\s*\(\s*((?!(object|Protocol|ABC|Enum|IntEnum|StrEnum|TypedDict|NamedTuple)\s*[,)\[])[A-Za-z_][\w.]*|$)', '\bboolean\s+equals\s*\(|\bdef\s+__eq__\s*\(|\bequals\s*\(\s*\w+\s*:', '^\s*\*?(?!(None|Some|Ok|Err|Self|True|False)\s*$)(\w+[.])?[A-Z]\w*(\[[^\]]*\])?\s*(`[^`]*`)?\s*(//.*)?$', '\bimpl\b[^{]*\bDeref(Mut)?\b[^{]*\bfor\b']
scope: callers
check_kind: semantic
severity_default: major
---

# A class extends another class only when its instances behave as the base type wherever a base-type reference is used, and otherwise holds an instance of it in a field

## Thesis
A class extends another class only when it is a kind of the base: every routine it inherits applies to it, no value an inherited routine accepts breaks the class's own rules, and an instance held through a base-type reference behaves as a base instance, equality included. A class that wants only the base's code holds an instance of the base in a field and forwards the routines it offers. Where a type reuses another by embedding it or by an automatic dereference to it, the same test decides: the outer type embeds or dereferences only when every method it gains applies to it as it does to the inner type, and otherwise keeps the inner value in a named field.

## Rationale
Inheritance lets a child type be used in the same places as the parent type, and code commonly refers to a subclass instance through a base-class reference; a subtype relation should ensure that any property proved about base objects also holds for subclass objects. A standard library's timestamp class extends its date class while its equality never returns true for an object that is not a timestamp, so the two equalities are not symmetric; the library's documentation recommends that code not view a timestamp as a date and calls the relationship implementation inheritance, not type inheritance. Such a class passes the type checker, which compares the subclass's signatures with the base's and rejects, for example, an override that requires a parameter the base routine does not take. The same library's property table, whose keys and values are strings, extends a general hash table; the inherited put routines let a caller insert keys or values that are not strings, and saving the table then fails. Inheritance makes a subclass share every characteristic of its parent, so callers can reach routines that make no sense for the subclass or cause errors because they do not apply to it; a base whose routines most subclasses cannot implement well becomes an implementation burden, and its users cannot rely on a member performing a meaningful operation, since it might throw instead. A field holding the reused instance gives the class only the routines it forwards, and only the interfaces those routines satisfy. Embedding a type in another is analogous, though not identical, to subclassing: it borrows pieces of an implementation, the inner type's methods become methods of the outer type, and the outer type then satisfies every interface those methods satisfy, though a promoted method runs on the inner value, not the outer one. An automatic dereference gives a wrapper every method of the inner type that takes the inner value by shared reference, and a reference to the wrapper coerces to a reference to the inner type. Both expose the inner type's operations as inheritance does.

## Example
```go
bad:  type Stack struct {
          list.List // promotes PushFront, InsertBefore, Remove
      }
good: type Stack struct {
          items list.List
      }
      func (s *Stack) Push(v any) { s.items.PushBack(v) }
      func (s *Stack) Pop() any { if e := s.items.Back(); e != nil { return s.items.Remove(e) }; return nil }
```

## Limits
Extension passes for a hierarchy that represents a concept with inherent hierarchical structure, where the idea the base represents exactly matches every derived type, as with user-interface elements that each render and buttons that each respond to a click. A data member does not do when the class has to override a routine the base declares overridable or reach a member the base keeps for subclasses; the class then extends the base, and it still has to be a kind of the base for code that holds it through a base-type reference. An embedding whose gained methods all apply to the outer type passes, such as a logger embedded so that the outer value can log; an interface embedded in an interface only unions method sets and is outside the rule. An automatic dereference passes where a value of the type transparently behaves like a value of the target type, the dereference is cheap, and no user is surprised by the coercion, as with a smart pointer. Implementing an interface or a trait inherits no base fields, so the choice between extending and holding a field does not arise there. This rule judges whether a type should extend, embed or dereference at all, and its fix is a field; how an override should be rewritten to keep the documented preconditions and postconditions of the routine it replaces is a contract question this rule does not judge, and neither are the depth of a hierarchy nor a base class that calls its own overridable routines. A tolerance in the project context that permits a named subclass rejects the finding.


An override that refuses an operation its base type's documentation marks optional, by throwing the unsupported-operation error that documentation directs, keeps the base's contract and is outside the rule.
## Validator
Grep the added lines for a class declared with an extends clause or a base-class list, a field declared by a bare type name, which embeds that type, an automatic-dereference implementation, and an equality routine; keep an equality routine only where its class has a base class other than the root object type. Open the class and its base, and list the routines the class overrides and the public routines it inherits unchanged. Look for an override that only throws, does nothing, or gives an inherited routine a different effect; an equality that answers differently from the base's for the same pair, such as one that never equals a base instance; and an inherited public routine that accepts a value or performs an operation the class's own rules forbid, so that a later routine of the class fails. For an embedding or a dereference, list the methods the outer type gains and look for one that does not apply to it or lets a caller break its rules, such as an insert in the middle of a type that pushes and pops at one end. Search the repository for usages of the new type: an instance passed to a base-type parameter, stored in a base-typed variable or collection, or held through an interface the gained methods satisfy, and note the first such caller. Skip a hierarchy whose base idea matches every derived type, an embedding whose gained methods all apply, an interface embedded in an interface, a smart-pointer dereference, and a subclass the project context permits. Validator question: **Does an added extension, embedding or dereference give a type the routines of another type of which it is not a kind, so that an inherited or gained routine does not apply to it, accepts a value that breaks its rules, or behaves differently from the base, equality included, when reached through a base-type reference?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: DSN-40`, severity major, `file`, `symbol`, `code` = the added line that extends, embeds or dereferences, and the signature line of the overriding or equality routine where the diff adds one, verbatim, `fix` = the type rewritten in the file's language to hold the base or inner value in a named field and forward only the routines it offers, `rationale` = names the inherited or gained routine that does not apply, accepts a value that breaks the type's rules or behaves differently from the base, and the caller or base-type reference through which code reaches it).
