# fixture Review

## Executive Summary
- Reviewed: `73246a6f8fc975c628969587a83c30c620fd9ed6...1fbf1e1ee5768a983e9a9854b6c7d297d7835e00` — 9 Java files (SMALL); packages: com.example.app
- Passes: 81 card jobs, 3 logic slices, 4 project invariants
- Findings: 54 (4 critical, 13 major, 14 minor, 23 suggestion)
- Verification: 54 raw findings → 53 confirmed, 1 downgraded, 0 rejected, 0 flagged for the author
- Recommendation: Block

## Critical & Major Findings

### PROJ-1.1: Cache values are loaded once
- **Severity**: Critical
- **Rule**: `PROJ-1` — project invariant from config.md
- **Location**: `src/main/java/com/example/app/Cache.java` · `Cache#getOrLoad`
- **Code**:
  ```java
          if (!cache.containsKey(key)) {
              cache.put(key, load(key));
          }
          return cache.get(key);
  ```
- **Problem**: `getOrLoad` runs a non-atomic check-then-act on the shared `cache` field, which is a ConcurrentHashMap used by every request thread. Two threads can ask for the same absent key at the same time. Both see `containsKey` return false, both call `load(key)`, and both call `put`, so the second put overwrites the first. Each thread then does a separate `cache.get(key)`, so the value a thread returns depends on which put landed last. It can be the other thread's value rather than the one it loaded. Using ConcurrentHashMap makes each call thread-safe on its own, but it does not make this sequence of three calls atomic.
- **Suggested fix**:
  ```java
  public String getOrLoad(String key) {
      return cache.computeIfAbsent(key, this::load);
  }
  ```
- **Rationale**: Invariant 1 (Cache values are loaded once) requires that a key two request threads ask for at the same time is loaded once and that both threads see the same value. This check-then-act allows the forbidden state under normal concurrent traffic: the key is loaded twice, and the second `put` replaces the first thread's value, so the value flips between the two threads. `ConcurrentHashMap#computeIfAbsent` runs the mapping function atomically, at most once per absent key, and every caller gets the one stored value. The per-call `HashMap` in `buildIndex` never leaves its method, so it falls outside this invariant and is correct.
- **Also flagged by**: CC-08

### SEC-06.1: A value written into an HTML or JavaScript response is encoded for the exact context it lands in, and HTML encoding is not JavaScript encoding
- **Severity**: Critical
- **Rule**: `SEC-06` — OWASP Cross Site Scripting Prevention Cheat Sheet — output encoding per context ("HTML Contexts", "HTML Attribute Contexts", "JavaScript Contexts": "the only 'safe' location for placing variables in JavaScript is inside a 'quoted data value'"; "Dangerous Contexts"); the interceptor anti-pattern — "JavaScript and HTML encoding are not interchangeable". OWASP ASVS 5.0 requirements 1.1.2, 1.2.1, 1.2.3. OWASP Java Encoder project README — "Contextual Output Encoding". CWE-79.
- **Location**: `src/main/java/com/example/app/OrderService.java` · `OrderService#render`
- **Code**:
  ```java
              return "<p>" + order + "</p>";
  ```
- **Problem**: When `forEmail` is true, `render` builds an HTML email body by concatenating the `order` parameter straight into `<p>` element content with no encoder. `order` is a non-constant String that callers pass into this public @Service method. Nothing in the repository encodes it before the call (git grep finds no Encode/escape call and no other caller), and nothing encodes it here. So the markup this method returns carries whatever `<`, `>`, `&`, `"` and `'` the order text contains.
- **Suggested fix**:
  ```java
  import org.owasp.encoder.Encode;
  
  public String render(String order, boolean forEmail) {
      if (forEmail) {
          return "<p>" + Encode.forHtml(order) + "</p>";
      }
      return order;
  }
  ```
- **Rationale**: The landing context is HTML element content, rendered as HTML by the mail client. Without HTML entity encoding, the order text's `<` and `>` open new tags, and `&`, `"` and `'` stay live. Any markup in the order (a `<script>`, an `<img onerror=...>`, a forged `<a href>`) is parsed as markup rather than shown as text (CWE-79, OWASP XSS Prevention Cheat Sheet, HTML Contexts). Encoding has to be the last step next to the output. This method is where the value becomes markup, so the encoder belongs here and not in some filter upstream that cannot know the output context.

### PROJ-4.1: Totals never go negative
- **Severity**: Critical
- **Rule**: `PROJ-4` — project invariant from config.md
- **Location**: `src/main/java/com/example/app/Totals.java` · `Totals#transfer`
- **Code**:
  ```java
              totals.merge(from, -amount, Integer::sum);
  ```
- **Problem**: The new `Totals#transfer` debits `from` by `amount` with no balance check and no guard on the sign of `amount`. If `from` is absent (null is treated as 0) or holds less than `amount`, the merge writes a negative balance for `from`. A negative `amount` does the same to `to`, through `(current == null ? 0 : current) + amount`. The method never rejects a transfer. The debit also runs as a nested `merge` inside `compute` on the same ConcurrentHashMap, which ConcurrentHashMap's contract forbids. So the check and the debit are not one atomic step for `from` either.
- **Suggested fix**:
  ```java
  public void transfer(String from, String to, int amount) {
      if (amount <= 0) {
          throw new IllegalArgumentException("transfer amount must be positive: " + amount);
      }
      // atomic check-and-debit on the source key; an exception leaves the mapping unchanged
      totals.compute(from, (key, current) -> {
          int balance = current == null ? 0 : current;
          if (balance < amount) {
              throw new IllegalStateException("transfer of " + amount + " would drive " + key + " below zero (balance " + balance + ")");
          }
          return balance - amount;
      });
      totals.merge(to, amount, Integer::sum);
  }
  ```
- **Rationale**: Invariant 4 (Totals never go negative) says `Totals#transfer` must reject any transfer that would drive a balance below zero. It names the forbidden state as a negative balance written by `Totals#transfer`. Here that state follows from ordinary use: any overdraft, such as transfer("a", "b", 10) when "a" holds 5 or does not exist, stores -5 or -10 for "a". The class feeds concurrent ingest workers, so the negative balance is stored and later reads pick it up. That is data corruption. Critical: this breaks the invariant's stated consequence under normal operation. Also, `TotalsTransferTest`, which the invariant names as its enforcer, does not exist at head. Only config.md mentions it, so no test catches this.

### SEC-01.1: A SQL query carrying untrusted data binds it as a parameter, never by concatenating it into the statement text
- **Severity**: Critical
- **Rule**: `SEC-01` — OWASP SQL Injection Prevention Cheat Sheet, "Defense Option 1: Prepared Statements (with Parameterized Queries)" — "the database will always distinguish between code and data, regardless of what user input is supplied", with the Java `PreparedStatement` and HQL named-parameter examples. OWASP Query Parameterization Cheat Sheet, Java and Hibernate examples. OWASP ASVS 5.0 requirement 1.2.4. CWE-89.
- **Location**: `src/main/java/com/example/app/UserLookup.java` · `UserLookup#findNameByEmail`
- **Code**:
  ```java
  ResultSet rs = st.executeQuery("select name from users where email = '" + email + "'")) {
  ```
- **Problem**: The `email` method parameter is concatenated into the SQL text and run through a plain `Statement.executeQuery`, so it becomes part of the SQL instead of a bound parameter. The class Javadoc says every parameter arrives from the request (the account endpoints), so an attacker controls this value.
- **Suggested fix**:
  ```java
  public String findNameByEmail(String email) throws SQLException {
      try (Connection c = dataSource.getConnection();
           PreparedStatement ps = c.prepareStatement("select name from users where email = ?")) {
          ps.setString(1, email);
          try (ResultSet rs = ps.executeQuery()) {
              return rs.next() ? rs.getString(1) : null;
          }
      }
  }
  ```
