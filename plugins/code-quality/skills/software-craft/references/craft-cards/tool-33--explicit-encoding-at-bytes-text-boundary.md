---
title: A conversion between bytes and text at a file, network or process boundary names its encoding through the language's explicit-encoding API whenever the data is not UTF-8 or a runtime the code supports takes the conversion's default from the host's locale
rule_id: TOOL-33
domain: tooling
step: [implement]
applies_to: [universal]
triggers: ['\b(read_to_string|read_text|write_text|readFileSync|readFile|writeFileSync|writeFile|readString|writeString|from_utf8(_lossy)?|TextIOWrapper|FileReader|FileWriter|InputStreamReader|OutputStreamWriter|PrintStream|PrintWriter|Scanner|TextDecoder|TextEncoder)\(|\bopen\((?![^)]*\bencoding\b)|\bgetBytes\(\s*\)|\bnew\s+String\(\s*\w+\s*\)|[.](decode|encode)\(\s*\)|\bstring\(\s*\w+\s*\)|\b(text|universal_newlines)\s*=\s*True\b']
scope: callers
check_kind: semantic
severity_default: major
---

# A conversion between bytes and text at a file, network or process boundary names its encoding through the language's explicit-encoding API whenever the data is not UTF-8 or a runtime the code supports takes the conversion's default from the host's locale

## Thesis
A call that turns bytes into text or text into bytes at a file, socket, pipe or process boundary names the encoding the data has through the language's explicit-encoding API whenever a runtime version the code supports takes that call's default encoding from the host's locale, or the data is in an encoding other than UTF-8. Where decoding with the host's own encoding is the intent, the call names the locale encoding explicitly. Where every supported runtime version's default for the conversion is UTF-8 and the data is UTF-8, the encoding may stay implicit.

## Rationale
A conversion that leaves the encoding out relies on the runtime's default. Where that default is locale-specific it can vary from machine to machine, and the application's encoding and decoding can then vary between platforms and between runs, even for ASCII characters, which take one byte in UTF-8 and two in UTF-16. Developers on macOS or Linux may forget that the default encoding is not always UTF-8: of the 4000 most downloaded packages of one package index, 489 use non-ASCII characters in their README and 82 fail to install from source on non-UTF-8 locales due to not specifying an encoding for a non-ASCII file. Stable encoding and decoding needs an explicit charset; where the locale-specific encoding is the one intended, naming it makes that encoding explicit in the call. A reading call that decodes only UTF-8 can return an error when the contents are not valid UTF-8; data in another encoding is read as bytes and decoded by a function for that encoding, such as the byte-to-character mapping that effectively decodes ISO-8859-1.

## Example
```rust
bad:  let text = fs::read_to_string(path)?; // the file is ISO-8859-1
good: fn decode_iso_8859_1(bytes: &[u8]) -> String {
          bytes.iter().map(|&b| char::from(b)).collect()
      }
      let text = decode_iso_8859_1(&fs::read(path)?); // the file is ISO-8859-1
```

## Limits
The rule is contested. Checkers for runtimes with a locale-specific default flag a conversion that omits the encoding, on the grounds that the default varies between machines and platforms, and one of them points to the proposal that counted the 82 failing packages. The maintainers of one runtime made UTF-8 its default and rejected deprecating the implicit encoding, because there are many cases in which the default encoding is used for reading or writing only ASCII text, such warnings are not useful for applications that run only on Unix and not cross-platform, and forcing users to specify the encoding everywhere is too painful; the maintainers of a second runtime made UTF-8 its default and rejected the same idea. A checker for the first runtime stops flagging the omission when the configured version is the one with the UTF-8 default. The cases separate on where the default comes from and what the data is. Where a supported runtime version takes the call's default from the host's locale, the encoding is named, because that default varies between hosts. Where every supported runtime version's default for the call is UTF-8 and the data is UTF-8, the omission is accepted. Both runtimes keep an opt-out of the UTF-8 default, an environment variable or command-line option in one and a command-line property in the other that derives the default from a value that typically depends on the operating system's locale and charset, and a deployment that uses either falls under the first case. Data in another encoding is decoded with that encoding named on every runtime, and a locale-specific encoding that is intended is named as such. The rule reaches calls that perform a byte-to-text or text-to-byte conversion on data read from or written to a file, socket, pipe or process; text already decoded and handled in memory is outside it. Text that a change writes into a format it introduces, or deploys in a new context, is encoded as UTF-8; the locale encoding is named only for data that already exists in the host's encoding.

## Validator
Grep the hunk for calls that convert between bytes and text: opening a file in text mode, reading a whole file as text, wrapping a file, socket, pipe or process stream in a reader, writer or scanner, running a child process with text output, building a string from a byte array, and getting a string's bytes. For each call, check whether it names an encoding through an argument or a charset object. Where it leaves the encoding out, read the hunk, its file and any declared minimum runtime version for whether a supported runtime version takes that call's default from the host's locale, since calls on one runtime differ in where their default comes from, and treat such a version as supported when no minimum is declared. Read the file name, the format and the surrounding code for the encoding the data has. A call that names the locale encoding passes where the data is in the host's encoding, and a call that leaves the encoding out passes where every supported runtime version's default for that call is UTF-8 and the data is UTF-8. Validator question: **Does a call that converts between bytes and text at a file, socket, pipe or process boundary leave its encoding unnamed while a supported runtime version takes that call's default from the host's locale, or convert the data with an encoding other than the one it has?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: TOOL-33`, severity major, `file`, `symbol`, `code` = the conversion call verbatim from the diff, `fix` = the same conversion with the data's encoding named through the language's explicit-encoding API, or with the locale encoding named where the host's encoding is intended, in the file's language, `rationale` = the condition that holds, either the supported runtime version whose default for that call comes from the host's locale or the encoding the data has against the one the call uses).
