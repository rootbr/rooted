---
title: A change that rewrites stored snapshot, golden or approved output rewrites only the entries its own intended behaviour change explains
rule_id: CHG-21
domain: change
step: [test, review]
applies_to: [tests]
triggers: ['[.]toMatch(Inline)?Snapshot\(|\bassert_\w*snapshot!|\bApprovals?[.]verify\w*\(', 'signal:test_file']
scope: base-compare
check_kind: semantic
severity_default: major
---

# A change that rewrites stored snapshot, golden or approved output rewrites only the entries its own intended behaviour change explains

## Thesis
A change that re-records stored snapshot, golden or approved output rewrites only the entries whose difference from the base version its intended behaviour change explains. Every failing entry is triaged before anything is re-recorded and assigned one of three causes: an error the change introduced, which is fixed before re-recording so that the buggy behaviour is not recorded; an intended change of visible behaviour, which the failing test corroborates and for which the entry is updated; or a test so sensitive that it fails on an inconsequential change, which is made to stop depending on the observation that varies. Re-recording every failing test at once is sound only when each failure has the second cause; otherwise the other failures are resolved first, or re-recording is limited to the tests whose failure the intended change explains. A change that intends no visible behaviour change therefore rewrites no stored entry except one whose own test it edits, as when it makes a test stop depending on an observation that varies.

## Rationale
A stored-output test compares the current output with a recorded copy and depends on the precise output, so any change, even a minor one, can fail it; in a review of 50 grey-literature documents on snapshot testing, this fragility was the most prominent drawback, identified in 14 documents (28%). The recorded copy shows only what the output was before and what it is now, and whether a difference is a fixed bug or a new one is decided by the person who re-records it. An update command that re-generates the stored output of every failing test at once records, for a test that fails because of an unintentional bug, the buggy behaviour as its expected output. The same review reports that updating stored output without understanding why the test failed can mask regressions and lead to decreasing confidence in the suite. Re-recording can be limited to the tests whose names match a pattern, and an update is checked by comparing the old expected value with the new one.

## Example
```typescript
bad:  // intent: label the total "Total due"; every failing snapshot re-recorded
      expect(totalLine(invoice)).toMatchInlineSnapshot(`"Total due: 10.00"`);
      expect(taxLine(invoice)).toMatchInlineSnapshot(`"Tax: 0.00"`); // was "Tax: 1.90"; no intent explains it
good: // intent: label the total "Total due"; only the matching test re-recorded
      expect(totalLine(invoice)).toMatchInlineSnapshot(`"Total due: 10.00"`);
      expect(taxLine(invoice)).toMatchInlineSnapshot(`"Tax: 1.90"`); // kept; the tax bug is fixed first
```

## Limits
A test with no stored entry in the base version is recorded for the first time: its current output becomes the stored copy, and there is no earlier entry to compare it with. A regression suite produced by a test generator may, once its failures are traced to an intended change of visible behaviour, be discarded and generated anew in whole rather than updated entry by entry; the triage of each failure still comes first. The rule judges which stored entries a change rewrites; whether a stored output is focused and short enough to review is a question of test design it does not reach. An entry whose own test the change edits, in its input or in a matcher, redaction, sort or normalisation that stops it depending on an observation that varies, is explained in the part of its difference that edit accounts for.

## Validator
List every stored-output entry the hunk rewrites: entries of snapshot files, inline snapshot arguments, approved files, and golden files, the expected-output files a test compares its output against wherever they are stored; skip entries added for a new test. Open the base version of each rewritten entry at base-compare and diff its old value against the new one. Read the change's description and its production-code hunks to establish which visible behaviour the change intends to alter, and the hunks that edit the test owning each rewritten entry. Trace each rewritten entry to the code path it records: a difference that the intended alteration accounts for, in an entry whose test a production hunk reaches, or that an edit to the entry's own test accounts for, is explained; any other difference is unexplained, and a change described as preserving behaviour has only the second kind of explained rewrite. Validator question: **Does the change rewrite a stored snapshot, golden or approved entry whose difference from its base version neither the change's intended behaviour change nor an edit to that entry's own test explains?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: CHG-21`, severity major, `file`, `symbol`, `code` = the rewritten entry's old and new value as the diff shows them, `fix` = the entry restored to its base value with the bug fixed in the code under test, the intended behaviour change named for that entry, or the entry's test made to stop depending on the observation that varies (a matcher, redaction, sort or normalisation), in the file's language, `rationale` = the difference no intended behaviour change explains and the regression or unstable value it would record as expected output).
