---
title: A value that must appear in two places, such as a version number in the build file and in the code, is read from one place or checked by a test that fails when the copies differ
rule_id: DSN-25
domain: design
step: [implement, test]
applies_to: [universal]
triggers: ['(?i)\b(_*version_*["''`]?\s*[:=]\s*["''`]?v?\d+[.]\d+|version\w*\s*(:\s*&?(''static\s+)?\w+|\s+string)\s*=\s*["''`]v?\d+[.]\d+)', '(?i)\b(keep\s+(this\s+|these\s+|them\s+|it\s+)?in\s+sync|in\s+sync\s+with|(must|should)\s+(match|equal|be\s+(the\s+same\s+as|identical\s+to|kept\s+in\s+sync))|mirrors?\s+(the\s+)?(value|constant|definition)|if\s+you\s+(change|update)\s+this|when\s+(changing|updating)\s+this|(also|then)\s+(change|update)\s+(the\s+)?(value|constant|copy)\s+in)\b']
scope: callers
check_kind: semantic
severity_default: minor
---

# A value that must appear in two places, such as a version number in the build file and in the code, is read from one place or checked by a test that fails when the copies differ

## Thesis
When one value must appear in two places that are meant to hold the same value — a version number in the build file and in the code or in a readme, a value that a comment says must match another — one place is the single source that the other reads at build or run time, or an automated test fails when the two copies differ. Two copies written by hand and linked by neither a read nor a test, such as a constant whose only link to its twin is a comment asking to keep the two in sync, break the rule.

## Rationale
A value kept by hand in two places diverges when one copy is updated and the other is not, as when the version in the build file moves on while the copy in the documentation keeps the old number. For a version number, packaging documentation names two choices: live with the data-entry duplication and rely on automated testing to ensure the values do not diverge, or use a way the build system may offer to define a single source of truth. Where the import package and the distribution package are meant to share one version, it recommends an automated test that the version the code reports and the version in the installed package's metadata are the same value. The single source can be the build file, from which the build copies the value into the other locations that need it; a file or attribute in the source, from which the build extracts it; or a version-control tag, so that nobody updates the number by hand in the source. A compile-time directive can initialise a string variable with the contents of a file read at compile time, so the code reads the value and holds no copy of it. With the test arm, a copy left behind fails the test run: a test helper for one package ecosystem checks that the version a readme names is updated when the package version changes, and its tests fail when the two are out of sync. Test runners apply the same check to an example kept in documentation: they run the example and compare its output with the output the documentation states, to verify that the example still works as documented.

## Example
```go
bad:  // version must match the VERSION file.
      const version = "1.4.2"
good: //go:embed VERSION
      var rawVersion string
      var version = strings.TrimSpace(rawVersion)
```

## Limits
The rule holds where the two places are meant to hold the same value, the condition on which the packaging documentation recommends its test; a value that only happens to equal another, such as two unrelated timeouts that happen to share a value, is outside it. A copy that the build writes from one input is not hand-kept: the build may copy a version from the build file into the other locations where it is required, or extract it from the code at build time, and a project context that names such a build step rejects the finding for the values that step writes. Keeping both copies and relying on an automated test is one of the two arms the packaging documentation names, and the one left when the build system offers no way to define a single source. An example in documentation is a copy of what the code does: one that the test run executes and compares meets the rule, while prose that restates the code with no value a test could compare is outside it.

## Validator
Grep the added lines for a version string assigned to a name or a key, and for a comment that asks to keep a value in sync with another place, says it must match or equal one, or says it mirrors one. For each hit, take the value and its name and search the repository for a second hand-written copy: the build or package manifest, a version or release file, a configuration file, a readme or other document, a constant in another module; for a comment that names its twin, open the twin. Decide whether the two places are meant to hold the same value. Skip a value that only happens to equal another, a file marked as generated, and a value that a build step writes from one input. For a hand-kept pair, look for the link: the value read from the other place at build or run time (a compile-time file include, a lookup of the installed package's metadata, a value the build injects or generates), or a test that reads both copies and fails when they differ. A test that compares one copy with a literal written in the test is a third copy, not a check. Validator question: **Does the diff add or change a value meant to equal a hand-written copy elsewhere in the repository, with neither a read from a single source nor a test that fails when the two copies differ?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: DSN-25`, severity minor, `file`, `symbol`, `code` = the added line that writes the value, or the added comment that names its twin, quoted verbatim from the diff, `fix` = the value read from the single source at build or run time, or a test that reads both copies and fails when they differ, in the file's language, `rationale` = names both places that hold the value and states that neither reads the other and no test compares them).

## Source
- Python Packaging User Guide, "Single-sourcing the Project Version" (pypa/packaging.python.org `source/discussions/single-source-version.rst`): "Some projects may choose to simply live with the data entry duplication, and rely on automated testing to ensure the different values do not diverge. Alternatively, a project's chosen build system may offer a way to define a single source of truth for the version number."; the version "derived from a version control system *tag* ... rather than being manually updated in the source code"; options: "the version can be extracted from the VCS", "hard-coded into the `pyproject.toml` file -- and the build system can copy it into other locations it may be required", or hard-coded in the source, where "The build system can then extract it from the runtime location at build time."; "When the intention is that a distribution package and its associated import package share the same version, it is recommended that the project include an automated test case that ensures `import_name.__version__` and `importlib.metadata.version("dist-name")` report the same value" (fetched)
- version-sync crate README (mgeisler/version-sync `README.md`): "Rust projects typically reference the crate version number in several places, such as the `README.md` file. The version-sync crate makes it easy to add an integration test that checks that `README.md` is updated when the crate version changes."; "If the README or `html_root_url` is out of sync with the crate version, the tests fail."; its example: "the version number in `Cargo.toml` has been changed to 0.2.0 while the `README.md` and `html_root_url` still use 0.1.2. The tests now fail" (fetched)
- Go standard library, package `embed`, package documentation (golang/go `src/embed/embed.go`): "Go source files that import "embed" can use the //go:embed directive to initialize a variable of type string, []byte, or [FS] with the contents of files read from the package directory or subdirectories at compile time." (fetched)
- Go standard library, package `testing`, section "Examples" (golang/go `src/testing/testing.go`): "The package also runs and verifies example code. Example functions may include a concluding line comment that begins with "Output:" and is compared with the standard output of the function when the tests are run." (fetched)
- Python documentation, `doctest` (python/cpython `Doc/library/doctest.rst`), introduction: "To check that a module's docstrings are up-to-date by verifying that all interactive examples still work as documented." (fetched)
- Caveat: the documentation states both arms for a version number and the test arm for a readme's version and for documented examples; the card applies the same two arms to any value kept by hand in two places, and no source measures how often such copies diverge.
