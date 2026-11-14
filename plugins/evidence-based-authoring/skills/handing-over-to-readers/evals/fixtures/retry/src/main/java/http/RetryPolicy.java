package http;

/** Delays between attempts: 200 ms, doubled for each further attempt, at most one second; four attempts in all. */
public final class RetryPolicy {
    public static final int MAX_ATTEMPTS = 4;
    private static final long BASE_DELAY_MILLIS = 200;
    private static final long MAX_DELAY_MILLIS = 1_000;

    /** Delay before the attempt with this number; the first attempt starts at once. */
    public long delayBeforeMillis(int attempt) {
        if (attempt <= 1) {
            return 0;
        }
        long delay = BASE_DELAY_MILLIS << (attempt - 2);
        return Math.min(delay, MAX_DELAY_MILLIS);
    }
}
