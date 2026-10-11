---
title: eval and exec receive no string that holds untrusted input, and a globals mapping that restricts or empties __builtins__ does not make such a call safe
rule_id: PY-99
domain: input
step: [implement, review]
applies_to: [python]
triggers: ['(?<![\w.])exec\(', '(?<![\w.])(?:eval|exec)\([^)\n]*,', '__builtins__']
scope: file
check_kind: semantic
severity_default: major
---

# eval and exec receive no string that holds untrusted input, and a globals mapping that restricts or empties __builtins__ does not make such a call safe

## Thesis
Python code gives eval and exec no string that holds untrusted user-supplied input, and a globals or locals mapping that restricts, replaces or empties __builtins__, {"__builtins__": {}} included, is not what makes such a call acceptable, because overriding __builtins__ is not a security mechanism.

## Rationale
eval and exec execute arbitrary code, and calling either with untrusted user-supplied input will lead to security vulnerabilities. If the globals dictionary does not contain a value for the key __builtins__, a reference to the dictionary of the built-in module builtins is inserted under that key, so all builtins are allowed unless the mapping says otherwise. Overriding __builtins__ can be used to restrict or change the available names, but this is not a security mechanism: the executed code can still access all builtins. A restricted mapping that still allows functions such as __import__ or open leaves exec insecure, since the executed code can write a file to the user's system and then execute code unrestrained by the restricted globals or locals. One position reports every use of exec because it allows arbitrary code execution, with that documented warning as the reason.

## Example
```python
bad:  exec(rule_source, {"__builtins__": {}})  # rule_source: a rule a user edited
      total = eval(formula_text, {"__builtins__": {}}, {"price": price})
good: OPERATIONS = {"discount": apply_discount, "tax": apply_tax}
      rule = json.loads(rule_source)
      result = OPERATIONS[rule["operation"]](order, *rule["args"])
```

## Limits
The sources differ on the restricted namespace. One position holds that the variables and methods available to exec can be restricted by passing optional globals and locals dictionaries, and its compliant example passes {"__builtins__": {}} under a disable comment; the other position holds that overriding __builtins__ is not a security mechanism. The separating condition is what the restriction is relied on for: a mapping that restricts or changes the names the executed code sees is allowed, a mapping relied on as the boundary that makes untrusted input safe is not, and the first position itself concedes that exec is still insecure if functions such as __import__ or open are allowed. The documented warning concerns untrusted user-supplied input; source text the program builds with no untrusted part is outside this rule.

## Validator
Grep the file for `exec(` and `eval(` not preceded by a name character or a dot, for such calls with a second argument, and for `__builtins__`. For each call, trace the first argument to where its text comes from: a request, an upload, a form field, a message, a file or setting a user edits, or a string formatted or concatenated with any of these holds untrusted input. Where it does, count a globals or locals mapping, including one that sets __builtins__ to {} or to a chosen subset, as no defence. Validator question: **Does the file pass to eval or exec a string that holds untrusted input, with or without a globals or locals mapping that restricts __builtins__?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: PY-99`, severity major, `file`, `symbol`, `code` = the eval or exec call and the line that reads its untrusted text, verbatim from the diff, `fix` = the input parsed as data and dispatched to functions the program defines, with no eval or exec, `rationale` = eval and exec run the text as code, and overriding __builtins__ is not a security mechanism because the executed code can still access all builtins).

## Source
- CPython Doc/library/functions §exec (https://docs.python.org/3/library/functions.html) — 'Overriding __builtins__ can be used to restrict or change the available names, but this is not a security mechanism: the executed code can still access all builtins.' (fetched)
- CPython Doc/library/functions §exec, warning (https://docs.python.org/3/library/functions.html) — 'This function executes arbitrary code. Calling it with untrusted user-supplied input will lead to security vulnerabilities.' (fetched)
- CPython Doc/library/functions §exec, globals (https://docs.python.org/3/library/functions.html) — 'a reference to the dictionary of the built-in module builtins is inserted under that key' (fetched)
- Pylint exec-used (W0122) (pylint-dev/pylint doc/data/messages/e/exec-used/details.rst) — 'However, use of ``exec()`` is still insecure if you allow some functions like ``__import__`` or ``open``.' (fetched)
- Pylint exec-used (W0122), restriction (pylint-dev/pylint doc/data/messages/e/exec-used/details.rst) — 'You can restrict the use of these variables and methods by passing optional globals' (fetched)
- Pylint exec-used (W0122), compliant example (pylint-dev/pylint doc/data/messages/e/exec-used/good.py) — 'all builtins are allowed. You need to be explicit about it being disallowed.' (fetched)
- Pylint exec-used (W0122), compliant example disable comment (pylint-dev/pylint doc/data/messages/e/exec-used/good.py) — 'pylint: disable-next=exec-used' (fetched)
- Pylint exec-used (W0122), unrestrained code (pylint-dev/pylint doc/data/messages/e/exec-used/details.rst) — 'and then execute code unrestrained by the' (fetched)
- Ruff S102 exec-builtin (astral-sh/ruff crates/ruff_linter/src/rules/flake8_bandit/rules/exec_used.rs) — 'The `exec()` function is insecure as it allows for arbitrary code execution.' (fetched)
- Bandit B102 (PyCQA/bandit doc/source/plugins/b102_exec_used.rst) — 'The Python docs succinctly describe why the use of `exec` is risky.' (fetched)
