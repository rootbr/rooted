---
title: At least one test or other dynamic-analysis run keeps the program's assertions enabled
rule_id: API-06
domain: interface
step: [test]
applies_to: [universal]
triggers: ['\bPYTHONOPTIMIZE\b|\b(python[0-9.]*|executable)\b.*[\s\x22\x27,]-[A-Za-z]*O[A-Za-z]*([\s\x22\x27,]|$)', '(?<![\w-])-(da|disableassertions)(?![\w-])', '(?i)enable_?assertions\b[\x22\x27]?\s*(>|=|:|\(|\s)\s*[\x22\x27]?false\b', '(?i)debug[-_]assertions\s*[=:]\s*[\x22\x27]?(false|off|no|n)\b', '\bcargo\b[\s\x22\x27,]+(\+[\w.-]+[\s\x22\x27,]+)?(test|nextest[\s\x22\x27,]+run)\b.*[\s\x22\x27,](-r|--release|--profile[\s=\x22\x27,]+(release|bench))(?![\w-])', '\bjava\b.*\b(junit|testng|ConsoleLauncher)']
scope: file
check_kind: mechanical
severity_default: minor
---

# At least one test or other dynamic-analysis run keeps the program's assertions enabled

## Thesis
At least one configuration that runs the code's tests, its fuzzing or another dynamic analysis executes the code with its assertions enabled. That run passes no interpreter or launcher switch that strips or disables assertions throughout the code under test, sets no environment variable or build setting that does, and selects no build profile that compiles them out; where the runtime disables assertions by default, it passes the switch that enables them or runs through a test runner that does. Whether the production build keeps the assertions is outside the rule.

## Rationale
Assertions are normally compiled into the code at development time and compiled out later so that they do not degrade performance, and an assertion form that only unoptimized builds execute by default is useful for checks too expensive to be present in a release build. An assertion that disappears from production builds is verified only in tests, on developer machines and in whatever pre-release builds keep it. A run with the assertions off does not execute them: one interpreter switch, or the environment variable equivalent to it, removes the assert statements and any code conditional on the debug flag; one runtime disables assertions in all packages and classes unless a launcher switch enables them; and an optimized build does not execute debug assertions unless a compiler flag turns them back on, so a test command that selects the release profile, whose default turns debug assertions off, runs without them. A test whose check is an assertion that is not executed continues to pass even if a bug is introduced, and one test runner started with the optimize switch warns that assertions outside the test modules will be ignored because they are not executed. Assertions make dynamic analysis more effective because they increase the number of problems, vulnerabilities among them, that it can detect; in a case study of two commercial components whose developers employed assertions systematically, the assertions found a large percentage of the faults in the bug database. Two build tools' test tasks enable assertions by default for the runtime that disables them, and a setting turns that off. Enabling assertions during dynamic analysis is completely different from enabling them in production, where in many cases they should not be enabled.

## Example
```go
bad:  test := exec.CommandContext(ctx, "python3", "-O", "-m", "pytest", dir)
      fuzz := exec.CommandContext(ctx, "java", "-da", "-jar", fuzzerJar)
good: test := exec.CommandContext(ctx, "python3", "-m", "pytest", dir)
      fuzz := exec.CommandContext(ctx, "java", "-ea", "-jar", fuzzerJar)
```

## Limits
A run with the assertions off follows the rule while another test, fuzzing or other dynamic-analysis run keeps them on, since the rule asks for at least some dynamic analysis with assertions enabled. A production build, a deployment configuration or a release profile that switches assertions off is outside the rule: whether production keeps them is up to the project and its users. An assertion form that no switch removes, such as a non-debug assertion macro or an always-enabled assertion library, executes in every run and is outside the rule; which form a check takes is judged by its own rule. The source states the rule as a suggestion and a recommendation, not a requirement, so a project context that documents why its dynamic analysis runs with assertions off rejects the finding. A switch or setting that disables assertions only in named packages, classes or dependencies, in a run that keeps the rest of the code's assertions enabled, follows the rule, since the source asks for a configuration that enables many assertions, not every one.

## Validator
Grep the added lines for an interpreter's optimize switch or the environment variable equivalent to it, a launcher switch that disables assertions, an enable-assertions setting set to false, a debug-assertions setting set to off, a test command that selects a release or other optimized profile, and a launcher started directly on a test platform. For each hit, open the file and decide what the line configures: a test, fuzzing or other dynamic-analysis run (a CI job or step that runs tests, a test-runner or test-task setting, a profile a test command selects, a harness that starts the code under test) or the production build, a deployment or a release profile; only a dynamic-analysis run is in scope. For a launcher of a runtime that disables assertions by default, check whether the run passes the enabling switch or goes through a test task that enables them. Then look through the file for another test, fuzzing or other dynamic-analysis run, such as a sibling matrix entry or a second job, whose configuration keeps the assertions on, and check the project context for a documented reason to run with them off. Validator question: **Does an added line make a test, fuzzing or other dynamic-analysis run execute the code with its assertions off, while no other test, fuzzing or other dynamic-analysis run in the file keeps them on?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: API-06`, severity minor, `file`, `symbol`, `code` = the added switch, environment variable, setting or profile selection that turns the assertions off, or the launcher line that omits the enabling switch, verbatim from the diff, `fix` = the same run without that switch or setting, or with the enabling switch where the runtime disables assertions by default, or a second run of the same tests that keeps them on, in the file's language, `rationale` = which assertions the run does not execute and that no other dynamic-analysis run in the file executes them).
