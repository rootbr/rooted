---
title: A string holding only Python literal values is turned into a value with ast.literal_eval rather than eval, and text from an untrusted source goes to neither function
rule_id: PY-96
domain: input
step: [implement, review]
applies_to: [python]
triggers: ['(?<![\w.])eval\(', '=\s*eval\(', 'literal_eval\(']
scope: file
check_kind: semantic
severity_default: major
---

# A string holding only Python literal values is turned into a value with ast.literal_eval rather than eval, and text from an untrusted source goes to neither function

## Thesis
Where Python code turns into a value a string that holds only a Python literal or container display (strings, bytes, numbers, tuples, lists, dicts, sets, booleans, None and Ellipsis), it calls ast.literal_eval rather than eval; text from an untrusted source is given to neither function, since eval executes it as code and calling literal_eval on untrusted data is not recommended.

## Rationale
eval executes arbitrary code, and calling it with untrusted user-supplied input will lead to security vulnerabilities. ast.literal_eval evaluates an expression node or a string containing only a Python literal or container display; it is specifically designed not to execute Python code, with no namespace, no name lookups and no ability to call out, and it raises an exception if the expression is not a valid Python literal. It is not free from attack: a relatively small input can lead to memory exhaustion or to C stack exhaustion, crashing the process, some inputs can cause excessive CPU consumption, and malformed input can raise ValueError, TypeError, SyntaxError, MemoryError or RecursionError. The function's past description as "safe", given without defining what that meant, is misleading, and calling it on untrusted data is not recommended. One position reports every use of eval and names ast.literal_eval as the replacement.

## Example
```python
bad:  saved_text = state_path.read_text()  # a list literal this program wrote
      retry_codes = eval(saved_text)
good: saved_text = state_path.read_text()  # a list literal this program wrote
      retry_codes = ast.literal_eval(saved_text)
```

## Limits
The sources differ on literal_eval for untrusted text. One position offers ast.literal_eval for safely evaluating strings containing Python expressions from untrusted sources, or calls it the safer choice there; the other position holds that the function is designed not to execute Python code, that a relatively small input can exhaust memory or the C stack, and that calling it on untrusted data is not recommended. The separating condition is the trust of the text: for text the program trusts, literal_eval replaces eval; for untrusted text, the documented behaviour of literal_eval itself applies, and the earlier "safe" label is misleading. A string whose value needs operators, indexing, name lookups or calls is not a literal: literal_eval is not capable of evaluating such expressions, and this rule does not say how such a string is handled.

## Validator
Grep the hunk for `eval(` not preceded by a name character or a dot, then open the file and also find every `literal_eval(` call. For each eval call, trace its first argument to where the string is made: a string that holds only literal values (a list, dict, tuple, set, number, string, bytes, boolean or None display, such as text the program itself wrote with repr) is the first case. For each eval or literal_eval call, trace the argument to its origin: text from a request, an upload, a form field, a message or another source the program does not trust is the second case. Validator question: **Does the file turn a string that holds only literal values into a value with eval, or pass text from an untrusted source to eval or ast.literal_eval?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: PY-96`, severity major, `file`, `symbol`, `code` = the eval or literal_eval call and the line that produces its argument, verbatim from the diff, `fix` = `ast.literal_eval(text)` for literal text the program trusts, or for untrusted text a parse that calls neither function, `rationale` = eval executes the string as code, while literal_eval evaluates only literals and is not recommended on untrusted data because a small input can exhaust memory or the C stack).
