# Fixture dry run (committed mode) Craft Review

## Executive Summary
- Reviewed: `80758d8da61b836367093349f4d73e8cd290cc65...e7a757c5a9002899a7bef9bf2fb131204b7eb098` (committed) — 34 files (MEDIUM); languages: go 7, java 7, python 8, rust 3, typescript 9
- Passes: find in 6 parts (98 finders), aggregate, verify in 6 parts (68 skeptics)
- Findings: 68 (19 major, 43 minor, 6 suggestion)
- Verification: 68 raw findings → 68 confirmed, 0 downgraded, 0 rejected, 0 flagged for the author
- Fix round: none
- Recommendation: Fix before merge

## Major Findings

### ERR-07.1: An error returned as a value, a status result, a future or a promise is checked, propagated, or discarded explicitly with a comment stating why that is safe
- **Severity**: Major
- **Rule**: `ERR-07` — - CWE-252 Unchecked Return Value (CWE 4.19) — "The product does not check the return value from a method or function, which can prevent it from detecting unexpected states and conditions."; "Two common programmer assumptions are "this function call can never fail" and "it doesn't matter if this function call fails"."; mitigation, effectiveness High: "Check the results of all functions that return a value and verify that the value is expected." (fetched)
- **Location**: `code/go/stock_http.go` · `Stockroom.ServeStockLevels`
- **Code**:
  ```go
  	fmt.Fprintf(w, "%s on_hand=%d reserved=%d\n", sku, level, s.reserved[sku])
  ```
- **Problem**: The added handler line calls fmt.Fprintf on an http.ResponseWriter and drops the (int, error) it returns. The call stands as a bare statement with no check and no explicit discard. The destination is a network response, not standard output or standard error. It is also not an in-memory buffer like the strings.Builder writes on lines 34, 56 and 59, which cannot fail and are correctly left alone. So the print exemption does not apply, and nothing explains why the error is dropped.
- **Suggested fix**:
  ```go
  	if _, err := fmt.Fprintf(w, "%s on_hand=%d reserved=%d\n", sku, level, s.reserved[sku]); err != nil {
  		// The 200 status is already committed, so the failed body write can only be recorded, not reported to the client.
  		log.Printf("serve stock level of %s: %v", sku, err) // add "log" to the file's imports
  	}
  ```
- **Rationale**: Unchecked return value (CWE-252): ResponseWriter.Write reports a failed body write through the error that Fprintf passes back, for example when the client has disconnected, when a TimeoutHandler returns http.ErrHandlerTimeout, or with ErrHijacked or ErrBodyNotAllowed. Because the error is ignored, the handler returns as if the stock level reached the client. Nothing is logged or counted, so a client that never got its answer leaves no server-side trace, and the failure only shows up later, far from its cause.

### CODE-01.1: A name never promises a type, a return value or a plurality that its own declaration contradicts
- **Severity**: Major
- **Rule**: `CODE-01` — - PMD rule `LinguisticNaming`, category codestyle (fetched): "It checks for fields, that are named, as if they should be boolean but have a different type. It also checks for methods, that according to their name, should return a boolean, but don't. Further, it checks, that getters return something and setters won't." Defaults: predicate prefixes is, has, can, have, will, should; transform prefixes to, as, with the infix check "disabled by default, since this detection is prone to false positives"; methods annotated as overrides ignored by default; a setter returning its enclosing type not flagged; only method, field and local-variable declarations visited, not parameters.
- **Location**: `code/java/InvoiceLedger.java` · `InvoiceLedger#hasOpenDisputes`
- **Code**:
  ```java
      int hasOpenDisputes(Invoice invoice) {
  ```
- **Problem**: The routine name opens with the predicate word 'has', which promises a boolean, but the declared return type is int (the count of unresolved disputes). It has no doc comment stating that it returns a count, and it is not inherited: InvoiceLedger has no supertype or interface.
- **Suggested fix**:
  ```java
      int countOpenDisputes(Invoice invoice) {
  ```
- **Rationale**: The word 'has' promises a yes/no answer, while the int return type allows a range of values that nothing documents. Every call site reads the name far from the declaration, so a reader takes it for a boolean test. This is the linguistic antipattern where a predicate-named routine does not return a boolean, and that mismatch raises the reader's cognitive load. The fix is to rename it to match the count it returns, or to keep the name and change it to return boolean (unresolved count > 0).

### LOGIC.1: reconcilePayments looks up each invoice inside the loop that applies the …
- **Severity**: Major
- **Rule**: `LOGIC` — logic and correctness pass (no card)
- **Location**: `code/java/InvoiceLedger.java` · `InvoiceLedger#reconcilePayments`
- **Code**:
  ```java
  Invoice invoice = invoiceFor(payment);
  ```
- **Problem**: reconcilePayments looks up each invoice inside the loop that applies the payments and sends receipts. If one payment names an unknown invoice, invoiceFor throws UnknownInvoiceException after every earlier payment has already been recorded and receipted. The reconciliation audit entry and the reminders are then never written, so the ledger is left half-reconciled.
- **Suggested fix**:
  ```java
  void reconcilePayments(Customer customer, List<Payment> payments) {
      List<Invoice> invoices = new ArrayList<>(payments.size());
      for (Payment payment : payments) {
          invoices.add(invoiceFor(payment)); // reject the batch before anything is applied
      }
      BigDecimal balanceBefore = balanceOf(customer);
      for (int i = 0; i < payments.size(); i++) {
          Payment payment = payments.get(i);
          Invoice invoice = invoices.get(i);
          invoice.recordPayment(payment.amount());
          receipts.send(customer.email(), invoice.number(), payment.amount());
      }
  
      List<Invoice> stillOpen = unpaidInvoicesOf(customer);
      if (!stillOpen.isEmpty()) {
          reminders.schedule(customer, stillOpen);
      }
  
      auditTrail.recordReconciliation(customer.id(), balanceBefore, balanceOf(customer));
  }
  ```
- **Rationale**: Trigger: a payments list [p1 -> INV-1, p2 -> INV-404] where INV-404 is not in invoicesByNumber. p1 is applied and its receipt is emailed, then the exception aborts the call with no recordReconciliation entry. A caller that fixes p2 and retries the batch applies p1 to INV-1 a second time and sends a second receipt.

### LOGIC.2: The function treats one degree of longitude as the same length as one …
- **Severity**: Major
- **Rule**: `LOGIC` — logic and correctness pass (no card)
- **Location**: `code/java/ShipmentPlanner.java` · `ShipmentPlanner#distanceFromDepot`
- **Code**:
  ```java
  double x = stop.longitude() - depot.longitude();
  ```
- **Problem**: The function treats one degree of longitude as the same length as one degree of latitude. A degree of longitude is really cos(latitude) times shorter, so east-west offsets count as too far. The distances therefore do not keep the true order of stops, which is the one thing the doc comment says the function is accurate enough for.
- **Suggested fix**:
  ```java
  double distanceFromDepot(GeoPoint stop) {
      double x = (stop.longitude() - depot.longitude()) * Math.cos(Math.toRadians(depot.latitude()));
      double y = stop.latitude() - depot.latitude();
      return Math.sqrt(x * x + y * y);
  }
  ```
- **Rationale**: Trigger: a depot at 52.52N 13.40E. Stop A is 0.010 deg east (about 0.68 km) and stop B is 0.008 deg north (about 0.89 km). The current code returns 0.010 for A and 0.008 for B, so it ranks A as farther, but B is actually farther. The error grows with distance from the equator (about 1.6x at 52 deg).

### CODE-02.1: A routine named as a query, predicate, accessor or conversion hides no state change, and a getter or predicate returns what its name asserts
- **Severity**: Major
- **Rule**: `CODE-02` — - clippy `misnamed_getters`, group `suspicious`, warn by default (rust-lang/rust-clippy, `clippy_lints/src/functions/mod.rs`): "Checks for getter methods that return a field that doesn't correspond to the name of the method, when there is a field's whose name matches that of the method. [...] It is most likely that such a method is a bug caused by a typo or by copy-pasting." (fetched)
- **Location**: `code/rust/session_cache.rs` · `SessionCache::idle_sessions`
- **Code**:
  ```rust
  pub fn idle_sessions(&mut self) -> Vec<SessionId> {
              self.sessions.remove(id);
  ```
- **Problem**: `idle_sessions` is named and documented as a noun-phrase accessor ("The sessions that have been idle for longer than the timeout."). Its body also removes every one of those sessions from `self.sessions`. Neither the name nor the doc comment mentions the eviction.
- **Suggested fix**:
  ```rust
      /// The sessions that have been idle for longer than the timeout.
      pub fn idle_sessions(&self) -> Vec<SessionId> {
          let now = Instant::now();
          self.sessions
              .iter()
              .filter(|(_, session)| now.duration_since(session.last_seen) > self.idle_timeout)
              .map(|(id, _)| *id)
              .collect()
      }
  
      /// Removes the sessions that have been idle for longer than the timeout and returns their ids.
      pub fn evict_idle_sessions(&mut self) -> Vec<SessionId> {
          let idle = self.idle_sessions();
          for id in &idle {
              self.sessions.remove(id);
          }
          idle
      }
  ```
