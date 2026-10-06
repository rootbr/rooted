package shop;

import java.math.BigDecimal;
import java.util.List;

public record Order(String id, List<String> skus, BigDecimal total) {
}
