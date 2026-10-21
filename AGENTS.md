# SQL from a data model

This file is the procedure for Codex, Copilot, and any other agent. Cursor and Claude Code use the same procedure from `.cursor/skills/sql-from-data-model-skill/SKILL.md`. If that skill file is available, follow it. The steps below are enough on their own.

This repo is one skill. It supports SQL Server and Azure SQL only. The dbvr driver is `microsoft`. Logins are SQL username and password, not Azure AD.

Do not rewrite the catalog scripts. Do not commit. Do not install dbvr. Do not push or modify a product repo.

## Files

Everything is in `.cursor/skills/sql-from-data-model-skill/`.

| What | Where |
|---|---|
| Main procedure (menu and Option A) | `SKILL.md` |
| Option B (manual) | `manual.md` |
| Blank notes template | `notes.template.md` |
| Catalog SQL | `catalog/queries.md` |
| Catalog gates and template, and the by-hand build | `catalog/build.md`. Option A uses only the sections `## Gates`, `## After each passing result`, and `## Write the data model` |
| Script | `scripts/sql_login.py` |
| Example database list | `scripts/databases.example.json` |

Settings live outside this repo. Run `paths` and use the paths it prints. Do not guess a home folder. Keep the data model outside this repo and do not commit it. The default is the `model_path` from `paths`. `paths` also prints `queries_path`, the saved-queries file: the data model's folder, named `<data model name>.saved-queries.md`. It also stays outside this repo.

Try `python3`, then `py -3`, then `python`.

```text
python3 .cursor/skills/sql-from-data-model-skill/scripts/sql_login.py paths
```

The same script accepts `check`, `init-databases <file>`, `setup`, `setup --env <name>`, `run <database> <sql-file>`, and `run <database> <sql-file> --csv <path>`. Add `--dbvr-path <path>` in front of any command. The script saves that path.

Run `check`, `setup`, and `run` with network access. `setup` needs a person at the computer.

## Rules that always apply

- The query filter keeps it read-only whichever login you use; a read-only login is still the safest choice.
- Queries may only use `SELECT` and `WITH`. Every statement must start with `SELECT` or `WITH`. The only `SET` lines allowed are `SET NOCOUNT ON/OFF` and `SET TRANSACTION ISOLATION LEVEL READ UNCOMMITTED`, which the catalog scripts use. Put values directly in the query, for example `WHERE CustomerId = N'C-1001'`. If a value contains an apostrophe, write it twice, for example `N'O''Brien'`. Do not use `DECLARE` or `@variables`. dbvr runs each statement separately, so a declared variable is lost (SQL Error 137, verified 2026-10-16). The script blocks `DECLARE`, `INTO`, `NEXT VALUE FOR`, a statement that is only a bracketed or double-quoted name (SQL Server runs a lone name as a stored procedure), and the other write keywords.
- One database. One result set. No cross-database join. Do not invent a table, column, type, key, or count.
- Passwords are typed only in the sign-in windows. They are stored only in the `.env` file from `paths`. Do not put a password in a markdown file, a JSON file, a chat message, or git. Do not print the `.env` file. The script redacts saved values to `[hidden]`.
- Do not read DBeaver’s saved passwords. Do not drive the DBeaver app.
- `setup.json` may hold `source` (`dbvr` or `repos`), `dbvr_path`, `model_path`, `repo_links`, `notes_path`, and `read_access_confirmed`. `repo_links` is `{"<label>": "<link>"}`. `notes_path` is optional and may be `""`. Nothing else.

## How replies read

The user may not be technical. Use the exact user-facing messages in `.cursor/skills/sql-from-data-model-skill/SKILL.md` (the menu, the setup questions, the check and sign-in tables, the done line, and the answer format). In short:

