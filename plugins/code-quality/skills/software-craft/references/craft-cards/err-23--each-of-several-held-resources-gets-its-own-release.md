---
title: Two or more resources held at once are released each by its own scoped release or release block, never by consecutive calls in one cleanup block that a failing earlier call cuts short, so a dependent resource is released before the one it depends on and a failing release skips none of the others
rule_id: ERR-23
domain: errors
step: [implement, handle-errors]
applies_to: [universal]
triggers: ['^\s*(\}\s*)?finally\s*(:|\{)', '\bif\b.*\b(a?close|Close|dispose|release|Release)\(', '^\s*((await\s+|[\w.]+\s*:?=\s*)?([\w.\[\]()]*[.])?(a?close|Close|dispose|release|disconnect|destroy|unlink|cancel|Stop|Release)\(\s*\)\s*;?\s*)+$']
scope: file
check_kind: semantic
severity_default: major
---

# Two or more resources held at once are released each by its own scoped release or release block, never by consecutive calls in one cleanup block that a failing earlier call cuts short, so a dependent resource is released before the one it depends on and a failing release skips none of the others

## Thesis
When a routine holds two or more resources at once, each resource gets a release of its own: a scoped-release declaration per resource, several declarations in one scoped-release statement included; a release block per resource, entered right after that resource's acquisition and nested inside the block of the resource acquired before it; or one entry per resource on a cleanup stack, registered right after the acquisition. The same holds for an object's own release method that releases several resources the object holds. These forms release the resources in reverse order of acquisition, so a resource that depends on another is released before the one it depends on, and they attempt every release even when an earlier one fails. Consecutive release calls in one cleanup block break the rule when an earlier call can leave the block before the later ones run — by throwing outside a handler of its own, or by a return on its error — and when they release a resource before another resource that depends on it.

## Rationale
When one cleanup block releases several resources by consecutive calls, an exception in an earlier call skips past the calls after it, and the resources they would have released leak: a block that closes a result set, then its statement, then its connection never closes the connection when either earlier close throws. Where several resources are released other than by nesting, bugs often come from exceptions in the release calls, and adding more cleanup logic to one cleanup block brings the risk of exceptions that prevent other resources from being released. A return taken before a release call skips it the same way: a routine that closes two files at its end returns without closing the first when opening the second fails. A release registered right after its acquisition runs whichever path the routine takes to return, and it sits next to the acquisition, where a later edit that adds a return path cannot miss it. Consecutive calls also run in the order the lines are written, so a resource can be released before another whose release depends on it. The scoped-release construct, the cleanup stack and a release block nested per resource all unwind like a stack, first in, last out: they release in reverse order of acquisition and attempt every release even when one of them fails, which releases a dependent resource before the one it depends on and still releases the earlier resource when releasing the later one throws. A cleanup stack that invokes its callbacks in reverse order of registration behaves as if one scoped-release statement had been nested inside another for each resource, and entering each resource on it right after creating the resource helps avoid dependency problems in the release order.

## Example
```java
bad:  Connection conn = connect();
      Statement stmt = null;
      try { stmt = conn.createStatement(); run(stmt); }
      finally {
          conn.close();
          if (stmt != null) stmt.close();
      }
good: try (Connection conn = connect();
           Statement stmt = conn.createStatement()) { run(stmt); }
```

## Limits
A single resource released by a release block of its own, entered right after its acquisition, is outside the rule. Whether such hand-written release blocks are acceptable at all is contested, and the condition that separates the cases is whether one hand-written cleanup block releases two or more resources by consecutive calls, an earlier one of which can leave the block before the later ones run — by a throw outside a handler of its own or by a return on its error. Where it does, the block releases them in the order its lines are written, and a throw or a return from an earlier release skips the later ones; this rule flags that case. Where each resource has a release block or a handler of its own, nested or chained where there are several, every resource is released on every path: a style guide accepts a hand-written release block beside the scoped construct, a must-close checker supports the hand-written block for legacy code, and a leak analyzer and a secure-coding standard give nested or chained release blocks as a correct way to release several resources. Tool rules that require the scoped construct for every closeable resource flag even the nested form, calling the scoped construct safer; this rule leaves that form alone. Consecutive releases in one block where every release but the last sits in a handler of its own that catches its failure, or runs the next release from its own cleanup clause, do not skip one another, so they pass when no resource among them is released before one that depends on it. Where the language drops each owned value when control leaves its scope, in reverse order of declaration, a value whose explicit release an early return skipped is still dropped, running its destructor, when the scope is left. Locks, and resources shared across threads, are outside the rule.

## Validator
Grep the added lines for a cleanup block — a finally clause, a deferred function, an object's own close or dispose method — and for release calls in it: a close, dispose, release, disconnect, cancel or delete call alone on its line, two such calls on one line, one guarded by a null check, or one followed by a return on its error. Open the file and find the routine or the object that holds the released resources and the acquisition of each; count resources by acquisition, so two release steps of one acquired resource, such as closing a temporary file and then deleting it, count as one. Skip a block that releases a single resource, a scoped-release declaration per resource, release blocks nested one per resource, and a cleanup stack with one entry per resource. Where one hand-written block releases two or more resources, check each release that another release follows in that block: does it sit outside a handler of its own, so that a throw from it leaves the block, or does a return on its error follow it? Then check the order: is a resource released before a resource created from it, wrapping it or otherwise depending on it — a connection before its statement, a stream before the reader over it? Validator question: **Does one hand-written cleanup block release two or more resources held at once so that a throw or a return from an earlier release skips a later one, or so that a resource is released before another that depends on it?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: ERR-23`, severity major, `file`, `symbol`, `code` = the cleanup block's release calls quoted verbatim from the diff, `fix` = each resource acquired in its own scoped-release declaration, or entered on a cleanup stack or in a nested release block of its own right after its acquisition, so the releases run in reverse order of acquisition, in the file's language, `rationale` = which later release a failing earlier release skips, or which resource is released before the one that depends on it, and what stays open as a result).
