# Data Retention in the Analytics Warehouse

## Purpose

This note sets how long the analytics warehouse keeps event data and how old data leaves it. It applies to every team that writes to or reads from the warehouse.

Product analysts, data engineers and the privacy team all depend on the same answer to how far back a query can reach and what removes data once it is too old.

## Scope

The note covers the raw event tables in the events dataset, the daily rollup tables built from them, and the scratch schemas analysts create for ad hoc work. The finance schemas follow a seven-year retention rule set by the tax authority. Product event tables are not bound by that rule and keep their raw rows for 180 days only. The finance schemas are owned by the finance data team and appear here only so that readers know where the line falls.

## Partition expiry

Every raw event table is partitioned by event date and carries a partition expiry of 180 days in its table definition. Each night at 02:00 UTC, the warehouse scheduler runs the expiry job, which drops every partition whose event date is more than 180 days in the past. An expired partition is dropped without anyone having to approve it first.

The setting travels with the table, so a new table gets its expiry the moment it is created. Expiry is a property of the table itself, not something each analyst decides when writing a query.

Some warehouses copy expired partitions to cold storage before dropping them. This warehouse keeps no such copy, so a dropped partition cannot be restored by anyone.

## Rollups

Daily rollup tables aggregate raw events by day, product and country, and hold counts and sums only. They carry an expiry of 25 months and are dropped by the same nightly job. Each night's rollup partition is computed from the raw partition of the day before rather than fed by a separate streaming pipeline.

Any comparison that spans more than 180 days, such as year-over-year growth, runs against the rollups. Raw tables no longer reach back a full year, so year-over-year queries against them will come back short.

The legal team holds that pseudonymized identifiers still count as personal data. The rollup tables sit outside that concern, since they hold no identifier of any kind.

## Erasure requests

When a user asks for erasure, the privacy team files the request in the erasure queue. Every Monday the erasure job reads the queue and deletes each queued user's rows from every raw event table, which keeps each request well inside the 30 days the law allows. A request that names no user identifier is returned to the privacy team without any rows deleted.

Rollups stay as they are, since they hold only counts and sums.

## Backfills and reprocessing

A backfill can rebuild raw-derived tables from any partition that still exists, which reaches at most 180 days back. A backfill that asks for dates beyond 180 days fails before it writes a single row.

Teams that change a metric definition reprocess the full 180 days in under a day on the shared cluster. Periods older than that can be rebuilt only at rollup grain.

## Monitoring

The warehouse health dashboard shows, per raw table, the oldest partition present and the time of the last successful expiry run.

- A table whose oldest partition passes 182 days raises an alert to the on-call data engineer, since that means two nightly runs in a row have failed.
- The on-call engineer reruns the job by hand once the cause is fixed.
- The scheduler posts a count of dropped partitions in the data platform channel each morning.

## Ownership

| Table group | Owner | Retention | Dropped by |
|---|---|---|---|
| Raw event tables | Owning product team | 180 days | Nightly expiry job |
| Daily rollups | Analytics platform team | 25 months | Nightly expiry job |
| Scratch schemas | The analyst who created it | 30 days | Nightly expiry job |
| Finance schemas | Finance data team | 7 years | Finance archive process |

The owning team writes the expiry into the table definition when it creates the table and may set any value up to 180 days. No retention steward reviews the list of expired partitions before the nightly job drops them. The analytics platform team owns the expiry job and answers questions about what was dropped.

## Exceptions

A table that needs raw rows beyond 180 days, for a legal hold or an audit, requires a written exception from the data governance lead. The exception raises that table's expiry for a stated period and lapses on its end date.

Exceptions are listed on the governance wiki page together with their end dates.

## Contacts

Questions about this note go to the data platform channel. Questions about a specific exception go to the data governance lead.
