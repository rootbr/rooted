---
title: A SQL query carrying untrusted data binds it as a parameter, never by concatenating it into the statement text
rule_id: SEC-01
domain: security
triggers: ['execute(Query|Update|LargeUpdate)?\(', 'createStatement\(', 'create(Native|Named)?Query\(', '@Query\(', 'JdbcTemplate|JdbcClient|NamedParameterJdbcTemplate', '(SELECT|INSERT|UPDATE|DELETE|WHERE|FROM)\b[^"]*"\s*\+']
scope: file
check_kind: semantic
severity_default: critical
---

# A SQL query carrying untrusted data binds it as a parameter, never by concatenating it into the statement text

## Thesis
Every SQL, JPQL or HQL statement whose text depends on a value from outside the code — a request parameter, a path variable, a message field, a stored value another user wrote — passes that value through a bind parameter: `PreparedStatement` `?` placeholders with `setX`, JPA `:name` or `?1` parameters with `setParameter`, `@Query` method parameters, `JdbcTemplate` argument arrays. The statement string itself contains no such value, whether the executing call is `Statement.execute`, `executeQuery`, `createNativeQuery` or a `@Query(nativeQuery = true)` string.

## Rationale
A parameterized query defines all SQL code first and passes each value later, so the database always distinguishes code from data regardless of the input: a value such as `tom' or '1'='1` is looked up as that literal string. A value concatenated into the text becomes part of the code the database parses; a quote, a comment marker or a `UNION` in it changes the query's intent, reads or deletes other rows, and on some databases runs commands. A `Statement` built from a concatenated string has no way to bind, so any external value in its text is unbound. Native JPA queries and HQL carry the same defect and the same fix. Where a value cannot be bound because it names a table or column, binding is not the answer — that part of the query comes from the code, not from the input.

## Example
```java
bad:  String sql = "SELECT * FROM users WHERE email = '" + email + "'";
      ResultSet rs = stmt.executeQuery(sql);
good: String sql = "SELECT * FROM users WHERE email = ?";
      try (PreparedStatement ps = conn.prepareStatement(sql)) {
          ps.setString(1, email);
          try (ResultSet rs = ps.executeQuery()) { return map(rs); }
      }
```

## Limits
Applies to a value that originates outside the code — a request, a message, a file, a database column that user input reached. A statement built from constants, enum names or values the code itself chose (a column picked by a `switch` over a fixed set) is not flagged. A `PreparedStatement` whose text is built by concatenating an untrusted value and then bound for other values is still flagged for the concatenated part. Criteria API and query-builder calls that never take a raw fragment are out of scope; a builder's raw-SQL escape hatch fed an untrusted value is in scope.

## Validator
On the triggered hunk find each statement string that is built with `+`, `String.format`, `StringBuilder`, a text block with interpolation, or `concat`, and each `execute`, `executeQuery`, `executeUpdate`, `createNativeQuery`, `createQuery` or `@Query` value that takes such a string. Open the file and trace each concatenated operand to its origin: a method parameter reachable from a controller, listener or job, a request accessor, a field loaded from a store. Validator question: **does a value that originates outside the code reach the statement text as part of the SQL rather than as a bound parameter?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: SEC-01`, severity critical, `file`, `symbol`, `code` = the concatenation and the executing call quoted verbatim from the diff, `fix` = the placeholder form of the statement with `setX` or `setParameter` for the value, `rationale` naming the code-versus-data boundary the concatenation removes).

## Source
OWASP SQL Injection Prevention Cheat Sheet, "Defense Option 1: Prepared Statements (with Parameterized Queries)" — "the database will always distinguish between code and data, regardless of what user input is supplied", with the Java `PreparedStatement` and HQL named-parameter examples. OWASP Query Parameterization Cheat Sheet, Java and Hibernate examples. OWASP ASVS 5.0 requirement 1.2.4. CWE-89.
