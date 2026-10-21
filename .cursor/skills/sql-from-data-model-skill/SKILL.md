---
name: sql-from-data-model-skill
description: >-
  Answers plain-English questions about a SQL Server or Azure SQL database
  with read-only queries written from a data model. On invoke, shows Option A
  and Option B and waits before any lookup. Option A uses dbvr 26.2 or newer
  as the primary source, with the repos as a secondary source, builds the
  data model, then writes a read-only query and runs it. Option B writes SQL
  for the user to paste into DBeaver, and can build the data model by hand
  first. Use when the user invokes /sql-from-data-model-skill.
disable-model-invocation: true
---

# SQL from Data Model

`/sql-from-data-model-skill` is the only entry point. It shows the menu, then runs Option A or Option B.

This skill supports SQL Server and Azure SQL only.

Do not rewrite the catalog scripts in `catalog/queries.md`.

Paths are relative to this skill folder. Do not invent a home-directory path.

- Script: `scripts/sql_login.py`
- Example database list (placeholders only): `scripts/databases.example.json`
- Option B: `manual.md`
- Blank notes template: `notes.template.md`
- Catalog SQL: `catalog/queries.md`
- Catalog gates and template, and the by-hand build: `catalog/build.md`

Settings, the `.env` file, the data model path, and the saved-queries path come from `paths`. Do not guess Mac, Windows, or Linux folders. The data model and the saved-queries file stay outside this repo. The default is the `model_path` from `paths`.

## How to run the script

Try `python3`, then `py -3`, then `python`. Use the first one that runs.

Run `check`, `setup`, and `run` outside any sandbox, with network access. `setup` needs a person at the computer. Do not type a password into the chat.

```text
python3 scripts/sql_login.py paths
python3 scripts/sql_login.py check
python3 scripts/sql_login.py init-databases <file>
python3 scripts/sql_login.py setup
python3 scripts/sql_login.py setup --env <name>
python3 scripts/sql_login.py run <database> <sql-file>
python3 scripts/sql_login.py run <database> <sql-file> --csv <path>
python3 scripts/sql_login.py --dbvr-path <path> check
```

`--dbvr-path` works on every command. The script saves that path in `setup.json`.

`paths` prints `settings_dir`, `setup_json`, `databases_json`, `env_file`, `model_path`, `model_path_saved`, `queries_path`, `dbvr_workspace`, and `platform`. `queries_path` is the saved-queries file: the data model's folder, named `<data model name>.saved-queries.md`.

Do not print the `.env` file. Do not read DBeaver’s saved passwords. Do not drive the DBeaver app. Do not call `dbeaver` or `dbeaver-cli`. dbvr uses `dbvr_workspace` from `paths`, never a DBeaver data folder.

## How replies read

The person using this skill may not be technical. Every reply the user sees follows these rules.

- During setup, start each reply with one plain sentence saying what this step does and why.
- Use everyday words. Say “can be reached”, not “port 1433 answered”. Say “can read data” and “can't change data”, not reader or writer roles. Say “a private file on this computer”, not `.env`. Say “data model (a map of every table and column)” the first time it comes up.
- During setup, do not show script output, `OK`/`SKIP` lines, file paths of the settings folder, or the commands you ran. Show setup results as short tables with ✅.
- During setup, keep it short. End with the one thing the user replies next, in bold.
- An answer uses this order:
  1. **Answer:** one short sentence. Every name, number, date, ID, and status in it must appear exactly in the table. No rounding. No new numbers: no totals, averages, or percentages. If one is needed, write a query that returns it. No facts that are not in the table.
  2. The script's table, pasted exactly: the header, the separator, and every row. Do not rename headers. Do not reorder or drop rows or columns. Do not reformat values. Keep `8,292` as `8,292`. Keep dates as printed. Keep blanks blank.
  3. `<n> rows returned.` The number is the script's `ROWS` line.
  4. Column notes. Explain a column or value only when the data model or the user's notes file documents it. Otherwise write `Meaning not documented.` or skip that column. Never explain a column from general knowledge.
  5. Which database it came from, in words (for example, “From the <Environment> <Label> database.”).
  6. The query, folded under “The query it ran”. SQL appears only there. When a saved query was used, the title is “The query it ran (saved query)”.
