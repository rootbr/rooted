---
title: Bytes are decoded to text where they enter the program and text is encoded where it leaves, so code between those points takes and returns text rather than encoded bytes
rule_id: TOOL-35
domain: tooling
step: [design, implement]
applies_to: [universal]
triggers: ['[.](decode|encode)\(|\bString::from_utf8(_lossy)?\(|\bstr::from_utf8\(|[.]as_bytes\(\)|\bgetBytes\(|\bnew\s+String\(|\bTextDecoder\(|\bTextEncoder\(', '->\s*bytes\b|:\s*bytes\b|\bbyte\[\]\s+\w+\s*[,)]|\[\]byte\b|&\[u8\]|Vec<u8>|\bBuffer\b|\bUint8Array\b']
scope: file
check_kind: semantic
severity_default: minor
---

# Bytes are decoded to text where they enter the program and text is encoded where it leaves, so code between those points takes and returns text rather than encoded bytes

## Thesis
Software should work only with decoded text internally, decoding input bytes as soon as possible after they enter the program and encoding output only at the end, for instance where it is written to disk or sent over a socket, so each of the program's own routines between those two points takes and returns one kind of string, text, rather than a mix of text and encoded bytes.

## Rationale
Processing routines that accept both text and encoded bytes are vulnerable to bugs wherever the two kinds of string are combined. One character can be represented by several bytes, so code that decodes bytes itself in chunks of arbitrary size, such as 1024 or 4096 bytes, needs error handling for a chunk that ends partway through a character; decoding the whole input at once instead means a 2 GiB file needs 2 GiB of RAM, and more for the moment both the encoded and the decoded copy exist. That manual approach is not recommended: the documented remedy is a file object that assumes the file's contents are in a specified encoding, handles partial sequences and accepts text parameters for methods such as read and write. A check for illegal characters in data from a web browser or another untrusted source, made before the string goes into a generated command line or a database, is made on the decoded text, not on the encoded bytes, since some encodings may be non-bijective or not fully ASCII-compatible; this matters most when the input also specifies its encoding, because an attacker can then choose a way to hide malicious text in the encoded bytes. Decoding at entry and encoding at exit leaves one kind of string in between, so no processing routine combines the two kinds.

## Example
```python
bad:  def label(raw: bytes) -> bytes:
          return raw.decode("utf-8").title().encode("utf-8")
      dst.write(label(src.read()))
good: def label(text: str) -> str:
          return text.title()
      with open(src_path, encoding="utf-8", newline="") as src:
          text = label(src.read())
      with open(dst_path, "w", encoding="utf-8", newline="") as dst:
          dst.write(text)
```

## Limits
The evidence addresses software that deals with Unicode text, so the rule reaches data the program handles as text and leaves other data out of scope. A library that supports Unicode natively already returns text, as XML parsers often do and as many relational databases can for Unicode-valued columns returned from a query; the documentation advises checking whether the libraries in use support Unicode natively. When a file's encoding is unknown but known to be ASCII-compatible and only its ASCII parts are examined or changed, the documented approach still decodes at the read site, with a decoding that turns each non-ASCII byte into a distinct code point and turns those code points back into the same bytes when the text is encoded and written out. In a language whose string type holds arbitrary bytes and is not required to hold Unicode text, UTF-8 text or any other predefined format, a string's content is exactly equivalent to a slice of bytes, so a conversion between the two types decodes nothing and neither type shows whether a value was decoded, while, where source code is always UTF-8, a string literal without byte-level escapes always holds valid UTF-8; there a byte sequence already in the encoding the program's own text uses counts as text.

## Validator
Grep the hunk for encode and decode calls, for parameters, fields and return values typed as bytes, byte arrays or byte buffers, and for conversions between strings and byte sequences. Open the file and trace each hit both ways: where the value came from (a read from a file, socket, process or library) and where it goes (a write, a send, or another of the program's own routines). Where the language's string type can hold arbitrary bytes, judge a value by its origin and its use, not by its type, and count bytes already in the encoding the program's own text uses as text. A decode applied to bytes just read, or right after the input's own declaration of its encoding has been read, and an encode whose result goes straight into a write, a send or a call that takes only bytes are the edges the rule asks for. Validator question: **Does the change pass text between the program's own routines as encoded bytes, give one of its routines a parameter that accepts both text and encoded bytes, or convert the same text to bytes and back between the site where it enters and the site where it leaves?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: TOOL-35`, severity minor, `file`, `symbol`, `code` = the routine signature or the encode or decode call that carries encoded bytes through the program's own code, `fix` = the routine taking and returning the language's text type with the decode moved to the read site and the encode to the write site, in the file's language, `rationale` = which conversion sits inside the program and the read or write site it belongs at).

## Source
- python/cpython Doc/howto/unicode.rst, "Tips for Writing Unicode-aware Programs" (fetched): "This section provides some suggestions on writing software that deals with Unicode." / "Software should only work with Unicode strings internally, decoding the input data as soon as possible and encoding the output only at the end." / "If you attempt to write processing functions that accept both Unicode and byte strings, you will find your program vulnerable to bugs wherever you combine the two different kinds of strings." / "When using data coming from a web browser or some other untrusted source, a common technique is to check for illegal characters in a string before using the string in a generated command line or storing it in a database. If you're doing this, be careful to check the decoded string, not the encoded bytes data; some encodings may have interesting properties, such as not being bijective or not being fully ASCII-compatible. This is especially true if the input data also specifies the encoding, since the attacker can then choose a clever way to hide malicious text in the encoded bytestream."
- python/cpython Doc/howto/unicode.rst, "Reading and Writing Unicode Data" (fetched): "you should check whether the libraries used in your application support Unicode natively. XML parsers often return Unicode data, for example. Many relational databases also support Unicode-valued columns and can return Unicode values from an SQL query." / "Unicode data is usually converted to a particular encoding before it gets written to disk or sent over a socket." / "the manual approach is not recommended" / "one Unicode character can be represented by several bytes. If you want to read the file in arbitrary-sized chunks (say, 1024 or 4096 bytes), you need to write error-handling code to catch the case where only part of the bytes encoding a single Unicode character are read at the end of a chunk." / "if you need to read a 2 GiB file, you need 2 GiB of RAM. (More, really, since for at least a moment you'd need to have both the encoded string and its Unicode version in memory.)" / "The solution would be to use the low-level decoding interface to catch the case of partial coding sequences. The work of implementing this has already been done for you: the built-in open() function can return a file-like object that assumes the file's contents are in a specified encoding and accepts Unicode parameters for methods such as read() and write()"
- python/cpython Doc/howto/unicode.rst, "Files in an Unknown Encoding" (fetched): "If you know the encoding is ASCII-compatible and only want to examine or modify the ASCII parts, you can open the file with the surrogateescape error handler" / "decode any non-ASCII bytes as code points in a special range running from U+DC80 to U+DCFF. These code points will then turn back into the same bytes when the surrogateescape error handler is used to encode the data and write it back out."
- golang/website _content/blog/strings.md, "What is a string?", "UTF-8 and string literals" and "Code points, characters, and runes" (fetched): "a string holds _arbitrary_ bytes. It is not required to hold Unicode text, UTF-8 text, or any other predefined format." / "As far as the content of a string is concerned, it is exactly equivalent to a slice of bytes." / "only string literals are UTF-8" / "Go source code is always UTF-8." / "A string literal, absent byte-level escapes, always holds valid UTF-8 sequences."
- Caveat: the first source states the tip for one language's text and byte types; the rule carries it to the text types of the others, and the second source narrows the type-based reading where a string holds arbitrary bytes.
