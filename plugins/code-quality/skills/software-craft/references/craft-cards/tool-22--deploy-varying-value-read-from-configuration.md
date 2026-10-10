---
title: An IP address, a URL or an absolute file path that differs between the environments the program runs in is read from the environment, a flag or a configuration file rather than written into the code
rule_id: TOOL-22
domain: tooling
step: [implement]
applies_to: [universal]
triggers: ['(?<![\w.])(?:25[0-5]|2[0-4]\d|1?\d?\d)(?:[.](?:25[0-5]|2[0-4]\d|1?\d?\d)){3}(?![\w.])', '["''](?:https?|wss?|ftp|jdbc:\w+|postgres(?:ql)?|mysql|mongodb(?:\+srv)?|redis|amqps?)://', '["''](?:/(?:home|Users|opt|var|etc|srv|mnt|data|tmp|usr)/|[A-Za-z]:(?:\\|/))', '(?i)\b\w*(?:host(?:name)?|endpoint|ur[li]|addr(?:ess)?)\w*\s*(?::=|[:=])\s*["''][^"'']+["'']']
scope: file
check_kind: semantic
severity_default: minor
---

# An IP address, a URL or an absolute file path that differs between the environments the program runs in is read from the environment, a flag or a configuration file rather than written into the code

## Thesis
An IP address, a URL or an absolute file path whose value differs between the environments the program runs in (development, test, staging, production, or another host or network) is supplied at run time through the environment, a flag or a configuration file rather than written into the code as a literal, inline or bound to a named constant.

## Rationale
An IP address written into the code embeds infrastructure configuration in the application. Any change to the network environment, such as moving a service to a different host or scaling horizontally, then requires a code modification and a full redeployment, which prevents operational teams from making infrastructure adjustments independently and slows down incident response; every hard-coded occurrence must be found and updated, and developers fix the code instead of an operations team updating a configuration file. The address is the same in every environment the application runs in, which makes it difficult to point development, staging and production at different infrastructure without modifying the source code, and an application with hard-coded IP addresses can become impossible to deploy in some cases. A hard-coded URL or path makes the program hard to test: a given absolute path may not exist in a specific test environment, an Internet URL may not be available when the tests run, production filesystems usually differ from the development one, and path literals are not always portable across operating systems. Supplied as a customizable parameter, the value can differ per environment without a modification of the source code.

## Example
```go
bad:  const serviceURL = "http://10.0.3.17:8080/orders"
      const exportPath = "/var/lib/orders/export.csv"
      resp, err := http.Get(serviceURL)
good: serviceURL := os.Getenv("SERVICE_URL")
      exportPath := os.Getenv("EXPORT_PATH")
      resp, err := http.Get(serviceURL)
```

## Limits
The rule reaches only a value that has to change when the program runs in another environment; a value that every environment the program runs in, test included, needs unchanged is outside it. Well-known special-purpose addresses do not represent configurable infrastructure endpoints and are exempt: the broadcast address 255.255.255.255, the non-routable address 0.0.0.0, strings of the form 2.5.<number>.<number>, which often match object identifiers, and the documentation ranges 192.0.2.0/24, 198.51.100.0/24, 203.0.113.0/24 and 2001:db8::/32. Static analyzers disagree on loopback: one exempts the whole 127.0.0.0/8 range as not a configurable endpoint, another reports 127.0.0.1 as not recommended. A loopback address is exempt when it names the program's own host in every environment the program runs in, and in scope when it stands for a service that another environment reaches on another host. A constant relative path of at most two parts, such as the endpoint path /user/friends resolved against a base URL, is exempt, and so is a constant path joined to a base directory or base URL that the program reads from the environment, a flag or a configuration file; a file path that starts at the filesystem root is an absolute pathname and stays in scope however few parts it has. A literal that is only the fallback of a value the program reads from the environment, a flag or a configuration file is outside the rule, since a deployment replaces it without a code modification. Where the value is read is a separate concern: code outside the entry point and the one configuration module receives it as an argument or field, and the entry point or that module reads and checks it at start-up from the environment, a flag or a configuration file.

## Validator
Grep the added lines of the hunk for a four-octet IPv4 literal, a quoted URL with a network or database scheme, a quoted absolute path under a home, system or data directory or a drive letter, and a quoted string assigned to a name containing host, endpoint, url, uri or addr. Drop each match that is one of the exempt addresses or paths in Limits; keep a loopback address for the question below. Open the file around each remaining match and trace the literal to its use, following a named constant to the lines that read it: note whether it is used directly or is only the fallback of a value read from an environment variable, a flag or a configuration-file key, and whether the value would differ on another host, network or environment, test included. Validator question: **Does the hunk add an IP address, URL or absolute path literal outside the exempt forms whose value differs between environments and which the program uses with no environment variable, flag or configuration-file key through which a deployment can replace it?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: TOOL-22`, severity minor, `file`, `symbol`, `code` = the line holding the address, URL or path literal, `fix` = that line reading the value from an environment variable, a flag or a configuration-file key, in the file's language, `rationale` = the environments the value differs between and the code modification and redeployment that changing it now requires).
