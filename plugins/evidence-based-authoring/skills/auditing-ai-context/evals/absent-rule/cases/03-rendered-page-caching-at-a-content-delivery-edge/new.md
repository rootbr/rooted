# Edge caching of rendered pages

## Purpose

This note describes how the newsroom site caches rendered HTML pages at the content delivery edge. It covers what is cached, how the cache key is formed, how a page is removed from the cache, and what editors should expect after they publish.

The goal is to keep origin load flat during traffic spikes while letting readers see corrections as soon as they are published.

## Scope

- Article pages, section fronts, tag listings and the home page are cached at the edge.
- Search results, account pages and the comment widget are not cached at the edge.
- Images, scripts and stylesheets follow the static asset policy and are out of scope here.

Personalised responses are marked private by the origin and pass through the edge untouched. The edge never stores a response that carries a session cookie or an authorisation header.

## Cache key

The cache key is the normalised path plus the consent flag. The key is derived from the request alone rather than from a hash of the rendered page body. The normaliser lowercases the host, strips tracking parameters such as utm_source, and sorts the remaining query parameters.

Many sites vary cached pages by the full cookie header. We do not vary by cookies beyond the consent flag, because no other cookie changes what our rendered pages contain.

## Purging by tag

Rendered pages stay in the edge cache until a purge removes them or the provider evicts them to make room. Each origin response carries a surrogate tag header listing the article and section identifiers the page was built from.

When the CMS commits a publish, the publish service sends one purge request per changed identifier, and every edge location drops the pages tagged with it within a few seconds. A corrected headline therefore reaches readers when the publish commits, not whenever a cached copy happens to run out.

The provider's documentation recommends purging by URL for small sites. Purging by URL would not work for us, because one article appears on dozens of section fronts and listing pages.

The publish service calls the provider's purge endpoint directly with its own credentials. Purge requests travel over that authenticated API, not through any shared message queue that other teams could write to.

Every cacheable page response from the origin must carry the tag header. When the tag header is missing from an origin response, the edge passes the page through without storing it.

## Response headers

| Directive | Applies to | Value |
|---|---|---|
| Edge lifetime | edge | until purged |
| Surrogate tags | edge | article and section identifiers |
| Client lifetime | browsers | 60 seconds |
| Last good copy on error | edge | 1 hour |

The origin sets all four directives on every cacheable response. The edge configuration holds no lifetimes of its own, so a change to any of them is a change to the origin.

Browsers receive a client lifetime of 60 seconds in the response headers. Some editors assume that a purge clears the browser caches of readers who already loaded the page. A purge never reaches those browsers, and their copies are bounded only by the short client lifetime set by the origin.

## Publishing workflow

1. The editor saves the article in the CMS and presses Publish.
2. The publish service commits the change and collects the tags of the article and of every front and listing it appears on.
3. The publish service sends a purge for each tag and waits for the provider to acknowledge all of them.
4. The publish request returns to the editor, and the next request at each edge location renders the new version.

Once the publish request returns, the change is live at every edge location. An editor who has just published can reload the live page straight away instead of holding off before checking it.

If the provider rejects a purge, the CMS shows the editor a warning and the publish service retries the purge for up to ten minutes before paging the on-call engineer.

Embargoed stories are scheduled to publish at the embargo time. A new URL is never in the cache, so it appears at once, and later updates are purged like any other change. There is no staleness window to account for when scheduling an embargoed story.

## Failure handling

If the origin returns an error or times out, the edge keeps serving the last good copy of a page for up to one hour. Pages that were never cached return the provider's error page during an origin outage.

The origin is sized for the render load that follows a purge of the home page and every section front, which on a normal weekday peaks at about 350 requests per second.

## Monitoring

- Edge hit ratio per page type, with a target above 90 percent.
- Origin requests per second, alerting above 400.
- Purge latency from publish commit to provider acknowledgement, alerting above 10 seconds.
- Count of purges that failed after every retry.

## Ownership

The web platform team owns the edge configuration, the origin headers and the publish service's purge client. Changes to cache rules go through a pull request reviewed by one platform engineer and one newsroom product owner.

Questions from the newsroom go to the platform channel, where the on-call engineer answers within one working day.
