---
title: A regular expression added or changed to validate or extract input is tested with values it must accept, values it must reject and near-matching values that differ from an accepted one at a boundary
rule_id: INP-20
domain: input
step: [test]
applies_to: [universal]
triggers: ['(re[.]compile|Pattern[.]compile|new RegExp|regexp[.](Must)?Compile|Regex::new)\(|@Pattern\(\s*regexp|=\s*/[^/\s][^/]*/[dgimsuy]*\s*;?\s*$', '\b(fullmatch|matches|MatchString|is_match)\(|\bre[.](match|search|findall|finditer)\(|/[^/\s][^/]*/[dgimsuy]*[.](test|exec)\(|[.](match|matchAll)\(\s*/[^/\s]']
scope: callers
check_kind: semantic
severity_default: minor
---

# A regular expression added or changed to validate or extract input is tested with values it must accept, values it must reject and near-matching values that differ from an accepted one at a boundary

## Thesis
A regular expression added or changed to validate or extract input is covered by tests that pass it three kinds of values: values it must accept, values it must reject that are not near matches, and near-matching values. A near-matching value is one the pattern must reject that differs from an accepted value at one boundary of the pattern, such as characters added or removed at either end, a trailing newline, or a length one past the bound the input is held to.

## Rationale
Incorrect behaviour of the regular expression itself is the dominant root cause of regular-expression bugs: 165 of 356 (46.3%) in a study of 350 merged regex-related pull requests from Apache, Mozilla, Facebook and Google repositories, where fixing such bugs took more time and more lines of code than general pull requests. The testing techniques asked of a regular expression include equivalence partitioning, boundary value analysis and robustness testing: accepted and rejected values sample the partitions, and near-matching values sit on the boundaries between them. A pattern without anchors, applied with a call that searches for a match rather than matching the whole value, accepts extra text around a matching part: a digits-hyphen-digits check passes `; ls -l ; echo 123-456`, and an address pattern passes an address with `0x` prepended, which the downstream command then reads as hexadecimal. Character classes and newline behaviour can differ between engines and languages, so a trailing newline is a near match whose outcome a test fixes; where input length is bounded, boundary value analysis places a value at the bound and one past it. Near-matching values can also make a regular expression cause denial of service.

## Example
```java
bad:  static final Pattern CODE = Pattern.compile("[A-Z]{3}-\\d{4}");
      @Test void accepts() { assertTrue(CODE.matcher("ABC-1234").matches()); }
good: static final Pattern CODE = Pattern.compile("[A-Z]{3}-\\d{4}");
      @Test void accepts() { assertTrue(CODE.matcher("ABC-1234").matches()); }
      @Test void rejects() { assertFalse(CODE.matcher("abc").matches()); }
      @Test void rejectsNearMatches() {
          for (String s : List.of("XABC-1234", "ABC-1234\n", "ABC-123", "ABC-12345"))
              assertFalse(CODE.matcher(s).matches(), s);
      }
```

## Limits
Testing brings a regular expression to a reasonable confidence level without making it foolproof: a value that slips through is recorded and the expression refactored, and a large expression is checked for whether several smaller ones would simplify it. The guidance names the three kinds of values and no count, so one value of each kind meets the rule. A pattern the change does not add or alter, or one that neither validates nor extracts input, is outside the rule.

## Validator
Grep the hunk for a regular expression being compiled, written as a literal, attached as a validation annotation or applied with a match call. Read the value it is applied to and confirm that it validates or extracts input. Open the callers of the routine that holds the pattern and the tests that exercise them, and sort every value those tests pass through the pattern into accepted, rejected and near-matching ones. Count a value as near-matching only when the pattern must reject it and it differs from an accepted value at one boundary of the pattern, such as characters added or removed at either end, a trailing newline or a length one past a bound. Validator question: **Does a regular expression the hunk adds or changes to validate or extract input lack a test with a value it must accept, a value it must reject that is not a near match, or a near-matching value?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: INP-20`, severity minor, `file`, `symbol`, `code` = the line that compiles, declares or applies the regular expression, quoted verbatim from the diff, `fix` = the missing test cases with accepted, rejected and near-matching values for that pattern, in the file's language, `rationale` = which of the three kinds of value the tests lack and the boundary a near match would probe).

## Source
- OWASP Input Validation Cheat Sheet, §Implementing Input Validation > Regular Expressions (Regex) (OWASP/CheatSheetSeries master cheatsheets/Input_Validation_Cheat_Sheet.md) (fetched): "Test valid, invalid, and near-matching values; [...] near-matches can cause denial of service."; "Check the engine's character classes and newline behavior rather than assuming patterns behave identically across languages."; "Bound input length before matching".
- CWE-185 Incorrect Regular Expression, Description, PotentialMitigations MIT-45 and DemonstrativeExamples (CWE-CAPEC/REST-API-wg main json_repo/W/185.json) (fetched): "The product specifies a regular expression in a way that causes data to be improperly matched or compared."; "subject the regular expression to thorough testing techniques such as equivalence partitioning, boundary value analysis, and robustness. After testing and a reasonable confidence level is achieved, a regular expression may not be foolproof. If an exploit is allowed to slip through, then record the exploit and refactor the regular expression."; "Determine if several smaller regular expressions simplify one large regular expression."; "\"; ls -l ; echo 123-456\" This would pass the check"; "the regular expression does not have anchors (CWE-777), i.e. is unbounded without ^ or $ characters, then prepending a 0 or 0x to the beginning of the IP address will still result in a matched regex pattern. Since the ping command supports octal and hex prepended IP addresses, it will use the unexpectedly valid IP address".
- .NET regular expression best practices (dotnet/docs main docs/standard/base-types/best-practices-regex.md) (fetched): "Text that nearly matches the regular expression pattern."; "its performance is inefficient when it's processing nearly valid input"; "Thoroughly test your regular expression using invalid, near-valid, and valid input."
- doi:10.1145/3379597.3387464 (MSR 2020), abstract (fetched): "a comprehensive empirical study of 350 merged regex-related pull requests from Apache, Mozilla, Facebook, and Google GitHub repositories"; "incorrect regular expression behavior is the dominant root cause of regular expression bugs (165/356, 46.3%)"; "it takes more time and more lines of code to fix them compared to the general pull requests".
- Caveat: the guidance recommends the three kinds of test values and the study counts bug causes; neither measures how many bugs near-match tests prevent.
