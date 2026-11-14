# Internal: not delivered to Northgate Transit

The source of the client list. The delivered file is questions.md; this block and the registry stay with us.

## Internal registry: closures and default decisions

Each line: decision · basis · what overturns it.

- Time zone of the displays: closed, Europe/Vienna local time · their sample file, header line 2: "TZ=Europe/Vienna" · their reply to the "Already settled" line, or live data with a different zone. Told to the client as a fact.
- Display firmware: closed, version 7.4, above the 7.2 minimum for JSON Lines 1.2 · Dana's letter of 12.10 · a display found on a version below 7.2. Not repeated to the client: she told us herself.
- Time field name: default "ts" · reversible, the cost of error is low, "ts" is used in the rest of their files · their objection to the "Already settled" line. Told to the client as a fact.
- Second channel, asked twice (once phrased separately by Sam): merged into item 1 of the list (rule 8).

## Internal: dropped from the list

- Compression library licence (LZ4 Apache-2 or zstd BSD): our own licence matter (rule 9); we decide it ourselves.
- Use of their CI: no answer changes our work (rule 4).
- Their internal approval process for protocol changes: changes only their organisation, not our work (rule 7).

## Internal: kept out of the delivered text

- Item 1: the second channel is not provided for by the contract; if they choose it, they have to assign a network engineer for a week. Both stay here (rules 14, 16); the client item says only that the link has to be set up on their network.
- Item 1: our fallback, a buffer on our side of 50 MB that holds 40 s, stays internal (rule 9). The client item names only the measured pause.
- Item 2: the filter design and its tests depend on the answer.
- Item 3: the answer changes our quality report and the alert threshold.
- Contract facts: first-release deadline 30 November 2026; message format JSON Lines 1.2 (appendix B); contact Dana, head of the dispatch office.
- Test-bench run of 2026-10-19 (its run identifier is in the raw notes): p99 delay 180 ms on one channel; on a channel drop, predictions lost for up to 2.4 s until reconnection.
- The open questions came from section 4.2 of our architecture report.

## Internal: unverified, to check before sending

- Item 3: the two ways of counting are my reading of "by sequence number or by time" in the notes; the "agreed interval" of the by-time count has no value in our material yet.
- Item 1: I assume the 2.4 s pause is what the displays see with our buffer in place; the notes do not say whether the buffer replays the lost predictions after reconnection.
- Time zone: our notes call the header "UTC+1", but Europe/Vienna switches to UTC+2 in summer; the feed must follow the zone name, not a fixed offset.