- **Rationale**: Concatenation removes the boundary between code and data. The database parses the request value as SQL, so an input like `x' or '1'='1` or a `UNION` clause changes what the query does and can read other users' rows. A `Statement` built from a concatenated string cannot bind anything. A `?` placeholder with `setString` defines the SQL first and passes the email later as a literal value.

### CC-04.1: A compound operation on lock-guarded state runs inside one lock region, not across two
- **Severity**: Major
- **Rule**: `CC-04` — `java.util.Collections#synchronizedList` Javadoc, Java SE 21 — "In order to guarantee serial access, it is critical that all access to the backing list is accomplished through the returned list"; "It is imperative that the user manually synchronize on the returned list when traversing it"; "Failure to follow this advice may result in non-deterministic behavior". jcstress sample `problems/racecondition/RaceCondition_02_CheckThenReact.java` — `Racy`: a check-then-set on a `volatile` flag, both actors enter the section in 12.36% of samples; `Sync`: the same under `synchronized (this)`, forbidden, zero samples. SEI CERT VNA03-J "Do not assume that a group of calls to independently atomic methods is atomic".
- **Location**: `src/main/java/com/example/app/Cache.java` · `Cache#getOrLoad`
- **Code**:
  ```java
          if (!cache.containsKey(key)) {
              cache.put(key, load(key));
  ```
- **Problem**: getOrLoad does a check-then-act on the shared `cache` field (a ConcurrentHashMap that every request thread uses, per the class Javadoc). It calls containsKey, then put, then get. Each call is atomic on its own, but nothing makes the three atomic together. Two threads asking for the same absent key can both see containsKey return false, both run load(key) and both call put. The later put overwrites the earlier one, so the following cache.get(key) can return a value this thread did not load. This breaks project invariant 1, 'Cache values are loaded once', which names exactly this violation: 'duplicate loads and a value that flips between the two'.
- **Suggested fix**:
  ```java
  public String getOrLoad(String key) {
      // one atomic check-and-insert on the concurrent map; load runs at most once per key
      return cache.computeIfAbsent(key, this::load);
  }
  ```
- **Rationale**: containsKey releases the map's internal lock before put takes it again. Another request thread can insert the same key in that gap, so put acts on the stale premise that the key is absent. The result is a duplicate load and a replaced value. The card's Limits name computeIfAbsent as the atomic call on a concurrent collection that needs no enclosing region. An external synchronized(cache) would not lock the ConcurrentHashMap's own internal locks.

### CC-17.1: A field shared between threads never holds a type whose Javadoc says it is not synchronized, such as SimpleDateFormat, HashMap, ArrayList or StringBuilder
- **Severity**: Major
- **Rule**: `CC-17` — `java.text.SimpleDateFormat` Javadoc, Java SE 21, "Synchronization" — "Date formats are not synchronized. It is recommended to create separate format instances for each thread. If multiple threads access a format concurrently, it must be synchronized externally"; `java.text.DecimalFormat` — the same wording for decimal formats. `java.util.HashMap` and `java.util.ArrayList` class Javadoc — "Note that this implementation is not synchronized. If multiple threads access [it] concurrently, and at least one of the threads modifies [it] structurally, it must be synchronized externally". `java.lang.StringBuilder` — "Instances of StringBuilder are not safe for use by multiple threads". `java.time.format.DateTimeFormatter` — "This class is immutable and thread-safe". SpotBugs `STCAL_STATIC_SIMPLE_DATE_FORMAT_INSTANCE`; SonarSource RSPEC-2885 "Non-thread-safe fields should not be static".
- **Location**: `src/main/java/com/example/app/Formatter.java` · `Formatter#recent`
- **Code**:
  ```java
  private final LinkedList<String> recent = new LinkedList<>();
  ...
  recent.add(value);
  ```
- **Problem**: Formatter keeps a plain LinkedList in an instance field. Its own Javadoc says it formats values for every response, and it is constructor-injected into the singleton @Service OrderService, so one instance serves every request thread. remember() changes the list's structure with recent.add(value), and recentAt() reads it with recent.get(index). No lock covers either call, so two request threads can use the list at the same time while at least one of them modifies it.
- **Suggested fix**:
  ```java
  private final List<String> recent = new CopyOnWriteArrayList<>();
  
  public String recentAt(int index) {
      return recent.get(index);
  }
  
  public void remember(String value) {
      recent.add(value);
  }
  
  // or keep LinkedList and put every access under one lock:
  // private final Object lock = new Object();
  // public String recentAt(int i) { synchronized (lock) { return recent.get(i); } }
  // public void remember(String v) { synchronized (lock) { recent.add(v); } }
  ```
- **Rationale**: The java.util.LinkedList Javadoc says: "Note that this implementation is not synchronized. If multiple threads access a linked list concurrently, and at least one of the threads modifies the list structurally, it must be synchronized externally." If two add calls race, they can corrupt the node links and the size count. A concurrent get can then return a wrong element, or throw far from the calls that raced. Declaring the field final protects only the reference, not the list it points to.

### REL-48.1: A long-lived collection that gains an entry per request, session or key has a bound or an eviction rule
- **Severity**: Major
- **Rule**: `REL-48` — arXiv:1810.00101 (Ghanavati, Costa, Seboek, Lo, Andrzejak, "Memory and Resource Leak Defects and their Repairs in Java Projects") §4.4 — "Collection mismanagement (collection) is the most common root cause for memory leaks (39% of the cases)"; "Leaks due to collection mismanagement can lead to severe memory waste, in particular when the collection is used as a static member. The reason is that the static fields are never garbage-collected"; Table 5 — "Dead objects referenced by a collection" 93 of 491 issues, "Over-sized cache or buffer" 14. `java.util.LinkedHashMap#removeEldestEntry` Javadoc, Java SE 21 — "This is useful if the map represents a cache: it allows the map to reduce memory consumption by deleting stale entries ... maintaining a steady state of 100 entries".
- **Location**: `src/main/java/com/example/app/Formatter.java` · `Formatter#remember`
- **Code**:
  ```java
  private final LinkedList<String> recent = new LinkedList<>();
  ...
          recent.add(value);
  ```
- **Problem**: `recent` is an instance field of `Formatter`, and `Formatter` is constructor-injected into the singleton `@Service OrderService`, so one instance lives for the whole process. The class Javadoc says each method runs once per request. `remember(String value)` therefore appends one caller-supplied string to `recent` per request. Nothing in the file removes entries, caps the size or expires them: `recentAt` only reads, and no other code in the repository touches the list.
- **Suggested fix**:
  ```java
  private static final int MAX_RECENT = 1_000;
  private final LinkedList<String> recent = new LinkedList<>();
  
  public synchronized void remember(String value) {
      recent.addLast(value);
      if (recent.size() > MAX_RECENT) {
          recent.removeFirst(); // evict the eldest entry to hold a steady state
      }
  }
  
  public synchronized String recentAt(int index) {
      return recent.get(index);
  }
  ```
- **Rationale**: The singleton bean holding the list stays reachable for the life of the process, so every string added to `recent` stays reachable too, and the garbage collector can never reclaim it. Each request adds one entry and none is removed, so the heap fills over hours or days until the process fails with OutOfMemoryError. Tests are too short to show this. The paper cited in the card (arXiv:1810.00101) found collection mismanagement to be the most common cause of memory leaks. A cap that evicts the eldest entry keeps the list at a steady size.