- When `ROWS` is 0, the answer sentence is `**Answer:** No rows came back for <the values searched>.` Do not guess why. If the data model or the user's notes file documents a likely reason, you may add one sentence quoting it.
- More than 50 rows: the CSV path in **Answer a question** stays. The summary may state only the row count and values that appear in the printed output.
- Before sending, compare every value in the answer sentence and the column notes against the script output. Remove or fix anything that does not match exactly.
- If the script prints `NOTE a value contains "|", so this table may display wrong`, include that note under the row count. Do not rebuild the table.

## Menu

If this same message says Option A or Option B, skip the menu and use that option. Match that phrase without case sensitivity. If it names both, ask for one option and stop.

Otherwise, on invoke, before any lookup, send the menu below as the whole reply, then stop.

Do not read a data model, the notes file, `catalog/queries.md`, or a repo. Do not run `scripts/sql_login.py`. Do not open `setup.json` or the `.env` file. Do not write SQL.

After the menu, accept `A`, `B`, `Option A`, or `Option B`. Then continue. If the reply names both, ask for one and stop.

Send this:

The skill answers questions about your data. There are two ways to use it:

**A: Automatic**
You ask a question in plain English. The skill writes the database query, runs it, and shows you the answer here in the chat.
*You need:* dbvr 26.2 or newer (a free database tool, Mac or Windows) and access to the databases. The first time, a short setup signs you in.

**B: Manual**
The skill writes the database query. You copy it into DBeaver, run it yourself, and paste the result back.
*You need:* DBeaver, connected to the database. If you don't have a data model file yet, the skill helps you build one first.

Reply **A** or **B**.

## Option B — manual

Read and follow `manual.md` in full. Column notes, when the user has them, come from `notes_path` in `setup.json`. The blank template is `notes.template.md`. Do not treat the template as the user's notes. Option A reads the notes file only to explain a column or a value. Option A does not use it to pick a table or write the query. If the notes and the data model disagree, the data model wins. If `notes_path` is empty or the file is missing, write `Meaning not documented.` unless the data model documents the column.

If they picked B and have not said what to find, ask what they want to find and stop. If they already said what to find, follow `manual.md` now. Do not run Option A.

## Option A — start

On Option A, run `paths`, then read `setup.json` at the `setup_json` path. Do not open the `.env` file.

Setup is finished when `source` is `dbvr` or `repos`, `model_path_saved` is `yes`, and that model file exists. For `dbvr`, `databases.json` and the `.env` file also have to exist. `notes_path` is optional. An empty `notes_path` still counts as finished. If setup is finished, go to **Answer a question**. Otherwise continue with **First-time setup**.

If they later say to change databases or passwords, run `setup` again. If they say “Refresh the data model”, rerun **Build the data model** for the database they name, or for every database if they do not name one, then mark that database's saved queries `Needs check: yes` (see **Saved queries**). If they say “Clear saved queries”, delete the file at `queries_path` and say in one sentence that the saved queries are cleared. Do not ask for a password in the chat.

If the user pastes a password or a connection string into the chat, do not store it, do not repeat it, and do not write it into a file. They enter passwords only in the sign-in windows.

`setup.json` may hold `source` (`dbvr` or `repos`), `dbvr_path`, `model_path`, `repo_links`, `notes_path`, and `read_access_confirmed`. `repo_links` is an object of `{"<label>": "<link>"}`. `notes_path` is a string and may be `""`. Nothing else.

## First-time setup

Resume at the first unfinished step. Do not repeat a step that already succeeded.

### 1. Prerequisite check

Run `check`. No questions.

- `OK` lines can stay in your notes. Do not read them aloud when the rest of setup continues.
- `SKIP databases`, `SKIP ports`, and `SKIP credentials` are expected before databases and sign-in exist.
- If the script prints `STOP dbvr not found`, ask once in the chat for the dbvr path. That path is not a secret. If they give it, run the same command with `--dbvr-path`. If they say they will use the repos, go to the repo section below and do not ask again. If they do neither, give them `https://github.com/dbeaver/dbvr/releases/latest` and stop.
- Any other `STOP` line: tell the user that message and stop.

