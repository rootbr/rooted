# Pagination of list endpoints

Owner: API platform team. Applies to every public list endpoint under `/v2`.

## Purpose

This note fixes how clients walk through large collections such as orders, invoices and audit events. It is the reference for endpoint authors and for the teams that maintain the official SDKs. Any new list endpoint follows it unless the platform team grants an exception in writing.

## Request parameters

Every list endpoint is paginated by page number. A client sends `page_number`, starting at 1, and `page_size`, between 1 and 100. Every response carries the `X-Total-Count` header with the number of items in the whole filtered collection.

A request that omits `page_size` receives 25 items, and a request that omits `page_number` receives the first page. Filters and the sort order are passed as ordinary query parameters and must be repeated unchanged on every request of a traversal.

The server computes the offset as `(page_number - 1) * page_size` and skips that many rows of the sorted collection before reading the page.

## Response shape

| Field | Type | Meaning |
|---|---|---|
| `items` | array | The items of the requested page, in sort order |
| `page_number` | integer | The page the server returned |
| `page_size` | integer | The page size the server applied |

The `X-Total-Count` header is present on every successful response, including an empty one. The `page_size` field echoes the size the server applied, which may be lower than the one requested under load.

## Ordering and consistency

Each endpoint sorts by a stable key, by default creation time followed by item id. Endpoint authors may offer other sort keys, but every key must end with the item id so that the order is total.

An item created or deleted ahead of the current position during a traversal shifts every later item by one place. A client walking the pages may therefore see an item twice or miss one. Clients that need an exact copy deduplicate by item id and repeat the traversal when `X-Total-Count` changed between the first and the last page.

## Limits and errors

- A `page_size` above 100 or below 1 receives 400 Bad Request with the error code `invalid_page_size`.
- A `page_number` past the last page receives 200 with an empty `items` array and the usual `X-Total-Count` header.
- A `page_number` above 1000 receives 400 with the error code `page_too_deep`, because deep pages force a long scan.
- Filters that differ from those of the first request are not detected, and the client receives pages of a different collection.

## Client guidance

Clients may fetch several pages in parallel, since each page is addressed by its number alone. A user interface that offers numbered page links sends the chosen `page_number` directly.

Progress bars divide `X-Total-Count` by `page_size` to know how many requests a full traversal takes. Clients that only need the size of a collection request one item and read the header.

## Performance

A request for page n costs the database a scan of roughly n times the page size rows before it reaches the first returned item. Computing `X-Total-Count` costs one count query per request, cached for 30 seconds per filter combination.

Rate limits count requests, so a client that asks for 100 items per request uses its quota most efficiently. Endpoint authors keep an index that covers the default sort key and every filter they expose.

## SDK support

The official SDKs wrap traversal in an iterator that increments `page_number` until a page holds fewer items than `page_size`. The iterator retries a request once on a network error and then raises.

The SDKs also expose a `count()` helper that requests one item and returns `X-Total-Count`. The mobile SDK fetches up to four pages in parallel to fill a feed quickly.

## Open questions

- Whether the depth cap should be raised for export jobs. The data team has asked for 5000 pages.
- Whether `X-Total-Count` may be approximate for collections above a million items.
- Whether the count cache should be shortened for audit events, where freshness matters more.
