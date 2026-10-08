---
title: A browser-driven test reaches its starting state through the system's API or seeded data and drives the UI only for the behaviour it verifies
rule_id: TST-36
domain: tests
step: [test, review]
applies_to: [tests]
triggers: ['(?i)[.](fill|type|sendKeys|send_keys|SendKeys|setValue)\(.*\b(user(name)?|email|password|login)\b', '(?i)[.](goto|visit|navigate\w*|get)\(.*\b(login|signin|sign-in|sign_in|register|signup)\b', '(?i)\b(log_?in|sign_?in)\w*\(\s*&?\s*(mut\s+)?(page|driver|browser|cy|wd|ctx)\b']
scope: file
check_kind: semantic
severity_default: minor
---

# A browser-driven test reaches its starting state through the system's API or seeded data and drives the UI only for the behaviour it verifies

## Thesis
A test that drives the application through a browser performs every repeated action and preparation that brings the system to its starting state, such as signing in or creating the records the scenario needs, through the system's API or a programmatic seeding routine, and drives the browser only for the behaviour the test verifies.

## Rationale
Eliminating the browser sign-in before every test improves both the speed and the stability of the test; a routine that gains access instead, such as an API call that signs in and sets a session cookie, takes its place. Tests that all lean on the same lengthy setup fail together the moment that setup breaks, and a screen of failures then says only that something upstream went wrong. Splitting a flow into tests that each cover a meaningful piece of behaviour named by the test's title, each reaching its starting point programmatically rather than by repeating the earlier steps through the UI, gives failures that narrow down where to look.

## Example
```rust
bad:  fn log_in(page: &Page) { page.goto("/login"); page.fill("#email", USER);
          page.fill("#password", PASSWORD); page.click("#sign-in"); }
      log_in(&page);
      page.goto("/orders/new"); page.click("#place-order");
      page.click("#cancel-order");
good: let session = api.sign_in(USER, PASSWORD)?;
      let order = api.create_order(&session.token, ITEM)?;
      page.set_cookie("session", &session.token);
      page.goto(&format!("/orders/{}", order.id)); page.click("#cancel-order");
```

## Limits
When the behaviour a test verifies is the sign-in form or the data-entry screen itself, driving that screen through the browser is the behaviour under test, not preparation, and stays in that test. The system's existing API is the default route for creating the test's data; a seeding routine may also send a request to a back-end endpoint or write to the database with direct queries. The rule reaches browser-driven tests, the scope its evidence addresses.

## Validator
Grep the hunk for browser steps that type into credential fields, navigate to a sign-in or registration path, or call a sign-in helper that takes the page or driver. Open the test file and, for each test holding such steps, read its name and its assertions to find the behaviour it verifies. Trace whether the matched steps, and any form submissions before the asserted action, only bring the system to that behaviour's starting state. Validator question: **Does a browser-driven test sign in or create its starting records through the browser when the behaviour it asserts is something other than that sign-in or that record creation?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: TST-36`, severity minor, `file`, `symbol`, `code` = the browser setup steps quoted verbatim from the diff, `fix` = the setup moved to a call to the system's API or a seeding routine with the browser steps kept for the asserted behaviour, in the file's language, `rationale` = the preparation the test drives through the browser and the speed, stability and failure diagnosis it costs).

## Source
- Selenium documentation, Test practices › Encouraged › "Generating application state" (SeleniumHQ/seleniumhq.github.io, trunk, website_and_docs/content/documentation/test_practices/encouraged/generating_application_state.en.md) (fetched): "Selenium should not be used to prepare a test case. All repetitive actions and preparations for a test case, should be done through other methods." · "Eliminating logging in via web browser before every test will improve both the speed and stability of the test. A method should be created to gain access to the AUT* (e.g. using an API to login and set a cookie)." · "existing APIs should be leveraged to create data for the AUT*."
- Cypress documentation, "Best Practices" (cypress-io/cypress-documentation, main, docs/app/core-concepts/best-practices.mdx) (fetched): "Test specs in isolation, programmatically log into your application, and take control of your application's state." · "Tests small enough that they all lean on the same lengthy setup fail together the moment that setup breaks, and a screen of red tells you only that something upstream went wrong." · "each test covers a meaningful piece of behavior, its title names that behavior, and a failure narrows down where to look [...] each getting to its starting point programmatically rather than by repeating the steps before it through the UI." · "a request is sent to a back end API, but you could also interact directly with your database with direct queries".
- Caveat: both sources are browser-automation documentation and give no measured effect sizes.
