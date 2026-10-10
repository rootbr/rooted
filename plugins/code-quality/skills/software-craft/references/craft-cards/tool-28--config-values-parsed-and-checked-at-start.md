---
title: Each configuration value is parsed and checked when the program starts, including one first used by error handling or fail-over code
rule_id: TOOL-28
domain: tooling
step: [implement, handle-errors]
applies_to: [universal]
triggers: ['\b(?:os[.](?:Getenv|LookupEnv|getenv)\s*\(|os[.]environ\b|System[.](?:getenv|getProperty)\s*\(|process[.]env[.]|env::var(?:_os)?\s*\()|[.]get(?:int|float|boolean|Int|Integer|Long|Boolean|Bool|String|Duration|Property)\s*\(\s*["\x27]|(?i:\b(?:config|conf|cfg|settings|props|properties)\s*(?:[.]get\w*\s*\(|\[\s*["\x27]))']
scope: callers
check_kind: semantic
severity_default: major
---

# Each configuration value is parsed and checked when the program starts, including one first used by error handling or fail-over code

## Thesis
During initialisation, before it starts to serve requests or workloads, the program reads, converts and checks each configuration setting it will use against the constraints its later use imposes, including a setting that only error handling or fail-over code consumes, and reports a setting that fails its check at that point. The check reaches as many settings as start-up can check; a setting whose check depends on runtime input or workload is beyond it.

## Rationale
Lazy use parses and consumes a setting only when an operation needs it, with no systematic check at initialisation. An error in a setting that start-up never touches then stays latent until error handling or fail-over runs, and it can break the failure handling it configures. In six mature, widely deployed systems, 14.0%–93.2% of the studied reliability, availability and serviceability settings had no special code that checked their correctness at initialisation; their correctness was verified implicitly when the value was used, for example in a file open call. Of the studied settings, 12.0%–38.6% were not used at all during initialisation, and 4.7%–38.6% had no early check of any kind, which left them subject to latent errors. In one storage company's customer configuration issues, latent errors were fewer than errors detected at start-up, yet they made up 75% of the high-severity issues and took much longer to diagnose. Administrators typically do not run a comprehensive suite of tests against configuration settings, especially hard-to-test failure-handling ones, so early detection falls to the program itself, at start-up. Checkers that emulate each value's later use, invoked at the end of initialisation, detected 75+% of the real-world latent configuration errors evaluated. The property restored is that an error surfaces before the configuration is put online, where an operator can correct it, rather than in the failure it was meant to handle.

## Example
```rust
bad:  fn on_failure() { let dir = env::var("DUMP_DIR").unwrap(); write_dump(Path::new(&dir)); }
      fn main() { serve(); }
good: struct Config { dump_dir: PathBuf }
      fn load_config() -> Result<Config, String> {
          let dump_dir = PathBuf::from(env::var("DUMP_DIR").map_err(|e| format!("DUMP_DIR: {e}"))?);
          let probe = dump_dir.join(".dump-check");
          fs::write(&probe, b"").and_then(|()| fs::remove_file(&probe)).map_err(|e| format!("DUMP_DIR {} is not writable: {e}", dump_dir.display()))?;
          Ok(Config { dump_dir })
      }
      fn main() { let config = load_config().unwrap_or_else(|e| { eprintln!("{e}"); process::exit(2) }); serve(&config); }
```

## Limits
A check at start-up cannot catch an error that arises after the check and before the use, such as a file checked at start and deleted later; running the checks periodically in a separate thread can catch that case. A check that emulates a value's later use misses an error that shows only in execution depending on runtime input or workload. It also misses a legal misconfiguration, a valid value that does not deliver the intended behaviour, such as an insufficient heap size or a too small timeout, which often shows up late as well. The measured shares come from reliability, availability and serviceability settings, and the study notes that latent errors are not limited to those components. The study covers checking in the initialisation phase, from the program's entry point to the point it starts to serve requests or workloads; a setting reloaded while the program runs is outside this rule.

## Validator
Grep the hunk for a read of a configuration value: a lookup in the environment, a flag lookup, a getter on a configuration or properties object, or an index into a settings map. For each read, open the routine that contains it and its callers, and decide whether it runs during start-up, before the program serves its first request, or only later, in a request, error handling, fail-over, backup, recovery or error-logging path. When it runs later, trace whether a start-up routine already reads, converts and checks the same key for what this later code does with it, such as writing into a path rather than only finding it, and passes the checked value down. Skip a read inside a routine that reloads the configuration while the program runs, and a read whose check needs a runtime input. Validator question: **Does the hunk first parse or check a configuration value in code that runs only after start-up, with no start-up routine that reads the same key and checks it for what that later code does with it?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: TOOL-28`, severity major, `file`, `symbol`, `code` = the late read of the configuration value, quoted verbatim from the diff, `fix` = a start-up routine in the file's language that reads, converts and checks the key, reports an error naming it, and passes the checked value to the later code, `rationale` = names the key, the late path that first reads it, such as error handling or fail-over, and the failure an invalid value would cause there).
