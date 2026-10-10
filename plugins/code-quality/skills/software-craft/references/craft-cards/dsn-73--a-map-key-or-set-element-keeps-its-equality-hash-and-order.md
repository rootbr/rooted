---
title: A hash or ordered map key or set element keeps its equality, hash and ordering unchanged while it is in the collection
rule_id: DSN-73
domain: design
step: [design, implement]
applies_to: [universal]
triggers: ['\b(\w*Hash(Map|Set)|\w*Tree(Map|Set)|ConcurrentSkipList(Map|Set)|(Sorted|Navigable|Index)(Map|Set)|Cell|RefCell)\s*(<|::)|\b(set|frozenset|dict|Set|FrozenSet|Dict|Mapping|MutableMapping|MutableSet|AbstractSet|defaultdict|OrderedDict|Counter)\[', '\b__(hash|eq|lt|le|gt|ge)__\b|\b(unsafe_hash|order)\s*=\s*True|\bhashCode\s*\(|\bboolean\s+equals\s*\(|\bcompareTo\s*\(|\bComparator[.]comparing\w*\s*\(|\bimpl\b[^{;]*?\b(Hash|PartialEq|Eq|PartialOrd|Ord)\s+for\b|#\[derive\([^)]*\b(Hash|Ord)\b']
scope: callers
check_kind: semantic
severity_default: major
---

# A hash or ordered map key or set element keeps its equality, hash and ordering unchanged while it is in the collection

## Thesis
An object held as a key of a hash or ordered map, or as an element of a hash or ordered set, keeps its equality, its hash and its ordering relative to the other keys unchanged for as long as it is in the collection. Every change that alters one of them counts, whether it is made by assignment, through interior mutability, or through global state or input and output that they read. A type meant for use as such a key computes its equality, hash and ordering only from state that does not change.

## Rationale
Hash collections use a key's hash value internally, and hash and ordered collections rely on the hash or the order of their keys being unchanging. A key whose hash changes while it is held is in the wrong hash bucket. Once a held key changes in a way that affects its equality comparisons, or its ordering relative to any other key, the collection's behaviour is not specified; one standard library lists panics, incorrect results, aborts, memory leaks and non-termination among the possible outcomes, confined to the collection that observed the change. One language defines a hashable object as one whose hash value never changes during its lifetime, and its generator of value types states that having a hash implies that the type's instances are immutable. Where a type can leave its hash undefined, a mutable type with value equality does so, and that generator marks a mutable one unhashable, so that its instances cannot become hash keys at all. Keys computed from unchanging state restore the unchanging hash and order the collection relies on.

## Example
```python
bad:  @dataclass(unsafe_hash=True)
      class Cell: ...
      seen: set[Cell] = {cell}
      cell.row += 1
good: @dataclass(frozen=True)
      class Cell: ...
      seen: set[Cell] = {cell}
      seen.remove(cell)
      seen.add(replace(cell, row=cell.row + 1))
```

## Limits
The rule reaches only state that the equality, hash or ordering reads, and of these only the comparisons the holding collection uses: a sorted collection that performs all key comparisons through the ordering or a comparator does not use the keys' equality or hash, and a hash collection that never orders its keys does not use their ordering. A key type may hold other state that changes, and a type with interior mutability is a correct key when its equality, hash and ordering read none of that state. A project may declare in its analyzer configuration the types to treat as free of interior mutability; that declaration is the tolerance that rejects a type-level finding for those types.

A key compared by identity keeps its equality and hash however its contents change. The rule does not reach a collection that discriminates object keys by identity, nor the equality and hash of a type that keeps the default identity-based equality and hash or of a reference key whose equality is the variable it points to; an ordering such a type defines over state that changes stays within the rule wherever an ordered collection uses it. Where assignment copies a value, a key held as such a copy is not the variable it was copied from, and changing that variable changes no key.

The rule governs only the time a key is in a collection: a key removed from every collection that holds it, changed, and inserted again afterwards is outside it.

Mutable objects can serve as keys with great care. Where the project context documents a mutable key type together with a discipline that never changes an instance while it is a key, the type-level part of the finding is rejected; a change made while the key is held is still a finding. A forced hash on a type that is logically immutable but can still be changed, a use the hash generator's documentation calls specialized and not recommended, makes that type such a mutable key type: its type-level finding is rejected only under the documented discipline above, and a change made while an instance is a key is a finding in every case.

## Validator
Grep the hunk for a hash or ordered map or set type, for an added or changed definition of equality, hash or ordering (an equality method, a hash method, a comparison method or comparator, a derived or forced hash), and for a field type with interior mutability. For each key type the hunk defines or changes, list the state its equality, hash and ordering read, including global state and input. Open the callers of the type and find where its instances become keys of a hash or ordered map or elements of a hash or ordered set. Trace what can change that state while an instance is in such a collection: a setter or an assignment to a field the methods read, a mutating call on a component they read, interior mutability, a change to global state or input they read. Where the hunk changes the state of an object, trace whether that object is held as such a key at that point. Set aside state none of the methods read, state that only a comparison the holding collection does not use reads, a key the holding collection compares only by identity or by the variable it points to, a key held as a value copy, a change made after the key has left every collection, a type a project declaration lists as free of interior mutability, and, for the type-level part only, a mutable key type the project context documents with a discipline that never changes a held key. Validator question: **Can state that an object's equality, hash or ordering reads change while the object is a key of a hash or ordered map or an element of a hash or ordered set, through code the hunk adds, or because a key type the hunk defines or changes reads state that its callers can change?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: DSN-73`, severity major, `file`, `symbol`, `code` = the added line that changes the held key's state, that makes state the equality, hash or ordering reads changeable (a setter, a field made assignable, an interior-mutable field), or that defines the equality, hash or ordering over changeable state, quoted verbatim from the diff, `fix` = the key type made unchangeable in the state its equality, hash and ordering read (a frozen or read-only value, a method that returns a changed copy), or the key removed before the change and inserted again after it, in the file's language, `rationale` = the collection that holds the key, the state whose change alters the key's equality, hash or ordering, and the unspecified collection behaviour that follows).
