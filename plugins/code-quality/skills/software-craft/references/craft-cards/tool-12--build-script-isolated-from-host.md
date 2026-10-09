---
title: A change to a build or check script reaches no tool or input through a host-specific absolute path or system binary, derives no output from timestamps or build ids, and does not write into the source tree
rule_id: TOOL-12
domain: tooling
step: [implement, review]
applies_to: [build-config]
triggers: ['(?:/home/|/Users/)[\w.-]+/', '[A-Za-z]:[\\/]+(?:Users|Program Files)', '/usr/(?:local/)?bin/(?!env\b)', '\$\{?(?:HOME|USER|USERNAME|USERPROFILE)\b', '\$\(date\b|\bdate\s+\+%']
scope: hunk
check_kind: mechanical
severity_default: minor
---

# A change to a build or check script reaches no tool or input through a host-specific absolute path or system binary, derives no output from timestamps or build ids, and does not write into the source tree

## Thesis
A change to a build or check script keeps the build isolated from the host it runs on: the script reaches each tool and input through the checked-out source tree, a tool the build manages, or an explicitly listed host tool rather than a system binary or an absolute path that differs across hosts, creates each file deterministically from the build's inputs rather than from a build id or timestamp, and writes its outputs outside the source tree during the build, so the same input source and product configuration return the same output.

## Rationale
A build isolated from changes to its host returns the same output whenever it is given the same input source code and product configuration. System binaries that differ across hosts, such as binaries under a system binary directory and absolute paths, tooling that creates files non-deterministically, usually involving build ids or timestamps, and writing to the source tree during the build are common sources of non-hermeticity. A write into the source tree also fixes that tree for the target built first, so a later build of another target from the same tree may fail. A build isolated this way is good for troubleshooting because the exact conditions that produced it are known. Where an exact copy of a previously built item might need to be rebuilt, the supporting tools and the build instructions need to be under configuration control so the correct versions of the tools stay available. A catalog of 79 continuous-integration bad smells, compiled from interviews with 13 experts and more than 2,300 mined developer question-and-answer posts, highlights the abuse of shell scripts among them and advises practitioners to favor specific, portable tools over hacking.

## Example
```python
bad:  protoc = "C:/Users/dev/bin/protoc.exe" if os.name == "nt" else "/usr/local/bin/protoc"
      subprocess.run([protoc, "--python_out=src", "api.proto"])
      subprocess.run("cp $HOME/conf/app.toml dist/app-$(date +%s).toml", shell=True)
good: protoc = os.path.join(TOOLS_DIR, "protoc")
      subprocess.run([protoc, f"--python_out={OUT_DIR}", "api.proto"])
      shutil.copy("conf/app.toml", os.path.join(OUT_DIR, f"app-{COMMIT}.toml"))
```

## Limits
A host tool the build lists explicitly satisfies the rule: running the build in a container that holds only the checked-out source tree and that explicit list of host tools turns any implicit system dependency into a build breakage. An interpreter line that finds its interpreter through the environment lookup names the host tool the script runs under and satisfies the rule. The hash with which the code repository identifies a set of code mutations identifies the build's input, unlike a build id or timestamp, so a file named from it changes only when that input changes. The rule reaches writes made during the build; a step run on request outside the build, such as one that rewrites sources in place, is outside it. A directory reserved for the build's outputs that holds no version-controlled file, such as the build tool's conventional output directory, is the build's output directory and outside the source tree, even where it lies inside the checkout. Pinning dependency versions and the design of integration and delivery pipelines are outside this rule.

## Validator
Grep the hunk of each changed build or check script (a build file, a task-runner or integration configuration, a script the build invokes) for an absolute path under a system binary directory (other than the environment lookup an interpreter line starts with) or under a user's home directory, a reference to a home or user-name environment variable or to a build-number or run-id variable, a date or time call, and an output destination (an output flag or setting, the target of a copy, move or redirection, a file opened for writing). For each hit, read the enclosing statement in the hunk and decide whether the path reaches a tool or input outside the checked-out tree, the build's managed tools and its explicit list of host tools; whether the time value or a build id names or fills a file the build creates; and whether an output path of the step resolves inside the source tree. Validator question: **Does the changed build or check script reach a tool or input through a host-specific absolute path or system binary, create a file from a timestamp or build id, or write a build output into the source tree?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: TOOL-12`, severity minor, `file`, `symbol`, `code` = the changed line with the host path, the time- or id-derived file name or the source-tree output, quoted verbatim from the diff, `fix` = the same step in the file's language reaching the tool through the build's managed or explicitly listed tools, naming the file from a build input such as the source's commit hash, and writing into the build's output directory, `rationale` = which source of non-hermeticity the line adds and that the same source and configuration then no longer return the same output on another host or for another target).

## Source
- Bazel documentation, "Hermeticity", bazelbuild/bazel docs/basics/hermeticity.mdx, § Overview, § Benefits, § Identifying non-hermeticity, § Troubleshooting non-hermetic builds (fetched): "When given the same input source code and product configuration, a hermetic build system always returns the same output by isolating the build from changes to the host system." · "Hermetic build systems treat tools as source code. They download copies of tools and manage their storage and use inside managed file trees." · "Hermetic builds are good for troubleshooting because you know the exact conditions that produced the build." · "Actions or tooling that create files non-deterministically, usually involving build IDs or timestamps * System binaries that differ across hosts (such as `/usr/bin` binaries, absolute paths, [...]) * Writing to the source tree during the build. This prevents the same source tree from being used for another target. The first build writes to the source tree, fixing the source tree for target A. Then trying to build target B may fail." · "Code repositories, such as Git, identify sets of code mutations with a unique hash code. Hermetic build systems use this hash to identify changes to the build's input." · "Execute a build within a docker container that contains nothing but the checked-out source tree and explicit list of host tools. Build breakages and error messages will catch implicit system dependencies."
- SWEBOK V3.0 ch. 6 §6.1 "Software Building", ligurio/swebok-v3 6_software_configuration_management.md (fetched): "It might be necessary to rebuild an exact copy of a previously built software configuration item. In this case, supporting tools and associated build instructions need to be under SCM control to ensure availability of the correct versions of the tools."
- DOI 10.1007/s10664-019-09785-8, abstract as reproduced in the neverworkintheory review (fetched): "leveraging semi-structured interviews of 13 experts and mining more than 2,300 [...] posts. As a result, we compiled a catalog of 79 CI bad smells [...] the study also highlights uncovered bad practices, e.g., related to static analysis tools or the abuse of shell scripts [...] favor specific, portable tools over hacking, and do not ignore nor hide build failures".
- Caveat: the documentation lists common sources of non-hermeticity from a build-system migration guide and gives no measured rate; the catalog's advice on portable tools is general and does not single out host paths.
