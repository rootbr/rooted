# Data Retention in the Analytics Warehouse

## Purpose

This note sets how long the analytics warehouse keeps event data and how old data leaves it. It applies to every team that writes to or reads from the warehouse.

Product analysts, data engineers and the privacy team all depend on the same answer to how far back a query can reach and who removes data once it is too old.

## Scope

The note covers the raw event tables in the events dataset, the daily rollup tables built from them, and the scratch schemas analysts create for ad hoc work. The finance schemas follow a seven-year retention rule set by the tax authority. The finance schemas are owned by the finance data team and appear here only so that readers know where the line falls.

## The 400-day window

Every raw event table keeps 400 days of data, counted from the event date of each partition. On the first Sunday of each month, the retention steward opens a purge ticket that lists every partition older than 400 days. The owner of each table approves its part of the ticket, and the steward then runs the monthly purge against the approved partitions.

The 400 days give analysts a full year of history plus a month of margin for late corrections.

## Rollups

Daily rollup tables aggregate raw events by day, product and country, and hold counts and sums only. They are kept for 25 months and removed by the same monthly purge.

Because raw tables hold more than a year, a year-over-year query can run straight against raw events at full detail. Rollups serve dashboards that need a longer view or faster answers.

The legal team holds that pseudonymized identifiers still count as personal data. Raw event tables therefore fall under the erasure process described below.

## Erasure requests

When a user asks for erasure, the privacy team files the request in the erasure queue. The retention steward adds each queued user to the next purge ticket, and the monthly purge deletes that user's rows from every raw event table. The law gives us 30 days, and a monthly cycle stays inside that limit as long as the purge runs on schedule.

Rollups stay as they are, since they hold only counts and sums.

## Backfills and reprocessing

A backfill can rebuild raw-derived tables from any partition inside the 400-day window. Teams that change a metric definition usually reprocess the full window, which takes about two days on the shared cluster.

Periods older than 400 days can be rebuilt only at rollup grain.

## Monitoring

The warehouse health dashboard shows, per raw table, the oldest partition present and the number of partitions waiting on the next purge ticket.

- A table whose oldest partition passes 430 days raises an alert to the retention steward.
- A purge ticket left unapproved for a week is escalated to the table owner's manager.
- The steward posts a summary of each monthly purge in the data platform channel.

## Ownership

| Table group | Owner | Retention | Removed by |
|---|---|---|---|
| Raw event tables | Owning product team | 400 days | Monthly purge |
| Daily rollups | Analytics platform team | 25 months | Monthly purge |
| Scratch schemas | The analyst who created it | 30 days | Monthly purge |
| Finance schemas | Finance data team | 7 years | Finance archive process |

The retention steward is a rotating role held for one quarter by a data engineer from the platform team. The steward keeps the purge calendar and answers questions about what was removed.

## Exceptions

A table that needs raw rows beyond 400 days, for a legal hold or an audit, requires a written exception from the data governance lead. The steward leaves the excepted partitions off every purge ticket until the exception lapses.

Exceptions are listed on the governance wiki page together with their end dates.

## Contacts

Questions about this note go to the data platform channel. Questions about a specific exception go to the data governance lead.
