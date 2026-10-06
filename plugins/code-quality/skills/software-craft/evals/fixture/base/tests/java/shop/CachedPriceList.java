package shop;

import java.math.BigDecimal;
import java.util.HashMap;
import java.util.Map;

/** Reads each SKU's price from the source price list once and answers repeats from memory. */
public final class CachedPriceList implements PriceList {
    private final PriceList source;
    private final Map<String, BigDecimal> cache = new HashMap<>();

    public CachedPriceList(PriceList source) {
        this.source = source;
    }

    @Override
    public BigDecimal priceOf(String sku) {
        return cache.computeIfAbsent(sku, source::priceOf);
    }
}
