---
title: The old name kept for a moved or renamed type during a migration is an alias of the new type rather than a separate type that copies, wraps or extends it
rule_id: CHG-26
domain: change
step: [implement, refactor, review]
applies_to: [universal]
triggers: ['^\s*type\s+\w+\s+\*?[a-z]\w*[.][A-Z]\w*\s*$', '^\s*class\s+\w+\s*\(\s*[\w.]+\s*\)\s*:\s*(?:pass|[.][.][.])?\s*(?:#.*)?$', '\bclass\s+\w+\s+extends\s+[\w.]+(?:<[^>]*>)?\s*\{\s*\}?\s*$', '^\s*pub\s+struct\s+\w+\s*\(\s*pub\s+[\w:<>]+\s*\)\s*;', '@[Dd]eprecated\b|#\[deprecated\b|//\s*Deprecated:']
scope: file
check_kind: mechanical
severity_default: major
---

# The old name kept for a moved or renamed type during a migration is an alias of the new type rather than a separate type that copies, wraps or extends it

## Thesis
When a migration moves or renames a type and keeps the old name for callers not yet migrated, the old name is declared with the language's alias mechanism (a type alias, a public re-export or a second binding of the same class) binding it in every role its callers use, as a type and, where they construct or test values through it, as the value, so that the old and the new name denote identical types and code referring to the old name interoperates with code referring to the new name in both directions.

## Rationale
In a large refactoring it is important to support a transition period in which the type is available from both the old and the new location and references to old and new can be mixed and interoperate. An alias declaration binds the old identifier to the given type: after it, the two names are identical types, and using the alias is exactly as if the aliased type had been written, so a value made through either name matches a parameter, a type switch or a type assertion written with the other. Where a declaration creates both a type and a value, as a class or a tuple struct can, a type alias binds only the type: a type alias of a tuple or unit struct cannot qualify that type's constructor, while a re-export of the struct can, so an alias that binds only the type leaves a construction or an instance test written with the old name broken. A type definition instead creates a new, distinct type, even one with the same underlying type and operations as the given type; a copy of the old definition and a wrapper holding the new type are such definitions. Under a nominal type checker a subtype is treated as a subclass of the original, which means a value of the original cannot be used where the subtype is expected; under a structural type checker, which compares members, a subtype that adds no members or a copy of only public members accepts the original's values, and an instance test written with the old name still rejects them. Each of these separate types therefore breaks interoperation in at least one direction, and the alias is the mechanism that arranges for the old and the new type to be identical. The property the alias restores is gradual code repair: the type moves while code referring to the old name interoperates with code referring to the new name.

## Example
```python
bad:  class OldConfig(NewConfig):  # old name of NewConfig, kept while callers migrate
          pass
      def load(c: OldConfig) -> None: ...
      load(NewConfig("a"))  # type checker rejects: NewConfig is not OldConfig
good: OldConfig = NewConfig  # old name of NewConfig, kept while callers migrate
      def load(c: OldConfig) -> None: ...
      load(NewConfig("a"))
```

## Limits
The rule reaches only an old name kept for callers that have not yet migrated. A declaration meant to create a distinct type, a new name whose values the type checker distinguishes from the original's to prevent logic errors, is a type definition by intent and correct as one. Where the language offers no alias declaration for a type, there is no way to arrange that the old and the new type are identical and that code referring to the old name interoperates with code referring to the new name; such a file has no alias to require, and the rule does not reach it. The rule governs how the old name is declared during the transition period; how the change is split and when the old name is removed lie outside it.

