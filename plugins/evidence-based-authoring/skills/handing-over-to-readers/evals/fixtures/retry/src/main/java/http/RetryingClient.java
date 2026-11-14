package http;

import java.net.http.HttpTimeoutException;

/** Sends a request and repeats it after a timeout, as the policy says. */
public final class RetryingClient {
    public static final long TIMEOUT_MILLIS = 2_000;

    private final Transport transport;
    private final Sleeper sleeper;
    private final RetryPolicy policy = new RetryPolicy();

    public RetryingClient(Transport transport, Sleeper sleeper) {
        this.transport = transport;
        this.sleeper = sleeper;
    }

    public Response send(Request request) throws HttpTimeoutException {
        HttpTimeoutException last = null;
        for (int attempt = 1; attempt <= RetryPolicy.MAX_ATTEMPTS; attempt++) {
            sleeper.sleep(policy.delayBeforeMillis(attempt));
            try {
                return transport.send(request, TIMEOUT_MILLIS);
            } catch (HttpTimeoutException e) {
                last = e;
            }
        }
        throw last;
    }
}
