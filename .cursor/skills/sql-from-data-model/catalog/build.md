# Build the data model by hand

This file is part of `/sql-from-data-model`. It is used two ways:

- **Option B, by hand.** The user has no data model yet. Follow this whole file.
- **Option A, through dbvr.** `SKILL.md` runs the same scripts itself. It follows only `## Gates`, `## After each passing result`, and `## Write the data model` below.

Build a structural data model of a SQL Server database by handing the user **one catalog query per turn**, waiting for the result, then continuing. The queries are general: they read `sys.*` only and work on any SQL Server or Azure SQL database. They do not name application tables.

By hand, you do not run the SQL. The user runs it in DBeaver (or any SQL Server client) and pastes or attaches the grid.

This file **creates** the data model. Looking up rows is the rest of the skill. The data model file is not in this repo. Save it only at a path the user names outside this repository. If they name a path inside this repo, ask for a path outside it.

## Non-negotiable

1. **One query per message.** Paste exactly one script from [queries.md](queries.md). Then stop. Do not preview, summarize, or attach the next script.
2. **Copy the script verbatim.** Read `queries.md` and paste that step's SQL unchanged. Do not rewrite it, add filters, or generate a table-specific follow-up.
3. **Advance only after a usable result.** Interpret the grid in a few sentences, apply that step's gate, then either repeat the same step or give the next one.
4. **Read-only.** These scripts are `SELECT` against catalog views. Do not write `INSERT` / `UPDATE` / `DELETE` / `MERGE` / `TRUNCATE` / `ALTER` / `DROP` / `CREATE` / `EXEC`.
5. **Facts come from the grids.** When you write the data model, every table, column, type, key, and count must appear in a result the user returned this run. Do not fill gaps from memory, an older data-model file, or a previous chat.
6. **SQL Server and Azure SQL only.** If the user says the target is not SQL Server or Azure SQL, stop and say these scripts will not run there.
7. **One database at a time.** Finish Steps 1–7 and write that database's data model before starting Step 1 on the next database. Do not ask for another database's grid in the middle of a pass.

## Start of a run

Record, from what the user already said:

- The database or databases they will connect to. If they did not name one, ask once: which database connection should the first result come from?
- The output file, if they named one. If they did not, do not ask yet. Write the markdown in the reply at the end, and save a file only when a path is already known.

If a run is already in progress in this conversation, resume at the first step that does not yet have a usable result for the database currently in progress. Do not restart at Step 1.

When they name more than one database, take them in the order named. The current database is the one confirmed in this pass's Step 1. A grid whose `database_name` is a different database belongs to a later pass: do not mix it into this one. If a grid has no database label, treat it as the current database.

## How to hand over a query

Use this shape every time:

**Step N of 7 — [name]**

**Database:** the one database confirmed in this pass's Step 1

**What it answers**

**How to read the result**

**If the grid is empty or wrong:** what that means, and that they should resend this step rather than continue

Then one fenced `sql` block, copied from `queries.md`.

Tell them to export a large grid as CSV with headers instead of pasting it. Step 3 is the one that is usually too big to paste.

## Gates

Stay on the current step when a gate fails. Say what is wrong and paste that same script again.

| Step | Pass | Stay and repeat |
|---|---|---|
| 1 Identity | One row, and `database_name` is the database they meant | Empty, error, or `master` / any other database. Tell them to select the database in the connection and rerun. |
| 2 Tables | Header includes `schema_name`, `table_name`, `row_count` | Error, missing header, or a partial export. A header with **zero table rows** is a pass: the database has no user tables. |
| 3 Columns | Header includes `table_name`, `column_name`, `type_display`, `is_nullable`, and every table from Step 2 appears at least once | A table from Step 2 is missing, or they said the export was truncated. Ask for the full grid. |
| 4 Indexes | Header includes `table_name`, `index_name`, `is_primary_key`, `column_name` | Error or missing header. A table that appears in Step 2 and not here is a pass: it has no key and no indexes. Say so. |
| 5 Foreign keys | Header includes `parent_table`, `parent_column`, `referenced_table`, `referenced_column` | Error or missing header. Zero rows is a pass: no foreign keys. |
| 6 Check constraints | Header includes `table_name`, `constraint_name`, `definition` | Error or missing header. Zero rows is a pass: no check constraints. |
| 7 Other objects | Header includes `object_kind`, `object_name` | Error or missing header. Zero rows is a pass: no views, procedures, functions, or triggers. |

After a passing Step 2 with zero tables, skip Steps 3–6 (there is nothing for them to describe) and go to Step 7.

After a passing Step 7, write the data model. Do not add a profiling query.

## After each passing result

Two to four sentences, then the next step:

- Which database the grid belongs to
- The count that matters (tables, columns, keys, foreign keys, other objects)
- Anything the next step needs (for example, which tables have no indexes)

`row_count` is a catalog estimate from `sys.partitions`, not `COUNT(*)`. Call it an estimate in the data model.

## Write the data model

Write one section per database. Use the template below. Omit a section only when that step was skipped because Step 2 returned no tables; say it was skipped.

Group columns, indexes, and foreign keys under each table, in Step 2 order. Under each table state the primary key, unique constraints (including `filter_definition` when `has_filter` is 1), foreign keys, and check constraints. A table with no Step 4 rows is "no primary key and no indexes." A table with no Step 5 rows is "no foreign keys."

```markdown
---
title: "[database_name] Data Model"
date: [date from generated_utc]
source: [database_name] on [server_name]
note: Structural catalog from read-only sys.* scripts. Row counts are catalog estimates, not COUNT(*).
---

# [database_name] — Data Model

## Identity
[generated_utc, server_name, collation_name, compatibility_level]

## Table inventory ([N] tables)

| Schema | Table | Rows (estimate) | Created | Modified | Temporal |
|---|---|---|---|---|---|

## [schema].[table]

**Rows (estimate):** …
**Primary key:** …
**Unique:** …
**Foreign keys:** …
**Check constraints:** …
**Indexes:** …

| # | Column | Type | Nullable | Identity | Computed | Default |
|---|---|---|---|---|---|---|

## Other objects

| Kind | Schema | Name | Detail |
|---|---|---|---|
```

If they named an output path, save that file and then give the path. If the path is an existing data model, replace this database's structural catalog with this run. Drop tables that are not in the new inventory for this database. Do not keep columns, keys, or counts that this run did not return. Leave any other database's section as it was until that database has its own finished pass.

By hand, after the file is written, stop. If another database is still queued, start its Step 1 in the next message only. Do not start it in the same message as the write-up. When every database is done, save the path as `model_path` in `setup.json` if the user agrees, and go back to `manual.md` for their question.

Through dbvr, Option A goes straight on to the next database, as `SKILL.md` says.
