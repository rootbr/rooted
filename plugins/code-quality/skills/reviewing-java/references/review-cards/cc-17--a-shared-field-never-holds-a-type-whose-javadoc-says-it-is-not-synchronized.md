---
title: A field shared between threads never holds a type whose Javadoc says it is not synchronized, such as SimpleDateFormat, HashMap, ArrayList or StringBuilder
rule_id: CC-17
domain: concurrency
triggers: ['SimpleDateFormat', 'DecimalFormat', 'new (HashMap|LinkedHashMap|TreeMap|HashSet|LinkedHashSet|ArrayList|LinkedList|ArrayDeque)<', 'StringBuilder\s+\w+\s*[=;]', 'static (final )?(Map|List|Set|Deque)<', 'volatile (Map|List|Set)<']
scope: file
check_kind: mechanical
severity_default: major
---

# A field shared between threads never holds a type whose Javadoc says it is not synchronized, such as SimpleDateFormat, HashMap, ArrayList or StringBuilder

## Thesis
An object reachable from more than one thread — a static field, a field of a singleton, a field of a request handler, an object handed to tasks — holds no instance of a type whose class Javadoc states it is not synchronized or not safe for multiple threads: `SimpleDateFormat` and `DecimalFormat`, `HashMap`, `ArrayList`, `HashSet` and the other plain collections, `StringBuilder`. Such a field holds a thread-safe alternative (`DateTimeFormatter`, `ConcurrentHashMap`, `CopyOnWriteArrayList`, a `Collections.synchronized*` wrapper with the wrapper's lock around compound calls), is created per thread or per call, or is accessed only under one lock.

## Rationale
These classes document the contract themselves: a date or decimal format "must be synchronized externally" if multiple threads access it, and separate instances per thread are recommended; a `HashMap` or `ArrayList` "must be synchronized externally" when at least one thread modifies it structurally; a `StringBuilder` is "not safe for use by multiple threads". Unsynchronized concurrent use breaks the object's internal invariants, and the corruption surfaces later as a wrong value, a missing entry or an exception far from the racing calls. Declaring the field `volatile` or `final` protects the reference, not the object it points to. `DateTimeFormatter` is documented "immutable and thread-safe" and replaces `SimpleDateFormat` outright.

## Example
```java
bad:  private static final SimpleDateFormat FMT = new SimpleDateFormat("yyyy-MM-dd");
      String stamp(Date d) { return FMT.format(d); }            // called from any thread
      private final Map<String, Session> sessions = new HashMap<>();
good: private static final DateTimeFormatter FMT = DateTimeFormatter.ISO_LOCAL_DATE;
      String stamp(LocalDate d) { return FMT.format(d); }
      private final Map<String, Session> sessions = new ConcurrentHashMap<>();
```

## Limits
Applies to an instance shared between threads. A local created and dropped inside one method, a `ThreadLocal<SimpleDateFormat>`, a field of a thread-confined or prototype-scoped object, and a collection populated once before publication and never modified afterwards are not flagged. A field whose every access sits inside one lock region on the same lock is correct. A `Collections.synchronized*` wrapper is thread-safe for single calls; compound calls and iteration still need the wrapper's lock. The per-call construction cost of a format is a performance note, not this finding.

## Validator
On the triggered hunk find each field or static declaration whose type is one of the named classes or a plain collection, and each use of such a field. Open the file: confirm the holder is shared — a static, a singleton, a handler, an object handed to tasks — and that the type's Javadoc states it is not synchronized; check for a lock enclosing every access, or for a modification after publication. Validator question: **can two threads call methods on this instance at the same time, at least one of them modifying it, with no lock enclosing both?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: CC-17`, severity major, `file`, `symbol`, `code` = the field declaration and one shared use quoted verbatim from the diff, `fix` = the thread-safe type, the per-thread or per-call instance, or the lock region, `rationale` quoting the type's own thread-safety statement).

## Source
`java.text.SimpleDateFormat` Javadoc, Java SE 21, "Synchronization" — "Date formats are not synchronized. It is recommended to create separate format instances for each thread. If multiple threads access a format concurrently, it must be synchronized externally"; `java.text.DecimalFormat` — the same wording for decimal formats. `java.util.HashMap` and `java.util.ArrayList` class Javadoc — "Note that this implementation is not synchronized. If multiple threads access [it] concurrently, and at least one of the threads modifies [it] structurally, it must be synchronized externally". `java.lang.StringBuilder` — "Instances of StringBuilder are not safe for use by multiple threads". `java.time.format.DateTimeFormatter` — "This class is immutable and thread-safe". SpotBugs `STCAL_STATIC_SIMPLE_DATE_FORMAT_INSTANCE`; SonarSource RSPEC-2885 "Non-thread-safe fields should not be static".
