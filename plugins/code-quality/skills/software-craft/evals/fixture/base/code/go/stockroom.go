package inventory

import "fmt"

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

// ReserveUnits sets aside quantity units of sku for an order that has not shipped yet.
func (s *Stockroom) ReserveUnits(sku string, quantity int) error {
	if s.levels[sku] < quantity {
		return fmt.Errorf("reserve %d units of %s: only %d on hand", quantity, sku, s.levels[sku])
	}
	s.reserved[sku] += quantity
	return nil
}

// ReleaseReservation drops every unit reserved for sku.
func (s *Stockroom) ReleaseReservation(sku string) {
	delete(s.reserved, sku)
}
