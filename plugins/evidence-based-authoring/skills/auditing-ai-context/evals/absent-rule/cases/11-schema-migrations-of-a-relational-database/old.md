# Schema Migrations for the Orders Service

Owner: platform data team. This note applies to the orders PostgreSQL database and to every service that writes to it.

## Purpose

This note describes how the orders team changes the schema of its production database. It covers how migrations are written, reviewed, applied and verified, and who is responsible at each step.

## Tooling

- Migrations are plain SQL files kept in the db/migrations directory of the orders repository.
- Each file is named with a sequence number and a short description, for example V042__add_shipping_region.sql.
- Flyway applies the files in sequence order and records each one in the flyway_schema_history table.
- The same files run against a local container in every developer's test suite.

## Release rule

All schema changes for a release are collected into one release migration file and applied in the Sunday window, between 02:00 and 04:00 UTC. The release DBA applies that file by hand with Flyway while the orders application is stopped and a downtime banner is shown to customers. Application code that depends on the new schema is deployed in the same window, right after the migration succeeds.

## Writing a migration

- Developers add their statements to the release migration file on the release branch, not to a file of their own.
- Any statement is allowed, including renames, drops and type changes, because no running code reads the tables while the window is open.
- Data backfills go into the same file after the schema statements so that the release DBA can watch them finish.
- A statement that is expected to run longer than twenty minutes is flagged in the file header so the window can be planned.

## Review

Every change to the release migration file needs approval from one member of the platform data team. The reviewer checks the SQL for correctness, estimates its running time on a production-sized copy, and adds the estimate to the release checklist. The release DBA reads the whole file on the Friday before the window and may move statements to the next release if the window would overrun.

## Applying the migration

1. On Sunday at 02:00 UTC the release DBA enables the downtime banner and scales the orders application to zero.
2. The release DBA takes a snapshot of the database.
3. The release DBA runs Flyway against production and watches its output.
4. When Flyway reports success, the deploy pipeline releases the new application version.
5. The release DBA scales the application back up, removes the banner and posts a note in the release channel.

## When something fails

If Flyway stops with an error, the release DBA restores the snapshot taken in step 2 and redeploys the previous application version. The failed statements are fixed on the release branch and wait for the next Sunday window. Because the application is offline for the whole procedure, a failure costs only the time of the restore.

## Responsibilities

| Role | Responsibility |
|---|---|
| Developer | Adds statements to the release migration file and tests them locally |
| Reviewer | Approves the SQL and estimates its running time |
| Release DBA | Runs the Sunday window, applies the file and restores on failure |
| Support lead | Tells customers about the window in advance |
| On-call engineer | Handles alerts once the application is back up |

## Testing

Every migration runs in the test suite against an empty local database and against a copy of the staging database. The staging copy is refreshed every Thursday so that the release migration file can be rehearsed on realistic data before the window. A rehearsal that runs longer than the estimate on the release checklist is reported to the release DBA.

## Monitoring

After the window the release DBA compares the row counts of the changed tables with the snapshot and records them on the release checklist. Query latency dashboards are watched for one hour after the application comes back up. Any regression is reported in the release channel and handled by the on-call engineer.

## Open questions

- Whether the Sunday window should move to Saturday for customers in Asia.
- Whether the snapshot can be replaced by point-in-time recovery.
- Whether the staging copy should be refreshed more often than once a week.
