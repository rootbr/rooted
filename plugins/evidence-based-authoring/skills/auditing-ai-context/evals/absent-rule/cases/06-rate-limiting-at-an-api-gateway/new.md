# Gateway Rate Limiting

Owner: Platform Edge team. Status: in force.

## Purpose

This note describes how the public API gateway limits the request rate of each customer. It is the reference for engineers who change the gateway, for support staff who answer questions about rejected requests, and for the documentation team.

The limiter exists to protect the shared backend services from a single customer who sends far more traffic than planned, whether by mistake or by design.

## The token bucket

Each API key has its own token bucket. The bucket holds up to the plan's capacity of tokens and refills at the plan's rate as time passes. Tokens come back a little at a time rather than all at once at some fixed moment.

A request that finds at least one token in its key's bucket takes that token and goes through. A request that finds the bucket empty is rejected and takes nothing. A new key starts with a full bucket.

The state of each bucket, its token count and the time it was last updated, lives in the shared Redis cluster under the API key. Each entry expires once the bucket would have refilled to capacity, because a full bucket needs no stored state.

## What is counted

- Every request that reaches the gateway with a valid API key is counted against that key.
- Requests without a valid key are rejected by authentication before the limiter sees them.
- Health checks from the load balancer are exempt and never counted.

Some gateways charge failed requests and successful requests at different rates. Ours makes no such distinction, and a request costs one token whatever status the backend returns.

Many public APIs apply their limits per source IP address. This gateway does not key its buckets on the address a request comes from, because many customers send all their traffic through one corporate proxy.

## Plans

| Plan | Capacity (tokens) | Refill (tokens per second) |
|---|---|---|
| Free | 100 | 10 |
| Team | 500 | 50 |
| Enterprise | 2,000 | 200 |

The plan of a key is read from the account service at authentication and cached for five minutes. When the account service cannot be reached, a key gets the Free plan's capacity and refill until a lookup succeeds.

Capacity and refill are fixed by the plan. They are a property of the account, not something a client can raise for a single request by sending a header.

## Responses

When a key's bucket is empty, the gateway answers 429 Too Many Requests. Every response carries two headers:

- X-RateLimit-Limit, the capacity of the key's bucket.
- X-RateLimit-Remaining, the whole tokens left in the bucket after this request.

A rejected response also carries Retry-After, set to the seconds until the bucket holds one token again, rounded up. The gateway makes this decision on its own instead of forwarding the request and letting the backend judge whether it has room.

Support staff sometimes assume that a 429 response means the backend is overloaded. That reading does not hold for this gateway, where a 429 says only that the calling key has run out of tokens.

## Guidance for clients

Clients should watch X-RateLimit-Remaining and, once it reaches zero, wait for the seconds given in Retry-After before sending again. There is no need to watch for the quota window to roll over before resuming.

A client may send a burst up to its bucket's capacity at any time, and after that its steady rate is the plan's refill. Clients that run batch jobs can pace them at the refill rate, which keeps the bucket from running dry.

Retrying is the client's job. The gateway never holds a rejected request back to deliver it later on the client's behalf.

Client libraries published by the team already follow this guidance and need no configuration.

## Operations

- Refill is computed by a script that runs on the Redis server and reads the server's time.
- The Redis cluster is a hard dependency. If it is unreachable, the gateway rejects requests with 503 until it returns.
- Dashboards show, per plan, the share of keys that found their bucket empty at least once in each hour.
- An alert fires when more than five percent of Enterprise keys find their bucket empty for ten seconds in a row.

## Known limits

A client with a full bucket can send its whole capacity at once, so the backend can see a short burst above the plan's steady rate. We accept this because each plan's capacity is small next to what the backend can absorb.

An empty bucket starts to fill again at once. A client that empties its bucket early is not shut out for the remainder of any fixed period.

## Changing this note

Changes to the limits or to the headers are agreed with the documentation team, because the public docs quote them.

The Platform Edge team reviews this note every quarter.
