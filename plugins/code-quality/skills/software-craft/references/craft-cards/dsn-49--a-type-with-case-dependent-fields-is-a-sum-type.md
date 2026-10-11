---
title: A type whose fields are valid only in some of its cases, told apart by a kind tag or by which level of a doubly optional value is set, is a sum type in which each case carries exactly the fields it requires
rule_id: DSN-49
domain: design
step: [design, implement, refactor]
applies_to: [universal]
triggers: ['\b(?:kind|type|tag|variant|status|Kind|Type|Tag|Variant|Status)\s*:\s*(?:string|str|["'']|[A-Z]\w*)|^\s*(?:[Kk]ind|Type|[Tt]ag|[Vv]ariant|[Ss]tatus)\s+\w|\b(?:\w*(?:Kind|Type|Tag|Variant|Status)|String|string|int)\s+(?:kind|type|tag|variant|status)\b', ':\s*Optional\[|\|\s*(?:None|null|undefined)\b|\bOption<|\bOptional<|@Nullable\b|\b\w+\?\s*:\s*[\w\["'']|^\s*\w+\s+\*(?:string|int\w*|uint\w*|float\w*|bool|time[.]Time)\b']
scope: file
check_kind: semantic
severity_default: minor
---

# A type whose fields are valid only in some of its cases, told apart by a kind tag or by which level of a doubly optional value is set, is a sum type in which each case carries exactly the fields it requires

## Thesis
A type that holds a kind tag beside optional or nullable fields, some of which are meaningful only for some values of the tag, is declared as a sum type: a discriminated union, an enumeration whose variants carry data, or a closed set of subtypes. The sum type has one case per valid shape, and each case declares as required exactly the fields that shape has. A doubly optional value whose three states (a value, an inner absence, an outer absence) are distinct cases is declared as an enumeration with a clearly named case for each. The rule reaches fields whose presence follows the case, not optional fields that may be set or unset in any combination.

## Rationale
When the case is a tag beside optional fields, the checker has no way to know from the tag whether a field is present. Where absent values are checked, code that has tested the tag still has to convince the checker, with a presence assertion, that the field it reads is present, and such assertions are error-prone once code is moved. Where absent values are not checked, an optional field is assumed present on every read. With one case per shape, testing the tag narrows the value to that case. Reading a field that only another case has is an error whether or not absent values are checked. Each case can carry different types and amounts of data, which a single record with one set of fields cannot. In a type system with sum types, a value of the sum type is one of its cases, and building a case without one of its fields is an error the checker reports. So a value that lacks a field its case requires cannot be built. Case analysis over a sum type can be checked for completeness: the checker reports a match that leaves a case unhandled, and after a case is added it reports each analysis that does not yet handle it. A doubly optional value is logically one optional value with an unneeded extra level of wrapping; where its three states are distinct cases, an enumeration gives each a clear name.

## Example
```rust
bad:  struct Payment { kind: Kind, receipt: Option<String>, reason: Option<String> }
      let p = Payment { kind: Kind::Refunded, receipt: None, reason: None };
good: enum Payment {
          Pending,
          Paid { receipt: String },
          Refunded { receipt: String, reason: String },
      }
      let p = Payment::Refunded { receipt, reason };
```

## Limits
Optional fields that may be set or unset in any combination, every combination valid, stay optional; the rule reaches only fields whose presence follows the case. A doubly optional value whose inner and outer absence mean the same thing is one optional value with an unneeded extra level of wrapping: it calls for dropping a level, not for an enumeration, and is not this rule's finding. Where the language has no sum types but an interface can be closed by an unexported method, the usual stand-in is such an interface, each case a type in the same package that implements it, with case analysis done by a type switch. That keeps the set of cases closed at compile time, but the type system is not aware of the set, so it cannot tell whether a case analysis is complete. The stand-in also does not make a missing field an error: a literal that names its fields may leave out a field, which then takes its zero value, and a variable of the interface type may hold no case at all. A sum-type linter adds the check: it reports a type switch that neither handles every case nor has a default clause. A tolerance the project context states for a named type rejects the finding.