## Validator
Grep the hunk for a type declaration whose body is empty or only forwards to another type (a subclass with an empty body, a type defined from a type in another module, a single-field wrapper struct) and for a deprecation marker beside a type declaration. Open the file and establish that the declared name is an old name kept for callers not yet migrated: it carries a deprecation marker or a comment naming the new type, or the same diff adds or moves the new type and leaves this name for existing callers. Confirm that the language offers a type alias, a public re-export or a second binding of the same class; where it offers none, stop. Check how the old name is declared: an alias, a re-export or a second binding of the new type passes; a subclass of it, a type defined from it, a wrapper holding it or a copy of its definition fails. Validator question: **Does the diff keep the old name of a moved or renamed type as a separate type that copies, wraps or extends the new type, in a language that offers an alias declaration for types?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: CHG-26`, severity major, `file`, `symbol`, `code` = the declaration of the old name quoted verbatim from the diff, `fix` = the old name declared, in the file's language, as an alias of the new type that binds it as a type and, where callers construct or test values through the old name, as the value too (a public re-export binds both), `rationale` = that the separate type is not identical to the new one, so code referring to the old name does not interoperate with code referring to the new name in at least one direction).

## Source
- Go design document 18130, 'Proposal: Type Aliases', §Abstract, §Background, §Proposal, golang/proposal design/18130-type-alias.md (fetched): "it is important to support a transition period in which the API is available from both the old and new locations and references to old and new can be mixed and interoperate"; "There is today no way to arrange that oldpkg.OldType and newpkg.NewType are identical and that code referring to the old name interoperates with code referring to the new name. Type aliases provide that mechanism."; "After such a declaration, T1 and T2 are identical types."; "a T2 stored in an interface value x does match a type assertion `x.(T1)` and does match a type switch `case T1`"; "The primary motivation is to enable gradual code repair during large-scale refactorings" (the "no way to arrange" sentence is stated of the language before it gained type aliases)
- The Go Programming Language Specification, §Alias declarations, §Type definitions, golang/go doc/go_spec.html (fetched): "An alias declaration binds an identifier to the given type"; "A type definition creates a new, distinct type with the same underlying type and operations as the given type"
- TypeScript Handbook, 'Everyday Types', §Type Aliases, microsoft/TypeScript-Website handbook-v2 (fetched): "When you use the alias, it's exactly as if you had written the aliased type."
- The Rust Reference, 'Use declarations', items.use.visibility.intro, rust-lang/reference src/items/use-declarations.md (fetched): "A public `use` declaration can therefore _redirect_ some public name to a different target definition"
- Python documentation, `typing`, §Type aliases and §NewType, python/cpython Doc/library/typing.rst (fetched): "type aliases can also be created through simple assignment"; "will make the static type checker treat ``Alias`` as being *exactly equivalent* to ``Original`` in all cases"; "a value of type ``Original`` cannot be used in places where a value of type ``Derived`` is expected. This is useful when you want to prevent logic errors"; "Use the NewType helper to create distinct types"
- The Rust Reference, 'Type aliases', items.type.constructor-alias, rust-lang/reference src/items/type-aliases.md (fetched): "A type alias to a tuple-struct or unit-struct cannot be used to qualify that type's constructor"; its example marks "let _ = UseAlias(5); // OK" for `use MyStruct as UseAlias;` and "let _ = TypeAlias(5); // Doesn't work" for `type TypeAlias = MyStruct;`
- TypeScript Handbook, 'Declaration Merging', microsoft/TypeScript-Website reference/Declaration Merging.md (fetched): "In TypeScript, a declaration creates entities in at least one of three groups: namespace, type, or value."; its table marks a Class as creating a type and a value and a Type Alias as creating a type only
- TypeScript Handbook, 'Type Compatibility', opening paragraph and §Classes, microsoft/TypeScript-Website reference/Type Compatibility.md (fetched): "Type compatibility in TypeScript is based on structural subtyping."; "When comparing two objects of a class type, only members of the instance are compared."; 'Narrowing', §`instanceof` narrowing, handbook-v2/Narrowing.md (fetched): "in JavaScript `x instanceof Foo` checks whether the _prototype chain_ of `x` contains `Foo.prototype`."
- Caveat: the evidence is language specification and documentation of the alias mechanism and its stated motivation; no measured study of migrations backs the rule.
