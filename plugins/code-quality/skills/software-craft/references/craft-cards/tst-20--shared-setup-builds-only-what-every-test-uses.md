---
title: Setup that runs for every test of a file, class or suite builds only what all of those tests use, and setup that only some tests need is called from those tests
rule_id: TST-20
domain: tests
step: [test, refactor]
applies_to: [tests]
triggers: ['@(BeforeEach|Before|BeforeAll|BeforeClass|BeforeMethod)\b', '^\s*def\s+(setUp|setUpClass|setUpModule|setup_method|setup_class|setup_module|setup_function)\s*\(', '\b(beforeEach|beforeAll)\s*\(', '^\s*func\s+(init\s*\(\s*\)|TestMain\s*\(\s*\w+\s+\*testing[.]M\s*\))', '@pytest[.]fixture\(.*\bautouse\s*=\s*True']
scope: callers
check_kind: semantic
severity_default: minor
---

# Setup that runs for every test of a file, class or suite builds only what all of those tests use, and setup that only some tests need is called from those tests

## Thesis
Where possible, a setup hook that runs before each test, a once-per-class or once-per-module initialiser, a package-level initialisation and an automatically applied fixture build only the objects and resources that every test in their scope uses. Setup that only some of those tests need is a helper that those tests call explicitly, so a test run on its own pays for no setup it does not use.

## Rationale
A setup or fixture routine that initialises fields some tests in its scope never access is too general, and every run of such a test does unnecessary work. Realistic setup is often complex, error-prone and potentially slow, so a test that does not need it still waits for it and can fail on it. A developer may wish to run one test in isolation of the others and should not be penalized by setup that test does not use. Fixtures shared by a whole class or module do not play well with features such as test parallelization and they break test isolation, so they are used with care. Calling the setup explicitly from the tests that need it scopes each resource as closely to those tests as possible, and a test that does not use the resource does not build it.

## Example
```go
bad:  var dataset []byte
      func init() { dataset = mustLoadDataset() }
      func TestParse(t *testing.T) { ... }     // reads dataset
      func TestGuessHost(t *testing.T) { ... } // never reads it
good: func TestParse(t *testing.T) {
          data := mustLoadDataset(t)
          ...
      }
      func TestGuessHost(t *testing.T) { ... }
```

## Limits
When all tests of a package or suite require a common setup and that setup requires teardown, a custom entry point that wraps the whole test run fits; this can happen when the resource is especially expensive to set up and its cost should be amortized, typically after unrelated tests have been extracted from the suite, and it is not the first choice because its correct use takes care. A lazily initialised, run-once helper that only the tests needing it call is the scoped form, and it may be appropriate, though not required, when the setup is expensive, applies only to some tests and needs no teardown.

## Validator
Grep the hunk for a setup hook that runs for every test in a scope: a before-each or before-all annotation or call, a per-test, per-class or per-module setup method, an automatically applied fixture, a package initialisation function, or a suite entry point. Open the file and list each field, variable or resource the hook builds. For each one, trace which tests in the hook's scope use it, directly, through a helper they call or through the code under test they run; for a package-level or module-level hook, the scope is every test file of that package or module, so look up usages of each built symbol across those files before deciding. Pass a suite entry point whose setup every test in its scope needs and which requires teardown, and pass a lazily initialised helper that only the tests needing it call. Validator question: **Does a setup hook that runs for every test in its scope build an object or resource that at least one test in that scope never uses?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: TST-20`, severity minor, `file`, `symbol`, `code` = the hook's line that builds the unused object or resource, verbatim from the diff, `fix` = that construction moved into a helper which only the tests that use it call, in the file's language, `rationale` = the test in the hook's scope that never uses the object and the setup each of its runs pays for).
