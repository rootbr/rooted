package shop

import (
	"bytes"
	"fmt"
	"os"
)

// Order is a placed order; Total is in cents.
type Order struct {
	ID    string
	Total int64
}

// appendAuditLineIgnoresWriteError appends one line to the audit log at path.
func appendAuditLineIgnoresWriteError(path, line string) error {
	f, err := os.OpenFile(path, os.O_APPEND|os.O_CREATE|os.O_WRONLY, 0o600)
	if err != nil {
		return fmt.Errorf("open audit log %s: %w", path, err)
	}
	defer f.Close()
	f.WriteString(line + "\n")
	return nil
}

// renderReceiptLinesDiscardsBufferErrors formats one tab-separated line per order.
func renderReceiptLinesDiscardsBufferErrors(orders []Order) string {
	var buf bytes.Buffer
	for _, o := range orders {
		// bytes.Buffer.WriteString always returns a nil error; it panics instead when memory runs out
		_, _ = buf.WriteString(fmt.Sprintf("%s\t%d\n", o.ID, o.Total))
	}
	return buf.String()
}
