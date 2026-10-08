---
title: A lookup table holds an entry for every key it can be asked for or its read states what a missing key yields, unless the zero value or null returned on a miss is the intended answer for every absent key
rule_id: CODE-16
domain: code
step: [implement, handle-errors]
applies_to: [universal]
triggers: ['[.]get\(\s*[^,()]+\)|(=|\breturn)\s*[\w.]+\[[^\]\[]+\]\s*;?\s*$|[.](floor|lower|ceiling|higher)(Entry|Key)\(|\bbisect(_left|_right)?\(|\bsort[.]Search(Ints|Float64s|Strings)?\(|\bslices[.]BinarySearch|[.](partition_point|binary_search)\(', '\bmap\[[\w.*]+\][\w.*\[\]]+\s*\{|\bRecord<|\b(Enum|Hash|Tree|Linked(Hash)?|Navigable|Sorted)?Map<|\bMap[.]of(Entries)?\(|\b[A-Z][A-Z0-9_]+\s*(:[^=]*)?=\s*\{']
scope: file
check_kind: semantic
severity_default: major
---

# A lookup table holds an entry for every key it can be asked for or its read states what a missing key yields, unless the zero value or null returned on a miss is the intended answer for every absent key

## Thesis
A read from a lookup table, whether a map, a dictionary, an object used as a map or a sorted table of breakpoints searched for the range a value falls in, whose key can be one the table has no entry for states what that miss yields. It passes a default to the read or relies on a fallback entry registered in the table, guards the read with a presence check whose miss branch returns a chosen value, reports the miss or raises an error, or uses a read form that itself raises or panics when the key is absent. Instead, the table may hold an entry for every key it can be asked for, such as every member of the enumerated type its keys are drawn from where the key can hold no value outside those members, or, for a breakpoint table, a result for values below its lowest and above its highest breakpoint, as a table of four breakpoints and five results does. A read that takes the zero value or the null the lookup returns for an absent key meets the rule only where that value is the intended answer for every absent key.

## Rationale
Several lookup forms return a value instead of failing when the key is absent. One returns the element type's zero value, so an absent key and a key whose entry is zero read the same: in an offset table whose entry for one zone is 0, a zone missing from the table also reads 0. Another returns null for an absent key and, where the table admits null entries, for a key mapped to null as well, and the null-dereference error comes only where code later uses that null as an object, not at the read. A third returns a none value when the call passes no default, so that it never raises. A keyed read through a type that declares its keys by an index signature is typed as the value type even for a key never declared, unless a checker option adds the absent value to that type. A two-result read or a contains-key test tells a miss from a stored zero or null, and a read with a default argument returns that default for a miss. A documented rewrite of a chain of equality branches as a table keeps the chain's final else value as that default, and a dispatch registry of handlers keyed by type registers a base handler that runs when no better one is found. At the ends of a breakpoint table, a search for the greatest key at or below a value returns null for a value below the lowest key, and a search for the first index whose breakpoint satisfies a test returns the table's length when none does, one past the last result of a table with one result per breakpoint. A grade table of four breakpoints and five grades returns a grade both for a score below its lowest breakpoint and for one above its highest. A completeness check for map literals keyed by an enumerated type exists as an analyzer option that is off by default, and a type checker can require an object literal to carry all the keys of a key type but no more.

## Example
```go
bad:  var offsets = map[string]int{"UTC": 0, "EST": -5}
      func offset(zone string) int {
          return offsets[zone]
      }
good: func offset(zone string) (int, error) {
          if hours, ok := offsets[zone]; ok {
              return hours, nil
          }
          return 0, fmt.Errorf("unknown zone %q", zone)
      }
```

## Limits
Where the zero value or null is the answer the code intends for every absent key, reading it is the stated default: a set held as a map to booleans, where a key not in the map reads false, and a counting map, where a key not yet counted reads zero. A read form that raises or panics when the key is absent states the miss as an error. A read form that returns an optional value returns none for an absent key, distinct from every entry, and the miss is then stated wherever the caller handles that none. A routine that documents the read's null or none as its own result for an absent key, as a map's read documents its null, passes the miss on through that documented contract.

