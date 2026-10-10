---
title: A table name, column name or sort direction taken from a request is mapped to an allowlisted value before it enters a query
rule_id: JAVA-51
domain: security
step: [implement, handle-errors]
applies_to: [java, service-boundary]
triggers: ['(?i)order\s+by', '(?i)group\s+by', 'Sort[.]by\(', 'JpaSort[.]unsafe\(', '(?i)sort(By|Field|Column|Dir|Order)', '(?i)(table|column)_?name']
scope: file
check_kind: semantic
severity_default: critical
---

# A table name, column name or sort direction taken from a request is mapped to an allowlisted value before it enters a query

## Thesis
A query part that a bind variable cannot carry — a table or column name, an `ORDER BY` column, an `ASC`/`DESC` indicator — is never taken from a request value as text. The code maps the request value to one entry of a fixed allowlist (a `Map<String, String>`, an enum, a `switch`) and appends the entry, or rejects the request.

## Rationale
Parameter binding protects values, not identifiers: a database accepts a placeholder where a literal may stand, not where a column or table is named, so a dynamic `ORDER BY` is concatenated by construction and escaping cannot help — an escaped value in that position produces a failed query or an injection. Validation against the set of legal names, applied before concatenation, keeps the query's structure under the code's control; a regex that admits any identifier still lets an attacker choose columns, and a denylist is bypassed by the next spelling. Mapping request values to code-owned names means the appended text never came from the request at all.

## Example
```java
bad:  String sql = "SELECT * FROM orders ORDER BY " + req.getParameter("sort");
good: private static final Map<String, String> SORT = Map.of("date", "created_at", "total", "amount");
      String col = SORT.get(req.getParameter("sort"));
      if (col == null) throw new IllegalArgumentException("unknown sort");
      String sql = "SELECT * FROM orders ORDER BY " + col;
```

## Limits
Applies when the identifier or direction originates outside the code. A sort column chosen from an enum the code defines, a `Sort.by(...)` on a JPQL or derived query whose property names Spring Data checks against the entity, and a constant `ORDER BY` are not flagged. A value validated against an allowlist of the exact legal names, in either the controller or the repository, is the correct form. A native query that appends a `Sort` built from a raw request property is flagged on the same mechanism — the sort property is spliced into the query text as an identifier — as the card's own extension of the sourced rule, not a quoted requirement.

## Validator
On the triggered hunk find each `ORDER BY`, `GROUP BY`, table or column fragment that is appended, formatted or interpolated, and each `Sort.by` or `JpaSort` built from a request value that reaches a native query. Open the file and trace the appended operand to where it is chosen: a fixed map or enum lookup, an exact-match check against constants, or the raw request value (possibly after a regex). Validator question: **can a request choose an identifier or direction that the code did not enumerate, and does that text reach the query?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: JAVA-51`, severity critical, `file`, `symbol`, `code` = the appended identifier expression quoted verbatim from the diff, `fix` = the map or enum lookup with rejection of unknown keys, `rationale` naming that identifiers cannot be bound and that escaping them fails or injects).
