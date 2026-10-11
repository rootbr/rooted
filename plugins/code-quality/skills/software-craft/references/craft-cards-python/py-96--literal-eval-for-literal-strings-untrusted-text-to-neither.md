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

## Source
- Pylint eval-used (W0123) (pylint-dev/pylint pylint/checkers/base/basic_checker.py, W0123 message definition) — 'Consider using `ast.literal_eval` for safely evaluating strings containing Python expressions from untrusted sources.' (fetched)
- Ruff S307 suspicious-eval-usage (astral-sh/ruff crates/ruff_linter/src/rules/flake8_bandit/rules/suspicious_function_call.rs) — 'consider using `ast.literal_eval()` instead, which will raise an exception if the expression is not a valid Python literal.' (fetched)
- Bandit B307 (PyCQA/bandit doc/source/blacklists/blacklist_calls.rst) — 'Use of possibly insecure function - consider using safer ast.literal_eval.' (fetched)
- CPython Doc/library/ast.rst §literal_eval (https://raw.githubusercontent.com/python/cpython/main/Doc/library/ast.rst) — 'This is specifically designed not to execute Python code, unlike the more general :func:`eval`. There is no namespace, no name lookups, or ability to call out. But it is not free from attack: A relatively small input can lead to memory exhaustion or to C stack exhaustion, crashing the process.' (fetched)
- CPython Doc/library/ast.rst §literal_eval, trust (https://raw.githubusercontent.com/python/cpython/main/Doc/library/ast.rst) — 'This function had been documented as "safe" in the past without defining what that meant. That was misleading.' (fetched)
- CPython Doc/library/ast.rst §literal_eval, untrusted data (https://raw.githubusercontent.com/python/cpython/main/Doc/library/ast.rst) — 'There is also the possibility for excessive CPU consumption denial of service on some inputs. Calling it on untrusted data is thus not recommended.' (fetched)
- CPython Doc/library/ast.rst §literal_eval, accepted input (https://raw.githubusercontent.com/python/cpython/main/Doc/library/ast.rst) — 'It is not capable of evaluating arbitrarily complex expressions, for example involving operators or indexing.' (fetched)
- CPython Doc/library/ast.rst §literal_eval, warning (https://raw.githubusercontent.com/python/cpython/main/Doc/library/ast.rst) — 'It can raise :exc:`ValueError`, :exc:`TypeError`, :exc:`SyntaxError`, :exc:`MemoryError` and :exc:`RecursionError` depending on the malformed input.' (fetched)
- CPython Doc/library/ast.rst §literal_eval, definition (https://raw.githubusercontent.com/python/cpython/main/Doc/library/ast.rst) — 'Evaluate an expression node or a string containing only a Python literal or container display.' (fetched)
- CPython Doc/library/ast.rst §literal_eval, literal structures (https://raw.githubusercontent.com/python/cpython/main/Doc/library/ast.rst) — 'strings, bytes, numbers, tuples, lists, dicts, sets, booleans, ``None`` and ``Ellipsis``.' (fetched)
- CPython Doc/library/functions §eval (https://docs.python.org/3/library/functions.html) — 'This function executes arbitrary code. Calling it with untrusted user-supplied input will lead to security vulnerabilities.' (fetched)
