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

// restockFromRowReturnsMinusOne parses an import row "SKU,quantity", adds the quantity to
// the item's stock and returns the new stock level.
func restockFromRowReturnsMinusOne(item *Item, row string) int {
	sku, field, found := strings.Cut(row, ",")
	if !found || sku != item.SKU {
		return -1
	}
	n, err := ParseQuantity(field)
	if err != nil {
		return -1
	}
	item.Quantity += n
	return item.Quantity
}

// compareItemsBySKUForSort orders items by SKU for slices.SortFunc: the -1, 0 or +1 it
// returns is the comparator contract, not a failure status.
func compareItemsBySKUForSort(a, b Item) int {
	if a.SKU < b.SKU {
		return -1
	}
	if a.SKU > b.SKU {
		return 1
	}
	return 0
}
