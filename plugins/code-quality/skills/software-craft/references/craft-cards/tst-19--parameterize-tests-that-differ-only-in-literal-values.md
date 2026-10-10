---
title: Three or more tests that differ only in a few literal input and expected values are one table-driven or parameterized test, unless merging them would make the test branch on its cases
rule_id: TST-19
domain: tests
step: [test, refactor]
applies_to: [tests]
triggers: ['signal:duplicate_block', '^\s*(async\s+)?(def\s+test\w*?|(public\s+)?void\s+\w*?|func\s+Test\w*?|fn\s+\w*?)_?\d+\s*\(|\b(it|test)\s*\(\s*[\x22\x27\x60][^\x22\x27\x60]*\d[\x22\x27\x60]']
scope: file
check_kind: semantic
severity_default: suggestion
---

# Three or more tests that differ only in a few literal input and expected values are one table-driven or parameterized test, unless merging them would make the test branch on its cases

## Thesis
When at least three tests run the same statements and differ only in a few hard-coded input and expected values, fewer than four varying values per test, they are written as one table-driven or parameterized test whose rows hold those values. Cases that need different setup, actions or assertions stay in separate tests, because merging them would put a branch on a case field into the shared body.

## Rationale
Merging tests that differ only by a few hard-coded values into one parameterized test reduces duplication, makes the tests easier to read and lowers the risk of introducing bugs when the test logic needs to change. When the behaviour under test changes only with the input, one table shows how it changes across all inputs, where separate tests make comparable cases harder to compare and contrast. Each row is a complete test case with its inputs and expected results, and can carry a name that keeps the test output readable. Complex error checking based on conditional differences in test setup can be difficult to understand when each table entry has specialized logic based on its inputs, and large, complex table tests harm readability and maintainability because their readers may have difficulty debugging the failures that occur.

## Example
```typescript
bad:  it("level 1 has health 100", () => { expect(health(1)).toBe(100); });
      it("level 2 has health 200", () => { expect(health(2)).toBe(200); });
      it("level 3 has health 300", () => { expect(health(3)).toBe(300); });
good: it.each([[1, 100], [2, 200], [3, 300]])("level %i has health %i", (level, expected) => {
        expect(health(level)).toBe(expected);
      });
```

## Limits
Parameterizing has little value when the resulting test becomes significantly more complex than the separate tests it replaces. The rule is contested, and whether the merged body would branch on the case separates the positions. On the merging side, a table may be preferable when the behaviour under test only changes based on changed input, with every table field used in all cases and all test logic run for every case as the ideals. On the duplication side, when row values would dictate conditional behaviour inside the test case, the extra clarity of duplication between the cases is necessary for readability, and when some cases need to be checked using different logic from the others, it is appropriate to write multiple test functions. A table test can become confusing and difficult to read when it uses multiple branching pathways on expectation flags, many conditional statements for specific mock expectations, or functions placed inside the table, and a large, complex table test should be split into multiple tables or individual tests. A short, straightforward body may keep a single success-versus-failure branch on one expected-error field; the alternative is one table for normal outputs and a second for error outputs. Cases with different logic but identical setup may read better as a sequence of subtests in one test, with a test helper holding the setup they share.

## Validator
Grep the hunk for test declarations whose names end in a number and for adjacent test blocks with near-identical statements. Open the file and line up each group of three or more sibling tests statement by statement. Count the literals that differ between them, and trace whether any case needs its own setup, action or assertion, so that a merged body would branch on a case field. Validator question: **Do three or more tests in the file run the same statements and differ only in fewer than four hard-coded input or expected values, with no case that would need its own setup, action or assertion?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: TST-19`, severity suggestion, `file`, `symbol`, `code` = the declaration lines of the similar tests and the literals that differ between them, quoted verbatim from the diff, `fix` = one table-driven or parameterized test with a row per case, in the file's language, `rationale` = the number of similar tests and the values that vary between them).
