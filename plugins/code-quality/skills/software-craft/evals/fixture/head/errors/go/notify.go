package shop

import (
	"fmt"
	"log"
	"net/http"
	"strconv"
	"text/template"
	"time"
)

// retryDelayExitsOnBadHeader reads how long the mail API asks the client to wait after a
// rate-limited reply.
func retryDelayExitsOnBadHeader(resp *http.Response) time.Duration {
	header := resp.Header.Get("Retry-After")
	secs, err := strconv.Atoi(header)
	if err != nil {
		log.Fatalf("parse Retry-After header %q: %v", header, err)
	}
	return time.Duration(secs) * time.Second
}

// mustParseBuiltinTemplate parses one of the constant templates below. It runs only during
// package initialization and only on those fixed texts, never on user input, so a failure is
// a programming error that shows on the first start.
func mustParseBuiltinTemplate(name, text string) *template.Template {
	t, err := template.New(name).Parse(text)
	if err != nil {
		panic(fmt.Sprintf("parse built-in template %s: %v", name, err))
	}
	return t
}

var receiptMailTemplate = mustParseBuiltinTemplate("receipt-mail", "Order {{.ID}}: {{.Total}} cents\n")
