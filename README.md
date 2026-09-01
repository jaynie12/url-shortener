Section B — Caching & Patterns
Exercises
B1  Cache-aside by hand
Implement lookup for 
short_code → long_url
 with the cache-aside pattern: check
Redis 
→
 on miss, read Postgres 
→
 write to Redis with a TTL 
→
 return.
Done when: a second lookup for the same code hits Redis (prove it with a log
line or Redis 
MONITOR 
).
Reflect on it: Walk through what happens on a cache miss vs hit. Why cache
aside rather than caching every row up front?
B2  TTL & eviction
Set a 60s TTL on cached codes. Observe expiry. Then configure Redis 
maxmemory
 small with an LRU policy and flood it — watch keys get evicted.
Done when: you can show a key expiring by TTL and a key evicted by
memory pressure — two different mechanisms.
Database & Caching
5
Reflect on it: TTL expiry vs LRU eviction — when does each fire? What TTL
would you pick for short-code lookups and why?
B3  Invalidation (the hard part)
Add "edit destination URL" and "delete URL" endpoints. Make the cache reflect
the change immediately (invalidate or update on write).
Done when: editing a url's destination and immediately hitting its short code
returns the new target, never stale.
Reflect on it: Why is "just cache everything" dangerous here? What's the
failure mode if you forget to invalidate on delete?
B4  Cache stampede
Make a cached key expire, then fire 100 concurrent requests for it. Observe
multiple DB hits at once (the stampede). Mitigate (lock / single-flight, or
jittered TTL.
Done when: under the same burst, DB hits for the missing key drop from 100
to 1.
Reflect on it: Why does a popular key expiring cause a spike? Name one
mitigation and its trade-off.
B5  Measure it
Benchmark the redirect endpoint with and without the cache (e.g. 
ab 
). Record p50/p95/p99 for both.
k6 
, wrk
, or 
Done when: you have a small before/after table of latency percentiles.
Reflect on it: Why report p95/p99 instead of the average? What did the cache
actually buy at p99?