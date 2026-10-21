# SQL from a data model

This file is the procedure for Codex, Copilot, and any other agent. Cursor and Claude Code use the same procedure from `.cursor/skills/sql-from-data-model/SKILL.md`. If that skill file is available, follow it. The steps below are enough on their own.

This repo is one skill. It supports SQL Server and Azure SQL only. The dbvr driver is `microsoft`. Logins are SQL username and password, not Azure AD.

Do not rewrite the catalog scripts. Do not commit. Do not install dbvr. Do not push or modify a product repo.

## Files

Everything is in `.cursor/skills/sql-from-data-model/`.

| What | Where |
|---|---|
| Main procedure (menu and Option A) | `SKILL.md` |
| Option B (manual) | `manual.md` |
| Blank notes template | `notes.template.md` |
| Catalog SQL | `catalog/queries.md` |
| Catalog gates and template, and the by-hand build | `catalog/build.md`. Option A uses only the sections `## Gates`, `## After each passing result`, and `## Write the data model` |
| Script | `scripts/sql_login.py` |
| Example database list | `scripts/databases.example.json` |

Settings live outside this repo. Run `paths` and use the paths it prints. Do not guess a home folder. Keep the data model outside this repo and do not commit it. The default is the `model_path` from `paths`.

Try `python3`, then `py -3`, then `python`.

```text
python3 .cursor/skills/sql-from-data-model/scripts/sql_login.py paths
```

The same script accepts `check`, `init-databases <file>`, `setup`, `setup --env <name>`, `run <database> <sql-file>`, and `run <database> <sql-file> --csv <path>`. Add `--dbvr-path <path>` in front of any command. The script saves that path.

Run `check`, `setup`, and `run` with network access. `setup` needs a person at the computer.

## Rules that always apply

- Queries may only use `SELECT` and `WITH`. Every statement must start with `SELECT` or `WITH`. The only `SET` lines allowed are `SET NOCOUNT ON/OFF` and `SET TRANSACTION ISOLATION LEVEL READ UNCOMMITTED`, which the catalog scripts use. Put values directly in the query, for example `WHERE CustomerId = N'C-1001'`. If a value contains an apostrophe, write it twice, for example `N'O''Brien'`. Do not use `DECLARE` or `@variables`. dbvr runs each statement separately, so a declared variable is lost (SQL Error 137, verified 2026-10-16). The script blocks `DECLARE`, `INTO`, `NEXT VALUE FOR`, and the other write keywords. That filter is what keeps the skill read-only, whichever login is used.
- One database. One result set. No cross-database join. Do not invent a table, column, type, key, or count.
- Passwords are typed only in the sign-in windows. They are stored only in the `.env` file from `paths`. Do not put a password in a markdown file, a JSON file, a chat message, or git. Do not print the `.env` file. The script redacts saved values to `[hidden]`.
- Do not read DBeaver’s saved passwords. Do not drive the DBeaver app.
- `setup.json` may hold `source` (`dbvr` or `repos`), `dbvr_path`, `model_path`, `repo_links`, `notes_path`, and `read_access_confirmed`. `repo_links` is `{"<label>": "<link>"}`. `notes_path` is optional and may be `""`. Nothing else.

## How replies read

The user may not be technical. Use the exact user-facing messages in `.cursor/skills/sql-from-data-model/SKILL.md` (the menu, the setup questions, the check and sign-in tables, the done line, and the answer format). In short:

- During setup, start each reply with one plain sentence saying what this step does and why.
- Use everyday words: “can be reached”, “can read data / can't change data”, “a private file on this computer”, “data model (a map of every table and column)”.
- During setup, do not show script output, `OK`/`SKIP` lines, settings paths, or commands. Show setup results as short tables with ✅. End with the one thing the user replies next, in bold.
- An answer uses this order:
  1. **Answer:** one short sentence. Every name, number, date, ID, and status in it must appear exactly in the table. No rounding. No new numbers: no totals, averages, or percentages. If one is needed, write a query that returns it. No facts that are not in the table.
  2. The script's table, pasted exactly: the header, the separator, and every row. Do not rename headers. Do not reorder or drop rows or columns. Do not reformat values. Keep `8,292` as `8,292`. Keep dates as printed. Keep blanks blank.
  3. `<n> rows returned.` The number is the script's `ROWS` line.
  4. Column notes. Explain a column or value only when the data model or the user's notes file documents it. Otherwise write `Meaning not documented.` or skip that column. Never explain a column from general knowledge. The notes file is `notes_path` in `setup.json`. Read it only for this. Do not use it to pick a table or write the query. If it disagrees with the data model, the data model wins. If `notes_path` is empty or the file is missing, there are no notes.
  5. Which database it came from, in words (for example, “From the <Environment> <Label> database.”).
  6. The query, folded under “The query it ran”. SQL appears only there.
