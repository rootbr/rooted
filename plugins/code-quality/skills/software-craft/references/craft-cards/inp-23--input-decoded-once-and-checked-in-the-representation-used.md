---
title: Input is decoded and parsed once into the representation the code uses, its checks run on that representation, and the same input is neither decoded again downstream nor handed raw to another parser after the check
rule_id: INP-23
domain: input
step: [implement, review]
applies_to: [service-boundary]
triggers: ['\b(unquote(_plus)?|decodeURI(Component)?|URLDecoder[.]decode|QueryUnescape|PathUnescape|percent_decode(_str)?|html[.]unescape|UnescapeString|unescapeHtml\w*|he[.]decode|b64decode|urlsafe_b64decode|atob|DecodeString|json[.]loads?|json[.]NewDecoder|JSON[.]parse|Unmarshal|readValue|fromJson|serde_json::from_\w+)\(|getDecoder\(\)[.]decode\(']
scope: callers
check_kind: semantic
severity_default: major
---

# Input is decoded and parsed once into the representation the code uses, its checks run on that representation, and the same input is neither decoded again downstream nor handed raw to another parser after the check

## Thesis
Input is decoded according to its protocol before its field rules are checked, the checks run on the representation the code will actually use, and every step after the check works on that checked value: no step decodes the same value again (such as a second percent-, URL-, HTML-entity- or base64-decode), and no step hands the raw input, in place of the checked value, to another parser that may read it differently.

## Rationale
Inconsistent decoding can invalidate an earlier check, which is why the check runs on the representation that will actually be used. Decoding the same input twice could be used to bypass an allowlist by introducing dangerous input after it has been checked: a value that passes after the first decode can become dangerous after the second. Handing the raw input onward lets a second parser decide its meaning again, and parsers can differ where a format leaves the meaning open: the JSON standard specifies no behaviour for duplicate names within an object, so different implementations may behave differently, and two JSON decoders in one standard library treat duplicate names and invalid UTF-8 differently by default. When one service authenticates a request and a second executes it, a request crafted so that the two believe it comes from different users could bypass the authenticator with one user's valid credentials and perform an action on behalf of another. A published survey categorises the anti-patterns underlying such parser differentials and gives as a case an XML vulnerability in which faulty Unicode parsing produced a higher-order parser differential. Decoding once before the check and passing the checked value onward keeps the validated representation the one the code uses.

## Example
```go
bad:  name, err := url.QueryUnescape(raw)
      if err != nil || strings.Contains(name, "..") { return nil, errBadName }
      path, _ := url.PathUnescape(name)
      return os.Open(filepath.Join(root, path))
good: name, err := url.QueryUnescape(raw)
      if err != nil || strings.Contains(name, "..") { return nil, errBadName }
      return os.Open(filepath.Join(root, name))
```

## Limits
Several decoding layers are consistent with the rule when the protocol defines them and all of them run before the field rules are checked; the rule concerns a decode that runs after the check. Repeating canonicalization before the check until the input no longer changes avoids double decoding, but it might inadvertently modify inputs that are allowed to contain properly-encoded dangerous content. Where the raw input has to travel onward unchanged, the check holds only as far as every parser that reads it agrees on its meaning; a decoder that rejects duplicate names and invalid UTF-8 removes two of the cases that implementations read differently. The rule does not reach which well-formed values are acceptable, the choice of character encoding, or Unicode normalization; it reaches the order of decoding, checking and use.

## Validator
Grep the hunk for decode calls (percent- or URL-decode, HTML-entity unescape, base64 decode) and for parse calls on a request body (a JSON decoder). For each one, open the enclosing routine and its callers, trace the value back to where it entered and forward to where it is used, and locate the check it passes (an allowlist, pattern, range, path or permission test). Mark a decode that runs on a value already decoded before that check. Mark a field rule checked on the raw form when the protocol's decode runs only after it. Mark a call after the check that passes the raw input, rather than the checked value, to another decoder, parser or service. Leave unmarked decoding layers that all run before the check; weigh a relay that must pass the original bytes on unchanged under Limits. Validator question: **After the value's field-rule check, does any step decode that value, for the first time or again, or hand the raw input rather than the checked value to another decoder or parser?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: INP-23`, severity major, `file`, `symbol`, `code` = the decode call after the check, or the call that hands the raw input onward, quoted verbatim from the diff, `fix` = the value decoded once before the check and the checked value passed onward, in the file's language, `rationale` = names the check that the later decode or parser bypasses and the input that crosses it).

## Source
- OWASP Input Validation Cheat Sheet, §Implementing Input Validation > Parse Safely, Then Validate (OWASP/CheatSheetSeries master cheatsheets/Input_Validation_Cheat_Sheet.md) (fetched): "Decode according to the protocol before checking field rules. Validate the representation that will actually be used, and avoid decoding it again downstream; CWE-20 explains how inconsistent decoding can invalidate earlier checks."
- CWE-20 Improper Input Validation, Potential Mitigations, phase Implementation (CWE-CAPEC/REST-API-wg main json_repo/W/20.json) (fetched): "Inputs should be decoded and canonicalized to the application's current internal representation before being validated (CWE-180, CWE-181). Make sure that your application does not inadvertently decode the same input twice (CWE-174). Such errors could be used to bypass allowlist schemes by introducing dangerous inputs after they have been checked." and "Consider performing repeated canonicalization until your input does not change any more. This will avoid double-decoding and similar scenarios, but it might inadvertently modify inputs that are allowed to contain properly-encoded dangerous content."
- encoding/json/v2 package documentation, Security Considerations (golang/go master src/encoding/json/v2/doc.go) (fetched): "it is important that all implementations agree upon the semantic meaning of the data." … "If an attacker were able to maliciously craft a JSON request such that both services believe that the same request is from different users, it could bypass the authenticator with valid credentials for one user, but maliciously perform an action on behalf of a different user." … "The standard does not specify a particular behavior when duplicate names are encountered within a JSON object, which means that different implementations may behave differently. By default, v1 allows for the presence of duplicate names, while v2 rejects duplicate names." … "By default, v1 replaces invalid bytes of UTF-8 in JSON strings with the Unicode replacement character, while v2 rejects inputs with invalid UTF-8." Caveat: the package builds under the jsonv2 experiment, and its statements concern JSON only.
- A Survey of Parser Differential Anti-Patterns, LangSec workshop at IEEE S&P 2023, https://langsec.org/spw23/papers/Ali_LangSec23.pdf (relayed): "categorises the anti-patterns underlying parser differentials, with the Stanza Smuggling XML vulnerability as a case where faulty Unicode parsing produced a higher-order parser differential". The search index gave no DOI.
