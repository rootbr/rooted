---
title: A recursive routine reaches a base case on every input, and one whose depth grows with unbounded input checks a depth limit or is written as a loop
rule_id: CODE-81
domain: code
step: [design, implement]
applies_to: [universal]
triggers: ['\b\w+\s*\([^()]*\b(?:n|depth|level|k|i|idx|count|size|len|mid|hi)\s*-\s*1\b', '\b\w+\s*\([^()]*\b\w+[.](?:get)?(?:[Ll]eft|[Rr]ight|[Nn]ext|[Pp]rev|[Cc]hildren|[Cc]hild|[Pp]arent|[Tt]ail|[Rr]est|[Ss]ubtree|[Bb]ranches|[Nn]odes)\b', '\b\w+\s*\([^()]*(?:\w\[1\s*(?::|[.][.])|[.](?:slice|subList|substring)\(\s*1\b)', '\b(?:setrecursionlimit|getrecursionlimit|SetMaxStack|StackOverflowError|RecursionError|stack_size|RUST_MIN_STACK)\b', '(?i)\brecurs', '\b\w+[.](?:get)?(?:[Cc]hildren|[Cc]hild[Nn]odes|[Ss]ubtrees|[Bb]ranches|[Kk]ids)\b', '\bisinstance\s*\([^)]*\b(?:dict|list|Mapping|Sequence)\b|\bArray[.]isArray\s*\(|\btypeof\s+\w+\s*===?\s*[\x22\x27]object[\x22\x27]|\bcase\s+(?:map\[|\[\])|\bValue::(?:Array|Object)\b|\binstanceof\s+(?:Map|List|Collection|JSONObject|JSONArray)\b|[.]is(?:Json)?(?:Array|Object|ContainerNode)\s*\(\s*\)']
scope: file
check_kind: semantic
severity_default: major
---

# A recursive routine reaches a base case on every input, and one whose depth grows with unbounded input checks a depth limit or is written as a loop

## Thesis
A routine that calls itself, directly or through other routines, reaches an end condition on every input: a base case that returns without recursing, which every recursive call approaches by changing the value the base case tests so that the test eventually holds. Where the depth of the recursion grows with its input — a linked structure's length, a tree's height, the nesting of data received from outside — and nothing bounds that input, the routine checks the depth of the recursion against a stated limit low enough for the stack to hold and exits with an error once the recursion goes deeper, or does the same work in a loop.

## Rationale
A recursion whose end condition is never reached calls itself over and over until the stack is exhausted. The cause is often an improper or missing conditional: a recursive call that leaves the tested value unmodified, an input changed in a way that prevents the call from detecting its exit condition, self-referencing pointers that never reach an end. A compiler lint and a static checker catch only the plain form, a routine that cannot return without calling itself; a routine whose end condition exists but is never reached on some input passes them. Recursion that does end still fails when it goes deep enough, because each level takes stack and the stack is capped: one runtime throws a stack-overflow error when an application recurses too deeply; one interpreter caps the depth of its stack with a recursion limit that prevents infinite recursion from overflowing the native stack and crashing; one runtime crashes the whole program when a single stack grows past 1 GB on 64-bit systems or 250 MB on 32-bit systems; one language gives a spawned thread a 2 MiB stack by default on its first-tier platforms. Input decides that depth: deeply nested arrays have triggered stack exhaustion, and a standard parser of nested data limits the nesting depth to 10000 to prevent stack overflow, answering deeper input with an "exceeded max depth" error. Enlarging the stack is rated a limited remedy, since the stack typically stays not very large and it might remain easy for an attacker to cause an out-of-stack fault, and an interpreter limit raised too high can itself crash the process. The remedy rated more effective puts the depth into the end condition, checking it and exiting with an error if the recursion goes too deep. A runtime without tail-call optimization gives a recursion meant to run on without end no safe recursive form, since it recurses until the system runs out of memory, and there a loop is used instead. The loop serves depth that crafted input decides as well: one standard library's remedy for stack exhaustion from deeply nested documents and from long runs of concatenated empty archive members is a loop, in the routine that skips nested elements and in the reader that moves from one member to the next.

## Example
```rust
bad:  fn total(node: Option<&Node>) -> i64 {
          node.map_or(0, |n| n.value + total(n.next.as_deref()))
      }
good: fn total(mut node: Option<&Node>) -> i64 {
          let mut sum = 0;
          while let Some(n) = node { sum += n.value; node = n.next.as_deref(); }
          sum
      }
```

## Limits
Recursion whose depth has a known bound small enough for the stack is outside the rule, such as recursion over a tree whose height was capped when it was built or parsed: one standard parser holds its pattern trees to a height of 1000 so that recursion over them, at probably about 1 kB per frame, stays clear of a 1 GB stack limit. A call in tail position escapes the depth bound only where the runtime implements tail-call optimization for it; where it does not, the call counts like any other recursive call. Raising an interpreter's recursion limit or a thread's stack size does not bound the depth and leaves the rule unmet for input of unbounded depth. A routine that hands its recursive call to a newly spawned concurrent task does not grow its own stack and is outside the rule. A project context that states the maximum depth its input can reach, enforced where that input enters the program, rejects the finding for recursion over that input. Which error a depth limit reports, recursion across asynchronous tasks, and the speed of a recursive routine are judged by their own rules.

## Validator
Grep the added lines for a call whose argument steps toward a smaller input — a count or index minus one, a field leading to a next, child or parent node, a slice that drops the first element — for a node's collection of children, for a test of whether a value is a map, an object or an array, for a recursion-limit, stack-size or stack-overflow identifier, and for the word recursion. Open the file at each hit and find the enclosing routine; confirm that it calls itself, directly or through another routine defined in the file, and skip it when it does not or when the call only spawns a concurrent task. Find its end condition and trace each recursive call: check that the call changes the value the end condition tests so that the condition eventually holds on every input, including an empty, cyclic or self-referencing one. Then decide what the depth grows with; when it grows with a list's length, a tree's height or the nesting of data read from a file, a request or another process, look for a bound: a depth argument compared with a named limit low enough for the stack to hold that many frames, exiting with an error, a cap enforced where the input is built or parsed, or a maximum depth the project context states. Treat a raised recursion limit, an enlarged stack, or a depth limit too high for the stack to hold as no bound. Validator question: **Does an added or changed routine call itself, directly or through another routine, where some input never reaches its end condition, or where its depth grows with input that nothing bounds and no depth check exits with an error before the stack runs out?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: CODE-81`, severity major, `file`, `symbol`, `code` = the recursive call and the end condition it should reach, quoted verbatim from the diff, `fix` = the recursive call changed so that it approaches its end condition, a depth argument checked against a named limit that exits with an error, or the same traversal written as a loop, in the file's language, `rationale` = the input that never reaches the end condition, or what the depth grows with and the stack limit a deep enough input meets).
