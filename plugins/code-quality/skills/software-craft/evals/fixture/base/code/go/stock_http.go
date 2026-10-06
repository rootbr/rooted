package inventory

import (
	"fmt"
	"net/http"
)

// ServeHealth reports that the stockroom service is up.
func ServeHealth(w http.ResponseWriter, r *http.Request) {
	fmt.Fprintln(w, "ok")
}
