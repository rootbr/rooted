---
title: A value that can take only one of a fixed, known set of domain values is typed as an enumeration or a union of literal values, not as a free string or integer code
rule_id: DSN-47
domain: design
step: [design, implement, refactor]
applies_to: [universal]
triggers: ['(?:===?|!==?|[.]equals(?:IgnoreCase)?\()\s*["\x27][A-Za-z_][\w-]*["\x27]|["\x27][A-Za-z_][\w-]*["\x27]\s*(?:===?|!==?|[.]equals(?:IgnoreCase)?\()|\bcase\s+["\x27][A-Za-z_][\w-]*["\x27]\s*(?:[:,|]|->)|["\x27][A-Za-z_][\w-]*["\x27]\s*(?:\|[^=]*)?=>', '\b\w*(?:[Ss]tatus|[Ss]tate|[Kk]ind|[Tt]ype|[Mm]ode|[Rr]ole|[Ll]evel|[Cc]ategory)\w*\??\s*:\s*&?(?:string|str|String|int|Integer|number|[iu](?:8|16|32|64|size))\b|\b(?:String|int|Integer)\s+\w*(?:[Ss]tatus|[Ss]tate|[Kk]ind|[Tt]ype|[Mm]ode|[Rr]ole|[Ll]evel|[Cc]ategory)\w*\s*[;=,)(]|(?<!type\s)\b\w*(?:[Ss]tatus|[Ss]tate|[Kk]ind|Type|[Mm]ode|[Rr]ole|[Ll]evel|[Cc]ategory)\w*\s+(?:string|int)\b|(?<!type\s)\b\w*(?:[Ss]tatus|[Ss]tate|[Kk]ind|[Tt]ype|[Mm]ode|[Rr]ole|[Ll]evel|[Cc]ategory)\w*\s*:?=\s*["\x27][A-Za-z_][\w-]*["\x27]']
scope: file
check_kind: semantic
severity_default: minor
---

# A value that can take only one of a fixed, known set of domain values is typed as an enumeration or a union of literal values, not as a free string or integer code

## Thesis
A variable, field, parameter or return value that can take only one of a limited set of values, where the set is fixed and known when the code is written (a status, a state within a defined process, a kind), has a type whose declared members are that set: an enumeration, or a union of literal values written directly or derived from a constant object that lists the members. A general string or integer type standing for such a set, with its legal values held in loose literals or constants, does not meet the rule.

## Rationale
A general string or integer type can represent any value of its type, so a misspelled value or a value from an unrelated set is accepted wherever a legal one is. A type whose values are exactly the set gives the type checker that set: a literal outside it is rejected where it is assigned or passed, and a checker that flags comparisons between types with no common value reports a comparison against one, so misspelling issues are avoided. An enumeration whose members are not themselves integers or strings, unlike a sequence of integer or string values, also keeps its values distinct from every other value, including the values of other enumerations, and leaves undefined the operations that have no meaning for the set, such as multiplying a day of the week by two. Its members are similar to global variables but add grouping, type safety and a more useful printed representation, and where the language checks membership a value of the type can only be one of its listed members.

## Example
```typescript
bad:  interface Order { id: string; status: string }
      if (order.status === "shiped") { ... }
good: type OrderStatus = "pending" | "shipped" | "delivered";
      interface Order { id: string; status: OrderStatus }
      if (order.status === "shipped") { ... }
```

## Limits
The rule needs a set that is fixed and known when the code is written; a set whose members configuration, stored data or users add after the code is written is outside it. Where the member a value holds is known only when the program runs, such as a value read from input or storage, the value is converted to the type by value or by name; how that input is validated and rejected is outside this rule. An enumeration whose members are comparable to integers, and thus by transitivity to members of unrelated enumerations, breaks part of these guarantees; it is acceptable where a plain enumeration will not do, for example where integer constants are replaced with an enumeration or for interoperability with other systems. Where the language's enumeration is a defined type over an integer or string type with named constants, the defined type is distinct from every other type but keeps the operations of its underlying type, an untyped constant it can represent is assignable to it, and any constant it can represent is convertible to it, whether or not a named constant lists that value; such a declaration meets the rule as that language's enumeration, without the guarantees against a misspelled literal and against meaningless operations. A boolean, a combination of flags and optional fields that together encode one state, the name a value carries, and the transitions between states are outside this rule. A project-context tolerance that keeps a named value in its raw string or integer type rejects the finding.

## Validator
Grep the added lines for a declaration that types as a string or integer a value whose name contains status, state, kind, type, mode, role, level or category; for an equality test, case label or match arm against a string literal; and for a string literal assigned to such a name. Open the file and trace the value: find its declared type and collect every literal or constant the file assigns to it, passes for it, compares it with or branches on. Confirm the set is fixed and known when the code is written: its legal values are written in the code, and no configuration, stored data or user input adds members. Skip a value already typed as an enumeration, a union of literal values or a defined type with named constants; a raw value read from input up to the point where it is converted; an integer-compatible enumeration kept to replace integer constants or for interoperability; a boolean; and a value whose declaration is neither in the file nor shown by the diff. Validator question: **Does an added line declare, assign, pass, compare or branch on a value typed as a general string or integer whose legal values form a set fixed and known when the code is written?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: DSN-47`, severity minor, `file`, `symbol`, `code` = the added declaration, comparison, case label or assignment that carries the value as a string or integer, quoted verbatim from the diff, `fix` = the enumeration or literal-union type listing the set and the declaration retyped to it, in the file's language, `rationale` = the value, the legal values the file uses for it, and the misspelled or foreign value the general type admits).
