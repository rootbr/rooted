# Internal: what does not go to the client and what to check before sending

Three questions out of ten note items go to the client: the backup channel, the divergence from the exchange tape and the count of missed quotes. The other seven are closed by facts, duplicate question 1 or are decided without the client.

## What to check with the team before sending

The text for the client contains statements that the notes do not make directly. I derived them myself and did not check them with the team.

- Question 1, option A: the notes say only "buffer 50 MB holds 40 s". That the buffer sends on the quotes after reconnection and that the delay will be up to 2,4 seconds is my inference.
- Question 1, option B: the text says "the feed runs over the second channel". Whether the feed switches over without a pause, the notes do not say, so the text names no pause length.
- Question 1, option B: the contract does not provide for a second channel. Whether a supplementary agreement and an extra payment are needed if the client chooses B, we decide before sending.
- Question 2, option B: I added the sub-question "does the terminal show the mark". Without this mark in the terminal, option B is for the trader the same as option A.
- Question 2, option C: who restarts the feed after a stop, and how, the notes do not define. If we have a procedure, it should be written into the option.
- Question 3, option B: I read "by time" as "did not arrive within a set period" and added a request to name the period. If the team meant a different definition, the option has to be rewritten.
- The notes name no deadline for the answer. The network engineer's week for option 1 — B has to fit before 30 November, so the answer date should be written at the top of the list.

## Note items that do not go to the client

| Note item | Why it does not go | How we act |
|--|--|--|
| Terminal time zone | The answer is in their sample: line 2 of the header, `TZ=Europe/Moscow` | We read the time in their files as Moscow time, UTC+3 |
| Terminal version | Marina answered in the letter of 12.10: version 7.4, and FIX 4.4 needs version 7.2 or later | We work on FIX 4.4 |
| Second channel (Ivan's wording) | Duplicate of the second-channel item | Merged into question 1 |
| Compression library licence (LZ4 Apache-2 or zstd BSD) | Our internal choice | We decide ourselves |
| Their CI | Our work does not change with the answer | We work in our own CI |
| Their approval process for protocol changes | Their internal organization | We do not ask |
| Time field name: `ts` or `timestamp` | The decision is reversible, the cost of error is low | We take `ts`, as in the rest of their files |

## Data from the notes omitted from the text for the client

- p99 latency 180 µs on one channel: does not relate to the questions.
- The test-bench run of 2026-10-19 and its identifier `7f3a9c2e-1b4d-4e2a-9c1a-5d8e7f6a4b3c`: the client gets the figure 2,4 seconds as "by our measurements".
- Buffer size 50 MB: the client is given only the capacity of 40 seconds of feed.
- References to section 4.2 of the architecture report and to appendix B of the contract: the client does not open our files, so each question carries its context in its own text.
