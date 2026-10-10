---
title: A component that keeps a mutable object received from a caller keeps its own copy or takes ownership of it
rule_id: DSN-70
domain: design
step: [design, implement]
applies_to: [universal]
triggers: ['^\s*(this|self|[a-z]\w*)[.]_?\w+\s*=\s*[a-z_]\w*\s*;?\s*$', '(^|[{,])\s*\w+\s*:\s*[a-z_]\w*\s*(,\s*$|[,}])']
scope: file
check_kind: semantic
severity_default: major
---

# A component that keeps a mutable object received from a caller keeps its own copy or takes ownership of it

## Thesis
A constructor, setter or other routine that keeps a mutable object its caller passed in — an array, a slice, a list, a set, a map, a mutable date — in a field, a static or other state that outlives the call stores a copy of that object, or takes the object over in a form the language enforces, such as a move after which the caller's variable is no longer valid. Changes the caller makes afterwards through its own reference then do not affect the component's state. The rule holds where a change the component did not make to the stored contents could compromise security or another important property of the component, such as the validity of contents it checked on receipt. It does not govern a routine whose documented purpose is to wrap, share, write into or take over the caller's object.

## Rationale
Storing a received array, slice, collection or map that has reference semantics stores a reference to the caller's object, not a copy of it: assignment creates a binding to an object rather than copying it, and a slice assigned to another refers to the same underlying array. An array the language treats as a value arrives as a copy already: assigning it copies all its elements, and a routine it is passed to receives a copy, not a pointer to it. The component's field and the caller's variable then name one object, so a later change through the caller's reference reaches the component's state unchecked and unexpected — contents that passed validation and security checks on arrival can change before the component uses them. In interviews, professional developers stated that incorrect state mutations are a major source of bugs, for example an object thought to be immutable changed by some other object because references were reused instead of immutable copies. A copy made on receipt separates the two: the caller can go on changing its own object, and the copy does not reflect those modifications. A move gives the same separation without copying the data: passing a value to a routine moves or copies it just as assignment does, and after a move the caller's variable is no longer valid. A routine that needs ownership of its argument takes ownership of it rather than borrowing it and cloning it. A read-only view or a read-only type over the caller's object is not a copy: changes to the backing collection stay visible through an unmodifiable view, and read-only properties can still change through another reference to the same object. A shallow copy of a container holds references to the objects found in the original, so where those elements are themselves mutable the copy's contents can still appear to change; where the component relies on the elements' state, a deep copy duplicates them as well.

## Example
```go
bad:  func NewRegistry(items []Item) *Registry { return &Registry{items: items} }
      func (r *Registry) SetItems(items []Item) {
          r.items = items
      }
good: func NewRegistry(items []Item) *Registry { return &Registry{items: slices.Clone(items)} }
      func (r *Registry) SetItems(items []Item) {
          r.items = slices.Clone(items)
      }
```

## Limits
Storing the caller's object is the design where the routine's documentation says it wraps, shares, writes into or takes over that object: a fixed-size list backed by the caller's array, with changes to either visible in the other, or a buffer that takes ownership of the caller's bytes and tells the caller not to use them after the call. A project context that documents such a hand-over for a family of routines rejects the finding for them. No copy is needed where the caller cannot change the object while the component holds it: an immutable value such as a string, an unmodifiable collection that is not a view onto a modifiable one and whose elements are themselves immutable, or a borrow during which the compiler allows no mutable reference to the same value. A handle that gives a value multiple owners together with interior mutability lifts that guarantee, since each owner can then mutate the value. A private helper that receives only objects the component already copied or created needs no second copy; the copy belongs at the routine a caller outside the component reaches. A deep copy can copy too much, such as data intended to be shared between copies, so the elements are copied only where the component relies on their state. The rule judges what a component keeps from a caller; returning the component's own mutable state, changing an argument the routine does not keep, and coordinating state that threads share are judged by their own rules.

## Validator
Grep the added lines for a field, static or struct member assigned straight from a parameter (`this.x = x`, `self._x = x`, `r.x = x`, `x: x` in a literal), for a setter taking a collection, array or date, and for a record, data class or constructor parameter property whose fields are filled from the parameters with no body. Open the file and read the parameter's declared or inferred type: keep an array, slice, list, set, map, mutable date or other mutable object, and drop an immutable value such as a string or an immutable date, an unmodifiable collection that is no view onto a modifiable one and holds immutable elements, an array the language passes by value and so copies on the call, a value the language moves into the component, and a borrow the compiler holds against the caller's writes. Keep the routine where a caller outside the component reaches it: a public, exported or package-visible routine, or a private helper that such a routine passes its own parameter to. Trace the stored object back to the parameter: look for a copy into fresh storage before the assignment — a clone or copy call, a copy constructor, a new collection built from the argument, a spread into a new literal — and count a read-only view or a read-only type over the argument as no copy. Name what the component relies on in the stored contents: a check it ran on receipt, state it derives from them, answers it gives its own callers from them; where it relies on the state of mutable elements, look for the elements' copies too. Skip a routine whose documentation or the project context says that it wraps, shares, writes into or takes ownership of the argument. Validator question: **Does an added line keep, in state that outlives the call, a mutable object received from a caller outside the component, neither copied nor taken over by an enforced move, where a later change by the caller could compromise a property the component relies on and no documented contract makes sharing the object the routine's purpose?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: DSN-70`, severity major, `file`, `symbol`, `code` = the assignment, literal field or declaration that stores the received object, verbatim from the diff, `fix` = that line in the file's language storing a copy of the argument — an unmodifiable copy where the field never changes, with mutable elements the component relies on copied too — or taking the argument by value as a move where the language enforces one, `rationale` = the received object, the caller's reference that still reaches it, and the check or property of the component that a later change through that reference would bypass).
