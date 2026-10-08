package serving

import "time"

// Server serves one listen address with a request timeout the operator can tune.
type Server struct {
	addr    string
	timeout time.Duration
}

// NewServer builds a server for addr with the default request timeout.
func NewServer(addr string) *Server {
	return &Server{addr: addr, timeout: 30 * time.Second}
}

// Addr is the listen address.
func (s *Server) Addr() string {
	return s.addr
}

// SetAddr changes the listen address.
func (s *Server) SetAddr(addr string) {
	s.addr = addr
}

// Timeout is the request timeout.
func (s *Server) Timeout() time.Duration {
	return s.timeout
}

// SetTimeout changes the request timeout; Configure calls it once the server is built.
func (s *Server) SetTimeout(d time.Duration) {
	s.timeout = d
}

// Configure applies the operator's settings to a server that is already built.
func Configure(s *Server, requestTimeout time.Duration) {
	s.SetTimeout(requestTimeout)
}
