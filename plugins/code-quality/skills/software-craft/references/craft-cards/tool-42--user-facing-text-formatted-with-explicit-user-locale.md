---
title: Numbers, dates and lists of text shown to a user are formatted, case-mapped and sorted by a locale-sensitive operation given the user's locale explicitly, never by code-point order, a format fixed regardless of locale or the host's default locale taken implicitly
rule_id: TOOL-42
domain: tooling
step: [implement]
applies_to: [universal]
triggers: ['\b(sort[.]Strings|slices[.]Sort)\(|\bsorted\(\s*\w*(name|title|label|city|countr)\w*|[.]sort\(\s*\)|\bnew\s+Intl[.]Collator\(\s*\)|\bCollator[.]getInstance\(\s*\)', '\bstrings[.]To(Upper|Lower|Title)\(|[.](toLowerCase|toUpperCase|to_lowercase|to_uppercase|lower|upper|toLocaleLowerCase|toLocaleUpperCase)\(\s*\)', '%[-+ #0-9]*[.][0-9]+[fFeEgG]|\{[^{}]*:[^{}]*[.][0-9]+[fFeEgG%]?\}|[.]toLocale(String|DateString|TimeString)\(\s*\)|\bnew\s+Intl[.](NumberFormat|DateTimeFormat|PluralRules|RelativeTimeFormat)\(\s*\)|\b(NumberFormat|DateFormat)[.](getInstance|getDateInstance|getDateTimeInstance|getCurrencyInstance|getPercentInstance)\(\s*\)|\bDateTimeFormatter[.]ofLocalized\w*\(|(?i:[''"](MM/dd/yy(yy)?|dd/MM/yy(yy)?|%m/%d/%[yY]|%d/%m/%[yY])[''"])|[''"](01/02/(06|2006)|02/01/(06|2006))[''"]|\bLocale[.](getDefault|setDefault)\(|\bsetlocale\(']
scope: hunk
check_kind: semantic
severity_default: minor
---

# Numbers, dates and lists of text shown to a user are formatted, case-mapped and sorted by a locale-sensitive operation given the user's locale explicitly, never by code-point order, a format fixed regardless of locale or the host's default locale taken implicitly

## Thesis
Each number, date or time, case-mapped string and sorted list of strings that code produces for display to a user comes from a locale-sensitive operation (a formatter, a case mapping or a collator) that receives the user's locale as an argument. Formatting for display follows that locale's conventions rather than a pattern that fixes the field order, separators or digit grouping regardless of locale, and sorting for display follows that locale's collation rather than an ordinal comparison of character codes. Where regionalisation by the host's default locale is what the code wants, the call passes that default, retrieved by name, as the argument. Library code hands the locale to the operation and leaves the process-wide locale setting alone.

## Rationale
Users of different languages might have very different expectations of what a sorted list looks like: alphabetical order varies from one language to another and can vary from document to document within the same language, and string comparison implementations often do not match local conventions. Case mapping is language-sensitive, so its result may differ depending on language. Dates, times and numbers displayed in a user interface should typically use the formatting conventions of the user's locale, and ordered strings displayed there should typically be sorted by that locale's conventions. When a locale-sensitive operation is called without a locale, the default it supplies might not have the effect wanted in all locales and rests on assumptions that might not be correct for the calling code. An implicit use of the runtime's default locale can make behaviour differ between executions: where a runtime's unqualified lowercase call consults the default locale, that call on a device whose user locale is Türkiye turns "I" into the dotless "ı". Even where the default behaviour would do, calling the form of the operation that takes the locale is better, because the code becomes self-documenting and more easily maintained. Setting the process-wide locale from a library routine affects the entire program as a side effect, and saving and restoring it is expensive and affects other threads that run before the setting is restored.

## Example
```go
bad:  sort.Strings(cityNames)
      heading := strings.ToUpper(title)
      label := fmt.Sprintf("%.2f", total)
good: collate.New(userLang).SortStrings(cityNames)
      heading := cases.Upper(userLang).String(title)
      label := message.NewPrinter(userLang).Sprintf("%.2f", total)
```

## Limits
A value that will be stored and accessed by software, persisted to a file or database, takes a locale-independent (root) form instead, and casing used to generate machine-readable identifiers from ASCII text takes a root or fixed locale independent of the user's; this rule covers values displayed to a user. Case mapping of display text written in a language other than the user's takes the language of that text, since case mapping differs between languages. Where the destination of a value is unknown, the data consumer or provider specifies the locale. The rule does not reach which locales a product supports or how a user's locale is obtained.

## Validator
Grep the hunk for the triggers: a locale-sensitive formatter, collator or case-mapping call with an empty argument list, a case-mapping call that takes no locale, a fixed-precision number format, a read or write of the default or process-wide locale, a hard-coded date pattern, and a sort of a list of names, titles or labels. Open each match in the hunk and decide where its result goes: to a person (a rendered page, a message, a notification, a report meant for people) or to software (a file, a database, a protocol field, an identifier). For a value bound for a person, trace the locale back to its source: an argument carrying the user's locale (for a case mapping of text written in another language, that text's language), or the host default retrieved by name, satisfies the rule. Check whether a library routine sets the process-wide locale around the call. Validator question: **Does a number, date, case-mapped string or sorted list of strings that the hunk produces for display to a user come from an operation given no locale argument, from a format pattern that fixes the field order, separators or digit grouping regardless of locale, from an ordinal comparison, or from a process-wide locale that library code sets itself?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: TOOL-42`, severity minor, `file`, `symbol`, `code` = the formatting, case-mapping or sorting call quoted verbatim from the diff, `fix` = the same operation given the user's locale as an argument through the language's explicit-locale API, in the file's language, `rationale` = which displayed value depends on the host default, a pattern fixed regardless of locale or code-point order, and which locale it receives instead).
