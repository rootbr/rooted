---
title: A value written into an HTML or JavaScript response is encoded for the exact context it lands in, and HTML encoding is not JavaScript encoding
rule_id: SEC-06
domain: security
triggers: ['Encode[.]for', 'htmlEscape\(|escapeHtml|escapeEcmaScript|escapeJson', 'text/html|TEXT_HTML', 'getWriter\(\)', '<(script|div|span|a|input|td|p|h[1-6]|img)[ >]', 'innerHTML|document[.]write']
scope: file
check_kind: semantic
severity_default: critical
---

# A value written into an HTML or JavaScript response is encoded for the exact context it lands in, and HTML encoding is not JavaScript encoding

## Thesis
Every value from outside the code that Java writes into markup — through a `PrintWriter`, a `String` returned as `text/html`, a `StringBuilder` of tags, an inline `<script>` block — passes through the encoder for its landing context: `Encode.forHtml` (or `HtmlUtils.htmlEscape`) between tags, `Encode.forHtmlAttribute` inside a quoted attribute, `Encode.forJavaScript` inside a quoted JavaScript string, `Encode.forCssString` in a CSS value, `Encode.forUriComponent` in a query parameter. A value placed in a JavaScript context with `forHtml`, or with no encoder, is the defect.

## Rationale
Each context has its own metacharacters: HTML entity encoding replaces `&`, `<`, `>`, `"` and `'`, which is what element content needs, but inside `<script>var x = "…"</script>` the value is read as script text, where the characters entity encoding leaves in place are the live ones — a backslash escapes the string's closing quote, and the U+2028 and U+2029 line terminators end it — so HTML and JavaScript encoding are not interchangeable; the JavaScript encoder writes every such character as `\xHH` (or `\uHHHH`). The only safe JavaScript location for a value is inside a quoted string; event-handler attributes, unquoted attributes, CSS selectors and `javascript:` URLs are dangerous contexts that no encoder makes safe. Encoding as the last step, adjacent to the output, is what keeps it correct; a filter that encodes request parameters on the way in cannot know the output context and double-encodes or under-encodes. A stored value another user wrote is as untrusted as a request parameter.

## Example
```java
bad:  out.println("<div>" + name + "</div>");
      out.println("<script>var user = \"" + Encode.forHtml(name) + "\";</script>");
good: out.println("<div>" + Encode.forHtml(name) + "</div>");
      out.println("<script>var user = \"" + Encode.forJavaScript(name) + "\";</script>");
```

## Limits
Applies to output a browser renders: HTML, inline JavaScript, CSS, URL parts. A JSON API response with `application/json` and no HTML rendering on the server is out of scope; the consumer encodes on render. A value that a template engine auto-escapes in its safe text binding is correct; the Java side is flagged only where it bypasses the template with raw markup. A value reduced to an allowlisted enum or numeric type before output carries no metacharacters and is not flagged. Rich HTML the user is allowed to write takes an HTML sanitizer policy, then encoding of whatever the policy did not sanitize.

## Validator
On the triggered hunk find each write of markup that includes a non-constant operand, and each `Encode.forX` or `htmlEscape` call. For each operand determine its landing context from the surrounding markup — element content, attribute, `<script>` string, CSS, URL — and the encoder applied. Open the file to trace the operand's origin. Validator question: **does a value from outside the code reach a browser-rendered context with no encoder, or with an encoder for a different context?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: SEC-06`, severity critical, `file`, `symbol`, `code` = the output statement quoted verbatim from the diff, `fix` = the same statement with the encoder of the landing context, `rationale` naming the context and the metacharacters the applied encoding leaves live).

## Source
OWASP Cross Site Scripting Prevention Cheat Sheet — output encoding per context ("HTML Contexts", "HTML Attribute Contexts", "JavaScript Contexts": "the only 'safe' location for placing variables in JavaScript is inside a 'quoted data value'"; "Dangerous Contexts"); the interceptor anti-pattern — "JavaScript and HTML encoding are not interchangeable". OWASP ASVS 5.0 requirements 1.1.2, 1.2.1, 1.2.3. OWASP Java Encoder project README — "Contextual Output Encoding". CWE-79.
