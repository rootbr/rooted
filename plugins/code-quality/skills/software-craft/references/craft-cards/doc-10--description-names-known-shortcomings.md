---
title: A change whose approach leaves a known shortcoming, such as a case it does not handle, a test it skips or work it defers, names that shortcoming in its description
rule_id: DOC-10
domain: docs
step: [review, document]
applies_to: [universal]
triggers: ['signal:todo_marker', '(?i)\b(not (yet )?(supported|implemented)|unsupported|unimplemented|known (issue|limitation)s?|limitation)\b', '@(Disabled|Ignore)\b|\bpytest[.]mark[.](skip|xfail)\b|@unittest[.](skip|expectedFailure)|#\[ignore\b|\bt[.]Skip(Now|f)?\(|\b(it|test|describe)[.](skip|todo)\(', '\b(todo|unimplemented)!\(|\bNotImplemented(Error)?\b|UnsupportedOperationException']
scope: base-compare
check_kind: semantic
severity_default: suggestion
---

# A change whose approach leaves a known shortcoming, such as a case it does not handle, a test it skips or work it defers, names that shortcoming in its description

## Thesis
When the approach a change takes has a known shortcoming, the change description mentions that shortcoming.

## Rationale
The change description is a public record of the change and becomes a permanent part of version control history, where future developers search for the change by its description. Reviewing code is difficult and reviewers have a limited amount of time; authors are encouraged to list the points of contention, the compromises that had to be made and the alternative approaches considered, because sparing the reviewer the work of puzzling together the intention and context of a change speeds the review and improves its quality. For an optimization, which usually trades CPU, memory and readability against one another, a description of its expected downsides lets the reviewer weigh costs against benefits. A good description can say that the solution is not ideal and name the possible future direction, and a clear, transparent rationale lets contributors down the line follow the reasoning and reconstruct what is going on.

## Example
```python
bad:  # change description: "Add CSV export."
      @pytest.mark.xfail(raises=NotImplementedError, reason="xlsx not supported yet")
      def test_export_xlsx():
          export(ROWS, "xlsx")  # TODO: xlsx
good: # change description: "Add CSV export; XLSX is not supported yet,
      #   so its test is marked xfail until a follow-up adds it."
      @pytest.mark.xfail(raises=NotImplementedError, reason="xlsx not supported yet")
      def test_export_xlsx():
          export(ROWS, "xlsx")  # TODO: xlsx
```

## Limits
The rule is conditional: a change whose approach has no known shortcoming owes its description no such mention. It reaches shortcomings of the approach the change takes; a limitation the API documents as its intended contract is behaviour the change delivers, not a shortcoming of its approach. A test skipped only in a short run, or left out of the default run because it is time-consuming and run on request, still runs in the full run and marks no shortcoming either. It reaches the description only: whether a marker in the code names its tracking issue, and whether a placeholder may ship at all, are judged by the checks on those markers. The documentation says shortcomings should be mentioned and encourages listing compromises and points of contention; it states no measured effect, so the finding is a suggestion.

## Validator
Grep the hunk for a mark of a known shortcoming: a deferral marker, a skipped, ignored or expected-to-fail test, a placeholder body, or code that rejects an input as not yet supported or not implemented. Pass over a rejection that the API's documentation states as its intended contract, and a test skipped only in a short run or left out of the default run because it is time-consuming. Open the change description (the commit message or the pull-request body) and look for a sentence that names the case, the test or the deferred work the mark stands for. When no change description is available to read, emit no finding. Validator question: **Does the hunk add a mark of a known shortcoming in the change's approach that the change description leaves unmentioned?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: DOC-10`, severity suggestion, `file`, `symbol`, `code` = the line that marks the shortcoming, quoted verbatim from the diff, `fix` = a sentence for the change description that names the unhandled case, skipped test or deferred work and its follow-up, `rationale` = the shortcoming the description leaves unmentioned and the reviewer's need to weigh what the change leaves undone).
