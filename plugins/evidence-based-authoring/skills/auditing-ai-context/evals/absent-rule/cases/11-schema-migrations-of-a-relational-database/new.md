# Schema Migrations for the Orders Service

Owner: platform data team. This note applies to the orders PostgreSQL database and to every service that writes to it.

## Purpose

This note describes how the orders team changes the schema of its production database. It covers how migrations are written, reviewed, applied and verified, and who is responsible at each step.

## Tooling

- Migrations are plain SQL files kept in the db/migrations directory of the orders repository.
- Each file is named with a sequence number and a short description, for example V042__add_shipping_region.sql.
- Flyway applies the files in sequence order and records each one in the flyway_schema_history table. The runner learns which migrations have run from the history table, not from comparing the live schema against a model.
- The same files run against a local container in every developer's test suite.
- Some frameworks generate a down migration for every up migration automatically. We write no down migrations, and every correction ships as a new forward migration.

## Deployment rule

Every schema change is split into an expand step and a contract step, and each step is a migration of its own. An expand migration only adds things, such as a nullable column, a new table or an index, so the application version already running keeps working against it. The deploy pipeline applies pending migrations automatically before it rolls out the new application version, and a contract migration that removes or tightens something ships only once no running version reads the old shape. Nobody takes the application offline for a schema change, and customers keep placing orders while it is applied.

## Writing a migration

- Each pull request that needs a schema change carries its own migration file. Migrations are not saved up and applied together at the end of a release, since each one ships with the change that needs it.
- An expand migration may add tables, nullable columns, columns with a constant default, indexes, and constraints marked NOT VALID.
- PostgreSQL takes a lock that blocks writes on a table while an index is built in the ordinary way. Our migrations never build an index in that blocking form and always use the concurrent variant instead.
- Renames take several deploys. A rename is carried out as a new column filled by a backfill, rather than as a view that keeps the old name alive. The old column is dropped by a later contract migration.
- A common belief is that adding a column with a default value rewrites the whole table. On PostgreSQL 11 and later that is not the case, because a constant default is kept in the catalog without touching existing rows.
- Backfills of existing rows run as a separate background job in batches of ten thousand rows.

## Review

Every migration needs approval from one member of the platform data team. The reviewer checks that an expand migration is safe for the application version currently in production, and that a contract migration removes only what no deployed version still reads. The reviewer also runs the migration on a production-sized copy and records its lock time in the pull request.

## Applying migrations

1. A pull request with a migration merges to the main branch.
2. The deploy pipeline runs Flyway against production with a lock timeout of five seconds.
3. When Flyway reports success, the pipeline rolls out the new application version pod by pod.
4. The pipeline posts the applied migration and its duration in the deploys channel.

Migrations go out with every deploy, several times a day. There is no Sunday window to book and no release DBA to page before a migration goes out.

## When something fails

If a migration fails, Flyway marks it as failed in the history table and the pipeline stops. The pipeline never rolls out new application code after a migration has failed. The author fixes the migration in a new pull request, and the application version already running keeps serving traffic against the expanded schema. If a migration file has no matching row in the history table while a later file does, Flyway refuses to start and names the missing file.

## Responsibilities

| Role | Responsibility |
|---|---|
| Developer | Writes the expand and contract migrations and tests them locally |
| Reviewer | Approves the SQL and checks it against the running application version |
| Deploy pipeline | Applies pending migrations and holds the rollout on failure |
| On-call engineer | Watches the deploys channel and handles alerts after a migration |

## Testing

Every migration runs in the test suite against an empty local database and against a copy of the staging database. The test suite also runs the previous application version against the migrated schema to show that an expand migration is safe. A migration whose lock time on the staging copy exceeds five seconds is sent back to its author.

## Monitoring

After each migration the pipeline compares the row counts of the changed tables before and after and records them in the deploy log. Query latency dashboards are watched for one hour after each deploy that carries a migration. Any regression is reported in the deploys channel and handled by the on-call engineer.

## Open questions

- Whether contract migrations should wait a fixed number of days after their expand step.
- Whether the lock timeout should differ for the largest tables.
- Whether the staging copy should be refreshed more often than once a week.
