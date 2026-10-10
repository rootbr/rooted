---
title: A secret such as a password, token or private key never reaches a process as a command-line argument, so the program accepts no secret through a flag and passes none in a child process's arguments
rule_id: TOOL-25
domain: tooling
step: [design, implement]
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
      secret = args.password_file.read_text(encoding="utf-8").strip()
      subprocess.run(["client", "--password-stdin"], input=secret, text=True, check=True)
```

## Limits
A flag whose value locates the secret, such as a file path, a descriptor number or a switch to read standard input, is the correct form, and so is a prompt for the secret. A flag whose name contains a secret word but whose value is not sensitive, such as a key identifier or a token lifetime, is outside the rule, which concerns sensitive arguments. The rule covers the argument vector only: environment variables are visible to other processes on certain platforms as well, and whether the environment is an acceptable channel for a secret is outside this rule. The exposure the evidence documents is to other users on the same system. The rule concerns only the channel that carries the secret; how the program decodes the file or stream it reads the secret from is judged on its own.

## Validator
Grep the hunk for a flag or option definition whose name carries password, passwd, passphrase, secret, token, api key, private key or credential, for a property defined on the command line with such a name, and for a process-start call whose argument list mentions such a value. Open the hunk around each hit. For a definition, read what the flag's value is: the secret itself, or a path, a descriptor number or a switch to read standard input. For a process start, read each element of the argument list, and of any command string built for a shell, in the hunk and check whether a secret value or a variable holding one is among them. Validator question: **Does the hunk define a flag whose value is the secret itself, or start a process with a secret value among its command-line arguments?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: TOOL-25`, severity major, `file`, `symbol`, `code` = the flag definition or the process-start line that carries the secret, verbatim from the diff, `fix` = the flag replaced by one that takes a file path or a switch to read standard input, and the secret handed to the child through standard input or a file descriptor, in the file's language, `rationale` = names that other users on the same system can list the process's command line and read the secret in it).
