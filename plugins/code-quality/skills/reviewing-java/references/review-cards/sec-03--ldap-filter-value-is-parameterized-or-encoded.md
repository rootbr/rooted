---
title: An LDAP search filter carrying untrusted data uses a parameterized or encoded value, never a value concatenated into the filter string
rule_id: SEC-03
domain: security
triggers: ['(?i)ldap', 'DirContext', 'objectClass', '[.]search\(', 'filterEncode\(|LdapEncoder', 'LdapQueryBuilder|LdapQuery']
scope: file
check_kind: semantic
severity_default: critical
---

# An LDAP search filter carrying untrusted data uses a parameterized or encoded value, never a value concatenated into the filter string

## Thesis
A value from outside the code that enters an LDAP search filter is passed as a filter argument (`DirContext.search(base, "(uid={0})", new Object[]{value}, controls)`), through `LdapQueryBuilder.query().where("uid").is(value)` or `filter(format, params)`, or after `LdapEncoder.filterEncode`; a distinguished name built from such a value is encoded with the DN encoder. The filter string itself carries no raw external value.

## Rationale
A search filter is parsed by the directory: parentheses, `*`, `&`, `|`, `!`, `\` and NUL are its syntax, so a value containing `*)(uid=*` turns a lookup of one user into a match of every user, and an injected `(|(...))` clause bypasses an authentication or membership check. Filter arguments and the builder's `is`/`like` methods escape each value per the filter grammar before it is joined; the hardcoded-filter method escapes nothing and its documentation says never to use direct user input with it. DN escaping is a different grammar from filter escaping, so a value used as a DN component needs the DN encoder, not the filter one. An allowlist regex on the value (letters and spaces only) is an acceptable second layer; it is not the primary defense.

## Example
```java
bad:  String filter = "(&(uid=" + user + ")(objectClass=person))";
      ctx.search("ou=users,dc=example,dc=com", filter, controls);
good: String filter = "(&(uid={0})(objectClass=person))";
      ctx.search("ou=users,dc=example,dc=com", filter, new Object[]{ user }, controls);
      // or: query().base("ou=users").where("uid").is(user).and("objectClass").is("person")
```

## Limits
Applies when the value originates outside the code. A filter assembled from constants, or from a value already reduced to an allowlisted enum, is not flagged. A value passed through `filterEncode` before concatenation, or bound through `filter(String, Object...)`, is the correct form for a filter; a DN component needs `nameEncode`. An attribute name taken from a request is a defect of the same shape and takes an allowlist rather than an encoder.

## Validator
On the triggered hunk find each filter string built with `+`, `format` or a builder's hardcoded `filter(String)`, and each `search` call receiving it without a `filterArgs` array. Open the file and trace each concatenated operand to its origin. Validator question: **does a value from outside the code reach the filter text without passing through a filter argument, the builder's typed condition methods, or `filterEncode`?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: SEC-03`, severity critical, `file`, `symbol`, `code` = the filter construction and the search call quoted verbatim from the diff, `fix` = the `{0}` filter-argument form or the builder's `where(...).is(...)` form, `rationale` naming the filter metacharacters the value can carry).

## Source
OWASP LDAP Injection Prevention Cheat Sheet — "When building LDAP queries in application code, you MUST escape any untrusted data that is added to any LDAP query"; "Insecure vs Secure Java LDAP Query Construction" (the `{0}` filter-argument form). Spring LDAP `org.springframework.ldap.query.LdapQueryBuilder#filter(String)` Javadoc — "Never use direct user input... Doing so opens up for "LDAP injection""; `#filter(String, Object...)` — parameters "properly encoded using LdapEncoder#filterEncode". OWASP ASVS 5.0 requirement 1.2.6. CWE-943.
