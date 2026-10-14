---
title: A document added to a repository sits in the project's documentation directory or is linked from the README or documentation index
rule_id: DOC-13
domain: docs
step: [document, review]
applies_to: [prose]
triggers: ['signal:added_file', '(?i)\b(wiki|confluence|notion[.]so|docs[.]google[.]com|sites[.]google[.]com)\b']
scope: callers
check_kind: mechanical
severity_default: minor
---

# A document added to a repository sits in the project's documentation directory or is linked from the README or documentation index

## Thesis
A document that a change adds to a repository sits in the project's documentation directory, or the README or the documentation index links to it. The project's own documentation that the change starts relying on and that is maintained outside the repository, such as a wiki page or a hosted site or document, is reachable through an obvious link from the README or the documentation index to that page or to the wiki, site or folder that holds it.

## Rationale
Of 138 documentation usability issues among 878 artifacts mined from mailing lists, question-and-answer discussions, issue repositories and pull requests, half (50%) concerned findability: the desired information was available but a user could not find it. Maintainers often handled these issues by giving users pointers to the documentation needed and, in some cases, by adding intra-documentation links. Placing documentation in a standard location was an effective practice to help users locate it; in one project a consolidated document was compiled into the docs/ folder because that location is much more prominent and easier to find. In a survey answered by 78 practitioners, 65% indicated accessibility and findability issues as important. The README provides critical information for people browsing the code, especially first-time users, and should at a minimum contain a link to the user- or team-facing documentation. A document that is neither in the standard location nor linked from the README or an index is information that is available but that a reader may fail to find; the rule gives every document a path from the places a reader starts.

## Example
```rust
bad:  // Backoff schedule: https://wiki.example.com/retry-policy
      // (neither README.md nor the docs index links this wiki)
      const MAX_RETRIES: u32 = 5;
good: // Backoff schedule: docs/retry-policy.md
      const MAX_RETRIES: u32 = 5;
```

## Limits
A document placed in the project's standard documentation directory meets the rule without a link of its own, because placing documentation in a standard location helps users locate it. Documentation kept outside the repository need not move into it: an obvious link from the README to its location meets the rule. A link to a page the project does not maintain, such as a dependency's reference documentation, a specification or an encyclopedia article, is a citation rather than project documentation kept elsewhere and needs no README link. A README added for a package sits in that package's top-level directory rather than in the documentation directory, where it is displayed to people browsing that directory. A document outside the documentation directory that a document under that directory links to also meets the rule, because that intra-documentation link gives it a path from the places a reader starts.

## Validator
List the files the change adds and keep the documents among them: Markdown, reStructuredText, AsciiDoc or plain-text pages such as guides, design documents, decision records and runbooks; skip a README added at the top of a package. Grep the hunk for links that the change adds to code, configuration or prose and that point to the project's own documentation on a wiki, a hosted document or a documentation site. For each added document, check whether its path lies under the project's documentation directory (the docs/ folder or the directory the documentation site builds from). For a document outside it and for each external page, open the callers at their state after the change: the top-level README, the README of the package the document sits in, and the documentation index (a table of contents, a site navigation or sidebar configuration, an index page); grep them, and for an added document also the files under the documentation directory, for the document's path or file name, and for an external page, for its URL or the URL of the wiki, site or folder that holds it. Validator question: **Does the change add a document outside the documentation directory, or start relying on a page of the project's own documentation kept outside the repository, that neither the README, the documentation index nor a document under the documentation directory links to, directly or through a link to the wiki, site or folder that holds it?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: DOC-13`, severity minor, `file`, `symbol`, `code` = the added document's path or the line that adds the external link, quoted verbatim from the diff, `fix` = the document's new path under the documentation directory, or the README or index line that links the document, the external page or the wiki, site or folder that holds it, `rationale` = names the document or page that no README or index link reaches).

## Source
- DOI 10.1109/ICSE.2019.00122, § IV.B, 'Usability (138)' (fetched): "Half of the issues (50%) were related to information findability, i.e., when the desired information was available but couldn't be found by a user [...] Developers often handle these issues by providing users with pointers to the documentation needed. In some cases, they go further [...] by adding more intra-documentation links"; "Placing documentation in standard locations is an effective practice to help users locating it, e.g., 'the consolidated document [...] is compiled into the 'docs/' folder, because as you already said, this location is much more prominent and easier to find'"; abstract: "878 documentation-related artifacts stemming from four different sources, namely mailing lists, [question-and-answer site] discussions, issue repositories, and pull requests".
- DOI 10.1145/3377811.3380405, Figure 2 and the Usability discussion (fetched): "issues related to accessibility/findability and information organization are considered important by practitioners (65% and 49% of them, respectively)"; "146 answers to our surveys, 78 to Survey-I"; "'% important' reports the percentage of surveyed practitioners that indicated the related issue as an important one".
- google/styleguide docguide/READMEs.md (fetched): "At a minimum, your `README.md` file should contain a link to your user- and/or team-facing documentation."; "README files provide critical information for people browsing your code, especially first-time users."; "`README.md` files should be located in the top-level directory for your product or library's actual codebase."; "The contents of the file are displayed in GitHub and Gitiles when you view the contents of the containing directory."
- google/styleguide docguide/best_practices.md, item 7 'Other external docs' (fetched): "Some teams maintain documentation in other locations, separate from the code, such as Google Sites, Drive, or wiki. If you do maintain documentation in other locations, you should clearly point to those locations from your project directory (for example, by adding an obvious link to the location from your project's `README.md`)."
- Caveat: the counts measure how often findability problems are reported and how practitioners rate them; no source measures the effect of a single link on a reader.
