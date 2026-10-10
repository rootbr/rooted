---
title: Per-element work that must stop the iteration early or return from the enclosing routine is written as a loop or a short-circuiting step rather than a for-each callback
rule_id: DSN-56
domain: design
step: [implement]
applies_to: [functional]
triggers: ['\b(forEach\w*|for_each|foreach|each|ForEach)\(', '\b(throw|raise)\s+(new\s+)?\w*(Break|Stop|Exit|Found|Done|BREAK|STOP|EXIT|FOUND|DONE)\w*']
scope: hunk
check_kind: semantic
severity_default: minor
---

# Per-element work that must stop the iteration early or return from the enclosing routine is written as a loop or a short-circuiting step rather than a for-each callback

## Thesis
Per-element work that has to stop the iteration before the last element, or to return from the enclosing routine at the element it has reached, is written as a loop whose body uses break or return at that element. When the stop condition itself yields the result — the first element that matches, or whether any element or every element matches — the work is written as a short-circuiting step such as find, any, some, all or every, and a leading run of elements that meet a condition may be taken with a take-while step, which ends at the first element that fails its predicate. A callback handed to a for-each step, a routine that calls the callback once for each element, does not carry such work: it is not made to stop by an exception thrown on a normal outcome and caught around the step, nor by a flag it sets that the remaining calls test so as to do nothing, and a return inside it is not relied on to leave the enclosing routine.

## Rationale
A for-each step calls its callback once for each element until every element has been processed or the callback throws an exception; unless the step's protocol gives the callback's return value a stop meaning, there is no other way to stop it. The callback is a function of its own: a loop's break and continue cannot be written inside it, and a return inside it stops only the current call and hands control back to the step, which discards the returned value and goes on to the next element. A return written to leave the enclosing routine early therefore leaves only the callback, and the routine carries on after the step. A flag that the remaining calls test does not stop the step either, since the step still calls the callback for every remaining element. A thrown exception caught around the step is the one stop the step allows, and where the work needs to stop, the for-each step is the wrong tool. A loop states the same work directly: break ends the loop early, return leaves the enclosing routine, and continue skips to the next element. A short-circuiting step stops as soon as its answer is determined: find at the first element its predicate accepts, any or some at the first true, all or every at the first false, and take-while at the first element that fails its predicate, ignoring the rest.

## Example
```python
bad:  class Stop(Exception): ...
      def send_fresh(item):
          if item.expired: raise Stop
          send(item)
      try: for_each(items, send_fresh)
      except Stop: pass
good: for item in items:
          if item.expired: break
          send(item)
```

## Limits
A callback that does its work on every element, with no stop to make, meets the rule, and at the end of a longer chain of steps a for-each step may read more plainly than a loop. A bare return that ends the current call so as to skip the rest of one element's work is not an attempt to stop: the step goes on with the next element, as intended. An iteration protocol in which the callback's return value stops the iteration provides the stop as part of its contract, so a callback that returns that value meets the rule: an iterator function stops when its yield callback returns false, and a fallible for-each step stops at the first break value its callback returns. An exception thrown because an element failed, and relayed to the step's caller, reports a failure and is outside the rule, which reaches an exception thrown to stop on a normal outcome such as a match found.

## Validator
Grep the added lines for a for-each call (forEach, for_each, each, or a helper that calls a callback once per element) and for a throw or raise of an exception whose name marks a stop (Break, Stop, Exit, Found, Done). Read the callback in the hunk, whether written inline or as a named function the hunk shows, and the lines around the for-each call. Look for three shapes: an exception thrown inside the callback on a normal outcome and caught around the call; a captured flag set inside the callback once the stop condition holds and tested by the later calls so that they return at once; a return inside the callback whose value was meant as the enclosing routine's result, which the step discards while the routine goes on past the step. Set aside a bare return that skips the rest of one element's work, a callback with no stop to make, a callback that returns the stop value its protocol defines (false from a yield callback, a break value from a fallible for-each), and an exception that reports a failure. Validator question: **Does an added for-each callback try to stop the iteration, or to leave the enclosing routine, through an exception thrown on a normal outcome and caught around the step, a flag that makes the remaining calls return at once, or a return whose value the step discards?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: DSN-56`, severity minor, `file`, `symbol`, `code` = the added line inside the callback that throws the stop, sets or tests the flag, or returns the value meant for the enclosing routine, with the for-each call line when the diff adds it, quoted verbatim from the diff, `fix` = the work rewritten as a loop that uses break or return at the stopping element, or as the short-circuiting step (find, any, some, all, every, take-while) that yields the result, in the file's language, `rationale` = which stop the callback emulates (an exception caught around the step, a flag the remaining calls test, a return whose value the step discards) and that the step calls the callback for every remaining element unless the callback throws).
