---
title: A user-visible message is written and translated as one string with placeholders for its variable parts, never assembled at run time from concatenated phrases, translated fragments or a plural ending chosen by a test such as n == 1
rule_id: TOOL-40
domain: tooling
step: [implement]
applies_to: [universal]
triggers: ['\b(_|gettext|tr|t|i18n[.]t|intl[.]formatMessage|getString|NSLocalizedString)\([^()]*\)\s*(\+|[.][.]|<<)', '(\+|<<)\s*(_|gettext|tr|t|i18n[.]t|getString|NSLocalizedString)\(', '==\s*1[\s)?{]*[''"]{2}[\s}:]*(else[\s{]*)?[''"]s[''"]|!==?\s*1[\s)?{]*[''"]s[''"]|[''"]s[''"]\s+if\s+\w+\s*!=\s*1|if\s+\w+\s*==\s*1\s+else\s+[''"]s[''"]|\w\([sS]\)[^''"()]*[''"]']
scope: hunk
check_kind: semantic
severity_default: minor
---

# A user-visible message is written and translated as one string with placeholders for its variable parts, never assembled at run time from concatenated phrases, translated fragments or a plural ending chosen by a test such as n == 1

## Thesis
A user-visible message is written as one translatable string that holds entire sentences, with placeholder syntax for its variable parts, and it is translated and formatted as that single unit, so the translator sees the whole sentence and can move the variable parts to fit the grammar of the target language. When the wording depends on a count, the message is one plural-aware message: the message facility selects the form from the count with the plural rules of the target language, and each form holds a full sentence wherever the facility allows.

## Rationale
Translators move the variable elements of a message around according to the grammar of the target language, and most of them do not look at the code and see only the string. A user-visible string concatenated from fragments and formatted elements leaves them unable to rearrange the pieces and hard put to translate each fragment; the concatenation bakes the word order, and with it the grammatical order of the original language, into the code. In many languages the declension of a word depends on the gender or number of another part of the sentence, so two half-sentences translated separately and joined by concatenation fail for many languages even where they work for English. A string with embedded expressions, interpolated at run time, is the same concatenation in a different syntax. A suffix chosen by a test such as n == 1 assumes that plurals are built by adding an s, a string such as "file(s)" looks unnatural, and a test that picks between two complete sentences helps languages whose plurals are built otherwise but still treats the source language's rule as universal: plural forms differ widely between language families, and in one reported language the word for file takes one form for 1, a second for 2 to 4 and 22 to 24, and a third for 5 to 21 and 25 to 31. A plural choice wrapped around only part of a sentence may leave the translator struggling to understand how its fragments interact with the rest of the sentence and unsure whether the part inside the choice may shrink or grow, which is why each choice holds a full sentence; keeping the choices in one message lets a single translator translate them in context, where commercial translation systems often send different messages to different translators.

## Example
```python
bad:  msg = _("Replace ") + old + _(" with ") + new + "?"
      note = str(n) + _(" file") + ("" if n == 1 else "s") + _(" deleted")
good: msg = _("Replace {old} with {new}?").format(old=old, new=new)
      note = ngettext("{n} file deleted", "{n} files deleted", n).format(n=n)
```

## Limits
Output that is ad hoc, local and aimed at other developers rather than end users, such as developer diagnostics, is not a user-visible message, and building it with output-operator chains or concatenation is outside the rule. Two adjacent sentences may stay separate messages when one of them is a stereotypic message that occurs in other places as well; related sentences are better merged into one message, which makes both easier to understand and translate. A long text is split at paragraph boundaries: a translatable string stays within one paragraph and at most ten lines, and long help output becomes several messages of five to ten lines each. A plural message in the source language carries that language's forms and always an other form; the translation system and the translator add forms such as one or few as each target language requires, so a source message is not flagged for lacking them. An interpolated string whose literal parts and values the translation function receives separately, so that extraction reads it as one message with placeholders, is one translatable string and keeps the rule.

## Validator
Grep the hunk for a concatenation operator, an output-operator chain or an interpolated string that joins a translation call or a text literal with another fragment or a run-time value, for a count compared with 1 that selects a suffix or a sentence, and for a literal containing (s). Open the hunk to decide whether the string reaches an end user, as interface text or a message shown to the user, or only developers, as a log line or a debug print. Trace each operand: a separately translated fragment, a bare literal or a run-time value spliced into translated text is the defect; one translated format string filled by the formatter, or an interpolated string whose literal parts and values the translation function receives separately as one message with placeholders, with its plural form chosen by the plural-aware lookup, is the rule kept. Validator question: **Does the hunk build a user-visible message by joining translated fragments, literals or run-time values through concatenation, an output-operator chain or an interpolation whose parts the translation function does not receive separately, or choose its plural wording by testing the count against 1 or with a "(s)" string, instead of one translatable string with placeholders whose plural form the message facility selects?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: TOOL-40`, severity minor, `file`, `symbol`, `code` = the concatenation, interpolation or count test quoted verbatim from the diff, `fix` = the whole sentence as one translatable format string with placeholders, passed through the plural-aware lookup when it depends on a count, in the file's language, `rationale` = names that translators reorder the variable parts to fit the target grammar and that plural forms differ between languages).