## Validator
Grep the hunk's added lines for table reads: a get call with one argument, an index read assigned or returned whole, a floor, lower, ceiling or higher search over a sorted map, a bisection or binary search over sorted breakpoints, and declarations of maps, records and constant literal tables whose reads the file holds. Open the file and find the table each read uses, its entries, and where the read's key comes from. Clear a read that passes a default; that a presence check or a two-result read guards with a miss branch returning a chosen value, reporting or raising; whose form raises or panics on an absent key; whose optional result the code branches on or defaults; whose table registers a fallback entry; whose table has an entry for every value the key can hold; or whose breakpoint table has a result below its lowest and above its highest breakpoint. Clear a read whose zero value or null is the answer the code intends for every absent key, such as a membership set or a counter, and a read whose routine documents that null or none as its result for an absent key. Otherwise trace whether the key can miss, coming from input, from a parameter, from a type wider than the table's keys or from beyond the breakpoints, and follow the value the read returns on that path: returned, stored, compared or dereferenced as if it were an entry. Validator question: **Can a table read that the hunk adds, or that reads a table the hunk adds or changes, receive a key the table has no entry for while the code uses the zero value or null returned for that miss as if it were an entry?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: CODE-16`, severity major, `file`, `symbol`, `code` = the table read verbatim from the diff, `fix` = the read with its miss stated, by a default passed to the read, a presence check whose miss branch returns a chosen value or raises an error naming the key, or the missing entries added to the table, in the file's language, `rationale` = the key that can miss, the zero value or null the read returns for it, and where the code uses that value as if it were an entry).

## Source
- Go specification, "Index expressions", map type `M`: "if the map is nil or does not contain such an entry, a[x] is the zero value for the element type of M"; comma-ok form: "The value of ok is true if the key x is present in the map, and false otherwise." (fetched)
- Effective Go, "Maps": "looking up a non-existent key will return 0"; `if attended[person] { // will be false if person is not in the map`; "Sometimes you need to distinguish a missing entry from a zero value. Is there an entry for \"UTC\" or is that 0 because it's not in the map at all?"; the `offset` example logs `"unknown time zone:"` on a miss. (fetched)
- OpenJDK 21 `java.util.Map`: `get` "or null if this map contains no mapping for the key"; "If this map permits null values, then a return value of null does not necessarily indicate that the map contains no mapping for the key"; "The containsKey operation may be used to distinguish these two cases."; `getOrDefault` "or defaultValue if this map contains no mapping for the key". (fetched)
- OpenJDK 21 `java.lang.NullPointerException`: "Thrown when an application attempts to use null in a case where an object is required." (fetched)
- OpenJDK 21 `java.util.NavigableMap.floorEntry`: "the greatest key less than or equal to the given key, or null if there is no such key". (fetched)
- Python 3.12 Built-in Types, `dict`: `d[key]` "Raises a KeyError if key is not in the map."; `get` "If default is not given, it defaults to None, so that this method never raises a KeyError."; `__missing__` returning `0` "shows part of the implementation of collections.Counter". (fetched)
- Python `bisect`, Examples: "can be useful for numeric table lookups"; `i = bisect([60, 70, 80, 90], score)`, `return "FDCBA"[i]`, scores `[33, 99, 77, 70, 89, 90, 100]` give `['F', 'A', 'C', 'C', 'B', 'A', 'A']`. (fetched)
- Go `sort.Search` doc comment: "Search returns the first true index. If there is no such index, Search returns n." (fetched)
- Python `functools.singledispatch`: "The original function decorated with @singledispatch is registered for the base object type, which means it is used if no better implementation is found." (fetched)
- Ruff SIM116 `if-else-block-instead-of-dict-lookup`: the chain's `else: return "Goodnight"` becomes `return phrases.get(x, "Goodnight")`. (fetched)
- Rust std `HashMap`: `get` returns `Option<&V>`, `assert_eq!(map.get(&2), None)`; `Index`: "Panics if the key is not present in the `HashMap`.", implemented as `self.get(key).expect("no entry found for key")`. (fetched)
- TypeScript TSConfig reference, `noUncheckedIndexedAccess`: "Not declared, but because of the index signature, then it is considered a string"; "will add `undefined` to any un-declared field in the type". (fetched)
- TypeScript 4.9 release notes, "The `satisfies` Operator": "we could ensure that an object has *all* the keys of some type, but no more". (fetched)
- `nishanths/exhaustive` go/analysis pass: "If configured via flags, the analysis can check that additional kinds of elements in the syntax tree, such as map literals, are exhaustive."; "mapliteral    check that composite literals of underlying type map (or pointer to) are exhaustive."; "The default argument is \"switch\"."; example `var m1 = map[T]bool{ X0: true, X1: true }` over the enumerated type `T`. (fetched)
- Caveat: no study measuring defects from unstated table misses was found; the evidence is language and library documentation of what each read form returns on a miss, one opt-in analyzer check and one type-checker operator.