- During setup, start each reply with one plain sentence saying what this step does and why.
- Use everyday words: “can be reached”, “can read data / can't change data”, “a private file on this computer”, “data model (a map of every table and column)”.
- During setup, do not show script output, `OK`/`SKIP` lines, settings paths, or commands. Show setup results as short tables with ✅. End with the one thing the user replies next, in bold.
- An answer uses this order:
  1. **Answer:** one short sentence. Every name, number, date, ID, and status in it must appear exactly in the table. No rounding. No new numbers: no totals, averages, or percentages. If one is needed, write a query that returns it. No facts that are not in the table.
  2. The script's table, pasted exactly: the header, the separator, and every row. Do not rename headers. Do not reorder or drop rows or columns. Do not reformat values. Keep `8,292` as `8,292`. Keep dates as printed. Keep blanks blank.
  3. `<n> rows returned.` The number is the script's `ROWS` line.
  4. Column notes. Explain a column or value only when the data model or the user's notes file documents it. Otherwise write `Meaning not documented.` or skip that column. Never explain a column from general knowledge. The notes file is `notes_path` in `setup.json`. Read it only for this. Do not use it to pick a table or write the query. If it disagrees with the data model, the data model wins. If `notes_path` is empty or the file is missing, there are no notes.
  5. Which database it came from, in words (for example, “From the <Environment> <Label> database.”).
  6. The query, folded under “The query it ran”. SQL appears only there. When a saved query was used, the title is “The query it ran (saved query)”.
- When `ROWS` is 0, the answer sentence is `**Answer:** No rows came back for <the values searched>.` Do not guess why. If the data model or the user's notes file documents a likely reason, you may add one sentence quoting it.
- More than 50 rows: the CSV path below stays. The summary may state only the row count and values that appear in the printed output.
- Before sending, compare every value in the answer sentence and the column notes against the script output. Remove or fix anything that does not match exactly.
- If the script prints `NOTE a value contains "|", so this table may display wrong`, include that note under the row count. Do not rebuild the table.

## Choose

If the user has not chosen, send the menu from `.cursor/skills/sql-from-data-model-skill/SKILL.md` and wait. It offers:

- **A: Automatic.** You ask in plain English; the skill writes the query, runs it, and shows the answer in the chat. Needs dbvr 26.2 or newer and access to the databases. The first time, a short setup signs you in. If dbvr isn't available, setup can read the code repos instead and write queries without running them.
- **B: Manual.** Read `.cursor/skills/sql-from-data-model-skill/manual.md` and follow it. The user copies the query into DBeaver and pastes the result back. With no data model yet, it first builds one by hand from `.cursor/skills/sql-from-data-model-skill/catalog/build.md`.

If the user already said Option A or Option B, skip the menu.

## Option A when setup is not finished

Run `paths`, then read `setup.json`. Continue only for what is missing.

1. Run `check`. It does not log in and does not open a window. Before databases exist, `SKIP` lines for databases, ports, and credentials are expected. If it prints `STOP dbvr not found`, ask once for the dbvr path, or give `https://github.com/dbeaver/dbvr/releases/latest` and stop. If the user says they will use the repos, use the repo steps instead.
2. Ask how to build the model if `source` is empty. 1 = dbvr (primary). 2 = repos (secondary).
3. For dbvr, there is no default database list. Ask in the chat for each database’s environment, label, server, database name, and port (default 1433). Or accept a path to a JSON file shaped like `.cursor/skills/sql-from-data-model-skill/scripts/databases.example.json`. When they describe the databases in the chat, write a temp JSON file with no secrets, run `init-databases <file>`, and delete the temp file. When they give a path, run `init-databases` on that file and do not delete it.
4. Run `check` again. If a server does not answer, name it, say to check the VPN or network, and stop. `SKIP credentials` is still expected.
5. If `check` printed `OK credentials`, skip sign-in. A shared `SQL_USER` still counts when `SQL_USER_<KEY>` is absent. Otherwise run `setup`. One sign-in window per environment, in order. Each database has a username field and a password field. Do not ask for a password in the chat.
6. When `setup` runs, any login that signs in passes. The script still reads each login's roles, only to report them: `OK <database>: read-only` or `OK <database>: can change data`. Report a table `Database | Signed in | Can change data`. If any database can change data, add this one sentence: “That login can change data, but the skill only runs queries that read data.” That report covers database roles only, not permissions granted directly to the login. `run` does not check roles; the query filter checks every query.
7. The script writes `.env` only if every database in that `setup` signed in. Then set `source` to `dbvr` and `dbvr_path` in `setup.json`. Do that write even when sign-in was skipped. Keep `notes_path`. Leave it `""` when the user has no notes file.
8. Ask where the model file should live. Default is the `model_path` from `paths` when `model_path_saved` is `no`. Save the chosen path as `model_path`. The file stays outside this repo. If the file exists, ask: “Use this model, or rebuild it from the databases?”
9. Build every database in `databases.json`, one at a time. Finish all seven catalog steps before the next database. Copy each step’s SQL from `.cursor/skills/sql-from-data-model-skill/catalog/queries.md` exactly into a temp file, run `run <database> <file>`, and delete the file. Follow the gates and template in `.cursor/skills/sql-from-data-model-skill/catalog/build.md`. Replace only that database’s section. Show progress, such as “Dev App: step 3 of 7”.
10. Say “Setup done, data model built. What do you want to find?” and stop. If Step 1 returned `can_view_definitions` = 0 for any database, put this sentence first, exactly, and name those databases: “This login cannot view definitions, so check-constraint rules, column defaults and some procedures and functions are not shown. Ask the DBA for VIEW DEFINITION (read-only) for a complete model.” Do not ask for a notes file. `notes_path` is optional.

