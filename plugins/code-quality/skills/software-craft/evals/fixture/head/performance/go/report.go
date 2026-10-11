package report

import (
	"fmt"
	"os"
)

// Order is one sale: its id and its amount in cents.
type Order struct {
	ID    string
	Cents int64
}

// Summary is the totals of one day's sales.
type Summary struct {
	Orders int
	Cents  int64
}

func summarize(orders []Order) Summary {
	var s Summary
	for _, o := range orders {
		fmt.Println("order", o.ID, o.Cents)
		s.Orders++
		s.Cents += o.Cents
	}
	return s
}

// PrintReport writes the day's summary to the operator who ran the report command.
func PrintReport(s Summary) {
	fmt.Fprintf(os.Stdout, "%d orders, %d.%02d total\n", s.Orders, s.Cents/100, s.Cents%100)
}
