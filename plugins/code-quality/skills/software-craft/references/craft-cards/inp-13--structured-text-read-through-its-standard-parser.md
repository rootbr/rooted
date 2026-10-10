---
title: Text in a structured format such as JSON, CSV, XML, HTML, a URL or a date is read, and its parts are checked, through the language's standard or established parser for that format, never by splitting, substring tests or a regular expression over the raw text
rule_id: INP-13
domain: input
step: [implement]
applies_to: [universal]
triggers: ['([.](split|split_once)\(\s*|strings[.](Split|SplitN|Cut)\(\s*\w+\s*,\s*)["\x27]([,;|&=@?]|\\t)["\x27]|(\bre[.]\w+|RegExp|Pattern[.]compile|\bregexp[.]\w+|Regex::new|replaceAll|matches)\(.*(</?(\w+|!--)|<\[\^>\]|<[.][*+]|https\?:|\\d\{4\})|(^|[=(,:!&|?;]\s*)/\^?(https\?:|\\d\{4\}|<\[\^>\]|<[.][*+]|</?\w|<!--)', '(startswith|startsWith|endswith|endsWith|HasPrefix|HasSuffix|starts_with|ends_with|includes|contains|Contains|indexOf)\(\s*(\w+\s*,\s*)?["\x27](https?:|//|[.]\w|[\w-]+([.][\w-]+)*[.][a-z]{2,}["\x27])|["\x27](https?://[^"\x27]*|[\w-]+([.][\w-]+)*[.][a-z]{2,}(/[^"\x27]*)?)["\x27]\s+(not\s+)?in\s+\w']
scope: file
check_kind: semantic
severity_default: major
---

# Text in a structured format such as JSON, CSV, XML, HTML, a URL or a date is read, and its parts are checked, through the language's standard or established parser for that format, never by splitting, substring tests or a regular expression over the raw text

## Thesis
A value in a defined format — JSON, CSV, XML or HTML, a URL, a date, a query or configuration language — is read with a maintained parser for that format: the language's standard one or an established library for that format. A check on one of the value's parts, such as a URL's host, is made on the parsed component. That parse takes the place of splitting the raw text on a delimiter, testing it for a substring, including a prefix or suffix, or matching it with a regular expression, whether to read the format or to check one of its parts. A regular expression stays the tool for a simple, structured field that has no standard or established parser of its own, and it matches the entire value.

## Rationale
A substring or suffix test on the raw URL can be bypassed by a URL that embeds the allowed host in an unexpected location: a substring test for `example.com` passes `http://evil-example.net/example.com`, where the allowed host sits in the path rather than the host. Outside a security-critical context, a check that succeeds accidentally may still cause undesirable behaviour. General HTML cannot be parsed with regular expressions; a pattern that matches single tags but is not written well may be circumvented, which can lead to cross-site scripting or other security issues. HTML and XML have special cases that break the obvious pattern, and a pattern that handles all of them becomes very complicated, while a well-tested parser library is much more likely to handle those corner cases correctly than a custom implementation. CSV has no well-defined standard, so the data different programs write often differs in subtle ways, delimiters and quoting characters among them; a module for the format hides those details from the code that reads it. A parse whose failures are handled yields values that the code then validates before business processing or storage; converting text to an integer establishes only a type, not an acceptable quantity. A date's rules are its expected type, accepted format, and minimum and maximum values, unlike a string's characters or structure, and a pattern over the raw text checks the format but yields no date value whose range can be checked.

## Example
```go
bad:  base, _, _ := strings.Cut(raw, "?")
      if strings.HasSuffix(base, "example.com") {
          redirect(raw)
      }
good: u, err := url.Parse(raw)
      if err == nil && u.Hostname() == "example.com" {
          redirect(u.String())
      }
```

## Limits
A regular expression that matches the entire value of a simple, structured field that has no standard or established parser of its own, unlike a date or a URL, is the recommended tool for that field, with the input's length bounded before matching and patterns with excessive backtracking avoided. A plain delimiter-separated list with no quoting is split. A parser library is called for where at all possible: a format the program itself defines has none, and a dedicated parser written for that format is outside the rule. Deciding which parsed values are acceptable, such as the set of allowed hosts and a host comparison that handles arbitrary subdomain sequences correctly, configuring the parser for untrusted input (external entities, deserialization, size and nesting limits), and sanitizing user-authored HTML are separate controls the rule does not reach.

## Validator
Grep the hunk for a split on a delimiter, a substring, prefix or suffix test against a literal that holds a scheme, host or path, and a regular expression whose pattern holds markup tags, field separators, URL parts or a date's digit groups. Open the file and trace the text being split, tested or matched back to where it enters: a request, a file, a message, a configuration value or another program's output. Name the format the text is in and the standard or established parser that reads it; then check whether the code reads that format's parts, or decides on one of them, from the raw text rather than from the parsed value. Pass a whole-value match of a simple, structured field that has no standard or established parser of its own and a split of a plain delimiter list with no quoting. Validator question: **Does the code read text in a format that has a standard or established parser, or check one of that text's parts, by splitting, a substring, prefix or suffix test, or a regular expression over the raw text rather than through that parser?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: INP-13`, severity major, `file`, `symbol`, `code` = the split, substring, prefix or suffix test, or regular-expression call over the raw text, `fix` = the same value read through the format's standard or established parser with its error handled and the check made on the parsed component, in the file's language, `rationale` = the format, the parser that reads it, and the input that the raw-text handling misreads or lets through).