`check` does not log in and does not open a window.

### 2. Data model source

If `source` is already `dbvr` or `repos`, keep it. If this reply already says 1, 2, dbvr, or repos, use that. Otherwise send this and stop:

> **First-time setup.** The skill needs to learn your databases’ tables and columns, and how to reach them.
>
> **1. Connect with dbvr** (recommended). One sign-in covers all your databases, and answers come back here in the chat.
> **2. Read the code repos instead.** Only if you can't use dbvr. The skill writes queries from the code, but can't run them.
>
> Reply **1** or **2**.

A reply of 1 or dbvr selects dbvr. A reply of 2 or repos selects the repo section. Write `source` into `setup.json` when that step’s other fields are ready. Never put a username, password, or connection string in `setup.json`.

### 3. Which databases

Skip this step when `source` is `repos`.

There is no default list. If `databases.json` does not exist yet, send this and stop:

> **Which databases should it connect to?** For each database, send the environment, a short label, the server, the database name, and the port. The port is 1433 if you leave it out.
>
> For example: Dev, App, sql-dev.example.com, app_db, 1433.
>
> Or send the path to a JSON file in the same shape as the example list.

When they describe databases in the chat, write a temporary JSON file in the shape of `scripts/databases.example.json`. No passwords in that file. Run `init-databases <file>`, then delete the temp file.

When they give a path to a JSON file, run `init-databases <that file>`. Do not delete their file.

### 4. Port check

Run `check` again. `SKIP credentials` is still expected. If a server does not answer, the script names it. Tell the user in plain words which database can't be reached and to check the VPN or network, then stop.

If `check` printed `OK credentials`, the saved login is already complete. Report the check below, without the sign-in sentence, and continue to **Build the data model**.

Otherwise send this, with one row per `OK port` line (environment and label from `databases.json`) and the version from the `OK dbvr` line, then stop:

> Before asking for any password, the skill checked that the database tool is installed and that every database can be reached.
>
> ✅ dbvr `<version>` installed
>
> | Environment | Database | Reachable |
> |---|---|---|
> | Dev | App | ✅ |
>
> **Next: sign in.** A window opens for each environment, one after the other. Paste your username and password for each database. Passwords are hidden and never appear in this chat.
>
> Reply **go** when ready.

### 5. Sign-in windows

If the latest `check` printed `OK credentials`, skip this step and the login check below. The saved `.env` is already complete. A shared `SQL_USER` still counts when `SQL_USER_<KEY>` is absent. Do not open a window.

Otherwise, on `go`, send one line first: “Opening the sign-in windows now. Check your screen.” Then run `setup`. It waits while the person fills in the windows; allow up to 10 minutes. One window per environment, in the order of `databases.json`. Each window is titled “Sign in to <environment>” and says which step it is. Each database in that environment has its own username field and password field. Usernames are prefilled. Every field is required. Cancel saves nothing.

Do not ask for a password until the script has printed `OK prerequisites`.

### 6. Login check

This runs inside `setup`. Any login that signs in passes. The script still asks each database for the login's roles, only to report them: each database prints `OK <database>: read-only` or `OK <database>: can change data`.

When the script prints `SAVED`, report it like this, one row per database, then continue to **Build the data model** in the same reply. **Can change data** is `Yes` for a `can change data` line and `No` for a `read-only` line:

> The skill signed in to each database and checked whether the login can change data.
>
> | Database | Signed in | Can change data |
> |---|---|---|
> | Dev, App | ✅ | No |
>
> Your passwords are saved only on this computer, in a private file. They never appear in the chat. Each person who uses the skill signs in with their own login.

If any row is `Yes`, add this one sentence under the table, exactly: “That login can change data, but the skill only runs queries that read data.”

This checks the login's database roles. A permission given to the login some other way is not covered. Mention that in one plain sentence only if the user asks how the check works.

On `FAILED` or `STOP`, say in plain words which database had a problem and the likely fix (see **Failures**). Say that nothing was saved and any earlier login still works. End with “Reply **retry** to open the windows again.” A failed login or cancel saves nothing and leaves an older `.env` file unchanged.

### 7. Save

