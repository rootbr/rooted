---
title: Input validation defines what is permitted and rejects everything else, and a denylist of dangerous characters is never the primary check
rule_id: SEC-46
domain: security
triggers: ['replaceAll\(|replace\(', '(?i)black[_ -]?list|deny[_ -]?list|block[_ -]?list|forbidden(Chars|Words|Pattern)', '[.]contains\("(<|>|''|--|;|script|select|union|drop)', '@Pattern\(regexp\s*=\s*"\[\^', 'Pattern[.]compile\("\[\^', '(?i)sanitiz|strip(Tags|Html)|escape(Sql|Html)']
scope: file
check_kind: semantic
severity_default: major
---

# Input validation defines what is permitted and rejects everything else, and a denylist of dangerous characters is never the primary check

## Thesis
A validation applied to a value from outside the code states what the value may be — a fixed set of options, a positive pattern of allowed characters with a length bound, a numeric range, a structural parse (`UUID.fromString`, `LocalDate.parse`) — and rejects anything else. Code whose check removes or refuses known-bad fragments (`<script>`, `'`, `--`, `1=1`, a list of words) and passes the rest is the defect when that check is the value's only defense.

## Rationale
A denylist enumerates attacks, and an attacker has more spellings than the list: case variants, encodings, nested fragments that survive a single removal (`<scr<script>ipt>`), and constructs the author never met. It also rejects legitimate input, such as an apostrophe in a name. An allowlist enumerates the legal input, so every unlisted form is refused without the author having to predict it; it is easy to state for structured data and for values chosen from a fixed set, where a mismatch on the server side means the client-side control was tampered with. A denylist may remain as a second layer that catches common probes; it does not replace the positive check or the sink-side defenses.

## Example
```java
bad:  String q = req.getParameter("q").replaceAll("(?i)<script.*?>|'|--", "");
good: String q = req.getParameter("q");
      if (!q.matches("[\\p{L}\\p{N} .,'-]{1,100}")) throw new IllegalArgumentException("invalid query");
```

## Limits
Applies to validation of a value that later reaches a sink or a decision. Removal of characters for normalization (trimming, collapsing whitespace) is not a denylist. Output sanitizing of rich HTML through a policy-based sanitizer is an allowlist of elements and is correct. A denylist kept beside an allowlist, or beside parameterization and encoding at the sink, is a second layer and is not flagged. Free-form text that legitimately carries any character is validated by length and Unicode category, not by pattern.

## Validator
On the triggered hunk find each check or transformation that names dangerous fragments, and the value it guards. Open the file to see whether a positive check (pattern, set membership, parse, range) also applies before the value reaches a sink, or whether the sink itself is parameterized or encoded. Validator question: **is a denylist of bad fragments the only thing standing between this value and its sink?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: SEC-46`, severity major, `file`, `symbol`, `code` = the denylist check quoted verbatim from the diff, `fix` = the positive pattern, set or parse that replaces it, `rationale` naming a spelling the denylist misses).

## Source
OWASP Input Validation Cheat Sheet, "Allowlist vs Denylist" — "It is a common mistake to use denylist validation... this is a massively flawed approach as it is trivial for an attacker to bypass such filters"; "Allowlist validation involves defining exactly what IS authorized, and by definition, everything else is not authorized"; denylisting "should supplement - not replace - allowlisting". OWASP ASVS 5.0 requirement 2.2.1 — "positive validation against an allow list of values, patterns, and ranges". OWASP Java Security Cheat Sheet, "General advice to prevent Injection".
