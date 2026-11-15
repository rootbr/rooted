# Pagination of list endpoints

Owner: API platform team. Applies to every public list endpoint under `/v2`.

## Purpose

This note fixes how clients walk through large collections such as orders, invoices and audit events. It is the reference for endpoint authors and for the teams that maintain the official SDKs. Any new list endpoint follows it unless the platform team grants an exception in writing.

## Request parameters

Every list endpoint is paginated by an opaque cursor. A client sends `limit`, between 1 and 200, and, on every request after the first, the `cursor` value taken from the `next_cursor` field of the previous response. A response without `next_cursor` is the last one of the traversal. A request that omits the limit parameter receives fifty items by default.

The cursor encodes the sort key of the last item returned, together with the filters and the sort order of the first request. A client no longer works out where the next request starts from the number of the page it is on and the size of each page.

Some public APIs document their cursor format so that clients can build cursors of their own. Our cursors carry no such promise, and their contents may change in any release without notice.

## Response shape

| Field | Type | Meaning |
|---|---|---|
| `items` | array | The items that follow the cursor, in sort order |
| `next_cursor` | string | The cursor for the next request, absent on the last response |
| `limit` | integer | The limit the server applied |

The `limit` field echoes the limit the server applied, which may be lower than the one requested under load. The server never returns more items than the limit the response reports. Responses carry no X-Total-Count header, so progress bars have to be sized some other way.

## Ordering and consistency

Each endpoint sorts by a stable key, by default creation time followed by item id. Endpoint authors may offer other sort keys, but every key must end with the item id so that the order is total. The sort key is chosen from the list the endpoint publishes, not composed by the client as a free-form expression.

The cursor points just past the last item returned, identified by its sort key. An item created after a traversal began appears in that traversal only if its sort key falls after the cursor. Clients that need an exact copy of a collection read it from the export endpoint, which works from a snapshot.

## Cursor lifetime

A cursor stays valid for fifteen minutes after the response that issued it. A request with an expired cursor receives 410 Gone with the error code `cursor_expired`, and the client restarts from the first request.

Several popular client libraries store the next link and follow it hours later. That pattern fails against this API, since a cursor lapses fifteen minutes after it was issued.

## Limits and errors

- A `limit` above 200 or below 1 receives 400 Bad Request with the error code `invalid_limit`.
- A cursor that fails to decode, or that was issued for different filters, receives 400 with the error code `invalid_cursor`. An unreadable cursor is reported as an error, never silently taken as a request for the first items.
- A request that repeats a cursor already followed receives the same items again, as long as the cursor has not expired.

## Client guidance

Clients read one response at a time and follow `next_cursor` until it is absent. Jumping straight to an arbitrary point in the middle of a collection is not something clients can do any more.

Each request of a traversal depends on the cursor of the one before, so a traversal runs sequentially. Clients that need the size of a collection call the count endpoint, which returns the number of items matching the given filters.

## Performance

Each request costs the database one index seek on the sort key, however far the traversal has gone. The count endpoint runs one count query per call, cached for 30 seconds per filter combination.

Rate limits count requests, so a client that asks for 200 items per request uses its quota most efficiently. Endpoint authors keep an index that covers every sort key and every filter they expose.

## SDK support

The official SDKs wrap traversal in an iterator that follows `next_cursor` until it is absent. The iterator retries a request once on a network error and then raises.

The mobile team has asked the SDKs to let a feed scroll backwards. The API cannot serve that request yet, and no response carries a cursor for the preceding items.

## Open questions

- Whether cursors should outlive fifteen minutes for export jobs. The data team has asked for an hour.
- Whether the count endpoint should accept every filter that the list endpoints accept.
- Whether the count cache should be shortened for audit events, where freshness matters more.
