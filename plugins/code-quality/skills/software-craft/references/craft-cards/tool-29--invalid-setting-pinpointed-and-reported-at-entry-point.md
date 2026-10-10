---
title: An invalid configuration value stops initialization with a message pinpointing the setting by name and value or by location, reported at the entry point
rule_id: TOOL-29
domain: tooling
step: [handle-errors, implement, review]
applies_to: [universal]
triggers: ['(?i)\b(?:config|conf|cfg|settings?|options?|env|flags?)\w*\b.*\b(?:panic!?|unwrap|expect|Fatal\w*|exit|raise|throw)\b', '(?i)\b(?:panic!?|Fatal\w*|exit|raise|throw)\b.*\b(?:config|conf|cfg|settings?|env|flags?)\w*', '\b(?:parse\w*|Parse\w*|Atoi|int|float|Number)\s*\(\s*(?:System[.](?:getenv|getProperty)|os[.](?:Getenv|getenv|environ)|process[.]env)']
scope: file
check_kind: semantic
severity_default: major
---

# An invalid configuration value stops initialization with a message pinpointing the setting by name and value or by location, reported at the entry point

## Thesis
When a value read from the environment, a flag or a configuration file fails its check during program initialization, the program denies the setting and reports a message that pinpoints the error: the misconfigured setting's name and rejected value, or its location, such as the line in the file, together with how to fix it. The error is propagated upward to the entry point, which reports that message on the display or in the log and exits with a non-zero status. A crash, a hang, an exit without a pinpointing message or a functional failure without one is a misconfiguration vulnerability of the program, and ending initialization by aborting at the check with a stack trace is, in general, avoided.

## Rationale
Configuration errors that manifest as crashes, hangs or silent failures resemble software bugs; they leave users clueless and forced to report to developers for technical support, wasting the time and effort of both. An exit without a pinpointing message gives users no useful feedback to fix the problem by themselves, and a functional failure without one can confuse them. Injecting configuration errors into one commercial storage system and six open-source server applications exposed 743 bad reactions (crashes, hangs, early terminations, functional failures, and settings silently changed or ignored), of which 364 were confirmed or fixed by the developers; every open-source system showed bad reactions such as crashes, hangs and early terminations under some misconfigurations. Good log messages can shorten users' self-diagnosis time by up to an order of magnitude. A stack trace that points at the check is not likely to be as useful as a human-generated, actionable message, so the check returns the error and the entry point reports it; by convention a non-zero exit status indicates an error.

## Example
```java
bad:  int cfgPort = Integer.parseInt(System.getenv("APP_PORT"));
      if (cfgPort < 1 || cfgPort > 65535) throw new IllegalStateException("invalid configuration");
good: static int port(String raw) {
        int p = raw != null && raw.matches("\\d{1,5}") ? Integer.parseInt(raw) : 0;
        if (p < 1 || p > 65535) throw new IllegalArgumentException("APP_PORT=" + (raw == null ? "<unset>" : "\"" + raw + "\"") + " (environment) is not 1-65535; set e.g. APP_PORT=8080");
        return p; }
      public static void main(String[] args) {
        int port; try { port = port(System.getenv("APP_PORT")); }
        catch (IllegalArgumentException e) { System.err.println("configuration error: " + e.getMessage()); System.exit(1); return; }
        run(port); }
```

## Limits
Either form of pinpointing suffices: the setting's name and value, or its location. Code below the entry point, such as a library that loads settings for its caller, prefers returning the error to its caller over aborting the program. Terminating the program at a failed check is occasionally necessary for an internal invariant whose failure means the internal state has become unrecoverable; an erroneous setting is instead denied and pinpointed. A misconfiguration that only degrades performance, with correct functionality, is outside the rule unless the degradation affects usability, which counts as a hang.

## Validator
Grep the hunk for reads of settings, environment lookups, system properties, flag parsing and configuration-file loading, and for a conversion or check of the value read that throws, panics, forces an absent value, exits or logs fatally. Open the file and trace each such failure to the message it produces, to where it is caught and to how the program ends. Check that the message names the setting with its rejected value or its location and a fix, that the error reaches the entry point, and that the entry point reports it and exits with a non-zero status. Validator question: **Does a setting read in this file, when its value fails conversion or a check during initialization, end the program in a crash, a hang, an uncaught exception or panic with a stack trace, an exit before the error reaches the entry point, an exit with no message or a zero status, or a message that names neither the setting with its value nor where it was set?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: TOOL-29`, severity major, `file`, `symbol`, `code` = the line that reads or converts the setting and the line that throws, panics or exits, quoted verbatim from the diff, `fix` = the check returning an error that names the setting, the rejected value or its location and a fix, and the entry point printing it to standard error and exiting with a non-zero status, in the file's language, `rationale` = the setting, the reaction it gets today (crash, hang, stack trace, exit before the error reaches the entry point, silent exit or vague message) and what the message leaves out).

## Source
- DOI 10.1145/2517349.2522727, §3.1 and Table 3 (fetched): "When a misconfiguration occurs, the system should pinpoint either the misconfigured parameter’s name/value or its location information (e.g., line numbers in the file). Otherwise, SPEX-INJ considers the system reaction as a misconfiguration vulnerability."; Table 3: "Early termination: The system exits without pinpointing the injected configuration error." "Functional failure: The system fails functional testing without pinpointing the injected error."; "the system terminates itself but does not give useful feedback for users to fix the problems by themselves. Similarly, function failures without pinpointing error messages can also confuse users"; "Unless the performance degradation affects the system usability (belonging to “hang”), we consider it acceptable"; abstract: "Many configuration issues manifest themselves in ways similar to software bugs such as crashes, hangs, silent failures. It leaves users clueless and forced to report to developers for technical support, wasting not only users’ but also developers’ precious time and effort.", "We evaluate SPEX with one commercial storage system and six open-source server applications."; §4.1 and Table 5(a): "SPEX-INJ exposes a total of 743 vulnerabilities ... 364 of them have been confirmed or fixed by the developers", "all the open-source systems experienced bad reactions such as crashes, hangs, and early terminations under some misconfigurations".
- DOI 10.1145/2791577, §6.2 and §7 (fetched): "When users’ configuration settings violate constraints, the system should pinpoint the error and provide potential solutions via the display (e.g., stdout, stderr) or log messages. ... good log messages can shorten users’ self-diagnosis time by up to an order of magnitude."; "when the users misconfigure the system, the system should not fail or crash; instead, the system should deny the erroneous settings and print log messages to pinpoint the errors."
- google/styleguide go/best-practices.md, 'Program initialization' and 'Program checks and panics' (fetched): "Program initialization errors (such as bad flags and configuration) should be propagated upward to `main`, which should call `log.Exit` with an error that explains how to fix the error. In these cases, `log.Fatal` should not generally be used, because a stack trace that points at the check is not likely to be as useful as a human-generated, actionable message."; "Libraries should prefer returning an error to the caller rather than aborting the program"; "It is occasionally necessary to perform consistency checks on an invariant and terminate the program if it is violated. In general, this is only done when a failure of the invariant check means that the internal state has become unrecoverable.".
- golang/glog glog.go, `Exit` (fetched): "Exit ... then calls os.Exit(1)."; golang/go src/os/proc.go, `Exit` (fetched): "Conventionally, code zero indicates success, non-zero an error."; openjdk/jdk java/lang/System.java, `exit` (fetched): "By convention, a nonzero status code indicates abnormal termination."
- Caveat: the measurements come from injecting errors into one commercial storage system and six open-source server applications; the propagation to the entry point and the exit come from documentation of program initialization.
