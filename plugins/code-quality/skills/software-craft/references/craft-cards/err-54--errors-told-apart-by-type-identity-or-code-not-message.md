---
title: Code that tells apart errors tests their type, identity or a structured field such as a code, not their message text, wherever the error's producer exposes such structure
rule_id: ERR-54
domain: errors
step: [implement, handle-errors, test]
applies_to: [exceptions, result-types, tests]
triggers: ['[.]Error\(\)\s*(==|!=)|\bstrings[.](Contains|HasPrefix|HasSuffix|EqualFold|Index)\([^)]*[.]Error\(\)|\bregexp[.]MatchString\([^)]*[.]Error\(\)', '[.]get(Localized)?Message\(\)\s*([.](equals|equalsIgnoreCase|contains|startsWith|endsWith|matches)\(|==|!=)', '[.][mM]essage\s*(===?|!==?)|[.][mM]essage[.](includes|startsWith|endsWith|match|indexOf|Contains|StartsWith|EndsWith|Equals)\(|[.]test\(\s*\w+[.]message\s*\)|\bswitch\s*\(\s*\w+[.][mM]essage\s*\)', '\bstr\(\s*\w+\s*\)\s*(==|!=|[.](startswith|endswith|find)\()|\bin\s+str\(\s*\w+\s*\)|[.]args\[0\]\s*(==|!=)', '\b(e|err|error)[.]to_string\(\)\s*(==|!=|[.](contains|starts_with|ends_with)\()', '\b(assert|require)[.](EqualError|ErrorContains)\(|\b(assert|require)[.](Equal|Contains)\([^;]*[.]Error\(\)|[.]Error\(\)\s*[,;]|\bswitch\s+\w+[.]Error\(\)|\bassert(Equals|That)\([^;]*[.]get(Localized)?Message\(\)|[.]equals(IgnoreCase)?\(\s*\w+[.]get(Localized)?Message\(\)\s*\)|[.]hasMessage(Containing|StartingWith|EndingWith|Matching)?\(|\bAssert[.](AreEqual|Equal|StartsWith|Contains)\([^;]*[.]Message\b|[.]WithMessage\(|\bexpect\(\s*\w+[.]message\s*\)|[.]toThrow(Error)?\(\s*["\x27`/]|\bstr\(\s*\w+[.](value|exception)\s*\)|\bpytest[.]raises\([^)]*\bmatch\s*=|[.]assertRaisesRegexp?\(|\bassert(_eq|_ne)?!\([^;]*[.]to_string\(\)']
scope: file
check_kind: semantic
severity_default: major
---

# Code that tells apart errors tests their type, identity or a structured field such as a code, not their message text, wherever the error's producer exposes such structure

## Thesis
Code that branches on which error occurred, and a test that checks which kind of error came back, identify the error by its type, by its identity (a sentinel value, compared through a wrap-aware test where errors are wrapped) or by a structured field such as a code, whenever the error's producer exposes such structure for the condition, whichever it is: a dependency, the runtime, the standard library, another module, the same module or, for a test, the code under test. The message text stays out of that decision.

## Rationale
Error values typically have a component intended for human eyes and a component intended for semantic control flow. Message text is the first: written for human consumption, it is subject to rewording or punctuation changes, and one runtime documents that its messages may change between any two versions while its error codes change only between major versions. Telling errors apart by their message is therefore error-prone and difficult to maintain, since a rewording may break any parsing written to consume the text. A test that compares message strings to check which kind of error came back becomes brittle when a message is reworded, and can turn into a change detector. A type, a sentinel value or a code is the component meant for control flow: it lets the caller tell conditions apart programmatically, and the same runtime calls its code property the most stable way to identify an error.

## Example
```python
bad:  try: conn.send(data)
      except OSError as err:
          if "Connection reset" not in str(err): raise
          reconnect()
good: try: conn.send(data)
      except ConnectionResetError:
          reconnect()
```

## Limits
Whether the error's producer exposes a type, sentinel value or code for the condition separates the cases the evidence disagrees on. A match on an error whose producer exposes nothing but text for the condition gets no finding: one platform reference shows code dispatching on the messages of errors that the same code throws, which share one type and carry no other discriminator, while it advises a library to prefer an error cause for discriminating its errors over asking consumers to parse the message; one standard library's release notes record that, before a sentinel for I/O on a closed network connection existed, the only way to reliably detect the case was to match the error string; and, for such an error from a dependency outside the code's control, the evidence suggests considering a bug filed against the owner to help improve the API rather than relying on parsing the message. Where the producer does expose such structure, the finding applies whoever owns the message: a style guide that says not to distinguish errors by their string form marks as bad a caller that matches the text of sentinel values its own package defines. A test that checks a property of the messages from the package under test, for example that a message includes the parameter name, gets no finding: the guide that rules out string comparison to check what type of error a function returns permits it. Giving errors that structure is the producer's task; this rule judges the code that consumes them. Showing the message to a person or logging it for debugging, the use it is written for, is outside the rule.

## Validator
Grep the hunk for a comparison, containment test, prefix or suffix test, regular-expression match or switch on an error's message or string form. Open the file and find where the error comes from: the call inside the try block, or the call that returned the error value. Set aside a test that checks a property of messages from the package under test, such as that a message names a parameter; what remains tells apart which error occurred. Trace the producer's errors for that condition, whether the producer is another component, the same module or, for a test, the code under test: a dedicated error class or subclass, a sentinel value, or a code field such as an error number or a code string. Validator question: **Does the code or test tell an error condition apart by matching message text where the error's producer exposes a type, sentinel value or structured field for the condition?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: ERR-54`, severity major, `file`, `symbol`, `code` = the line that compares, searches or switches on the error's message text, `fix` = the same branch rewritten to test the error's type, sentinel value or code in the file's language, `rationale` = names the component that produces the message and the type, sentinel value or code it exposes for the condition).
