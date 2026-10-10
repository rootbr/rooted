---
title: A setting the program accepts but does not apply, an unrecognised key or option or one that has no effect while another option disables it, is reported with a warning or an error naming it or its place in the file, never dropped silently
rule_id: TOOL-31
domain: tooling
step: [implement, handle-errors, review]
applies_to: [universal]
triggers: ['(?i)\bstrict\s*:\s*false\b|\bparse_known_args\s*\(|\b(?:ignore|allow|disallow|deny|fail_?on)_?unknown\w*|\bunknown_?(?:fields|keys|properties|args|options)\b|\bextra(?:\s*=\s*["'']?|[.])(?:ignore|allow)\b']
scope: file
check_kind: semantic
severity_default: minor
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
When the validator answers yes, the finder emits one finding (`rule_id: TOOL-31`, severity minor, `file`, `symbol`, `code` = the lenient parse call or the conditional read of the dependent setting, quoted verbatim from the diff, `fix` = the strict parse, or the warning that names the setting left without effect and the setting that disables it, in the file's language, `rationale` = names the setting that is accepted and dropped silently and the path by which it is dropped).

## Source
- DOI 10.1145/2517349.2522727 (SOSP 2013, 'Do Not Blame Users for Misconfigurations'), Table 3 and the paragraph introducing it, §4 and §4.1 (fetched): "one commercial system and six open-source systems"; "the system should pinpoint either the misconfigured parameter's name/value or its location information"; "Silent violation — The system changes input configurations to different values without notifying users"; "Silent ignorance — The system ignores input configurations (mainly for control-dependency violation)"; "Early termination — The system exits without pinpointing the injected configuration error"; "silent violation and ignorance are more prevalent compared with terminations and failures"; Figure 5(e): "commit_siblings silently takes no effect".
- DOI 10.1145/3485517 (Proc. ACM Program. Lang. 5, OOPSLA, Article 140, 2021), abstract and §2 (fetched): "although some parameters are set in the configuration file, they do not influence the system runtime behavior, thus failing to meet the user's intent. Moreover, such misconfigurations rarely lead to an error message or raising an exception"; "prohibitively hard to identify due to (1) lack of feedback"; "Table 1 lists 27 real-world silent misconfigurations reported by Apache users"; "The majority (74.0%) of silent misconfigurations are caused by interactions between multiple configuration parameters and their values"; "All these 19 cases have the same root cause"; "the effect of one configuration was either disabled by other configurations or overwritten by the code affected by other configurations"; "Most (70.4%) silent misconfigurations happen without any system messages or logs"; "for 19 out of 27 (70.4%) of the cases, there was no feedback".
- Python documentation, argparse, 'Invalid arguments', `parse_known_args`, `deprecated` (fetched): "When it encounters such an error, it exits and prints the error along with a usage message"; "PROG: error: unrecognized arguments: --bar"; "leaving any unrecognized arguments for another script or program"; "returns a two item tuple that contains the populated namespace and the list of any unrecognized arguments"; "Before removing them, you should inform your users that the arguments are deprecated and will be removed"; "if deprecated is True, then a warning will be printed to sys.stderr when the argument is used".
- Node.js API documentation, `util.parseArgs` `config.strict` (fetched): "Should an error be thrown when unknown arguments are encountered ... Default: true".
- Go standard library, package flag, `ExitOnError` and `FlagSet.parseOne` (fetched): "CommandLine = NewFlagSet(os.Args[0], ExitOnError)"; "flag provided but not defined: -%s".
- Compose Specification (compose-spec/compose-spec main: spec.md 'Version top-level element (obsolete)', 01-status.md, 11-extension.md 'Extension') (fetched): "Compose validates whether it can fully parse the Compose file. If some fields are unknown, typically because the Compose file was written with fields defined by a newer version of the Specification, you'll receive a warning message. Compose offers options to ignore unknown fields"; "Default: warn the user about unsupported attributes, but ignore them"; "Loose: ignore unsupported attributes AND unknown attributes"; "Compose ignores any fields that start with `x-`, this is the sole exception where Compose silently ignores unrecognized fields".
- Caveat: the failure measurements cover one commercial and six open-source systems and user reports on Apache, vsftpd and PostgreSQL; neither study injects or counts unknown keys, so the unrecognised-name case rests on the command-line parsers' defaults and on one configuration-file specification.
