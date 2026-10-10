---
title: A Python logger is obtained with logging.getLogger(__name__), never by instantiating logging.Logger directly and never named by __file__ or __cached__
rule_id: PY-105
domain: errors
step: [implement, review]
applies_to: [python]
triggers: ['\blogging[.]Logger\(', '\bgetLogger\(\s*__(?:file|cached)__\s*\)', '(?<![.\w])Logger\(\s*(?:__name__|[\"''])']
scope: hunk
check_kind: mechanical
severity_default: major
---

# A Python logger is obtained with logging.getLogger(__name__), never by instantiating logging.Logger directly and never named by __file__ or __cached__

## Thesis
Python code obtains each logger through logging.getLogger(name), conventionally a module-level logger = logging.getLogger(__name__), rather than by instantiating logging.Logger, and the name it passes is the module's __name__, the fully qualified dotted module name, rather than __file__ or __cached__, which are file paths.

## Rationale
The logging documentation states that loggers should never be instantiated directly but always obtained through the module-level function logging.getLogger(name), and multiple calls to getLogger() with the same name always return a reference to the same Logger object. A directly instantiated logger is not added to the logger tree and bypasses all configuration: messages logged to it are sent only to the handler of last resort, skipping any filtering or formatting. The logger name hierarchy is analogous to the package hierarchy, and identical to it when loggers are organised per module with logging.getLogger(__name__), so logger names track the package/module hierarchy and it is intuitively obvious where events are logged just from the logger name. __name__ is the fully qualified module name, such as foo.bar, the intended format for logger names; __file__ is the pathname of the module, such as foo/bar.py, and __cached__ the pathname of its compiled version, such as foo/__pycache__/bar.cpython-311.pyc.

## Example
```python
bad:  logger = logging.Logger(__name__)
good: logger = logging.getLogger(__name__)
```

## Limits
An application that needs custom logger behavior installs its logger class with logging.setLoggerClass(), which tells the logging system to use that class when instantiating a logger and is typically called before any loggers are instantiated; the card concerns calling a logger class directly, not defining one. A literal name passed to logging.getLogger() keeps the logger in the tree; the card's name check covers the two module-level dunder constants that are file paths, __file__ and __cached__.

## Validator
Grep the hunk for logging.Logger(, for a bare Logger( call, and for getLogger(__file__) or getLogger(__cached__). Open the file's imports to confirm that a bare Logger is logging.Logger and not another class of that name. Validator question: **Does the hunk instantiate logging.Logger directly, or pass __file__ or __cached__ as the name to logging.getLogger()?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: PY-105`, severity major, `file`, `symbol`, `code` = the logger construction verbatim, `fix` = `logger = logging.getLogger(__name__)`, `rationale` = a directly built logger bypasses all logging configuration and reaches only the handler of last resort, and a logger named by a file path does not track the package/module hierarchy).
