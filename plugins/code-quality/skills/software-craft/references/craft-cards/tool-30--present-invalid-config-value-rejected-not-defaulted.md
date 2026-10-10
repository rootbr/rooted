---
title: A configuration value that is present but malformed or outside its allowed values is rejected with an error, never converted by a lenient parser or silently replaced by the default meant for an absent setting
rule_id: TOOL-30
domain: tooling
step: [implement, handle-errors, review]
applies_to: [universal]
triggers: ['\b(?:bool|Boolean)\s*\(\s*(?:os[.](?:environ|getenv)|process[.]env|config|cfg|settings|env)\b|\bBoolean[.](?:parseBoolean|getBoolean)\s*\(|\b(?:parseInt|parseFloat|atoi|atol|atof|sscanf)\s*\(|\bstrconv[.](?:Atoi|Parse(?:Bool|Int|Uint|Float))\s*\(|(?:[Gg]etenv|environ|process[.]env|getProperty)\b.*(?:[!=]==?|[.]equals(?:IgnoreCase)?\s*\()\s*[\x22\x27]|[\x22\x27][.]equals(?:IgnoreCase)?\s*\(\s*\w+[.](?:getenv|getProperty)\b', '\bexcept\s*\(?\s*(?:ValueError|TypeError|KeyError)\b|\bcatch\s*\(\s*(?:NumberFormatException|IllegalArgumentException)\b|[.]parse(?:::<[^>]+>)?\s*\(\s*\)\s*[.](?:unwrap_or|unwrap_or_default|unwrap_or_else|ok)\s*\(|(?:getenv|environ|process[.]env|env::var|getProperty)\b.*(?:\|\||\?\?|\bor\b|unwrap_or|getOrDefault)']
scope: hunk
check_kind: semantic
severity_default: major
---

# A configuration value that is present but malformed or outside its allowed values is rejected with an error, never converted by a lenient parser or silently replaced by the default meant for an absent setting

## Thesis
A value the user set for a configuration option, through the environment, a flag or a configuration file, is converted by a parser that reports unexpected characters, overflow and unrecognised words, and a value the parser or a check of its allowed values rejects reaches the user as an error. The default stands in for a setting that is absent; a value the user gave is not changed into the default without notifying the user. Where an empty value and an unset one must be told apart, the loader reads the setting with a lookup that distinguishes them.

## Rationale
Silent overruling changes an unacceptable user setting into the default value without notifying the user, and it may cause silent violation of the user's intention: a parser that treats a boolean as off whenever it is not set to "on" turns "yes" and "enable" into off, so the system's behaviour does not match what the user expects. Analysis of two open-source servers found silent overruling cases affecting 74 parameters, all fixed by their developers once reported. Lenient conversion functions in configuration handling can also create confusing behaviour. atoi gives no way to check unexpected characters ("1O0" becomes 1) or overflow. The global parseInt function may interpret only a leading portion of the string and gives no indication that the rest was ignored, while a parseInt that throws on a string without a parsable integer is a checked conversion. parseBoolean returns false for "yes". The truth value of the string "False" is true. More than half of the evaluated systems used such unsafe conversions for large numbers of parameters, though the authors judge it arguable whether those cases really confuse users and did not report them to developers. User settings may not be trustworthy and can easily be misspelled: in 546 real-world misconfigurations, 70.0% to 85.5% were mistakes in setting configuration parameters, and many configuration issues show up as crashes, hangs and silent failures that leave users clueless. Some environment lookups return an empty value when the variable is not present, and a separate lookup distinguishes an empty value from an unset one.

## Example
```python
bad:  verbose = bool(settings.get("app", "verbose", fallback=""))
      try:
          port = int(os.environ["PORT"])
      except (KeyError, ValueError):
          port = 8080
good: verbose = settings.getboolean("app", "verbose", fallback=False)
      raw = os.environ.get("PORT")
      port = 8080 if raw is None else int(raw)
```

## Limits
A default assigned before the user settings are read, which any user setting overwrites, is static initialization and not overruling. Silent overruling is defined by the missing notification: a loader that reports the refused value to the user and then continues on the default is outside it. A lenient conversion is handy in a controlled context, on a value that does not come from user settings, and the rule does not reach it.

