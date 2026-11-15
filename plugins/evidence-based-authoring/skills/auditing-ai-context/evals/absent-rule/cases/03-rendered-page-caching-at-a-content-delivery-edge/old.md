# Edge caching of rendered pages

## Purpose

This note describes how the newsroom site caches rendered HTML pages at the content delivery edge. It covers what is cached, how the cache key is formed, how long a page stays fresh, and what editors should expect after they publish.

The goal is to keep origin load flat during traffic spikes while letting readers see corrections within a predictable time.

## Scope

- Article pages, section fronts, tag listings and the home page are cached at the edge.
- Search results, account pages and the comment widget are not cached at the edge.
- Images, scripts and stylesheets follow the static asset policy and are out of scope here.

Personalised responses are marked private by the origin and pass through the edge untouched.

## Cache key

The cache key is the normalised path plus the consent flag. The normaliser lowercases the host, strips tracking parameters such as utm_source, and sorts the remaining query parameters.

Many sites vary cached pages by the full cookie header. Our pages read only the consent cookie, so the key carries that one flag and nothing else from the request headers.

## Freshness

Every rendered page is cached at the edge with a fixed 300-second TTL. The publishing system sends no purges to the edge, so a changed page reaches readers only when its cached copy expires at each edge location.

We call the period between a publish and the moment every edge location has refetched the page the staleness window. The staleness window never exceeds 300 seconds, and editors, support staff and the corrections desk all plan around that figure.

Browsers receive a client lifetime of 60 seconds in the response headers, which comes on top of the staleness window.

## Response headers

| Directive | Applies to | Value |
|---|---|---|
| Edge lifetime | edge | 300 seconds |
| Client lifetime | browsers | 60 seconds |
| Last good copy on error | edge | 1 hour |

The origin sets all three directives on every cacheable response. The edge configuration holds no lifetimes of its own, so a change to any of them is a change to the origin.

## Publishing workflow

1. The editor saves the article in the CMS and presses Publish.
2. The origin starts rendering the new version for any request that reaches it.
3. Each edge location keeps serving its cached copy until the 300-second TTL runs out there.
4. The next request at that location fetches the new version from the origin and caches it again.

Editors who need to check a correction wait out the staleness window before reloading the live page. The corrections desk adds five minutes to every promised correction time it gives to readers or to legal.

Embargoed stories are scheduled to publish at the embargo time. A new URL is never in the cache, so it appears at once, but any update made after it goes live is subject to the staleness window like any other change.

## Failure handling

If the origin returns an error or times out, the edge keeps serving the last good copy of a page for up to one hour. Pages that were never cached return the provider's error page during an origin outage.

The origin is sized for the refetch load that follows a full expiry cycle, which on a normal weekday peaks at about 350 requests per second.

## Monitoring

- Edge hit ratio per page type, with a target above 90 percent.
- Origin requests per second, alerting above 400.
- Count of pages served past their TTL during origin errors.
- Weekly report of corrections that readers flagged before the staleness window closed.

## Ownership

The web platform team owns the edge configuration and the origin headers. Changes to cache rules go through a pull request reviewed by one platform engineer and one newsroom product owner.

Questions from the newsroom go to the platform channel, where the on-call engineer answers within one working day.
