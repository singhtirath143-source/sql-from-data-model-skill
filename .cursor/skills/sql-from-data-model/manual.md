# Option B — manual

This is Option B of `/sql-from-data-model`. `SKILL.md` sends the user here when they pick B. Paths in this file are relative to the skill folder.

The user gives a **scenario** (who or what they need to find or verify). You write **read-only SQL** they can paste into DBeaver. You do not run SQL against the database.

Option B **reads** a data model. If the user does not have one yet, build it by hand first with [catalog/build.md](catalog/build.md): the user runs 7 catalog scripts in DBeaver and pastes each result back. Then come back here.

The model can be any file in the shape `catalog/build.md` writes: one section per database, an Identity block, a table inventory, and per-table keys, foreign keys, checks, indexes, and columns. Option A writes the same shape. The SQL is general. The table names come from the file in front of you.

## Non-negotiable

1. **Read the data model before writing SQL.** Every table, column, type, key, and foreign key in the script must appear in that file for the database you name. Do not invent names from memory, an older chat, or another database's section.
2. **Read-only only.** `SELECT` / `WITH` / `DECLARE` for filters. No `INSERT` / `UPDATE` / `DELETE` / `MERGE` / `TRUNCATE` / `ALTER` / `DROP` / `CREATE` / `EXEC` of user data.
3. **Name the database** above every script, using `database_name` from that section's Identity block. Wrong database is the most common failure.
4. **One database per script.** Do not join across databases, even when two catalogs live in the same file.
5. **DBeaver-safe scripts.** One result set per script. Do not chain `@sql` / `sp_executesql` across batches. Prefer several short scripts over one mega-script.
6. **If the model does not have the field, say so.** Do not guess a column. Offer a documented column that is actually in the model, or stop. A `sys.columns` probe is only for a column the user says exists and the model does not list.
7. **SQL Server and Azure SQL only.** These scripts target SQL Server or Azure SQL, the same engines the catalog scripts describe. If the user says the target is not SQL Server or Azure SQL, stop.

## Which data model

1. If the user names a file, or attaches one, that file is the model.
2. If they do not, run `paths` on `scripts/sql_login.py`. Use `model_path` when `model_path_saved` is `yes` and that file exists.
3. If `model_path` is not saved, or the file is missing, ask which data-model file to use, or whether to build one by hand with `catalog/build.md`. Do not guess a path.

Try `python3`, then `py -3`, then `python`.

A file may contain more than one database. Use only the section whose Identity `database_name` matches the database in the script.

Column notes are optional. `notes_path` in `setup.json` starts empty and is not required. When it is non-empty and that file exists, you may use it for column meanings, status values, and join rules the user wrote for that database. [notes.template.md](notes.template.md) is only a blank template. Do not treat it as the user's notes.

If `notes_path` is empty, or the file is missing, meanings come only from the data model. When a column or value is not documented there, write `Meaning not documented.`

If the notes and the data model disagree, the data model wins. Do not apply notes from one database's section to another database.

## Workflow

### 1. Restate the scenario

In one or two sentences: what they want to find, which identifiers they already have, and which `database_name` you will query. If the file has more than one database and the scenario does not say which, pick the section that actually contains the tables you need and say why.

Ask only if you cannot write a useful first query without a missing identifier. Prefer a query that discovers the identifier over a clarifying question.

### 2. Map scenario → tables

Open the data model. For each needed fact, write down:

| Fact | Schema | Table | Column(s) | Database |
|---|---|---|---|---|
| … | … | … | … | `database_name` |

Join on a foreign key the model documents. If there is no foreign key, join only when both columns are in the model and you say the join is inferred from matching names. A join rule in the user's notes file may explain a join that the model already allows. Do not invent a key. If the notes and the data model disagree, the data model wins.

### 3. Write the queries

Default template (every script):

```sql
SET NOCOUNT ON;
SET TRANSACTION ISOLATION LEVEL READ UNCOMMITTED;

DECLARE @Id NVARCHAR(50) = N'…'; /* only if needed; match the column type in the model */

SELECT …
FROM schema.TableName
WHERE …;
```

Rules:

- Use the schema from the inventory. Put it on every table.
- Bracket reserved names (`dbo.[Order]`).
- Declare variables with a type taken from that column's `type_display`. Use `NVARCHAR` for national string types and `VARCHAR` for the others.
- Filter with `DECLARE` when the user gave an id. Do not hardcode a value they will reuse. A literal in the query looks like `WHERE CustomerId = N'C-1001'`.
- If a value contains an apostrophe, write it twice, in a `DECLARE` value or a literal, for example `N'O''Brien'`.
- Filter out stale rows only when that column is in this table's column list (`DeletedAt`, `RemovedAt`, `ValidTo`, or a status column the model actually has). Do not add those filters because another database has them.
- Split: (1) confirm the entity exists, (2) the lookup, (3) a fallback only if (2) can be empty and the model has another table that could answer it.
- Label each script with a one-line comment of what it answers and which database.

### 4. Deliver

For each script, state:

- **Database:** full `database_name` from Identity
- **What it answers**
- **How to read the result** (which column is the value they asked for)
- **What empty means** and the next script if empty

Do not wrap the SQL in a file unless the user asks. They paste into DBeaver.

When they paste results, interpret them against the same table map. Quote a column meaning only when the data model or the user's notes file documents it. Otherwise write `Meaning not documented.` Offer the next query only if the scenario is still unanswered.

## Words that are not columns

A word in the scenario ("role", "owner", "active", "manager") is a column only when the model has that column, or a column the model names for that idea. If the model has several candidates, say which one you used. If it has none, say the model does not record that fact. The user's notes may say which documented column matches the word. If the notes and the data model disagree, the data model wins.