When the script prints `SAVED`, it wrote the `.env` file. If sign-in was skipped because `check` already printed `OK credentials`, there is no new `.env` write. Either way, update `setup.json` with `"source": "dbvr"` and the `dbvr_path` from the script’s `OK dbvr` line. Keep any `repo_links`, `notes_path`, and `model_path` already there. Do not put secrets in `setup.json`. Leave `notes_path` as `""` when the user has no notes file.

To change one environment later, run `setup --env <name>`. That opens only that environment’s window, keeps the other environments’ saved values, signs in to that environment, and saves the merged file only if that sign-in works.

### 8. Build the data model

If `model_path_saved` is `no`, ask where the model file should live, then stop:

> **Last step: the data model.** That's a map of every table and column. The skill uses it to write correct queries. Where should it be saved?
>
> Reply **default** to save it in the skill's settings folder, or paste a file path.

The default is the `model_path` from `paths`. The user can name another path outside this skill’s repo. Save the chosen path as `model_path` in `setup.json`. Do not save the data model inside this repo.

If that file already exists, send this and stop:

> **Last step: the data model.** That's a map of every table and column. The skill uses it to write correct queries. One already exists.
>
> Reply **use** to use it, or **rebuild** to build a fresh one from the databases (a few minutes per database).

Use it only if they say to use it. Rebuild if they say to rebuild, or if the file does not exist.

On dbvr, build every database in `databases.json`. Go one database at a time and finish all seven steps before the next one. Show progress, such as “Dev App: step 3 of 7”.

For each step, copy that step’s SQL from `catalog/queries.md` exactly into a temp file. The steps are the seven headings in that file, from Step 1 through Step 7. Run `run <database> <file>`, then delete the file. Do not rewrite the SQL. Do not edit `catalog/queries.md`.

Follow `## Gates`, `## After each passing result`, and `## Write the data model` in `catalog/build.md`. Use that template. Replace only that database’s section. Every table, column, type, key, and count in the section must appear in a result from this run. Do not invent one. Do not hand the catalog SQL to the user. Do not ask them to paste a grid back.

On the repo source, build the sections from migrations and entity models instead. Row counts are `unknown (repos do not contain rows)`. Each repo updates the data-model sections for databases with that label. `database_name` comes from the Identity block already in that section. If the section does not exist, ask for the `database_name`. Do not invent one.

Do not write the model file into this skill’s repo.

### 9. Done

If Step 1 returned `can_view_definitions` = 0 for any database, start this reply with this sentence, exactly, then name those databases in words: “This login cannot view definitions, so check-constraint rules, column defaults and some procedures and functions are not shown. Ask the DBA for VIEW DEFINITION (read-only) for a complete model.” Leave it out when every database returned 1.

Send this and stop:

> ✅ **Setup is done.** From now on, just ask a question in plain English. For example: *How many orders does customer C-1001 have?* If they already asked a question in this same conversation, answer it with **Answer a question** instead of stopping.

Do not ask for a notes file during setup. `notes_path` stays `""` unless the user already gave one. The blank template is `notes.template.md`. Setup is finished without it.

### From the repos (secondary)

Use this only if dbvr is not available, or they chose 2.

Ask only for these, then stop until you have them:

- One repo link for each database label they listed. The same label in more than one environment shares one link. `repo_links` stores `{"<label>": "<link>"}`.
- Read access to those repos

Do not ask for dbvr or passwords during this setup. Do not run `setup` or `run`.

When every label has a link and they have read access, save `source` as `repos`, the links under `repo_links`, and `read_access_confirmed` true. Leave `notes_path` as `""` unless they already gave a notes file.

Read migrations and entity models only. Do not open `.env`, user secrets, or connection strings. If a secret appears, do not copy it, repeat it, or save it.

Do not push, commit, or modify the repos. If a repo is already on disk, read that checkout. If it is not, clone it so you can read those files, and do not push.

Then do **Build the data model** from the repos, then the done line.

The code does not contain table rows. This choice does not run the query. On a later question, write the script and tell them the result comes back only after a dbvr connection is added.

