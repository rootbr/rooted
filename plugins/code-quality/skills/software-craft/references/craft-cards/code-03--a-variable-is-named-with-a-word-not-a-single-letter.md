---
title: A variable is named with a word rather than a single letter, except a conventional letter in its conventional role
rule_id: CODE-03
domain: code
step: [implement, refactor]
applies_to: [universal]
triggers: ['\b(let|var|const|val|auto|mut)\s+[A-Za-z]\b(?!\s*[.(])|^\s*((private|public|protected|readonly|static)\s+)*[A-Za-z]\s*[?!]?\s*(:=|:\s*\w|=(?!=)|,\s*[A-Za-z_]\w*\s*:?=)|^(?!.*\bfor\s*\().*\b([A-Z][\w.]*(<.*>)?(\[\])*|int|long|short|byte|char|double|float|bool|boolean|string)\s+[*&]?[A-Za-z]\s*[=;,)]|\bfor\s+[A-Za-z]\s+in\b|\bfor\s*\([^;]*?[\s&*][A-Za-z]\s*:(?!:)|\bfor\s+([A-Za-z_]\w*\s*,\s*)?[A-Za-z]\s*:?=\s*range\b|^\s*[a-z](\s*,\s*[a-z])*\s+[*\[\]]*(map\[[\w.*\[\]]+\]|chan\s+)?[\w.]+,?\s*(`[^`]*`)?\s*(//.*)?$', '[(,]\s*[A-Za-z]\s*:\s*[&\[\w]|\bfunc\b.*[(,]\s*[A-Za-z]\s+[*\[\]\w.]+|\b(def|function)\b[^(]*\((.*,)?\s*[A-Za-z]\s*[,)=]|(?<![\w$.])[A-Za-z]\s*\)?\s*(=>|->)|\(\s*[A-Za-z]\s*,[^()]*\)\s*(=>|->)|\|\s*&?(mut\s+)?[A-Za-z]\s*[|,:]|\blambda\s+[A-Za-z]\s*[,:]|\{\s*[A-Za-z]\s+in\b']
scope: file
check_kind: mechanical
severity_default: minor
---

# A variable is named with a word rather than a single letter, except a conventional letter in its conventional role

## Thesis
Outside a conventional role, a variable, field or parameter is named with a whole word or phrase, not a single letter. The conventional roles are a loop index or counter (i, j, k), a generic iteration value (v), a coordinate (x, y, z), a caught exception (e), a file handle used only inside the block that opens it (f), a type parameter (T, E), and, outside a public interface, a letter that matches the notation of a paper or algorithm cited in a comment or docstring of the code that uses it. A single letter that stands for a domain value, such as an order, a price, a rate or a customer, is replaced with the word for that value.

## Rationale
A word gives the reader direct access to the meaning of the concept a name represents. In a within-subjects experiment 72 professional developers looked for defects in code snippets written three ways; with whole words they found semantic defects on average 19% faster than with single letters or abbreviations, letters and abbreviations did not differ significantly, and the naming style had no significant effect on finding syntax errors. With whole words they also scrolled less often to the snippets' comments to retrieve the meaning of a variable. In a study in which over 100 programmers described twelve functions written with single letters, abbreviations or full words, full words gave the best comprehension, though in many cases not significantly better than abbreviations. A conventional letter is the exception because the convention supplies the meaning: letters mined from 1000 popular projects in five languages show i in loops and some other letters in wide use, and a survey found certain letters strongly associated with certain types and meanings. The measured cost is in reading speed and comprehension; on the ability to change code, controlled experiments that gave the same functions different variable names failed to show a significant difference. Descriptiveness scales with a name's scope: the further from its declaration a name is used, the more descriptive it has to be.

## Example
```typescript
bad:  export function applyDiscount(p: number, r: number): number {
        const d = p * r;
        return p - d;
      }
good: export function applyDiscount(price: number, rate: number): number {
        const discount = price * rate;
        return price - discount;
      }
```

## Limits
A letter in one of the conventional roles meets the rule, and so does an underscore used as a deliberate discard, which names nothing. A parameter name fixed by an inherited declaration, on a routine that overrides or implements it, is judged at the declaration that introduced it. The rule weighs one-letter names only; abbreviations, casing and the choice between two words are outside it. Whether a letter is acceptable is contested, and two conditions separate the cases. The first is whether the letter is conventional for its role: a conventional letter conveys its meaning, as certain letters are strongly associated with certain types and meanings, and two static-analysis rules that flag short names exempt a short list of letters by default (one exempts loop counters i, j, k, an exception variable e and a parameter n; the other allows i, j, x, y, z, w and n); a non-conventional letter standing for a domain value is the case the timed defect-finding experiment measured, with letters assigned in order of occurrence (a, b), and a word replaces it. The second is whether a documented convention admits short local names: where the language's official convention prefers short names for local variables of limited scope and one or two letters for a method receiver, a letter inside that scope meets the rule, and where the project context documents a tolerance, such as single letters for variables, parameters outside an exported interface included, that are in scope for 10 lines or fewer, a letter inside that tolerance meets it.


The conventional-role exemption covers a letter whose uses stay within a small scope; a conventional letter read across several nested scopes or far from its declaration is judged by its scope, which this rule does not weigh. A familiar letter for a common type that stands for no domain value, r for a reader or a request, w for a writer or a response writer, p for a generic pointer, x for a generic floating-point operand, is a conventional letter in that role.
## Validator
Grep the added lines for a declaration, assignment, field or parameter, a lambda or closure parameter included, whose name is one letter. Open the file and, for each such name, read its role (loop index or counter, iteration value, coordinate, caught exception, file handle, type parameter, method receiver) and any comment or docstring of the enclosing code that cites a paper or algorithm whose notation it follows. Count the lines over which it is in scope and the lines from its declaration to its last use, note whether it is a parameter of an exported interface or of an overriding routine, apply what the file language's official naming convention says about short local names, and read the project context for a documented tolerance on short local names. Validator question: **Does an added variable, field or parameter carry a single-letter name that is neither a conventional letter in its conventional role, nor inside the scope that a documented language convention or project tolerance admits for short names, nor a parameter name fixed by the inherited declaration of a routine it overrides or implements?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: CODE-03`, severity minor, `file`, `symbol`, `code` = the added line declaring the single-letter name, quoted verbatim from the diff, `fix` = the declaration and its uses with the letter replaced by the word or phrase for the value it holds, in the file's language, `rationale` = the letter, the domain value it stands for, and why no conventional role or documented tolerance covers it).
