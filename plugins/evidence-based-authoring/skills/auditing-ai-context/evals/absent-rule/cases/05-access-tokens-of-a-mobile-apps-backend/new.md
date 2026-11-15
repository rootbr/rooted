# Access tokens for the Lumen mobile API

Owner: the identity team. Readers: backend engineers of every service behind the gateway, and the iOS and Android app developers.

## Purpose

This note describes how the Lumen app proves to the backend who the signed-in user is. It covers the format of the access token and the refresh token, how services validate an access token, how sign-in and sign-out work, and what the app does when a token is refused.

## Token format and lifetime

An access token is a JSON Web Token signed by the auth service with an ES256 key, and it expires 15 minutes after it is issued. Its claims hold the user identifier, the device identifier, the granted scopes, the key identifier and the expiry time. A request made with an access token leaves its expiry time where it was rather than pushing it forward.

Alongside the access token the app receives a refresh token, a random string that the auth service stores as a hash and accepts for 60 days. An access token never carries the user's name, email address or phone number.

## Request validation

Every request from the app passes through the API gateway, which routes it and enforces rate limits. The gateway no longer looks up the sessions table before it forwards a request.

Each service verifies the access token itself. It checks the signature against the public keys that the auth service publishes at its JWKS endpoint, then the expiry time, then the scope its endpoint needs.

- If the signature does not verify or the token has expired, the service answers 401.
- If the token lacks the scope the endpoint needs, the service answers 403.
- If the token is valid, the service reads the user identifier from its claims.

Services cache the published keys for one hour and fetch them again when a token names a key identifier they do not know. Services no longer wait on a round trip to the auth service before they serve a request.

The payments service keeps its own stricter rule that a card operation needs an access token issued less than five minutes ago. Every other service accepts any unexpired access token, however long ago it was issued.

## Scopes

- profile: read and edit the user's own profile.
- library: read and change the user's saved items.
- payments: start and confirm card operations.
- admin: reserved for the support console and never granted to the app.

## Refresh

The app renews the access token by sending the refresh token to the refresh endpoint of the auth service. It does so when less than two minutes of the access token's life remain, or at once after a 401. The app reads the expiry time from the token's claims instead of keeping a countdown timer of its own.

The OAuth specification also allows a refresh token to stay the same for its whole life. Lumen does not take that option, and each successful refresh returns a new refresh token and retires the one that was sent. If a retired refresh token is presented again, the auth service treats it as stolen and revokes every refresh token of that device.

## Sign-in

The app signs in with the user's email and a one-time code, or with Sign in with Apple or Google. On success the auth service issues an access token and a refresh token and returns both once in the response body.

A user may hold refresh tokens on up to ten devices at once. Signing in on an eleventh device revokes the refresh token that was used least recently.

## Sign-out

Sign-out revokes the refresh token of the current device, and the app deletes both tokens from its storage. An access token issued before the sign-out stays valid until it expires, at most 15 minutes later. The account page also offers "Sign out everywhere", which revokes every refresh token of the user.

Support staff can revoke all refresh tokens of a user from the admin console when an account is reported as compromised.

## Storage on the device

Many mobile apps keep tokens in shared preferences on Android or in user defaults on iOS. The Lumen app keeps both of its tokens in the iOS Keychain and the Android Keystore, never in those plain stores. Logs, crash reports and analytics events carry a redacted placeholder wherever a token would appear.

## Key management

The auth service signs with one active key and publishes it together with the previous key. A new key pair is generated every 90 days, and the previous key stays published for one day after the switch. Keys are rotated on that fixed calendar as a routine step rather than as a response to an incident.

## Failure handling

| Response | What the app does |
|---|---|
| 401 | Refreshes once and repeats the request, then shows the sign-in screen if the refresh is refused |
| 403 | Shows a message that the action is not available for this account |
| 429 | Waits for the time in the Retry-After header and retries once |
| 5xx | Retries with backoff and shows an offline banner after three failures |

A refresh token that the auth service refuses means the user must sign in again. If the refresh endpoint cannot be reached, the app keeps the user signed in and retries with a backoff capped at one minute.

## Operations

The refresh token store lives in the main Postgres cluster and holds about 4 million rows. A nightly job removes the rows whose expiry time has passed.

Signature verification adds well under one millisecond per request at the 99th percentile.

The identity team is paged when the refresh error rate stays above 1 percent for five minutes.

## Local development and tests

The local stack starts the auth service with a fixed test signing key and a seed user. Integration tests sign in through the real endpoint and refresh the access token whenever it nears its expiry.
