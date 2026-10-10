---
title: Every line of a file is indented with the file's one indentation character and one fixed unit per nesting level, comments included
rule_id: CODE-52
domain: code
step: [implement]
applies_to: [universal]
triggers: ['^(\t+ +| +\t)', '^(  )*[ ](?! )[^\s*]']
scope: file
check_kind: mechanical
severity_default: minor
---

# Every line of a file is indented with the file's one indentation character and one fixed unit per nesting level, comments included

## Thesis
Within a file, the leading whitespace of every line uses one indentation character, spaces or tabs, and each nested block is indented one fixed unit deeper than the block that holds it and returns to that block's level when it ends, so a line starts at the unit multiplied by the level at which its block is nested. A comment on a line of its own is indented at the same level as the surrounding code it applies to. The character and the unit are the ones the file's existing lines use, or the ones the project's configured or declared style sets where that style and the file's lines differ; in a new file, or one whose lines already disagree, they are the ones the project's configured or declared style sets, then the ones the language's official style documentation sets, and where none of these sets them the added lines agree with one another.

## Rationale
Consistent indentation is a simple and effective way to improve readability, and it reduces the differences committed to version control, which makes reviews easier; inconsistent indentation makes code more tedious to review and modify. With one character and one unit, the expected column of a line is the indent size multiplied by the level at which its block is nested, and a checker raises an issue where the indentation does not match, reporting only the first line of a badly indented section. A tab has no fixed width: its width can be configured differently in different environments, so code that mixes spaces and tabs may look fine in one editor and confusing in another configured differently. Most code conventions require either tabs or spaces for indentation, so a single line indented with both is usually an error; one language computes indentation by replacing each tab with one to eight spaces up to the next multiple of eight, calls a mixture of spaces and tabs in a single source file unwise, and rejects with a TabError a file whose mix makes the meaning depend on the width of a tab. A block comment generally applies to the code that follows it and is indented to that code's level, and a checker reports a comment line whose indentation is not a multiple of the unit, or that is indented where the code before it opens no block, as it reports a code line. The width itself is where the sources part: style documents set four spaces per level for two languages, two spaces for a third and a tab for a fourth. One experiment with experienced and novice subjects, reading one program indented 0, 2, 4 or 6 spaces, found that the level of indentation had a significant effect on comprehension, 2 to 4 spaces scoring the highest mean; a non-exact replication in which 22 participants computed the output of code snippets at different indentation levels under eye tracking found no indication that the level affects comprehension or visual effort.

## Example
```go
bad:  if item.Valid {
      // count valid items
         count++
      	    total += item.Size
      }
good: if item.Valid {
      	// count valid items
      	count++
      	total += item.Size
      }
```

## Limits
The rule fixes no width: two spaces, four spaces or a tab per level each meet it when the file uses that width for every level. Spaces that follow the indentation to align a line with an element of the line above are alignment, not indentation: a checker's documented option allows mixed tabs and spaces when the spaces are used for alignment, and where a multi-line block comment starts each later line with a star, that star aligns with the star on the line above, one column past the comment's indentation. A continuation line of a statement broken across lines follows the convention's continuation rule rather than the block unit: at least twice the block unit in one style document, a hanging indent that may differ from the unit or a vertical alignment with the opening bracket in another, one extra tab in a third; only its indentation character is weighed. Which constructs open a level is the convention's: one style document indents the labels of a switch block one level inside the switch, while another language's official examples set them at the switch's own level. Whitespace inside a string literal, a multi-line string or a comment's text is content, not indentation. Where the project's configured or declared style sets a character or unit the file's existing lines do not use, the sources part on which governs: one style document ranks consistency within one module above consistency within a project and keeps tabs only where code is already indented with tabs, while one code-review standard makes the style guide the absolute authority over existing code inconsistent with it, and a checker measures the expected column against the configured indent size; an added line that follows either the file's lines or the project's style meets the rule there. The rule judges the lines the change adds; re-indenting untouched lines is outside it. A tolerance stated in `project_context`, such as generated or vendored files exempt from the project's style, rejects the finding.

## Validator
Grep the added lines for leading whitespace that mixes tabs and spaces and for an odd number of leading spaces. Open the file and establish its indentation: the character and the unit per nesting level its existing lines use, and, where the project's formatter or editor configuration or declared style sets a different character or unit, that one too, either of which an added line may follow; in a new file or one whose lines already disagree, the character and unit the project's formatter or editor configuration or declared style sets, then the language's official style documentation, and where none sets them, the character and unit the other added lines use. For each added line, take the level at which its block is nested, counting the levels the language's convention counts, and compare its leading whitespace with the unit multiplied by that level; give a comment on a line of its own the level of the surrounding code it applies to, and a closing line the level of the line that opened the block it closes. Skip spaces that follow the indentation to align a continuation line or a block-comment star, a continuation line indented by the convention's continuation rule, and whitespace inside a string literal or a comment's text. Report a run of mis-indented lines once, at its first line. Validator question: **Does an added line's leading whitespace, a comment on its own line included, use an indentation character the established indentation does not use, mix the two characters outside alignment, or, a continuation line excepted, start at a column other than the established unit multiplied by the line's nesting level?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: CODE-52`, severity minor, `file`, `symbol`, `code` = the first mis-indented added line of the run, quoted verbatim from the diff with its leading whitespace, `fix` = the run re-indented with the file's character and unit at each line's nesting level, in the file's language, `rationale` = naming the file's indentation character and unit, the line's nesting level, and the character or column found instead).