## Validator
Grep the hunk for conversions of a value read from the environment, a flag or a configuration file: unchecked or prefix-accepting numeric conversions (atoi, atol, sscanf, and the global parseInt and parseFloat functions, not a parseInt that throws on malformed input), boolean conversions that compare against one word or take the string's truth value, a parse result folded into a default (unwrap_or, getOrDefault, or, ||, ??), handlers that catch a conversion error, and an else block or default case that overwrites the setting with the default when it is outside its allowed values. Open the hunk and trace each such value from where it is read to where it is used. For each fallback, check whether it fires only when the setting is absent or also when the setting is present and rejected, and whether the rejection reaches the user. Validator question: **Does a value the user set for a configuration option pass through a conversion that accepts unexpected characters, overflow or unrecognised words, or get replaced by the default after it fails to parse or falls outside its allowed values, without the user being notified?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: TOOL-30`, severity major, `file`, `symbol`, `code` = the line that converts the setting or assigns the default after a failed conversion or range check, `fix` = a checked conversion whose failure reaches the user and a default applied when the setting is absent, in the file's language, `rationale` = names the setting, the malformed input the code would accept or replace, and the value the program would run with instead).

## Source
- DOI 10.1145/2517349.2522727, §3.2 Silent Overruling and Unsafe APIs, §4 (fetched): "the system changes an unacceptable user setting into the default value without notifying the user. It may cause silent violation of user intention"; "Squid silently treats any boolean parameter as “off” as long as it is not set to “on”, even if its value is “yes” or “enable”. Such design can easily confuse users because the system behavior would not match their expectation."; "Using unsafe APIs in configuration handling can also create confusing behavior."; "We do not consider static initialization of configuration parameters as silent overruling. It is mainly used to assign default values that would be overwritten by user settings."; "there is no way to check unexpected characters [atoi(1O0) returns 1] and overflow issues"; "a good practice is to use safe APIs such as strtol and check errors through errno and end pointers"; "These APIs are handy in controlled contexts but should be avoided in configuration parsing since user inputs may not be trustworthy and can easily be misspelled"; "To detect silent overruling, for enumerative range constraints inferred in “if...else if...else” or switch logics, if the parameter is silently overwritten in the else block or default case, we flag it as silent overruling."; "In Squid and Apache, we detect many silent overruling cases that affected 74 parameters. All of these have been fixed by developers after we reported them."; "more than half of the systems use unsafe transformation APIs for large numbers of parameters"; "it might be arguable whether the cases in Table 7 and 8 are really confusing and error-prone to users. To be conservative, we did not report them to the developers."; abstract: "Many configuration issues manifest themselves in ways similar to software bugs such as crashes, hangs, silent failures. It leaves users clueless".
- ECMA-262, parseInt(string, radix), note (fetched): "This function may interpret only a leading portion of _string_ as an integer value; it ignores any code units that cannot be interpreted as part of the notation of an integer, and no indication is given that any such code units were ignored."
- OpenJDK 21, java.lang.Boolean#parseBoolean Javadoc (fetched): "Example: {@code Boolean.parseBoolean("yes")} returns {@code false}."
- OpenJDK 21, java.lang.Integer#parseInt Javadoc (fetched): "@throws NumberFormatException if the {@code String} does not contain a parsable {@code int}."
- Python documentation, configparser, Supported Datatypes and getboolean (fetched): "simply passing the value to bool() would do no good since bool('False') is still True"; "Any other value will cause it to raise ValueError."
- Go os package, Getenv doc comment (fetched): "It returns the value, which will be empty if the variable is not present. To distinguish between an empty value and an unset value, use [LookupEnv]."
- SOSP 2011, "An empirical study on configuration errors in commercial and open source systems", http://www.sigops.org/sosp/sosp11/current/2011-Cascais/printable/12-yin.pdf (relayed): "546 real-world misconfigurations ... 70.0%–85.5% are mistakes in setting configuration parameters".
- Caveat: the overruling and unsafe-conversion counts come from one commercial storage system and six open-source servers; the conversion behaviours come from each function's own documentation.
