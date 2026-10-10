---
title: A change adds a configuration option only for a value the people deploying or running the program need to choose, leaving implementation details and values the program can obtain itself to the code
rule_id: TOOL-24
domain: tooling
step: [design]
applies_to: [universal]
triggers: ['\bflag[.]\w+\s*\(\s*["'']', '\badd_argument\s*\(\s*["'']-', '[.]option\s*\(\s*["'']-', '#\[(?:arg|clap)\(', '@Value\s*\(\s*["'']\$\{|@ConfigurationProperties\b', '\b(?:os[.](?:Getenv|LookupEnv|getenv)|os[.]environ[.]get|System[.](?:getenv|getProperty)|env::var)\s*\(\s*["'']', '\bprocess[.]env\b|\bos[.]environ\[']
scope: callers
check_kind: semantic
severity_default: minor
---

# A change adds a configuration option only for a value the people deploying or running the program need to choose, leaving implementation details and values the program can obtain itself to the code

## Thesis
Each flag, environment variable or configuration key that a change exposes to the program's users and administrators carries a setting with explicit semantics or visible external impact that users need to set. A parameter specific to the internal implementation, one most users do not need, or one users find hard to set correctly stays out of their configuration, and a value the program can obtain from information about the running instance can be set by the program instead of by its users.

## Rationale
Configuration is exposed to users for flexibility of control, and that flexibility comes with a high cost in complexity and error proneness; when users do not or cannot use it, the cost is not worthwhile. Across the field settings of one commercial storage system and two open-source system-software projects, only 6.1%–16.7% of parameters were set by the majority of users, and up to 54.1% were rarely set by any user. Parameters with explicit semantics and visible external impact were set by more users than parameters specific to the internal implementation, and users cannot, or may not have time to, read the source code. Too many knobs come with a cost: up to 48.5% of user-reported configuration issues were difficulties in finding or setting the parameters that give the intended behaviour, and up to 53.3% of configuration errors came from users staying with default values incorrectly. For the storage system, 51.9% of the parameters could be hidden or removed and 19.7% of the remaining ones converted into simpler types, with an impact on fewer than 1% of its users. Some values can be set by the program from information about the current system instance, and even a parameter that many users set can be eliminated by inferring or generating its value from the runtime environment.

## Example
```java
bad:  int slots = Integer.parseInt(System.getenv("RING_BUFFER_SLOTS"));
      int cpus = Integer.parseInt(System.getenv("CPU_COUNT"));
good: static final int RING_SLOTS = 1024;
      int cpus = Runtime.getRuntime().availableProcessors();
```

## Limits
The rule covers configuration as the interface for the software's users, such as administrators; a setting meant for developers or support engineers is outside it, and the findings may not apply to developing, testing or debugging environments. Simplicity of configuration and flexibility of control are conflicting goals: many users need knobs to customize and fine-tune a system, especially a performance-critical one, and simplification does not aim to prevent that tuning. A parameter that few users still set can be decoupled from the basic configuration instead of removed, hidden from common users and introduced in separate manuals, templates and files, with arbitrary values still accepted when a user insists. The 1.8%–7.8% of parameters configured by more than 90% of users, many of which supply necessary runtime information that is hard to default in advance, are the ones to expose or recommend to users as first-class options. A value that needs information from outside the system, such as the connection details of a backup service, is hard for the program to determine itself, and a critical setting that may permanently change system state or user data is not one for the program to decide automatically.

## Validator
Grep the hunk for a new flag definition, argument-parser option, configuration-key binding, system-property read or environment-variable read. Open the callers of the value it yields and trace what the value controls: an endpoint, a path, a limit, a feature switch or another effect users can observe, or a mechanism inside the implementation such as a buffer, slot or table size. Check whether the program can obtain the value from the running instance, such as the processor count or the file system's block size, without information from outside the system and without deciding by itself a critical setting that may permanently change system state or user data. Leave alone an option documented for developers, testers or support engineers, an advanced option kept apart from the basic configuration, and a tuning option for a performance-critical path that the change documents for its users. Validator question: **Does the change expose to the program's users a new option whose value controls only an internal implementation detail with no visible external effect, or one the program can obtain from its own running instance under those two conditions?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: TOOL-24`, severity minor, `file`, `symbol`, `code` = the line that defines or reads the new option, `fix` = the value set in code as a named constant or, when the Validator's two conditions hold, obtained from the running instance, in the file's language, `rationale` = what the option controls inside the implementation and why users cannot judge it or the program can obtain it itself).
