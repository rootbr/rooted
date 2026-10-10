---
title: Text read back by a program, such as identifiers, keys, tags, file names and stored numbers and dates, is case-mapped, compared, formatted and parsed with a locale-independent operation, never one that follows the user's or the host's locale
rule_id: TOOL-41
domain: tooling
step: [implement]
applies_to: [universal]
triggers: ['[.](toLowerCase|toUpperCase)\(\s*\)|[.]toLocale(LowerCase|UpperCase)\(|[.]localeCompare\(|\bCollator[.]getInstance\(\s*\)|\blocale[.](strcoll|strxfrm)\(|\bStringComparison[.]CurrentCulture', '[.]toLocale(String|DateString|TimeString)\(|\bString[.]format\(\s*"|[.]formatted\(|\bNumberFormat[.]getInstance\(\s*\)|\bDecimalFormat\(|\blocale[.](format_string|atof|atoi|currency|str)\(|\bstrftime\(\s*[''"][^''"]*%[cxXaAbBp]|\bLocale[.]getDefault\(|\bCultureInfo[.]CurrentCulture\b|\bIntl[.](NumberFormat|DateTimeFormat|Collator)\(\s*(\)|undefined\b)']
scope: hunk
check_kind: semantic
severity_default: major
---

# Text read back by a program, such as identifiers, keys, tags, file names and stored numbers and dates, is case-mapped, compared, formatted and parsed with a locale-independent operation, never one that follows the user's or the host's locale

## Thesis
Text meant to be interpreted independently of locale, such as programming-language identifiers, protocol keys, markup tags, file names, and numbers and dates persisted in string form, is case-mapped with the root locale, with a fixed locale whose case mappings are the default ones such as English, or with the default Unicode case mapping, compared ordinally, and formatted and parsed in a form that does not vary by culture, such as the invariant locale's. An operation on such text whose rules come from the user's or the host's current locale is the defect: a case mapping that takes the default locale because it names none, a locale-aware case or number variant, a culture-sensitive comparison, or a number or date format that varies by culture.

## Rationale
A locale-sensitive case mapping may produce unexpected results on text meant to be interpreted independently of locale: in a Turkish locale "TITLE" lower-cases to "tıtle" with a dotless i, which could be extremely dangerous where the code expects to operate on ASCII text to generate machine-readable identifiers. Where a case mapping that names no locale takes the default locale, that default depends on how the runtime is set up and usually on the system it runs on, so on text received over the network or from a file in a well-defined form independent of the environment the transformation is brittle and may yield unexpected results on a machine whose locale has other case rules. Persisting dates or numbers in a format that varies by culture is a common programming error that results in corrupted data or a runtime exception: a date written under one culture's conventions and parsed under another's can be read as a different date or fail to parse, and numbers written under one culture can fail to parse under a culture with a different decimal separator. A comparison that grants access, such as verifying a password or confirming that a file exists, is non-linguistic, and a culture-sensitive one can let through what it should refuse: a case-insensitive check for the prefix "FILE" assumes "i" is always the lowercase of "I", whereas in Turkish and Azerbaijani the uppercase of "i" is "İ", and the culture-sensitive comparison allows file-system access when it should be prohibited. Where the default case mapping already follows the character value only or the default Unicode mappings, the locale-sensitive call is the locale-aware variant, which may give a different result for locales such as Turkish; a locale-aware number format may also vary between implementations even within the same locale and use non-breaking spaces or bidirectional control characters, so its output is not compared with hard-coded constants. The root locale, or a fixed locale such as English, gives casing independent of the user's current locale.

## Example
```typescript
bad:  const key = header.toLocaleLowerCase();
      const row = `${total.toLocaleString()},${due.toLocaleDateString()}`;
      store.write(key, row);
good: const key = header.toLowerCase();
      const row = `${total.toString()},${due.toISOString()}`;
      store.write(key, row);
```

## Limits
Numbers and dates displayed in a user interface take culture-sensitive formatting, output displayed to the user takes the current culture's string operations, and ordered strings displayed in the interface are sorted by culture; that display is outside the rule. Using the host's default locale may be exactly what is wanted for strings the program got through standard input; where that regionalisation is desired, the code names the default locale to make that explicit. A comparison that is linguistically irrelevant, such as a symbolic one, is ordinal rather than one based on the invariant locale.

## Validator
Grep the hunk for case mappings that name no locale, locale-aware case, number and date calls, culture-sensitive comparisons, and number or date formatting or parsing that reads the current or default locale. For each hit, trace the value within the hunk: where it comes from, and whether it is written to a file, a store or a message, used as a key, identifier, tag, header name or file name, compared to grant or refuse access, or parsed from stored or received text, as opposed to shown to a person. Check whether the operation names a root or invariant locale, compares ordinally, or is a case mapping that the language defines as locale-independent, applying the default Unicode mappings whatever the current locale; a case mapping that names no locale but takes the default locale stays a hit. Validator question: **Does the hunk case-map, compare, format or parse text read back by a program with an operation whose result follows the user's or the host's current locale?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: TOOL-41`, severity major, `file`, `symbol`, `code` = the locale-following call and the expression it applies to, quoted verbatim from the diff, `fix` = the same operation in the file's language with its locale-independent form, a root locale for a case mapping, an ordinal comparison for a comparison, or an invariant format for a number or date, `rationale` = where the text is read back and the locale-dependent result it can take, such as a dotless i or a different decimal separator).
