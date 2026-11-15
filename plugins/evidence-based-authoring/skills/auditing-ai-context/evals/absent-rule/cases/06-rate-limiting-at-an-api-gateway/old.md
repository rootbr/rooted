# Gateway Rate Limiting

Owner: Platform Edge team. Status: in force.

## Purpose

This note describes how the public API gateway limits the request rate of each customer. It is the reference for engineers who change the gateway, for support staff who answer questions about rejected requests, and for the documentation team.

The limiter exists to protect the shared backend services from a single customer who sends far more traffic than planned, whether by mistake or by design.

## The quota window

Each API key may send at most 600 requests in one quota window. A quota window is one clock minute, starting at second zero of the minute in UTC. When a new quota window begins, the counter of every key returns to zero.

The counter for each key lives in the shared Redis cluster under a name made of the API key and the start minute of the quota window. Each counter expires two minutes after it was created, so old quota windows clean themselves up.

A request that arrives while its key's counter is below the plan's limit increments the counter and goes through. A request that arrives once the counter has reached the limit is rejected and does not increment it.

## What is counted

- Every request that reaches the gateway with a valid API key is counted against that key.
- Requests without a valid key are rejected by authentication before the limiter sees them.
- Health checks from the load balancer are exempt and never counted.
- A request counts as one, whatever status the backend returns.

## Plans

| Plan | Requests per quota window |
|---|---|
| Free | 600 |
| Team | 3,000 |
| Enterprise | 12,000 |

The plan of a key is read from the account service at authentication and cached for five minutes.

A change of plan takes effect at the next quota window after the cache entry expires.

## Responses

When a key has used up its quota window, the gateway answers 429 Too Many Requests until the next quota window starts. Every response carries three headers:

- X-RateLimit-Limit, the number of requests the plan allows per quota window.
- X-RateLimit-Remaining, the requests still left in the current quota window.
- X-RateLimit-Reset, the Unix time at which the current quota window ends.

A rejected response also carries Retry-After, set to the seconds left until the quota window ends.

## Guidance for clients

Clients should read X-RateLimit-Reset and pause until that moment once X-RateLimit-Remaining reaches zero.

Clients that run batch jobs are advised to spread their work evenly across the minute. A batch that starts at second zero can use the whole quota window in a few seconds and then sit idle for the rest of it.

Client libraries published by the team already follow this guidance and need no configuration.

## Operations

- All gateway nodes must keep their clocks synchronised by NTP, because each node computes the start minute of the quota window from its own clock.
- The Redis cluster is a hard dependency. If it is unreachable, the gateway rejects requests with 503 until it returns.
- Dashboards show, per plan, the share of keys that reached their limit in each quota window.
- An alert fires when more than five percent of Enterprise keys reach their limit in three quota windows in a row.

## Known limits

A client can send its whole allowance in the last second of one quota window and the same again in the first second of the next. The backend can then see twice the plan's rate for a short time.

We accept this because the burst is bounded by the plan and lasts no more than two seconds.

## Changing this note

Changes to the limits or to the headers are agreed with the documentation team, because the public docs quote them.

The Platform Edge team reviews this note every quarter.
