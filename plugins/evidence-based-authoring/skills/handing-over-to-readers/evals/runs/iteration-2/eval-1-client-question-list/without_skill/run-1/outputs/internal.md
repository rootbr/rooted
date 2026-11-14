# Arrival feed for Northgate Transit: what stays internal

Source: fixtures/client/notes.md. Out of 10 items in the open-question list, 3 go to the client (questions.md). The rest are listed below with the reason each was held back.

## Before sending

- Set the reply-by date in questions.md (currently `[date]`). Today is 07.11 and the release is 30.11, so allow time for the filter work and tests that depend on answers 2 and 3.
- Question 1 says the buffer "covers" a reconnection. The 2.4 s gap is from the bench run of 2026-10-19 and the buffer is sized at 40 s, but I did not see a measurement of the buffer actually replaying across a drop. Confirm this before we promise "catch up".
- Question 1 rounds 2,4 s up to "about 2.5 seconds" for the client.

## Already answered, not asked

- Display firmware: Dana's letter of 12.10 says 7.4. That is at least 7.2, so JSON Lines 1.2 is supported. Nothing to ask.
- Time zone: the header of their sample file (line 2) says `TZ=Europe/Vienna`. Default: interpret unzoned times as Europe/Vienna. Correction to our note: Vienna is UTC+1 only in winter and UTC+2 in summer (DST). Handle it as a named zone, not a fixed +1 offset. The release date falls in winter time, so +1 only appears to be right until the end of March.

## Decided by default (reversible, cheap if wrong)

- Time field name: `ts`, as in the rest of their files. If their schema turns out to use `timestamp`, renaming is a small change.

## Ours to decide, not the client's

- Compression library licence (LZ4 Apache-2 vs zstd BSD): this is our internal choice and gets decided in the team.
- Their CI: it changes nothing for our work, so the question is dropped. Use it only if they offer.

## Not asked

- Their internal approval process for protocol changes: this belongs to their organisation and does not affect our delivery.
- "Is a second channel needed?" (Sam's item): a duplicate of the second-channel question, merged into question 1.

## Kept out of the client text

The client does not open our files, so the following were removed from questions.md: the reference to our architecture report section 4.2, the test-bench run id (run 7f3a9c2e-…), the p99 delay of 180 ms (not needed for any of their decisions), the contract appendix reference for the message format, and the library names.
