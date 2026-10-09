---
title: A dependency a change adds names the intended package as published in its registry, not a misspelling of a popular name or a name that does not exist
rule_id: TOOL-11
domain: tooling
step: [implement, document, review]
applies_to: [build-config, prose]
triggers: ['^\s*"[@\w./-]+"\s*:\s*"(\^|~|>=?|<=?|=)?\s*v?\d', '^\s*[\w-]+\s*=\s*("[\^~=<>]?\s*\d+([.]\d+|")|\{[^}]*\bversion\s*=)', '^\s*["'']?[A-Za-z][\w.-]*(\[[\w,.-]+\])?\s*(==|>=|~=|<=|!=|<|>)\s*\d', '<artifactId>[^<]+</artifactId>|^\s*(require\s+)?[\w.-]+[.][a-z]{2,}/[\w./-]+\s+v\d+[.]\d+', '\b(npm|pnpm|yarn|bun)\s+(install|i|add)\s+(-\S+\s+)*[@\w]', '\b(pip3?\s+install|uv\s+(add|pip\s+install)|poetry\s+add|cargo\s+add|go\s+get)\s+[\w@.-]', '^\s*[A-Za-z][\w-]*\s*[(=]?\s*["''][\w.-]+:[\w.-]+:']
scope: callers
check_kind: semantic
severity_default: major
---

# A dependency a change adds names the intended package as published in its registry, not a misspelling of a popular name or a name that does not exist

## Thesis
A package name that a change adds to the ecosystem's manifest or to an install command names the package the change intends to use: a package the ecosystem's registry publishes under exactly that name, and not a name that looks much like a popular package's name standing in for that package. A name the registry holds is not yet proof, because an attacker may already have published a package under it.

## Rationale
Attackers publish malicious packages under names that look much like those of popular packages, so that a typing error or a visual similarity installs their package instead of the legitimate one the developer intended to use (typosquatting). Code assistants may suggest package names that do not exist, and attackers publish malicious packages under exactly those names (slopsquatting); such a name looks completely legitimate, which makes it harder to detect. In 30 tests, code-generating language models produced 2.23 million packages, of which 440,445 (19.7%) were hallucinations, references to packages that do not exist, covering 205,474 distinct non-existent package names. Once an attacker has published a malicious package under such a name, installing it compromises the system silently. Against slopsquatting, the guard is to confirm, before installing, that the registry holds the name, and then to check the package's download count, its source repository with genuine code, commits and contributors, and its release history: legitimate packages have thousands or millions of downloads, while newly published malicious ones have very few.

## Example
```typescript
bad:  // npm install node-fetch-promise
      import fetch from "node-fetch-promise";
      export const load = (url: string) => fetch(url);
good: // npm install node-fetch
      import fetch from "node-fetch";
      export const load = (url: string) => fetch(url);
```

## Limits
A name that resembles a popular package's name is correct when it is itself the legitimate package the change intends to use; the defect is a name that installs some other package in place of the intended one. The rule reaches the names a hunk adds to a manifest or to an install command; a name declared before the change is outside its scope. Registry-side defences, resolution between an internal and a public registry, and verification of artifact signatures or checksums are supply-chain design and outside this rule's scope.

## Validator
Grep the hunk for dependency entries added to the ecosystem's manifest and for install or add commands added to scripts, documentation or CI configuration. For each package name the hunk adds, look the name up in the registry the ecosystem resolves from, through the package manager's view or info command or the registry's package page: confirm that a package is published under exactly that name, and read its download count where the registry reports one, its source repository and its release history. Compare the name with popular packages that serve the same purpose, looking for the marks of a typing error or a visual similarity: a dropped, doubled or swapped character, a changed separator, an added prefix or suffix. Trace the imports in the changed code to the name and confirm that the package's published description matches what the code uses it for. Validator question: **Does the hunk add a package name that the registry does not publish, or one that resembles a popular package's name without being the package the code intends to use?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: TOOL-11`, severity major, `file`, `symbol`, `code` = the added manifest entry or install command, verbatim, `fix` = the same entry or command naming the intended package as the registry publishes it, `rationale` = names whether the registry lacks the name or which popular package the name resembles).

## Source
- OWASP Cheat Sheet Series, NPM Security Cheat Sheet, §10 'Understanding typosquatting and slopsquatting attacks' (fetched): "bad actors publish malicious modules to the npm registry with names that look much like existing popular modules. These malicious packages exploit common typing errors or visual similarities to trick developers into installing them instead of the legitimate packages they intended to use."; "When developers ask AI tools [...] to suggest packages, these models may hallucinate package names that do not actually exist. Attackers monitor these hallucinations and publish malicious packages with those exact names"; "making it harder to detect since the suggested name looks completely legitimate"; "If an attacker has already published a malicious package under that hallucinated name, installing it compromises your system silently."; "To protect against slopsquatting: [...] Run `npm view <package-name>` before installing any AI-suggested package to confirm it exists."; "legitimate packages have thousands or millions of downloads while newly published malicious ones have very few"; "Verify the package has a real GitHub repository with genuine code, commits and contributors."; "Be suspicious of packages created very recently with no release history."
- arXiv:2406.10279 (relayed: quoted verbatim in the guide below, its references [josephspracklen2024e] and [josephspracklen2024a]): "These 30 tests generated a total of 2.23 million packages in response to our prompts, of which 440,445 (19.7%) were determined to be hallucinations, including 205,474 unique non-existent packages (i.e. packages that do not exist in PyPI or npm repositories [...])"; definition: "Package hallucination occurs when an LLM generates code that recommends or contains a reference to a package that does not actually exist."
- OpenSSF, Security-Focused Guide for AI Code Assistant Instructions, supply-chain instructions (fetched): "Do not add dependencies that may be malicious or hallucinated."
- Caveat: the evidence observes the npm and PyPI registries; the cheat sheet reports that similar typosquatting attacks "have been observed on the PyPi Python registry as well".