Put values directly in the query, for example `WHERE CustomerId = N'C-1001'`. If a value contains an apostrophe, write it twice, for example `N'O''Brien'`. Do not use `DECLARE` or `@variables`. dbvr runs each statement separately, so a declared variable is lost (SQL Error 137, verified 2026-10-16).

## Answer a question

Setup is already done.

1. Run `check`. No questions and no windows. If every line is `OK`, do not show the check. If any line is `SKIP`, setup is not finished: return to the unfinished setup step. If the script stops, use **Failures**.
2. The user asks in plain language. If this message does not ask a question, ask what they want to find and stop.
3. Before reading the data model, look in the saved queries at `queries_path` (see **Saved queries → Use a saved query**). If one entry matches, use its filled-in SQL, its database, and its column notes, and go to step 7. If the file does not exist, nothing matches, or you are unsure, continue with step 4.
4. Read the model at `model_path`. Find the tables and columns there. Pick the database by which tables are involved. For the environment, use the one the user named. If they did not name one and more than one environment has those tables, ask which environment and stop.
5. On the repo source, write the query and stop. Do not run it. `SELECT` and `WITH` only. Put values directly in the query, for example `WHERE CustomerId = N'C-1001'`. If a value contains an apostrophe, write it twice, for example `N'O''Brien'`. Do not use `DECLARE` or `@variables`. dbvr runs each statement separately, so a declared variable is lost (SQL Error 137, verified 2026-10-16).
6. On dbvr, the query goes with the answer, folded under “The query it ran” (step 8). `SELECT` and `WITH` only. Put values directly in the query, for example `WHERE CustomerId = N'C-1001'`. If a value contains an apostrophe, write it twice, for example `N'O''Brien'`. Do not use `DECLARE` or `@variables`. dbvr runs each statement separately, so a declared variable is lost (SQL Error 137, verified 2026-10-16). One database. One result set. No cross-database join. Do not invent a table or a column. If the model does not have the field, say so.
7. Write the query to a temp file, run `run`, and delete the file.
8. Results. The script prints the table, then `ROWS <n>` on its own line. If a value contains `|`, it also prints `NOTE a value contains "|", so this table may display wrong`. Include that note under the row count. Do not rebuild the table.
   - 50 rows or fewer: reply in this order.
     1. **Answer:** one short sentence. Every name, number, date, ID, and status in it must appear exactly in the table. No rounding. No new numbers: no totals, averages, or percentages. If one is needed, write a query that returns it. No facts that are not in the table.
     2. The script's table, pasted exactly: the header, the separator, and every row. Do not rename headers. Do not reorder or drop rows or columns. Do not reformat values. Keep `8,292` as `8,292`. Keep dates as printed. Keep blanks blank.
     3. `<n> rows returned.` The number is the script's `ROWS` line.
     4. Column notes. Explain a column or value only when the data model or the user's notes file documents it. Otherwise write `Meaning not documented.` or skip that column. Never explain a column from general knowledge. Option A may read the notes file only for this. Do not use it to pick a table or write the query. If it disagrees with the data model, the data model wins. If `notes_path` is empty or the file is missing, there are no notes. When a saved query was used, use that entry's stored column notes.
     5. Which database it came from, in words (for example, “From the <Environment> <Label> database.”).
     6. `<details><summary>The query it ran</summary>` … the query in a `sql` block … `</details>`. When a saved query was used, the summary is `The query it ran (saved query)`. Nothing else in the answer changes.
   - When `ROWS` is 0, the answer sentence is `**Answer:** No rows came back for <the values searched>.` Do not guess why. If the data model or the user's notes file documents a likely reason, you may add one sentence quoting it.
   - Before sending, compare every value in the answer sentence and the column notes against the script output. Remove or fix anything that does not match exactly.
   - More than 50 rows: run the same query again with `--csv`. Save it in the user’s Downloads folder as `<database>-<short-topic>-<YYYY-MM-DD>.csv` unless the user names a path. The summary may state only the row count and values that appear in the printed output. Include the file path and the folded query.
   - If they ask to change or delete data, don't write or run anything. Say that the skill only runs queries that read data, so it doesn't run anything that changes data.
