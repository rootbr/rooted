---
title: An InetSocketAddress built from a hostname resolves DNS in its constructor, so it is created off the event-loop or selector thread, or pre-resolved
rule_id: PF-30
domain: performance
triggers: ['new InetSocketAddress\(', 'InetAddress[.]getByName\(', 'InetAddress[.]getAllByName\(', 'createUnresolved\(', 'Selector', 'EventLoop|eventLoop']
scope: file
check_kind: semantic
severity_default: minor
---

# An InetSocketAddress built from a hostname resolves DNS in its constructor, so it is created off the event-loop or selector thread, or pre-resolved

## Thesis
`new InetSocketAddress(hostname, port)` and `InetAddress.getByName(hostname)` are called where a blocking name lookup is acceptable — at configuration time, on a worker thread, or through the resolver of the networking library in use — and their results are kept; they are not called on a selector loop, a non-blocking event loop, or any thread whose stall delays every connection it multiplexes. Where the address is passed to a library that resolves itself, `InetSocketAddress.createUnresolved` is used.

## Rationale
Constructing an `InetSocketAddress` from a hostname makes an attempt to resolve the hostname into an `InetAddress` inside the constructor: a synchronous name-service query that blocks the calling thread for the duration of the lookup — the round trip to the resolver, its timeout on failure, and any retries — and on failure the address is merely flagged as unresolved. A selector or event-loop thread serves many connections; blocking it on one lookup stalls all of them for that time — under a failing resolver, for the resolver's timeout. A pre-resolved address, a lookup on a worker, or an unresolved address handed to a resolver-aware client keeps the loop responsive.

## Example
```java
bad:  void connect(String host, int port) {      // runs on the selector thread
          channel.connect(new InetSocketAddress(host, port));
      }
good: private final InetSocketAddress addr = new InetSocketAddress(host, port);   // resolved at startup
      void connect() { channel.connect(addr); }
```

## Limits
A hostname that is an IP literal is not looked up. A blocking client on its own thread pays the lookup harmlessly. A library that documents asynchronous resolution and accepts `createUnresolved` addresses is the correct path for per-request hostnames on a loop. Keeping resolved addresses trades against DNS-based failover; the refresh policy is the project's call, and a tolerance stated in the project context rejects the finding.

## Validator
On the triggered hunk find each `new InetSocketAddress(String, int)` and each `InetAddress.getByName` or `getAllByName`. Open the file: is the call reachable from a selector loop, an event-loop handler, a channel callback, or another single-threaded multiplexing path? Validator question: **does this code resolve a hostname synchronously on a thread that multiplexes other connections?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: PF-30`, severity minor, `file`, `symbol`, `code` = the address construction quoted verbatim from the diff, `fix` = the pre-resolved address, the worker-thread lookup or `createUnresolved`, `rationale` naming the blocking lookup on the loop thread).

## Source
`java.net.InetSocketAddress(String hostname, int port)` Javadoc, Java SE 21 — "Creates a socket address from a hostname and a port number. An attempt will be made to resolve the hostname into an InetAddress. If that attempt fails, the address will be flagged as unresolved"; `#createUnresolved` — "No attempt will be made to resolve the hostname into an InetAddress." `java.net.InetAddress#getByName` Javadoc — "Determines the IP address of a host, given the host's name... If a literal IP address is supplied, only the validity of the address format is checked."
