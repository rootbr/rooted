# Questions about the MOEX quote feed into your terminal

How we build the feed for the first release on 30 November 2026 depends on the three answers below. For each question it is enough to answer with the option letter, for example "1 — A, 2 — B, 3 — A".

## 1. How to close the gap on a connection drop: a buffer on our side or a second channel on yours

When the connection between our server and your terminal drops, quotes stop arriving until reconnection. By our measurements reconnection takes up to 2,4 seconds.

- A. A buffer on our side. Our server keeps the last 40 seconds of the feed and after reconnection sends on the quotes that arrived during the drop. With a drop shorter than 40 seconds all quotes arrive, but the quotes from the time of the drop arrive up to 2,4 seconds late. With a drop longer than 40 seconds the quotes beyond this reserve are lost. No work is needed on your side.
- B. A second communication channel on your side. When one channel drops, the feed runs over the second. For this you need to assign a network engineer for about a week, and that week must fit before the release on 30 November. The current contract does not provide for a second channel.

Which option do you choose: A or B?

## 2. What to do with a quote that diverges from the exchange tape by more than 1 tick

A quote in our feed can differ from the MOEX exchange tape by more than one tick. We can treat such a quote in one of three ways:

- A. Skip. The quote does not reach the terminal, and the trader sees the previous price until the next quote.
- B. Mark. The quote arrives in the terminal with a divergence mark, and the trader decides how to use it. If you choose B, tell us whether your terminal shows such a mark to the trader.
- C. Stop the feed. On a divergence the feed stops, and the terminal receives no quotes until the feed is restarted.

Which option do you choose: A, B or C?

How we build and test the quote check on our side depends on the answer.

## 3. How to count a missed quote in the feed quality guarantees (SLA)

- A. By sequence number. Every quote carries a number, and a quote counts as missed when its number did not reach the terminal. A quote that arrived late does not count as missed.
- B. By time. A quote counts as missed when it did not reach the terminal within a set period. If you choose B, name this period.

The answer is linked to question 1. With the buffer (1 — A) the quotes from the time of a drop arrive up to 2,4 seconds late. When counting by number they do not count as missed, and when counting by time with a period shorter than 2,4 seconds every drop produces misses.

Our feed quality reports and the threshold at which the miss alert fires depend on the answer.

Which option do you choose: A or B?
