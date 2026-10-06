# Smoke task: token-bucket rate limiter Craft Review

## Executive Summary
- Reviewed: `c65a23179a6e6936974fe27002154f8182f3aac6...worktree` (worktree) — 2 files (SMALL); languages: python 2
- Passes: pre-pass (worktree mode), 12 card finders, 2 logic passes, 2 skeptics; stage all, one workflow
- Findings: 2 (0 major, 2 minor, 0 suggestion)
- Verification: 2 raw findings → 2 confirmed, 0 downgraded, 0 rejected, 0 flagged for the author
- Fix round: none
- Recommendation: Merge with fixes

## What was built

# Smoke task — developer agent's report

Task: a token-bucket rate limiter in `errors/py/ratelimit.py` with tests in `errors/py/test_ratelimit.py`, on a copy of the fixture tree (committed mode, the change left uncommitted). Dispatch: a general-purpose agent carrying the body of `plugins/code-quality/agents/software-developer.md` (the plugin agent type does not resolve in a checkout), `claude-opus-5-5`, the write zone named in the task. Single run, unrepeated. The report below is the agent's, verbatim.

---

I built the token-bucket limiter in the two files the task allowed, and its 20 tests pass along with ruff, mypy and pyright. Changes are uncommitted; `git status` shows only the two new files plus the review's own `craft/` output.

**1. What changed**

`errors/py/ratelimit.py` (new):
- `InvalidBucketParameters(ValueError)`: raised by the constructor when capacity or refill rate is zero, negative, NaN or infinite. The message names the operation and the rejected value.
- `InvalidTokenRequest(ValueError)`: raised when `try_acquire` gets an `n` outside `(0, capacity]`. That covers zero, negative, NaN and over-capacity, since such a request could never succeed.
- `ClockWentBackwards(RuntimeError)`: raised when the injected clock reads earlier than its previous reading. A clock going backwards would otherwise silently drain tokens.
- `_is_positive_finite`: private check used by the constructor.
- `TokenBucket.__init__(capacity, refill_rate, clock=time.monotonic)`: the bucket starts full.
- `TokenBucket.try_acquire(n=1) -> bool`: takes `n` tokens and returns True, or returns False and takes none.
- `TokenBucket._refill`: refills continuously from elapsed clock time, capped at capacity.
- Every error is raised before any state changes.

`errors/py/test_ratelimit.py` (new):
- `ManualClock`: a clock the test sets by hand; every reading is a value the test stored.
- 11 test functions (20 cases with parametrization) covering: starting full and granting up to capacity; taking `n` tokens at once, and a refused request taking nothing; fractional refill that carries over across refused calls, and refill stopping at capacity; `time.monotonic` as the default clock, read from the signature without calling it; invalid capacity, rate and `n`, including that a rejected `n` takes no tokens and the exact-capacity request is allowed; a clock going backwards leaving tokens untouched. No sleeping and no real time.

**2. Cards applied**
- Naming: CODE-01, CODE-02, CODE-03, CODE-04, CODE-05, CODE-06, CODE-07, CODE-08, CODE-09, CODE-10, CODE-11, CODE-12.
- Errors: ERR-01, ERR-03, ERR-04, ERR-06, ERR-07, ERR-09, ERR-11, ERR-12.
- Tests: TST-01, TST-05, TST-07, TST-11, TST-12.
- Self-review fixed one finding: four test set-up calls ignored the `try_acquire` result, so they now assert it is True (ERR-07).
- Left in place because the cards' own exceptions cover them: CODE-03 and CODE-12, the parameter `n` (CODE-03 lists `n` as a conventional parameter letter; under CODE-12 a token count counts as a domain value, but the task's interface fixes the name, and it matches the standard library's `threading.Semaphore.release(n=1)`); CODE-07, exception names without an `Error` suffix (they follow the project's usual form, `InsufficientFunds` in `ledger.py`, `DirectoryUnavailable` in `tests/python`); TST-05 and TST-07, `ManualClock` only returns values the test stores; TST-11 does not apply to hand-written classes in Python, and mypy checks it against `Callable[[], float]` anyway.

