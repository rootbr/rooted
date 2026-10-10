---
title: A setting the program accepts but does not apply, an unrecognised key or option or one that has no effect while another option disables it, is reported with a warning or an error naming it or its place in the file, never dropped silently
rule_id: TOOL-31
domain: tooling
step: [implement, handle-errors]
applies_to: [universal]
triggers: ['(?i)\bstrict\s*:\s*false\b|\bparse_known_args\s*\(|\b(?:ignore|allow|disallow|deny|fail_?on)_?unknown\w*|\bunknown_?(?:fields|keys|properties|args|options)\b|\bextra(?:\s*=\s*["'']?|[.])(?:ignore|allow)\b']
scope: file
check_kind: semantic
severity_default: major
---

# A setting the program accepts but does not apply, an unrecognised key or option or one that has no effect while another option disables it, is reported with a warning or an error naming it or its place in the file, never dropped silently

## Thesis
A configuration setting the program receives but does not apply produces a warning or an error that names it or gives its place in the configuration file. This covers a key or option, on the command line or in a configuration file, that matches no setting of that name, and a setting that is set while the value of another setting leaves it without effect.

## Rationale
Parameters set in a configuration file that do not influence the runtime behaviour fail the user's intent, and such misconfigurations rarely lead to an error message or an exception; they are hard to identify for lack of feedback. In a study of 27 silent misconfigurations reported by the users of one web server, most were caused by interactions between multiple configuration parameters and their values, the effect of one setting either disabled by other settings or overwritten by the code that other settings affect, and 70.4% (19 of 27) happened without any system message or log. Injecting misconfigurations into one commercial and six open-source systems found that the reaction of ignoring input configurations arose mainly for violations of a control dependency between parameters, and that silently changing or ignoring input configurations was more prevalent than terminations and failures. An exit that does not pinpoint the erroneous setting, by its name or value or by its place in the file, was counted among the bad reactions too. The standard-library argument parsers of three languages reject an unrecognised option by default: one exits with an error naming the unrecognised argument, one throws on unknown arguments, and one fails with a message naming the undefined flag. One open specification of a configuration file format has its implementation warn when fields in the file are unknown, typically because the file was written for a newer version of the format, and by default warn the user about attributes it does not support while ignoring them.

## Example
```typescript
bad:  const { values } = parseArgs({ options, strict: false });
      if (values.cache) enableCache(values.ttl);
good: const { values } = parseArgs({ options });
      if (values.ttl !== undefined && !values.cache)
        console.warn("--ttl has no effect without --cache");
      if (values.cache) enableCache(values.ttl);
```

## Limits
A parse that handles only part of the arguments and leaves the unrecognised ones for another script or program meets the rule when it returns the list of unrecognised arguments to the caller that hands them on. An argument on its way out of the program may stay accepted while a warning, printed whenever it is used, tells users it is deprecated and will be removed. A key under a prefix that the configuration format reserves for extensions may be skipped without a report, and so may an unknown key while a lenient mode that the user turns on as an option is in force.

## Validator
Grep the hunk for a parse that tolerates unknown input: a strict switch turned off, a known-arguments parse, an ignore-unknown or allow-extra option on a configuration decoder, or a decoder that drops unknown fields by default. Open the file at the configuration loader and list the settings it reads; trace where the leftover keys or arguments go, to an error, a warning, a hand-off to another program or nowhere. Trace each setting that is read only under a condition on another setting, and check whether setting it while that condition disables it produces a warning naming it. Validator question: **Does the file accept a configuration key, option or setting that it neither applies, nor reports in a warning or an error that names it or gives its place in the file, nor hands on to another program, other than a key under a prefix the format reserves for extensions or an unknown key while a lenient mode the user turned on is in force?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: TOOL-31`, severity major, `file`, `symbol`, `code` = the lenient parse call or the conditional read of the dependent setting, quoted verbatim from the diff, `fix` = the strict parse, or the warning that names the setting left without effect and the setting that disables it, in the file's language, `rationale` = names the setting that is accepted and dropped silently and the path by which it is dropped).
