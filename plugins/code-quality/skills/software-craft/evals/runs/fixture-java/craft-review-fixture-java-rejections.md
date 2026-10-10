# fixture-java — Rejection Report

## Summary
- Raw findings submitted to verification: 48
- Confirmed (in review report): 46
- Rejected: 0
- Downgraded: 2
- Modified: 7
- Flagged for the author: 0

## Rejected Findings

None.

## Downgraded Findings

### JAVA-53.1: An external command runs through ProcessBuilder or exec(String[]) with each argument as its own element, never through Runtime.exec(String) or a shell -c string _(critical → major)_
- **Original severity**: Critical
- **Rule**: `JAVA-53`
- **Verdict**: Downgraded
- **Evidence**: Opened the file at head (`git show a224c33:src/main/java/com/example/app/UserLookup.java`). Line 40 holds `return Runtime.getRuntime().exec("sh -c 'convert " + uploadedFile + " avatar.png'");`. Lines 35-45 carry no comment calling the pattern intentional, and line 12 has the class doc "every parameter arrives from the request", so the value comes from outside the code.

`git log -3` on the file prints one line, `a224c33 head: seeded defects and controls`. That commit message names no deliberate choice. The project context lists no tolerance for external commands.

`git diff 5333531..a224c33` shows the file as newly added, so line 40 is part of the diff. The neighbouring `UserLookup#convertAvatarSafely` (line 44) does not guard `convertAvatar`.

I read JDK 21 `src.zip` `java/lang/Runtime.java:482-491`. There `exec(String)` builds a `StringTokenizer` on the whole string and passes the tokens on as `cmdarray`.

I compiled and ran my own `Tok.java` in `scratchpad/skeptic-java53`, outside the repo, with `uploadedFile = "x.png; touch /tmp/pwned"`. It printed the tokens `[sh] [-c] ['convert] [x.png;] [touch] [/tmp/pwned] [avatar.png']`. The same file compiled `new ProcessBuilder("convert", "--", uploadedFile, "avatar.png")` and printed `[convert, --, x.png; touch /tmp/pwned, avatar.png]`.

The card's Limits ("a value from outside the code") and its Validator ("a string that a shell or a whitespace tokenizer will split") both match this line.

### PROJ-3.1: Repositories prefer constructor injection _(major → minor)_
- **Original severity**: Major
- **Rule**: `PROJ-3`
- **Verdict**: Downgraded
- **Evidence**: I opened `OrderService.java` at head (`git show a224c33:src/main/java/com/example/app/OrderService.java`). The file is wholly added in the diff, and lines 13-14 contain `@Autowired private Repo repo;` next to a constructor that takes only `Formatter` (lines 19-21). No comment marks the pattern as intentional. The only commit touching the file is `a224c33 head: seeded defects and controls`, and its message names no deliberate choice. I opened `Repo.java` at head: it takes its `DataSource` through its constructor (lines 11-15). I opened `.claude/software-craft/config.md` at head; invariant 3 reads "Repositories prefer constructor injection: Repository classes should take their dependencies through the constructor. Violation: a field-injected repository (`@Autowired` on a field)." The rest of the config states no tolerance for field injection. `git grep` for `OrderService` and `@Autowired` across the head tree found no caller of `new OrderService(` and no test sources; the tree is ten production files plus the config. The proposed fix compiles: `Repo` and `Formatter` are in the same package, and both final fields are assigned in the one constructor. Spring autowires that single constructor implicitly, so the fix introduces no defect; the `Autowired` import is left unused.