9. If the query was new (not a saved query) and `run` finished without `STOP`, save it (see **Saved queries → Save a new query**). Do not ask and do not mention it.
10. Follow-up questions in the same chat repeat from step 3. Do not run `check` again.

`run` reads the temp file and sends it with `-in=<file>` and `-l=100000`. Both were verified on Mac on 2026-10-16. `run` does not check the login's roles. The query filter checks the SQL before dbvr starts. The role check in `setup` is one trailing `SELECT`.

## Saved queries

The saved-queries file is at `queries_path` from `paths`: the data model's folder, named `<data model name>.saved-queries.md`. It stays outside this skill's repo, like the data model. Do not write it into this repo. It is used only by Option A.

**Never store returned data or the user's real values.** No row values, no counts from a result, and no ID, name, date, or other value the user typed. Those become `{placeholders}`.

### Entry format

The file starts with `# Saved queries`. Each entry is one `##` section:

````markdown
## <the question in general words, for example: How many orders does customer {customer_id} have?>

- Database: `<database_name from the data model's Identity block>`
- Tables: `dbo.Customer`, `dbo.[Order]`
- Placeholders:
  - `{customer_id}`: `dbo.Customer.CustomerId`, `nvarchar(20)`, text
- Column notes:
  - `ColumnName`: <the note given in the answer, or `Meaning not documented.`>
- Saved: <YYYY-MM-DD>
- Needs check: no

```sql
SELECT COUNT(*) AS OrderCount FROM dbo.[Order] WHERE CustomerId = N'{customer_id}';
```
````

Each placeholder lists its column, its type from the data model's `type_display`, and `text` or `number`. A text placeholder sits inside quotes in the SQL (`N'{customer_id}'`). A number placeholder sits bare (`= {order_id}`).

### Use a saved query

1. If the file does not exist, nothing matches.
2. An entry matches only when all of these hold: the same database, the same tables, the same kind of answer, and only the values differ. The database follows the environment rule in **Answer a question** step 4: use the environment the user named; if they named none and more than one environment has those tables, ask which environment and stop.
3. If more than one entry could match, or you are unsure, write a new query as usual.
4. If the entry says `Needs check: yes`, first check every table and column it uses (Tables, Placeholders, and the SQL) against that database's section of the current data model. If all are there, change it to `Needs check: no` and use it. If any is missing, delete the entry and write a new query.
5. Fill in each `{placeholder}` with the user's value. For a text placeholder, write any apostrophe in the value twice (`O'Brien` becomes `O''Brien`). A number placeholder takes digits only; if the value has anything else, do not use the entry and write a new query.
6. Run it as in **Answer a question** step 7. Use the entry's column notes. The folded query's summary says `The query it ran (saved query)`.

### Save a new query

After a new query runs without `STOP`, add an entry at the end of the file. Create the file with its `# Saved queries` heading if it does not exist. Do not ask and do not mention it.

- Do not save when a saved query was used, when an entry for the same kind of question already exists, on the repo source (nothing runs), or for the data model build's catalog scripts.
- Write the question in general words, with each user value replaced by a `{placeholder}`.
- In the SQL, replace each value the user gave with its `{placeholder}`. Keep the quotes around text placeholders.
- Copy the column notes from the answer. Leave out anything that quotes a value from the result.
- `Saved:` is today's date. `Needs check: no`.

### Keeping it right

- If the user says an answer was wrong, remove the entry that answer used or saved.
- After “Refresh the data model”, set `Needs check: yes` on every entry for each database that was rebuilt. They are checked the next time they could match.
- “Clear saved queries” deletes the file at `queries_path`.

The password is one item in a Python subprocess argument list, never a shell string, and never echoed. Before anything is printed, saved values are replaced with `[hidden]`. Command-line arguments can be seen by other processes on the same machine while dbvr runs. dbvr has no verified way to read the password from an environment variable. Do not invent one.

Driver `microsoft`. SQL username and password, not Azure AD. No SSL or trust-certificate flags. Do not pass `--stateless`. The first run downloads the SQL Server driver into `dbvr_workspace`.

## Failures

