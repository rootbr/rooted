---
title: A benchmark or timing run measures the optimized release build, not an unoptimized debug build, unless the problem measured occurs only in the debug build
rule_id: PRF-27
domain: performance
step: [test]
applies_to: [build-config]
triggers: ['\btarget[/\\]debug[/\\]|\b(hyperfine|time|perf\s+stat)\b.*\bcargo\s+run\b(?!.*(--release|--profile))|CMAKE_BUILD_TYPE[=:\s"]+Debug\b|(?<![\w-])-O0\b|\bopt-level\s*=\s*0\b|\[profile[.]bench\]|\bDisableOptimizationsValidator\b|\bJitOptimizationsValidator[.]DontFailOnError\b|(\s-c|--configuration)\s+Debug\b']
scope: file
check_kind: semantic
severity_default: minor
---

# A benchmark or timing run measures the optimized release build, not an unoptimized debug build, unless the problem measured occurs only in the debug build

## Thesis
A benchmark, a profiling run or an ad-hoc timing whose numbers stand for the code's running time measures the optimized release build, the build compiled with optimizations for the program given to users. A development or debug build compiled with optimization off, such as optimization level 0 or a debug configuration, gives less accurate numbers and is rebuilt in release before it is timed. The one exception is a performance problem that occurs only in the debug build, which may be measured there.

## Rationale
Optimizations make code run faster but lengthen compilation, which is why a toolchain keeps two profiles: one for development, rebuilt quickly and often, and one for the final program given to a user, which runs as fast as possible. In one toolchain's documented defaults the development profile is the default for the plain build command and sets optimization level 0, so a timing taken on the default build measures unoptimized code. The release build inlines function calls and constants and prunes unused code paths; the debug build lacks these optimizations, so its performance numbers are less accurate, and for CPU-intensive calls the two builds may differ considerably. Release-build numbers taken without the debugger attached are the most precise and accurate and closer to the end-user experience, since the debugger itself changes performance times. Benchmark harnesses build the rule in: one fails validation by default for a benchmark built without optimization and asks that it be built in release, and another prints a warning that timings may be affected when its library was built as debug.

## Example
```java
bad:  new ProcessBuilder("cargo", "build").inheritIO().start().waitFor();
      Process timing = new ProcessBuilder("hyperfine", "target/debug/app").start();
good: new ProcessBuilder("cargo", "build", "--release").inheritIO().start().waitFor();
      Process timing = new ProcessBuilder("hyperfine", "target/release/app").start();
```

## Limits
A harness whose default benchmark profile inherits the release settings already measures the optimized build and needs no flag. A performance problem that occurs only in the debug build may be measured in the debug build. A debug build run under the debugger may help narrow down a performance problem with breakpoints and code stepping; whether a CPU-bound problem exists is then checked in the release build. File I/O and network responsiveness problems look much the same in both builds; considerable differences may arise for CPU-intensive calls. Benchmarking an interpreter built from source follows the same rule: an interpreter benchmark suite's guidance for stable benchmarks compiles the interpreter with link-time and profile-guided optimization, the default of that suite's compile command.

## Validator
Grep the hunk for a run of a development-profile output path (`target/debug/`), a timer wrapped around a run command with no release flag, `CMAKE_BUILD_TYPE=Debug` or `-O0`, `opt-level = 0` or a benchmark profile section, a disabled optimization validator, or `-c Debug` / `--configuration Debug`. Open the file and decide whether the command or configuration builds or runs a benchmark, a profiling session or a timing whose numbers are reported or compared; a debug build used only for tests or stepping is outside the rule. Trace the build the measurement uses: the profile or configuration it selects, what that profile inherits, and the optimization level it ends at. Look for a stated reason that the problem measured occurs only in the debug build. Validator question: **Does a benchmark, profiling or timing run in the hunk measure a build with optimization off, for a problem that is not confined to the debug build?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: PRF-27`, severity minor, `file`, `symbol`, `code` = the command or configuration line that selects the unoptimized build for the measurement, `fix` = the same line selecting the release build or an optimized profile, in the file's language, `rationale` = the measured build lacks the optimizations of the shipped build, so its numbers misstate the code's running time).

## Source
- rust-lang/book main, src/ch01-03-hello-cargo.md, §Building for Release (fetched): "The optimizations make your Rust code run faster, but turning them on lengthens the time it takes for your program to compile. This is why there are two different profiles: one for development, when you want to rebuild quickly and often, and another for building the final program you’ll give to a user that won’t be rebuilt repeatedly and that will run as fast as possible. If you’re benchmarking your code’s running time, be sure to run `cargo build --release` and benchmark with the executable in _target/release_."
- MicrosoftDocs/visualstudio-docs main, docs/profiling/running-profiling-tools-with-or-without-the-debugger.md (fetched): "Tools that appear in the Performance Profiler run without the debugger, typically on release builds" / "Release build performance numbers in the Performance Profiler are the most precise and accurate. These tools give you results closer to the end-user experience." / "the debugger itself changes performance times, as it does necessary debugger operations like intercepting exception and module load events." / "there may be scenarios where using the debugger in a debug build may help to narrow down the performance problem, especially if you want to use debugger features such as breakpoints and code stepping." / "Release builds provide optimizations like inlining function calls and constants, pruning unused code paths, and storing variables in ways that can't be used by the debugger. Performance numbers in debug builds are less accurate, because debug builds lack these optimizations." / "For performance problems caused by CPU-intensive calls, there might be considerable performance differences between release and debug builds. Check to see whether the CPU performance issue exists in release builds." / "External performance problems, like file I/O or network responsiveness issues, won't look much different in a release build or a debug build." / "If the problem occurs only with debug builds, you probably don't need to run the tools with release builds."
- dotnet/BenchmarkDotNet master, src/BenchmarkDotNet/Validators/JitOptimizationsValidator.cs and src/BenchmarkDotNet/Configs/DefaultConfig.cs (fetched): "Benchmark was built without optimization enabled (most probably a DEBUG configuration). Please, build it in RELEASE." / `yield return JitOptimizationsValidator.FailOnError;`
- google/benchmark main, README.md §Debug vs Release and src/reporter.cc (fetched): "By default, benchmark builds as a debug library. You will see a warning in the output when this is the case." / "***WARNING*** Library was built as DEBUG. Timings may be affected."
- rust-lang/cargo master, doc/book/src/reference/profiles.md, §dev and §bench (fetched): "It is the default for build commands like `cargo build`" / `[profile.dev] opt-level = 0` / "The `bench` profile is the default profile used by `cargo bench`." / `[profile.bench] inherits = "release"`
- python/pyperformance main, doc/usage.rst, §How to get stable benchmarks (fetched): "Compile Python using LTO (Link Time Optimization) and PGO (profile guided optimizations): use the pyperformance compile command with uses LTO and PGO by default"
- Caveat: these are toolchain documentation and harness behaviour; none gives a slowdown ratio, so the size of the gap depends on the workload.
