# How the gateway limits a client's requests

The gateway lets each client send a burst of requests and then holds it to a steady rate. It does this with a count of tokens for every client: a request spends one token, and tokens come back with time. This page explains how the count moves. The mechanism is five steps and two numbers it keeps.

## The whole mechanism

The mechanism keeps two numbers for every client: its tokens and the time of its last request. It takes in one event, a request from the client, with the time it arrived.

On a request the gateway adds ten tokens for every second since the client's last request. With at least one token the gateway takes one and passes the request on. With less than one token it refuses the request and tells the client how long to wait for the next token. In both cases it notes the time of this request as the client's last.

```
tokens = tokens + 10 × (now − last)
if tokens ≥ 1:   tokens = tokens − 1; pass the request on
else:            refuse; reply "wait (1 − tokens) / 10 seconds"
last = now
```

A client that was silent for a minute can send one hundred requests at once and ten a second after that.