Repos: ask for one repo link per database label, and read access. Labels shared by more than one environment use one link. Save those under `repo_links` with `read_access_confirmed` true and `source` set to `repos`. Read migrations and entity models only. Do not run a query. Row counts are `unknown (repos do not contain rows)`. Each repo updates the data-model sections for databases with that label. Do not push or edit those repos.

Running `setup` again changes databases or passwords. “Refresh the data model” reruns the build for one database or all of them, then marks that database's saved queries `Needs check: yes`. “Clear saved queries” deletes the file at `queries_path`.

`setup --env <name>` opens only that environment’s window and keeps the other saved values.

## Option A when setup is finished

1. Run `check`. If every line is `OK`, do not show it. If any line is `SKIP`, setup is not finished.
2. Before reading the data model, look in the saved queries at `queries_path` (see **Saved queries** below). If one entry matches, fill it in, run it in step 4, and use its column notes. Otherwise continue with step 3.
3. Read the model at `model_path`. Pick the database from the tables involved. Use the environment the user named. If they did not name one, ask.
4. Show the query, write it to a temp file, run `run`, and delete the file. `SELECT` and `WITH` only. Put values directly in the query, for example `WHERE CustomerId = N'C-1001'`. If a value contains an apostrophe, write it twice, for example `N'O''Brien'`. Do not use `DECLARE` or `@variables`. dbvr runs each statement separately, so a declared variable is lost (SQL Error 137, verified 2026-10-16).
5. The script prints the table, then `ROWS <n>`. 50 rows or fewer: paste that table exactly (header, separator, and every row). Do not rename headers or reformat values. Under it, write `<n> rows returned.` from the `ROWS` line. The **Answer:** sentence may use only names, numbers, dates, IDs, and statuses that appear exactly in the table. No rounding and no new totals, averages, or percentages. Explain a column only when the data model or the user's notes file documents it. Otherwise write `Meaning not documented.` or skip it. Read the notes file only for that explanation. Do not use it to pick a table or write the query. If the notes and the data model disagree, the data model wins. When `ROWS` is 0, the answer sentence is `**Answer:** No rows came back for <the values searched>.` Do not guess why. If the data model or the user's notes file documents a likely reason, you may add one sentence quoting it. Before sending, check every value in the sentence and the column notes against the script output. If the script prints `NOTE a value contains "|", so this table may display wrong`, include that note under the row count. More than 50: run again with `--csv` into the user’s Downloads folder as `<database>-<short-topic>-<YYYY-MM-DD>.csv`, unless they name a path. The summary may state only the row count and values that appear in the printed output. Name the database in words, for example “From the <Environment> <Label> database.” When a saved query was used, use its stored column notes and title the folded query “The query it ran (saved query)”. Nothing else in the answer changes.
6. If the query was new and `run` finished without `STOP`, add a saved-query entry. Do not ask and do not mention it.
7. Follow-up questions in the same chat skip `check`.

