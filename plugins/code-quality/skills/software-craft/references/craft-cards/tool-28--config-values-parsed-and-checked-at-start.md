---
title: Each configuration value is parsed and checked when the program starts, including one first used by error handling or fail-over code
rule_id: TOOL-28
domain: tooling
step: [implement, handle-errors, review]
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

## Source
- "Early Detection of Configuration Errors to Reduce Failure Damage", OSDI 2016 (USENIX), pp. 619–634, Abstract (fetched, https://raw.githubusercontent.com/tianyin/tianyin.github.io/master/pub/pcheck.pdf): "many (14.0%–93.2%) of these configurations do not have any special code for checking the correctness of their settings at the system’s initialization time" · "the errors become latent until their manifestations cause severe damage, such as breaking the failure handling" · "The checkers emulate the late execution that uses configuration values" · "[the tool] can help systems detect 75+% of real-world LC errors at the initialization phase".
- Same paper, §1.3 (fetched): "six mature, widely-deployed software systems" · "Many (12.0%–38.6%) of these configuration parameters are not used at all during system initialization" · "4.7%–38.6% of these critically important configuration parameters do not have any early checks and are thereby subject to LC errors".
- Same paper, §2.2 Finding 1 and footnote 2 (fetched): "the correctness is verified (implicitly) when the parameters’ values are actually used in operations such as a file open call" · "adopt the lazy practice of using configuration values — parsing and consuming configuration settings only when the values are immediately needed for the operations, without any systematic configuration checking at the system’s initialization phase" · "A system’s initialization phase is defined from its entry point to the point it starts to serve user requests or workloads".
- Same paper, §2.2, Table 4 and Figure 3b (fetched): "rely on the usage code for verifying correctness, because their initial checks are either missing or incomplete" · "for more complicated parameters, some checking is incomplete" · "though the initial checking code covers file existence and types, it misses other constraints such as file permissions" · "one configuration parameter could have multiple subtle constraints depending on how the system uses its value".
- Same paper, §1.1 and Tables 1–2 (fetched): "errors in their settings go undetected until their late manifestation, e.g., under circumstances like error handling and fail-over" · "a major storage company in the US" · "Although there have been fewer LC errors than non-latent ones, LC errors contribute to 75% of the high-severity issues and take much longer to diagnose" · "system administrators typically do not perform a comprehensive suite of test cases against configuration settings, especially for those hard-to-test ones (e.g., failure/error-handling related configurations)" · "the system should automatically check as many configurations as possible at its early stages (the startup time)" · "if detected earlier, the errors can be corrected immediately before the configurations are put online for production".
- Same paper, §3 and footnote 4 (fetched): "invokes these checkers at the end of the system initialization phase" · "A TOCTTOU (Time-Of-Check-To-Time-Of-Use) error occurs after the checking phase and before the use phase, e.g., inadvertently deleting a file that had been checked early but will be used later on" · "supports running checkers periodically in a separate thread".
- Same paper, §5 Limitations (fetched): "It cannot detect legal misconfigurations" … "that have valid values but do not deliver the intended system behavior" · "(e.g., insufficient heap size and too small timeout)" · "often manifested in a latent fashion as well" · "cannot emulate the execution that depends on runtime inputs/workloads" · "it would miss the configuration errors that are only manifested during such execution".
- Caveat: the shares were measured on reliability, availability and serviceability settings of six open-source server systems; §2, in its introduction before §2.1, notes "LC errors are not limited to RAS components".