### REL-02.1: A Stream returned by Files.lines, Files.list, Files.walk or Files.find, or a streaming query result, is closed by try-with-resources
- **Severity**: Major
- **Rule**: `REL-02` — `java.nio.file.Files#lines(Path, Charset)` Javadoc, Java SE 21 — "The returned stream contains a reference to an open file. The file is closed by closing the stream"; its API note — "This method must be used within a try-with-resources statement or similar control structure to ensure that the stream's open file is closed promptly after the stream's operations have completed". `Files#list`, `#walk`, `#find` — "The directory is closed by closing the stream", with the same API note. `java.lang.AutoCloseable` Javadoc — try-with-resources is "in general unnecessary when using non-I/O-based forms" of `Stream`. Hibernate ORM `org.hibernate.query.SelectionQuery#getResultStream` Javadoc — "The client should call Stream.close() after processing the stream so that resources are freed as soon as possible".
- **Location**: `src/main/java/com/example/app/LogScanner.java` · `LogScanner#countErrors`
- **Code**:
  ```java
          return Files.lines(path).filter(line -> line.contains("ERROR")).count();
  ```
- **Problem**: The Stream returned by Files.lines(path) is consumed by count() and then dropped. It is never declared as a try resource or closed in a finally, so nothing closes it.
- **Suggested fix**:
  ```java
  public long countErrors(Path path) throws IOException {
      try (Stream<String> lines = Files.lines(path)) {
          return lines.filter(line -> line.contains("ERROR")).count();
      }
  }
  ```
- **Rationale**: The stream from Files.lines holds a reference to an open file, and the file closes only when the stream is closed. The count() terminal operation finishes the pipeline but does not close the stream, so the file descriptor stays open. Each call to countErrors leaves one more descriptor open until the process runs out of file handles.

### REL-01.1: Every AutoCloseable that holds an I/O handle is opened in a try-with-resources statement, so it closes on every exit path
- **Severity**: Major
- **Rule**: `REL-01` — `java.lang.AutoCloseable` Javadoc, Java SE 21 — "The close() method of an AutoCloseable object is called automatically when exiting a try-with-resources block for which the object has been declared in the resource specification header. This construction ensures prompt release, avoiding resource exhaustion exceptions and errors that may otherwise occur"; its API note that try-with-resources is unnecessary for non-I/O-based forms. JLS §14.20.3 — resources closed in reverse order of initialization, exceptions from `close()` suppressed.
- **Location**: `src/main/java/com/example/app/Repo.java` · `Repo#findNameByEmail`
- **Code**:
  ```java
  Connection c = dataSource.getConnection();
  ```
- **Problem**: findNameByEmail opens a Connection with getConnection(), a PreparedStatement with prepareStatement() and a ResultSet with executeQuery() as plain locals. None of them is a try resource or closed in a finally block. The explicit rs.close(), ps.close() and c.close() calls run only when the method returns normally. If ps.setString, executeQuery, rs.next or rs.getString throws SQLException, the method exits by exception and all three handles are never closed.
- **Suggested fix**:
  ```java
  public String findNameByEmail(String email) throws SQLException {
      try (Connection c = dataSource.getConnection();
           PreparedStatement ps = c.prepareStatement("select name from users where email = ?")) {
          ps.setString(1, email);
          try (ResultSet rs = ps.executeQuery()) {
              return rs.next() ? rs.getString(1) : null;
          }
      }
  }
  ```
- **Rationale**: A close() placed after the work covers only the normal-return path. On the exception path, which any SQLException from setString, executeQuery, next or getString takes, the pooled Connection and its Statement and ResultSet are never released. Under load these leaks pile up until the DataSource connection pool runs out and every later request fails waiting for a connection. try-with-resources closes the handles on every exit, in reverse order (ResultSet, then PreparedStatement, then Connection). It also attaches any close() failure as a suppressed exception.

### REL-03.1: A ThreadLocal set on a pooled thread is removed in a finally block, and set(null) is not a removal
- **Severity**: Major
- **Rule**: `REL-03` — `java.lang.ThreadLocal` Javadoc, Java SE 21 — class: "Each thread holds an implicit reference to its copy of a thread-local variable as long as the thread is alive and the ThreadLocal instance is accessible"; `#remove` — "Removes the current thread's value for this thread-local variable. If this thread-local variable is subsequently read by the current thread, its value will be reinitialized by invoking its initialValue method"; `#set` — "Sets the current thread's copy of this thread-local variable to the specified value"; that `set(null)` keeps the entry is read from the class source (`set` writes through `ThreadLocalMap.set(this, value)`, `remove` calls `ThreadLocalMap.remove(this)`), not from the `#set` Javadoc. `java.lang.ScopedValue` class Javadoc, Java SE 21 (preview API) — a value is bound "for the bounded period of execution of a method" and "reverts to being unbound when the original method completes normally or with an exception", for a `Runnable.run`, `Callable.call` or `Supplier.get`. SEI CERT Oracle Coding Standard for Java, TPS04-J "Ensure ThreadLocal variables are reinitialized when using thread pools".
- **Location**: `src/main/java/com/example/app/RequestContext.java` · `RequestContext#handle`
- **Code**:
  ```java
  CURRENT_USER.set(user);
          process();
          CURRENT_USER.set(null);
  ```
- **Problem**: The per-request user is stored in the static ThreadLocal CURRENT_USER, and the only cleanup is `CURRENT_USER.set(null)`. That cleanup is not in a finally block, so it is skipped if process() throws. Even when it runs, set(null) is not a removal: it writes null into the thread's existing map entry and leaves that entry in place.
- **Suggested fix**:
  ```java
  public void handle(String user) {
      CURRENT_USER.set(user);
      try {
          process();
      } finally {
          CURRENT_USER.remove();
      }
  }
  ```
- **Rationale**: This context lives on the request handler thread, and that thread goes back to a pool and serves the next request. If process() throws, the thread still holds the previous request's user id, so currentUser() hands it to code that never set it. On the normal path, set(null) leaves the ThreadLocalMap entry in place. Only remove() inside a finally clears the entry on every exit.

### CC-09.1: A read-modify-write on a shared field is an atomic operation, never a plain or volatile increment
- **Severity**: Major
- **Rule**: `CC-09` — jcstress sample `openjdk/jcstress`, `jcstress-samples/.../samples/api/API_01_Simple.java` — two actors each run `++v` on an `int`; outcome `1, 1` "Both actors came up with the same value: atomicity failure" observed at 10.1% of samples. `java.util.concurrent.atomic.AtomicInteger#incrementAndGet` Javadoc, Java SE 21 — "Atomically increments the current value, with memory effects as specified by VarHandle.getAndAdd". SEI CERT Oracle Coding Standard for Java, VNA02-J "Ensure that compound operations on shared variables are atomic" — the `++`, `--` and compound-assignment operators always form compound operations.
- **Location**: `src/main/java/com/example/app/Stats.java` · `Stats#hit`
- **Code**:
  ```java
  private volatile int hits;
  ...
          hits++;
  ```
- **Problem**: `hit()` runs `hits++` on an instance field of `Stats`, and the class Javadoc says `Stats` is "shared by every handler thread". The method is not synchronized and no lock covers the update. Making `hits` volatile does not make the increment atomic, so two handler threads can both read the same value and both write the same result.
- **Suggested fix**:
  ```java
  private final AtomicInteger hits = new AtomicInteger();
  
  public void hit() {
      hits.incrementAndGet();
  }
  
  public int hits() {
      return hits.get();
  }
  ```
- **Rationale**: `hits++` is three separate steps: read, add and write. When two threads interleave these steps they write the same value, so one increment is lost. `volatile` orders and publishes each single read and each single write, but it does not join the read and the write into one atomic step. A volatile increment therefore loses updates just as a plain one does. `AtomicInteger#incrementAndGet` does the whole read-modify-write as one atomic operation.

