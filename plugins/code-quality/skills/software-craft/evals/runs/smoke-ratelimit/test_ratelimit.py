import inspect
import math
import time

import pytest

from ratelimit import ClockWentBackwards, InvalidBucketParameters, InvalidTokenRequest, TokenBucket


class ManualClock:
    """A clock the test sets by hand: every reading is the value the test last stored in `now`."""

    def __init__(self, now: float = 0.0) -> None:
        self.now = now

    def __call__(self) -> float:
        return self.now


def test_bucket_starts_full_and_grants_up_to_capacity():
    bucket = TokenBucket(capacity=3, refill_rate=1, clock=ManualClock())
    assert [bucket.try_acquire() for _ in range(4)] == [True, True, True, False]


def test_acquire_takes_n_tokens_at_once():
    bucket = TokenBucket(capacity=5, refill_rate=1, clock=ManualClock())
    assert bucket.try_acquire(3) is True
    assert bucket.try_acquire(3) is False
    assert bucket.try_acquire(2) is True


def test_refused_request_consumes_no_tokens():
    bucket = TokenBucket(capacity=4, refill_rate=1, clock=ManualClock())
    assert bucket.try_acquire(3) is True
    assert bucket.try_acquire(2) is False
    assert bucket.try_acquire(1) is True
    assert bucket.try_acquire(1) is False


def test_tokens_refill_continuously_and_accumulate_across_refusals():
    clock = ManualClock()
    bucket = TokenBucket(capacity=4, refill_rate=2, clock=clock)
    assert bucket.try_acquire(4) is True
    clock.now = 0.25  # half a token has refilled
    assert bucket.try_acquire() is False
    clock.now = 0.5  # the refused call kept the half token: one whole token now
    assert bucket.try_acquire() is True
    assert bucket.try_acquire() is False


def test_refill_stops_at_capacity():
    clock = ManualClock()
    bucket = TokenBucket(capacity=2, refill_rate=10, clock=clock)
    assert bucket.try_acquire(2) is True
    clock.now = 100.0
    assert bucket.try_acquire(2) is True
    assert bucket.try_acquire() is False


def test_clock_defaults_to_monotonic_time():
    assert inspect.signature(TokenBucket).parameters["clock"].default is time.monotonic


@pytest.mark.parametrize("capacity", [0, -1, math.nan, math.inf])
def test_capacity_must_be_positive_and_finite(capacity):
    with pytest.raises(InvalidBucketParameters, match=f"capacity {capacity!r}"):
        TokenBucket(capacity=capacity, refill_rate=1, clock=ManualClock())


@pytest.mark.parametrize("refill_rate", [0, -0.5, math.nan, math.inf])
def test_refill_rate_must_be_positive_and_finite(refill_rate):
    with pytest.raises(InvalidBucketParameters, match=f"refill rate {refill_rate!r}"):
        TokenBucket(capacity=1, refill_rate=refill_rate, clock=ManualClock())


@pytest.mark.parametrize("n", [0, -1, 3.5, math.nan])
def test_request_outside_one_to_capacity_is_rejected_and_takes_nothing(n):
    bucket = TokenBucket(capacity=3, refill_rate=1, clock=ManualClock())
    with pytest.raises(InvalidTokenRequest, match=rf"acquire {n!r} tokens: .* capacity 3"):
        bucket.try_acquire(n)
    assert bucket.try_acquire(3) is True


def test_request_equal_to_capacity_is_valid():
    bucket = TokenBucket(capacity=2.5, refill_rate=1, clock=ManualClock())
    assert bucket.try_acquire(2.5) is True


def test_clock_going_backwards_is_reported_and_leaves_tokens_untouched():
    clock = ManualClock(now=10.0)
    bucket = TokenBucket(capacity=2, refill_rate=1, clock=clock)
    assert bucket.try_acquire() is True
    clock.now = 9.0
    expected = "clock read 9.0, earlier than its previous reading 10.0"
    with pytest.raises(ClockWentBackwards, match=expected):
        bucket.try_acquire()
    clock.now = 10.0
    assert bucket.try_acquire() is True
    assert bucket.try_acquire() is False
