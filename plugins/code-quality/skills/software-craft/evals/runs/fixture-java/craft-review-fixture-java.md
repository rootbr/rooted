# fixture-java Craft Review

## Executive Summary
- Reviewed: `5333531672e1d760169b0d59fb0bc78c3a80756b...a224c3353ffa8a40ffdeb41fe810a403a201a998` (committed) — 9 files (SMALL); languages: java 9
- Passes: 81 card jobs (the Java corpus and the META cards), 3 logic slices, 4 project invariants; the universal corpus's 96 jobs filtered from the plan after the pre-pass; the two field-anchored findings re-run after the symbol rule gained Class#field
- Findings: 48 (5 critical, 17 major, 15 minor, 11 suggestion)
- Verification: 48 raw findings → 46 confirmed, 2 downgraded, 0 rejected, 0 flagged for the author
- Fix round: none
- Recommendation: Block

## Critical & Major Findings

### JAVA-55.1: A value written into an HTML or JavaScript response is encoded for the exact context it lands in, and HTML encoding is not JavaScript encoding
- **Severity**: Critical
- **Rule**: `JAVA-55` — OWASP Cross Site Scripting Prevention Cheat Sheet
- **Location**: `src/main/java/com/example/app/OrderService.java` · `OrderService#render`
- **Code**:
  ```java
              return "<p>" + order + "</p>";
  ```
- **Problem**: The public method `render` takes the caller-supplied String `order` and concatenates it raw into HTML element content (`<p>…</p>`) for the e-mail body. No encoder is applied anywhere in the file. The value is a free-form String rather than an allowlisted enum or number, and no template engine stands between it and the markup.
- **Suggested fix**:
  ```java
              return "<p>" + org.springframework.web.util.HtmlUtils.htmlEscape(order) + "</p>";
  ```
- **Rationale**: The landing context is HTML element content, and its metacharacters are `<`, `>`, `&`, `"` and `'`. Nothing encodes them here, so an order text containing `<script>` or `<img onerror=…>` reaches the HTML e-mail as live markup when a webmail client renders it in the browser. HTML entity encoding at the point of output is the encoder for this context. A filter applied earlier on input cannot know that this value ends up between tags.

### LOGIC.1: transfer debits `from` unconditionally, so a transfer larger than the …
- **Severity**: Critical
- **Rule**: `LOGIC` — logic and correctness pass (no card)
- **Location**: `src/main/java/com/example/app/Totals.java` · `Totals#transfer`
- **Code**:
  ```java
              totals.merge(from, -amount, Integer::sum);
  ```
- **Problem**: transfer debits `from` unconditionally, so a transfer larger than the source balance writes a negative balance. That breaks the project invariant that Totals#transfer rejects a transfer driving a balance below zero. A negative `amount` is also accepted, and it debits `to`, which can drive `to` below zero.
- **Suggested fix**:
  ```java
  public void transfer(String from, String to, int amount) {
      if (amount < 0) {
          throw new IllegalArgumentException("negative transfer amount: " + amount);
      }
      if (from.equals(to)) {
          return;
      }
      totals.compute(from, (key, current) -> {
          int balance = current == null ? 0 : current;
          if (balance < amount) {
              throw new IllegalStateException("transfer would drive " + key + " below zero");
          }
          return balance - amount;
      });
      totals.merge(to, amount, Integer::sum);
  }
  ```
- **Rationale**: Trigger: balance of `from` is 0 and transfer(from, to, 50) runs. Result: `from` ends at -50 and `to` at 50 (checked with the same code in a scratch run). Invariant 4 names a negative balance written by Totals#transfer as the violation. A rejection thrown inside `compute` leaves the mapping unchanged, so the fix cannot leave a half-applied transfer.

### PROJ-4.1: Totals never go negative
- **Severity**: Critical
- **Rule**: `PROJ-4` — project invariant from config.md
- **Location**: `src/main/java/com/example/app/Totals.java` · `Totals#transfer`
- **Code**:
  ```java
              totals.merge(from, -amount, Integer::sum);
  ```
- **Problem**: The new `Totals#transfer` debits `from` unconditionally: `merge(from, -amount, Integer::sum)` writes `balance - amount` whatever the balance is. No path in the method rejects an overdrawing transfer. Example: `from` holds 30 and `transfer(from, to, 100)` stores -70 for `from` and credits `to` with 100. A negative `amount` has the same effect on `to`. Separately, the debit runs inside the `compute(to, ...)` remapping function. That function updates another mapping of the same `ConcurrentHashMap`, which the `ConcurrentHashMap` contract forbids; it can throw `IllegalStateException("Recursive update")` or deadlock.
- **Suggested fix**:
  ```java
  public void transfer(String from, String to, int amount) {
      if (amount < 0) {
          throw new IllegalArgumentException("transfer amount must be non-negative: " + amount);
      }
      totals.compute(from, (key, current) -> {
          int balance = current == null ? 0 : current;
          if (balance < amount) {
              throw new IllegalStateException(
                      "transfer of " + amount + " would drive " + key + " below zero (balance " + balance + ")");
          }
          return balance - amount;
      });
      totals.merge(to, amount, Integer::sum);
  }
  ```
- **Rationale**: Invariant 4 (Totals never go negative) requires `Totals#transfer` to reject a transfer that would drive a balance below zero. It names a negative balance written by `Totals#transfer` as the violation, and `TotalsTransferTest` enforces it. The base commit has no `transfer`. The diff adds one that writes the forbidden state on every overdrawing call, with no race or fault needed. That makes it a data corruption under normal operation. In the fix, the balance check and the debit run atomically inside a single `compute` on `from`, so a concurrent transfer cannot pass the check against a stale balance. The exception thrown from the remapping function leaves the mapping unchanged. The credit to `to` runs only after the debit succeeds, and outside the remapping function. I compiled the fix with javac in a scratch directory.

### LOGIC.2: The remapping function of `totals.compute(to, ...)` updates another …
- **Severity**: Critical
- **Rule**: `LOGIC` — logic and correctness pass (no card)
- **Location**: `src/main/java/com/example/app/Totals.java` · `Totals#transfer`
- **Code**:
  ```java
          totals.compute(to, (key, current) -> {
  ```
