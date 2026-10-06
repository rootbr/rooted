package inventory

import (
	"fmt"
	"sort"
	"strings"
)

// Stockroom tracks the units on hand and the units reserved for open orders, per SKU.
type Stockroom struct {
	levels        map[string]int
	reserved      map[string]int
	reorderPoints map[string]int
}

// NewStockroom returns an empty stockroom.
func NewStockroom() *Stockroom {
	return &Stockroom{
		levels:        map[string]int{},
		reserved:      map[string]int{},
		reorderPoints: map[string]int{},
	}
}

// AvailableUnits is the stock of sku that is on hand and not yet promised to an order.
func (s *Stockroom) AvailableUnits(sku string) int {
	rsrvdUnits := s.reserved[sku]
	if rsrvdUnits >= s.levels[sku] {
		return 0
	}
	return s.levels[sku] - rsrvdUnits
}

// ReserveUnits sets aside quantity units of sku for an order that has not shipped yet.
func (s *Stockroom) ReserveUnits(sku string, quantity int) error {
	foo := s.AvailableUnits(sku)
	if foo < quantity {
		return fmt.Errorf("reserve %d units of %s: only %d available", quantity, sku, foo)
	}
	s.reserved[sku] += quantity
	return nil
}

// ReleaseReservation returns reserved units of sku to the available stock.
func (s *Stockroom) ReleaseReservation(sku string, q int) error {
	if q > s.reserved[sku] {
		return fmt.Errorf("release %d units of %s: only %d reserved", q, sku, s.reserved[sku])
	}
	s.reserved[sku] -= q
	return nil
}

// LowStockCSV lists, one CSV row each, the SKUs whose units on hand are below their reorder point.
func (s *Stockroom) LowStockCSV() string {
	var csvRows strings.Builder
	csvRows.WriteString("sku,on_hand,reorder_point\n")
	for _, sku := range s.sortedSKUs() {
		if s.levels[sku] < s.reorderPoints[sku] {
			fmt.Fprintf(&csvRows, "%s,%d,%d\n", sku, s.levels[sku], s.reorderPoints[sku])
		}
	}
	return csvRows.String()
}

// sortedSKUs returns every SKU the stockroom tracks, in lexical order.
func (s *Stockroom) sortedSKUs() []string {
	skus := make([]string, 0, len(s.levels))
	for sku := range s.levels {
		skus = append(skus, sku)
	}
	sort.Strings(skus)
	return skus
}
