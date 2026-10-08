---
title: A behaviour that a test of its own components can detect in one process or against local dependencies is not verified only through a UI-driven or whole-system test
rule_id: TST-27
domain: tests
step: [design, test, review]
applies_to: [tests]
triggers: ['[.]([Gg]oto|[Vv]isit|[Nn]avigate\w*)\(\s*[\x22\x27\x60]', '\b(find_element|findElement|FindElement|querySelector|query_selector|getByRole|getByText|getByTestId|GetByRole|GetByText|GetByTestId|get_by_role|get_by_text|get_by_test_id)\(', '[.]([Cc]lick|[Dd]blclick|[Ff]ill|sendKeys|send_keys|SendKeys)\(', '(?i)\b(e2e|end[_-]?to[_-]?end|system[_-]?tests?|acceptance[_-]?tests?)\b', 'signal:added_file']
scope: callers
check_kind: semantic
severity_default: minor
---

# A behaviour that a test of its own components can detect in one process or against local dependencies is not verified only through a UI-driven or whole-system test

## Thesis
A behaviour that lives in one component, or in the interaction of a few, is verified by a test that runs those components in one process or against local dependencies. A UI-driven or whole-system test may exercise that behaviour as well; it is the behaviour's sole test only where no such narrower test can observe it.

## Rationale
Broadly, a flaky test indicates that it relies on system state that is not being appropriately controlled, and higher-level tests are more likely to be flaky as they rely on more state. A flaky test whose functionality other tests cover may be removed; otherwise it may be rewritten at a lower level, which removes the flakiness or makes its source more apparent. In a study of flaky UI-based tests from web and mobile projects, the largest root-cause category is waiting on asynchronous work: network resource loading 19, resource rendering 61 and animation timing 26 of 235 root causes; 73 of 236 fixes removed the test. In industry, a significant fraction of system tests for services-based implementations, typically non-hermetic, exhibit some level of flakiness, so completely eliminating flaky tests is not a realistic option. For other than small, simple software, incremental integration testing is usually preferred to putting all of the components together at once. A test confined to the components that hold the behaviour relies on less state than one that drives the whole system, and that smaller dependence on state is the property the rule secures.

## Example
```java
bad:  @Tag("e2e") @Test void appliesBulkDiscount() {
        page.navigate("/cart?items=10");
        page.getByText("Checkout").click();
        assertEquals("90.00", page.getByTestId("total").textContent()); }
good: @Test void appliesBulkDiscount() {
        Cart cart = new Cart(new PriceList());
        cart.add(item, 10);
        assertEquals(new BigDecimal("90.00"), cart.total()); }
```

## Limits
Where no narrower test can observe the behaviour, a UI-driven or whole-system test may be its sole test, and the rule does not apply. A UI-driven or whole-system test of a user path whose behaviours narrower tests also verify is outside the rule; the rule does not ask for end-to-end tests of critical user paths to be removed. A test that renders and drives a user-interface component inside the test's own process runs in one process and counts as a narrower test; the UI-driven tests the rule reaches drive the interface from outside the test's process, in a browser, on a device or through the running system. A UI-driven or whole-system test added for a behaviour that the change leaves untouched is outside the check. The preference for incremental integration is stated for software other than small and simple; for small, simple software the evidence states no preference. The evidence compares test levels by the state each relies on and states no proportion, so the rule sets no ratio between unit, integration and whole-system tests in a suite.

## Validator
Grep the hunk's added test code for UI-driving calls (navigation to a URL, element lookup by role, text, test id or selector, click, fill or key input) and for end-to-end, system or acceptance test names and tags. Continue only when the change also adds or changes the code that computes a value the test asserts, and trace each asserted value to that code. Open the usages of that changed code across the repository and look among them, and in the change, for a test that runs it, alone or with the few components it interacts with, in one process or against local dependencies and asserts the same behaviour. Validator question: **Does the added UI-driven or whole-system test verify a behaviour that the change adds or changes and that a test of its own components could observe in one process or against local dependencies, with no such test in the change or among the usages of the changed code?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: TST-27`, severity minor, `file`, `symbol`, `code` = the UI-driving or whole-system call and the assertion it feeds, quoted verbatim from the diff, `fix` = a test that constructs the component computing the asserted value and asserts it in one process or against a local dependency, in the file's language, `rationale` = the component that computes the asserted value and the state the larger test relies on beyond it).

## Source
- pytest documentation, 'Flaky tests' (pytest-dev/pytest `doc/en/explanation/flaky.rst`), 'System state' and 'Delete or rewrite the test': "Higher level tests are more likely to be flaky as they rely on more state." "If the functionality is covered by other tests, perhaps the test can be removed. If not, perhaps it can be rewritten at a lower level which will remove the flakiness or make its source more apparent." (fetched)
- doi:10.1109/ICSE43902.2021.00141 (arXiv:2103.02669); counts from the study website https://raw.githubusercontent.com/ui-flaky-test/ui-flaky-test.github.io/main/index.html, whose Table 4 marks cells changed to new category names and counts, Tables 4 and 6: "We found that the highest causes of flakiness come from causes under Async Wait." [Network Resource Loading 19, Resource Rendering 61, Animation Timing Issue 26, Total 235; Remove Test 73, Total 236] (fetched)
- doi:10.1145/3377813.3381370, abstract: "Completely eliminating flaky tests is not a realistic option as a significant fraction of system tests (typically non-hermetic) for services-based implementations exhibit some level of flakiness." (fetched)
- IEEE SWEBOK V3.0 ch. 4 §2.1.2 'Integration Testing': "For other than small, simple software, incremental integration testing strategies are usually preferred to putting all of the components together at once - which is often called “big bang” testing." (fetched)
- Caveat: the UI study counts flaky UI-based tests only and the industrial abstract names no cause of the flakiness; the comparison between test levels rests on the pytest documentation.
