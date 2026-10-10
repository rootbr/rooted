---
title: A rename or move of a code element updates every use of its old name that is resolved at run time, such as by reflection, serialization, templates or string-named lookups, or deliberately keeps the old external name
rule_id: CHG-03
domain: change
step: [refactor, review]
applies_to: [universal]
triggers: ['\b(def|fn|function|class|struct|interface|trait|enum|type)\s+\w+|\bfunc\s+(\([^)]*\)\s*)?\w+|\b(public|protected|private|internal)\s+[\w<>\[\],.? ]+\s+\w+\s*\(|\b(getattr|setattr|hasattr|delattr)\(\s*[\w.]+\s*,\s*[\x22\x27]|\b(Class[.]forName|getMethod|getDeclaredMethod|getField|getDeclaredField|MethodByName|FieldByName|Reflect[.](get|set|has|apply))\s*\(|\b(patch|jest[.]mock|vi[.]mock)\(\s*[\x22\x27][\w./-]+[\x22\x27]|\bpatch[.]object\(\s*[\w.]+\s*,\s*[\x22\x27]|\{\{-?\s*[.]?\w+([.]\w+)+', '#\[derive\([^)]*\b(Serialize|Deserialize)\b|`[^`]*\b(json|yaml|xml|toml|db|form|mapstructure):\x22|@(JsonProperty|SerializedName|JsonAlias)\b|#\[serde\(']
scope: callers
check_kind: semantic
severity_default: major
---

# A rename or move of a code element updates every use of its old name that is resolved at run time, such as by reflection, serialization, templates or string-named lookups, or deliberately keeps the old external name

## Thesis
When a change renames or moves a field, method, type, function or module, every use of the old name that the compiler does not check (a lookup by a name string at run time, a serialization key or template reference taken from the member's name, a test double's target path) is either updated to the new name in the same change or bound explicitly to the old external name, so that the rename introduces no run-time error and leaves no stored value unread.

## Rationale
A rename that the compiler accepts can still introduce errors at run time, through uses that reach the element by reflection or by a run-time type check rather than through a name the compiler binds. A language server's rename documentation names packages that use reflection, such as a serializer and a template engine, as places where such errors may arise, and states that a method rename may make a run-time assertion to an interface fail when the value reached that assertion only through a conversion to a broader type. A lookup by qualified name, such as a type loaded from its string name or a test double whose target is a dotted path imported when the test function executes, is resolved only when that code runs, so a path left stale by a move is not caught before then. Serialization that takes a member's name as the external key changes the key with the rename unless an explicit name is set, and two serialization libraries ignore an incoming key with no matching member by default, one of them for self-describing formats such as JSON, so a value stored under the old key is not read into the renamed member. Relying on “chasing error messages” when refactoring by hand is, as a formative study of developers' manual refactoring suggests, an error-prone strategy, and a use reached by reflection produces no compiler error to chase. An inspection that searched manual refactorings for missed edits and for extra edits that might be incorrect detected 22 times more anomalies than running the existing regression test suites, at 94 percent precision on average; the search for stale uses comes in addition to judgment and testing, not in place of them.

## Example
```rust
bad:  #[derive(Serialize, Deserialize)]
      struct Order { total: u64 } // renamed from amount; stored JSON still has "amount"
good: #[derive(Serialize, Deserialize)]
      struct Order {
          #[serde(rename = "amount")]
          total: u64,
      }
```

## Limits
A use that the compiler checks or that the rename tool updates is outside this rule, and so is a name that no string, serialized key, template or test-double path refers to. Where the old name is a key in data stored or exchanged outside the code, an explicit external name keeps that data readable unchanged, and an alias that accepts both the old and the new name on input lets one reader take data written before and after the rename. Callers outside the repository that use the old name see it as a published interface and are a deprecation question, not a rename one.

## Validator
Find each declaration the hunk renames or moves: a removed declaration and an added one with the same body under a new name or a new module path. Search the callers' scope for the old name and the old qualified path as a string literal, in serialization tags or attributes, in template files, in reflection calls that take a member or type name as a string, and in test-double targets given as a dotted path. When the renamed member belongs to a type that a derived or reflection-based serializer reads with keys taken from member names, count that derived key as a use of the old name. For each hit, check whether the diff updates it; an explicit external name on the renamed declaration settles only the serialization key it sets, not a template, reflection lookup or test-double path that names the member directly. For a derived serialization key, the use is settled when the diff updates the data that holds the old key, or when the renamed declaration carries an explicit external name equal to the old one or an input alias that accepts it. Validator question: **Does the diff rename or move a declaration while a run-time lookup, template reference or test-double path elsewhere still names the old identifier, or while a member of a deserialized type changes the key derived from its name with neither an update of the data that holds the old key nor an explicit external name or input alias equal to the old one?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: CHG-03`, severity major, `file`, `symbol`, `code` = the renamed declaration line and the stale use of the old name, or the serializer derivation whose key changes, quoted verbatim, `fix` = the stale use updated to the new name, or the declaration with an explicit external name or input alias equal to the old one, in the file's language, `rationale` = the run-time lookup, key, template or test-double path that still names the old identifier, or the stored key the renamed member no longer reads, and the failure it produces at run time).
