---
title: A resource acquired for one loop iteration or one step of a routine is released when that iteration or step ends, not held until the enclosing routine returns
rule_id: ERR-22
domain: errors
step: [implement, refactor]
applies_to: [universal]
triggers: ['^\s*defer\s+([\w.]+[.](Close|Release|Stop|Rollback|Remove)|cancel\w*)\(', '[.]enter_(async_)?context\(|\bstack[.](defer|adopt|use)\(', '(?<![=!<>])=\s*(await\s+)?(new\s+\w*(InputStream|OutputStream|Reader|Writer|Socket|Channel|Scanner)\b|([\w.:]*[.:])?(open|openSync|urlopen|connect|getConnection|createConnection|createReadStream|createWriteStream|Open|Create|OpenFile|CreateTemp|Dial|DialContext)\s*\()', '^\s*(async\s+)?with\s+.+\bas\s+\w+|\btry\s*\(\s*(final\s+)?[\w.<>]+\s+\w+\s*=|\b(await\s+)?using\s+\w+\s*=']
scope: file
check_kind: semantic
severity_default: major
---

# A resource acquired for one loop iteration or one step of a routine is released when that iteration or step ends, not held until the enclosing routine returns

## Thesis
A file, a socket, a connection, a stream, a temporary file or a cancellation function is released promptly once the code that uses it is done with it. A resource acquired in each iteration of a loop is released within that iteration, and a resource used by one step of a longer routine is released when that step ends: the language's scoped-release construct encloses that step alone, or an explicit release follows it. Where the language's deferred release runs when the enclosing routine returns rather than when the enclosing block ends, a release deferred inside a loop body holds every iteration's resource until the routine returns; the loop body then moves into a routine of its own, so that its deferred release runs as each call returns.

## Rationale
Files, sockets and resources that use sockets internally, such as database connections, may consume limited system resources such as file descriptors, and code that deals with many of them may exhaust those resources unnecessarily if they are not returned to the system promptly after use. Holding files open may also prevent other actions, such as moving or deleting them, or unmounting a filesystem. Removing a temporary file once it is no longer required lets its name and its storage be recycled, and calling a cancellation function releases the resources associated with its context, so code should call it as soon as the operations running in that context complete. The scoped-release construct releases its resource when the block that declares it exits, which ensures prompt release and avoids the resource-exhaustion errors that may otherwise occur; where the language releases a value at the closing brace of the block that owns it, a step enclosed in a block of its own, or a value dropped explicitly before the end of its scope, is released before the rest of the routine runs. A deferred release that runs before the routine returns is not executed at the end of each loop iteration but at the end of the routine, so a release deferred inside a loop is a possible resource leak; in a loop that ends only when the channel it receives from is closed, those deferred calls do not run until that channel is closed. Moving the loop body into a routine called once per iteration makes each deferred release run when that call returns, at the end of the iteration.

## Example
```rust
bad:  let file = File::open(path)?;
      let config = parse(&file)?;
      serve(config) // the file stays open while serve runs
good: let config = {
          let file = File::open(path)?;
          parse(&file)?
      };
      serve(config)
```

## Limits
A resource that is not local to one section of code is outside the rule: one the routine returns, assigns to a field, or hands to another routine or object that takes over its release (a call that only reads or writes through it does not hand it over), and a shared resource the program opens once and keeps, such as a database handle that maintains its own pool of idle connections and rarely needs closing; a connection borrowed from that pool is returned to it after use and stays inside the rule. A resource acquired once before a loop and used by every iteration belongs to the whole loop and is released after it. A set of resources handled together, such as a set of files entered into one cleanup stack inside a single scoped-release block, is held until that block ends, and that block ends when the work on the set ends. An object that implements the closing interface but holds no releasable resource, such as a stream in a form not based on input-output, in general needs no scoped release. Release on the paths an error takes and the order in which several resources are released are judged by their own rules; a lock and any resource shared across threads are outside the rule.

