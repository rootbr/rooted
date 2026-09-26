---
title: A metric tag value comes from a bounded set, and a user-supplied value such as a raw URI or an id is normalized before it becomes a tag
rule_id: MNT-33
domain: maintainability
triggers: ['Tags?[.]of\(', '[.]tag\(', '[.]tags\(', '(Counter|Timer|Gauge|DistributionSummary)[.]builder\(', 'registry[.](counter|timer|gauge|summary)\(', 'Metrics[.](counter|timer|gauge|summary)\(']
scope: file
check_kind: semantic
severity_default: major
---

# A metric tag value comes from a bounded set, and a user-supplied value such as a raw URI or an id is normalized before it becomes a tag

## Thesis
Every value passed as a Micrometer tag (`Tags.of("k", v)`, `.tag("k", v)`, `registry.counter(name, "k", v)`) is drawn from a small, known set — an enum, a status-code class, a normalized route template such as `/users/{id}`, a fixed bucket; a value that is user-supplied or otherwise unbounded — derived from user input, an entity id, an email, a raw request path, an exception message or a free-text field — is mapped to such a set, or dropped, before it becomes a tag.

## Rationale
Each distinct combination of tag values is its own time series in the registry and in the monitoring backend, held in memory and shipped on every scrape; a tag whose values come from users grows without bound — one series per user id, per unknown URL probed by a scanner, per message text — until the application's heap and the backend's storage fail. The hazard is easy to miss: the URI tag of an HTTP request is fine while it is the route template and unbounded the moment a 404 records the raw path, which is why the instrumentation constrains 404s to `NOT_FOUND`.

## Example
```java
bad:  registry.counter("orders.placed", "customer", customerId).increment();
      registry.timer("http.requests", "uri", request.getRequestURI()).record(d);
good: registry.counter("orders.placed", "channel", order.channel().name()).increment();
      registry.timer("http.requests", "uri", routeTemplate(request), "status", statusClass(code)).record(d);
```

## Limits
A tag from an enum, a boolean, an HTTP status or its class, a bounded set of route templates, a host name from a small fixed set of peers, or a value the project context declares bounded (a tenant list of ten) is correct. A high-cardinality value that must be observable belongs in a log line or a trace attribute, not a metric tag. The metric name itself is normalized by the registry's naming convention and is not this concern.

## Validator
On the triggered hunk find each tag key/value pair. Open the file and trace each value: an enum or constant, a bounded mapping, or something derived from a request, an entity, user input or an exception. Validator question: **can this tag value take an unbounded or user-controlled number of distinct values?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: MNT-33`, severity major, `file`, `symbol`, `code` = the tag expression quoted verbatim from the diff, `fix` = the normalized or bucketed value, or the value moved to a log or trace attribute, `rationale` naming the series growth per distinct value).

## Source
Micrometer reference, Concepts → Naming Meters → Tag Values — "Beware of the potential for tag values coming from user-supplied sources to blow up the cardinality of a metric. You should always carefully normalize and add bounds to user-supplied input … Consider the URI tag for recording HTTP requests on service endpoints. If we do not constrain 404's to a value like NOT_FOUND, the dimensionality of the metric would grow with each resource that cannot be found" (fetched from `docs/modules/ROOT/pages/concepts/naming.adoc`, branch `main`).
