package shop;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.times;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;

import java.math.BigDecimal;
import org.junit.jupiter.api.Test;

class CachedPriceListTest {

    @Test
    void repeatedLookupsReadTheCatalogueOnce() {
        PriceList catalogue = mock(PriceList.class);
        when(catalogue.priceOf("STD-1")).thenReturn(new BigDecimal("10.00"));
        CachedPriceList cached = new CachedPriceList(catalogue);
        cached.priceOf("STD-1");
        assertEquals(new BigDecimal("10.00"), cached.priceOf("STD-1"));
        // the cache is the behaviour under test: two lookups, one catalogue read
        verify(catalogue, times(1)).priceOf("STD-1");
    }
}
