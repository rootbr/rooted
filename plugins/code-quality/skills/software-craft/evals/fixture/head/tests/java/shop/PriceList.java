package shop;

import java.math.BigDecimal;

/** Catalogue unit prices, read from the pricing database. */
public interface PriceList {

    BigDecimal priceOf(String sku);
}
