---
title: A change to a value in a configuration file the program ships or deploys with is tested by running the code that reads it with the new value, not only by checking the value's syntax or range
rule_id: TOOL-32
domain: tooling
step: [test, review]
applies_to: [build-config]
triggers: ['^\s*["'']?[A-Za-z_][\w.-]*["'']?\s*[=:]\s*(?:"[^"]*"|''[^'']*''|[^\s"''(){};,]+)\s*,?\s*$']
scope: callers
check_kind: semantic
severity_default: major
---

# A change to a value in a configuration file the program ships or deploys with is tested by running the code that reads it with the new value, not only by checking the value's syntax or range

## Thesis
A change to a value in a configuration file the program ships or deploys with is exercised by at least one test that runs the code reading that setting with the new value, in addition to any check of the value's syntax or range. A test that resets the setting to a value of its own does not count, because it cannot be applied to other valid values of the setting.

## Rationale
Configuration changes are prevalent causes of production failures: at one large web company thousands of configuration changes are committed daily, outpacing code changes, and 16% of its service-level incidents, including major outages, are induced by configuration changes; at another, faulty configurations are the second largest cause of service disruptions in a main production service. In the experience of researchers who analyzed hundreds of configuration-induced incidents, failure-inducing configuration changes are rarely trivial mistakes such as typos, a rarity attributed to practices that enforce change review and validation. Their root causes commonly reside in the program and not in the changed configuration: failures typically occur when a valid change exposes a dormant bug in the code or violates an undocumented, hidden constraint. Techniques that check only configuration values cannot detect common types of such changes, those that cause code to fail or violate hidden constraints, and review and validation of the change alone can hardly detect them. Running tests with the changed configuration, in the context of the code it affects, detected the failure-inducing configuration in 96.9% (62 of 64) of real-world configuration-induced failures: 79.7% (51 of 64) with tests generated automatically from the existing suites, the other 17.2% (11 of 64) after rewriting a test, in 9 of those 11 only by removing an unnecessary reset of the value inside the test. Each of those failures was caused by a value different from the program's default. The detecting tests were transformed from the older version of each system on which the failure was reported, so they could have detected the failures earlier.

## Example
```go
bad:  batch_size = 64
      func TestRun(t *testing.T) {
          cfg := mustLoad(t, "deploy/app.conf")
          cfg.BatchSize = 64
          if err := run(cfg, sampleInput()); err != nil { t.Fatal(err) }
      }
good: func TestRunWithShippedConfig(t *testing.T) {
          cfg := mustLoad(t, "deploy/app.conf")
          if err := run(cfg, sampleInput()); err != nil { t.Fatal(err) }
      }
```

## Limits
A test that resets a setting to a specific value because its logic or oracle depends on that value is an intended reset and stays as it is; it covers that value only. A reset that only sets up the test environment, such as a test file, address or port, is not needed when the test runs with the actual configuration, and removing it lets the test check the configured value. Testing a configuration change with the code complements validation of its values, as software testing complements static analysis for bug detection. Tests generated this way, without rewriting, missed 28.4% (300 of 1,055) of injected misconfigurations; 75.3% of those misses came from tests that did not expose the effect or had no oracle to check it, and many of those effects were non-functional, such as performance. The figures come from five mature open-source cloud systems whose existing test suites were transformed into the tests. A changed default value in code is outside the rule. Rolling a configuration change out across a fleet is outside the rule.

## Validator
Grep the hunk for changed `key = value`, `key: value` or `"key": value` lines, with the key in any case and dotted or not, in a configuration file the program ships or deploys with; skip comments and test fixtures. For each changed setting, find the code that reads it, open its callers and the tests that reach that code, and check whether a test in the change or in the existing suite runs that code with the configuration as changed, by loading the shipped or deployed file rather than setting its own value. Validator question: **Does the change alter a value in a configuration file the program ships or deploys with while no test runs the code that reads that setting with the new value?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: TOOL-32`, severity major, `file`, `symbol`, `code` = the changed configuration line verbatim, `fix` = a test, in the language of the code that reads the setting, that loads the shipped or deployed configuration file and runs that code with it, `rationale` = the changed setting, the code that reads it, and the missing test that runs that code with the new value).
