package shop;

import java.time.Clock;
import java.time.LocalDate;

public final class QuoteService {
    private static final int VALIDITY_DAYS = 14;

    private final Clock clock;

    public QuoteService(Clock clock) {
        this.clock = clock;
    }

    public Quote quote(Money unitPrice, int quantity) {
        return new Quote(unitPrice.times(quantity), LocalDate.now(clock).plusDays(VALIDITY_DAYS));
    }
}
