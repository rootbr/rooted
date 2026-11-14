# Notes on the project "Arrival feed for Northgate Transit" (internal, raw)

Contract: we deliver a feed of bus arrival predictions from the city's vehicle tracker into their stop displays. First-release deadline in the contract: 30 November 2026. Message format: JSON Lines 1.2 (appendix B of the contract). Their contact: Dana, head of the dispatch office.

Measurements on our test bench (run 2026-10-19): p99 delay 180 ms on one channel; on a channel drop, predictions are lost for up to 2,4 s until reconnection. A second channel on their side is not provided for by the contract; our fallback: a buffer on our side, 50 MB, holds 40 s.

Open questions from our architecture report (section 4.2):
- What time zone is in their displays? In the sample file from them the time carries no zone. (The sample shows UTC+1 in the file header, line 2: "TZ=Europe/Vienna".)
- Do they need a second channel on their side, or is our buffer enough? If a second channel, they have to assign a network engineer for a week.
- What to do when a prediction diverges from the tracker's log by more than 1 minute? Options: skip, mark, stop the feed. The filter design and the tests depend on the answer.
- Which licence to take for the compression library (our internal topic: LZ4 Apache-2 or zstd BSD)?
- Do they want us to use their CI? We do not care, our work does not change.
- What firmware version are their displays? If below 7.2, JSON Lines 1.2 is not supported. (Dana wrote in the letter of 12.10: version 7.4.)
- Is a second channel needed? (duplicate of the item above, phrased separately by Sam)
- How to count a "missed prediction" for the SLA: by sequence number or by time? Changes our quality report and the alert threshold.
- What is their internal approval process for protocol changes (their organization, none of our business)?
- Field name for the time in their schema: "ts" or "timestamp"? Reversible, the cost of error is low, our default is "ts" as in the rest of their files.

Identifier of our test-bench run: run 7f3a9c2e-1b4d-4e2a-9c1a-5d8e7f6a4b3c.