## Validator
In the hunk, find each added or changed type declaration that holds a tag field — a field whose value names the case, such as one named kind, type, tag, variant or status — beside optional or nullable fields, or a doubly optional field. Open the file and read the type's declaration, the code that builds its values and the code that reads its optional fields. For each optional or nullable field, trace whether its presence follows the case: a branch on the tag that then asserts, unwraps or tests the field before reading it; a constructor or factory that sets the field for some tag values and leaves it absent for others; a comment, a validation or an error saying that the field is required for one value of the tag. For a doubly optional field, trace whether code treats the inner absence differently from the outer one. Skip optional fields that may be set in any combination, a doubly optional field whose two absences are handled alike, and a type the project context names in a tolerance. Validator question: **Does the type hold, beside a tag field, optional or nullable fields whose presence follows the tag's value, or a doubly optional field whose levels of absence are distinct cases?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: DSN-49`, severity minor, `file`, `symbol`, `code` = the tag field and the optional or nullable fields whose presence follows it, or the doubly optional field, quoted verbatim from the diff, `fix` = the sum type with one case per valid shape and each case declaring its fields as required, or, where the language has no sum types but an interface can be closed by an unexported method, such a closed interface with one implementing type per case, in the file's language, `rationale` = which field is meaningful only in which case, and the presence assertion the flat type forces on its readers or, where the fix is a sum type, the invalid value the flat type lets be built).

## Source
- TypeScript Handbook, "Narrowing" § Discriminated unions — "the type-checker doesn't have any way to know whether or not `radius` or `sideLength` are present based on the `kind` property"; "We had to shout a bit at the type-checker with those non-null assertions (`!`) to convince it that `shape.radius` was defined, but those assertions are error-prone if we start to move code around."; "`radius` and `sideLength` are declared as required properties in their respective types"; "That narrowed `shape` down to the type `Circle`."; "optional properties are just assumed to always be present when reading them"; "When `radius` was optional, we got an error (with `strictNullChecks` enabled) because TypeScript couldn't tell whether the property was present."; "only the union encoding of `Shape` will cause an error regardless of how `strictNullChecks` is configured"; § Exhaustiveness checking — "Adding a new member to the `Shape` union, will cause a TypeScript error" (fetched)
- TypeScript Handbook, "Type Compatibility" — "the compiler checks each property of `pet` to find a corresponding compatible property in `dog`"; "Object Types" § Optional Properties — "We can choose to provide either of them, so every call [in the handbook's example] to `paintShape` is valid." (fetched)
- The Rust Programming Language, ch. 6.1 "Defining an Enum" — "Rather than an enum inside a struct, we can put data directly into each enum variant."; "Each variant can have different types and amounts of associated data. [...] we wouldn’t be able to with a struct."; ch. 6.2 § Matches Are Exhaustive — "We must exhaust every last possibility in order for the code to be valid." (fetched)
- rustc error index E0063 — "A struct's or struct-like enum variant's field was not provided." (fetched)
- clippy `option_option` (pedantic) — "This is logically the same thing as an optional value but has an unneeded extra level of wrapping. If you have a case where `Some(Some(_))`, `Some(None)` and `None` are distinct cases, consider a custom `enum` instead, with clear names for each case." (fetched)
- mypy documentation, "Literal types" § Tagged unions — "you can discriminate between each kind of TypedDict by checking the label"; "This feature is sometimes called "sum types" or "discriminated union types" in other programming languages." (fetched)
- Go FAQ, "Why does Go not have variant types?" — "a value might take one of a set of other types, but only those types"; "easy to express using an interface value to hold the error and a type switch to discriminate cases" (fetched)
- go-check-sumtype README (golangci-lint `gochecksumtype`), § Details and motivation — "In type systems that support sum types, the language will guarantee that if one has a sum type `T`, then its value must be one of its variants."; "use an interface with an unexported method and define each variant of the sum type in the same package to satisfy said interface. This guarantees that the set of types that satisfy the interface is closed at compile time."; "Go's type system is not aware of the set of variants, so it cannot tell you whether case analysis over a sum type is complete or not."; § Usage — "Adding either a `default` clause or a clause to handle `*VariantB` will cause exhaustive checks to pass." (fetched)
- Go language specification, "Composite literals" (struct literals with keys) — "The element list does not need to have an element for each struct field. Omitted fields get the zero value for that field."; "Interface types" — "The value of an uninitialized variable of interface type is nil." (fetched)
- Caveat: each source documents its own language's or tool's mechanism and none measures the cost of the flat encoding, so the rule rests on what the checker can and cannot verify.