### REL-04.1: Arithmetic whose overflow would corrupt a balance, a size or a count uses Math.addExact, multiplyExact or toIntExact, never a silently wrapping operator
- **Severity**: Major
- **Rule**: `REL-04` — `java.lang.Math#addExact(int, int)`, `#multiplyExact`, `#toIntExact(long)` Javadoc, Java SE 21 — "Returns the sum of its arguments, throwing an exception if the result overflows an int"; `@throws ArithmeticException if the result overflows an int`; `toIntExact` — "throwing an exception if the value overflows an int". SEI CERT Oracle Coding Standard for Java, NUM00-J "Detect or prevent integer overflow". SpotBugs `ICAST_INTEGER_MULTIPLY_CAST_TO_LONG` — an `int` multiplication cast to `long` overflows before the widening.
- **Location**: `src/main/java/com/example/app/Totals.java` · `Totals#addWithinLimit`
- **Code**:
  ```java
  int next = base + amount;
  ```
- **Problem**: The account balance `base` and the caller-supplied `amount` are added with a plain `int` `+`. Nothing in the method bounds `amount`, so `base + amount` can pass Integer.MAX_VALUE and wrap to a large negative number. The `Math.min(next, limit)` clamp runs after the wrap and does not catch it: a wrapped negative `next` is always smaller than `limit`, so `compute` writes the corrupted value as the new balance. In the other direction, a sum below Integer.MIN_VALUE wraps to a positive number and gets clamped to `limit` as if it were a valid credit.
- **Suggested fix**:
  ```java
  public void addWithinLimit(String account, int amount) {
      totals.compute(account, (key, current) -> {
          Integer limit = limits.get(key);
          int base = current == null ? 0 : current;
          int next = Math.addExact(base, amount); // throws ArithmeticException instead of wrapping
          return limit == null ? next : Math.min(next, limit);
      });
  }
  ```
- **Rationale**: `int` `+` wraps on overflow and throws nothing. The per-account balance in `totals` becomes a wrong, possibly negative number, which breaks the project invariant that totals never go negative, and it is stored and propagated as if it were correct. `Math.addExact` does the same addition but throws ArithmeticException when the result overflows an int, so the failure shows up where the sum is computed.

### CC-11.1: A function passed to compute, computeIfAbsent or merge never updates the same concurrent map
- **Severity**: Major
- **Rule**: `CC-11` — `java.util.concurrent.ConcurrentHashMap#computeIfAbsent`, `#compute` Javadoc, Java SE 21 — "The mapping function must not modify this map during computation"; "Some attempted update operations on this map by other threads may be blocked while computation is in progress, so the computation should be short and simple"; throws `IllegalStateException` "if the computation detectably attempts a recursive update to this map that would otherwise never complete". `#merge` — the function "must not attempt to update any other mappings of this Map". Class Javadoc — "Retrieval operations (including get) generally do not block", which is why a read inside the function is outside the rule.
- **Location**: `src/main/java/com/example/app/Totals.java` · `Totals#transfer`
- **Code**:
  ```java
  totals.compute(to, (key, current) -> {
              totals.merge(from, -amount, Integer::sum);
  ```
- **Problem**: The remapping function passed to totals.compute (a ConcurrentHashMap) calls totals.merge on the same map for another key (from). That is a recursive update of the map while compute holds the bin for key `to`.
- **Suggested fix**:
  ```java
  public void transfer(String from, String to, int amount) {
      totals.merge(from, -amount, Integer::sum);
      totals.merge(to, amount, Integer::sum);
  }
  ```
- **Rationale**: ConcurrentHashMap runs the remapping function while holding the lock on the bin that owns `to`. The Javadoc forbids the function from modifying the map ("The mapping function must not modify this map during computation"), and the nested totals.merge does exactly that. When `from` falls in `to`'s bin, one of two things happens. The map may detect the recursion and throw IllegalStateException("Recursive update"). If both keys are new and the bin already holds another key, that exception comes after the debit to `from` has been written, so the transfer is left half-applied. Otherwise, because the bin lock is reentrant, the nested merge runs and the call completes. With from == to on an existing key, the credit then overwrites the debit and the balance grows by `amount`. When `from` sits in another bin, the call waits for that bin's lock while holding `to`'s. Two ingest workers transferring in opposite directions then deadlock, and neither call ever completes.
- **Verifier note**: The finding is real. The remapping function updates the same ConcurrentHashMap, which the Javadoc forbids. Nothing in the code, the commit log or config.md tolerates it, and the fix compiles and is correct. Severity stays major.

One correction, to the rationale only. It says that when `from` hashes to the same bin, the call waits on a bin the calling thread already holds and never completes. The JDK 21 run contradicts this. The bin lock is reentrant, so the same-bin case either throws IllegalStateException or completes. When it throws, the transfer can be left half-applied. When it completes with from == to, the balance comes out wrong. The case that never completes is a different one: two workers transferring in opposite directions across two bins, which I observed deadlocking.

Context, not a new finding: neither the head code nor the fix enforces config.md invariant 4 (no negative balances). That belongs to a separate rule and is not a defect this fix introduces.

### REL-04.2: Arithmetic whose overflow would corrupt a balance, a size or a count uses Math.addExact, multiplyExact or toIntExact, never a silently wrapping operator
- **Severity**: Major
- **Rule**: `REL-04` — `java.lang.Math#addExact(int, int)`, `#multiplyExact`, `#toIntExact(long)` Javadoc, Java SE 21 — "Returns the sum of its arguments, throwing an exception if the result overflows an int"; `@throws ArithmeticException if the result overflows an int`; `toIntExact` — "throwing an exception if the value overflows an int". SEI CERT Oracle Coding Standard for Java, NUM00-J "Detect or prevent integer overflow". SpotBugs `ICAST_INTEGER_MULTIPLY_CAST_TO_LONG` — an `int` multiplication cast to `long` overflows before the widening.
- **Location**: `src/main/java/com/example/app/Totals.java` · `Totals#transfer`
- **Code**:
  ```java
  return (current == null ? 0 : current) + amount;
  ```
- **Problem**: The destination balance is credited with a plain `int` `+` on an unbounded `amount` parameter, and `compute` stores the result as the new balance. A destination balance close to Integer.MAX_VALUE plus a large enough `amount` wraps the sum to a negative value. The debit on the line before, `totals.merge(from, -amount, Integer::sum)`, wraps the same way: `Integer::sum` is a plain `+`, and `-amount` is itself Integer.MIN_VALUE when `amount == Integer.MIN_VALUE`.
- **Suggested fix**:
  ```java
  public void transfer(String from, String to, int amount) {
      int debit = Math.negateExact(amount);           // amount == Integer.MIN_VALUE throws, nothing stored
      totals.merge(from, debit, Math::addExact);       // debit overflow throws, nothing stored
      try {
          totals.compute(to, (key, current) -> Math.addExact(current == null ? 0 : current, amount));
      } catch (ArithmeticException e) {
          totals.merge(from, amount, Math::addExact);  // credit overflowed: put the debit back so no half-transfer remains
          throw e;
      }
  }
  ```
- **Rationale**: `int` addition and negation wrap silently on overflow. At head, a transfer of 10 from 100 into Integer.MAX_VALUE-5 stores to=-2147483644, the negative balance that invariant 4 forbids. `Math.addExact` and `Math.negateExact` throw ArithmeticException instead. Debit and credit are two separate atomic updates, though. Without an undo, a credit that overflows after the debit is stored leaves the source debited and the destination not credited ({from=90, to=2147483642} in the run). Putting the debit back in the catch block makes an overflowing transfer leave both balances unchanged. Moving the merge out of the compute lambda also removes the nested update that ConcurrentHashMap rejects: a self-transfer on an absent key throws IllegalStateException "Recursive update" at head.
- **Verifier note**: The finding is real: I reproduced every wrap it describes at runtime. Only the fix needed correcting. As proposed, it stores the debit (merge) and then runs a credit that can throw. So a credit overflow leaves the source debited and the destination not credited: 10 units vanished in the run. This contradicts the fix's own rationale that the bad transfer "is never stored". The corrected fix puts the debit back when the credit throws, so an overflowing transfer leaves both balances unchanged; I compiled and ran it. The fix covers REL-04 only. It does not add the below-zero rejection that invariant 4 requires.