On the repo source, write the query and do not run it. Use the same literal values. If a value contains an apostrophe, write it twice, for example `N'O''Brien'`. Do not use `DECLARE` or `@variables`.

## Saved queries

Option A only. The file is `queries_path` from `paths`. It stays outside this repo, like the data model. The full entry template is in `.cursor/skills/sql-from-data-model-skill/SKILL.md` under **Saved queries**.

- **Never store returned data or the user's real values.** Each value the user gave becomes a `{placeholder}`.
- An entry holds: the question in general words, each `{placeholder}` with its column and type, the database, the tables used, the column notes, `Saved: <YYYY-MM-DD>`, `Needs check: no`, and the SQL.
- A match means the same database, the same tables, the same kind of answer, and only the values differ. If more than one entry could match, or you are unsure, write a new query.
- To use an entry, fill in each `{placeholder}`. Write any apostrophe in a text value twice. A number placeholder takes digits only; otherwise write a new query.
- An entry marked `Needs check: yes` is checked against the current data model first: keep it (set `Needs check: no`) if every table and column is still there, otherwise delete it.
- If the user says an answer was wrong, remove the entry that answer used or saved. “Refresh the data model” marks the rebuilt database's entries `Needs check: yes`. “Clear saved queries” deletes the file.

## Failures

- Wrong username or password: `setup --env <that environment>`, then retry the query.
- Firewall message: tell the user to ask the database admin to allow their IP.
- dbvr missing: tell them to reinstall it.
- A server did not answer: tell them to check the VPN or network.

## Known limits

`DECLARE` does not work. dbvr runs each statement separately, so a variable declared in one statement is missing in the next (SQL Error 137, verified 2026-10-16). Put the value directly in the query. If a value contains an apostrophe, write it twice, for example `N'O''Brien'`. The script refuses `DECLARE`.

A login without `VIEW DEFINITION` still sees every table and column, but SQL Server hides some metadata from it without an error. Step 1 reports this as `can_view_definitions`. When it is 0, the data model carries this line under Identity: “This login cannot view definitions, so check-constraint rules, column defaults and some procedures and functions are not shown. Ask the DBA for VIEW DEFINITION (read-only) for a complete model.” An empty check definition, or a default that exists but is hidden, is written as `not visible to this login`. A column with no default stays blank. An empty index filter definition is written as `filter definition not returned`. Do not guess them. A column whose user-defined alias type is hidden is listed with its built-in base type.

Building the data model through dbvr was verified on 2026-10-19: all seven catalog scripts ran unchanged through `run`, with `--csv`, on four Azure SQL databases. Also verified on 2026-10-21 on SQL Server 2022 on Windows, with a `db_datareader` login without `VIEW DEFINITION`: 109 of 109 columns.

The password goes to dbvr on its command line, because dbvr has no verified way to read it from an environment variable or a file. While a query runs, other programs on the same computer can see it in the process list. The script never puts it in a shell string and never prints it.

On Windows, dbvr's bundled Java writes the printed table in the Windows code page, so a character outside it, such as an emoji, came back as `?` (verified with dbvr 26.2.3). Setting `JAVA_TOOL_OPTIONS=-Dstdout.encoding=UTF-8` fixed it; `-Dfile.encoding=UTF-8` did not. The script sets that option for dbvr on Windows only, and keeps any `JAVA_TOOL_OPTIONS` already set. The CSV from `--csv` was always UTF-8.

## Not verified

Say this when you use these parts.

- Whether `SET NOCOUNT ON` and `SET TRANSACTION ISOLATION LEVEL READ UNCOMMITTED` carry over to the next statement. They are harmless either way. Leave the catalog scripts unchanged.
- The Windows dbvr install paths. The Windows test used `--dbvr-path`.
- The Linux sign-in window.
- The Mac sign-in window with one username and one password per database. Windows was verified on 2026-10-21 with one database.
- The “can change data” report covers database roles only.
- Answers from a fresh agent session in Cursor or Claude Code.
