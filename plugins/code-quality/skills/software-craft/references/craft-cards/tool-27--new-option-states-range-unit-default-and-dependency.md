---
title: A configuration option a change adds states its allowed values or range, its unit, its default and any option it depends on, in its help text, the configuration documentation, its error or log message or its name
rule_id: TOOL-27
domain: tooling
step: [document, implement, review]
applies_to: [universal]
triggers: ['\bflag[.](?:Bool|Int|Int64|Uint|Uint64|String|Float64|Duration|Func|BoolFunc|TextVar)(?:Var)?\s*\(', '\badd_argument\s*\(', '[.]option\s*\(\s*["'']-', '#\[(?:arg|clap)\(', '@Value\s*\(\s*["'']\$\{|@ConfigurationProperties\b', '\bos[.](?:Getenv|LookupEnv|getenv)\s*\(|\bos[.]environ\b|\bprocess[.]env\b|\benv::var(?:_os)?\s*\(|\bSystem[.]getenv\s*\(']
scope: file
check_kind: semantic
severity_default: suggestion
---

# A configuration option a change adds states its allowed values or range, its unit, its default and any option it depends on, in its help text, the configuration documentation, its error or log message or its name

## Thesis
Each configuration option a change adds states its constraints in at least one form its users see: its help text, the configuration documentation, the error message for a rejected value or the log message for an ignored one, or an accurate name. The constraints stated are its allowed values or range, its unit when it holds a quantity, its default, and any other option whose setting decides whether it takes effect. Options of one kind keep one case-sensitivity convention for their values, and one unit granularity unless each states its unit in its name or in a required value suffix.

## Rationale
Some configuration constraints have never been documented in any form, and users can easily make mistakes with them. Documenting range constraints explicitly is good practice, but this is not always the case: one open-source system limits index lengths within [4, 255] and does not document the constraint, and if users set out-of-range values, the system misbehaves silently, leaving users suspecting a bug. When the use of one option relies on the setting of another and that dependency is neither documented in the manual nor pinpointed by log messages, it is difficult for users to figure it out; their question is why their setting of the first option does not work. One commercial storage system exposes the unit in the name (cleanup.msec, takeover.sec), which serves as both constraint description and mnemonic, and requires unit suffixes in some values to help users express their intention explicitly. Inconsistent case sensitivity or unit granularity across parameters of the same type is error-prone, because users are likely confused by the contradictory requirements. Standard command-line libraries can print each flag's default in the usage message beside its help string, by default or when configured to, so a declared default reaches users through the help text.

## Example
```go
bad:  limit := flag.Int("max-body", 512, "")
      level := flag.Int("level", 3, "")
good: limit := flag.Int("max-body-kib", 512,
          "largest accepted request body in KiB, 1 to 10240; used only when -uploads is set")
      level := flag.Int("level", 3, "compression level, 1 (fastest) to 9 (smallest)")
```

## Limits
One documented form satisfies the rule: a constraint stated in the configuration documentation, in the error message for a rejected value or the log message for an ignored one, or by an accurate name needs no repetition in the help text. The finder reads the changed file alone and cannot open a configuration reference kept in another file: it flags an option whose constraints that file states nowhere, and the developer answers such a finding by naming the reference that states them. A quantity whose value must carry its unit suffix, as a duration written 500ms must, states its unit in the value. A default the library prints with the usage message counts as stated; a library that omits the default when it equals the type's zero value leaves a meaningful zero default to the help text. The rule asks that each constraint be stated; whether the program also rejects an out-of-range value at load, which value an option defaults to, and how a configuration language is parsed lie outside it.

## Validator
Grep the hunk for a new flag, command-line argument, environment-variable read or configuration-property declaration. For each new option, read its name, its help string, the error message raised for a bad value or logged for an ignored one, and any configuration documentation the hunk adds. Trace the value through the hunk to the range check, the set of accepted values, the unit conversion, or the condition on another option that gates its use, and compare a new quantity's unit granularity, and whether a new option matches its values case-sensitively, with the existing options of the same kind in the file. Validator question: **Does the hunk add an option whose enforced range or allowed values, unit, default or gating option is stated in none of its help text, configuration documentation, error or log message or name, or whose values' case sensitivity differs from existing options of the same kind, or whose unit granularity differs from theirs while neither its name nor a required value suffix states its unit?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: TOOL-27`, severity suggestion, `file`, `symbol`, `code` = the option's declaration line verbatim from the diff, `fix` = the declaration with a name, help text or error message that states the range or allowed values, the unit, the default and the gating option, or the option's value comparison changed to the case convention of the existing options of its kind, in the file's language, `rationale` = which constraint the code enforces or implies and that no user-facing form in the file states, or which case-sensitivity or unit convention of the existing options of its kind the option breaks).

## Source
- SOSP 2013, DOI 10.1145/2517349.2522727, §3.2 'Undocumented Constraints' (fetched): "check whether the constraints are documented in any form (e.g., user manuals, error messages, or even accurate parameter naming). Our evaluation shows that some configuration constraints have never been documented in any form. As the consequence, users can easily make mistakes with them."
- Same paper, §2.2.3 Data Range Inference (fetched): "As a good practice, range constraints should be explicitly documented, but this is not always the case. ... OpenLDAP limits index lengths within [4, 255]. However, this constraint is not documented. If users set out-of-range values, the system misbehaves silently, leaving users suspecting it as a bug."
- Same paper, §2.1 Control Dependency (fetched): "the usage of parameter Q relies on the setting of parameter P" / "the resolution to problems like, “Why does my setting of parameter A not work?” is simply, “Turn on parameter B.” When such dependencies are neither documented in the manual, nor pinpointed explicitly by log messages, it is difficult for users to figure them out."
- Same paper, §3.2 Design Inconsistency and §5.2 Handling Inconsistency (fetched): "two types of configuration inconsistency: (1) case sensitivity, and (2) unit granularity. Such inconsistency is error-prone because users are likely confused by the contradictory requirements for parameters of same types." / "We observe two efforts in Storage-A in handling unit inconsistency. First, the unit information is exposed in naming (e.g., “cleanup.msec”, “takeover.sec”) which serves as both constraint descriptions and mnemonics for users. Second, some parameter settings enforce users to specify unit suffixes to help them express their intention explicitly."
- Go package flag, func PrintDefaults (fetched): "a usage message showing the default settings of all defined command-line flags ... The parenthetical default is omitted if the default is the zero value for the type."
- Python argparse, formatter_class (fetched): "ArgumentDefaultsHelpFormatter automatically adds information about default values to each of the argument help messages"
- Caveat: the paper evaluates "one commercial system and six open-source systems", the commercial one a storage system. Its Table 8 counts undocumented data-range, control-dependency and value-relationship constraints per system, and §4.1 qualifies them and the unit inconsistencies of Table 7: "it might be arguable whether the cases in Table 7 and 8 are really confusing and error-prone to users. To be conservative, we did not report them to the developers." The mistake rate an undocumented constraint or a unit inconsistency causes is not measured.