- When `ROWS` is 0, the answer sentence is `**Answer:** No rows came back for <the values searched>.` Do not guess why. If the data model or the user's notes file documents a likely reason, you may add one sentence quoting it.
- More than 50 rows: the CSV path below stays. The summary may state only the row count and values that appear in the printed output.
- Before sending, compare every value in the answer sentence and the column notes against the script output. Remove or fix anything that does not match exactly.
- If the script prints `NOTE a value contains "|", so this table may display wrong`, include that note under the row count. Do not rebuild the table.

## Choose

If the user has not chosen, send the menu from `.cursor/skills/sql-from-data-model/SKILL.md` and wait. It offers:

- **A: Automatic.** You ask in plain English; the skill writes the query, runs it, and shows the answer in the chat. Needs dbvr 26.2 or newer and access to the databases. The first time, a short setup signs you in. If dbvr isn't available, setup can read the code repos instead and write queries without running them.
- **B: Manual.** Read `.cursor/skills/sql-from-data-model/manual.md` and follow it. The user copies the query into DBeaver and pastes the result back. With no data model yet, it first builds one by hand from `.cursor/skills/sql-from-data-model/catalog/build.md`.

If the user already said Option A or Option B, skip the menu.

## Option A when setup is not finished

Run `paths`, then read `setup.json`. Continue only for what is missing.

1. Run `check`. It does not log in and does not open a window. Before databases exist, `SKIP` lines for databases, ports, and credentials are expected. If it prints `STOP dbvr not found`, ask once for the dbvr path, or give `https://github.com/dbeaver/dbvr/releases/latest` and stop. If the user says they will use the repos, use the repo steps instead.
2. Ask how to build the model if `source` is empty. 1 = dbvr (primary). 2 = repos (secondary).
3. For dbvr, there is no default database list. Ask in the chat for each database’s environment, label, server, database name, and port (default 1433). Or accept a path to a JSON file shaped like `.cursor/skills/sql-from-data-model/scripts/databases.example.json`. When they describe the databases in the chat, write a temp JSON file with no secrets, run `init-databases <file>`, and delete the temp file. When they give a path, run `init-databases` on that file and do not delete it.
4. Run `check` again. If a server does not answer, name it, say to check the VPN or network, and stop. `SKIP credentials` is still expected.
5. If `check` printed `OK credentials`, skip sign-in. A shared `SQL_USER` still counts when `SQL_USER_<KEY>` is absent. Otherwise run `setup`. One sign-in window per environment, in order. Each database has a username field and a password field. Do not ask for a password in the chat.
6. When `setup` runs, it checks that each login can sign in. Any login can be used, including one that can change data: the script only runs `SELECT` and `WITH`. Report each database as OK or with the script’s failure line. When the script prints `can change data` for a database, say: “That login can change data, but the skill only runs queries that read data.” That label comes from database roles only.
7. The script writes `.env` only if every database in that `setup` signed in. Then set `source` to `dbvr` and `dbvr_path` in `setup.json`. Do that write even when sign-in was skipped. Keep `notes_path`. Leave it `""` when the user has no notes file.
8. Ask where the model file should live. Default is the `model_path` from `paths` when `model_path_saved` is `no`. Save the chosen path as `model_path`. The file stays outside this repo. If the file exists, ask: “Use this model, or rebuild it from the databases?”
9. Build every database in `databases.json`, one at a time. Finish all seven catalog steps before the next database. Copy each step’s SQL from `.cursor/skills/sql-from-data-model/catalog/queries.md` exactly into a temp file, run `run <database> <file>`, and delete the file. Follow the gates and template in `.cursor/skills/sql-from-data-model/catalog/build.md`. Replace only that database’s section. Show progress, such as “Dev App: step 3 of 7”.
10. Say “Setup done, data model built. What do you want to find?” and stop. Do not ask for a notes file. `notes_path` is optional.

Repos: ask for one repo link per database label, and read access. Labels shared by more than one environment use one link. Save those under `repo_links` with `read_access_confirmed` true and `source` set to `repos`. Read migrations and entity models only. Do not run a query. Row counts are `unknown (repos do not contain rows)`. Each repo updates the data-model sections for databases with that label. Do not push or edit those repos.

Running `setup` again changes databases or passwords. “Refresh the data model” reruns the build for one database or all of them, then marks that database's saved queries `Needs check: yes`.