### LOGIC.1: When `from.equals(to)`, the nested `totals.merge(from, -amount, ...)` …
- **Severity**: Major
- **Rule**: `LOGIC` — logic and correctness pass (no card)
- **Location**: `src/main/java/com/example/app/Totals.java` · `Totals#transfer`
- **Code**:
  ```java
              return (current == null ? 0 : current) + amount;
  ```
- **Problem**: When `from.equals(to)`, the nested `totals.merge(from, -amount, ...)` debits the same entry that `compute` holds. `compute` then overwrites that debit with a value built from the `current` it read before the merge ran. A self-transfer therefore raises the balance by `amount` instead of leaving it unchanged. If the key is absent, ConcurrentHashMap instead throws `IllegalStateException("Recursive update")`, and when the bin already holds other keys the merge has already left a `-amount` entry behind.
- **Suggested fix**:
  ```java
  public void transfer(String from, String to, int amount) {
      if (amount <= 0) {
          throw new IllegalArgumentException("amount must be positive: " + amount);
      }
      if (from.equals(to)) {
          return; // a self-transfer is a no-op
      }
      // debit first (rejecting overdraft), then credit; never mutate the map inside a remapping function
      totals.compute(from, (key, current) -> {
          int base = current == null ? 0 : current;
          if (base < amount) {
              throw new IllegalStateException("insufficient funds in " + key);
          }
          return base - amount;
      });
      totals.merge(to, amount, Integer::sum);
  }
  ```
- **Rationale**: Input: `transfer("A", "A", 50)` with A = 100, on one thread with no concurrency. `compute` locks A's bin and calls the lambda with current = 100. The nested `merge` re-enters the same monitor and writes A = 50. The lambda returns 100 + 50 = 150, and `compute` stores that over the 50. A ends at 150, so a request that names the same account twice creates 50 out of nothing.

### SEC-31.1: A security-relevant random value comes from SecureRandom, never from java.util.Random, ThreadLocalRandom, Math.random or a name-based UUID
- **Severity**: Major
- **Rule**: `SEC-31` — `java.util.Random` class Javadoc, Java SE 21 — "its period is only 2^48. The class uses a 48-bit seed, which is modified using a linear congruential formula"; "Instances of java.util.Random are not cryptographically secure. Consider instead using java.security.SecureRandom". `java.util.concurrent.ThreadLocalRandom` — the same note. `java.util.random.RandomGenerator` interface Javadoc — "Objects that implement RandomGenerator are typically not cryptographically secure. Consider instead using SecureRandom"; `java.util.SplittableRandom` class Javadoc — "Instances of SplittableRandom are not cryptographically secure". `java.security.SecureRandom` class Javadoc — "a cryptographically strong random number generator", non-deterministic output per RFC 4086, and "This self-seeding will not occur if setSeed was previously called". `java.util.UUID#randomUUID` — "generated using a cryptographically strong pseudo random number generator"; `#nameUUIDFromBytes` — a type 3 (name-based) UUID, computed with MD5 in the reference implementation. OWASP Cryptographic Storage Cheat Sheet, "Secure Random Number Generation" — Java unsafe: `Math.random()`, `java.util.Random`, `SplittableRandom`, `ThreadLocalRandom`; secure: `SecureRandom`, `UUID.randomUUID()`. OWASP ASVS 5.0 §11.5.1 — non-guessable values from a CSPRNG with at least 128 bits of entropy, which a UUID does not meet. SEI CERT MSC02-J and CWE-330 — by id.
- **Location**: `src/main/java/com/example/app/UserLookup.java` · `UserLookup#newPasswordResetToken`
- **Code**:
  ```java
  Random random = new Random();
  ```
- **Problem**: The password-reset token is built from two nextLong() calls on java.util.Random, which is not cryptographically secure, so the token is predictable.
- **Suggested fix**:
  ```java
  public String newPasswordResetToken() {
      byte[] bytes = new byte[32];
      secureRandom.nextBytes(bytes);
      return java.util.HexFormat.of().formatHex(bytes);
  }
  ```
- **Rationale**: java.util.Random is a linear congruential generator with a 48-bit seed and a period of only 2^48, and its Javadoc says it is not cryptographically secure. An attacker who sees earlier output can predict the next values, which makes the password-reset token guessable and lets them take over an account. SecureRandom seeds itself from the platform's entropy source. Its output cannot be predicted from earlier output.

### SEC-04.1: An external command runs through ProcessBuilder or exec(String[]) with each argument as its own element, never through Runtime.exec(String) or a shell -c string
- **Severity**: Major _(downgraded from critical)_
- **Rule**: `SEC-04` — `java.lang.Runtime#exec(String)` Javadoc, Java SE 21 — "@deprecated This method is error-prone and should not be used, the corresponding method exec(String[]) or ProcessBuilder should be used instead. The command string is broken into tokens using only whitespace characters"; `#exec(String, String[], File)` — tokens from "a StringTokenizer created by the call new StringTokenizer(command)". OWASP OS Command Injection Defense Cheat Sheet — "In Java, use ProcessBuilder and the command must be separated from its arguments"; `Runtime.exec` "does NOT try to invoke the shell at any point"; the `--` end-of-options guideline. OWASP ASVS 5.0 requirement 1.2.5. SEI CERT IDS07-J; CWE-78.
- **Location**: `src/main/java/com/example/app/UserLookup.java` · `UserLookup#convertAvatar`
- **Code**:
  ```java
  return Runtime.getRuntime().exec("sh -c 'convert " + uploadedFile + " avatar.png'");
  ```
- **Problem**: The request-supplied `uploadedFile` is concatenated into one command string (the class Javadoc on line 12 says every parameter arrives from the request). The string runs through `Runtime.exec(String)`, wrapped in `sh -c`. `Runtime.exec(String)` splits it with `new StringTokenizer(command)` and ignores the single quotes, so the argv is always `[sh, -c, 'convert, <filename tokens...>, avatar.png]`. The shell's script is the fixed token `'convert`, an unterminated quote, so every call exits with status 2 and `convert` never runs. The method is broken, and one quoting repair would turn it into a shell command built from request data. `convertAvatarSafely` (line 44) already uses the argument-list form.
- **Suggested fix**:
  ```java
  public Process convertAvatar(String uploadedFile) throws java.io.IOException {
      return new ProcessBuilder("convert", "--", uploadedFile, "avatar.png").start();
  }
  ```
- **Rationale**: `Runtime.exec(String)` tokenizes on whitespace only (Java SE 21 Javadoc: `new StringTokenizer(command)`). Here the tokenizer keeps the filename away from the shell parser. The filename lands in `$0` and the positional parameters behind a `-c` script that fails to parse, and option-like tokens after the script are not read as shell options. As written, there is no command or argument injection, only a call that always fails. The CWE-78 exposure is latent: the obvious repair, `exec(new String[]{"sh", "-c", "convert " + uploadedFile + " avatar.png"})` or its ProcessBuilder equivalent, passes the concatenated filename to a shell that runs `;`, `|`, `$( )` and backticks as commands. `ProcessBuilder` with one element per argument makes the call work and removes the shell. The `--` marker makes ImageMagick read the next argument as the input file even when it starts with `-`.
- **Verifier note**: The rule violation, location, code and fix stand. Request data reaches `Runtime.exec(String)` wrapped in `sh -c`, the card validator answers yes, and the ProcessBuilder argument list is the right fix. The fix also makes the method work.

The claimed mechanism does not hold for this code as written. The filename never reaches a shell parser, because the tokenizer makes the `-c` script the fixed token `'convert`, which fails to parse. There is no command injection and no argument injection, and `convert` never runs. What breaks today is that every call exits 2 and produces no avatar.png, which is a correctness bug.

