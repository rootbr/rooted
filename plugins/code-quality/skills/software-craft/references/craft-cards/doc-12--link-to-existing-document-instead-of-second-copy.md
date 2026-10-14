---
title: A change links to the repository document that already holds the material rather than copying it into a second document
rule_id: DOC-12
domain: docs
step: [document, review]
applies_to: [prose]
triggers: ['signal:duplicate_block', 'signal:added_file', '(?i)^\W*(install(ation)?|set ?up|getting started|configuration|usage|requirements)\b', '(?i)\b(install(ation)?|set ?up|getting started|configuration)\s*:']
scope: callers
check_kind: semantic
severity_default: suggestion
---

# A change links to the repository document that already holds the material rather than copying it into a second document

## Thesis
A change that adds documentation material which another document in the repository already holds, such as install steps, a configuration table or a guide to a shared tool or process, replaces that material with a link or reference to the holding document, so the repository keeps one copy. When the holding document is badly out of date, the change puts its updates into that document and links to it.

## Rationale
Documentation maintainability concerns how easy it is to apply changes or corrections to the documentation. In a study of 878 mined documentation artifacts, duplicated content caused troubles for documentation maintainers, just as in source code, and the maintainers mostly resolved it by replacing the clone with links and references. In a practitioner survey, 46% considered clone or duplicate content one of the main sources of maintainability concern, beside superfluous content at 55%; in the mined study, those two subcategories account for about 71% of developers' discussions on documentation maintainability. A link in place of the copy leaves one document in which a change or correction to the material is applied.

## Example
```go
bad:  // Package store keeps orders.
      // Install: go get example.com/store, set STORE_DSN,
      // then run store-migrate before the first start.
      package store
good: // Package store keeps orders. Install and configure it
      // as the [README] describes.
      //
      // [README]: https://example.com/store#install
      package store
```

## Limits
Documentation frameworks often make duplicates hard to avoid, so a copy that the project's documentation tooling requires in two places is outside the rule. A one-line pointer that names the topic and links to the holding document is the link or reference the rule asks for, not a second copy. The rule reaches a second guide, procedure or table in a separate document; repetition inside one document is outside its reach. A conceptual or overview document that restates part of what reference documentation holds, to explain it, is outside the rule as well.

## Validator
For each document the change adds or extends (a README, guide, design or decision record, runbook, change log, package documentation), take each added block of steps, commands, options, table rows or procedure, and grep the repository's other documents for its distinctive lines: commands, option names, table keys, headings. Open each document that matches and compare the material with the added block. Skip a copy that the project's documentation tooling requires in both places, a restatement inside the same document, and a conceptual or overview document that restates part of what reference documentation holds, to explain it. Validator question: **Does the change add to one document material that another document in the repository already holds, in place of a link or reference to that document?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: DOC-12`, severity suggestion, `file`, `symbol` = the heading of the added section, `code` = the first copied lines verbatim from the diff, `fix` = the copied block replaced by a one-line pointer with a link to the document that holds the material, in the file's format, with any step or value the copy adds or corrects moved into that document, `rationale` = the path of the document that already holds the material and the second place each later change to it would have to land).

## Source
- DOI 10.1109/ICSE.2019.00122, § IV.B Information Content (How), "Maintainability (21)" (fetched): "This category concerns issues related to the maintenance of documentation, e.g., how easy it is to apply changes or corrections to it. Just like in source code, duplicated content caused troubles for documentation maintainers, which were mostly resolved by replacing the clone with links and references. However, we noticed that documentation frameworks often make it hard to avoid duplicates."; abstract: "mined, analyzed, and categorized 878 documentation-related artifacts".
- DOI 10.1145/3377811.3380405, § 4 (RQ1), Information Content (How) (fetched): "Regarding Maintainability issues, practitioners considered superfluous content (55% of them) and clone/duplicate content (46%) the main sources of concern. This observation is in line with our previous study [2], which reports that these two subcategories are responsible for ∼71% of developers' discussions on maintainability of documentation."; abstract: "two surveys performed with 146 practitioners".
- google/styleguide, docguide/best_practices.md, § "Duplication is Evil" (fetched): "Do not write your own guide to a common Google technology or process. Link to it instead. If the guide doesn't exist or it's badly out of date, submit your updates to the appropriate directory or create a package-level README.md."
- Caveat: the papers classify mined discussions (21 maintainability artifacts) and survey answers (125 of 146 respondents from one company), not measured maintenance cost; the style-guide entry speaks of guides to a common technology or process.
