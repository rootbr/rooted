---
title: An automated test replaces any third-party server or external site the team does not control at its boundary
rule_id: TST-35
domain: tests
step: [test, review]
applies_to: [tests, service-boundary]
triggers: ['https?://(?!localhost\b|127[.]0[.]0[.]1\b|0[.]0[.]0[.]0\b|\[::1\]|(www[.])?example[.](com|org|net)\b)[\w-]+([.][\w-]+)+', '\b(requests[.](get|post|put|patch|delete)|http[.](Get|Post|Head)|axios[.]\w+|urlopen|reqwest::get|fetch)\(', '(?i)\b(api[_-]?key|secret[_-]?key|access[_-]?token|client[_-]?secret)\b\s*[:=]', '(?i)\b(sandbox|staging|prod|production)[.-][\w-]+([.][\w-]+)*[.](com|io|net|org|dev)\b']
scope: hunk
check_kind: semantic
severity_default: major
---

# An automated test replaces any third-party server or external site the team does not control at its boundary

## Thesis
An automated test sends its requests only to systems the team controls. A third-party server or its API, or an external website, whose content and availability the team does not control is replaced at that boundary by a stand-in that guarantees the response the test needs.

## Rationale
A server the team does not control is time-consuming to reach and can slow the tests down, its content can change, and it can show cookie banners or overlay pages or have issues outside the team's control, any of which might cause the test to fail. Eliminating the dependencies on external services greatly improves the speed and the stability of the tests. Network dependency, a category that covers remote connection failures as well as local socket or port handling, is a major source of flaky tests: 6% of the flaky-test fixes in one study of 51 open-source projects, 14% of the flaky tests in six large-scale Microsoft projects, 413 flaky tests in one single-language study, and 13% of the causes of flakiness in another. Tests that rely directly on resources accessed over the network are still common, although many programmers prefer to mock the APIs and services that need network connectivity.

## Example
```go
bad:  apiKey := os.Getenv("RATES_API_KEY")
      app := httptest.NewServer(NewApp("https://sandbox.thirdparty.com", apiKey))
      resp, err := http.Get(app.URL + "/convert?usd=10")
good: rates := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
          fmt.Fprint(w, `{"usd": 1.0}`)
      }))
      defer rates.Close()
      app := httptest.NewServer(NewApp(rates.URL, "test-key"))
      defer app.Close()
      resp, err := http.Get(app.URL + "/convert?usd=10")
```

## Limits
A domain or hosted instance the team controls, such as its own instance of an authentication or content-management service, counts as controlled and may stay real. Which kind of stand-in takes the server's place, and a check against the real service that runs on its own schedule, apart from the tests run on every change, lie outside this rule.

## Validator
Grep the hunk's test code for a URL whose host is neither loopback nor a reserved example domain, an outbound HTTP call, a credential assignment, or a sandbox, staging or production hostname. Open each matching test at hunk scope and trace every request to the host it reaches: a server the test or its fixture starts, a domain or hosted instance the team controls, or a server outside the team's control. A test that a build tag, a marker or an opt-in flag in the hunk keeps out of the tests run on every change, so that it checks the real service on its own schedule, is outside this rule and is not flagged. Validator question: **Does a test in the hunk send a request to a server whose content and availability the team does not control, with no stand-in at that boundary?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: TST-35`, severity major, `file`, `symbol`, `code` = the line in the diff that names the uncontrolled host or sends the request to it, quoted verbatim, `fix` = the test with that server replaced at its boundary by a stand-in that serves the response the test needs, in the file's language, `rationale` = the uncontrolled server and what it costs the test: slower runs, content that can change, and failures outside the code under test).

## Source
- Playwright documentation, Best Practices › Testing philosophy › Avoid testing third-party dependencies (microsoft/playwright, docs/src/best-practices-js.md) (fetched): "Only test what you control. Don't try to test links to external sites or third party servers that you do not control. Not only is it time consuming and can slow down your tests but also you cannot control the content of the page you are linking to, or if there are cookie banners or overlay pages or anything else that might cause your test to fail." · "Instead, use the [...] Network API and guarantee the response needed."
- Cypress documentation, Best Practices › Visiting External Sites (cypress-io/cypress-documentation, docs/app/core-concepts/best-practices.mdx) (fetched): "Only test websites that you control. Try to avoid visiting or requiring a 3rd party server. If you choose, you may use cy.request() to talk to 3rd party servers via their APIs. If possible, cache results via cy.session() to avoid repeat visits." · "you will only want to use these commands for resources in your control, either by controlling the domain or hosted instance" · "Authentication as a service platforms [...] These domains and service instances are usually owned and controlled by you or your organization." · "CMS instances" · "The 3rd party site may have changed or updated its content." · "The 3rd party site may be having issues outside of your control."
- Selenium documentation, Test practices › Encouraged › Mock external services (SeleniumHQ/seleniumhq.github.io) (fetched): "Eliminating the dependencies on external services will greatly improve the speed and stability of your tests."
- arXiv:2208.01106, §I, §V-A and related work 'Flakiness caused by Network Dependencies' (fetched): "[...] classify 6% of the flaky tests fixes they studied to be due to network dependencies" · "This includes both local and remote network issues." · "This makes network dependencies a major source of flakiness" · "413 tests are flaky due to network issues" · "14% of the flaky tests found in six large-scale Microsoft projects are due to network related causes" · "Many programmers prefer to mock APIs and services relying on network connectivity [...] However, tests directly relying on resources accessed via the network are still common."
- DOI 10.1145/2635868.2635920 (relayed): "201 commits that likely fix flaky tests in 51 open-source projects"; its 6% network share as stated in arXiv:2208.01106. arXiv:2101.09077 and 'A study on the lifecycle of flaky tests', ICSE 2020 (both unfetched) are the primary sources of the 413-test and 14% figures, which the card quotes as arXiv:2208.01106 (fetched) states them.
- arXiv:2207.01047, §IV-A (fetched): "RQ1 findings: The top four causes of test flakiness in JavaScript projects are concurrency (21%), async wait (20%), OS (18%) and network (13%)." · network category: "a test fails due to remote connection failures (e.g., lost internet connection when accessing an external URL) or local bad socket management."
- Caveat: the vendor guidance addresses browser-level end-to-end tests, and one vendor also permits a direct request to a third-party API, cached where possible, which this rule does not exempt; the studies' network category also counts local socket and port handling, so its shares are not shares of remote services alone.