`setup --env <name>` opens only that environment’s window and keeps the other saved values.

## Option A when setup is finished

1. Run `check`. If every line is `OK`, do not show it. If any line is `SKIP`, setup is not finished.
2. First look in the saved queries at `queries_path` (below). If an entry matches, use its query with the user's values and its column notes, and go to step 3. Otherwise read the model at `model_path`. Pick the database from the tables involved. Use the environment the user named. If they did not name one, ask.
3. Show the query, write it to a temp file, run `run`, and delete the file. `SELECT` and `WITH` only. Put values directly in the query, for example `WHERE CustomerId = N'C-1001'`. If a value contains an apostrophe, write it twice, for example `N'O''Brien'`. Do not use `DECLARE` or `@variables`. dbvr runs each statement separately, so a declared variable is lost (SQL Error 137, verified 2026-10-16).
4. The script prints the table, then `ROWS <n>`. 50 rows or fewer: paste that table exactly (header, separator, and every row). Do not rename headers or reformat values. Under it, write `<n> rows returned.` from the `ROWS` line. The **Answer:** sentence may use only names, numbers, dates, IDs, and statuses that appear exactly in the table. No rounding and no new totals, averages, or percentages. Explain a column only when the data model or the user's notes file documents it. Otherwise write `Meaning not documented.` or skip it. Read the notes file only for that explanation. Do not use it to pick a table or write the query. If the notes and the data model disagree, the data model wins. When `ROWS` is 0, the answer sentence is `**Answer:** No rows came back for <the values searched>.` Do not guess why. If the data model or the user's notes file documents a likely reason, you may add one sentence quoting it. Before sending, check every value in the sentence and the column notes against the script output. If the script prints `NOTE a value contains "|", so this table may display wrong`, include that note under the row count. More than 50: run again with `--csv` into the user’s Downloads folder as `<database>-<short-topic>-<YYYY-MM-DD>.csv`, unless they name a path. The summary may state only the row count and values that appear in the printed output. Name the database in words, for example “From the <Environment> <Label> database.”
5. After a new query runs and the answer is sent, save it in the saved queries (below). When a saved query was used, title the folded query “The query it ran (saved query)”.
6. Follow-up questions in the same chat skip `check`.

On the repo source, write the query and do not run it. Use the same literal values. Do not use `DECLARE` or `@variables`.

## Saved queries

The file is `queries_path` from `paths`, next to the data model and outside this repo. The entry shape is in `.cursor/skills/sql-from-data-model/SKILL.md` → **Saved queries**.

- Use an entry only when the question needs the same database, tables, and kind of answer, and only the values differ. Fill each `{placeholder}`; write an apostrophe twice; a number placeholder takes digits only. If unsure, write a new query. Skip entries marked `Needs check: yes` until checked.
- Save a new query only after it ran through `run` (not from the repo source). Do not ask or mention it. Never store returned data or the user's real values: the question in general words and `{placeholder}`s only.
- If the user says an answer was wrong, remove that entry. After a data model refresh, check each flagged entry's tables and columns against the new model: keep it (`Needs check: no`) or delete it. “Clear saved queries” deletes the file.

## Failures

- Wrong username or password: `setup --env <that environment>`, then retry the query.
- Firewall message: tell the user to ask the database admin to allow their IP.
- dbvr missing: tell them to reinstall it.
- A server did not answer: tell them to check the VPN or network.

## Known limits

`DECLARE` does not work. dbvr runs each statement separately, so a variable declared in one statement is missing in the next (SQL Error 137, verified 2026-10-16). Put the value directly in the query. The script refuses `DECLARE`.

Check constraint definitions and index filter definitions can come back empty when the login cannot view object definitions. Write them as `definition null` and `filter definition not returned`. Do not guess them.

Building the data model through dbvr was verified on 2026-10-19: all seven catalog scripts ran unchanged through `run`, with `--csv`, on four Azure SQL databases.

## Not verified

Say this when you use these parts.

- Whether `SET NOCOUNT ON` and `SET TRANSACTION ISOLATION LEVEL READ UNCOMMITTED` carry over to the next statement. They are harmless either way. Leave the catalog scripts unchanged.
- dbvr’s output encoding on Windows. The script tries UTF-8 first, then the Windows code page.
- The PowerShell sign-in window and the Windows dbvr install paths. Windows needs one real setup and one query.
- The Linux sign-in window.
- The Mac sign-in window with one username and one password per database.
- Setup and a query with a login that can change data (changed 2026-10-20). Not run against a real database yet.
- “Can change data” comes from database roles only.
- Saved queries (added 2026-10-20). Not used in a real session yet.
