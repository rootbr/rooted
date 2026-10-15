---
title: User-visible text that a change adds, such as labels, prompts and messages shown to users, is looked up from the project's resource or message catalog rather than written as a bare literal in the code that displays it
rule_id: TOOL-39
domain: tooling
step: [implement]
applies_to: [universal]
triggers: ['(?i)\b(set_?text|set_?title|set_?label|set_?message|set_?tool_?tip(_?text)?|show_?message_?dialog)\((?:[^()\x27"`]*,\s*)?[\x27"`][A-Za-z]', '>\s*[A-Z][a-z]+(\s+[A-Za-z]+)+[.!?]?\s*</', '\b(alert|confirm|toast|flash|notify|showError|showMessage)\(\s*[\x27"`][A-Z]', '(?i)\b(title|label|placeholder|aria-label|tooltip|caption|button_?text)\s*[:=]\s*[\x27"][A-Z][^\x27"]*\s[^\x27"]*[\x27"]']
scope: callers
check_kind: semantic
severity_default: minor
---

# User-visible text that a change adds, such as labels, prompts and messages shown to users, is looked up from the project's resource or message catalog rather than written as a bare literal in the code that displays it

## Thesis
Text that a change adds for users to read, such as labels, prompts, status displays, help messages and error messages, is looked up from the project's resource or message catalog, by key or by passing it through the catalog's marking call, rather than handed to the code that displays it as a bare literal. The rule holds for a product that targets a single culture or region and for text written in English.

## Rationale
Interactive software may contain dozens or hundreds of prompts, status displays, help messages and error messages, and its design and construction should accommodate how those strings are maintained without changing the code and translated into different languages with minimal impact on the processing code and the user interface. Text hard-coded at the point of display cannot be properly translated to other languages. A catalog keeps all the strings in a single location, so changing one for a language or culture needs no search through the source code. Without one, the same string is often defined in several source files, and that duplication increases the probability that one or more instances are overlooked when the string is modified. With the text in the catalog, the program can load the variant appropriate for the current user's locale, and the program code can stay largely independent of that locale. In the marking form, the source string handed to the marking call serves as the key for looking up its translation, and extraction tools collect the marked strings for translation.

## Example
```java
bad:  button.setText("Save changes");
      String title = "Unsaved changes";
      showError("Could not save the file.");
      label.setText("<html><b>Unsaved changes</b></html>");
good: ResourceBundle messages = ResourceBundle.getBundle("Messages", locale);
      button.setText(messages.getString("button.save"));
      String title = messages.getString("dialog.unsaved.title");
      showError(messages.getString("error.save.failed"));
      label.setText(messages.getString("label.unsaved"));
```

## Limits
A string that is not meant for translation, such as a file name or a file-open mode, stays a literal in code; only a string that needs to be translated is marked. Unit test code, which does not need to be localized, may hold literal text, and code that parses data files from foreign sources may hard-code the strings those files use as delimiters. A suppression the project has recorded, such as a lint configuration that turns the hard-coded display-text check off for a folder and its subfolders, is a documented tolerance there. The rule reaches text the hunk adds; how a looked-up message is assembled, which languages a product supports and what its translations say lie outside it.

## Validator
Grep the hunk's added lines for string literals passed to display calls (set-text, title, label, message, dialog, alert, toast and notify calls), for literal prose between markup tags, and for literal values of user-facing attributes (title, label, placeholder, aria-label, tooltip, caption). For each match, read the surrounding hunk to decide whether a person reads the string: skip file names, modes, keys, identifiers, delimiters of parsed data formats and anything in a test file. Check whether the literal already passes through the project's catalog lookup or marking call, and whether a recorded suppression covers the file. Validator question: **Does the hunk add text that a user reads as a bare literal at the point of display, outside test code, with no catalog lookup or marking call around it and no recorded suppression covering it?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: TOOL-39`, severity minor, `file`, `symbol`, `code` = the added line that displays the literal, verbatim, `fix` = the same display call reading the text from the project's catalog by key or through its marking call, plus the catalog entry it needs, in the file's language, `rationale` = names the literal, where users see it, and that text written at the point of display cannot be translated or changed without a code change).

## Source
- SWEBOK Guide V3.0 ch. 3 §4.8 'Runtime Configuration and Internationalization' (raw.githubusercontent.com/ligurio/swebok-v3/master/3_software_construction.md) — "Interactive software may contain dozens or hundreds of prompts, status displays, help messages, error messages, and so on. The design and construction processes should accommodate string and character-set issues including [...] how to maintain the strings without changing the code, and translating the strings into different languages with minimal impact on the processing code and the user interface." (fetched)
- .NET documentation 'Globalization', 'Use resource files' (dotnet/docs docs/core/extensions/globalization.md) — "Even if you are developing an app that targets a single culture or region, you should use resource files to store strings and other resources that are displayed in the user interface. You should never add them directly to your code."; "All the strings are in a single location. You don't have to search throughout your source code to identify strings to modify for a specific language or culture."; "Developers who don't use resource files often define the same string in multiple source code files. This duplication increases the probability that one or more instances will be overlooked when a string is modified." (fetched)
- Google C++ Style Guide, 'Non-ASCII Characters' (google/styleguide cppguide.html) — "You shouldn't hard-code user-facing text in source, even English"; "if your code parses data files from foreign sources, it may be appropriate to hard-code the non-ASCII string(s) used in those data files as delimiters. More commonly, unit test code (which does not need to be localized) might contain non-ASCII strings." (fetched)
- Python gettext documentation, 'Internationalizing your programs and modules' (python/cpython Doc/library/gettext.rst) — "Any string that needs to be translated should be marked by wrapping it in _('...')"; "the string 'writing a log message' is marked as a candidate for translation, while the strings 'mylog.txt' and 'w' are not."; "There are a few tools to extract the strings meant for translation." (fetched)
- java.util.ResourceBundle Javadoc (openjdk/jdk jdk-21-ga ResourceBundle.java) — "your program can load it from the resource bundle that is appropriate for the current user's locale. In this way, you can write program code that is largely independent of the user's locale" (fetched)
- golang.org/x/text/message package documentation (pkg.go.dev), 'Translation' and 'Translation Pipeline' — "The format strings that are passed to Printf, Sprintf, Fprintf, or Errorf are used as keys to look up translations"; "Mark strings in your source to be translated by using message.Printer, instead of the functions of the fmt package."; "Extract the strings from your source" (fetched)
- Android Lint check SetTextI18n (googlesamples/android-custom-lint-rules docs/checks/SetTextI18n.md.html), severity Warning, category Internationalization — "Do not pass a string literal (e.g. "Hello") to display text. Hardcoded text can not be properly translated to other languages."; suppression via "a special lint.xml file in the source tree which turns off the check in that folder and any sub folder" (fetched)
- Caveat: the sources are construction guidance, platform documentation and a lint rule; none measures a defect or cost rate, so the rule rests on documented practice rather than an effect size.
