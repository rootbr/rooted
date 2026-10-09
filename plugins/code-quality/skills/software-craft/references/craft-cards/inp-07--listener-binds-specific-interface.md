---
title: A network listener the change adds binds to the specific interface it must serve, not to all interfaces
rule_id: INP-07
domain: input
step: [implement, review]
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

## Source
- Ruff S104 hardcoded-bind-all-interfaces, astral-sh/ruff `crates/ruff_linter/src/rules/flake8_bandit/rules/hardcoded_bind_all_interfaces.rs` (fetched): "Binding to all network interfaces is insecure as it allows access from unintended interfaces, which may be poorly secured or unauthorized. Instead, bind to specific interfaces."
- Bandit B104, PyCQA/bandit `bandit/plugins/general_bind_all_interfaces.py` (fetched): "Binding to all network interfaces can potentially open up a service to traffic on unintended interfaces, that may not be properly documented or secured."
- gosec G102, securego/gosec `RULES.md` and `rules/bind.go` (fetched): "G102 — Bind to all interfaces"; "Binds to all network interfaces", matching `^(0\.0\.0\.0|\[::\]|:).*$`.
- Go `net.Listen`, pkg.go.dev/net (fetched): "For TCP networks, if the host in the address parameter is empty or a literal unspecified IP address, Listen listens on all available unicast and anycast IP addresses of the local system."
- Node.js `server.listen`, nodejs/node `doc/api/net.md` (fetched): "If `host` is omitted, the server will accept connections on the unspecified IPv6 address (`::`) when IPv6 is available, or the unspecified IPv4 address (`0.0.0.0`) otherwise."
- OpenJDK `java.net.ServerSocket` and `java.net.InetSocketAddress`, openjdk/jdk (fetched): "If bindAddr is null, it will default accepting connections on any/all local addresses."; "Creates a socket address where the IP address is the wildcard address".
- OWASP Cheat Sheet Series, Attack Surface Analysis (fetched): the attack surface is "the sum of all paths for data/commands into and out of the application"; 'Managing the Attack Surface': "turning off features and interfaces that aren't being used, by introducing operational controls such as a Web Application Firewall (WAF)".
- OWASP Cheat Sheet Series, Secure Product Design, 'Methodology' (fetched): "As a basic start, establish secure defaults, minimize the attack surface area, and fail securely to those well-defined and understood defaults."
- OWASP ASVS 5.0, 15.2.3 (L2) (fetched): "does not expose extraneous functionality such as test code, sample snippets, and development functionality"; 13.4.5 (L2): "documentation (such as for internal APIs) and monitoring endpoints are not exposed unless explicitly intended."
- Django settings reference, django/django `docs/ref/settings.txt` (fetched): ALLOWED_HOSTS is "A list of strings representing the host/domain names that this Django site can serve", whose values "will be matched against the request's ``Host`` header exactly".
- OpenJDK `java.net.InetAddress`, openjdk/jdk `src/java.base/share/classes/java/net/InetAddress.java` (fetched): "If the host is null or host.length() is equal to zero, then an InetAddress representing an address of the loopback interface is returned."
- CPython socket documentation, python/cpython `Doc/library/socket.rst` (fetched): "For IPv4 addresses, two special forms are accepted instead of a host address: '' represents INADDR_ANY, which is used to bind to all interfaces".
- Flask `Flask.run`, pallets/flask `src/flask/app.py` (fetched): "Runs the application on a local development server."; "the hostname to listen on. Set this to '0.0.0.0' to have the server available externally as well. Defaults to '127.0.0.1' or the host in the SERVER_NAME config variable if present".
- Caveat: the tool rules state the exposure as possible ("may be", "can potentially"); no measured rate of exposure backs the rule.
