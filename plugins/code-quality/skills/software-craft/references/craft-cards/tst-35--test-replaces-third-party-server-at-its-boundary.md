---
title: An automated test replaces any third-party server or external site the team does not control at its boundary
rule_id: TST-35
domain: tests
step: [test]
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
