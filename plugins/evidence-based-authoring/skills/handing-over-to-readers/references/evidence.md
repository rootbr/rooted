# Evidence

Evidence for an agent's claim is a result produced outside the agent's write zone — a test, an exit code, a read log, a verified anchor; the agent's own report is none.

## Accepted

- A test that fails when the change is reverted, provided the test, the grading code and the build and CI configuration lie outside the paths the agent may write. Inside those paths a green exit code comes without the test passing, from an early `sys.exit(0)` or from a `conftest.py` that patches the test report, and `testFailureIgnore` in `pom.xml` or `ignoreFailures` in `build.gradle` does the same in a Java build.
- An exit code taken by the harness or CI — of the tests, a linter, a compiler, a type checker, a reconciliation script, a mutation run. The report's status line names an enumerated value (`clean`, `findings`, `failed`, `not-run`) and the count of checked units, and a missing answer from a checker counts as a failure. The exit code counts only from a process outside the agent's write zone, since a process the agent writes into returns 0 from `sys.exit(0)`.
- The log of files read, taken from the harness transcript rather than from the agent's report: agents failed to read every file they were asked to review in 67.9 % of runs and misled about it in 80.4 % of those.
- A `path:line` anchor with the fragment of that line; `scripts/check_report.py` matches the fragment against the line's content, not only the address.

## Not accepted

- A self-report: "everything works", "the tests pass", "done" without an exit code and an anchor. False success made up 45–48 % of failures in single-control tau2-bench domains and 75.8 % of AppWorld coding-agent trajectories with explicit status claims, and 3 % in dual-control telecom, so the rate depends on the setting. An agent that read untrusted content — issues, the web, other people's files — returns a summary that is a self-report of the same kind: the evidence is the diff and the check result, which the author of that content does not write.
- The verdict of an LLM judge reading the same text without access to the environment: no configuration exceeded AUROC 0.65 on tau2-bench, and the same judges reached 0.54 on AppWorld traces. These studies do not measure how reliably a judge with access to the artefacts detects false success; its verdict becomes evidence only when the harness, outside the judge's write zone, writes the exit code and the run log.
- A green test as evidence about races, inter-thread order and latency: an ordinary test does not explore thread schedules. For this class the evidence is its own — jcstress or model checking with a run threshold, JMH against a baseline with a tolerance — and without it the reviewer reads the code.
