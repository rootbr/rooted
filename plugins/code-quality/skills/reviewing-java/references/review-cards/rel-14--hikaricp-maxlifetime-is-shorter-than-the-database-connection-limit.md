---
title: A HikariCP maxLifetime is set, non-zero, and shorter than the database's own connection time limit
rule_id: REL-14
domain: reliability
triggers: ['setMaxLifetime\(', 'HikariConfig', 'HikariDataSource', 'maxLifetime', 'setIdleTimeout\(']
scope: hunk
check_kind: semantic
severity_default: major
---

# A HikariCP maxLifetime is set, non-zero, and shorter than the database's own connection time limit

## Thesis
When pool settings are configured in Java, `HikariConfig.setMaxLifetime` receives a value several seconds shorter than the connection lifetime the database or an intermediate proxy enforces (`wait_timeout`, `idle_session_timeout`, a load balancer's idle cut), and never `0`, which means an infinite lifetime.

## Rationale
The database or the network in between closes a connection that has lived or idled past its own limit. If the pool's lifetime is equal to or longer than that limit, the pool hands out a connection the server has already closed, and the first statement on it fails; the failure lands on an arbitrary request, some time after a quiet period, and looks like a transient network error. HikariCP retires a connection when its `maxLifetime` expires, with small per-connection variation so the pool does not retire everything at once, and states that the value "should be several seconds shorter than any database or infrastructure imposed connection time limit". A value of `0` disables lifetime-based retirement; only `idleTimeout` still retires connections that sit idle, so a server-side lifetime cut on a connection the pool keeps is discovered by a failing request.

## Example
```java
bad:  config.setMaxLifetime(0);                          // never retired; server cuts at 5 min idle
      config.setMaxLifetime(Duration.ofMinutes(30).toMillis());   // MySQL wait_timeout is 10 min
good: config.setMaxLifetime(Duration.ofMinutes(9).toMillis());    // 60 s under wait_timeout = 10 min
```

## Limits
Applies where the pool is configured in Java; a value set in `application.yml` is not this diff. The database limit comes from the project context or a comment; when neither states it, flag only `0` — a non-zero value cannot be judged against an unknown limit and is not a finding. A construction without `setMaxLifetime` runs at the default of 30 minutes and is judged as that value. A `keepaliveTime` shorter than the server's idle cut keeps idle connections alive but does not replace `maxLifetime` for a lifetime-based server limit.

## Validator
On the triggered hunk find each `setMaxLifetime` call and each `HikariConfig`/`HikariDataSource` construction without one. Read the project context for the database's connection or idle limit. Flag `setMaxLifetime(0)`; flag a value (or the 30-minute default of a construction without one) not below the stated limit; when no limit is stated, emit nothing for a non-zero value. Validator question: **can the pool hand out a connection that the database or the network has already closed because the pool's lifetime is not shorter than theirs?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: REL-14`, severity major, `file`, `symbol`, `code` = the `setMaxLifetime` call, or the pool construction lacking one, quoted verbatim from the diff, `fix` = `setMaxLifetime` set some seconds below the server limit, `rationale` naming the server-side cut and the failing first statement).

## Source
HikariCP README (`brettwooldridge/HikariCP`, `dev`), configuration property `maxLifetime` — "This property controls the maximum lifetime of a connection in the pool. An in-use connection will never be retired, only when it is closed will it then be removed ... We strongly recommend setting this value, and it should be several seconds shorter than any database or infrastructure imposed connection time limit. A value of 0 indicates no maximum lifetime (infinite lifetime), subject of course to the idleTimeout setting. The minimum allowed value is 30000ms (30 seconds). Default: 1800000 (30 minutes)".
