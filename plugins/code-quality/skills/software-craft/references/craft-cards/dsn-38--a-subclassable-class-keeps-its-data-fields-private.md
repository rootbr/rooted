---
title: A class that can be subclassed keeps its data fields private and gives subclasses its state only through methods
rule_id: DSN-38
domain: design
step: [design, implement, refactor]
applies_to: [object-oriented]
triggers: ['^\s*(@\w+(\([^)]*\))?\s+)*protected\s+(?!((static|final|transient|volatile|readonly|internal|new|override|unsafe|required)\s+)*(static\s+final|final\s+static|static\s+readonly|readonly\s+static|const|abstract|class|interface|enum|record|void)\b)[^(=;:{]*\s\w+\s*(=(?![>=])(?!\s*(async\s+)?(\([^()]*\)|\w+)\s*(:[^=]*)?=>)|;)', '(^\s*(@\w+(\([^)]*\))?\s+)*|[(,]\s*)protected\s+((override|declare)\s+)?(static\s+(?!readonly\b))?((override|declare)\s+)?(readonly\s+)?\w+\s*[?!]?\s*(:|=(?!>))(?!\s*(async\s+)?(\([^()]*\)|\w+)\s*(:[^=]*)?=>)', '\b(self|cls)[.]_[a-z]\w*\b(?!\s*\()']
scope: callers
check_kind: semantic
severity_default: minor
---

# A class that can be subclassed keeps its data fields private and gives subclasses its state only through methods

## Thesis
A class that can be subclassed keeps its data fields private rather than at an access level meant for its subclasses, and a subclass that needs the base class's state reaches it through methods or accessor properties that the base class defines, which may themselves be restricted to subclasses. Constants and class-level read-only fields are exempt. Where visibility is only a naming convention, a subclass reads and writes no non-public data attribute that its base class assigns; it calls a method or a property of the base class instead.

## Rationale
A data field that subclasses can reach has an open set of users: anyone can derive a new class and start reading it and, unless the field is read-only, changing it, and in a large hierarchy its consistent use is hard to maintain, because the code that touches it can be spread over many classes. A field that subclasses can change complicates the statement of the class's invariants, and no invariant over it is enforced; it is much like a global variable. A subclass can freely read it, write it unless it is read-only, and in some languages redeclare it as public. Because the complete set of subclasses often cannot be examined, any change to the class's representation, such as a field's name or type, becomes infeasible; a field can change without breaking code outside the class only when it is private. A private field can carry a well-specified and enforced invariant, and a method that gives subclasses the state, restricted to subclasses where the language has that level, can be just fine. Such a method is still reachable by anyone who subclasses the class, so a class that can be subclassed treats every member it opens to subclasses as public for security, documentation and compatibility, and a class meant for extension decides explicitly which attributes are public, which form its subclass API and which only the class itself uses. Where visibility is only a naming convention, the convention's class-private form mangles the class name into the attribute name, which helps a subclass avoid colliding by accident with a base attribute of the same name.

## Example
```python
bad:  class Cart:
          def __init__(self): self._items = []
      class GiftCart(Cart):
          def add(self, item): self._items.append(item)
good: class Cart:
          def __init__(self): self.__items = []
          def _add_item(self, item): self.__items.append(item)
      class GiftCart(Cart):
          def add(self, item): self._add_item(item)
```

## Limits
Constants and class-level read-only fields are outside the rule, since such fields are almost by definition never required to change. A method or property that gives subclasses the state meets the rule, including one restricted to subclasses. A field open to every caller, or only to code of its own package or module, is outside the rule: the rule concerns the access level meant for subclasses.

A class that the language closes to subclassing has no subclasses, and the rule does not reach its fields. The rule judges a class the codebase defines: a subclass of a class from outside the codebase that reaches a field that class opens to subclasses is outside it, since the fix belongs to that class.

Where visibility is only a naming convention, no attribute is truly private, and a non-public name says only that the attribute is not meant for third parties; whether subclasses may use it is a separate decision. There the convention's ordinary non-public name is its documented form for a non-public instance variable, so the declaration alone does not break the rule; a subclass's direct read or write of a non-public data attribute of its base class does. The convention's guidance for a class meant to be subclassed is to decide explicitly which attributes are public, which form the subclass API and which only the class itself uses, and to consider the class-private form for attributes that subclasses are not to use. That form makes debugging and some dynamic lookups less convenient, so a method or property in front of an ordinary non-public attribute also meets the rule.

A language without implementation inheritance has no type hierarchy and no way, short of a macro, to define a type that inherits another type's fields. The fields of an embedded type act like ordinary fields of the embedding type, reachable under the same visibility rules as from any other code, and a trait's associated items are functions, types and constants, never fields. The rule does not reach such a language.

A project context that allows fields restricted to subclasses, or that lists annotations whose fields are exempt, rejects the finding; tool rules offer both settings.

## Validator
In the hunk, find each data-field declaration at an access level meant for subclasses, and, where visibility is only a naming convention, each read or write of a non-public attribute through the instance or the class. Open the file, and grep the repository for the field's or the attribute's name to find the class that assigns it and the subclasses that read or write it. For a declaration, confirm that the member is a data field, not a method, an accessor property, a nested type or a function-valued member; skip a constant and a class-level read-only field, and skip a class that the language closes to subclassing. For an access by naming convention, find the class that assigns the attribute and confirm that the attribute is a plain data attribute, not a property or a method. Continue when the access sits in a subclass of that class and the codebase defines that class, or when the access sits in that class and a subclass in the codebase reads or writes the attribute directly. Skip what the project context allows: fields restricted to subclasses, or fields carrying an annotation it lists as exempt. Validator question: **Does a class that can be subclassed open a data field, other than a constant or a class-level read-only field, to its subclasses, by declaring it at an access level meant for subclasses or, where visibility is only a naming convention, by a subclass reading or writing a non-public data attribute of its base class directly?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: DSN-38`, severity minor, `file`, `symbol`, `code` = the field declaration, or the subclass's read or write of the base class's field, quoted verbatim from the diff, `fix` = the field made private (where visibility is a naming convention, renamed to the class-private form or left non-public) together with a method or property of the base class that gives subclasses the state they need, and the subclass's access rewritten to call it, in the file's language, `rationale` = the field, the subclasses that can reach it, and the invariant or representation change that its open set of readers and writers takes out of the base class's control).