**3. What I verified**
- `pytest -q test_ratelimit.py`: 20 passed in 0.03s.
- Mutation check on a scratch copy outside the repo: each of 7 deliberate breaks made some tests fail (removing the capacity cap, letting a refusal consume tokens, skipping the refill timestamp, dropping the over-capacity check, dropping the clock check, dropping the finite check, starting the bucket empty).
- `ruff check`: passed. `mypy --strict ratelimit.py` and `mypy --check-untyped-defs test_ratelimit.py`: no issues. `pyright ratelimit.py`: 0 errors.
- Line width is at most 107 columns, the width of the existing `errors/py` modules.
- Baseline before my change: ruff was clean on `errors/py`, black would reformat all four existing files (so I matched the files' own layout rather than black), and `tests/python` already fails collection on two files.
- `static-craft.py`: 2 files, 12 jobs, 0 candidates. I applied each named card's Validator question. I regenerated `craft/` from a clean state because a rerun had counted its own `plan.json` as part of the change.
- I removed the `__pycache__` directories my test runs created.

**4. Not verified**
- Pyright cannot type-check the test file because it can't find `pytest` (installed in a separate tool environment); mypy does check it.
- The repo has no formatter, linter or CI config, so there was no project-defined build to run.
- Thread safety is neither built nor tested; the class docstring says to put a lock around a shared instance.

**5. Reserved specialty:** none met. Thread-safe sharing was out of the task's scope, so I documented it rather than designing it.

**6. Questions for the operator**
- Should the parameter be renamed from `n` to `tokens`, which strict CODE-12 would prefer? That breaks callers who pass `n=` by keyword.
- Should the exception names take an `Error` suffix, as PEP 8 advises, which would match `ConfigError` instead of `InsufficientFunds`?
- Is a full bucket at construction the intended start? The task didn't say.
- Rejecting a non-positive or NaN `n`, non-finite construction values, and a clock that goes backwards goes beyond the cases the task listed. Are those extra failures wanted?
- Should the limiter be made thread-safe?

---

Operator's integrity check after the run: `git status` in the repository showed exactly the two new files and the review's `craft/` directory, as reported; `git diff --stat` showed no change to a tracked file. The pre-pass run the agent reports counted its own `craft/plan.json` as a changed file in worktree mode; that is a defect of the pre-pass, fixed in the deny-list after this run.

## Major Findings

None.

## Minor & Suggestions

| # | Severity | Rule | Location | Finding | Suggested fix |
|---|---|---|---|---|---|
| LOGIC.1 | Minor | `LOGIC` | `errors/py/ratelimit.py` · `TokenBucket#_refill` | The clock guard uses `<`, which is False for NaN, so a NaN clock reading gets past it. `refilled` becomes NaN, `min(self._capacity, refilled)` returns the capacity, and `_last_refill` is set to NaN. The next call with a valid reading computes NaN again and refills to full once more. That call stores a finite `_last_refill`, and limiting resumes after it. Each NaN reading therefore grants up to two extra full buckets of tokens and raises nothing. A clock that keeps returning NaN turns limiting off completely. |         self._tokens = capacity         self._last_refill = clock()         if math.isnan(self._last_refill):             raise InvalidBucketParameters(                 f"create token bucket: clock read {self._last_refill!r}, which is not a number"             )      ...      def _refill(self) -> None:         now = self._clock()         # written as `not >=` so that a NaN reading is refused too; `<` is false for NaN         if not now >= self._last_refill:             raise ClockWentBackwards(                 f"refill token bucket: clock read {now!r},"                 f" earlier than its previous reading {self._last_refill!r}"             ) |
| CODE-12.1 | Minor | `CODE-12` | `errors/py/ratelimit.py` · `TokenBucket#try_acquire` | The public method try_acquire is added in this change (the file is untracked, so there is no base version) and names its parameter `n`. The letter stands for a domain value, the number of tokens to take from the bucket. It is not a conventional letter (a generic float operand, a pointer, a reader or writer, a receiver), and the repository has no linter configuration that allows `n`. |     def try_acquire(self, tokens: float = 1) -> bool:         """Take `tokens` tokens and return True when at least that many are available; else take none, return False.          Raises InvalidTokenRequest when `tokens` is not greater than 0 and at most the capacity,         since such a request could never be granted, and ClockWentBackwards when the clock reads         earlier than it did before.         """         # the chained comparison is also false for NaN, so a NaN request is refused here too         if not 0 < tokens <= self._capacity:             raise InvalidTokenRequest(                 f"acquire {tokens!r} tokens: a request must be greater than 0"                 f" and at most the capacity {self._capacity!r}"             )         self._refill()         if self._tokens < tokens:             return False         self._tokens -= tokens         return True |

