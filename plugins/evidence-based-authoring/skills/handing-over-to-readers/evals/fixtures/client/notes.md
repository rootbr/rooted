# Notes on the project "Quote feed for Alder Capital" (internal, raw)

Contract: we deliver a quote feed from the MOEX exchange into their trading terminal. First-release deadline in the contract: 30 November 2026. Message format: FIX 4.4 (appendix B of the contract). Their contact: Marina, head of the trading desk.

Measurements on our test bench (run 2026-10-19): p99 latency 180 µs on one channel; on a channel drop, quotes are lost for up to 2,4 s until reconnection. A second channel on their side is not provided for by the contract; our fallback: a buffer on our side, 50 MB, holds 40 s.

Open questions from our architecture report (section 4.2):
- What time zone is in their terminal? In the sample file from them the time carries no zone. (The sample shows UTC+3 in the file header, line 2: "TZ=Europe/Moscow".)
- Do they need a second channel on their side, or is our buffer enough? If a second channel, they have to assign a network engineer for a week.
- What to do when a quote diverges from the exchange tape by more than 1 tick? Options: skip, mark, stop the feed. The filter design and the tests depend on the answer.
- Which licence to take for the compression library (our internal topic: LZ4 Apache-2 or zstd BSD)?
- Do they want us to use their CI? We do not care, our work does not change.
- What version is their terminal? If below 7.2, FIX 4.4 is not supported. (Marina wrote in the letter of 12.10: version 7.4.)
- Is a second channel needed? (duplicate of the item above, phrased separately by Ivan)
- How to count a "missed quote" for the SLA: by sequence number or by time? Changes our quality report and the alert threshold.
- What is their internal approval process for protocol changes (their organization, none of our business)?
- Field name for the time in their schema: "ts" or "timestamp"? Reversible, the cost of error is low, our default is "ts" as in the rest of their files.

Identifier of our test-bench run: run 7f3a9c2e-1b4d-4e2a-9c1a-5d8e7f6a4b3c.
