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

## Source
- google/eng-practices, review/developer/cl-descriptions.md, "Body is Informative": "If there are any shortcomings to the approach, they should be mentioned."; same document: "A CL description is a public record of change", "The CL description will become a permanent part of our version control history", "Future developers will search for your CL based on its description", and on its example description: "that the solution isn't ideal, and possible future direction" (fetched)
- rust-lang/rust-forge, src/compiler/reviews.md, "Basic Reviewing Requirements": "authors are encouraged to list potential **points of contention**, **compromises** that needed to be made, **alternative approaches** that have been considered"; "Reviewing code is difficult, and reviewers only have a **limited amount of time** to do it. Jump-starting the review process by not making the reviewer puzzle together the intention and context of a pull request will not only speed things up but also improve the quality of the review."; section "Reviewer and PR author report to the same entity / work for the same employer": "so that contributors down the line can follow the reasoning and reconstruct what's going on" (fetched)
- Linux kernel, Documentation/process/submitting-patches.rst, "Describe your changes": "Optimizations usually aren't free but trade-offs between CPU, memory, and readability"; "Describe the expected downsides of your optimization so that the reviewer can weigh costs against benefits." (fetched)
- Go standard library documentation, package testing (pkg.go.dev/testing), section "Skipping": "Tests or benchmarks may be skipped at run time with a call to T.Skip or B.Skip", with the example `func TestTimeConsuming` that calls `t.Skip("skipping test in short mode.")` only `if testing.Short()` (fetched)
- rust-lang/book, src/ch11-02-running-tests.md, "Ignoring Tests Unless Specifically Requested": "Sometimes a few specific tests can be very time-consuming to execute, so you might want to exclude them during most runs of `cargo test`"; "annotate the time-consuming tests using the `ignore` attribute to exclude them"; "If you want to run all tests whether they’re ignored or not, you can run `cargo test -- --include-ignored`." (fetched)
- Caveat: the three sources on the description are project documentation stating the practice and its purpose, none measures its effect, and the kernel text scopes its downsides sentence to optimizations; the two testing sources bound the Limits only.
