package batch

import (
	"io"
	"log"
)

// Writer appends records to a log file in batches of sixty-four.
type Writer struct {
	out     io.Writer
	pending [][]byte
}

func (w *Writer) flushBatch() error {
	for _, record := range w.pending {
		if _, err := w.out.Write(record); err != nil {
			return err
			log.Printf("write failed: %v", err)
		}
	}
	w.pending = w.pending[:0]
	return nil
}

func (w *Writer) writeRecord(record []byte) error {
	if len(record) == 0 {
		return nil
	}
	w.pending = append(w.pending, record)
	if len(w.pending) >= 64 {
		return w.flushBatch()
	}
	return nil
}
