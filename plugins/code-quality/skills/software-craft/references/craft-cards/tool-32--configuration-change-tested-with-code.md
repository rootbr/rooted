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
bad:  func TestRun(t *testing.T) {
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

## Source
- OSDI 2020, "Testing Configuration Changes in Context to Prevent Production Failures", Abstract — https://raw.githubusercontent.com/tianyin/tianyin.github.io/master/pub/ctest.pdf (fetched): "configuration changes have inevitably become prevalent causes of production failures. Existing misconfiguration detection and configuration validation techniques only check configuration values. These techniques cannot detect common types of failure-inducing configuration changes, such as those that cause code to fail or those that violate hidden constraints." · "connecting production system configurations to software tests so that configuration changes can be tested in the context of code affected by the changes"
- Same paper, §1.1 (fetched): "at Facebook, thousands of configuration changes are committed daily, outpacing the frequency of code changes" · "faulty configurations are the second largest cause of service disruptions in a main Google production service [5]. At Facebook, 16% of service-level incidents, including major outages [54], are induced by configuration changes" · "Based on our experience from analyzing hundreds of configuration-induced incidents, failure-inducing configuration changes are rarely caused by trivial mistakes (e.g., typos). This rarity is attributed to the DevOps practices that enforce change review and validation" · "they commonly reside in the program and not in the changed configurations. Failures typically occur when valid configuration changes expose dormant software bugs [55] and when configuration changes violate undocumented, hidden configuration constraints." · "Review and validation of configuration changes alone can hardly detect failures resulting from these root causes."
- Same paper, §1, §6.1 and §6.1.1 (fetched): "Each failure was reported by real system users and was caused by a configuration change (i.e., a value different from the default was used)." · "The ctests that detected these real-world failures were transformed from the tests in the older version of the systems on which the failures were reported. That is, ctests could have detected these failures earlier." · "96.9% (62/64) of the failure-inducing configurations are detected by ctests. ... 79.7% (51/64) of all failures are detected by using only generated ctests; the other 17.2% (11/64) require rewriting of ctests (§5.4). In 9 of the 11 failures that require rewriting, we only remove unnecessary value resets"
- Same paper, §3.2, §4.2.2 and §4.3 (fetched): "Ctests are complementary to configuration validation, similar to how software testing complements static analysis for bug detection." · "Respecting intended configuration resets. If a test explicitly resets a configuration parameter to a specific value, then the test logic or its oracle depends on the new value. So, the test cannot be applied to other valid values of the configuration parameter." · "many configuration resets in test code are used for setting up the test environment, e.g., a test file, address, port, etc. Those resets are not needed in ctests which are run with actual environment variables. ... by simply removing the reset, the ctest can check alluxio.master.rpc.port's values."
- Same paper, §5 and §6.2.1 (fetched): "transforming existing tests in five mature and widely-used open-source cloud systems" · "The generated ctests failed to detect 28.4% (300 of 1055) injected misconfigurations ... Recall that we do not rewrite tests in this evaluation" · "75.3% of false negatives are due to inadequacy of ctests that either does not expose the effects of the misconfigurations or does not have oracles to check the effects. Many of these effects are nonfunctional (e.g., performance issues)."
- Caveat: the incident figures are the paper's citations of other studies, not opened here; the evaluation covers five open-source cloud systems with mature test suites.
