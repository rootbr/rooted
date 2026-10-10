---
title: A secret such as a password, token or private key never reaches a process as a command-line argument, so the program accepts no secret through a flag and passes none in a child process's arguments
rule_id: TOOL-25
domain: tooling
step: [design, implement, review]
applies_to: [universal]
triggers: ['(?i)\b(?:flag[.]\w+|add_argument|option|arg|Arg::new|long|longOpt|addOption|String\w*)\s*\(\s*(?:&\w+\s*,\s*)?(?:["''][\w-]*["'']\s*,\s*)?["'']-{0,2}[\w-]*(?:password|passwd|passphrase|pwd|secret|token|api[_-]?key|private[_-]?key|credential)', '(?i)["''](?:[^"''\n]*\s)?--?(?:password|passwd|passphrase|secret|token|api-?key|private-?key|credentials?)\b', '(?i)\b(?:exec\w*|spawn\w*|system(?=\s*\()|Command::new|ProcessBuilder|subprocess[.]\w+|Popen)\b.*\b(?:password|passwd|passphrase|secret|token|api_?key|private_?key|credentials?)\b', '(?i)-D[\w.]*(?:password|secret|token)\w*=']
scope: hunk
check_kind: mechanical
severity_default: major
---

# A secret such as a password, token or private key never reaches a process as a command-line argument, so the program accepts no secret through a flag and passes none in a child process's arguments

## Thesis
A secret such as a password, token or private key never reaches a process as a command-line argument. No flag of the program takes the secret as its value, and no child process the program starts receives the secret among its command-line arguments; a flag through which the secret is supplied carries only where to read it from, such as a file path, a file descriptor number or a switch to read standard input.

## Rationale
Many operating systems let a user list information about processes that other users own, command-line arguments included; when an argument carries a credential, those users may take it and launch an attack against the product or the resources it reaches. On Linux the default procfs mode lets everybody access every `/proc/<pid>/` directory, and the hidepid mode that protects a process's `cmdline` against other users is not the default. A password defined as a property on the command line at start-up may be displayed in the process list. Hiding the argument after start-up is not enough, because the value is still visible for a moment before it is cleared. The exposure is the same when the program starts another process: a password included in a process call lets local users obtain it, and an access token passed as a command-line parameter is visible to other processes via the process listing. A file, a file descriptor fed by a pipe, or standard input delivers the secret instead, and the flag that selects one of them carries only a path, a descriptor number or a switch.

## Example
```python
bad:  parser.add_argument("--password")
      subprocess.run(["client", "--password", args.password], check=True)
      subprocess.run(["java", f"-Ddb.password={args.password}", "-jar", "app.jar"], check=True)
good: parser.add_argument("--password-file", type=pathlib.Path, required=True)
      secret = args.password_file.read_text().strip()
      subprocess.run(["client", "--password-stdin"], input=secret, text=True, check=True)
```

## Limits
A flag whose value locates the secret, such as a file path, a descriptor number or a switch to read standard input, is the correct form, and so is a prompt for the secret. A flag whose name contains a secret word but whose value is not sensitive, such as a key identifier or a token lifetime, is outside the rule, which concerns sensitive arguments. The rule covers the argument vector only: environment variables are visible to other processes on certain platforms as well, and whether the environment is an acceptable channel for a secret is outside this rule. The exposure the evidence documents is to other users on the same system.

## Validator
Grep the hunk for a flag or option definition whose name carries password, passwd, passphrase, secret, token, api key, private key or credential, for a property defined on the command line with such a name, and for a process-start call whose argument list mentions such a value. Open the hunk around each hit. For a definition, read what the flag's value is: the secret itself, or a path, a descriptor number or a switch to read standard input. For a process start, read each element of the argument list, and of any command string built for a shell, in the hunk and check whether a secret value or a variable holding one is among them. Validator question: **Does the hunk define a flag whose value is the secret itself, or start a process with a secret value among its command-line arguments?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: TOOL-25`, severity major, `file`, `symbol`, `code` = the flag definition or the process-start line that carries the secret, verbatim from the diff, `fix` = the flag replaced by one that takes a file path or a switch to read standard input, and the secret handed to the child through standard input or a file descriptor, in the file's language, `rationale` = names that other users on the same system can list the process's command line and read the secret in it).

## Source
- CWE-214 'Invocation of Process Using Visible Sensitive Information', Description, Extended Description, Demonstrative Example 1, Observed Examples (CWE-CAPEC/REST-API-wg json_repo/W/214.json) (fetched): "Many operating systems allow a user to list information about processes that are owned by other users. Other users could see information such as command line arguments or environment variable settings. When this data contains sensitive information such as credentials, it might allow other users to launch an attack against the product or related resources."; "If the property is defined on the command line when the program is invoked (using the -D... syntax), the password may be displayed in the OS process list."; CVE-2023-38994 "includes LDAP password in a process call, allowing local users to obtain the password"; CVE-2021-32638 "passes access tokens as a command-line parameter or through an environment variable, making them visible to other processes via the ps command."
- curl documentation, option `--user` (curl/curl docs/cmdline-opts/user.md) (fetched): "On systems where it works, curl hides the given option argument from process listings. This is not enough to protect credentials from possibly getting seen by other users on the same system as they still are visible for a moment before being cleared. Such sensitive data should be retrieved from a file instead or similar and never used in clear text in a command line."; "If you specify only the username, curl prompts for a password."
- OpenSSL openssl-passphrase-options(1) (openssl/openssl doc/man1/openssl-passphrase-options.pod) (fetched): "pass:password ... Since the password is visible to utilities (like 'ps' under Unix) this form should only be used where security is not important."; "env:var ... Since the environment of other processes is visible on certain platforms ... this option should be used with caution."; "file:pathname Reads the password from the specified file"; "fd:number Reads the password from the file descriptor number. This can be useful for sending data via a pipe"; "stdin Reads the password from standard input."
- Linux kernel Documentation/filesystems/proc.rst, mount option hidepid (fetched): "hidepid=off or hidepid=0 means classic mode - everybody may access all /proc/<pid>/ directories (default)."; "hidepid=noaccess or hidepid=1 ... Sensitive files like cmdline, sched*, status are now protected against other users."
- Caveat: the evidence documents the exposure mechanism and individual incidents, not an incidence rate.
