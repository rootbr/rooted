---
title: Input is parsed in one layer at the boundary where it enters, into a typed value, or into a type whose only constructor checks it, and processing code takes that value instead of raw text or an untyped map whose parsing and checks it repeats
rule_id: INP-14
domain: input
step: [design, implement, refactor]
applies_to: [universal]
triggers: ['Map<String,\s*Object>|map\[string\](interface\{\}|any)|dict\[str,\s*Any\]|Record<string,\s*any>|serde_json::Value|\bas\s+any\b|:\s*any\b', '^\s*(self[.]|this[.])?(validate|check|verify|ensure)\w*\(.*\)\s*;?\s*$', '\b(json[.]loads|JSON[.]parse|json[.]Unmarshal|serde_json::from_str|readValue)\(']
scope: callers
check_kind: semantic
severity_default: minor
---

# Input is parsed in one layer at the boundary where it enters, into a typed value, or into a type whose only constructor checks it, and processing code takes that value instead of raw text or an untyped map whose parsing and checks it repeats

## Thesis
Input is parsed in one distinct layer at the boundary where it enters, into the program's internal data representation, and the processing code past that layer takes that representation in its signatures, so the parsing and checks of an input live in that layer rather than in each routine that receives raw text, a string-keyed map of untyped values or a parse result of a catch-all type on which any operation compiles. Where it is absolutely critical that the program operate only on values that hold a property and many routines require it, a dedicated type carries the property: its only constructor runs the check, its field stays private, and those routines take the type in their signatures instead of each repeating the check.

## Rationale
Parser code scattered throughout a program could be subject to errors or inconsistencies that create weaknesses; parsing as a distinct layer enforces a boundary between raw input and internal data representations. Parsing and input-validating code mixed with and spread across processing code throws a cloud of checks at the input, with no systematic justification that one or another catches all the bad cases. Once the input is parsed into a data structure representing it, the program uses that structure as the input to its computational processes. Where it is absolutely critical that the program operate only on values that hold a property and many routines require it, a check written into every one of them is tedious and might impact performance; a type in a dedicated module, created only through a function that runs the checks, makes it safe for routines to use the type in their signatures and confidently use the values they receive. An argument type that rules out bad inputs usually comes at little run-time cost: it pushes the cost to the boundaries, where a value is first converted into that type, and, where the language checks types before the program runs, it catches bugs early, during that type check, rather than through run-time failures. Of two catch-all types that represent any value, the one with which it is not legal to do anything is safer than the one on which any operation compiles.

## Example
```rust
bad:  fn reserve(body: &str) -> u64 {
          let v: serde_json::Value = serde_json::from_str(body).unwrap();
          check_qty(&v);
          v["qty"].as_u64().unwrap() }
      fn refund(v: &serde_json::Value) -> u64 { check_qty(v); v["qty"].as_u64().unwrap() }
good: mod qty { pub struct Qty(u64);
          impl Qty { pub fn parse(body: &str) -> Result<Qty, String> { ... }
                     pub fn get(&self) -> u64 { self.0 } } }
      fn reserve(qty: &qty::Qty) -> u64 { ... }
      fn refund(qty: &qty::Qty) -> u64 { ... }
```

## Limits
Some properties are difficult or impossible to express using types; the dedicated-type sentence of the thesis does not reach them. A dedicated type's guarantee rests on its field being private, so that code outside the defining module cannot set the value directly, and holds only as far as the language also stops that code from creating an instance without the checking constructor. The dedicated-type sentence of the thesis applies where many routines require the property; a property that one routine requires is outside it. The rule reaches the boundary between raw input and internal data representations and the routines past it that receive the input or a field or property of it; checks on values the program computes inside that boundary, rather than on the input's fields or properties, are outside it.

## Validator
Grep the hunk for a parameter, field or variable typed as raw text, as a string-keyed map of untyped values or as a parse result of a catch-all type on which any operation compiles; for a call that parses input; and for a check call whose result is discarded or is a boolean while the caller goes on using the raw value. Open the callers of the routine that holds it and the other routines that receive the same input, and trace where that input was parsed and which of them parse or check the same field or property again. Validator question: **Does code past the layer where the input enters take raw text, an untyped map or a parse result of a catch-all type on which any operation compiles, and parse or check it again where another routine or the boundary layer already parses or checks the same input?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: INP-14`, severity minor, `file`, `symbol`, `code` = the signature that takes the raw or untyped input and the repeated parse or check line, `fix` = the typed value that the boundary layer builds once, or, where many routines require the property, a type whose only constructor runs the check, and the signature that takes it, in the file's language, `rationale` = the routines that repeat the parse or check and the property they repeat).
