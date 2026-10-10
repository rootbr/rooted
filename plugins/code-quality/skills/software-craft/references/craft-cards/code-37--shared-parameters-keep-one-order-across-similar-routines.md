---
title: A routine takes the parameters it shares with similar routines in the same order
rule_id: CODE-37
domain: code
step: [design, implement]
applies_to: [universal]
triggers: ['\b(?:def|fn|func|function)\b[^=;]*\((?:.*,|\s*$)', '^\s*(?:(?:public|protected|private|internal|static|export|abstract|final|override|async|synchronized|default)\s+)+[^=;]*\((?:.*,|\s*$)', '^\s*(?!(?:return|new|throw|else|yield|await)\b)(?:<[^>]*>\s*)?(?:[\w.?\[\]>]|<[^>]*>)+\s+\w+\s*\((?:[^)]*[\w>\]]\s+\w+\s*,|\s*$)', '^\s*(?!(?:return|if|for|while|switch|catch|super|await|yield|typeof|new|import|const|var|type)\b)\w+\s*(?:<[^>]*>)?\s*\((?:\s*\w+\??\s*:\s*[^)]*,|\s*$)', '=\s*(?:async\s+)?\([^)]*,.*=>', '^\s*(?!(?:for|if|while|switch|catch|return|await|yield|new|throw)\b)[A-Za-z_]\w*\s*\((?=[^)]*,)\s*\w+(?:\s*,\s*\w+)*\s+[*\[\]]*[\w.]+']
scope: file
check_kind: semantic
severity_default: minor
---

# A routine takes the parameters it shares with similar routines in the same order

## Thesis
Similar routines that take the same inputs, routines of one type or module that are not overloads of one another, take the shared parameters in the same order. Output parameters placed after the inputs are left out of the comparison, because the documented guidelines rank output-last ordering and consistency with related routines differently where the two clash, and so is the variadic parameter of a variadic routine, since variadic routines may require unusual parameter ordering.

## Rationale
When a call passes arguments by position, parameters of similar types are prone to mix-ups, and adjacent arguments of one type are easily swapped by mistake. A static checker flags a call when a permutation of its arguments matches the parameter names better than the order written, a sign that they may have been swapped by accident; it reports a warning, and its documentation names legitimate swaps, such as width and height when rotating an image. As routines with many parameters evolve, keeping one parameter ordering across overloads and similar methods becomes increasingly difficult, and a set of overloads that holds parameters of similar types at one position with different meanings, as a reversed pair of shared parameters of similar types does, is documented as a design not to use. Output parameters follow an order of their own: they are placed after the by-value and in-out parameters, because they can be seen as extra return values and grouping them together makes the signature easier to understand, and input-only parameters go before any output parameter, a new input-only parameter included rather than added at the end just because it is new. Where that order and consistency with related routines clash, one guideline keeps output parameters after the by-value and in-out parameters even if the ordering between overloads becomes inconsistent, while another calls input-before-output ordering not a hard-and-fast rule and lets consistency with related functions bend it. Variadic routines may require unusual parameter ordering.

## Example
```python
bad:  def copy_rows(source, target, limit): ...
      def move_rows(target, source, limit): ...
good: def copy_rows(source, target, limit): ...
      def move_rows(source, target, limit): ...
```

## Limits
Parameters whose order is not important, such as the two operands of a maximum, raise no problem in either order, so a different order between related routines is no defect. A parameter that a call can supply only by name is never filled in by a positional argument, and naming each parameter at the call site eliminates confusion about argument order; a shared parameter that every routine of the group takes only by name, or as a field of a parameter object the call fills in by name, is outside the comparison. Where output parameters cause the difference, each side has its own documented position: one guideline keeps output parameters after the by-value and in-out parameters even if the ordering between overloads becomes inconsistent, another lets consistency with related functions bend the input-before-output order, and a project convention that settles the clash decides the case.

## Validator
Grep the added lines for a routine signature with two or more parameters, or one that opens a parameter list continued on the following lines. Open the file and gather the routines similar to each such signature: the routines of the same type or module, other than its own overloads, that take parameters representing the same inputs, recognised by shared parameter names and types or by a shared name stem. List the parameters the signature shares with each similar routine, skipping the receiver, output parameters placed after the inputs, a variadic parameter, parameters every routine of the group takes only by name or as a field of a parameter object, and parameters whose order is not important. Compare the order of the remaining shared parameters. If the difference disappears once every output parameter of both routines is set aside, output parameters cause it; skip it. If the hunk's removed lines show the same signature with the same order, the difference predates the change; skip it. Validator question: **Does an added or changed signature take parameters it shares with a similar routine, not an overload of it, in a different order, once the receiver and the output, variadic, by-name and order-free parameters are set aside?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: CODE-37`, severity minor, `file`, `symbol`, `code` = the added signature line verbatim from the diff, followed by the related routine's signature from the file, `fix` = the added signature with its shared parameters moved to the similar routine's order and its calls in the hunk reordered to match, in the file's language, `rationale` = the shared parameters with their positions in both routines, and that parameters of similar types are prone to mix-ups when a call passes them by position).
