// Package shop holds the order, stock and catalogue services of the web shop.
package shop

import (
	"fmt"
	"strconv"
	"strings"
)

// Item is one stock-keeping unit held in the warehouse.
type Item struct {
	SKU      string
	Quantity int
}

// ParseQuantity reads a quantity field from an import row.
func ParseQuantity(field string) (int, error) {
	n, err := strconv.Atoi(strings.TrimSpace(field))
	if err != nil {
		return 0, fmt.Errorf("parse quantity %q: %w", field, err)
	}
	return n, nil
}

// Reserve takes n units of the item out of stock.
func Reserve(item *Item, n int) error {
	if n > item.Quantity {
		return fmt.Errorf("reserve %d of %s: only %d in stock", n, item.SKU, item.Quantity)
	}
	item.Quantity -= n
	return nil
}

// restockFromRow parses an import row "SKU,quantity", adds the quantity to the item's
// stock and returns the new stock level.
func restockFromRow(item *Item, row string) (int, error) {
	sku, field, found := strings.Cut(row, ",")
	if !found || sku != item.SKU {
		return 0, fmt.Errorf("restock %s from row %q: SKU does not match", item.SKU, row)
	}
	n, err := ParseQuantity(field)
	if err != nil {
		return 0, fmt.Errorf("restock %s: %w", item.SKU, err)
	}
	item.Quantity += n
	return item.Quantity, nil
}
