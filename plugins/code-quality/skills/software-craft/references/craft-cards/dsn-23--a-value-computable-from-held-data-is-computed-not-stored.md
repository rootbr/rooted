---
title: A value computable from data the same object or record already holds is computed from that data, and a stored copy is kept only while the source cannot change or a mechanism recalculates it on every change of the source
rule_id: DSN-23
domain: design
step: [design, implement]
applies_to: [universal]
triggers: ['(?i)\b\w+\s*[.]\s*_?\w*(total|(?<!ac)(?<!dis)(?<!en)count(?!r[iy])|sum(?!e|mar)|size|length|average|avg|full_?name|is_?empty|selected)\w*\s*[-+*/]?=[^=]', '(?i)^\s*(pub(\([\w:]+\))?\s+|public\s+|private\s+|protected\s+|readonly\s+)*_?\w*(total|(?<!ac)(?<!dis)(?<!en)count(?!r[iy])|sum(?!e|mar)|length|average|full_?name|is_?empty)\w*(\s*:\s*|\s+)(int|integer|bigint|numeric|i32|i64|u32|u64|usize|f32|f64|float|float64|int64|double|long|number|string|str|String|bool|boolean|Decimal|BigDecimal)\b', '(?i)^\s*((private|public|protected|final|static|readonly)\s+)*(int|long|double|float|short|BigDecimal|String|boolean|Integer|Long|Double)\s+_?\w*(total|(?<!ac)(?<!dis)(?<!en)count(?!r[iy])|sum(?!e|mar)|length|average|full_?name|is_?empty)\w*\s*[;=]', '\b(cached_property|lru_cache|memoize|OnceCell|OnceLock|LazyLock|useMemo)\b|\bsync[.]Once\w*|[@.]cache\b|\buseState\s*[<(]']
scope: file
check_kind: semantic
severity_default: major
---

# A value computable from data the same object or record already holds is computed from that data, and a stored copy is kept only while the source cannot change or a mechanism recalculates it on every change of the source

## Thesis
A field, state variable or column whose value can be calculated from other data that the same object, component, record or row already holds is calculated from that data on demand, not stored beside it. Typical cases are a total or a count calculated from the items held, a full name calculated from its parts, and a selected element found in the list by the identifier that selects it. A stored copy of such a value is kept only in two cases. In the first, the data it is calculated from cannot change after the copy is made. In the second, a mechanism recalculates the copy whenever that data changes, such as a column generated from other columns of its row or a memo keyed on its inputs, and nothing else writes the copy; a copy that each write path refreshes by hand is not one of these cases.

## Rationale
A stored copy of a calculable value stays correct only while every piece of code that changes its source also updates the copy. Data duplicated between several variables is difficult to keep in sync, and the first write path that forgets the copy leaves it stale. Two cases show this. A count of total and packed items, kept beside the item list, goes wrong once an item is marked packed and then deleted. A selected item, copied out of the list, keeps its old content after the item in the list is edited. A copy taken once, when its holder is initialized, does not follow any later change to its source. A value calculated on demand from its source is always up to date, and the code that changes the source does nothing extra to update it, because the next read calculates the value from the fresh data. Calculating it avoids the bugs that come from separate state variables getting out of sync with each other. Removing redundant and duplicate data helps keep all the pieces of state in sync, much as normalizing a database structure is meant to reduce the chance of bugs.

A stored copy does not drift in the two cases the rule accepts. A cache that computes a value once and keeps it for the life of its holder suits an expensive value on a holder that is otherwise effectively immutable. Where the attributes it was computed from are mutable, such a cache cannot detect their changes. A copy that is recalculated whenever its source changes stays current. A column generated from other columns of its row is updated whenever the row changes and cannot be written to directly. A memoized result is calculated again whenever one of its inputs differs from the last time it was calculated. A memo keyed on the attributes it reads detects their updates. A copy that each write path updates by hand stays correct only until one write path forgets it, so a counter is removed even where every handler could update it correctly.

## Example
```python
bad:  class Cart:
          def __init__(self, items):
              self.items = list(items)
              self.total = sum(i.price for i in self.items)
good: class Cart:
          def __init__(self, items):
              self.items = list(items)
          @property
          def total(self):
              return sum(i.price for i in self.items)
```

## Limits
A copy that is meant to keep the value its source had when the copy was made, and to ignore every later change of that source, is outside the rule; a name that marks the source or the copy as an initial or default value, such as a parameter whose name starts with initial or default, makes that intent visible. The rule reaches a value calculable from data the same object, component, record or row holds; a value calculated from data held elsewhere, such as another table or a remote service, is outside it. The project context rejects the finding where it names the stored value as a deliberate denormalization together with a mechanism outside the file that recalculates it on every change to its source.

## Validator
In the hunk, find each field, property, state variable or column that is declared or assigned under a name or with an initializer that reads as a total, a count, a sum, a size or length, an average, a full name, an emptiness flag or a selected element, and each cache or memo construct. Open the file and read the type, component or table that holds it. Decide whether its value can be calculated from other data the same holder holds: either the code that assigns it performs that calculation, or its name says what it summarizes, such as a total beside a list of items or a count beside a collection. Skip a value that is calculated on each read, such as a property, an accessor method, a value computed during rendering or a virtual generated column. For a stored value, trace the data it is calculated from: find every place in the file that writes that data, and check whether the data is mutable and reachable for writing from outside the holder. Skip the value when that data cannot change after the copy is made. Skip it when a mechanism recalculates the copy whenever that data changes and nothing else writes the copy, as with a generated column or a memo keyed on its inputs; do not skip a copy that each write path refreshes or clears by hand. Skip a copy that is meant to ignore later changes of its source where the source or the copy is named or documented as an initial or default value, such as a copy of a parameter whose name starts with initial or default, and a value the project context names as a deliberate denormalization with its refresh mechanism. Validator question: **Does this holder store a value that can be calculated from data it already holds, while that data can still change without a mechanism that recalculates the stored value?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: DSN-23`, severity major, `file`, `symbol`, `code` = the declaration or assignment of the stored value quoted verbatim from the diff, `fix` = the value calculated from its source on each read, as a property, an accessor method, a value computed during rendering or a virtual generated column, or recalculated on every change of the row, as a stored generated column, or, where the calculation is expensive, a memo keyed on its inputs, in the file's language, `rationale` = the data the value is calculated from and the write to that data that leaves the stored value stale).