- **Problem**: The remapping function of `totals.compute(to, ...)` updates another mapping of the same ConcurrentHashMap through `totals.merge(from, ...)`. The ConcurrentHashMap contract forbids that, because compute holds the bin lock of `to` while the function runs.
- **Suggested fix**:
  ```java
  public void transfer(String from, String to, int amount) {
      if (amount < 0) {
          throw new IllegalArgumentException("negative transfer amount: " + amount);
      }
      if (from.equals(to)) {
          return;
      }
      totals.compute(from, (key, current) -> {
          int balance = current == null ? 0 : current;
          if (balance < amount) {
              throw new IllegalStateException("transfer would drive " + key + " below zero");
          }
          return balance - amount;
      });
      totals.merge(to, amount, Integer::sum);
  }
  ```
- **Rationale**: Three triggers. (1) Two ingest workers run transfer(A, B) and transfer(B, A) at the same time: each thread holds its own `to` bin lock and blocks in `merge` on the other's bin, so both deadlock. (2) transfer("a", "a", 30) with a=100: the nested merge writes 70, then compute overwrites it with 130, so the debit is lost and money is created. (3) transfer("b", "b", 10) with b absent throws IllegalStateException("Recursive update"). Cases 2 and 3 were reproduced with this code in a scratch run on JDK 25.

### JAVA-50.1: A SQL query carrying untrusted data binds it as a parameter, never by concatenating it into the statement text
- **Severity**: Critical
- **Rule**: `JAVA-50` — OWASP SQL Injection Prevention Cheat Sheet, "Defense Option 1: Prepared Statements (with Parameterized Queries)"
- **Location**: `src/main/java/com/example/app/UserLookup.java` · `UserLookup#findNameByEmail`
- **Code**:
  ```java
  ResultSet rs = st.executeQuery("select name from users where email = '" + email + "'")) {
  ```
- **Problem**: The method parameter `email` is concatenated into the SQL text and executed through a plain `Statement`. The class doc-comment states that every parameter arrives from the request, so an untrusted value becomes part of the SQL instead of a bound parameter.
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
- **Rationale**: Concatenation removes the boundary between code and data. The database parses the request value as SQL, so an input such as `x' or '1'='1` changes what the query means and returns other users' rows. A `?` placeholder bound with `setString` makes the database read that same input as a literal string.
- **Also flagged by**: LOGIC

### JAVA-08.1: A check-then-act on a concurrent map is one atomic compute call, never a read followed by a put
- **Severity**: Major
- **Rule**: `JAVA-08` — `java.util.concurrent.ConcurrentHashMap` Javadoc, Java SE 21: `computeIfAbsent(K, Function)`, `compute(K, BiFunction)`, `merge(K, V, BiFunction)`
- **Location**: `src/main/java/com/example/app/Cache.java` · `Cache#getOrLoad`
- **Code**:
  ```java
          if (!cache.containsKey(key)) {
              cache.put(key, load(key));
  ```
- **Problem**: getOrLoad checks the shared ConcurrentHashMap field `cache` with containsKey and then calls put with a freshly loaded value. Those are two separate calls, and no lock or synchronized block covers both. The class doc says one instance serves every request thread, so two threads that ask for the same absent key can both pass the containsKey check, both call load, and both put. The second put overwrites the first thread's value, and the later cache.get(key) can return the other thread's value. This breaks project invariant 1, 'Cache values are loaded once'.
- **Suggested fix**:
  ```java
      public String getOrLoad(String key) {
          return cache.computeIfAbsent(key, this::load);
      }
  ```
- **Rationale**: A ConcurrentMap makes each method call atomic, but it does not make a sequence of calls atomic. Another thread can insert the key between containsKey and put, and the first thread's put then overwrites that thread's value. That is a lost update, and it shows up here as a duplicate load whose value flips between threads. computeIfAbsent runs the whole check-and-insert atomically, calls load at most once per key, and returns the value that won.

### LOGIC.3: getOrLoad runs a check-then-act on the shared ConcurrentHashMap. Two …
- **Severity**: Major
- **Rule**: `LOGIC` — logic and correctness pass (no card)
- **Location**: `src/main/java/com/example/app/Cache.java` · `Cache#getOrLoad`
- **Code**:
  ```java
          if (!cache.containsKey(key)) {
              cache.put(key, load(key));
          }
          return cache.get(key);
  ```
- **Problem**: getOrLoad runs a check-then-act on the shared ConcurrentHashMap. Two threads can both see containsKey false, both call load, and both put. The key is then loaded twice, and the second put overwrites the first, so the thread that put first can read back the other thread's value. This breaks project invariant 1 (a key is loaded once and both threads see the same value).
- **Suggested fix**:
  ```java
  public String getOrLoad(String key) {
      return cache.computeIfAbsent(key, this::load);
  }
  ```
- **Rationale**: The trigger is two request threads calling getOrLoad on the shared Cache with the same absent key at the same time. Each thread passes the containsKey check before either put lands. ConcurrentHashMap makes each single call atomic, but not the sequence containsKey, put, get. computeIfAbsent performs the load and the insert as one atomic step per key.
- **Also flagged by**: PROJ-1

### JAVA-17.1: A field shared between threads never holds a type whose Javadoc says it is not synchronized, such as SimpleDateFormat, HashMap, ArrayList or StringBuilder
- **Severity**: Major
- **Rule**: `JAVA-17` — `java.text.SimpleDateFormat` class Javadoc, Java SE 21, "Synchronization"
- **Location**: `src/main/java/com/example/app/Formatter.java` · `Formatter#remember`
- **Code**:
  ```java
      private final LinkedList<String> recent = new LinkedList<>();
  ...
          recent.add(value);
  ```
- **Problem**: Formatter is one instance shared by every request (its class doc says it formats values for every response, and the @Service singleton OrderService holds it through its constructor). Its field `recent` is a plain LinkedList. `remember` modifies that list structurally and `recentAt` reads it, and no lock covers either access. Two request threads can call `remember` concurrently, or one can call `remember` while another calls `recentAt`.
- **Suggested fix**:
  ```java
  private final List<String> recent = java.util.Collections.synchronizedList(new java.util.ArrayList<>());
  
  public String recentAt(int index) {
      return recent.get(index);
  }
  
  public void remember(String value) {
      recent.add(value);
  }
  ```
