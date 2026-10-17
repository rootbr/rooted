# Quote feed: channel drop, divergence from the tape, count of misses

1. The feed reaches your terminal over a single communication channel. A drop of this channel interrupts the quotes for up to 2,4 seconds while the channel reconnects. A second channel on your side removes this pause. Whether such a pause is acceptable for your trading, only you know. Will one channel be enough for you, or do you need a second one?

2. A quote in the feed can diverge from the exchange tape by more than one tick. Skipping such a quote is right if the trader is better off not seeing a doubtful price while the rest of the feed is needed. Marking it is right if the trader wants to see such a price and decide himself. Stopping the whole feed is right if such a divergence means for you that the feed cannot be trusted. Which of the ways suits your trading, only you know. What to do with such a quote: skip it, mark it or stop the feed?

3. The quality guarantees of the feed (SLA) include a count of missed quotes. Every message of the feed carries a sequence number. If only the completeness of the feed matters, misses are counted by gaps in the numbers. If a late quote is as bad for you as a lost one, misses are counted by time. What counts as a miss, only you know. How to count a missed quote: by message numbers or by time?

## What we decided ourselves

The time field in the messages is called "ts", as in the rest of your files. If your schema calls it differently, we will rename it.
