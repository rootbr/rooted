"""Token-bucket rate limiting: a bucket of tokens that refills continuously at a fixed rate."""
import math
import time
from collections.abc import Callable


class InvalidBucketParameters(ValueError):
    """A token bucket was given a capacity or refill rate that is not a positive finite number."""


class InvalidTokenRequest(ValueError):
    """try_acquire asked for a token count no bucket can grant: not positive, or above the capacity."""


class ClockWentBackwards(RuntimeError):
    """The bucket's clock returned a reading earlier than one it returned before."""


def _is_positive_finite(value: float) -> bool:
    return math.isfinite(value) and value > 0


class TokenBucket:
    """A rate limiter holding up to `capacity` tokens, refilled at `refill_rate` tokens per second.

    The bucket starts full. `clock` returns seconds as a float and must never go backwards; it
    defaults to time.monotonic. One instance is not safe to share between threads without a lock.
    """

    def __init__(
        self, capacity: float, refill_rate: float, clock: Callable[[], float] = time.monotonic
    ) -> None:
        if not _is_positive_finite(capacity):
            raise InvalidBucketParameters(
                f"create token bucket: capacity {capacity!r} is not a positive finite number"
            )
        if not _is_positive_finite(refill_rate):
            raise InvalidBucketParameters(
                f"create token bucket: refill rate {refill_rate!r} tokens per second"
                " is not a positive finite number"
            )
        self._capacity = capacity
        self._refill_rate = refill_rate
        self._clock = clock
        self._tokens = capacity
        self._last_refill = clock()

    def try_acquire(self, n: float = 1) -> bool:
        """Take `n` tokens and return True when at least `n` are available; else take none, return False.

        Raises InvalidTokenRequest when `n` is not greater than 0 and at most the capacity, since
        such a request could never be granted, and ClockWentBackwards when the clock reads earlier
        than it did before.
        """
        # the chained comparison is also false for NaN, so a NaN request is refused here too
        if not 0 < n <= self._capacity:
            raise InvalidTokenRequest(
                f"acquire {n!r} tokens: a request must be greater than 0"
                f" and at most the capacity {self._capacity!r}"
            )
        self._refill()
        if self._tokens < n:
            return False
        self._tokens -= n
        return True

    def _refill(self) -> None:
        now = self._clock()
        if now < self._last_refill:
            raise ClockWentBackwards(
                f"refill token bucket: clock read {now!r},"
                f" earlier than its previous reading {self._last_refill!r}"
            )
        refilled = self._tokens + (now - self._last_refill) * self._refill_rate
        self._tokens = min(self._capacity, refilled)
        self._last_refill = now
