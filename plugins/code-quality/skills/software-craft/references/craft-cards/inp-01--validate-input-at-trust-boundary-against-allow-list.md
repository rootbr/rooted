---
title: A value that enters across a trust boundary is checked on the server where it enters against allow-list rules for its type, format, length and range, and is rejected when it does not match
rule_id: INP-01
domain: input
step: [implement, handle-errors]
applies_to: [service-boundary]
triggers: ['\brequest[.](args|form|values|json|get_json|GET|POST|query_params|data|files|cookies|headers)\b', '\breq[.](body|query|params|headers|cookies)\b', '@(RequestParam|PathVariable|RequestBody|RequestHeader|QueryParam|PathParam|FormParam)\b', '[.](FormValue|PostFormValue|URL[.]Query\(\)|Header[.]Get)\(?', '\b(web|extract)::(Query|Json|Path|Form)\s*<|\b(Query|Json|Path|Form)\(\w+\)\s*:\s*(Query|Json|Path|Form)<']
scope: file
check_kind: semantic
severity_default: major
---

# A value that enters across a trust boundary is checked on the server where it enters against allow-list rules for its type, format, length and range, and is rejected when it does not match

## Thesis
Every value that crosses into a component from outside its trust boundary — a form field, URL parameter, header, cookie, file, queue message, partner feed, internal API response or stored record — is checked on the server by the receiving component, before business processing or storage, against allow-list rules defined for its field: exact membership in the allowed set for a fixed choice; expected type, accepted format and minimum and maximum values for a number or date; length limits and the characters or structure the field requires for a string; allowed and required fields for an object; minimum and maximum item counts, with every item validated, for an array. A value that fails is rejected with a clear error, and processing continues only with fully validated data. At OWASP ASVS verification Level 2 and above the check applies to all input; a project held to ASVS Level 1 may focus it on input used to make a specific business or security decision.

## Rationale
Client-side validation is easily bypassed: it serves usability, and security does not depend on it. An internal transport does not establish that a value meets the receiving component's rules, so data from internal APIs, partner feeds, queues and stored records is validated when it crosses a trust boundary. A successful conversion establishes only the type — converting text to an integer does not establish an acceptable quantity — and a high number that controls how many times a loop runs can lead to excessive processing and a potential denial of service. Rules that define what is accepted replace the attempt to recognise every malicious string: a denylist is prone to error and can be bypassed with evasion techniques, blocking apostrophes rejects legitimate names without making a database query safe, and removing suspicious characters can change a value's meaning. Validation reduces the risk of malformed data, invalid business operations and excessive resource consumption, and rejecting a failing request keeps processing from continuing with partially validated data.

## Example
```rust
bad:  let qty: i64 = req.query("qty").parse()?;
      let note = req.query("note").replace('\'', "");
      save_order(qty, note)
good: let qty: u32 = req.query("qty").parse().map_err(|_| Rejected)?;
      let note = req.query("note");
      if !(1..=MAX_QTY).contains(&qty) || note.chars().count() > MAX_NOTE {
          return Err(Rejected);
      }
      save_order(qty, note.to_string())
```

## Limits
Validation does not make a value safe to use in another component: a value bound for an SQL query still goes through parameterized queries, a value written to a page still gets context-aware output encoding, removing suspicious characters supplies neither control, and normalization does not replace output encoding. A valid account identifier does not mean the caller may access that account; authorization is checked separately, outside this rule. User-authored HTML is accepted through a maintained HTML sanitization library, a control that input validation and regular expressions cannot replace. A free-form field such as a comment is still allow-listed: the rule can permit broad Unicode text while limiting its length, and legitimate punctuation and scripts in names and comments are preserved. The rule covers the values a parser hands over, validated before business processing or storage; the choice of parser, the grammar of structured input and the preconditions of routines that call each other inside one trust boundary are outside it.

## Validator
Grep the hunk for a read of an outside value: a request query, body, form, path, header or cookie accessor, a framework extractor or binding annotation, or a read of a file, queue message, partner feed, internal API response or stored record owned by another component. Open the file and trace each such value from that read to its first business decision, storage write, loop count or call into another component. On that path, look for a server-side check of the field's rule — membership for a fixed choice, type, format and minimum and maximum for a number or date, length and required characters or structure for a string, allowed and required fields for an object, item count and per-item checks for an array — written inline, held in a schema or a validating type, or declared through the framework's validation annotations, and confirm that a failure returns an error rather than continuing, substituting a default or stripping characters. Count a bare type conversion as a type check only. Where the project documents ASVS Level 1 as its verification target, limit the trace to values used to make a business or security decision. Validator question: **Does a value read across a trust boundary reach a business decision, storage write, loop count or downstream call without a server-side check of every part of its field's rule — type, format, length and range as the field requires — that rejects it on failure?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: INP-01`, severity major, `file`, `symbol`, `code` = the line that reads the outside value and the line where it is first used unchecked, `fix` = the server-side check of the field's type, format, length or range that returns an error on failure, in the file's language, `rationale` = the trust boundary the value crosses, the field rule it skips and the use it reaches).
