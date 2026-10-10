---
title: A breakpoint written into the source, such as a debugger statement, a call that enters the debugger or an import made only to reach one, is removed before the change lands, and breakpoints are set in the debugging tool instead
rule_id: PRF-04
domain: performance
step: [implement, review]
applies_to: [universal]
triggers: ['^\s*debugger\s*;?\s*(//.*)?$', '\b(i?pdb|pudb|rdb)\s*[.]\s*set_trace\s*\(', '(?<![.\w])breakpoint\s*\(\s*\)|\bsys\s*[.]\s*breakpointhook\s*\(', '^\s*(import\s+(i?pdb|pudb|debugpy|ptvsd)\b|from\s+(i?pdb|pudb|debugpy|ptvsd)\b\s+import\b)', '\b(debugpy|ptvsd)\s*[.]\s*(listen|wait_for_client|wait_for_attach|break_into_debugger|breakpoint|enable_attach)\s*\(', '\bruntime\s*[.]\s*Breakpoint\s*\(\s*\)']
scope: file
check_kind: mechanical
severity_default: major
---

# A breakpoint written into the source, such as a debugger statement, a call that enters the debugger or an import made only to reach one, is removed before the change lands, and breakpoints are set in the debugging tool instead

## Thesis
A statement or call that stops execution and opens a debugger at its location, or that accepts or waits for a debugger attaching to the program, and an import of a debugger module kept only to reach one, stays in the code only while that code is actively being debugged; it is removed before the change lands, so code headed for production carries none, and a breakpoint is set at the line in the debugging tool instead.

## Rationale
A debugger statement, call or import is for debugging purposes only, and in production code its presence is likely a mistake. A debugger statement or call tells the executing environment to stop execution and start a debugger at that point: in a browser it can stop executing code and open a debugger, and in a program it may cause unintended behavior such as exposing sensitive information or making the program hang. When reaching the debugger takes an import on one line and a call on another, the split adds opportunities for mistakes at clean-up time, because one of the lines can be forgotten once the code no longer needs debugging. A debugging tool sets a breakpoint at a given line without an edit to the source, and the correct example in the linter documentation replaces the statement with a breakpoint set at that line. Linters report these statements, calls and imports in their default or recommended rule sets.

## Example
```python
bad:  import pdb
      def total(items):
          pdb.set_trace()
          return sum(items)
good: def total(items):
          return sum(items)  # breakpoint set on this line in the debugger
```

## Limits
While code is actively being debugged, inserting the statement or call at the location to break is a documented way to enter the debugger, and a project may switch the check off while code is still very much in development; the rule applies to every change submitted to land, since that code is no longer being actively debugged. In place of the breakpoint, information about the program's state can be logged through a logging library, and tests can verify that the program behaves as expected.

## Validator
Grep the added lines of the hunk with the triggers for a standalone debugger statement, a call that enters a debugger, executes a breakpoint trap or makes the program accept or wait for a debugger attaching, and an import of a debugger module. Open the hunk around each hit and confirm that the name resolves to the debugger entry point rather than to a project symbol of the same name, and that the file is shipped or committed code rather than the debugging tooling's own source. For an import, trace whether anything other than such a call uses it. Validator question: **Does the hunk add a statement, call or import whose only purpose is to stop execution in a debugger or to reach one?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: PRF-04`, severity major, `file`, `symbol`, `code` = the added debugger statement, call or import line verbatim, `fix` = the same routine without that line and without an import kept only for it, in the file's language, `rationale` = names that the line stops execution or waits for a debugger in code that lands, and that the breakpoint belongs in the debugging tool).
