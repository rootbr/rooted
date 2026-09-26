# fixture — Rejection Report

## Summary
- Raw findings submitted to verification: 54
- Confirmed (in review report): 53
- Rejected: 0
- Downgraded: 1
- Modified: 17
- Flagged for the author: 0

## Rejected Findings

None.

## Downgraded Findings

### SEC-04.1: An external command runs through ProcessBuilder or exec(String[]) with each argument as its own element, never through Runtime.exec(String) or a shell -c string _(critical → major)_
- **Original severity**: Critical
- **Rule**: `SEC-04`
- **Verdict**: Downgraded
- **Evidence**: (1) `git show 1fbf1e1:src/main/java/com/example/app/UserLookup.java`, lines 34-45: no comment marks line 40 as intentional. The line 12 Javadoc says "every parameter arrives from the request". Line 44 `convertAvatarSafely` is the argument-list control. (2) `git log -3 -- UserLookup.java` gives only "1fbf1e1 head: seeded defects and controls", which names no deliberate choice. `.claude/reviewing-java/config.md` at head tolerates only `Stats#sample`. (3) `git diff 73246a6 1fbf1e1` shows a new file with line 40 added. `git grep convertAvatar` finds no callers and no guard. (4) `javap -c -p java.lang.Runtime` on the installed JDK 21.0.10: `exec(String)` calls `exec(String,String[],File)`, which calls `new StringTokenizer(command)` and then `exec(String[],...)`. The argv is therefore always [sh, -c, 'convert, <filename tokens>, avatar.png']. (5) I ran that exact argv through /bin/sh (dash) and bash with the filenames `cat.jpg`, `x; echo INJECTED`, `$(echo${IFS}INJECTED)`, `x';echo${IFS}INJECTED;'` and `-i --rcfile /dev/null -x`. Every run printed "Syntax error: Unterminated quoted string" (dash) or "unexpected EOF while looking for matching `''" (bash) and exited 2. None printed INJECTED. The filename showed up only as $0 in the error prefix and was never parsed as code or as a shell option. (6) The fix compiles: `ProcessBuilder(String...)` exists and `start()` throws the declared IOException. ImageMagick 6 wand/convert.c lines 604-605 read the argument after `--` as the input file. In ImageMagick 7, option.c line 651 declares `{ "--", 1L, NoImageOperatorFlag, MagickTrue }` and operation.c lines 4927-4928 handle `--` like `-read`. So the `--` adds no defect in the ImageMagick 6 and 7 sources I opened. I could not open IM7's legacy `ConvertImageCommand`, which the `convert` name dispatches to (404, and GitHub API access is not enabled for this session), so that path is unchecked.

