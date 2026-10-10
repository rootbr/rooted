---
title: Text that a change writes into a file format, protocol or export it defines or deploys in a new context is encoded as UTF-8, not as UTF-16, a legacy code page or the host's locale encoding
rule_id: TOOL-34
domain: tooling
step: [design, implement]
applies_to: [universal]
triggers: ['(?i)\b(encoding|charset)\s*[=:]\s*\\?[''"]?(latin-?1|iso-?8859[-_]?\d*|cp\d{3,4}|windows-\d+|shift_jis|euc-\w+|gb2312|utf-?16\w*|ucs-?2|mbcs|locale|(us-)?ascii)\b', '(?i)[''"](windows-\d+|cp\d{3,4}|iso-?8859-\d+|latin-?1|binary|shift_jis|euc-(jp|kr)|gb2312|utf-?16(be|le)?|ucs-?2|us-ascii)\\?[''"]']
scope: hunk
check_kind: semantic
severity_default: minor
---

# Text that a change writes into a file format, protocol or export it defines or deploys in a new context is encoded as UTF-8, not as UTF-16, a legacy code page or the host's locale encoding

## Thesis
Text written into a protocol, file format or export format that a change introduces, or into an existing format that the change deploys in a new context, is encoded as UTF-8 exclusively, not as UTF-16, a code page or the host's default encoding, and where the format exposes the name or label of its encoding, it exposes "utf-8".

## Rationale
UTF-8 is the most appropriate encoding for interchange of Unicode, the universal coded character set; it is the de facto standard text encoding, the one that JSON, TOML and YAML use and that many popular programming languages use by default. A code page gives the values 0x80 through 0xFF a meaning that depends on the specific code page, so text saved under one code page and decoded on a system whose default code page differs can lose its original characters; a host's default encoding is platform dependent, and an inconsistent default encoding causes many bugs. Encoding security issues arise when producer and consumer do not agree on the encoding in use or on the way an encoding is implemented: in one reported attack a Shift_JIS leading byte 0x82 masked a 0x22 trailing byte in a JSON resource whose field an attacker could control, the consumer decoded the pair as a single U+FFFD, and the overall interpretation changed because U+0022 (") is an important delimiter. The issue is larger for encodings that map an ASCII byte to something that is not an ASCII code point when no leading byte is present, a class of ASCII-incompatible encodings that includes UTF-16BE and UTF-16LE. The use of Unicode ensures that the same code units always map to the same characters and the same characters always map to the same byte arrays.

## Example
```java
bad:  try (Writer out = Files.newBufferedWriter(path, Charset.forName("windows-1252"))) {
        out.write("<?xml version=\"1.0\" encoding=\"windows-1252\"?>\n");
      }
good: try (Writer out = Files.newBufferedWriter(path, StandardCharsets.UTF_8)) {
        out.write("<?xml version=\"1.0\" encoding=\"utf-8\"?>\n");
      }
```

## Limits
The requirement covers new protocols and formats and existing formats deployed in new contexts; an existing format in its existing deployment keeps the encoding its deployed content requires, the way the web platform supports UTF-16BE and UTF-16LE because deployed content requires them. Code pages are avoided in a globalized application where possible; where an existing consumer or a format specification named in the hunk or its comments requires one, keeping it is not a finding. Reading a legacy encoding that existing content carries is outside the rule: the standard that requires UTF-8 for new formats still defines every legacy encoding, with its algorithms from bytes to scalar values and back and its labels, which user agents must support.

## Validator
Grep the hunk for an encoding named in a charset or encoding argument, a content-type charset parameter or an encoding declaration: a UTF-16 variant, an ISO-8859 or windows code page, an ASCII-only charset, a regional legacy encoding, or the host's default charset passed by name. Open the hunk and decide whether the text goes into a protocol, file, message or export format the change introduces, or into an existing format the change deploys in a new context, and whether an encoding label that the format exposes reads anything other than utf-8. Read the hunk and its comments for an existing consumer or a format specification that requires the legacy encoding. Validator question: **Does the hunk write text for a format it introduces or deploys in a new context in an encoding other than UTF-8, or label that encoding other than utf-8, with no existing consumer or format specification that requires it?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: TOOL-34`, severity minor, `file`, `symbol`, `code` = the line that names the legacy encoding or writes its label, `fix` = the same writer with the language's UTF-8 charset and a "utf-8" label where the format carries one, in the file's language, `rationale` = the new format or new context, the encoding it names, and the producer and consumer disagreement on the bytes that the encoding risks).
