package http;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertThrows;

import java.net.http.HttpTimeoutException;
import java.util.ArrayList;
import java.util.List;
import org.junit.jupiter.api.Test;

class RetryingClientTest {
    private final List<Long> sleeps = new ArrayList<>();
    private int attempts;

    private RetryingClient clientThatSucceedsOn(int successfulAttempt) {
        Transport transport = (request, timeoutMillis) -> {
            attempts++;
            assertEquals(2_000, timeoutMillis);
            if (attempts < successfulAttempt) {
                throw new HttpTimeoutException("timed out");
            }
            return new Response(200);
        };
        return new RetryingClient(transport, sleeps::add);
    }

    @Test
    void delaysDouble() {
        RetryPolicy policy = new RetryPolicy();
        assertEquals(List.of(0L, 200L, 400L, 800L),
            List.of(policy.delayBeforeMillis(1), policy.delayBeforeMillis(2), policy.delayBeforeMillis(3), policy.delayBeforeMillis(4)));
    }

    @Test
    void delayIsCappedAtOneSecond() {
        assertEquals(1_000, new RetryPolicy().delayBeforeMillis(6));
    }

    @Test
    void firstSuccessStopsTheLoop() throws Exception {
        assertEquals(200, clientThatSucceedsOn(2).send(new Request("GET", "/catalog")).status());
        assertEquals(2, attempts);
    }

    @Test
    void givesUpAfterFourAttempts() {
        assertThrows(HttpTimeoutException.class, () -> clientThatSucceedsOn(99).send(new Request("GET", "/catalog")));
        assertEquals(4, attempts);
    }

    @Test
    void waitsBetweenAttempts() {
        assertThrows(HttpTimeoutException.class, () -> clientThatSucceedsOn(99).send(new Request("GET", "/catalog")));
        assertEquals(List.of(0L, 200L, 400L, 800L), sleeps);
    }
}
