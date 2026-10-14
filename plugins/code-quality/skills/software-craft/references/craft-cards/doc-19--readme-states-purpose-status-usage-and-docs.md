---
title: A package or repository README states what the code is for, its maintenance or release status, how to start using it, and where the rest of its documentation is, inline or by link
rule_id: DOC-19
domain: docs
step: [document, review]
applies_to: [prose]
triggers: ['signal:added_file', '(?i)^\s*#{2,3}\s+(usage|installation|install|status|about|overview|getting started|documentation)\s*$', '(?i)\b(deprecated|unmaintained|no longer maintained|experimental|archived|retired|development status :: 7 - inactive|not for (general|production) (release|use))\b']
scope: file
check_kind: semantic
severity_default: suggestion
---

# A package or repository README states what the code is for, its maintenance or release status, how to start using it, and where the rest of its documentation is, inline or by link

## Thesis
The README at the top-level directory of a code package or repository includes, or points to, four items: what the code is and what it is used for; its status, such as deprecated or not for general release; how to use it, for example through sample code or a copyable command; and links to the rest of its documentation. The README stays up to date with that status: a change that deprecates or retires the whole package updates the README's status in the same change. A README added at the top-level directory of a code package or repository that carries one of the four items neither inline nor by link fails the rule, and so does a change that deprecates or retires the package while leaving the README's status as it was.

## Rationale
A README is often the first item a visitor sees in a repository; it shapes a developer's first impression of the repository and documents the project the repository hosts, and it gives people browsing the code, especially first-time users, critical information. An up-to-date README is especially important for a package that provides interfaces to other teams. In a manual annotation of 4,226 README sections from 393 randomly sampled GitHub repositories, information on the What and How of a repository was very common, while many README files lacked information on its purpose and status. Changing the documentation in the same change as the code keeps it fresh.

## Example
```java
bad:  String readme = """
          ## Status
          Experimental.
          """;
good: String readme = """
          Parser reads records from a file. Status: experimental.
          ## Usage
          new Parser().parse(path)
          Further documentation: docs/index.md
          """;
```

## Limits
Pointing counts: a README that links to the page stating an item carries that item, so a README made only of links and a README with an inline quick start can both satisfy the rule. The rule reaches the README at the top-level directory of a code package or repository; a README in a directory that is not a code package is outside it. Points of contact, also on the package-level README list quoted in the Source, are outside this rule. A change that deletes or deprecates code inside a package that stays in use leaves the package's status unchanged, so whether its documentation changes is a reviewer's judgement and outside the deprecation half of the rule.

## Validator
On a hunk that adds a README at the root of a code package or repository, open the file at file scope and read it for the four items: what the code is and what it is used for, its status, how to use it, and links to further documentation. Read for purpose and status first, the two items many READMEs lack. Count a link whose text or target names an item as carrying that item. On a hunk that marks the whole package or repository deprecated, archived or retired, through a deprecation notice, a package-metadata status or an archive note, trace whether the same change carries a hunk that states the new status in that package's README or in the package's page that the README links for its status. Validator question: **Does an added package or repository README carry one of the four items neither inline nor by link, or does a change that deprecates or retires the whole package leave its README's status unchanged?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: DOC-19`, severity suggestion, `file`, `symbol`, `code` = the README's heading lines or the deprecation line, quoted verbatim from the diff, `fix` = the missing purpose, status, usage or documentation-link lines, or the updated status line, written in the README's markup, `rationale` = which of the four items is missing or which status went stale, and that a README is often a visitor's first contact with the code).

## Source
- DOI 10.1007/s10664-018-9660-3, abstract (fetched, via a GitHub-hosted review page): "README files play an essential role in shaping a developer's first impression of a software repository and in documenting the software project that the repository hosts [...] manual annotation of 4,226 README file sections from 393 randomly sampled GitHub repositories [...] information discussing the 'What' and 'How' of a repository is very common, while many README files lack information regarding the purpose and status of a repository."
- Google documentation guide, docguide/READMEs.md, § Overview, § Where to put your README, § What to put in your README (fetched): "README files provide critical information for people browsing your code, especially first-time users." "All top-level directories for a code package should have an up-to-date `README.md` file. This is especially important for package directories that provide interfaces for other teams." "Every package-level `README.md` should include or point to the following information: [...] What is in this package or library and what's it used for. [...] Points of contact. [...] Status of whether this package or library is deprecated, or not for general release, etc. [...] How to use the package or library. Examples include sample code, copyable `bazel run` or `bazel test` commands, etc. [...] Links to relevant documentation."
- Google documentation guide, docguide/best_practices.md, § Update Docs with Code (fetched): "Change your documentation in the same CL as the code change. This keeps your docs fresh".
- Google engineering practices, review/reviewer/looking-for.md, § Documentation (fetched): "If the CL deletes or deprecates code, consider whether the documentation should also be deleted."
- GitHub Docs, 'About READMEs' (fetched): "A README is often the first item a visitor will see when visiting your repository."
- Caveat: the study describes what GitHub README files contain, not the cost of a missing item; the four-item list is a documentation guide's convention, not a measured threshold.
