---
title: A field that every method using it assigns before first reading it is replaced by a local variable in those methods, since its value never carries from one call to the next
rule_id: CHG-07
domain: change
step: [implement, refactor, review]
applies_to: [object-oriented]
triggers: ['\b(?:self|this)[.]_?[a-z]\w*\s*=(?!=)', '^\s*private\s+(?!static\b|final\b|readonly\b)(?:(?:transient|volatile)\s+)?[\w<>\[\],.?]+(?:\s+[\w<>\[\],.?]+)*\s+[a-z]\w*\s*;', '^\s*(?:private\s+(?!readonly\b)|#)[a-z]\w*\s*[?!]?\s*(?::\s*[^=;]+)?;', '^\s*[a-z]{1,3}[.][a-z]\w*\s*=(?!=)']
scope: callers
check_kind: semantic
severity_default: minor
---

# A field that every method using it assigns before first reading it is replaced by a local variable in those methods, since its value never carries from one call to the next

## Thesis
A field that every method using it assigns before its first read is replaced by a local variable in each of those methods. The value the field held before a call is never observed, so the object need not store it. The rule covers fields whose every use lies in the type's own code, such as private fields.

## Rationale
When each method that uses the field writes it before reading it, every read sees a value written earlier in the same call, so no call depends on what a previous call left in the field. The field then stores a value that no later call reads, and, provided no other code assigns the field between a method's assignment and its read, a local variable in each method holds the same value for the one call that uses it. The check belongs to a starter rule set described as holding the rules most likely to apply everywhere.

## Example
```rust
bad:  struct Report { total: u64 }
      impl Report {
          fn sum(&mut self, xs: &[u64]) -> u64 { self.total = xs.iter().sum(); self.total }
      }
good: struct Report;
      impl Report {
          fn sum(&self, xs: &[u64]) -> u64 { let total: u64 = xs.iter().sum(); total }
      }
```

## Limits
A field that any method reads before assigning it carries a value between calls and is outside the rule, as is the usual field set in a constructor and read by later methods. A field with a use outside the type's own methods, a public or exported field whose uses the review cannot all see, and a field captured by a closure or a nested type or carrying an annotation that generated accessors or a framework rely on are outside the rule; where a field's visibility spans its module or package rather than the type alone, its uses are searched across that scope. A field of a type whose values are compared, hashed, printed or serialized as a whole — through a derive, decorator or type-level annotation that generates that code, or through built-in structural equality or formatting — is outside the rule, since that code reads the field without naming it. A field that other code may assign while a method sits between its own assignment and a later read — a method of the same object that it calls, a callback it triggers, or code running concurrently — carries that code's value into the read and is outside the rule.

## Validator
Grep the hunk for an assignment to a field through the receiver and for a newly declared mutable private field. Open the type in the file and list every method, constructor and initializer that reads or writes that field. Trace each one: on every path, is the first use an assignment? Between that assignment and each later read, look for a call to another method of the same object, or a call that hands the object to other code, that may assign the field, and set the field aside when one exists. Search the scope the field's visibility spans — the type, or its whole file, module or package — and set aside a field used there outside the type's own methods, a public or exported field, and a field captured by a closure or nested type, assigned or read by concurrently running code, or carrying an annotation that generated accessors or a framework use. Set aside a field of a type that carries a derive, decorator or type-level annotation generating equality, hashing, formatting, serialization or accessors, and a field of a type whose values that scope compares with built-in equality, prints whole or serializes. In a type whose attributes come into being on first assignment, start from an attribute first assigned outside the constructor. Validator question: **Does every method that uses this field, all of whose uses lie in the type's own code, assign it before its first read?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: CHG-07`, severity minor, `file`, `symbol`, `code` = the added line that matched — the field's declaration, or the assignment that precedes its first read in one method — quoted verbatim from the diff, `fix` = the field removed and a local variable declared at that assignment in each method that used it, in the file's language, `rationale` = names that every method using the field assigns it before reading it, so no call observes the value an earlier call left).

## Source
- PMD 7 Java rule SingularField (since 3.1), pmd/pmd main pmd-java/src/main/resources/category/java/design.xml — "in every method where the field is used, it is assigned before it is first read. Hence, the value that the field had before the method call may not be observed, so it might as well not be stored in the enclosing object"; "We can only check private fields"; "The rule is not aware of threading, so it may cause false positives in concurrent code. Such FPs are best handled by suppression" (fetched)
- PMD 7 SingularFieldRule.java, pmd/pmd main pmd-java/src/main/java/net/sourceforge/pmd/lang/java/rule/design/SingularFieldRule.java — "the field is singular if it is used as a local var in every method"; "They're valid if they don't escape the scope of their method, eg by being in a nested class or lambda"; ignored annotations by default "lombok.Setter", "lombok.Getter", "java.lang.Deprecated", "lombok.experimental.Delegate", "javafx.fxml.FXML"; type annotations that make the rule skip the whole type "lombok.Builder", "lombok.EqualsAndHashCode", "lombok.Getter", "lombok.Setter", "lombok.Data", "lombok.Value" (fetched)
- PMD 7 rulesets/java/quickstart.xml — "Includes the rules that are most likely to apply everywhere", with `<rule ref="category/java/design.xml/SingularField"/>` (fetched)
- PMD 7 SingularField test suite, pmd/pmd main pmd-java/src/test/resources/net/sourceforge/pmd/lang/java/rule/design/xml/SingularField.xml — the disabled test "SingularField false-positive with field used concurrently": "This is disabled because it looks legit to the rule, we can't know that doLoop is used concurrently." (runLoop assigns doLoop = true, calls the overridable onEvent and reads doLoop; stopLoop assigns doLoop = false) (fetched)
- PMD 7 DataflowPass.java, pmd/pmd main pmd-java/src/main/java/net/sourceforge/pmd/lang/java/rule/internal/DataflowPass.java — "For unknown method calls, we don't know if the existing reaching defs were killed or not. In that case we just add an unbound entry to the existing reaching def set." (fetched)
- The Rust Reference, rust-lang/reference master src/visibility-and-privacy.md — "If an item is private, it may be accessed by the current module and its descendants." (fetched)
- The Go Programming Language Specification, golang/go master doc/go_spec.html, Exported identifiers — "An identifier may be exported to permit access to it from another package." (fetched)
- The Rust Reference, rust-lang/reference master src/attributes/derive.md — "The derive attribute invokes one or more derive macros, allowing new items to be automatically generated for data structures." (fetched)
- The Go Programming Language Specification, golang/go master doc/go_spec.html, Comparison operators — "Struct types are comparable if all their field types are comparable. Two struct values are equal if their corresponding non-blank field values are equal." (fetched)
- Python tutorial, Classes, python/cpython main Doc/tutorial/classes.rst — “"Private" instance variables that cannot be accessed except from inside an object don't exist in Python.” (fetched)
- Pylint W0201 attribute-defined-outside-init, pylint-dev/pylint main pylint/checkers/classes/class_checker.py — "Used when an instance attribute is defined outside the __init__ method." (fetched)
- Caveat: the evidence is a static-analysis rule for one language plus a detection cue in another; none of these sources measures the pattern's effect on maintenance effort.