- **Rationale**: The LinkedList Javadoc says "this implementation is not synchronized" and that the list "must be synchronized externally" when several threads access it and at least one modifies it structurally. Concurrent `add` calls corrupt the list's node links and size count. The damage shows up later as a lost entry, a wrong element from `get`, or an exception far from the racing calls. The `final` modifier protects only the reference, not the list it points to.

### JAVA-179.1: A long-lived collection that gains an entry per request, session or key has a bound or an eviction rule
- **Severity**: Major
- **Rule**: `JAVA-179` — arXiv:1810.00101 (Ghanavati, Costa, Seboek, Lo, Andrzejak, "Memory and Resource Leak Defects and their Repairs in Java Projects", Empirical Software Engineerin…
- **Location**: `src/main/java/com/example/app/Formatter.java` · `Formatter#remember`
- **Code**:
  ```java
  private final LinkedList<String> recent = new LinkedList<>();
          recent.add(value);
  ```
- **Problem**: `Formatter#remember` adds one per-request value to the instance list `recent`, and nothing in the file removes it. The list has no size bound, no expiry and no removal path, because `recentAt` only reads it. `Formatter` is constructor-injected into the singleton `@Service` `OrderService`, so it lives as long as the process. Its class doc says each method runs once per request. The list therefore grows with every request served.
- **Suggested fix**:
  ```java
  private static final int MAX_RECENT = 100;
      private final LinkedList<String> recent = new LinkedList<>();
  
      public void remember(String value) {
          recent.add(value);
          if (recent.size() > MAX_RECENT) {
              recent.removeFirst();
          }
      }
  ```
- **Rationale**: `recent` is reachable from a singleton bean for the life of the process. Every String it holds is still referenced by the list, so the garbage collector can never reclaim those entries. Each request adds one entry and none is removed, so the heap fills over a long run until the process fails with OutOfMemoryError. Capping the list and evicting the eldest entry keeps its size steady.

### LOGIC.7: remember appends to an unsynchronized LinkedList that nothing ever …
- **Severity**: Major
- **Rule**: `LOGIC` — logic and correctness pass (no card)
- **Location**: `src/main/java/com/example/app/Formatter.java` · `Formatter#remember`
- **Code**:
  ```java
          recent.add(value);
  ```
- **Problem**: remember appends to an unsynchronized LinkedList that nothing ever trims. The class documentation says the methods run once per request, and the singleton OrderService keeps one Formatter instance for the life of the application. The list therefore grows with every request, and concurrent request threads mutate a LinkedList that is not thread-safe.
- **Suggested fix**:
  ```java
  private static final int RECENT_LIMIT = 100;
  
  public synchronized String recentAt(int index) {
      return recent.get(index);
  }
  
  public synchronized void remember(String value) {
      recent.addLast(value);
      if (recent.size() > RECENT_LIMIT) {
          recent.removeFirst();
      }
  }
  ```
- **Rationale**: The trigger is the shared Formatter, injected into the singleton @Service OrderService, receiving remember calls from request threads. Two threads adding at once can lose an element or corrupt the list's links and its size count, and recentAt can then throw or return the wrong element. Because no call ever removes entries, the list also grows without bound for as long as the process runs.
- **Verifier note**: I could not refute the defect, and the fix is sound. The severity moves from minor to major because the consequences the finding names are, on the scale, a resource leak that degrades over time and a concurrency defect that yields wrong results. Per the class contract on line 8, `remember` runs once per request against the one instance held by the singleton OrderService. Nothing ever removes from `recent`, so the heap grows for the life of the process, and concurrent `add` calls can corrupt the LinkedList's links and its size. One gap in the trigger: `git grep` at head finds no caller of `remember` or `recentAt`. OrderService stores the formatter but never calls it. The per-request use therefore comes from the doc comment on line 8, not from a call site in the diff.

### JAVA-133.1: A Stream returned by Files.lines, Files.list, Files.walk or Files.find, or a streaming query result, is closed by try-with-resources
- **Severity**: Major
- **Rule**: `JAVA-133` — `java.nio.file.Files#lines(Path, Charset)` Javadoc, Java SE 21
- **Location**: `src/main/java/com/example/app/LogScanner.java` · `LogScanner#countErrors`
- **Code**:
  ```java
  return Files.lines(path).filter(line -> line.contains("ERROR")).count();
  ```
- **Problem**: The stream returned by Files.lines(path) is not a try resource and is never closed: count() is its terminal operation, and the stream object is then dropped.
- **Suggested fix**:
  ```java
  try (Stream<String> lines = Files.lines(path)) {
      return lines.filter(line -> line.contains("ERROR")).count();
  }
  ```
- **Rationale**: The stream returned by Files.lines holds a reference to the open file, and only closing the stream closes that file. The terminal count() runs and drops the stream without closing it, so every call to countErrors leaves one more file descriptor open.

### LOGIC.4: countErrors never closes the Stream that Files.lines returns, so every …
- **Severity**: Major
- **Rule**: `LOGIC` — logic and correctness pass (no card)
- **Location**: `src/main/java/com/example/app/LogScanner.java` · `LogScanner#countErrors`
- **Code**:
  ```java
          return Files.lines(path).filter(line -> line.contains("ERROR")).count();
  ```
- **Problem**: countErrors never closes the Stream that Files.lines returns, so every call leaves the log file's handle open until garbage collection reclaims it. A second, related problem: a read or decoding failure partway through the file (for example, non-UTF-8 bytes in a log line) surfaces as UncheckedIOException out of count(). The method declares IOException, so a caller that handles IOException never sees that failure.
- **Suggested fix**:
  ```java
  public long countErrors(Path path) throws IOException {
      try (java.util.stream.Stream<String> lines = Files.lines(path)) {
          return lines.filter(line -> line.contains("ERROR")).count();
      } catch (java.io.UncheckedIOException e) {
          throw e.getCause();
      }
  }
  ```
- **Rationale**: Every call leaks one file descriptor. Repeated scans can exhaust the process's descriptor limit and fail with "Too many open files", and on Windows the open handle blocks log rotation or deletion. A log file containing a malformed byte sequence makes the lazy reader throw UncheckedIOException during count(), and that exception bypasses the declared IOException contract.

### JAVA-132.1: Every AutoCloseable that holds an I/O handle is opened in a try-with-resources statement, so it closes on every exit path
- **Severity**: Major
- **Rule**: `JAVA-132` — `java.lang.AutoCloseable` Javadoc, Java SE 21
- **Location**: `src/main/java/com/example/app/Repo.java` · `Repo#findNameByEmail`
- **Code**:
  ```java
          Connection c = dataSource.getConnection();
  ```
- **Problem**: findNameByEmail opens a Connection, a PreparedStatement and a ResultSet as plain locals and closes them by explicit close() calls after the work, with no try resource header and no finally. If ps.setString, ps.executeQuery, rs.next or rs.getString throws an SQLException, the method exits before rs.close(), ps.close() and c.close() run, so all three handles leak.
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
- **Rationale**: The close() calls run only when the work returns normally. On the exception path, for example a failing executeQuery or rs.next, the pooled JDBC connection and its statement are never returned to the DataSource pool. Under repeated failures the leaked connections pile up until the pool is exhausted, and after that every later getConnection call blocks or fails. A try-with-resources header closes ResultSet, then PreparedStatement, then Connection on every exit path, and it attaches any exception thrown by close() as a suppressed exception.

### LOGIC.5: The connection, statement and result set are closed only on the success …
- **Severity**: Major
- **Rule**: `LOGIC` — logic and correctness pass (no card)
- **Location**: `src/main/java/com/example/app/Repo.java` · `Repo#findNameByEmail`
- **Code**:
  ```java
          Connection c = dataSource.getConnection();
          PreparedStatement ps = c.prepareStatement("select name from users where email = ?");
          ps.setString(1, email);
          ResultSet rs = ps.executeQuery();
          String name = rs.next() ? rs.getString(1) : null;
          rs.close();
          ps.close();
          c.close();
  ```
- **Problem**: The connection, statement and result set are closed only on the success path; if prepareStatement, setString, executeQuery, next or getString throws SQLException, none of the close() calls runs and the pooled connection is never returned. The sibling methods count() and countActive() in the same class use try-with-resources.
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
- **Rationale**: Any SQLException during the lookup (query timeout, lost connection, constraint on a bad parameter) skips c.close(). The caller OrderService#loadName catches that SQLException and rethrows IllegalStateException, so the failure is an expected, recoverable path; each occurrence leaks one connection from the DataSource pool until the pool is exhausted and every later getConnection() blocks or fails.

### JAVA-134.1: A ThreadLocal set on a pooled thread is removed in a finally block, and set(null) is not a removal
- **Severity**: Major
- **Rule**: `JAVA-134` — `java.lang.ThreadLocal` Javadoc, Java SE 21 — class
- **Location**: `src/main/java/com/example/app/RequestContext.java` · `RequestContext#handle`
- **Code**:
  ```java
          CURRENT_USER.set(user);
          process();
          CURRENT_USER.set(null);
  ```
- **Problem**: RequestContext#handle sets the CURRENT_USER thread-local on the handler thread and clears it only with set(null) after process() returns. There is no try/finally, so if process() throws, the user id stays on the thread. On the normal path, set(null) leaves the thread-local entry in the thread's map rather than removing it.
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
- **Rationale**: A pooled request-handler thread keeps its ThreadLocal entry for as long as the thread lives. If process() throws, the request's user id outlives this unit of work, and the next request served on that thread reads the wrong user through RequestContext.currentUser(). On the normal path, set(null) writes null into the existing entry instead of deleting it. The entry and its ThreadLocal key therefore stay in the thread's map. Only remove() inside a finally block covers every exit.
- **Also flagged by**: LOGIC

### JAVA-09.1: A read-modify-write on a shared field is an atomic operation, never a plain or volatile increment
- **Severity**: Major
- **Rule**: `JAVA-09` — jcstress `jcstress-samples/src/main/java/org/openjdk/jcstress/samples/api/API_01_Simple.java` (fetched, `master`) — two actors run `++v` on a plain `int`
- **Location**: `src/main/java/com/example/app/Stats.java` · `Stats#hit`
- **Code**:
  ```java
  private volatile int hits;
  ...
          hits++;
  ```
- **Problem**: `Stats#hit` increments the `volatile int hits` field with `hits++` and holds no lock. The class doc says every handler thread shares a `Stats` instance, so two threads can run the read-add-write at the same time and one increment is lost.
- **Suggested fix**:
  ```java
  private final java.util.concurrent.atomic.AtomicInteger hits = new java.util.concurrent.atomic.AtomicInteger();
  
      public void hit() {
          hits.incrementAndGet();
      }
  
      public int hits() {
          return hits.get();
      }
  ```
- **Rationale**: `hits++` runs as three steps: read, add, write. When two threads interleave them, both read the same value and both write the same result, so one increment is lost. `volatile` orders and publishes each single read and each single write, but it does not join the two into one operation. `incrementAndGet` performs the update as one atomic read-modify-write. The project context's lost-increment tolerance names only `Stats#sample`, so it does not cover `hits`.

### LOGIC.6: `hits` is volatile, but `hits++` is a separate read, add and write. …
- **Severity**: Major
- **Rule**: `LOGIC` — logic and correctness pass (no card)
- **Location**: `src/main/java/com/example/app/Stats.java` · `Stats#hit`
- **Code**:
  ```java
          hits++;
  ```
- **Problem**: `hits` is volatile, but `hits++` is a separate read, add and write. Concurrent handler threads that call hit() overwrite each other's increments, so hits() undercounts.
- **Suggested fix**:
  ```java
  private final java.util.concurrent.atomic.AtomicInteger hits = new java.util.concurrent.atomic.AtomicInteger();
  
  public void hit() {
      hits.incrementAndGet();
  }
  
  public int hits() {
      return hits.get();
  }
  ```
- **Rationale**: Trigger: two handler threads call hit() at once. Both read 5 and both write 6, so one hit is lost. The class doc says every handler thread shares Stats. The project context accepts lost increments only for Stats#sample, not for hits, and the sibling counter `total` is updated under synchronized.

### JAVA-135.1: Arithmetic whose overflow would corrupt a balance, a size or a count uses Math.addExact, multiplyExact or toIntExact, never a silently wrapping operator
- **Severity**: Major
- **Rule**: `JAVA-135` — `java.lang.Math#addExact(int, int)`, `#addExact(long, long)`, `#multiplyExact`, `#subtractExact`, `#toIntExact(long)` Javadoc, Java SE 21
- **Location**: `src/main/java/com/example/app/Totals.java` · `Totals#addWithinLimit`
- **Code**:
  ```java
  int next = base + amount;
  ```
- **Problem**: The new balance is a plain int addition of the stored balance and an unchecked int amount. The limit cap runs after the addition, so it does not bound the operands. On overflow `next` wraps to a large negative value, Math.min(next, limit) passes it through as below the limit, and compute() stores it as the balance.
- **Suggested fix**:
  ```java
  int next = Math.addExact(base, amount);
  ```
- **Rationale**: An int `+` wraps on overflow without throwing. The account balance wraps to a negative number, and the limit check treats that number as a valid value under the cap, so the corrupted balance is written to `totals`. Math.addExact throws ArithmeticException before the cap runs and before the store.

### JAVA-11.1: A function passed to compute, computeIfAbsent or merge never updates the same concurrent map
- **Severity**: Major
- **Rule**: `JAVA-11` — `java.util.concurrent.ConcurrentHashMap#computeIfAbsent`, `#compute` Javadoc, Java SE 21
- **Location**: `src/main/java/com/example/app/Totals.java` · `Totals#transfer`
- **Code**:
  ```java
  totals.compute(to, (key, current) -> {
              totals.merge(from, -amount, Integer::sum);
  ```
- **Problem**: The remapping function passed to `totals.compute(to, ...)` calls `totals.merge(from, ...)`, which updates the same ConcurrentHashMap from inside the function.
- **Suggested fix**:
  ```java
  public void transfer(String from, String to, int amount) {
          totals.merge(from, -amount, Integer::sum);
          totals.merge(to, amount, Integer::sum);
      }
  ```
- **Rationale**: ConcurrentHashMap runs the remapping function while it holds the monitor of the bin that owns `to`, and its contract forbids the function from modifying the map. The nested `merge` is a recursive update. When `from` falls into the same bin, the map either throws IllegalStateException("Recursive update") or lets the nested update through, depending on the bin's state. When `from` falls into a different bin, the nested call takes a second bin lock while still holding the first. Two ingest workers running `transfer(a, b)` and `transfer(b, a)` then each hold one bin and wait for the other, so both calls deadlock and never complete.
- **Verifier note**: The defect, location, quoted code, fix and severity all stand. One part of the rationale is wrong: the claim that the nested call hangs "when `from` hashes to the bin already held" because it "waits on the bin the calling thread holds". Java `synchronized` is reentrant, so a thread never blocks on a bin it already holds. When `from` lands in the same bin, the nested `merge` either throws `IllegalStateException` (empty bin holding a `ReservationNode`, or the `pred.next != null` check in `compute`) or completes. The real hang involves two threads. When `from` and `to` sit in different bins, `transfer(a, b)` on one worker holds bin(b) and waits for bin(a). At the same time `transfer(b, a)` on another worker holds bin(a) and waits for bin(b), and the two deadlock. The class doc says the totals are "updated concurrently by the ingest workers", so this case is reachable. The corrected rationale below states that mechanism. Separately, invariant 4 (reject negative balances) is enforced neither by the original `transfer` nor by the fix. That is outside JAVA-11, and the fix does not make it worse.

### JAVA-135.2: Arithmetic whose overflow would corrupt a balance, a size or a count uses Math.addExact, multiplyExact or toIntExact, never a silently wrapping operator
- **Severity**: Major
- **Rule**: `JAVA-135` — `java.lang.Math#addExact(int, int)`, `#addExact(long, long)`, `#multiplyExact`, `#subtractExact`, `#toIntExact(long)` Javadoc, Java SE 21
- **Location**: `src/main/java/com/example/app/Totals.java` · `Totals#transfer`
- **Code**:
  ```java
  return (current == null ? 0 : current) + amount;
  ```
- **Problem**: The credit to the receiving account's balance is a plain int addition. `amount` is an unchecked int parameter. A receiving balance near Integer.MAX_VALUE plus a positive amount wraps to a large negative value, and compute() stores that value as the account's balance.
- **Suggested fix**:
  ```java
  totals.compute(to, (key, current) -> {
      int credited = Math.addExact(current == null ? 0 : current, amount);
      totals.merge(from, -amount, Integer::sum);
      return credited;
  });
  ```
- **Rationale**: An int `+` wraps on overflow and throws nothing. The receiving balance wraps past Integer.MAX_VALUE to a negative number, which breaks Invariant 4, and that value is written into `totals` as if it were correct. Math.addExact throws ArithmeticException instead. The exact sum has to be computed before the debit of `from`: then the exception aborts the remapping function before either balance changes, and the transfer does not end half-applied.
- **Verifier note**: The defect is real and major is the right severity. The int credit can wrap with inputs the method accepts, and the wrapped balance would be stored. The fix needs a correction. In the proposed fix, `totals.merge(from, -amount, ...)` on line 16 commits the debit before Math.addExact runs on line 17. On overflow, addExact throws and compute() leaves `to` unchanged, but `from` stays debited. The transfer ends half-applied, so the rationale's claim that "the stored balance stays unchanged" is true only for the receiving account. The corrected fix computes the checked credit before the debit, so an overflow aborts before any mapping changes. I compiled this version with javac 25 in a scratchpad directory outside the repo. The fix keeps the nested merge inside compute() and the unchecked `-amount` on the debit. Both lie outside this finding.

### JAVA-80.1: A security-relevant random value comes from SecureRandom, never from java.util.Random, ThreadLocalRandom, Math.random or a name-based UUID
- **Severity**: Major
- **Rule**: `JAVA-80` — `java.util.Random` class Javadoc, Java SE 21 (fetched `src/java.base/share/classes/java/util/Random.java`) — 48-bit seed, linear congruential formula, period 2…
- **Location**: `src/main/java/com/example/app/UserLookup.java` · `UserLookup#newPasswordResetToken`
- **Code**:
  ```java
  Random random = new Random();
  ```
- **Problem**: The password-reset token is built from two nextLong() calls of a java.util.Random, a non-cryptographic generator, so the token a client receives as a credential is predictable.
- **Suggested fix**:
  ```java
  public String newPasswordResetToken() {
          byte[] bytes = new byte[32];
          secureRandom.nextBytes(bytes);
          return java.util.HexFormat.of().formatHex(bytes);
      }
  ```
- **Rationale**: java.util.Random is a 48-bit-seed linear congruential generator whose documentation states it is not cryptographically secure; an attacker who observes earlier output can predict later values, so the reset token drawn from it is guessable. SecureRandom, already held in the secureRandom field, is self-seeded from the platform entropy source.
- **Also flagged by**: LOGIC

### JAVA-53.1: An external command runs through ProcessBuilder or exec(String[]) with each argument as its own element, never through Runtime.exec(String) or a shell -c string
- **Severity**: Major _(downgraded from critical)_
- **Rule**: `JAVA-53` — `java.lang.Runtime#exec(String)` Javadoc, Java SE 21
- **Location**: `src/main/java/com/example/app/UserLookup.java` · `UserLookup#convertAvatar`
- **Code**:
  ```java
  return Runtime.getRuntime().exec("sh -c 'convert " + uploadedFile + " avatar.png'");
  ```
- **Problem**: The class doc says `uploadedFile` comes from the request. The code concatenates it into one command string and passes that string to `Runtime.exec(String)`, which splits it on whitespace. The string is also written as a `sh -c` invocation, so the code aims request data at a shell.
- **Suggested fix**:
  ```java
  return new ProcessBuilder("convert", "--", uploadedFile, "avatar.png").start();
  ```
- **Rationale**: `Runtime.exec(String)` splits the string with a `StringTokenizer` and does not interpret quotes. `sh` therefore always gets the constant script `'convert`, which has an unterminated quote, and the request value lands only in the positional parameters. The method fails with a shell syntax error on every call and never converts the avatar. The intended shell form is still the injection pattern: the natural repair `{"sh","-c","convert " + uploadedFile + ...}` would let `;`, `|` and backticks in a filename run arbitrary commands. As an argument vector, `ProcessBuilder` keeps the value as one element that no shell parses, and `--` stops option injection.
- **Verifier note**: I could not refute the finding. The line does break JAVA-53: the request value reaches a command through `Runtime.exec(String)`'s whitespace tokenizer, and the proposed fix compiles and is correct.

I moved the severity because the finding's rationale describes something this code cannot do. The tokenizer always gives `sh -c` the fixed script token `'convert`, which has an unterminated quote. The request value only ever becomes positional parameters ($0, $1, …) of that script. So `;`, `|` and backticks in the value never reach a shell parser, and no extra arguments reach `convert`. The real effect is that the shell fails on a syntax error every time, so `convertAvatar` never converts anything. That is a correctness bug.

The injection is latent. The obvious repair for "convert never runs" is to pass `{"sh","-c","convert " + uploadedFile + " avatar.png"}` as an array, and that repair would turn the line into a remote code execution. Both effects fall under major on the scale: a correctness bug, and a security defect that needs a specific condition.

I have not checked that ImageMagick `convert` treats `--` as the end of options. The `--` in the fix follows the card's prescribed form.
- **Also flagged by**: LOGIC

## Minor & Suggestions

| # | Severity | Rule | Location | Finding | Suggested fix |
|---|---|---|---|---|---|
| META-01.1 | Minor | `META-01` | `.claude/software-craft/config.md` · `Inv 2` | Invariant 2 is an allocation rule graded only by the adjectives `cheap` and `large`. Neither the invariant nor any definitions or scale section of the config gives a per-call byte budget or the rate at which `Cache#load` runs. Naming `CacheLoadBench` names a check, but the config states no threshold that check enforces. | 2. **Cache loads stay under <B> bytes per call**: No single allocation inside `Cache#load` exceeds <B> bytes; `Cache#load` runs ~<R> times per second at peak, so every <B> bytes allocated per call is ~<B×R> bytes/s of churn. `CacheLoadBench` fails above <B> bytes allocated per call. Violation: an allocation over <B> bytes inside `Cache#load`. |
| META-05.1 | Minor | `META-05` | `.claude/software-craft/config.md` · `Inv 3` | The rule clause of numbered invariant 3 is a recommendation, not an obligation: both its name ("prefer") and its body ("should take") use recommendation wording, and it names no enforcement. A reviewer therefore cannot fail a diff on it. | 3. **Repositories take dependencies through the constructor**: No repository class declares `@Autowired` on a field; every dependency arrives as a constructor parameter. Violation: a field-injected repository (`@Autowired` on a field). Enforced by ArchUnit rule `RepositoriesUseConstructorInjection` (to be added). |
| META-08.1 | Minor | `META-08` | `.claude/software-craft/config.md` · `Invariants` | The diff adds a rule on code as a prose sentence after the numbered list. It has no invariant number and no `Violation:` clause, and it does not sit under a tolerances, definitions or rationale heading. | 5. **Production classes write no console output**: No production class references `System.out`. Violation: a `System.out` call in a class under the production source tree. |
| JAVA-115.1 | Minor | `JAVA-115` | `src/main/java/com/example/app/Formatter.java` · `Formatter#isUpperCase` | isUpperCase compiles the constant regular expression "^[A-Z]+$" inside the method body. Per the class doc, the method runs on every request, so the expression is recompiled on each call. The sibling isDigits already uses a static DIGITS pattern. | private static final Pattern UPPER_CASE = Pattern.compile("^[A-Z]+$");  public boolean isUpperCase(String value) {     return UPPER_CASE.matcher(value).matches(); } |
| JAVA-110.1 | Minor | `JAVA-110` | `src/main/java/com/example/app/Formatter.java` · `Formatter#joinAll` | joinAll declares the String accumulator `out` outside the for-each loop and grows it by `+=` twice per iteration, so every append creates a new String. The class doc says the method runs on every request, and the size of `parts` is unbounded. | public String joinAll(List<String> parts) {         StringBuilder out = new StringBuilder();         for (String part : parts) {             out.append(part).append(',');         }         return out.toString();     } |
| JAVA-101.1 | Minor | `JAVA-101` | `src/main/java/com/example/app/Formatter.java` · `Formatter#recent` | The `recent` list is a LinkedList read by index through `recentAt(int)` (`recent.get(index)`). The class doc says each method runs once per request, so this indexed read sits on a per-request path. No ListIterator at the cursor touches this field, so the exemption does not apply. |     private final List<String> recent = new ArrayList<>(); |
| JAVA-212.1 | Minor | `JAVA-212` | `src/main/java/com/example/app/OrderService.java` · `OrderService#loadName` | The catch block in OrderService#loadName logs the SQLException with its stack trace and also rethrows it wrapped in an IllegalStateException. OrderService is an intermediate service layer, not a boundary handler: it neither returns a fallback nor terminates the process. | } catch (java.sql.SQLException e) {             throw new IllegalStateException("lookup failed for " + email, e);         } |
| JAVA-192.1 | Minor | `JAVA-192` | `src/main/java/com/example/app/OrderService.java` · `OrderService#render` | The public method `render` tests its boolean parameter `forEmail` in `if (forEmail)` to choose between two paths: it either wraps the order in HTML or returns it unchanged. The boolean is a selector, not data. | public String renderForEmail(String order) {     return "<p>" + order + "</p>"; }  public String renderPlain(String order) {     return order; } |
| JAVA-224.1 | Minor | `JAVA-224` | `src/main/java/com/example/app/OrderService.java` · `OrderService#repo` | The @Service bean OrderService receives its required collaborator Repo by @Autowired field injection into a non-final field, while Formatter already arrives through the constructor; loadName and loadCount dereference repo unconditionally, so the dependency is required, not optional. |     private final Repo repo;     private final Formatter formatter;     private boolean archived;      public OrderService(Repo repo, Formatter formatter) {         this.repo = repo;         this.formatter = formatter;     } |
| JAVA-18.1 | Minor | `JAVA-18` | `src/main/java/com/example/app/OrderService.java` · `OrderService#setArchived` | The `@Service` bean is a Spring singleton (it has no `@Scope`). It declares the non-final, unsynchronized instance field `archived`, and the public method `setArchived` writes that field from whatever request thread calls it. Nothing reads the field yet. | @Service public class OrderService {     private static final Logger log = LoggerFactory.getLogger(OrderService.class);      @Autowired     private Repo repo;      private final Formatter formatter;      public OrderService(Formatter formatter) {         this.formatter = formatter;     }      // the archived flag belongs to one request's order, so it travels as an argument     public String render(String order, boolean forEmail, boolean archived) {         String body = archived ? "[archived] " + order : order;         return forEmail ? "<p>" + body + "</p>" : body;     }      // loadName and loadCount unchanged } |
| PROJ-3.1 | Minor | `PROJ-3` | `src/main/java/com/example/app/OrderService.java` · `OrderService#repo` | The new OrderService injects the repository `Repo` through a mutable field annotated `@Autowired`, while its other dependency, `Formatter`, arrives through the constructor. A field-injected repository is the exact forbidden state that invariant 3 names. `Repo` itself takes its `DataSource` through its constructor, so the violation is in how the repository is wired into its consumer. | private final Repo repo;     private final Formatter formatter;     private boolean archived;      public OrderService(Repo repo, Formatter formatter) {         this.repo = repo;         this.formatter = formatter;     } |
| JAVA-199.1 | Minor | `JAVA-199` | `src/main/java/com/example/app/Repo.java` · `Repo#countActive` | The added body of Repo#countActive (head lines 38-42) is a copy of the existing Repo#count body (head lines 18-22, starting `try (Connection c = dataSource.getConnection();`). The two blocks have the same three try-with-resources declarations and the same `return rs.next() ? rs.getInt(1) : 0;`. They differ only in the SQL string literal. | public int count() throws SQLException {     return queryCount("select count(*) from users"); }  public int countActive() throws SQLException {     return queryCount("select count(*) from users where active = true"); }  private int queryCount(String sql) throws SQLException {     try (Connection c = dataSource.getConnection();          PreparedStatement ps = c.prepareStatement(sql);          ResultSet rs = ps.executeQuery()) {         return rs.next() ? rs.getInt(1) : 0;     } } |
| JAVA-05.1 | Minor | `JAVA-05` | `src/main/java/com/example/app/Stats.java` · `Stats#record` | The added `record()` is a `synchronized` method, so its monitor is the `Stats` instance itself. `Stats` is a public, non-final class whose instances every handler thread shares, so any code holding a reference can lock that same monitor. | private final Object lock = new Object();  public long total() {     synchronized (lock) {         return total;     } }  public void record() {     synchronized (lock) {         total++;     } } |
| JAVA-228.1 | Minor | `JAVA-228` | `src/main/java/com/example/app/Totals.java` · `Totals#mirror` | `mirror` takes two adjacent `String` parameters with different roles: `account` is the balance that gets overwritten, and `sibling` is the balance that gets copied. Swapping them still compiles and overwrites the sibling with the account's balance. | public void mirror(String target, String source) {     totals.compute(target, (key, current) -> {         Integer other = totals.get(source);         return other == null ? current : other;     }); } // and at each call site: mirror(/* target= */ account, /* source= */ sibling) |
| JAVA-228.2 | Minor | `JAVA-228` | `src/main/java/com/example/app/Totals.java` · `Totals#transfer` | `transfer` takes two adjacent `String` parameters with opposite meanings: `from` is the debited account and `to` is the credited one. A caller that passes them in the wrong order still compiles and moves the money the wrong way. | public record AccountId(String value) {     public AccountId {         if (value == null \|\| value.isBlank()) throw new IllegalArgumentException("account id");     } }  /** Second step of a transfer: names the credited account, e.g. {@code totals.debit(alice, 100).creditTo(bob)}. */ @FunctionalInterface public interface PendingTransfer { void creditTo(AccountId to); }  public PendingTransfer debit(AccountId from, int amount) {     return to -> { /* move amount from `from` to `to` */ }; } // where no wrapper is wanted: keep transfer(String from, String to, int amount) // and name the arguments at each call site: transfer(/* from= */ a, /* to= */ b, amount) |
| JAVA-219.1 | Suggestion | `JAVA-219` | `src/main/java/com/example/app/Cache.java` · `Cache` | The added public method Cache#getOrLoad carries no Javadoc summary. Its signature does not say whether a key is loaded once under concurrent callers, nor what is returned when the loader yields null. The sibling Cache#buildIndex added in the same hunk is documented. |     /**      * Returns the cached value for {@code key}, loading and caching it on first request.      *      * @param key the cache key; must not be null      * @return the cached or freshly loaded value      */     public String getOrLoad(String key) { |
| JAVA-219.2 | Suggestion | `JAVA-219` | `src/main/java/com/example/app/Formatter.java` · `Formatter` | Six added public methods have no Javadoc summary. isUpperCase and isDigits accept only non-empty ASCII A-Z and 0-9 and throw on null. joinAll and joinWithBuilder append a trailing comma. recentAt does not state its index base or its bounds behaviour. remember does not state whether the list is bounded or thread-safe. Formatter#separate is documented. |     /**      * Tells whether {@code value} is a non-empty run of ASCII capital letters {@code A-Z}.      *      * @param value the text to test; must not be null      * @return true only for one or more characters in {@code A-Z}      */     public boolean isUpperCase(String value) { |
| JAVA-219.3 | Suggestion | `JAVA-219` | `src/main/java/com/example/app/LogScanner.java` · `LogScanner` | The added public methods countErrors and countErrorsIn have no Javadoc summary. Neither says what counts as an error line: a line containing the case-sensitive substring "ERROR". countErrors also does not say that the file is decoded as UTF-8, or which exception reports which failure. IOException covers only a failure to open the file. Read failures and malformed input surface as UncheckedIOException. | /**  * Counts the lines of the file at {@code path} that contain the case-sensitive substring {@code "ERROR"}.  * The file is decoded as UTF-8.  *  * @param path the log file to scan  * @return the number of matching lines  * @throws IOException if the file cannot be opened  * @throws java.io.UncheckedIOException if reading fails after the file is opened, or the file is not valid UTF-8  */ public long countErrors(Path path) throws IOException { |
| JAVA-219.4 | Suggestion | `JAVA-219` | `src/main/java/com/example/app/OrderService.java` · `OrderService` | Three added public methods have no Javadoc summary. render does not say that forEmail wraps the order in an HTML paragraph. loadName does not say that it returns null for an unknown email or that it throws IllegalStateException on a lookup failure. loadCount does not state its failure mode either. The constructor and the setter setArchived are self-explanatory and are not flagged. |     /**      * Renders an order as plain text, or wrapped in an HTML paragraph when it goes into an email.      *      * @param order the order text to render      * @param forEmail true to wrap the text in {@code <p>} for an HTML email body      * @return the rendered order      */     public String render(String order, boolean forEmail) { |
| JAVA-211.1 | Suggestion | `JAVA-211` | `src/main/java/com/example/app/OrderService.java` · `OrderService#OrderService` | The public constructor stores the reference parameter `formatter` into a final field without a null check at entry. The class is a Spring `@Service`, so the container normally supplies the argument (a lower-value site under the card's Limits), but a direct `new OrderService(null)` call still goes through unchecked. | public OrderService(Formatter formatter) {         this.formatter = java.util.Objects.requireNonNull(formatter, "formatter");     } |
| JAVA-219.5 | Suggestion | `JAVA-219` | `src/main/java/com/example/app/Repo.java` · `Repo` | The added public methods findNameByEmail and countActive have no Javadoc summary. findNameByEmail does not state that it returns null when no user matches. countActive does not state which users count as active. |     /**      * Looks up the name of the user registered under {@code email}.      *      * @param email the user's email address      * @return the user's name, or {@code null} when no user has this email      * @throws SQLException if the query fails      */     public String findNameByEmail(String email) throws SQLException { |
| JAVA-219.6 | Suggestion | `JAVA-219` | `src/main/java/com/example/app/RequestContext.java` · `RequestContext` | The added public methods handle and handleSafely have no Javadoc summary. Nothing tells a caller how the two differ. handleSafely clears the thread-local user even when process throws, and handle leaves it set on failure. |     /**      * Runs the request as {@code user}, binding the user to the current thread for the call.      * The binding is not cleared if processing throws; prefer {@link #handleSafely(String)}.      *      * @param user the user the request runs as      */     public void handle(String user) { |
| JAVA-219.7 | Suggestion | `JAVA-219` | `src/main/java/com/example/app/Stats.java` · `Stats` | The added public methods hit and record have no Javadoc summary. hit does not say whether it is safe to call from several handler threads at once, or whether its count is exact. record does not say what it records or how it relates to total(). The getter hits() is self-explanatory, and Stats#sample is documented. | /**  * Counts one hit. Safe to call from any handler thread; every call is counted.  * (The contract needs an atomic counter: {@code volatile int} with {@code hits++} loses increments.)  */ public void hit() { |
| JAVA-219.8 | Suggestion | `JAVA-219` | `src/main/java/com/example/app/Totals.java` · `Totals` | The added public methods transfer and addWithinLimit have no Javadoc summary. transfer does not state whether it rejects a transfer that would drive the source balance below zero, the rule that project invariant 4 sets. addWithinLimit does not say that it silently caps the total at the account's limit. Totals#mirror is documented. | /**  * Moves {@code amount} from account {@code from} to account {@code to}.  *  * @param from the debited account  * @param to the credited account  * @param amount the amount to move  */ public void transfer(String from, String to, int amount) { // Add "@throws IllegalArgumentException if the transfer would make the balance of {@code from} negative" // only in the same change as the guard that enforces invariant 4; the code at head never throws. |
| JAVA-219.9 | Suggestion | `JAVA-219` | `src/main/java/com/example/app/UserLookup.java` · `UserLookup` | Six added public methods have no Javadoc summary: findNameByEmail, findNameById, convertAvatar, convertAvatarSafely, newPasswordResetToken and newSessionId. None states that the lookups return null when nothing matches. None states what the conversions return or where they write avatar.png. None says whether the generated tokens are cryptographically unguessable. sampleAvatarIndex is documented, and the injection constructor is self-explanatory. |     /**      * Looks up the name of the user registered under {@code email}.      *      * @param email the user's email address, taken from the request      * @return the user's name, or {@code null} when no user has this email      * @throws SQLException if the query fails      */     public String findNameByEmail(String email) throws SQLException { |
| JAVA-211.2 | Suggestion | `JAVA-211` | `src/main/java/com/example/app/UserLookup.java` · `UserLookup#UserLookup` | The public constructor stores the reference parameter `dataSource` into a final field without validating it at entry, so `new UserLookup(null)` builds an object that looks valid. | public UserLookup(DataSource dataSource) {         this.dataSource = java.util.Objects.requireNonNull(dataSource, "dataSource");     } |

