---
title: Input from outside the trust boundary is size-limited before it is buffered or parsed, and a parser that offers a nesting-depth or size limit has that limit set
rule_id: INP-24
domain: input
step: [implement]
applies_to: [service-boundary]
triggers: ['\b(io|ioutil)[.]ReadAll\(|\brequest[.](get_data|get_json|data|body)\b|\breq[.]body\b|[.]readAllBytes\(\)|IOUtils[.]toByteArray\(|[.]read_to_end\(|[.]read_to_string\(|\b(json[.]loads?|yaml[.]safe_load|JSON[.]parse|serde_json::from_(slice|reader|str)|json[.]NewDecoder)\(|await\s+\w+[.](json|text|arrayBuffer)\(\)']
scope: callers
check_kind: semantic
severity_default: major
---

# Input from outside the trust boundary is size-limited before it is buffered or parsed, and a parser that offers a nesting-depth or size limit has that limit set

## Thesis
Input that arrives from outside the trust boundary has its size limited before it is buffered or parsed, and when the parser for it offers a nesting-depth or size limit, that limit is in effect.

## Rationale
A malicious input may cause a decoder to consume considerable CPU and memory, and limiting the size of the data before it is buffered or parsed is the recommended guard. Size bounds nesting only through the size itself: a must-reject case in a public JSON conformance suite is 100,000 bytes, every one an opening bracket, and so opens 100,000 levels of nesting. For one standard literal evaluator, a relatively small input can lead to memory exhaustion or to native stack exhaustion, crashing the process, and some inputs bring the possibility of excessive CPU consumption. The parser's own limits, such as a maximum nesting depth, are the second guard; the JSON format explicitly supports implementation limits on size, depth and numbers. A schema check after parsing cannot protect a parser that has already exhausted resources, so both limits act before or during the parse.

## Example
```rust
bad:  let mut body = Vec::new();
      reader.read_to_end(&mut body)?;
      let doc = parse(&body)?;
good: let mut body = Vec::new();
      reader.take(MAX_BODY + 1).read_to_end(&mut body)?;
      if body.len() as u64 > MAX_BODY { return Err(Error::TooLarge); }
      let doc = parse_with(&body, Limits { max_depth: MAX_DEPTH })?;
```

## Limits
The rule's condition is input from untrusted sources; input that originates inside the trust boundary, such as a file shipped with the program, is outside it. The rule asks for each limit to be in effect, not for it to be set at a particular place in the code: a request size limit set once in the server or framework configuration and applied before the body is read satisfies the size limit, a nesting-depth or size limit that the parser sets by default and the code leaves in place satisfies the parser limit, and neither stands in for the other. Where the parser offers no nesting-depth or size limit, the size limit before parsing is the part of the rule that applies: one standard JSON decoder imposes no such limits beyond those of the language's data types and interpreter, and its documentation recommends limiting the size of the data to be parsed. The sources give no value for either limit, and the rule sets none. Depth bounds inside a hand-written recursive parser, and whether a well-formed value is acceptable once parsed, are outside this rule. A parser whose documentation advises against running it on untrusted data at all, as the literal evaluator's does, is not made safe by either limit, and choosing another parser is outside this rule.

## Validator
Grep the hunk for a call that reads a whole stream or request body into memory and for a call that hands input to a parser. Open the callers to find where the input comes from; when it crosses the trust boundary (a network request, an uploaded file, a message from another service), trace back from the read or parse call to a size limit applied before the bytes are buffered: a bounded reader, a check of the declared length against a maximum before reading that also rejects or bounds a body whose length is not declared, or a request size limit in the server or framework configuration. Open the parser's construction or options: when the parser offers a nesting-depth or size limit, confirm that one is in effect, set by the code or by the parser's default. Validator question: **Does input from outside the trust boundary reach buffering or parsing with no size limit applied before it, or reach a parser that offers a nesting-depth or size limit with no such limit in effect?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: INP-24`, severity major, `file`, `symbol`, `code` = the read or parse call that takes the untrusted input, quoted verbatim from the diff, `fix` = the same input read through a size limit applied before buffering and parsed with the parser's depth or size limit set where the parser offers one, in the file's language, `rationale` = names the trust boundary the input crosses and the resource, memory, stack or CPU, that the unbounded read or parse leaves exposed).