- **Rationale**: The noun-phrase name promises a read with no consequences. In fact the body deletes entries from `self.sessions`, and callers can see that: afterwards `remaining_lifetime` returns `None` for those ids, and a later `idle_sessions` call no longer lists them. A caller that trusts the name and calls it to inspect, log or count idle sessions will silently end those sessions. A reader who trusts the name will not open the body to find the write. This is the linguistic antipattern where an entity's behaviour betrays what its name conveys, and it is not a cache whose only effect is speed.

### LOGIC.3: An unknown id is never translated to ErrProductNotFound. sql.ErrNoRows …
- **Severity**: Major
- **Rule**: `LOGIC` — logic and correctness pass (no card)
- **Location**: `errors/go/catalog.go` · `Catalog.PriceOfProductLeaksDriverError`
- **Code**:
  ```go
  return 0, fmt.Errorf("price of product %s: %w", id, err)
  ```
- **Problem**: An unknown id is never translated to ErrProductNotFound. sql.ErrNoRows goes out wrapped with %w, so errors.Is(err, ErrProductNotFound) is false for a missing product. ProductByID and the Catalog contract (callers see only this file's errors, never the database) both promise the opposite.
- **Suggested fix**:
  ```go
  func (c *Catalog) PriceOfProductLeaksDriverError(id string) (int64, error) {
  	var price int64
  	err := c.db.QueryRow(`SELECT price FROM products WHERE id = ?`, id).Scan(&price)
  	if errors.Is(err, sql.ErrNoRows) {
  		return 0, fmt.Errorf("price of product %s: %w", id, ErrProductNotFound)
  	}
  	if err != nil {
  		return 0, fmt.Errorf("price of product %s: catalogue store failed: %v", id, err)
  	}
  	return price, nil
  }
  ```
- **Rationale**: Calling it with an id the products table does not hold returns an error that wraps sql.ErrNoRows rather than ErrProductNotFound. A caller that branches on ErrProductNotFound (for example to return 404) handles a missing product as a store failure, and it can only detect the case by importing database/sql.

### ERR-12.1: An expected, recoverable failure is returned or raised to the caller, and code outside the entry point and start-up does not panic, exit or abort the process on it
- **Severity**: Major
- **Rule**: `ERR-12` — - rust-lang/book `src/ch09-03-to-panic-or-not-to-panic.md` — "When code panics, there's no way to recover"; "you're making the decision that a situation is unrecoverable on behalf of the calling code"; §Guidelines for Error Handling — "If someone calls your code and passes in values that don't make sense, it's best to return an error if you can so that the user of the library can decide what they want to do in that case"; "when failure is expected, it's more appropriate to return a `Result` than to make a `panic!` call. Examples include a parser being given malformed data or an HTTP request returning a status that indicates you have hit a rate limit"; "in cases where continuing could be insecure or harmful, the best choice might be to call `panic!`" (fetched)
- **Location**: `errors/go/notify.go` · `func retryDelayExitsOnBadHeader`
- **Code**:
  ```go
  		log.Fatalf("parse Retry-After header %q: %v", header, err)
  ```
- **Problem**: retryDelayExitsOnBadHeader runs while the program is handling a mail API reply, not at start-up and not in main. When the remote service's Retry-After header does not parse, it calls log.Fatalf, which runs os.Exit(1). That header comes from the network, so a bad value is a failure to expect in normal operation. It can be missing, malformed, or in the HTTP-date form that RFC 9110 allows, and strconv.Atoi rejects that form.
- **Suggested fix**:
  ```go
  import (
  	"fmt"
  	"net/http"
  	"strconv"
  	"text/template"
  	"time"
  )
  
  func retryDelayExitsOnBadHeader(resp *http.Response) (time.Duration, error) {
  	header := resp.Header.Get("Retry-After")
  	secs, err := strconv.Atoi(header)
  	if err != nil {
  		return 0, fmt.Errorf("parse Retry-After header %q: %w", header, err)
  	}
  	return time.Duration(secs) * time.Second, nil
  }
  ```
- **Rationale**: The trigger is an expected failure: the remote service sent a Retry-After header the code cannot parse. log.Fatalf decides for every caller that this cannot be recovered from, and it ends the process at once without unwinding the stack. The caller loses the choice to fall back to a default backoff, retry, or report the error. Deferred cleanup does not run. Every other request or task in the same process goes down with it, and so does any test run that calls this routine. If the function returned the error instead and every caller passed it up, it would still reach main and end there with a non-zero status. The fix also removes "log" from the import block, because log.Fatalf was its only use in this file and Go does not compile a file with an unused import.
- **Verifier note**: The finding stands at major. Only the fix needed a correction. The log.Fatalf call on line 18 is the only use of the "log" import in notify.go, so replacing just the routine leaves "log" unused, and Go rejects that at compile time. The corrected fix also removes "log" from the import block. Once the routine stops exiting, the name retryDelayExitsOnBadHeader no longer describes it, so it is worth renaming in the same change (for example to retryDelay). Nothing in the tree calls it, so neither the signature change nor a rename breaks other code.

### LOGIC.4: The only parse attempted is decimal delta-seconds, and its failure path …
- **Severity**: Major
- **Rule**: `LOGIC` — logic and correctness pass (no card)
- **Location**: `errors/go/notify.go` · `func retryDelayExitsOnBadHeader`
- **Code**:
  ```go
  secs, err := strconv.Atoi(header)
  ```
- **Problem**: The only parse attempted is decimal delta-seconds, and its failure path calls log.Fatalf. A rate-limited reply with no Retry-After header (Get returns "") fails Atoi and exits the whole process. So does a reply whose header uses the HTTP-date form, which RFC 9110 section 10.2.3 allows. A negative numeric value is accepted as a negative delay.
- **Suggested fix**:
  ```go
  import (
  	"fmt"
  	"net/http"
  	"strconv"
  	"text/template"
  	"time"
  )
  
  // "log" is removed from the imports: log.Fatalf was its only use in this file, and Go will not
  // compile an unused import.
  
  func retryDelayExitsOnBadHeader(resp *http.Response) (time.Duration, error) {
  	header := resp.Header.Get("Retry-After")
  	if header == "" {
  		return 0, fmt.Errorf("rate-limited reply has no Retry-After header")
  	}
  	if secs, err := strconv.Atoi(header); err == nil {
  		if secs < 0 {
  			return 0, fmt.Errorf("negative Retry-After header %q", header)
  		}
  		return time.Duration(secs) * time.Second, nil
  	}
  	when, err := http.ParseTime(header)
  	if err != nil {
  		return 0, fmt.Errorf("parse Retry-After header %q: %w", header, err)
  	}
  	if d := time.Until(when); d > 0 {
  		return d, nil
  	}
  	return 0, nil
  }
  ```
- **Rationale**: Any 429/503 from the mail API with no Retry-After header, or with one like "Wed, 21 Oct 2026 07:28:00 GMT", terminates the process. log.Fatalf calls os.Exit(1), so deferred cleanup is skipped, and the caller never gets a chance to fall back to a default backoff.
- **Verifier note**: The finding holds. The defect is real, the anchored code is on added line 16, and major is the right severity; nothing in the file, the commit message or the design intent says exiting is intended. Only the fix needed a correction. Pasted over the routine as given, the fix leaves the `log` import unused, because log.Fatalf was its only use in the file. Go refuses to compile an unused import (go vet: `"log" imported and not used`). The corrected fix drops that import. The new signature, (time.Duration, error), breaks no callers because the tree has none.

### ERR-07.2: An error returned as a value, a status result, a future or a promise is checked, propagated, or discarded explicitly with a comment stating why that is safe
- **Severity**: Major
- **Rule**: `ERR-07` — - CWE-252 Unchecked Return Value (CWE 4.19) — "The product does not check the return value from a method or function, which can prevent it from detecting unexpected states and conditions."; "Two common programmer assumptions are "this function call can never fail" and "it doesn't matter if this function call fails"."; mitigation, effectiveness High: "Check the results of all functions that return a value and verify that the value is expected." (fetched)
- **Location**: `errors/go/receipts.go` · `func appendAuditLineIgnoresWriteError`
- **Code**:
  ```go
  	f.WriteString(line + "\n")
  ```
- **Problem**: (*os.File).WriteString returns (n int, err error), and this bare call statement drops the error. If the write fails or is short (disk full, I/O error, quota exceeded), the function still returns nil, so callers believe the audit line was recorded.
- **Suggested fix**:
  ```go
  	if _, err := f.WriteString(line + "\n"); err != nil {
  		return fmt.Errorf("write audit log %s: %w", path, err)
  	}
  	return nil
  ```
- **Rationale**: An ignored return value fails silently. os.File.WriteString reports a failed or short write only through the error it returns. The next statement, `return nil`, assumes the audit line reached the file, so the missing audit entry turns up later and far from where the write failed. This is the case CWE-252 and the Go style guide's 'deliberate choice' rule describe.

### LOGIC.5: Both the WriteString error and the deferred Close error are dropped, and …
- **Severity**: Major
- **Rule**: `LOGIC` — logic and correctness pass (no card)
- **Location**: `errors/go/receipts.go` · `func appendAuditLineIgnoresWriteError`
- **Code**:
  ```go
  f.WriteString(line + "\n")
  ```
- **Problem**: Both the WriteString error and the deferred Close error are dropped, and the function returns nil. The caller is told the audit line was written when it was not.
- **Suggested fix**:
  ```go
  func appendAuditLineIgnoresWriteError(path, line string) (err error) {
  	f, err := os.OpenFile(path, os.O_APPEND|os.O_CREATE|os.O_WRONLY, 0o600)
  	if err != nil {
  		return fmt.Errorf("open audit log %s: %w", path, err)
  	}
  	defer func() {
  		if cerr := f.Close(); cerr != nil && err == nil {
  			err = fmt.Errorf("close audit log %s: %w", path, cerr)
  		}
  	}()
  	if _, err := f.WriteString(line + "\n"); err != nil {
  		return fmt.Errorf("append to audit log %s: %w", path, err)
  	}
  	return nil
  }
  ```
- **Rationale**: The write can fail with ENOSPC on a full disk, EIO, or a quota limit, or the error can surface only at Close on a network filesystem. In each case the audit record is silently lost and the function still reports success.

### ERR-08.1: A local handler catches only the error types it can handle, and a catch-all either re-raises the error or sits at an isolation point
- **Severity**: Major
- **Rule**: `ERR-08` — - [narrow] PMD `AvoidCatchingGenericException` (`category/java/errorprone.xml`) — "Catching overly broad exception types makes it difficult to understand what can actually go wrong in your code and can hide real problems"; Throwable: "handle both recoverable exceptions and serious errors (like OutOfMemoryError) the same way, which is dangerous"; Checkstyle `IllegalCatch` — "catching java.lang.Exception, java.lang.Error or java.lang.RuntimeException is almost never acceptable", which "leads to code that inadvertently catches NullPointerException, OutOfMemoryError, etc." (fetched)
- **Location**: `errors/py/jobs.py` · `jobs.load_plugin_config_catches_everything`
- **Code**:
  ```python
      except Exception:
          return {}
  ```
- **Problem**: An ordinary config-loading routine catches every non-fatal error with `except Exception` and returns an empty config. It does not test the error type, re-raise, or log a traceback, and it does not sit at an isolation point.
- **Suggested fix**:
  ```python
  def load_plugin_config_catches_everything(path):
      try:
          with open(path, encoding="utf-8") as handle:
              return json.load(handle)
      except FileNotFoundError:
          return {}
  ```
- **Rationale**: The catch-all also receives errors nobody anticipated. A programming error (TypeError or AttributeError in the loading path), a permission error, a decode error, or malformed JSON all turn into a silent 'no config' result. The evidence that would locate the fault is lost, and any new error type the block raises later gets absorbed the same way.

### ERR-04.1: A handler that lets execution continue after a failure leaves the program in a valid state, so no later step runs on the failed step's missing result or on a half-applied update
- **Severity**: Major
- **Rule**: `ERR-04` — - SEI CERT ERR00-J — "Each `catch` block must ensure that the program continues only with valid invariants"; "the `catch` block must either recover from the exceptional condition, rethrow the exception ..., or throw an exception that is appropriate to the context of the `catch` block"; "Ignoring or suppressing exceptions can result in inconsistent program state." (fetched)
- **Location**: `errors/py/ledger.py` · `ledger.transfer_credits_after_failed_debit`
- **Code**:
  ```python
      except InsufficientFunds as err:
          log.warning("transfer %s -> %s: %s", source.id, target.id, err)
  ```
- **Problem**: The added handler catches InsufficientFunds from debit(source, amount), only logs it, and falls through to credit(target, amount) on line 26. Before this change the failure propagated. Now the target is credited money that was never taken from the source.
- **Suggested fix**:
  ```python
  def transfer_credits_after_failed_debit(source, target, amount):
      try:
          debit(source, amount)
      except InsufficientFunds as err:
          log.warning("transfer %s -> %s: %s", source.id, target.id, err)
          raise
      credit(target, amount)
  ```
- **Rationale**: debit() exists to take `amount` from the source and guards the second half of a paired update. When it raises, source.balance is left unchanged. The handler neither propagates nor recovers, so the following statement credit(target, amount) still runs. That is the step the failed debit guarded, and it makes the transfer fail open: the target's balance grows by `amount` with no matching debit. Logging records the broken invariant but does not restore it.
- **Also flagged by**: LOGIC

### ERR-02.1: A caught exception or received error is acted on, or ignored only with a comment stating why that is safe, and an empty handler, a bare pass, a TODO or a printed stack trace does not count as acting
- **Severity**: Major
- **Rule**: `ERR-02` — - PMD rule `EmptyCatchBlock` (`category/java/errorprone.xml`) — "Empty Catch Block finds instances where an exception is caught, but nothing is done. In most circumstances, this swallows an exception which should either be acted on or reported."; defaults `allowCommentedBlocks` false, `allowExceptionNameRegex` `^(ignored|expected)$` (fetched)
- **Location**: `errors/ts/orders.ts` · `saveDraftSwallowsError`
- **Code**:
  ```typescript
    } catch (err) {}
  ```
- **Problem**: The catch clause around `await store.save(order)` has an empty body and no comment saying why the error can be dropped, so a failed save is silently swallowed.
- **Suggested fix**:
  ```typescript
  export async function saveDraftSwallowsError(store: OrderStore, order: Order): Promise<void> {
    try {
      await store.save(order);
    } catch (err) {
      throw new Error(`saving draft order ${order.id} failed`, { cause: err });
    }
  }
  ```
- **Rationale**: The handler drops the error with an empty body. The caller awaits a Promise<void> that resolves either way, so it assumes the draft was saved. When the save fails, that assumption is false: execution continues past the failed save and nothing records the failure. An empty body also looks the same as an unfinished handler, so a reader cannot tell a deliberate choice from an omission.

### ERR-08.2: A local handler catches only the error types it can handle, and a catch-all either re-raises the error or sits at an isolation point
- **Severity**: Major
- **Rule**: `ERR-08` — - [narrow] PMD `AvoidCatchingGenericException` (`category/java/errorprone.xml`) — "Catching overly broad exception types makes it difficult to understand what can actually go wrong in your code and can hide real problems"; Throwable: "handle both recoverable exceptions and serious errors (like OutOfMemoryError) the same way, which is dangerous"; Checkstyle `IllegalCatch` — "catching java.lang.Exception, java.lang.Error or java.lang.RuntimeException is almost never acceptable", which "leads to code that inadvertently catches NullPointerException, OutOfMemoryError, etc." (fetched)
- **Location**: `errors/ts/orders.ts` · `prefetchOrderIgnoresMissByDesign`
- **Code**:
  ```typescript
  store.prefetch(id).catch(() => {
    // prefetch only warms a cache: a miss costs one fetch when the order is first opened
  });
  ```
- **Problem**: This prefetch runs fire-and-forget, and its rejection handler receives every error that `store.prefetch` rejects with. It drops each one without a record. It does no type test and logs nothing, so an error nobody anticipated is suppressed just like the failed cache warm that the comment tolerates.
- **Suggested fix**:
  ```typescript
  store.prefetch(id).catch((err: unknown) => {
    // prefetch only warms a cache: a miss costs one fetch when the order is first opened;
    // nothing awaits this promise, so its outermost handler records the error instead of rethrowing it
    console.warn(`prefetch order ${id}: the cache stays cold`, err); // the error object itself, so the log carries its stack trace
  });
  ```
- **Rationale**: The comment justifies only the cost of a cold cache: one fetch when the order is first opened. The handler also receives errors the author did not anticipate, such as a TypeError or a stack-overflow RangeError from a bug inside prefetch. It treats them as a harmless miss and leaves no stack trace. A prefetch that fails on every call would disable the cache without anyone noticing, and the evidence that would locate the bug is gone. Nothing awaits the promise, so this handler is the outermost block of that background task. A rethrow here has no caller to reach; it only reaches the unhandled-rejection path, which exits a Node process by default. The card's route at such a point is a recorded suppression: log the error object so the record carries its stack trace, then go on.
- **Verifier note**: The finding is real. The rejection handler receives every error, does no type test and drops each error unrecorded. That is neither of the card's two routes, and the intent comment states a cost tolerance, which the card's Limits do not include.

The fix needed correction for two reasons:
1. It names `OrderNotFoundError`, which exists nowhere in the fixture, so it does not compile (TS2304). It also reads the comment's "miss" as a rejection type. The comment actually describes the cache miss that any failed prefetch leaves when the order is first opened.
2. The routine detaches the promise and returns void, so a rethrow from this last `.catch` has no caller to reach. Under Node's default unhandled-rejection mode the process exits, as I observed. A dropped connection during a best-effort cache warm would crash the service. The finding's own rationale lists that error as one to propagate. Exiting on a non-fatal error is the outcome the card's failure study counts as catastrophic.

This handler is the outermost block of that background task. The card's route at such a point is to record the error with its stack trace and then suppress it, and the card's Limits make no finding on that form. The corrected fix does this and keeps the comment.

Severity stays major. The card ties a generic catch with a dummy handler to defects. The comment bounds the cost of the failure it tolerates, not the cost of the unanticipated errors.

### ERR-08.3: A local handler catches only the error types it can handle, and a catch-all either re-raises the error or sits at an isolation point
- **Severity**: Major
- **Rule**: `ERR-08` — - [narrow] PMD `AvoidCatchingGenericException` (`category/java/errorprone.xml`) — "Catching overly broad exception types makes it difficult to understand what can actually go wrong in your code and can hide real problems"; Throwable: "handle both recoverable exceptions and serious errors (like OutOfMemoryError) the same way, which is dangerous"; Checkstyle `IllegalCatch` — "catching java.lang.Exception, java.lang.Error or java.lang.RuntimeException is almost never acceptable", which "leads to code that inadvertently catches NullPointerException, OutOfMemoryError, etc." (fetched)
- **Location**: `errors/ts/orders.ts` · `saveDraftSwallowsError`
- **Code**:
  ```typescript
    } catch (err) {}
  ```
- **Problem**: An untyped catch in an ordinary routine receives every error from `store.save` and drops it. There is no type test, no rethrow and no logged stack, and this is not an isolation point.
- **Suggested fix**:
  ```typescript
  export async function saveDraftSwallowsError(store: OrderStore, order: Order): Promise<void> {
    await store.save(order);
  }
  ```
- **Rationale**: The untyped catch takes in every rejection: a programming error such as a TypeError, a storage or network failure, or a resource failure. The handler treats each one as harmless, so the caller believes the draft was saved, and nothing records the error that would locate the fault.

### LOGIC.6: The empty catch turns every failed `store.save` into a resolved promise. …
- **Severity**: Major
- **Rule**: `LOGIC` — logic and correctness pass (no card)
- **Location**: `errors/ts/orders.ts` · `orders.saveDraftSwallowsError`
- **Code**:
  ```typescript
  } catch (err) {}
  ```
- **Problem**: The empty catch turns every rejected `store.save` into a resolved promise. The base `saveDraft` passed the rejection on. At head, a caller that awaits the call sees success when nothing was saved and cannot find out, because the error is thrown away instead of handled.
- **Suggested fix**:
  ```typescript
  export async function saveDraft(store: OrderStore, order: Order): Promise<void> {
    await store.save(order);
  }
  ```
- **Rationale**: When `store.save(order)` rejects (storage unavailable, validation failure, conflict), the `await` throws inside the try. The empty catch then finishes normally, so the async function resolves with undefined. The caller reports the draft as saved, and the user's edits are lost without any signal. Nothing in the tree calls the function (git grep at base and head finds only the definition). What breaks is the exported Promise<void> contract that any awaiting caller relies on. The fix must also drop the 'SwallowsError' name. On a body that passes errors on, that name tells callers the promise never rejects. A caller who trusts it and drops the promise turns a failed save into an unhandled rejection, which Node raises as an error by default.
- **Verifier note**: The defect is real and stays major. It was added by this diff, nothing nearby guards against it, and nothing documents it as tolerated. Two corrections are needed. (1) The fix: the suggested fix keeps the name `saveDraftSwallowsError` on a body that now passes errors on. The name would then say the opposite of what the code does, and naming is one of the fixture's three review domains. A caller who trusts the name may drop the promise, and under Node 22's default (`--unhandled-rejections=throw`) a failed save then raises an uncaught error. The corrected fix restores the base routine word for word as `saveDraft`. No code in the repo imports it under either name, so nothing breaks. (2) The rationale: "The base version's callers depended on that rejection" has no support in the tree, because git grep at base and at head finds no callers. The defect instead rests on the exported Promise<void> contract and on the routine itself, which the design intent says is self-contained.

### ERR-06.1: Code that detects an unexpected broken assumption, contract or invariant that later code relies on stops or propagates an error instead of continuing on a substitute value
- **Severity**: Major
- **Rule**: `ERR-06` — - [stop] rust-lang/book `src/ch09-03-to-panic-or-not-to-panic.md` §Guidelines for Error Handling — "It's advisable to have your code panic when it's possible that your code could end up in a bad state"; "Your code after this point needs to rely on not being in this bad state" (fetched)
- **Location**: `errors/ts/pricing.ts` · `function monthlyPriceFallsBackToZero`
- **Code**:
  ```typescript
        return 0; // unreachable: the billing schema admits only these three tiers
  ```
- **Problem**: The default branch handles a tier outside the three the billing schema admits, a state its own comment calls unreachable. Instead of stopping, it returns 0 as the monthly price. `tier` is a plain `string` read from the billing database, so the type does not rule the bad value out. The code this diff replaces threw an error naming the subscription and the unknown tier.
- **Suggested fix**:
  ```typescript
      default:
        throw new Error(`monthly price of subscription ${sub.id}: unknown tier ${sub.tier}`);
  ```
- **Rationale**: The broken invariant is that a subscription's tier is one of free, team or enterprise. Anything that bills or totals with this routine's result relies on it. With the substitute 0, an unknown or corrupted tier comes back as a $0 monthly price, and a caller cannot tell that from the real price of a free plan. The subscription is silently billed nothing, and the failure shows up downstream in the wrong routine with no record of the bad tier. Stopping at the check, or returning an error the caller must handle, reports the mistake while the offending value is still in hand.

### LOGIC.7: `Subscription.tier` is typed `string` and read from the billing …
- **Severity**: Major
- **Rule**: `LOGIC` — logic and correctness pass (no card)
- **Location**: `errors/ts/pricing.ts` · `pricing.monthlyPriceFallsBackToZero`
- **Code**:
  ```typescript
        return 0; // unreachable: the billing schema admits only these three tiers
  ```
- **Problem**: `Subscription.tier` is typed `string` and read from the billing database, so the type system does not enforce that this branch is unreachable. The base `monthlyPrice` threw on an unknown tier. This version returns 0 instead, so a subscription with an unrecognised tier gets a monthly price of zero.
- **Suggested fix**:
  ```typescript
      default:
        throw new Error(`monthly price of subscription ${sub.id}: unknown tier ${sub.tier}`);
  ```
- **Rationale**: Some subscriptions carry a tier outside the three cases. Examples are a newly added plan such as "business", a casing variant such as "Team", or a legacy value. All of them are priced at 0 and billed nothing for their seats, and nothing reports the error, where the base version threw.

### TST-11.1: A test double is built from the real type it replaces so that its shape is checked against that type
- **Severity**: Major
- **Rule**: `TST-11` — - Python documentation, `unittest.mock`, section "Autospeccing" (cpython `Doc/library/unittest.mock.rst`) (fetched): "any tests for code that is still using the *old api* but uses mocks instead of the real objects will still pass. This means your tests can all pass even though your code is broken." The same section documents the constructor-attribute limit and that integration tests remain needed.
- **Location**: `tests/python/test_checkout.py` · `test_checkout.test_checkout_pays_through_bare_gateway_mock`
- **Code**:
  ```python
      gateway = MagicMock()
  ```
- **Problem**: The double for PaymentGateway, which is passed into Checkout(gateway), is a bare MagicMock with no spec. It accepts any attribute and any call signature, including calls to charge that do not match the real `charge(amount_cents, currency, *, idempotency_key)`.
- **Suggested fix**:
  ```python
      gateway = create_autospec(PaymentGateway, instance=True)
  ```
- **Rationale**: Nothing checks this double's shape against PaymentGateway. If charge is renamed or its signature changes, the double goes stale and nothing fails where it is built, so the test keeps passing on broken code. The test in the same file already uses create_autospec(PaymentGateway, instance=True), which checks signatures. The Mock() on_paid callback is a throwaway callable with no production class behind it, so the card's Limits exempt it and it is not flagged.

## Minor & Suggestions

| # | Severity | Rule | Location | Finding | Suggested fix |
|---|---|---|---|---|---|
| CODE-12.1 | Minor | `CODE-12` | `code/go/stockroom.go` · `func (*Stockroom) ReleaseReservation` | The exported method ReleaseReservation gains a new parameter named with the single letter `q`. It stands for a domain value: the number of reserved units to release. The base signature was `ReleaseReservation(sku string)`, so this change introduces the letter. It is not a conventional letter for its role, and the sibling method ReserveUnits names the same value `quantity`. | func (s *Stockroom) ReleaseReservation(sku string, quantity int) error { 	if quantity > s.reserved[sku] { 		return fmt.Errorf("release %d units of %s: only %d reserved", quantity, sku, s.reserved[sku]) 	} 	s.reserved[sku] -= quantity 	return nil } |
| LOGIC.8 | Minor | `LOGIC` | `code/go/stockroom.go` · `(*Stockroom).ReleaseReservation` | ReleaseReservation checks only the upper bound of q. A negative q passes the check, and s.reserved[sku] -= q then increases the reservation. That skips the availability check ReserveUnits enforces, so reserved can grow beyond the units on hand. | func (s *Stockroom) ReleaseReservation(sku string, q int) error { 	if q < 0 { 		return fmt.Errorf("release %d units of %s: quantity must not be negative", q, sku) 	} 	if q > s.reserved[sku] { 		return fmt.Errorf("release %d units of %s: only %d reserved", q, sku, s.reserved[sku]) 	} 	s.reserved[sku] -= q 	return nil } |
| CODE-06.1 | Minor | `CODE-06` | `code/go/supplier_client.go` · `(*SupplierClient).WebhookTarget` | The method returns the address on this service that the supplier posts webhook events to. In this package that concept is already called the callback URL: the `Webhook.CallbackURL` field, the supplier API's `callback_url` (`GetCallbackUrl()`), and even this method's own local `callbackUrl`. The method name calls the same value a 'target', so the package now has two words for one concept. | // CallbackURL returns the callback URL on this service that the supplier posts events of one kind to. func (c *SupplierClient) CallbackURL(eventKind string) string { |
| CODE-03.1 | Minor | `CODE-03` | `code/java/InvoiceLedger.java` · `InvoiceLedger#computeLateFee` | The late fee computed from the outstanding amount, the daily rate and the days late is held in a variable named with the single letter `d`. |         BigDecimal lateFee = invoice.outstanding()                 .multiply(DAILY_LATE_FEE_RATE)                 .multiply(BigDecimal.valueOf(daysLate));         return lateFee.min(MAX_LATE_FEE); |
| CODE-06.2 | Minor | `CODE-06` | `code/java/InvoiceLedger.java` · `InvoiceLedger#hasOpenDisputes` | The method name calls the disputes it counts "open". The Dispute type names that state "resolved" (`dispute.isResolved()`), and the method's own local calls them "unresolved" (`unresolvedCount`). So inside one 9-line routine, one concept (a dispute that is not resolved) gets two words. The same file's added code also uses "open" for a second concept. In reconcilePayments, `stillOpen` holds invoices that still have an outstanding amount, so "open" has two meanings in InvoiceLedger. | int unresolvedDisputeCount(Invoice invoice) {     int unresolvedCount = 0;     for (Dispute dispute : invoice.disputes()) {         if (!dispute.isResolved()) {             unresolvedCount++;         }     }     return unresolvedCount; } |
| CODE-06.3 | Minor | `CODE-06` | `code/java/InvoiceLedger.java` · `InvoiceLedger#reconcilePayments` | The local names the invoices that still have an outstanding amount "open". The method that produces them, and its own local, call the same concept "unpaid" (`unpaidInvoicesOf`, `unpaid`), and so does the isOverdueOn doc comment ("still unpaid"). One concept gets two words on a single line. In the same file, "open" also means an unresolved dispute (hasOpenDisputes). | List<Invoice> stillUnpaid = unpaidInvoicesOf(customer); if (!stillUnpaid.isEmpty()) {     reminders.schedule(customer, stillUnpaid); } |
| CODE-11.1 | Minor | `CODE-11` | `code/java/InvoiceLedger.java` · `InvoiceLedger#reconcilePayments` | The local `tmp` holds the customer's balance from before the payments are applied. It is declared on line 73 and last used on line 85, 12 lines later, after a payment loop and a reminder block. At `auditTrail.recordReconciliation(customer.id(), tmp, balanceOf(customer))` the generic word `tmp` does not say which balance it is, or that it is a balance at all. |         BigDecimal balanceBeforePayments = balanceOf(customer);         // ... payment loop and reminder scheduling unchanged ...         auditTrail.recordReconciliation(customer.id(), balanceBeforePayments, balanceOf(customer)); |
| LOGIC.9 | Minor | `LOGIC` | `code/java/InvoiceLedger.java` · `InvoiceLedger#computeLateFee` | The fee is never rounded to currency precision. outstanding (scale 2) x DAILY_LATE_FEE_RATE (scale 4) x days gives a scale-6 BigDecimal. Every fee below the cap comes back with fractions of a cent, while a capped fee comes back at scale 2, so the method returns amounts in two different precisions. | BigDecimal fee = invoice.outstanding()         .multiply(DAILY_LATE_FEE_RATE)         .multiply(BigDecimal.valueOf(daysLate))         .setScale(MAX_LATE_FEE.scale(), java.math.RoundingMode.HALF_UP); return fee.min(MAX_LATE_FEE); |
| LOGIC.10 | Minor | `LOGIC` | `code/java/RateCardImporter.java` · `RateCardImporter#parseRateRow` | The check meant to accept only positive weights lets NaN and Infinity through. Double.parseDouble accepts "NaN" and "Infinity", and NaN <= 0 is false, so a rate row with a weight that is not a number is imported as valid. | double weight = Double.parseDouble(weightString); if (!(weight > 0) \|\| Double.isInfinite(weight)) {     throw new IllegalArgumentException("rate row weight must be a positive finite number, was " + weightString); } |
| CODE-06.4 | Minor | `CODE-06` | `code/rust/billing.rs` · `Money::to_text` | `Money::to_text` turns the amount into a string, which is Rust's standard string conversion, but it does so under a private synonym (`to_text`) instead of going through `std::fmt::Display`. This is the type's only user-facing representation: `#[derive(Debug)]` covers the diagnostic form, and Money has no `Display` impl. As a result, `format!("{}", money)`, `println!("{money}")` and `money.to_string()` do not compile for Money, even though `to_text` does exactly what they promise. The repository has no callers of `to_text`, so the rename costs nothing at call sites. | impl std::fmt::Display for Money {     /// Formats the amount as whole units and two-digit cents, such as `-12.05`.     fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {         let sign = if self.cents < 0 { "-" } else { "" };         let magnitude = self.cents.unsigned_abs();         write!(f, "{sign}{}.{:02}", magnitude / 100, magnitude % 100)     } } // callers use `money.to_string()` or `format!("{money}")`; remove `to_text` from `impl Money` |
| LOGIC.11 | Minor | `LOGIC` | `code/rust/session_cache.rs` · `SessionCache::idle_sessions` | The change makes `insert` store a caller-supplied `now` as `last_seen`, and `remaining_lifetime` also takes `now` from the caller. `idle_sessions` still measures against the system clock. Before this change, `last_seen` always came from `Instant::now()`, so measuring against the system clock was safe. Now eviction can disagree with the timestamps the caller supplied. | pub fn idle_sessions(&mut self, now: Instant) -> Vec<SessionId> {     let idle: Vec<SessionId> = self         .sessions         .iter()         .filter(\|(_, session)\| now.duration_since(session.last_seen) > self.idle_timeout)         .map(\|(id, _)\| *id)         .collect();     for id in &idle {         self.sessions.remove(id);     }     idle } |
| LOGIC.12 | Minor | `LOGIC` | `code/rust/session_cache.rs` · `SessionCache::remaining_lifetime` | The struct doc says a session times out only once it has been idle for longer than `idle_timeout`, and `idle_sessions` uses the matching strict `>`. `remaining_lifetime` instead counts a session as expired when the idle time exactly equals the timeout, so the two routines disagree at the boundary. | let expired = now > expires; if expired {     return None; } Some(expires - now) |
| LOGIC.13 | Minor | `LOGIC` | `code/rust/session_cache.rs` · `SessionCache::remaining_lifetime` | `Instant + Duration` panics when the result cannot be represented, so a very large `idle_timeout` makes `remaining_lifetime` panic. `idle_sessions` handles the same configuration without trouble. | let session = self.sessions.get(&id)?; let idle_for = now.saturating_duration_since(session.last_seen); if idle_for > self.idle_timeout {     return None; } Some(self.idle_timeout - idle_for) |
| ERR-05.1 | Minor | `ERR-05` | `errors/go/catalog.go` · `func (*Catalog) PriceOfProductLeaksDriverError` | PriceOfProductLeaksDriverError is an exported method of Catalog, and Catalog's doc comment says callers "see products and the errors declared in this file, never the database behind it". The method still wraps the raw database/sql error with %w. Callers can therefore match errors.Is(err, sql.ErrNoRows) or errors.As on driver error types, and an unknown id comes back as sql.ErrNoRows instead of ErrProductNotFound. ProductByID in the same file translates both cases correctly. | 	err := c.db.QueryRow(`SELECT price FROM products WHERE id = ?`, id).Scan(&price) 	if errors.Is(err, sql.ErrNoRows) { 		return 0, fmt.Errorf("price of product %s: %w", id, ErrProductNotFound) 	} 	if err != nil { 		return 0, fmt.Errorf("price of product %s: catalogue store failed: %v", id, err) 	} 	return price, nil |
| ERR-03.1 | Minor | `ERR-03` | `errors/go/inventory.go` · `func restockFromRowReturnsMinusOne` | restockFromRowReturnsMinusOne returns the in-band sentinel -1 on both of its failure paths: a row whose SKU is missing or does not match, and a quantity field that ParseQuantity rejects. The rest of package shop returns an error value for failures (ParseQuantity and Reserve in this file, ProductByID in catalog.go). This change also removed the (int, error) signature the routine had at base and dropped the wrapped ParseQuantity error. | func restockFromRow(item *Item, row string) (int, error) { 	sku, field, found := strings.Cut(row, ",") 	if !found \|\| sku != item.SKU { 		return 0, fmt.Errorf("restock %s from row %q: SKU does not match", item.SKU, row) 	} 	n, err := ParseQuantity(field) 	if err != nil { 		return 0, fmt.Errorf("restock %s: %w", item.SKU, err) 	} 	item.Quantity += n 	return item.Quantity, nil } |
| LOGIC.14 | Minor | `LOGIC` | `errors/go/inventory.go` · `func restockFromRowReturnsMinusOne` | The -1 failure sentinel shares its value range with the success result. ParseQuantity accepts negative numbers and item.Quantity += n can land on -1, so a successful restock that mutated the item is indistinguishable from a rejected row. | func restockFromRowReturnsMinusOne(item *Item, row string) (int, error) { 	sku, field, found := strings.Cut(row, ",") 	if !found \|\| sku != item.SKU { 		return 0, fmt.Errorf("restock %s from row %q: SKU does not match", item.SKU, row) 	} 	n, err := ParseQuantity(field) 	if err != nil { 		return 0, fmt.Errorf("restock %s: %w", item.SKU, err) 	} 	item.Quantity += n 	return item.Quantity, nil } |
| ERR-03.2 | Minor | `ERR-03` | `errors/go/notify.go` · `func retryDelayExitsOnBadHeader` | retryDelayExitsOnBadHeader aborts the whole process with log.Fatalf (log.Fatalf calls os.Exit) when the Retry-After header of a rate-limited mail API reply does not parse. A bad header from a remote server is an expected failure, not a broken invariant. The routine is also not a must-named start-up helper, while the rest of package shop returns an error value for failures (ParseQuantity, Reserve, ProductByID). | // The "log" import is no longer used after this change and is removed. func retryDelay(resp *http.Response) (time.Duration, error) { 	header := resp.Header.Get("Retry-After") 	secs, err := strconv.Atoi(header) 	if err != nil { 		return 0, fmt.Errorf("parse Retry-After header %q: %w", header, err) 	} 	return time.Duration(secs) * time.Second, nil } |
| ERR-01.1 | Minor | `ERR-01` | `errors/go/receipts.go` · `func appendAuditLineIgnoresWriteError` | The wrap repeats what the wrapped error already says. The *os.PathError from os.OpenFile already reads "open <path>: <reason>". The resulting message is "open audit log /x/audit.log: open /x/audit.log: permission denied", which carries both the operation and the path twice. | 		return fmt.Errorf("append audit line: %w", err) |
| ERR-01.2 | Minor | `ERR-01` | `errors/py/profiles.py` · `profiles.parse_age_field_with_vague_message` | The error does not name the operation (parsing the age field) or the rejected value. The routine holds both `raw` and `text` at this point. |         raise ValueError(f"parse age field: {raw!r} is not a string of decimal digits") |
| CODE-06.5 | Minor | `CODE-06` | `errors/py/settings.py` · `settings.ConfigError` | settings.py uses the word "settings" for the service-settings concept everywhere else: the module name, the module docstring ("Service settings read from a TOML file"), load_settings_drops_cause, parse_timeout_setting_keeps_input, and the messages "cannot load settings from {path}" and "timeout setting ... is not a number". The exception for that same settings file is called "Config", and its own docstring says "The settings file is missing...". So one concept has two names in one module. The sibling module errors/py/jobs.py, added in the same diff, already uses "config" for something else: the plugin configuration JSON read by load_plugin_config_catches_everything. That function never raises ConfigError (it returns {}). As a result, "config" now means two things in errors/py. | class SettingsError(Exception):     """The settings file is missing, unreadable or holds an invalid value."""  # and at both raise sites in this module: #   raise SettingsError(f"cannot load settings from {path}") #   raise SettingsError(f"timeout setting {raw!r} is not a number") from None |
| ERR-01.3 | Minor | `ERR-01` | `errors/py/settings.py` · `settings.load_settings_drops_cause` | The `except OSError:` handler drops the caught OSError. It is not bound or chained as the cause (`from err`), and its reason (not found, permission denied, is a directory) is not in the message. The new error names only the path and says that loading failed. |     except OSError as err:         raise ConfigError(f"load settings from {path}: {err.strerror}") from err |
| ERR-05.2 | Minor | `ERR-05` | `errors/py/settings.py` · `settings.load_settings_drops_cause` | load_settings_drops_cause is a public module function. It translates only OSError into ConfigError. If the file is not valid TOML, tomllib.loads raises tomllib.TOMLDecodeError, which escapes to callers untranslated. ConfigError's own docstring says it covers a settings file that is "missing, unreadable or holds an invalid value", so a caller that catches ConfigError will miss a malformed settings file. | def load_settings_drops_cause(path):     try:         raw = Path(path).read_text(encoding="utf-8")     except OSError:         raise ConfigError(f"cannot load settings from {path}")     try:         return tomllib.loads(raw)     except tomllib.TOMLDecodeError as err:         raise ConfigError(f"settings file {path} is not valid TOML: {err}") from err |
| ERR-11.1 | Minor | `ERR-11` | `errors/py/settings.py` · `settings.load_settings_drops_cause` | Inside `except OSError:`, the code raises a new ConfigError without `from` and without binding the caught OSError. The replacement does not carry the original as its `__cause__`. The cut is also not a deliberate one the card allows: there is no `from None`, no catch variable named as unused, and no failed parse, and the message drops the OSError's text (e.g. the errno and strerror, such as 'No such file or directory' versus 'Permission denied'). |     except OSError as err:         raise ConfigError(f"cannot load settings from {path}") from err |
| ERR-09.1 | Minor | `ERR-09` | `errors/ts/quota.ts` · `reserveQuotaThrowsString` | The routine throws a template-literal string rather than an Error object, so the thrown value is not an error type and does not say what failed. | export class QuotaExceededError extends Error {   constructor(readonly accountId: string, readonly requested: number, readonly limit: number) {     super(`quota exceeded for account ${accountId}: ${requested} of ${limit} units`);     this.name = "QuotaExceededError";   } }  // inside reserveQuotaThrowsString: throw new QuotaExceededError(account.id, account.used + units, account.limit); |
| ERR-10.1 | Minor | `ERR-10` | `errors/ts/tags.ts` · `hashtagsOfPostOrNull` | hashtagsOfPostOrNull, which returns a string array, returns null when the post has no '#' labels. Here null means only "no hashtags", which is exactly what an empty array says. The routine has no doc comment or contract that gives null a separate "no answer" meaning. | export function hashtagsOfPostOrNull(post: Post): string[] {   const tags = post.labels.filter((label) => label.startsWith("#"));   if (tags.length === 0) {     return [];   }   return tags.map((tag) => tag.slice(1)); } |
| LOGIC.15 | Minor | `LOGIC` | `errors/ts/tags.ts` · `tags.hashtagsOfPostOrNull` | A post with no '#' labels has a clear answer: it has no hashtags. The function returns null in that case instead of an empty array. Every caller then has to special-case a normal result, and a caller that iterates the result or reads `.length` fails on it. | export function hashtagsOfPost(post: Post): string[] {   return post.labels.filter((label) => label.startsWith("#")).map((tag) => tag.slice(1)); } |
| LOGIC.16 | Minor | `LOGIC` | `tests/java/shop/OrderServiceTest.java` · `OrderServiceTest#placeOrderReturnsTheOrderAsStored` | The test is named for the contract that `place` returns the order as stored, which is what `OrderRepository.save` returns. But the `save` stub hands back its own argument, so the stored order and the order built before saving are the same object. The test passes whether `OrderService.place` returns `orders.save(order)` or ignores that return value and returns the order it built, so it can never catch the regression its name describes. |     @Test     void placeOrderReturnsTheOrderAsStored() {         when(prices.priceOf("STD-1")).thenReturn(new BigDecimal("10.00"));         Order stored = new Order("o-9", List.of("STD-1"), new BigDecimal("9.50"));         when(orders.save(any(Order.class))).thenReturn(stored);         Order order = service.place("o-9", List.of("STD-1"));         assertEquals(stored, order);     } |
| TST-07.1 | Minor | `TST-07` | `tests/java/shop/OrderServiceTest.java` · `OrderServiceTest#placeOrderPricesSaleItemsInsideTheStub` | The PriceList stub's answer function branches on a pattern of its argument (`sku.startsWith("SALE-")`) to choose the price. That puts pricing logic inside the double instead of having it give fixed answers. | when(prices.priceOf("SALE-1")).thenReturn(new BigDecimal("8.00"));         when(prices.priceOf("STD-1")).thenReturn(new BigDecimal("10.00")); |
| TST-09.1 | Minor | `TST-09` | `tests/java/shop/OrderServiceTest.java` · `OrderServiceTest#shipSendsShippedNotice` | The test checks that `orders.findById("o-7")` was called, but the same test already stubs that exact call with `when(orders.findById("o-7")).thenReturn(order);`. The stub matches the same argument the verification checks, so the verification only repeats the stub. | @Test void shipSendsShippedNotice() {     Order order = new Order("o-7", List.of("STD-1"), new BigDecimal("10.00"));     when(orders.findById("o-7")).thenReturn(order);     service.ship("o-7");     verify(mailer).sendShippedNotice(order); } |
| TST-01.1 | Minor | `TST-01` | `tests/java/shop/QuoteServiceTest.java` · `QuoteServiceTest#quoteTotalMocksMoneyValue` | The test mocks Money and stubs times(3) to return 29.97. Money is a record (tests/java/shop/Money.java) whose times() only multiplies a BigDecimal. It runs in process, is deterministic and is built with its constructor, which the same file already calls. |         Money unitPrice = new Money(new BigDecimal("9.99"), "EUR");         Quote quote = new QuoteService(Clock.systemUTC()).quote(unitPrice, 3);         assertEquals(new BigDecimal("29.97"), quote.total().amount()); |
| TST-04.1 | Minor | `TST-04` | `tests/java/shop/QuoteServiceTest.java` · `QuoteServiceTest#quoteTotalMocksMoneyValue` | The test mocks Money, a record (tests/java/shop/Money.java) whose members are its amount and currency fields, a constructor that validates them, and times(), which derives a new Money from those fields; it reaches no store, service or I/O, so it is a value the test can construct for real. | Money unitPrice = new Money(new BigDecimal("9.99"), "EUR");         Quote quote = new QuoteService(Clock.systemUTC()).quote(unitPrice, 3);         assertEquals(new BigDecimal("29.97"), quote.total().amount()); |
| TST-02.1 | Minor | `TST-02` | `tests/java/shop/ReservationServiceTest.java` · `ReservationServiceTest#reserveStubsEveryInventoryGatewayMethod` | The test stubs every non-private method of InventoryGateway on one mock instance. The interface declares three: stockOf, warehouseFor and reserve, and lines 15-17 stub all of them. The double re-creates the whole gateway call by call and does not fake any single dependency. | @Test void reserveConfirmsStockInTheWarehouseThatHoldsIt() {     InventoryGateway inventory = new InventoryGateway() {         private int onHand = 5;          @Override         public int stockOf(String sku) {             return onHand;         }          @Override         public String warehouseFor(String sku) {             return "BER-1";         }          @Override         public boolean reserve(String sku, int quantity) {             if (onHand < quantity) {                 return false;             }             onHand -= quantity;             return true;         }     };     DeliveryEstimator delivery = warehouse -> 2;     Reservation reservation = new ReservationService(inventory, delivery).reserve("sku-1", 2);     assertTrue(reservation.confirmed());     assertEquals("BER-1", reservation.warehouse()); } |
| TST-03.1 | Minor | `TST-03` | `tests/python/test_profiles.py` · `test_profiles.test_profile_name_is_guest_when_directory_raises_key_error` | The stub makes UserDirectory.find raise KeyError for an unknown user id. The real method's docstring rules this out for that case: "Return the user with this id, or None when no user has it. Raises DirectoryUnavailable when the LDAP server does not answer. An unknown id is not an error: find returns None for it and raises nothing." Its signature, `def find(self, user_id: int) -> Optional[User]`, also gives None as the normal result. | def test_profile_name_is_guest_for_unknown_id():     directory = create_autospec(UserDirectory, instance=True)     directory.find.return_value = None     assert Profiles(directory).name(7) == "guest" |
| TST-01.2 | Minor | `TST-01` | `tests/python/test_release_notes.py` · `test_release_notes.test_render_notes_patches_markdown_package` | The test patches markdown.markdown, an in-process, deterministic third-party Markdown renderer that needs no setup. The output it returns, "<ul><li>Fix login</li></ul>", is not what the real library produces: the repo's own test_markdown_renderer_integration.py asserts "<ul>\n<li>Fix login</li>\n</ul>". The test therefore asserts HTML that render_notes never returns in production. | def test_render_notes_wraps_real_markdown_output():     html = render_notes(["Fix login"])     assert html == '<section class="notes"><ul>\n<li>Fix login</li>\n</ul></section>' |
| TST-01.3 | Minor | `TST-01` | `tests/python/test_release_notes.py` · `test_release_notes.test_render_notes_through_project_renderer` | The test doubles MarkdownRenderer, the project's no-argument wrapper whose to_html only calls the in-process markdown library. The stubbed to_html returns "<ul><li>Fix login</li></ul>", while the real renderer returns "<ul>\n<li>Fix login</li>\n</ul>" (see test_markdown_renderer_integration.py). render_notes is checked against output that its real collaborator never produces. Having an integration test for the wrapper is not one of the card's Limits: the wrapper is not hard to set up, slow or external. | def test_render_notes_through_project_renderer():     html = render_notes(["Fix login"], MarkdownRenderer())     assert html == '<section class="notes"><ul>\n<li>Fix login</li>\n</ul></section>' |
| TST-06.1 | Minor | `TST-06` | `tests/python/test_release_notes.py` · `test_release_notes.test_render_notes_patches_markdown_package` | The test patches `markdown.markdown`, a function from the third-party `markdown` package (markdown==3.7 in requirements.txt), which `release_notes.MarkdownRenderer.to_html` calls. The project already has its own wrapper, MarkdownRenderer, and an integration test runs that wrapper against the real library, so this patch skips the project's own seam and imitates the library API directly. | def test_render_notes_patches_markdown_package():     renderer = Mock(spec=MarkdownRenderer)     renderer.to_html.return_value = "<ul><li>Fix login</li></ul>"     html = render_notes(["Fix login"], renderer)     assert html == '<section class="notes"><ul><li>Fix login</li></ul></section>' |
| TST-10.1 | Minor | `TST-10` | `tests/python/test_welcome_flow.py` · `test_welcome_flow.test_welcome_mail_addresses_member_by_name` | The test is named for addressing the member by name, which only needs the greeting argument "Welcome, Ann!". The check also pins literal values the behaviour does not decide: template="welcome-v3", locale="en-GB", track_opens=True, and the recipient address, which test_welcome_mail_goes_to_member_address already covers. |     mailer.send.assert_called_once_with(ANY, "Welcome, Ann!", template=ANY, locale=ANY, track_opens=ANY) |
| LOGIC.17 | Minor | `LOGIC` | `tests/ts/checkout.test.ts` · `test("checkoutTotalOnATuesdayTakesTenPercentOff")` | The test pins a UTC instant, but Checkout.total reads the weekday with Date#getDay(), which uses the host's local time zone. 2026-03-03T10:00Z is only a Tuesday in zones from UTC-10 to UTC+13. In Pacific/Pago_Pago or Etc/GMT+12 it is Monday 23:00/22:00, and in Pacific/Kiritimati it is Wednesday 00:00. In those zones DiscountRules returns 5, the total is 95 instead of 90, and the test fails. | const clock: jest.Mocked<Clock> = { now: jest.fn().mockReturnValue(new Date(2026, 2, 3, 10, 0, 0)) }; // local-time Tuesday in every zone |
| TST-01.4 | Minor | `TST-01` | `tests/ts/checkout.test.ts` · `test("checkoutTotalStubsDiscountRules")` | The test replaces DiscountRules with a jest.fn() stub that always answers 5. DiscountRules (tests/ts/discount-rules.ts) is an in-process, deterministic domain-rules class with a no-argument constructor, and the file already builds it as `new DiscountRules()`. The clock is the only external dependency here, and the next line already doubles it. |   const clock: Clock = { now: () => new Date("2026-03-04T10:00:00Z") };   const checkout = new Checkout(new DiscountRules(), clock);   expect(checkout.total([{ sku: "sku-1", price: 50, quantity: 2 }])).toBe(95); |
| TST-12.1 | Minor | `TST-12` | `tests/ts/invoice.test.ts` · `test("invoiceTotalStubsItsOwnTaxMethod")` | The test spies on InvoiceCalculator, the unit under test, and stubs that unit's own taxFor method while total() runs for real. That turns the calculator into a partial double. No comment or project context marks this code as legacy, a third-party interface or an interim refactoring step. | test("invoiceTotalAddsRegionalTax", () => {   const taxes = new TaxTable();   jest.spyOn(taxes, "rateFor").mockReturnValue(0.19);   const calculator = new InvoiceCalculator(taxes);   expect(calculator.total([{ net: 100, region: "DE" }])).toBe(119); }); |
| LOGIC.18 | Minor | `LOGIC` | `tests/ts/order-history.test.ts` · `InMemoryOrderRepository#save` | The fake claims to implement OrderRepository, but its save() does not follow the interface's documented contract that "save() rejects with DuplicateOrderError for an id already stored". It quietly adds a second row with the same id, which PgOrderRepository turns into a DuplicateOrderError. | // import { DuplicateOrderError, Order, OrderHistory, OrderRepository } from "./order-repository"; async save(order: Order): Promise<void> {   if (this.rows.some((row) => row.id === order.id)) {     throw new DuplicateOrderError(`order ${order.id} already exists`);   }   this.rows.push(order); } |
| TST-05.1 | Minor | `TST-05` | `tests/ts/order-history.test.ts` · `InMemoryOrderRepository` | The diff adds InMemoryOrderRepository, a hand-written fake that keeps state and stands in for PgOrderRepository, and no suite runs the OrderRepository tests against both implementations. Nothing in the test tree constructs PgOrderRepository, and the only describe.each covers the SessionStore contract. The two already disagree. The interface doc says save() rejects a stored id with DuplicateOrderError, and PgOrderRepository#save maps code 23505 to that error. InMemoryOrderRepository#save always pushes the row. | import { Pool } from "pg"; import { DuplicateOrderError, Order, OrderHistory, OrderRepository, PgOrderRepository } from "./order-repository";  class InMemoryOrderRepository implements OrderRepository {   private readonly rows: Order[] = [];    async save(order: Order): Promise<void> {     if (this.rows.some((row) => row.id === order.id)) {       throw new DuplicateOrderError(`order ${order.id} already exists`);     }     this.rows.push(order);   }    async findByCustomer(customer: string): Promise<Order[]> {     return this.rows       .filter((order) => order.customer === customer)       .sort((a, b) => b.placedAt.getTime() - a.placedAt.getTime());   } }  // One contract suite runs against the fake and, when a test database is configured, the real Postgres repository. const pgUrl = process.env.ORDERS_TEST_DATABASE_URL; const pool = pgUrl ? new Pool({ connectionString: pgUrl }) : undefined; afterAll(async () => {   await pool?.end(); });  const implementations: Array<[string, () => Promise<OrderRepository>]> = [   ["InMemoryOrderRepository", async () => new InMemoryOrderRepository()], ]; if (pool) {   implementations.push(["PgOrderRepository", async () => {     await pool.query("TRUNCATE orders");     return new PgOrderRepository(pool);   }]); }  describe.each(implementations)("OrderRepository contract (%s)", (_name, makeRepo) => {   test("findByCustomerListsNewestFirst", async () => {     const repo = await makeRepo();     await repo.save({ id: "o-1", customer: "ann", total: 20, placedAt: new Date("2026-03-01T09:00:00Z") });     await repo.save({ id: "o-2", customer: "ann", total: 35, placedAt: new Date("2026-03-05T09:00:00Z") });     expect((await repo.findByCustomer("ann")).map((order) => order.id)).toEqual(["o-2", "o-1"]);   });    test("saveRejectsADuplicateId", async () => {     const repo = await makeRepo();     const order: Order = { id: "o-1", customer: "ann", total: 20, placedAt: new Date("2026-03-01T09:00:00Z") };     await repo.save(order);     await expect(repo.save(order)).rejects.toBeInstanceOf(DuplicateOrderError);   }); });  test("latestOrderIsTheNewestPlaced", async () => {   const repo = new InMemoryOrderRepository();   await repo.save({ id: "o-1", customer: "ann", total: 20, placedAt: new Date("2026-03-01T09:00:00Z") });   await repo.save({ id: "o-2", customer: "ann", total: 35, placedAt: new Date("2026-03-05T09:00:00Z") });   expect((await new OrderHistory(repo).latestFor("ann"))?.id).toBe("o-2"); }); |
| TST-08.1 | Minor | `TST-08` | `tests/ts/shipping.test.ts` · `test("shippingQuoteSurfacesPrimaryCarrierFailure")` | The test creates a `fallback` CarrierApi double and stubs `quote` to resolve 20, but never hands it to the code under test. `ShippingQuotes` is built as `new ShippingQuotes(primary)`. The only other mention of `fallback` is its own stubbing, so the stub never runs. | test("shippingQuoteSurfacesPrimaryCarrierFailure", async () => {   const primary: jest.Mocked<CarrierApi> = { quote: jest.fn().mockRejectedValue(new Error("carrier timeout")) };   const quotes = new ShippingQuotes(primary);   await expect(quotes.quote("DE", 2)).rejects.toThrow("carrier timeout"); }); |
| CODE-04.1 | Suggestion | `CODE-04` | `code/go/stockroom.go` · `Stockroom.ReserveUnits` | The added short variable declaration names the units of sku still available to reserve `foo`, a metasyntactic placeholder that says nothing about what the value holds. | 	available := s.AvailableUnits(sku) 	if available < quantity { 		return fmt.Errorf("reserve %d units of %s: only %d available", quantity, sku, available) 	} |
| CODE-09.1 | Suggestion | `CODE-09` | `code/go/stockroom.go` · `Stockroom.AvailableUnits` | The local variable rsrvdUnits shortens "reserved" to "rsrvd" by deleting its vowels. That spelling is a contraction the author made up, not a known abbreviation. | 	reservedUnits := s.reserved[sku] 	if reservedUnits >= s.levels[sku] { 		return 0 	} 	return s.levels[sku] - reservedUnits |
| CODE-07.1 | Suggestion | `CODE-07` | `code/go/supplier_client.go` · `SupplierClient#WebhookTarget` | The local variable `callbackUrl` writes the initialism URL as `Url`. Go's convention keeps an initialism in one case, so it should be `callbackURL`. The same file already does this with `publicBaseURL` and `CallbackURL`. | 	callbackURL := c.publicBaseURL + "/hooks/" + url.PathEscape(eventKind) 	if c.tenant != "" { 		callbackURL += "?tenant=" + url.QueryEscape(c.tenant) 	} 	return callbackURL |
| CODE-08.1 | Suggestion | `CODE-08` | `code/java/ShipmentPlanner.java` · `ShipmentPlanner#countShipmentsByCarrier` | The local `carrierMap` ends in the word `Map`, which repeats the `Map<String, Integer>` type its declaration already states. The name says what the keys are but not what the value is for: a count of shipments for each carrier. |         Map<String, Integer> shipmentsPerCarrier = new HashMap<>();         for (Shipment shipment : shipments) {             shipmentsPerCarrier.merge(shipment.carrier(), 1, Integer::sum);         }         return shipmentsPerCarrier; |
| CODE-05.1 | Suggestion | `CODE-05` | `code/rust/route_table.rs` · `RouteTable::hub_status` | `hub_status` takes `&self`, so it does not change state, and it returns a bool. Its name ends in the bare noun `status`, which names the subject but not the claim. The body returns true when the hub is open and below capacity, but neither the name nor the doc comment ("Reports the hub's state") says which state true means. |     /// Whether the hub is open and still below capacity, so it can take a new shipment today.     pub fn can_accept_shipment(&self, hub: &str) -> bool {         let closed = self.closed_hubs.contains(hub);         let load = self.load_by_hub.get(hub).copied().unwrap_or(0);         !closed && load < self.hub_capacity     }     // caller: if table.can_accept_shipment(&hub.code) { ... } |
| LOGIC.19 | Suggestion | `LOGIC` | `tests/ts/shipping.test.ts` · `test("shippingQuoteSurfacesPrimaryCarrierFailure")` | The test builds a fallback double that resolves 20 and never passes it to ShippingQuotes, so the test only covers the no-fallback branch. Because the setup includes a fallback, the test reads as if a primary failure surfaces even when a fallback is configured. The SUT does the opposite: it would return 20. The 'primary rejects, fallback answers' branch is left with no test. | test("shippingQuoteSurfacesPrimaryCarrierFailureWithoutFallback", async () => {   const primary: jest.Mocked<CarrierApi> = { quote: jest.fn().mockRejectedValue(new Error("carrier timeout")) };   await expect(new ShippingQuotes(primary).quote("DE", 2)).rejects.toThrow("carrier timeout"); });  test("shippingQuoteFallsBackWhenPrimaryFails", async () => {   const primary: jest.Mocked<CarrierApi> = { quote: jest.fn().mockRejectedValue(new Error("carrier timeout")) };   const fallback: jest.Mocked<CarrierApi> = { quote: jest.fn().mockResolvedValue(20) };   await expect(new ShippingQuotes(primary, fallback).quote("DE", 2)).resolves.toBe(20); }); |

