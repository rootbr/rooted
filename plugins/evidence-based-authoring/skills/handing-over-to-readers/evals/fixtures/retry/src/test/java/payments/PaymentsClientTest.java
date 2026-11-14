package payments;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertThrows;

import http.Request;
import http.Response;
import http.RetryingClient;
import java.net.http.HttpTimeoutException;
import org.junit.jupiter.api.Test;

/** Owned by the payments team. */
class PaymentsClientTest {
    private int attempts;

    /** A payment reaches the gateway at most once: a POST that timed out may have been applied. */
    @Test
    void postIsNotRetriedOnTimeout() {
        RetryingClient client = new RetryingClient((request, timeoutMillis) -> {
            attempts++;
            throw new HttpTimeoutException("timed out");
        }, millis -> { });
        assertThrows(HttpTimeoutException.class, () -> client.send(new Request("POST", "/payments")));
        assertEquals(1, attempts);
    }
}
