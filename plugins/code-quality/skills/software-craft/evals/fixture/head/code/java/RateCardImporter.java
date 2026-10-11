package shipping;

import java.math.BigDecimal;
import java.util.ArrayList;
import java.util.List;
import java.util.regex.Pattern;

/** Reads a carrier's rate card: one line per zone and weight band, with the price to ship it. */
public class RateCardImporter {
    private static final int COLUMN_COUNT = 3;

    private final Pattern separator;

    public RateCardImporter(char delimiter) {
        this.separator = Pattern.compile(Pattern.quote(String.valueOf(delimiter)));
    }

    List<RateCard> importLines(List<String> lines) {
        List<RateCard> rateCards = new ArrayList<>();
        for (String line : lines) {
            if (!line.isBlank()) {
                rateCards.add(parseRateRow(line));
            }
        }
        return rateCards;
    }

    RateCard parseRateRow(String line) {
        String[] columns = separator.split(line);
        if (columns.length != COLUMN_COUNT) {
            throw new IllegalArgumentException("rate row needs zone, weight and price, was: " + line);
        }
        String zone = columns[0].trim();
        String weightString = columns[1].trim();
        double weight = Double.parseDouble(weightString);
        if (weight <= 0) {
            throw new IllegalArgumentException("rate row weight must be positive, was " + weightString);
        }
        BigDecimal price = new BigDecimal(columns[2].trim());
        return new RateCard(zone, weight, price);
    }
}