The CWE-78 risk is latent. It becomes real once someone repairs the quoting with `exec(new String[]{"sh","-c","convert " + uploadedFile + " avatar.png"})`. A security defect that needs a specific condition, plus a broken method, is major, not critical.

Card-level context: the SEC-04 card's own bad example (card line 21) has the same property. An example that actually injects would be `new ProcessBuilder("sh", "-c", "convert " + userFile + " out.pdf")`.
- **Also flagged by**: LOGIC

## Minor & Suggestions

| # | Severity | Rule | Location | Finding | Suggested fix |
|---|---|---|---|---|---|
| META-01.1 | Minor | `META-01` | `.claude/reviewing-java/config.md` · `Inv 2` | Invariant 2 is an allocation rule that depends on load, and it grades the construct only with the adjectives "cheap" and "large". It gives no per-call byte budget and no call rate for `Cache#load`. The config has no definitions or scale section that supplies either one, and `CacheLoadBench` does not exist in the repository at HEAD, so the threshold is not recorded anywhere a reviewer can read it. | 2. **Cache loads allocate under 4 KiB per call**: No single buffer allocated inside `Cache#load` exceeds 4 KiB. `Cache#load` runs about 2 M times a day on cache misses, so each 4 KiB allocated per call adds about 8 GB/day of heap churn. Violation: a buffer larger than 4 KiB allocated inside `Cache#load`. Enforced by `CacheLoadBench` (fails above 4 KiB allocated per op). The budget and rate here are examples; replace them with the project's measured call rate and its agreed budget. |
| META-05.1 | Minor | `META-05` | `.claude/reviewing-java/config.md` · `Inv 3` | Invariant 3 is written as a recommendation. Its rule clause uses 'prefer' in the title and 'should' in the text, and it names no enforcement. A reviewer cannot fail a diff on it: any field-injected repository can be defended as a valid exception. | 3. **Repositories take dependencies through the constructor**: No repository class declares an `@Autowired` (or `@Inject`) field; every dependency is a constructor parameter. Violation: a field-injected repository (`@Autowired` on a field). Enforced by ArchUnit rule `RepositoriesUseConstructorInjection`. |
| META-08.1 | Minor | `META-08` | `.claude/reviewing-java/config.md` · `Invariants` | The diff adds a rule on code as a prose sentence after the numbered list under ## Invariants. It is not a tolerance, definition or rationale, and it has no invariant number and no Violation: clause. | 5. **Production code does not print to stdout**: No production class calls `System.out`. Violation: a `System.out` reference in a class under `src/main/java`. |
| PF-16.1 | Minor | `PF-16` | `src/main/java/com/example/app/Formatter.java` · `Formatter#isUpperCase` | isUpperCase calls Pattern.compile on the constant regex "^[A-Z]+$" inside the method body, so the pattern is compiled again on every call. The class Javadoc says each method runs once per request, which makes this a request-path method. | private static final Pattern UPPER_CASE = Pattern.compile("^[A-Z]+$");  public boolean isUpperCase(String value) {     return UPPER_CASE.matcher(value).matches(); } |
| PF-11.1 | Minor | `PF-11` | `src/main/java/com/example/app/Formatter.java` · `Formatter#joinAll` | joinAll declares the String accumulator `out` outside the for loop and grows it with `+=` twice per iteration over an unbounded `parts` list. The method runs on every request. | public String joinAll(List<String> parts) {     StringBuilder out = new StringBuilder(parts.size() * 8);     for (String part : parts) {         out.append(part).append(',');     }     return out.toString(); } |
| PF-02.1 | Minor | `PF-02` | `src/main/java/com/example/app/Formatter.java` · `Formatter#recent` | The `recent` field is a LinkedList, and `recentAt(int)` reads it by position with `recent.get(index)`. Per the class Javadoc, each method runs once per request, so this indexed read is on the hot path. No ListIterator cursor touches this list, and it holds no null-bearing queue. | private final List<String> recent = new ArrayList<>();  public String recentAt(int index) {     return recent.get(index); // constant time on ArrayList } |
| PROJ-3.1 | Minor | `PROJ-3` | `src/main/java/com/example/app/OrderService.java` · `OrderService#repo` | Rule MNT-34: OrderService is a Spring `@Service`. It gets its required `Repo` from `@Autowired` on a private, non-final field, while its existing constructor, which already takes `Formatter`, leaves `Repo` out. Invariant 3 (PROJ-3) does not apply here. That invariant is about repository classes taking their own dependencies through the constructor, and the only repository class, `Repo`, already does (`Repo(DataSource)`). OrderService is not a repository class. | @Service public class OrderService {     private static final Logger log = LoggerFactory.getLogger(OrderService.class);      private final Repo repo;     private final Formatter formatter;     private boolean archived;      public OrderService(Repo repo, Formatter formatter) {         this.repo = repo;         this.formatter = formatter;     }     // ... rest unchanged; remove the org.springframework.beans.factory.annotation.Autowired import } |
| CC-18.1 | Minor | `CC-18` | `src/main/java/com/example/app/OrderService.java` · `OrderService#setArchived` | OrderService is a Spring singleton: @Service, with no @Scope, @Configuration or @Bean anywhere in the repository. It declares a non-final, non-volatile instance field `archived` and a public setter that writes it with no lock. Nothing in the repository reads the field or calls setArchived. The field is shared state that is only ever written, and the setter invites callers to store per-order or per-request state that a singleton cannot hold. | @Service public class OrderService {     private static final Logger log = LoggerFactory.getLogger(OrderService.class);      @Autowired     private Repo repo;      private final Formatter formatter;      public OrderService(Formatter formatter) {         this.formatter = formatter;     }      // `private boolean archived;` and setArchived(boolean) deleted: nothing in the     // repository reads the flag or calls the setter. State about one order or one     // request is passed as a method parameter or kept in a @RequestScope bean.      // render, loadName and loadCount unchanged }  // Only if a service-wide flag is really wanted, keep the setter and make the // field final and thread-safe (import java.util.concurrent.atomic.AtomicBoolean): private final AtomicBoolean archived = new AtomicBoolean();  public void setArchived(boolean archived) {     this.archived.set(archived); } |
| MNT-22.1 | Minor | `MNT-22` | `src/main/java/com/example/app/OrderService.java` · `OrderService#loadName` | The catch block logs the SQLException, stack trace included, and then rethrows it wrapped in an IllegalStateException. One failure is therefore recorded here and again by whichever layer finally handles the wrapper. | } catch (java.sql.SQLException e) {     throw new IllegalStateException("lookup failed for " + email, e); } |
| MNT-02.1 | Minor | `MNT-02` | `src/main/java/com/example/app/OrderService.java` · `OrderService#render` | The public method render takes a boolean selector, forEmail. The method tests it in `if (forEmail)` to pick one of two separate paths: wrap the order in HTML for email, or return it unchanged. | public String renderForEmail(String order) {     return "<p>" + order + "</p>"; }  public String renderPlain(String order) {     return order; }  // caller: renderForEmail(order) instead of render(order, true) |
| MNT-09.1 | Minor | `MNT-09` | `src/main/java/com/example/app/Repo.java` · `Repo#countActive` | The added body of Repo#countActive is a copy of the existing Repo#count body in the same file (lines 18-22, starting `try (Connection c = dataSource.getConnection();`). The statements are the same three resource declarations and the same `return rs.next() ? rs.getInt(1) : 0;`. Only the SQL string literal differs. | public int count() throws SQLException {     return countWhere("select count(*) from users"); }  public int countActive() throws SQLException {     return countWhere("select count(*) from users where active = true"); }  private int countWhere(String sql) throws SQLException {     try (Connection c = dataSource.getConnection();          PreparedStatement ps = c.prepareStatement(sql);          ResultSet rs = ps.executeQuery()) {         return rs.next() ? rs.getInt(1) : 0;     } } |
| CC-05.1 | Minor | `CC-05` | `src/main/java/com/example/app/Stats.java` · `Stats#record` | The added synchronized method locks on the Stats instance's own monitor (`this`). Stats is a public, non-final class shared by every handler thread, and the pre-existing `total()` uses the same monitor. Any code that holds a Stats reference can take that monitor with `synchronized (stats)`, and a subclass can take it too. | public class Stats {     private final Object lock = new Object();     private long total;      public long total() {         synchronized (lock) {             return total;         }     }      public void record() {         synchronized (lock) {             total++;         }     } } |
| MNT-38.1 | Minor | `MNT-38` | `src/main/java/com/example/app/Totals.java` · `Totals#mirror` | `account` (the balance that gets overwritten) and `sibling` (the balance it copies from) are adjacent `String` parameters with different roles. A call such as `mirror(sibling, account)` compiles and overwrites the source balance with the target's. | public record MirrorRequest(AccountId target, AccountId source) {}  public void mirror(MirrorRequest r) {     totals.compute(r.target().value(), (key, current) -> {         Integer other = totals.get(r.source().value());         return other == null ? current : other;     }); } // or, at each call site: // totals.mirror(/* account= */ target, /* sibling= */ source); |
| MNT-38.2 | Minor | `MNT-38` | `src/main/java/com/example/app/Totals.java` · `Totals#transfer` | `from` (the account debited) and `to` (the account credited) are adjacent `String` parameters with opposite roles. A call such as `transfer(to, from, 100)` compiles and moves money in the wrong direction. | public record AccountId(String value) {     public AccountId {         if (value == null \|\| value.isBlank()) throw new IllegalArgumentException("account id");     } } public record Transfer(AccountId from, AccountId to, int amount) {}  public void transfer(Transfer t) {     totals.compute(t.to().value(), (key, current) -> {         totals.merge(t.from().value(), -t.amount(), Integer::sum);         return (current == null ? 0 : current) + t.amount();     }); } // or, if no type is warranted, name each argument at the call site: // totals.transfer(/* from= */ source, /* to= */ target, amount); |
| MNT-29.1 | Suggestion | `MNT-29` | `src/main/java/com/example/app/Cache.java` · `Cache#getOrLoad` | Public method added to a public class without a Javadoc summary; the name does not say when a load happens or what concurrent callers observe. | /**  * Returns the cached value for {@code key}, loading and caching it on first request.  *  * @param key the cache key; must not be null  * @return the cached or freshly loaded value  */ public String getOrLoad(String key) { |
| MNT-29.2 | Suggestion | `MNT-29` | `src/main/java/com/example/app/Formatter.java` · `Formatter` | Four public methods added to Formatter have no Javadoc summary: joinAll, joinWithBuilder, recentAt and remember. Their names do not show the output format (joinAll and joinWithBuilder add a comma after every element, the last one included) or the contract (recentAt throws IndexOutOfBoundsException for a bad index and does not say whether index 0 is the oldest entry; remember keeps every value with no bound). isUpperCase and isDigits are borderline: their regexes accept only non-empty ASCII input. | /**  * Concatenates {@code parts}, appending a comma after every element including the last.  *  * @param parts the values to join; must not be null  * @return the joined string, empty when {@code parts} is empty  */ public String joinAll(List<String> parts) { |
| MNT-29.3 | Suggestion | `MNT-29` | `src/main/java/com/example/app/Formatter.java` · `Formatter` | Six public methods added to the public class Formatter have no Javadoc summary: isUpperCase, isDigits, joinAll, joinWithBuilder, recentAt and remember. Only the class and separate() are documented. | /**  * Returns whether {@code value} consists of one or more ASCII uppercase letters {@code A-Z}.  *  * @param value the string to test; must not be null  * @return {@code true} when {@code value} is non-empty and every character is in {@code A-Z}  */ public boolean isUpperCase(String value) { |
| MNT-29.4 | Suggestion | `MNT-29` | `src/main/java/com/example/app/Formatter.java` · `Formatter#recentAt` | Public method without Javadoc; index ordering (oldest-first) and out-of-range behavior are not stated. | /**  * Returns the remembered value at {@code index}, counting from the oldest remembered value.  *  * @param index the 0-based position  * @throws IndexOutOfBoundsException if {@code index} is outside the remembered range  */ public String recentAt(int index) { |
| MNT-29.5 | Suggestion | `MNT-29` | `src/main/java/com/example/app/Formatter.java` · `Formatter#remember` | Public method without Javadoc; it does not say the history is unbounded or that the method is not thread-safe on a formatter used for every response. | /**  * Appends {@code value} to this formatter's history of recent values.  *  * <p>The history is unbounded and not thread-safe; callers must synchronize externally.  */ public void remember(String value) { |
| MNT-29.6 | Suggestion | `MNT-29` | `src/main/java/com/example/app/LogScanner.java` · `LogScanner` | Two public methods added to LogScanner have no Javadoc summary: countErrors(Path) and countErrorsIn(List<String>). Neither says what counts as an error line (a case-sensitive substring match on "ERROR"), and countErrors does not say when IOException or UncheckedIOException is thrown. | /**  * Counts the lines of the file at {@code path} that contain the case-sensitive substring {@code "ERROR"}.  *  * @param path the log file to scan, read as UTF-8  * @return the number of matching lines  * @throws IOException if an I/O error occurs opening the file  * @throws java.io.UncheckedIOException if an I/O error occurs while reading, including malformed UTF-8 input  */ public long countErrors(Path path) throws IOException { |
| MNT-29.7 | Suggestion | `MNT-29` | `src/main/java/com/example/app/LogScanner.java` · `LogScanner` | Two public methods are added without Javadoc: countErrors(Path) and countErrorsIn(List<String>). Neither states what counts as an error line. | /**  * Counts the lines of the file at {@code path} that contain the substring {@code "ERROR"} (case-sensitive).  *  * @param path the log file to scan  * @return the number of matching lines  * @throws IOException if the file cannot be opened or read  */ public long countErrors(Path path) throws IOException {  /**  * Counts the entries of {@code lines} that contain the substring {@code "ERROR"} (case-sensitive).  *  * @param lines the log lines to scan; must not be null  * @return the number of matching lines  */ public long countErrorsIn(List<String> lines) { |
| MNT-29.8 | Suggestion | `MNT-29` | `src/main/java/com/example/app/OrderService.java` · `OrderService#loadCount` | Public method without Javadoc; what is counted and the unchecked failure mode are not stated. | /**  * Returns the total number of users.  *  * @throws IllegalStateException if the database count fails  */ public int loadCount() { |
| MNT-29.9 | Suggestion | `MNT-29` | `src/main/java/com/example/app/OrderService.java` · `OrderService` | OrderService adds public members with no Javadoc summary. render(String, boolean): the boolean switches the output to HTML-wrapped text, and the order text is not escaped. loadName(String): the result is null when no user has the email, and it throws IllegalStateException when the SQL lookup fails. loadCount(): it throws IllegalStateException when the SQL count fails. The constructor OrderService(Formatter) and setArchived(boolean) are arguably self-explanatory under §7.3.1. | /**  * Renders {@code order} as plain text, or wrapped in an HTML paragraph for an email body.  *  * @param order the order text; inserted without HTML escaping  * @param forEmail {@code true} to wrap the text in {@code <p>...</p>}  * @return the order text, wrapped in a paragraph element when {@code forEmail} is true  */ public String render(String order, boolean forEmail) {  /**  * Returns the name of the user registered with {@code email}.  *  * @param email the user's email address  * @return the user's name, or {@code null} if no user has that email  * @throws IllegalStateException if the database lookup fails  */ public String loadName(String email) { |
| MNT-29.10 | Suggestion | `MNT-29` | `src/main/java/com/example/app/OrderService.java` · `OrderService` | Public members added without a Javadoc summary: render(String, boolean), loadName(String), loadCount(). A call site like render(order, true) does not show what the boolean does to the output, and the signatures of loadName and loadCount do not say they throw IllegalStateException when the repository lookup fails. | /**  * Renders {@code order} for display.  *  * @param order the order text  * @param forEmail {@code true} to wrap the text in an HTML paragraph for email, {@code false} for plain text  * @return the rendered order  */ public String render(String order, boolean forEmail) { |
| MNT-29.11 | Suggestion | `MNT-29` | `src/main/java/com/example/app/Repo.java` · `Repo#findNameByEmail` | Public method without Javadoc; the null return when no user matches is not stated. | /**  * Returns the name of the user with the given email address.  *  * @param email the email to match exactly  * @return the user's name, or {@code null} if no user matches  * @throws SQLException if the query fails  */ public String findNameByEmail(String email) throws SQLException { |
| MNT-29.12 | Suggestion | `MNT-29` | `src/main/java/com/example/app/RequestContext.java` · `RequestContext` | The diff adds two public methods without a Javadoc summary: handle(String) and handleSafely(String). Neither says that it binds the user to the calling thread's ThreadLocal while processing runs, or what thread-local state is left behind afterwards (handle sets it to null, handleSafely removes it even on exception). | /**  * Processes the current request with {@code user} bound as the thread's current user.  *  * @param user the authenticated user for this request  */ public void handle(String user) { |
| MNT-29.13 | Suggestion | `MNT-29` | `src/main/java/com/example/app/RequestContext.java` · `RequestContext` | The diff adds two public methods without Javadoc: handle(String) and handleSafely(String). Neither has a summary sentence, and nothing tells a reader how they differ: handle clears the binding with set(null) only when process() returns normally, while handleSafely always calls remove() in a finally block. | /**  * Processes the current request with {@code user} bound as the thread's current user,  * then clears the binding. The binding is not cleared if processing throws; prefer  * {@link #handleSafely(String)}.  *  * @param user the authenticated user for this request  */ public void handle(String user) { |
| MNT-29.14 | Suggestion | `MNT-29` | `src/main/java/com/example/app/Stats.java` · `Stats` | Public members added to Stats, a class shared by every handler thread, have no Javadoc summary: hit() and record(). Neither says whether it is safe to call concurrently. | /**  * Increments the hit counter.  *  * <p>Not atomic: concurrent calls may lose increments.  */ public void hit() { |
| MNT-29.15 | Suggestion | `MNT-29` | `src/main/java/com/example/app/Totals.java` · `Totals#addWithinLimit` | Public method without Javadoc; it does not say the result is silently capped at the account's limit rather than rejected. | /**  * Adds {@code amount} to {@code account}, capping the new total at the account's limit if one is set.  *  * @param account the account to credit  * @param amount the amount to add  */ public void addWithinLimit(String account, int amount) { |
| MNT-29.16 | Suggestion | `MNT-29` | `src/main/java/com/example/app/Totals.java` · `Totals` | The diff adds public methods transfer and addWithinLimit with no Javadoc. transfer does not say whether the two-account update is atomic, how an absent account is handled, or whether an overdraft is rejected. addWithinLimit does not say that an amount over the account's limit is capped silently rather than rejected. | /**  * Moves {@code amount} from account {@code from} to account {@code to}; an account with no entry is treated as a zero balance.  *  * @param from the debited account  * @param to the credited account  * @param amount the amount to move  */ public void transfer(String from, String to, int amount) { // Add "@throws IllegalArgumentException if the transfer would drive {@code from} below zero" only together with the guard that the project's invariant 4 requires; the method at HEAD performs no such check. |
| MNT-29.17 | Suggestion | `MNT-29` | `src/main/java/com/example/app/UserLookup.java` · `UserLookup#convertAvatar` | Public method without Javadoc; it does not say it spawns an asynchronous process, where the output is written, or what input is acceptable. | /**  * Starts converting {@code uploadedFile} to {@code avatar.png} in the working directory.  *  * @param uploadedFile path of the uploaded image  * @return the started conversion process; the caller must wait for it  * @throws java.io.IOException if the process cannot be started  */ public Process convertAvatar(String uploadedFile) throws java.io.IOException { |
| MNT-29.18 | Suggestion | `MNT-29` | `src/main/java/com/example/app/UserLookup.java` · `UserLookup#convertAvatarSafely` | Public method without Javadoc; what "Safely" means relative to convertAvatar and the asynchronous return are not stated. | /**  * Starts converting {@code uploadedFile} to {@code avatar.png}, passing the path as a single  * argument without a shell.  *  * @param uploadedFile path of the uploaded image  * @return the started conversion process; the caller must wait for it  * @throws java.io.IOException if the process cannot be started  */ public Process convertAvatarSafely(String uploadedFile) throws java.io.IOException { |
| MNT-29.19 | Suggestion | `MNT-29` | `src/main/java/com/example/app/UserLookup.java` · `UserLookup` | These public methods added to UserLookup have no Javadoc summary: findNameByEmail, findNameById, convertAvatar, convertAvatarSafely, newPasswordResetToken and newSessionId. Neither find method says it returns null when no user matches. The two convertAvatar methods do not say what the returned Process is for or which input they trust. The token and session-id methods do not state what randomness they guarantee. | /**  * Returns the name of the user with the given email address.  *  * @param email the email to match exactly  * @return the user's name, or {@code null} if no user matches  * @throws SQLException if the query fails  */ public String findNameByEmail(String email) throws SQLException { |
| MNT-29.20 | Suggestion | `MNT-29` | `src/main/java/com/example/app/UserLookup.java` · `UserLookup` | Public members added without a Javadoc summary: findNameByEmail, findNameById (both return null when no user matches, which is not stated), convertAvatar, convertAvatarSafely (spawn an external process and throw IOException, conditions unstated), newPasswordResetToken, newSessionId (token format and unpredictability guarantee unstated). Only sampleAvatarIndex is documented. | /**  * Returns the name of the user with the given email address.  *  * @param email the email address to match  * @return the user's name, or {@code null} if no user has that email  * @throws SQLException if the query fails  */ public String findNameByEmail(String email) throws SQLException { |
| MNT-29.21 | Suggestion | `MNT-29` | `src/main/java/com/example/app/UserLookup.java` · `UserLookup#newPasswordResetToken` | Public method without Javadoc: nothing tells the caller the token's format or its randomness guarantee. The body uses java.util.Random, so a Javadoc must not claim a cryptographically secure source unless the body changes too. | /**  * Returns a new single-use password-reset token: 64 lowercase hex characters encoding  * 32 bytes drawn from {@link java.security.SecureRandom}, so it cannot be guessed.  */ public String newPasswordResetToken() {     byte[] bytes = new byte[32];     secureRandom.nextBytes(bytes);     return java.util.HexFormat.of().formatHex(bytes); } |
| MNT-29.22 | Suggestion | `MNT-29` | `src/main/java/com/example/app/UserLookup.java` · `UserLookup#newSessionId` | Public method without Javadoc; the id's length, encoding and randomness source are not stated. | /**  * Returns a new session id: 32 bytes from {@link java.security.SecureRandom}, encoded as 64 lowercase hex characters.  */ public String newSessionId() { |
| MNT-21.1 | Suggestion | `MNT-21` | `src/main/java/com/example/app/UserLookup.java` · `UserLookup#UserLookup(DataSource)` | UserLookup is not a container-managed bean. Its public constructor stores the dataSource reference parameter in a final field without checking it at entry, so a null argument is accepted and kept. | public UserLookup(DataSource dataSource) {     this.dataSource = java.util.Objects.requireNonNull(dataSource, "dataSource"); } |

