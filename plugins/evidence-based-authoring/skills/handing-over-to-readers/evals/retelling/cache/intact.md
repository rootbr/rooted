# How a thumbnail finds its cache entry

The gallery shows a small copy of every picture, a thumbnail. Drawing one takes about a second, so the gallery keeps drawn thumbnails in a cache. This page explains how a thumbnail is stored and found, so that a picture uploaded again never shows its old thumbnail. The mechanism is five steps and one counter.

## The whole mechanism

The mechanism keeps one number for every picture, the count of its uploads, called the version. It takes in two events: an upload of a picture and a request for its thumbnail.

Every upload of a picture raises its version by one. The cache key joins the picture's number and its version. A request asks the cache for the entry under the newest key. When the cache has no entry under that key, the gallery draws the thumbnail and stores it under the key. An entry leaves the cache one day after it was stored.

```
on upload(picture):   picture.version = picture.version + 1
key(picture)        = picture.number + ":v" + picture.version
on request(picture):  entry = cache.get(key(picture))
if entry is missing:  entry = draw(picture); cache.put(key(picture), entry)
every entry:          leaves the cache one day after cache.put
```

After a second upload the key changes, so the old entry is never read again and leaves after its day.