- **Wrong username or password:** run `setup --env <that environment>` so only that window opens, then retry the query. The environment name is the one in `databases.json` for that database.
- **Firewall** (“blocking your IP address”): tell the user to ask the database admin to allow their IP, then run setup again. Do not keep retrying.
- **dbvr missing:** tell the user to reinstall it, or ask once for the path and pass `--dbvr-path`.
- **A server did not answer:** tell them to check the VPN or network.

## Read-only

The query filter keeps Option A read-only whichever login you use; a read-only login is still the safest choice. Allowed SQL is `SELECT` and `WITH` only. Every statement must start with `SELECT` or `WITH`. The only `SET` lines allowed are `SET NOCOUNT ON/OFF` and `SET TRANSACTION ISOLATION LEVEL READ UNCOMMITTED`, which the catalog scripts use. Put values directly in the query, for example `WHERE CustomerId = N'C-1001'`. If a value contains an apostrophe, write it twice, for example `N'O''Brien'`. Do not use `DECLARE` or `@variables`. dbvr runs each statement separately, so a declared variable is lost (SQL Error 137, verified 2026-10-16). The script stops on `DECLARE` with that reason. It also blocks `INTO`, so `SELECT … INTO` is refused, and `NEXT VALUE FOR`, which advances a sequence. A statement that is only a bracketed or double-quoted name, such as `[usp_Purge]`, is refused, because SQL Server runs a lone name at the start of a batch as a stored procedure. The catalog scripts’ `SET` lines are allowed because those scripts are copied unchanged. `@@` functions such as `@@SERVERNAME` are allowed.

- Repos: read migrations and entity models. Do not push, commit, or modify those repos. Do not run the query. Write the same literal-value queries as the dbvr source.
- Database: catalog scripts from `catalog/queries.md` go through `run` unchanged. A question the skill writes is `SELECT` and `WITH` only. `run` checks every query with the filter before dbvr starts. It does not check the login's roles.
- One database per script. No cross-database joins.
- Do not invent tables or columns.

## Known limits

`DECLARE` does not work. dbvr runs each statement separately, so a variable declared in one statement is missing in the next (SQL Error 137, verified 2026-10-16). Put the value directly in the query. If a value contains an apostrophe, write it twice, for example `N'O''Brien'`. The script refuses `DECLARE`.

A login without `VIEW DEFINITION` still sees every table and column, but SQL Server hides some metadata from it without an error. Step 1 reports this as `can_view_definitions`. When it is 0, the data model carries this line under Identity: “This login cannot view definitions, so check-constraint rules, column defaults and some procedures and functions are not shown. Ask the DBA for VIEW DEFINITION (read-only) for a complete model.” An empty check definition, or a default that exists but is hidden, is written as `not visible to this login`. A column with no default stays blank. An empty index filter definition is written as `filter definition not returned`. Do not guess them. A column whose user-defined alias type is hidden is listed with its built-in base type.

Building the data model through dbvr was verified on 2026-10-19: all seven catalog scripts ran unchanged through `run`, with `--csv`, on four Azure SQL databases. Also verified on 2026-10-21 on SQL Server 2022 on Windows, with a `db_datareader` login without `VIEW DEFINITION`: 109 of 109 columns.

On Windows, dbvr's bundled Java writes the printed table in the Windows code page, so a character outside it, such as an emoji, came back as `?` (verified with dbvr 26.2.3). Setting `JAVA_TOOL_OPTIONS=-Dstdout.encoding=UTF-8` fixed it; `-Dfile.encoding=UTF-8` did not. The script sets that option for dbvr on Windows only, and keeps any `JAVA_TOOL_OPTIONS` already set. The CSV from `--csv` was always UTF-8.

## Not verified

Say this when you use these parts.

- Whether `SET NOCOUNT ON` and `SET TRANSACTION ISOLATION LEVEL READ UNCOMMITTED` carry over to the next statement. They are harmless either way. Leave the catalog scripts unchanged.
- dbvr’s Windows install paths. The Windows test used `--dbvr-path`.
- The Linux sign-in window.
- The new sign-in window has one username and one password per database. The Mac window mechanism was verified on 2026-10-15 with a shorter field list. Windows was verified on 2026-10-21 with one database.
- The “can change data” report covers database roles only, not permissions granted directly to the login.
- Answers from a fresh agent session in Cursor or Claude Code.
