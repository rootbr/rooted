---
title: A network listener the change adds binds to the specific interface it must serve, not to all interfaces
rule_id: INP-07
domain: input
step: [implement]
applies_to: [service-boundary]
triggers: ['\b0[.]0[.]0[.]0\b|[\x22\x27](::|\[::\])(:\d+)?[\x22\x27]|\b(INADDR_ANY|IN6ADDR_ANY|in6addr_any|Ipv[46]Addr::UNSPECIFIED|IPv4zero|IPv6unspecified)\b|\(\s*\[\s*0\s*(,\s*0\s*){3}\]\s*,', '\b(Listen\w*|listen)\(\s*(\x22(tcp|udp)[46]?\x22\s*,\s*)?[\x22\x27]:\d+|\bnew\s+(InetSocketAddress|ServerSocket)\(\s*\w+\s*\)|[.]listen\(\s*\w+\s*[,)]|\(\s*(\x22\x22|\x27\x27)\s*,\s*\w+\s*\)|[\x22\x27]:\d{1,5}[\x22\x27]|[.]listen\(\s*\{(?![^}]*\bhost\b)|\b(TCP|UDP)Addr\{(?![^}]*\bIP\b)']
scope: hunk
check_kind: semantic
severity_default: minor
---

# A network listener the change adds binds to the specific interface it must serve, not to all interfaces

## Thesis
A network listener that a change adds, through its bind or listen call or the host setting that configures it, binds to the specific interface the service is meant to answer on (the loopback address for a service meant only for the local host) rather than to all interfaces, which an unspecified address (`0.0.0.0`, `::`) selects, and which an empty, null or omitted host or a port given without a host selects only where the platform documents that form as the unspecified or wildcard address. A bind to all interfaces is correct only where every interface it opens is an intended one.

## Rationale
An all-interfaces bind accepts connections on every address of the host, and each platform's documentation states which forms select it: on one, for TCP, an empty host or a literal unspecified address listens on all available unicast and anycast addresses; on another, an omitted host accepts connections on the unspecified address `::` or `0.0.0.0`; on a third, a null bind address accepts connections on any/all local addresses while a null or empty host name resolves to an address of the loopback interface; and a development server's omitted host defaults to the loopback address unless a server-name setting supplies the host. An all-interfaces bind allows access from unintended interfaces, which may be poorly secured or unauthorized, and can potentially open the service to traffic on interfaces that may not be properly documented or secured. Each interface a listener answers on is a path for data and commands into the application and so part of its attack surface; establishing secure defaults and minimizing the attack surface area is the basic start of a secure product design. Minimizing the attack surface also covers what a listener exposes: a production environment includes only the functionality the application requires and exposes no test code, sample snippets or development functionality, and documentation and monitoring endpoints are not exposed unless explicitly intended (both Level 2 verification requirements).

## Example
```java
bad:  admin.bind(new InetSocketAddress("0.0.0.0", ADMIN_PORT));
      metrics.bind(new InetSocketAddress(METRICS_PORT));
good: InetAddress loopback = InetAddress.getLoopbackAddress();
      admin.bind(new InetSocketAddress(loopback, ADMIN_PORT));
      metrics.bind(new InetSocketAddress(loopback, METRICS_PORT));
```

## Limits
A bind to all interfaces is correct where every interface it opens is an intended one. An empty, null or omitted host is an all-interfaces bind only where the platform documents that form as the unspecified or wildcard address; where the platform resolves it to the loopback address, the listener is local-only and outside the rule. The exposure is stated as a possibility, interfaces that may be poorly secured, so a finding asks about intent rather than proving an exposure. Where the listen address is read from configuration, the rule reaches the default value the code supplies, which a secure default makes the specific interface. Operational controls such as a web application firewall are a separate means of reducing the attack surface, and the rule leaves them aside: it checks the address the code binds. An allowed-hosts list matched against the request's Host header selects no interface and is outside the rule.

## Validator
Grep the hunk for a bind, listen or serve call, a server-socket or socket-address constructor, and a listen-host setting whose address is `0.0.0.0`, `::` or `[::]`, a string that starts with `:` and so carries no host, an empty or null host, a port passed with no host, or a named any-address constant. Open the hunk around the call to find which address the listener receives, including the default of a configuration value it reads and, for an empty, null or omitted host or a port with no host, the address the platform documents for that form. Trace any stated intent for the exposure: a comment, a configuration key or a deployment setting in the hunk that names the interfaces the service must answer on. Validator question: **Does the hunk bind a listener to all interfaces with nothing in the hunk stating that every interface it opens is intended?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: INP-07`, severity minor, `file`, `symbol`, `code` = the bind, listen or host-setting line quoted verbatim from the diff with its all-interfaces address, `fix` = the same call in the file's language bound to the specific interface, the loopback address for a local-only service or a configured interface address whose default is specific, `rationale` = names the all-interfaces address, the unintended interfaces it opens and the absence of a stated intent).
