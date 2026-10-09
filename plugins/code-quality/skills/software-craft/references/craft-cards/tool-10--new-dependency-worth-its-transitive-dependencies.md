---
title: A new dependency is added only when the functionality it supplies is worth the transitive dependencies it brings in
rule_id: TOOL-10
domain: tooling
step: [design, implement, review]
applies_to: [build-config]
triggers: ['^\s*"[@\w./-]+"\s*:\s*"(\^|~|>=?|<=?|=)?\s*v?\d', '^\s*[\w-]+\s*=\s*("[\^~=<>]?\s*\d+[.]\d+|\{[^}]*\bversion\s*=)', '^\s*["'']?[A-Za-z][\w.-]*(\[[\w,.-]+\])?\s*(==|>=|~=|<=|!=|<|>)\s*\d', '^\s*(require\s+)?[\w.-]+[.][a-z]{2,}/[\w./-]+\s+v\d+[.]\d+', '<artifactId>[^<]+</artifactId>', '\b(implementation|api|compileOnly|runtimeOnly|testImplementation)\s*\(?\s*["''][\w.-]+:[\w.-]+']
scope: callers
check_kind: semantic
severity_default: minor
---

# A new dependency is added only when the functionality it supplies is worth the transitive dependencies it brings in

## Thesis
A package added to the manifest for trivial functionality — a package of at most 35 lines of code and McCabe complexity at most 10 — is taken only when it brings no packages of its own into the project's dependency tree, which the change's lock-file diff shows or, where the project keeps no lock file, the package's own published manifest; otherwise those few lines are written in the project's own code.

## Rationale
Every package the manifest reaches, directly or transitively, becomes part of the implicitly trusted code base, and the risks an added package brings can propagate through multiple levels of dependencies. The transitive count grows faster than the direct count: in one large registry, installing an average package introduces implicit trust in 79 third-party packages and 39 maintainers, and a small, linear increase in direct dependencies leads to a significant, super-linear increase in transitive ones. Typical problems in packaging ecosystems are backward-incompatible package updates and the risk of transitively depending on packages that have become obsolete or inactive; in another large registry, 75.1% of 723,444 dependency relationships are not needed to compile and run the code, and 57% of all relationships are such unneeded transitive dependencies. Trivial packages make up 16.8% of the studied packages of the first registry; only 45.2% of them have tests, though they appear deployment-tested and have test, usage and community interest similar to non-trivial packages, while 11.5% of them have more than 20 dependencies, so the choice of a trivial package needs care. No tooling eliminates the risk involved in reusing code, so the strongest mitigation is a small dependency tree, kept by preferring a bit of copying to adding a new dependency. Where the project keeps a lock file, it describes the exact tree that was generated, and its diff makes the tree changes an added package brings visible in source control.

## Example
```python
bad:  dependencies = [
          "pad-text>=1.0",  # 18 lines, 4 packages of its own
      ]
      from pad_text import pad_left
good: def pad_left(text: str, width: int, fill: str = " ") -> str:
          return text.rjust(width, fill)
```

## Limits
When the package supplies substantial code the project would otherwise write, reuse pays off: libraries that leverage dependencies deliver four times more code than their own while adding only a 4% delay to the time interval between their releases, though libraries with such leverage have 1.6 times higher odds of being vulnerable than libraries with lower leverage. Such a package is selected after its code and tests are evaluated for reuse, since reused software often carries the same or better quality requirements as newly developed software. The separating condition is the size of what the package supplies: a package of at most 35 lines of code and McCabe complexity at most 10 is trivial, and the figures on tests and dependencies were measured on that class. The rule reaches a package the change adds; a declared package the code no longer uses, an imported package left undeclared and a version with a known vulnerability lie outside it.

## Validator
Grep the hunk for a line added to the ecosystem's manifest that declares a new package. Open the lock-file diff of the same change and list the packages that enter with it; where the project keeps no lock file, list the dependencies the package's own published manifest declares. Open the call sites that import the new package and read what the code uses from it; judge from the package's published source or metadata whether it is at most 35 lines of code with McCabe complexity at most 10. Validator question: **Does the change add a package of at most 35 lines of code and McCabe complexity at most 10 that brings packages of its own into the project's dependency tree?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: TOOL-10`, severity minor, `file`, `symbol`, `code` = the added manifest line verbatim, `fix` = the few lines that replace the package at its call site, in the file's language, `rationale` = the package's size and the packages it adds to the project's dependency tree).

## Source
- arXiv:1902.09217, §1 and §4.1.1 (fetched): "Installing an average npm package introduces an implicit trust on 79 third-party packages and 39 maintainers"; "a small, linear increase in direct dependencies leads to a significant, super-linear increase in transitive dependencies"; "each directly or transitively depended on package becomes part of the implicitly trusted code base".
- DOI 10.1109/MSR.2017.55, abstract (fetched): "adding a package to a project can also introduce risks, which can propagate through multiple levels of dependencies"; "developers should look more carefully into their dependencies to understand what exactly is included."
- arXiv:1710.04936, abstract (fetched): "Typical problems are backward incompatible package updates, and the risk of (transitively) depending on packages that have become obsolete or inactive."
- arXiv:2001.07808, DOI 10.1007/s10664-020-09914-8, abstract and RQ1 results (fetched): "We analyze 9,639 Java artifacts hosted on Maven Central, which include a total of 723,444 dependency relationships"; "543,610 (75.1%) of all dependencies are bloated, they are not needed to compile and run the code"; "412,288 (57%) are bloated-transitive dependencies".
- DOI 10.1145/3106237.3106267, abstract (fetched), with the study's trivial-package definition as a published review of the paper restates it (fetched): "no more than 35 lines of code and a McCabe complexity score no greater than 10"; "making up 16.8% of the studied npm packages"; "only 45.2% of trivial packages even have tests. However, trivial packages appear to be `deployment tested' and to have similar test, usage and community interest as non-trivial packages"; "11.5% of the studied trivial packages have more than 20 dependencies. Hence, developers should be careful about which trivial packages they decide to use."
- Go project documentation, "How Go Mitigates Supply Chain Attacks", §"A little copying is better than a little dependency" (fetched): "preferring a bit of copying to adding a new dependency"; "The label “zero dependencies” is proudly worn by high-quality reusable Go modules"; "it can’t eliminate the risk involved in reusing code, so the strongest mitigation will always be a small dependency tree."
- npm CLI documentation, package-lock.json (fetched): "It describes the exact tree that was generated"; "Facilitate greater visibility of tree changes through readable source control diffs."
- DOI 10.1109/ICSE43902.2021.00125, abstract (fetched): "by using free open-source software (FOSS) libraries a developer leverages on other people's code to multiply the offered functionalities with a much smaller own codebase"; "leverage pays off as leveraged libraries only add a 4% delay in the time interval between library releases while providing four times more code than their own"; "1.6 higher odds of being vulnerable in comparison to the libraries with lower leverage".
- SWEBOK Guide V3.0 ch. 3 §3.6 "Construction with Reuse" (fetched): "Reused and off-the-shelf software often have the same - or better - quality requirements as newly developed software"; "The selection of the reusable units"; "The evaluation of code or test reusability."
- Caveat: the trust, super-linear and trivial-package figures come from the npm registry, the bloat figures from Maven Central and the leverage figures from Maven-based libraries; the 35-line and McCabe-10 bound is the study's definition of a trivial package, not a measured break-even point.
