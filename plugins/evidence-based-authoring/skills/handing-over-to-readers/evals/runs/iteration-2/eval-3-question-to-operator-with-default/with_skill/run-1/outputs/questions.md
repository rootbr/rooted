The task is to move the limit settings from constants into a configuration file. Two open points came up before I continue. The first, where the file lives, I decided myself, because moving it later is cheap. The second is yours: the old limits table in the database. Deleting it would lose its history for good, so I need your answer before I write the migration.

## Where the file lives

The new file goes into the config folder. The three other configuration files of the project already live there. The resources folder holds only the logging setup. Moving the file later costs one path change and one commit. Tell me if you want it in resources, and I will move it.

## The old table

After the move, the code no longer reads the old limits table. The table still holds the limit history from 2019 to 2024. That is 14 000 rows. The test bench has no database backup. So a deleted table cannot be brought back. Only you know whether anyone still needs that history.

There are two ways.

```diff
  1. Keep the table
+ the history stays, and a later migration can still drop it
- an unread table stays in the schema; the migration gains one comment line

  2. Delete the table
+ the schema is clean
- the history is gone for good, with no backup to restore it
```

I would keep it. Keeping costs one line, and it leaves the choice open. If you choose to delete, I will repeat what is lost and wait for you to type the table name.

Keep the table or delete it?

## Where to look

- where the other configuration files live: `fixtures/question/context.md:5` `(3 files)`
- the rows and the missing backup: `fixtures/question/context.md:7` `14 000 rows`
