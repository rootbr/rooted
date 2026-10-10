---
title: A type inherits, embeds or dereferences to another type only when every public member it gains belongs in its own interface, and otherwise holds that type in a field and forwards what it needs
rule_id: DSN-39
domain: design
step: [design, implement]
applies_to: [universal]
triggers: ['\bclass\s+\w+(\s*<[^>]*>)?\s+extends\s+[\w.]+', '^\s*class\s+\w+\s*\(\s*(?!(object|Protocol|ABC|Enum|IntEnum|StrEnum|TypedDict|NamedTuple|Exception|BaseException|\w*Error|\w*TestCase)\s*[,)\[])[A-Za-z_][\w.]*', '^\s+\*?([a-z]\w*[.])?[A-Z]\w*\s*(//.*)?$', '\bimpl(<[^>]*>)?\s+((std|core)::ops::)?Deref(Mut)?(<[^>]*>)?\s+for\b']
scope: callers
check_kind: semantic
severity_default: minor
---

# A type inherits, embeds or dereferences to another type only when every public member it gains belongs in its own interface, and otherwise holds that type in a field and forwards what it needs

## Thesis
A type inherits from a class, embeds another type as an unnamed field, or declares implicit dereference to a wrapped type only when every public member it gains that way is one it would add directly to its own interface. When only some of those members would be added, or none, the type holds the other type in a private field and writes forwarding methods for the members it needs.

## Rationale
Inheritance is often at risk of sharing more code than necessary: a subclass shares all characteristics of its parent class, which can make the design less flexible and introduces the possibility of calling methods on the subclass that make no sense or that cause errors because they do not apply to it. When a type is embedded, its methods become methods of the outer type, and the outer type gains a field named after the embedded type, public when that type is public. A type with implicit dereference implicitly has every method of its target that takes the receiver by shared reference, and because the compiler inserts the dereference implicitly, the declaration is a much larger part of the type's public interface than any other interface the type implements. A gained member can bypass the outer type's own operations: a property list of strings that inherits a general hash table keeps the table's put and putAll, which let callers insert entries whose keys or values are not strings in place of the list's own setter, and storing or saving such a compromised list then fails. An embedded lock grants callers access to the type's internal synchronization, which should not be delegated out to the callers and is a source of bugs. On a public type, an embedded type leaks implementation details, inhibits type evolution and obscures documentation: adding methods to an embedded interface, removing methods from an embedded struct, removing the embedded type, and replacing it, even with an alternative that satisfies the same interface, are each a breaking change, so every future version of the outer type must keep the embedded type. Holding the other type in a field and writing the forwarding methods is tedious, and the effort hides an implementation detail, leaves more opportunities for change, and removes the indirection a reader follows to find the type's full interface in its documentation. Delegation has proven a good alternative to implementation inheritance, and a language can generate the forwarding methods of a delegated interface from one declaration.

## Example
```typescript
bad:  class Registry extends Map<string, Handler> {
        register(name: string, handler: Handler): void { ... }
      }
good: class Registry {
        private readonly handlers = new Map<string, Handler>();
        register(name: string, handler: Handler): void { ... }
        get(name: string): Handler | undefined { return this.handlers.get(name); }
      }
```

## Limits
Where every public member the outer type gains, the field an embedded type adds among them, belongs in its interface, the rule does not fire, and inheriting, embedding or dereferencing saves the forwarding bookkeeping: a buffered reader-writer that embeds a buffered reader and a buffered writer has the methods of both, except the few that both declare, and satisfies the reader, writer and reader-writer interfaces, and a wrapper meant to have every method of its inner type can dereference to it. An interface built by embedding other interfaces is the union of the embedded interfaces and meets the condition. The guidance divides over embedding and dereference for convenience. One side treats embedding as a simple convenience, as when a job type embeds a logger so that the job has the logger's print methods, and holds that implicit dereference should in general be implemented when a value of the type transparently behaves like a value of the target type, the dereference is cheap, and users will not be surprised by it. The other side holds that embedding should not be purely cosmetic or convenience-oriented, expose unrelated functions or fields, or let users observe or control the type's internals, and that implicit dereference should be used for smart pointers only, because the rules it interacts with were designed specifically to accommodate them. The separating condition is the member test: would all of the exported inner members, and for an embedded type the field named after it, be added directly to the outer type. When the answer is all, embedding or dereferencing passes; when it is some or none, it is the finding and a field takes its place. For dereference, the mechanism's own documentation adds two cases that fail: a type whose methods are likely to collide with the target's, and a type for which committing to the dereference as part of its public interface is not desirable. A lock is not embedded, even in a private type. The breaking-change cost falls on a public outer type; on a private one, the finding rests on a gained member that does not apply, bypasses the type's own operations or exposes its internals. Whether a subtype keeps the base type's pre- and postconditions, the depth and breadth of a hierarchy, a base class whose change breaks subclasses through self-use, and whether a class is designed for extension are outside this rule.

## Validator
Grep the hunk for a class that extends another class or names a base class, an unnamed embedded field in a struct, or a declaration of implicit dereference to a wrapped type. Open the declaration of the inherited, embedded or target type and list its public members; for an embedded type, note the field it adds. Open the outer type's declaration and documentation to read the interface it presents. Search the outer type's callers for calls to gained members, and note any call that bypasses one of the outer type's own operations. For each gained public member, decide whether the outer type would add it directly: a member that does not apply to the outer type, that the outer type overrides to refuse, that bypasses its own validation or invariant, or that exposes its lock or other internals would not be. Skip an interface built from other interfaces, a type whose documentation says it presents every member of the other type, and each exemption in Limits. Validator question: **Does the outer type gain, through inheritance, embedding or implicit dereference, a public member it would not add directly to its own interface?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: DSN-39`, severity minor, `file`, `symbol`, `code` = the extends clause, base-class list, embedded field or dereference declaration quoted verbatim from the diff, `fix` = the outer type holding the other type in a private field with forwarding methods for only the members it needs, in the file's language, `rationale` = the gained public members that do not belong in the outer type's interface and the bypassed operation, broken invariant or exposed internal each one opens to callers).
