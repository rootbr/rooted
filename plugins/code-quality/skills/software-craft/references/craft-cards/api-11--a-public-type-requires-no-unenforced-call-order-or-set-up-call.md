---
title: A public type requires no call order or set-up call that neither its types nor a check at the call enforce
rule_id: API-11
domain: interface
step: [design, implement, refactor]
applies_to: [public-api]
triggers: ['\b([Ii]nit|[Ii]nitiali[sz]e|[Ss]etup|set_up|[Pp]repare|[Cc]onfigure|[Oo]pen|[Cc]onnect|[Ss]tart|[Bb]egin)(_[a-z]\w*|[A-Z]\w*)?\s*\(\s*\)', '\b(def|fn|func|void|public|async)\b[^=;]*?\b([Ii]nit|[Ii]nitiali[sz]e|[Ss]etup|set_up|[Pp]repare|[Cc]onfigure|[Oo]pen|[Cc]onnect|[Ss]tart|[Bb]egin)(_[a-z]\w*|[A-Z]\w*)?\s*\(|(?<![\w.])([Ii]nit|[Ii]nitiali[sz]e|[Ss]etup|set_up|[Pp]repare|[Cc]onfigure|[Oo]pen|[Cc]onnect|[Ss]tart|[Bb]egin)(_[a-z]\w*|[A-Z]\w*)?\s*\([^)]*\)\s*(:\s*[^={;]+)?\{', '\b\w+[.]_?(initiali[sz]ed|started|opened|connected|configured|ready)\b|\b[Ii]s_?(Initiali[sz]ed|initiali[sz]ed|Started|started|Open|open|Connected|connected|Configured|configured)\b', '(?i)\b(must|should|has to|needs to)\s+(first\s+)?be\s+(called|invoked)\s+(before|after|first|prior)\b|\bcall\s+\w+(\(\))?\s+(first|before)\b', '(?i)\b(not|never)\s+(yet\s+)?(been\s+)?(initiali[sz]ed|started|opened|connected|configured)\b']
scope: file
check_kind: semantic
severity_default: major
---

# A public type requires no call order or set-up call that neither its types nor a check at the call enforce

## Thesis
A public type spares its callers from remembering an order of calls or a set-up call. For each public operation that needs state an earlier call establishes, one of three designs holds. The value is ready when it is created: its constructor or factory takes what the operation needs, or its zero or default value can be used without further initialization, and setting its properties, in any order, means the same as passing them to a constructor. Or the types carry the order: each step returns a value of the type that alone offers the next operation, so type checking rejects a call out of order. Or the type records its own state and checks it at the call: an operation called in a state that does not admit it is rejected at that call with an error that says the object is not in an appropriate state for it.

## Rationale
Interface design aims for an interface that is hard to misuse. Interfaces often impose constraints such as a call order, and a usage that violates such a constraint is a misuse that may cause crashes, data loss and vulnerabilities. A field that no constructor sets, read by another operation without a check, could be absent after construction, and the operation fails with a null dereference when it runs before the call that sets the field. Static detectors that look for such misuses in the callers typically still have low recall and precision: an improved detector reached a recall of 20.9% and a precision of 21.9% in a typical setting, and 42.2% and 33.0% when it mined patterns across projects. A value usable without further initialization lets its user create one and get right to work, and a compiler can check that the constructor sets every field not declared as possibly absent. Properties that can be set in any order, with no difference in semantics from a constructor that takes them, impose no call order. A type per state makes a call out of order a type error, so the invalid states become impossible through type checking at compile time. A check at the call signals the misuse at the operation invoked at an inappropriate time, with an error that can identify the uninitialized state being accessed.

## Example
```java
bad:  public class Exporter {
          private Writer out;
          public void open(Writer target) { out = target; }
          public void write(String row) throws IOException { out.write(row); }
      }
good: public class Exporter {
          private final Writer out;
          public Exporter(Writer target) { out = target; }
          public void write(String row) throws IOException { out.write(row); }
      }
```

## Limits
A type per state and an object that keeps its states and transitions inside it are different trade-offs, and the rule accepts either: with a type per state the transitions are not encapsulated in the type, and the caller keeps each value a step returns. A type that models a workflow, where an order of steps is a rule of the domain, meets the rule when it holds its state itself and specifies that an operation out of order has no effect, as when approving a draft before a review was requested leaves it an unpublished draft. Properties that depend on each other may pass through a temporarily invalid combination while they are set; the exception for that combination is postponed until the object uses them together, not raised in the setter called first. A field initialized through dependency injection or inside the set-up method of a unit test, where initializing it in the constructor is not convenient, is outside the rule. A precondition, such as a constraint on an argument's value, is a separate kind of constraint from a call order and is outside the rule. A call required after use, such as one that releases a resource, is outside the rule. The project context can reject the finding by naming a type whose set-up a dependency-injection framework or a test runner performs.

## Validator
Grep the hunk for a method that sets up the object — init, setup, prepare, configure, open, connect, start, begin and the like — for a field or flag that records whether such a call has happened, and for a doc comment that tells the caller to call one operation before another. Open the file and, for each public type the hunk touches, list the fields each public operation reads. For each such field, find where it gets a value the operation can use: in every constructor or factory, by a declaration initializer, by a zero or default value, or only in another public operation; a constructor or declaration initializer that sets it to an absent value, such as a null reference or an empty optional, does not give it one. For an operation that reads a field that gets a usable value only in another public operation, trace what it does when that operation was not called first. Treat it as meeting the rule when type checking rejects the call out of order because the operation exists only on the type the earlier step returns, when the operation checks the state and rejects the call with an error, or when the type models a workflow, holds its state itself and specifies that the operation out of order has no effect. Check also whether a setter rejects a value because another property has not been set yet. Skip a type that is not public, a field set by a dependency-injection framework or by a test's set-up method, a call required after use such as releasing a resource, and a constraint on an argument's value. Validator question: **Does this public type leave its callers to remember an order of calls — an operation that, called before the call that sets up its state, passes type checking and is not rejected by a check of that state with an error, in a type that is not a workflow specifying that such a call has no effect, or a setter that refuses a value, or gives a different object, when it is called before another?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: API-11`, severity major, `file`, `symbol`, `code` = the set-up method, or the operation that reads the state it sets, quoted verbatim from the diff, `fix` = the type made ready at creation by a constructor, factory or usable default that supplies the state, or the earlier step returning the type that carries the next operation, or a state check at the start of the operation that rejects the call with an error that says the object is not in an appropriate state and identifies the state not yet set up, in the file's language, `rationale` = the earlier call the operation depends on, what the operation does when that call is skipped, and that only the caller's memory enforces the order).
