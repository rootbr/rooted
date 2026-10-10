---
title: A bug fix corrects the same mistake in the other places that repeat it, including code with a similar role that is not a textual copy, and not only where the reported failure surfaced
rule_id: PRF-03
domain: performance
step: [implement, review]
applies_to: [universal]
triggers: ['(?i)\b(fix(es|ed)?|closes?|resolves?)\b\s*[#:]?\s*[A-Z]*-?\d+', '(?i)(?<!de)(regression|bug|issue)[_ -]?#?[A-Z]*-?\d{2,}', '(?i)(^|[^a-z]|(?<=test))regression([^a-z]|$|(?=test))']
scope: callers
check_kind: semantic
severity_default: major
---

# A bug fix corrects the same mistake in the other places that repeat it, including code with a similar role that is not a textual copy, and not only where the reported failure surfaced

## Thesis
When a change fixes a bug, the code is searched for the mistake the fix corrects, and each other place that repeats it is corrected in the same change, whether or not its text matches the fixed lines: a code peer with a similar role, a missed port of the same change, or code that an incomplete refactoring left behind.

## Rationale
In Eclipse JDT core, Eclipse SWT and Mozilla, 22% to 33% of resolved bugs involved more than one fix attempt: the initial patch was later considered incomplete and programmers applied a supplementary patch. Such an incomplete fix is an error of omission, and a prior study found that errors of omission are harder for programmers to detect than errors of commission; the causes of these omissions were diverse, including missed porting changes, incorrect handling of conditional statements and incomplete refactorings. A large percentage of recurring bug fixes occur in code peers, the classes and methods with similar roles, such as providing similar functions or participating in similar object interactions. Only 12% (JDT), 25% (SWT) and 9% (Mozilla) of the supplementary patches had content similar to their initial patches, so the locations an initial fix leaves out cannot be predicted by code clone analysis alone. For security vulnerabilities, variant analysis seeds a query with the known vulnerability to find logical variants of the same bug that could be missed using traditional manual techniques. The property the search targets is the one these supplementary patches show missing: a fix completed in its first attempt.

## Example
```java
bad:  // fixes BUG-42, a regression: reject a blank name
      void create(String name) { if (name.isBlank()) throw new IllegalArgumentException(); store(name); }
      void rename(Item item, String name) { item.setName(name); }
good: void create(String name) { requireName(name); store(name); }
      void rename(Item item, String name) { requireName(name); item.setName(name); }
      static void requireName(String name) { if (name.isBlank()) throw new IllegalArgumentException(); }
```

## Limits
A caller that reaches the corrected routine through a call, rather than repeating its logic, does not repeat the mistake, and a fix whose search finds no repeat is complete at the failure site. A verbatim copy of the edited block left unchanged is reported as duplicated code rather than here; this check reaches the repeats whose text differs. Of the files in supplementary patches, 14% to 15% neither overlapped the initial patch locations nor had direct structural dependencies on them, such as calls, accesses or subtyping relations; this check reaches such a file only when it is a peer opened from the callers or from the module or type the corrected routine sits in, namely a sibling routine that takes the same input or writes the same state, another implementation of the same interface or base type, a routine using the same API under the same condition, the port counterpart, or the old or new home of moved code, and a repeat in any other file lies beyond this check and within reach of a whole-codebase search seeded by the known bug. A data race, a deadlock or another concurrency failure, and a failure traced across services, lie outside this rule; the finder names them and stops.

## Validator
Grep the hunk, its commit message, test names and comments for a fix reference or the word regression, and read what the hunk corrects: the condition, check, boundary, argument, call order or cleanup it adds or changes, and the routine it sits in. Open the callers of that routine and, from them and from the module or type the routine sits in, the routines with a similar role: sibling routines that take the same input or write the same state, other implementations of the same interface or base type, routines that use the same API under the same condition, the counterpart the change was ported from or to, and the old and new homes of code a refactoring moved. In each, trace whether the same input or state reaches the faulty form the hunk replaced; skip verbatim copies of the edited block. Validator question: **Does a place in scope that the change leaves untouched, other than a verbatim copy of the edited block, still carry the mistake the change corrects?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: PRF-03`, severity major, `file`, `symbol`, `code` = the corrected line from the diff and the untouched line that still carries the mistake, each quoted verbatim, `fix` = the same correction applied at the untouched place, in the file's language, `rationale` = the mistake the fix corrects and the peer, port or refactoring leftover that still carries it).