## Validator
Grep the added lines for a release deferred to routine exit, a resource entered into a cleanup stack, an acquisition assigned to a variable — an open, a connect or a dial, the construction of a stream, reader, writer, socket or channel — and the opening of a scoped-release block. Open the file and find the loop and the routine that enclose each hit. For a deferred release, check whether it runs when the enclosing routine returns, and whether a loop inside that routine encloses it; a deferral inside a routine or function literal that the loop calls on each iteration runs when that call returns and passes. For an acquisition or a scoped-release block, find the resource's last use and trace what runs between it and the release: the remaining iterations of the loop, or later steps of the routine that do not use the resource — a long call, a wait, a move or delete of the same file. Skip a resource the routine returns, assigns to a field or hands to another routine or object that takes over its release, but not one it only passes to a call that reads or writes through it; a shared resource opened once and kept; a set of resources handled together in one block that ends when the work on the set ends; a resource acquired before a loop that every iteration uses and released when that loop ends; and an object that holds no releasable resource. Validator question: **Does an added line acquire a resource, enter it into a cleanup stack or defer its release so that it is released only when the enclosing routine returns or a wider block ends, while further loop iterations or later steps that do not use it run before that release?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: ERR-22`, severity major, `file`, `symbol`, `code` = the acquiring line, the cleanup-stack entry or the deferred release, quoted verbatim from the diff, `fix` = the iteration's or step's use of the resource moved into a scoped-release block or a routine of its own, or followed by an explicit release when the step ends, in the file's language, `rationale` = which resource stays held, the iterations or later steps that run while it is held, and what it ties up meanwhile — a file descriptor, a connection, a context, a file that cannot be moved or deleted).

## Source
- PEP 8, "Programming Recommendations" — "When a resource is local to a particular section of code, use a ``with`` statement to ensure it is cleaned up promptly and reliably after use. A try/finally statement is also acceptable." (fetched)
- Google Python Style Guide §3.11 "Files, Sockets, and similar Stateful Resources" — "Explicitly close files and sockets when done with them. This rule naturally extends to closeable resources that internally use sockets, such as database connections"; "They may consume limited system resources, such as file descriptors. Code that deals with many such objects may exhaust those resources unnecessarily if they're not returned to the system promptly after use."; "Holding files open may prevent other actions such as moving or deleting them, or unmounting a filesystem." (fetched)
- OpenJDK `java.lang.AutoCloseable` Javadoc (Java SE 21) — "The close() method of an AutoCloseable object is called automatically when exiting a try-with-resources block [...] This construction ensures prompt release, avoiding resource exhaustion exceptions and errors that may otherwise occur."; "It is possible, and in fact common, for a base class to implement AutoCloseable even though not all of its subclasses or instances will hold releasable resources."; "try-with-resources blocks are in general unnecessary when using non-I/O-based forms" (fetched)
- Effective Go, "Defer" — "Go's defer statement schedules a function call (the deferred function) to be run immediately before the function executing the defer returns."; "it's not block-based but function-based" (fetched)
- revive `defer`, option `loop` — "deferring inside loops can be misleading (deferred functions are not executed at the end of the loop iteration but of the current function)" (fetched)
- go-critic `deferInLoop` — "Possible resource leak, 'defer' is called in the 'for' loop"; the documented fix moves the loop body and its `defer f.Close()` into `func process(filename string)`, called once per iteration (fetched)
- Staticcheck SA9001 "Defers in range loops may not run when you expect them to" — "defers in this range loop won't run unless the channel gets closed" (fetched)
- Go `context.WithCancel` — "Canceling this context releases resources associated with it, so code should call cancel as soon as the operations running in this [Context] complete." (fetched)
- SEI CERT FIO03-J — "Removing temporary files when they are no longer required allows file names and other resources (such as secondary storage) to be recycled." (fetched)
- Rust book ch. 4.1 "What Is Ownership?" — "Rust calls `drop` automatically at the closing curly bracket."; ch. 15.3 "Running Code on Cleanup with the Drop Trait" — "you have to call the `std::mem::drop` function provided by the standard library if you want to force a value to be dropped before the end of its scope." (fetched)
- SpotBugs `OS_OPEN_STREAM` — "The method creates an IO stream object, does not assign it to any fields, pass it to other methods that might close it, or return it, and does not appear to close the stream on all paths out of the method." (fetched)
- Go `database/sql` — `Open`: "maintains its own pool of idle connections. Thus, the Open function should be called just once. It is rarely necessary to close a [DB]."; `DB.Conn`: "Every Conn must be returned to the database pool after use by calling [Conn.Close]." (fetched)
- Python `contextlib.ExitStack` — "a set of files may easily be handled in a single with statement"; "All opened files will automatically be closed at the end of the with statement" (fetched)
- Caveat: no source here measures how often a resource held past its use fails, so the card carries no rate; the loop-deferral sources are Go tool rules and documentation, and the card applies them wherever a deferred release runs at routine exit.
