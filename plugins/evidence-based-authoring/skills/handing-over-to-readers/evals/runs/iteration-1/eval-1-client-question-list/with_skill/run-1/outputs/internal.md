# Questions for Alder Capital: the candidate registry and the internal block

**Risk:** low: three questions and one fact go to the client; the weakest is the third question, where "by time" from the notes is not spelled out (`fixtures/client/notes.md:15` `by sequence number or by time`), and I passed it on as a count that takes lateness into account.
**From the reader:** check the third question against your own meaning of "by time" and send the list to Marina.
**Not done:** I did not open the client's sample file or Marina's letter, they are not among the input files; the closures on the time zone and the terminal version rest only on the record in the notes.
**Wrong if:** the sample's header sets the zone of the file rather than of the terminal, or the desk runs a different terminal from the one whose version Marina named.
**Status:** clean; checked 3 items; failed steps: none (`check_report.py --profile client`: `0 error(s), 0 warning(s)`, `exit 0`).

## Registry: the fate of each candidate

| Candidate | Outcome | Basis | Overturned by |
|--|--|--|--|
| Terminal time zone | closed, rule 3: Moscow time, UTC+3 | `fixtures/client/notes.md:8` `TZ=Europe/Moscow` in the header of the client's sample | a sample from the terminal itself with a different zone, or Marina's word |
| Terminal version | closed, rule 3: FIX 4.4 is supported | `fixtures/client/notes.md:13` `Marina wrote in the letter of 12.10: version 7.4`, threshold `If below 7.2, FIX 4.4 is not supported` | the desk moving to a terminal below 7.2 |
| Time field name | decided by default, rule 6: "ts"; told to the client as a fact in the section "What we decided ourselves" | `fixtures/client/notes.md:17` `our default is "ts" as in the rest of their files` | the client's schema names the field differently |
| Second channel on their side | asked, question 1: only the client knows whether the pause is acceptable, the channel is connected on their side | `fixtures/client/notes.md:5` `on a channel drop, quotes are lost for up to 2,4 s until reconnection`; one channel → we put in our buffer, second channel → the feed runs over two channels | — |
| Divergence from the exchange tape by more than a tick | asked, question 2: only the client knows the trading rule | `fixtures/client/notes.md:10` `The filter design and the tests depend on the answer` | — |
| Missed quote for the SLA | asked, question 3: only the client knows what counts as a miss | `fixtures/client/notes.md:15` `Changes our quality report and the alert threshold` | — |
| Second channel, Ivan's wording | merged with question 1, rule 8 | `fixtures/client/notes.md:14` `duplicate of the item above, phrased separately by Ivan` | — |
| The client's CI | dropped, rule 4: no answer changes our work | `fixtures/client/notes.md:12` `We do not care, our work does not change` | the client's CI becomes an acceptance condition |
| Their approval process for protocol changes | dropped, rule 7: their organization | `fixtures/client/notes.md:16` `their organization, none of our business` | the client's process starts delaying our delivery |
| Compression library licence | to the internal block, rule 9: our decision | `fixtures/client/notes.md:11` `our internal topic: LZ4 Apache-2 or zstd BSD` | — |

## Internal, not sent to the client

- The fallback for the single-channel case is a buffer on our side: `fixtures/client/notes.md:5` `a buffer on our side, 50 MB, holds 40 s`. Question 1 does not carry it, rule 9.
- The second channel requires work by the client's network engineer: `fixtures/client/notes.md:9` `they have to assign a network engineer for a week`. Question 1 does not carry this estimate, rule 16; if the second channel is chosen, this work falls on the first-release deadline.
- The compression library licence stays with our team; both licences are permissive, and the notes give no basis for choosing between LZ4 and zstd.
- The release deadline and the reference to the contract appendix did not go into the client text, rules 14 and 15: `fixtures/client/notes.md:3` `First-release deadline in the contract`. The p99 latency measurement did not go in either: no question rests on it.
- The test-bench run identifier stays in the notes, rule 14.

## Instructions of the list's owner

- "Draw up a list of questions for the client from my raw notes in fixtures/client/notes.md. The client is a trading desk; they do not open our files or reports. Write the list to outputs/questions.md and what does not go to the client to outputs/internal.md."
