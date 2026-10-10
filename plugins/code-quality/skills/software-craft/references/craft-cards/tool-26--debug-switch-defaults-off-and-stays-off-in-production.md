---
title: A debug mode or other switch that exposes debugging features defaults to off, and a change does not turn it on unconditionally in code or in configuration that the production deployment reads
rule_id: TOOL-26
domain: tooling
step: [implement, review]
applies_to: [universal]
triggers: ['(?i)\b\w*debug\w*["''\]]*\s*[:=,]\s*(?:true\b|1\b|["''](?:1|on|yes|true)["''])', '(?i)\b(?:set|enable|with)?_?debug\w*\s*\(\s*(?:true|1)\s*\)']
scope: file
check_kind: mechanical
severity_default: minor
---

# A debug mode or other switch that exposes debugging features defaults to off, and a change does not turn it on unconditionally in code or in configuration that the production deployment reads

## Thesis
A debug mode, and any other switch that enables debugging features (stack trace printing, verbose logging, detailed error pages, profiling APIs or a remote debugging endpoint), is disabled for every component in production environments. Its value in code and in the default configuration file is off, and it is turned on only through the environment, by the configuration of a non-production deployment, or behind an environment check that leaves it off in production. A change that sets such a switch on unconditionally in code, or in a configuration file the production deployment reads, releases the product with debugging code still enabled.

## Rationale
Debug instructions and error messages can leak detailed information about the system, such as the application's path, file names, stack traces and configuration data, which an attacker can use to craft further attacks; debug features may also expose remote debugging endpoints, profiling APIs or detailed error pages that significantly increase the attack surface. Adding code designed for debugging or testing is a common development practice; that code is not intended to be shipped or deployed with the product, and such entry points create security risks because they are not considered during design or testing and fall outside the expected operating conditions of the product. Tool rules flag a debug switch hard-coded on in code or in a framework's default configuration file, and direct that it be disabled, set through an environment variable, or guarded by an environment check before deploying to production. The detecting rule rates the defect minor, with low security impact, and the verification standard lists the requirement at its Level 2.

## Example
```typescript
bad:  const server = createServer({ debug: true });
      server.setDebug(true);
good: // off unless the deployment sets APP_DEBUG
      const server = createServer({ debug: process.env.APP_DEBUG === "true" });
```

## Limits
The requirement covers production environments: a configuration file read only by a development, test or local deployment may turn the switch on, and so may a value guarded by an environment check that keeps it off in production. Test code that turns the switch on for itself is outside the rule, since the detecting tool rule scopes itself to main code. A switch read from the environment at run time complies when the production deployment leaves it off. The rule governs the switch's value, not what the debugging code prints: inserting sensitive information into debugging code is a separate weakness.

## Validator
Grep the hunk for a debug-named key, field, variable or setter given true, 1, "on", "yes" or "true", and for a switch that turns on stack trace printing, verbose logging, detailed error pages, a profiling API or a remote debugging endpoint. Open the file and stop when it is test code, or a configuration file whose name or directory ties it to a development, test or local deployment; a configuration file whose name and directory tie it to no deployment is the default configuration file, which the production deployment reads. Trace the value and stop when it is read from the environment or a flag and is off when unset, or sits behind an environment check that is false in production. Validator question: **Does the hunk set a debugging switch on unconditionally in code, or in a configuration file that the production deployment reads?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: TOOL-26`, severity minor, `file`, `symbol`, `code` = the line that sets the switch on, quoted verbatim from the diff, `fix` = the switch read from the environment or a flag with off as its value when unset, in the file's language, `rationale` = the debugging feature the switch exposes in production and the information it can leak).

## Source
- OWASP ASVS 5.0, V13.4.2 (Level 2), raw.githubusercontent.com/OWASP/ASVS/master/5.0/en/0x22-V13-Configuration.md: "Verify that debug modes are disabled for all components in production environments to prevent exposure of debugging features and information leakage." (fetched)
- CWE-489 'Active Debug Code', cwe.mitre.org/data/definitions/489.html: "The product is released with debugging code still enabled or active."; "A common development practice is to add "back door" code specifically designed for debugging or testing purposes that is not intended to be shipped or deployed with the product. These back door entry points create security risks because they are not considered during design or testing and fall outside of the expected operating conditions of the product."; related weakness "Insertion of Sensitive Information Into Debugging Code" (fetched)
- RSPEC-4507 'Debugging features should not be enabled in production', sonar-python S4507.html and S4507.json (VULNERABILITY, defaultSeverity Minor, impacts SECURITY LOW, scope Main): "Debug features should be disabled or guarded by environment checks before deploying to production."; "Debug instructions or error messages can leak detailed information about the system, such as the application’s path, file names, or stack traces."; "Attackers can exploit debug output to learn internal application details, file paths, stack traces, and configuration data that can be leveraged to craft further attacks."; "Debug features may expose remote debugging endpoints, profiling APIs, or detailed error pages that significantly increase the attack surface of the application."; "The rule flags configurations and API calls that enable debug features, including stack trace printing, verbose logging, debug mode flags, and remote debugging endpoints."; in "the default configuration files": "DEBUG = True  # Noncompliant" (fetched)
- Semgrep avoid_hardcoded_config_DEBUG, semgrep-rules python/flask/security/audit/hardcoded-config.yaml (CWE-489; likelihood LOW, impact LOW, confidence LOW): "Hardcoded variable `DEBUG` detected. Set this by using FLASK_DEBUG environment variable"; its patterns flag DEBUG hard-coded to False as well as to True, so it supports setting the switch through the environment, not an off value fixed in code (fetched)
- Caveat: the two tool rules draw their examples from Python web frameworks; the standard and the weakness entry state the rule for every component and every product.
