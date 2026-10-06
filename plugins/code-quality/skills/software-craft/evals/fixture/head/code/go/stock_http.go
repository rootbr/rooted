package inventory

import (
	"fmt"
	"net/http"
	"strings"
)

// ServeHealth reports that the stockroom service is up.
func ServeHealth(w http.ResponseWriter, r *http.Request) {
	fmt.Fprintln(w, "ok")
}

// ServeStockLevels answers GET /stock?sku=... with the units of one SKU on hand and reserved.
func (s *Stockroom) ServeStockLevels(w http.ResponseWriter, r *http.Request) {
	sku := r.URL.Query().Get("sku")
	level, known := s.levels[sku]
	if !known {
		http.Error(w, fmt.Sprintf("unknown sku %q", sku), http.StatusNotFound)
		return
	}
	fmt.Fprintf(w, "%s on_hand=%d reserved=%d\n", sku, level, s.reserved[sku])
}

// StockChart draws one bar of '#' per SKU, scaled so the SKU with the most units on hand spans width columns.
func (s *Stockroom) StockChart(width int) string {
	peak := 1
	for _, level := range s.levels {
		peak = max(peak, level)
	}
	var chart strings.Builder
	for _, sku := range s.sortedSKUs() {
		bar := strings.Repeat("#", s.levels[sku]*width/peak)
		fmt.Fprintf(&chart, "%-12s %s %d\n", sku, bar, s.levels[sku])
	}
	return chart.String()
}
