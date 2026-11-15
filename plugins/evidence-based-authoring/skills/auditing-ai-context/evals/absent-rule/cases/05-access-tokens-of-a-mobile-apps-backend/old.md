# Access tokens for the Lumen mobile API

Owner: the identity team. Readers: backend engineers of every service behind the gateway, and the iOS and Android app developers.

## Purpose

This note describes how the Lumen app proves to the backend who the signed-in user is. It covers the format of the access token, how the gateway validates it, how sign-in and sign-out work, and what the app does when a token is refused.

## Token format and lifetime

An access token is an opaque string of 32 random bytes, encoded in base64url, that carries no meaning of its own. The auth service stores a SHA-256 hash of each token as one row of the sessions table, together with the user identifier, the device identifier, the granted scopes and an expiry time. A token stays valid for 30 days after its last use, because every accepted request moves its expiry forward by 30 days.

The app therefore never has to renew a token while the user keeps opening it at least once a month.

## Request validation

Every request from the app reaches the API gateway first. The gateway hashes the bearer token and looks the hash up in the sessions table.

- If no row matches, the gateway answers 401 and the request goes no further.
- If the row has expired, the gateway deletes it and answers 401.
- If the row is valid, the gateway moves its expiry time forward and adds the user identifier and the scopes as the X-Lumen-User and X-Lumen-Scopes headers.

Services behind the gateway trust these two headers and never see the token itself. Each service checks that the scopes in X-Lumen-Scopes include the scope its endpoint needs and answers 403 otherwise.

The gateway keeps a 10-second in-memory cache of recent lookups, so that a burst of requests from one screen costs a single database read.

## Scopes

- profile: read and edit the user's own profile.
- library: read and change the user's saved items.
- payments: start and confirm card operations.
- admin: reserved for the support console and never granted to the app.

## Sign-in

The app signs in with the user's email and a one-time code, or with Sign in with Apple or Google. On success the auth service creates a token, writes its row into the sessions table and returns the token once in the response body.

A user may hold up to ten sessions at once, one per device. Signing in on an eleventh device deletes the session that was used least recently.

## Sign-out

Sign-out deletes the row of the current token from the sessions table, and the token stops working as soon as the gateway cache entry expires. The account page also offers "Sign out everywhere", which deletes every row of the user.

Support staff can end all sessions of a user from the admin console when an account is reported as compromised.

## Storage on the device

The app keeps the token in the iOS Keychain or the Android Keystore. Logs, crash reports and analytics events carry a redacted placeholder wherever a token would appear.

## Failure handling

| Response | What the app does |
|---|---|
| 401 | Deletes the stored token and shows the sign-in screen |
| 403 | Shows a message that the action is not available for this account |
| 429 | Waits for the time in the Retry-After header and retries once |
| 5xx | Retries with backoff and shows an offline banner after three failures |

A 401 always means the session is gone, so the app does not retry the request.

## Operations

The sessions table lives in the main Postgres cluster and holds about 4 million rows. A nightly job removes the rows whose expiry time has passed.

Gateway latency is dominated by the lookup, which adds about 3 ms at the median and 20 ms at the 99th percentile.

The identity team is paged when the lookup error rate stays above 1 percent for five minutes.

## Local development and tests

The local stack starts the auth service with an empty sessions table and a seed user. Integration tests sign in through the real endpoint and reuse the returned token for the whole suite.
