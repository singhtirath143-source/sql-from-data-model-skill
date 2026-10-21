# SQL from a data model

An agentic, read-only database assistant for SQL Server and Azure SQL. You ask a question in plain English, such as *How many orders does customer C-1001 have?*, and the agent does the database work from start to finish:

1. **Sets itself up.** It checks that dbvr is installed and every database can be reached. It opens a sign-in window for your username and password, never the chat. Then it tells you whether the login can change data.
2. **Learns the database.** It runs 7 read-only catalog scripts and writes a data model: a map of every table, column, and key.
3. **Answers.** It picks the right database and tables from the data model, writes the query, runs it, and checks its answer against the result before replying.

It never changes data. The query filter keeps it read-only whichever login you use; a read-only login is still the safest choice. The script refuses anything but `SELECT` and `WITH`. The agent doesn't guess either: it uses only tables and columns in the data model, and only values that came back from the database.

It is one skill, `/sql-from-data-model-skill`, with two options:

- **Option A: Automatic.** The agent does all three steps above and answers in the chat. Needs dbvr.
- **Option B: Manual.** The agent writes the query. You run it in DBeaver and paste the result back. Use this when you can't install dbvr.

dbvr uses the `microsoft` driver and a SQL username and password. The skill does not use Azure AD. It does not support other database engines.

This repo does not include your data model. [examples/](examples/) has one built from Microsoft's public sample database. The default location is the `model_path` from `paths`, inside the settings folder, which is outside this repo. You can choose another path. Keep the data model outside this repo and do not commit it. Do not commit passwords or connection strings. Passwords are typed in the sign-in windows and stored only in the private `.env` file.

## How it works

Every question needs a data model: a map of the database's tables, columns, and keys. Option A builds it during first-time setup. Option B uses a model you already have, or walks you through building one, one catalog script at a time.

```mermaid
flowchart TD
  start["/sql-from-data-model-skill"] --> menu{"Option A or B?"}

  menu -->|"A: Automatic"| done{"Setup done?"}
  done -->|No| setup["First-time setup<br/>1. Check dbvr and that each database can be reached<br/>2. Sign in through a window, never the chat<br/>3. Report whether the login can change data<br/>4. Build the data model"]
  setup --> ask
  done -->|Yes| ask["Ask a question in plain English"]
  ask --> write["The skill reuses a saved query,<br/>or writes a SELECT from the data model"]
  write --> run["The script refuses anything but SELECT and WITH,<br/>then runs the query through dbvr"]
  run --> verify["Check before sending<br/>Table pasted exactly as returned<br/>Row count from the script, not the agent<br/>Answer uses only values in the table<br/>Column meanings only from the data model or notes"]
  verify --> answer["Answer in the chat:<br/>the exact table, the row count, and the query"]

  menu -->|"B: Manual"| has{"Have a data model?"}
  has -->|No| discover["Build it by hand<br/>7 catalog scripts you run yourself"]
  discover --> model[("Data model file")]
  has -->|Yes| model
  model --> writeb["The skill writes a SELECT"]
  writeb --> dbeaver["You run it in DBeaver<br/>and paste the result back"]
```

If dbvr is not available, Option A can build the data model from your code repos instead. It then writes the query but does not run it.

## Example

[examples/](examples/) holds one real run on Microsoft's AdventureWorksLT sample database: the data model the skill wrote, five questions with their answers and queries, and 19 write attempts the script refused.

## Prerequisites

- Python 3. The standard library is enough. Try `python3`, then `py -3`, then `python`.
- dbvr 26.2 or newer for Option A. The skill does not install it. Releases: https://github.com/dbeaver/dbvr/releases/latest
- Network or VPN access to the database ports.
- Your IP allowed in the Azure SQL firewall, when the server is Azure SQL.

Option B needs DBeaver. It does not need dbvr.

## Install

Clone this repo, or use **Code → Download ZIP** on GitHub and unzip it.

```text
git clone https://github.com/singhtirath143-source/sql-from-data-model-skill.git
```

**Cursor.** Copy the `.cursor/skills/sql-from-data-model-skill` folder into the user skills folder:

- Mac and Linux: `~/.cursor/skills/`
- Windows: `%USERPROFILE%\.cursor\skills\`

**Claude Code.** Copy the same folder into:

- Mac and Linux: `~/.claude/skills/`
- Windows: `%USERPROFILE%\.claude\skills\`

**Codex, Copilot, and other agents.** Open this repo and follow `AGENTS.md`.

The folder holds everything the skill needs:

| File | What it is |
|---|---|
| `SKILL.md` | The menu and Option A |
| `manual.md` | Option B |
| `catalog/queries.md` | The 7 read-only catalog scripts |
| `catalog/build.md` | How the data model is built and written |
| `notes.template.md` | A blank, optional column-notes file |
| `scripts/sql_login.py` | The dbvr script |
| `scripts/databases.example.json` | A placeholder database list |

The dbvr script is `.cursor/skills/sql-from-data-model-skill/scripts/sql_login.py`. Copying the skill folder copies the script. `.cursor/skills/sql-from-data-model-skill/scripts/databases.example.json` is a placeholder list with no passwords. Copy it, replace the placeholders, and pass that file to `init-databases`. Do not commit the copy if it contains real server names.

Opening this repo in Cursor also finds the skill under `.cursor/skills/`.

## Where settings live

The script prints the paths. Run:

```text
python3 .cursor/skills/sql-from-data-model-skill/scripts/sql_login.py paths
```

- Mac and Linux: `~/.config/sql-from-data-model/`
- Windows: `%APPDATA%\sql-from-data-model\`

That folder holds:

- `setup.json` — source, dbvr path, model path, repo links, an optional notes path, and whether read access was confirmed. No passwords.
- `databases.json` — servers and database names. No passwords.
- `.env` — username and password per database.
- `dbvr-workspace/` — dbvr’s own workspace. The skill does not use DBeaver’s folders.

The saved-queries file sits next to the data model, named `<data model name>.saved-queries.md`. `paths` prints it as `queries_path`. Like the data model, it stays outside this repo. It holds questions in general words with `{placeholders}`, the tables, column notes, and SQL. It never holds returned data or the values a user typed.

`setup.json` looks like this. `repo_links` is one link per database label. `notes_path` may be empty.

```json
{
  "source": "",
  "dbvr_path": "",
  "model_path": "",
  "repo_links": {},
  "notes_path": "",
  "read_access_confirmed": false
}
```

On Mac and Linux the script sets the folder to mode `0700` and `.env` to mode `0600`. On Windows it relies on the user profile being private. Windows does not get those Unix modes.

## Using the skill

In chat, type `/sql-from-data-model-skill`.

The skill shows Option A, then Option B. Read both. Reply with A or B. It does not look anything up until you choose.

If that same message already says Option A or Option B, it skips the menu and uses that option.

### Option A

dbvr is the primary way, on Mac or Windows. You need dbvr 26.2 or newer, the database ports reachable, and your IP allowed by the database firewall. There is no built-in database list. You enter each database (environment, label, server, database name, and port), or you point at a JSON file shaped like `.cursor/skills/sql-from-data-model-skill/scripts/databases.example.json`.

Setup opens one sign-in window per environment. Each database has a username and a password. Paste with ⌘V on Mac and Ctrl+V on Windows. Any login that signs in is saved. Setup still reads each login's database roles, only to report them: when a login can change data, the user sees “That login can change data, but the skill only runs queries that read data.” That report covers database roles, not permissions granted directly to the login. A read-only login plus `VIEW DEFINITION` gives a complete data model; without it the model still works, but rules and defaults are hidden.

An `.env` already saved with `SQL_USER` and `SQL_PASSWORD_<KEY>` keeps working. `SQL_USER_<KEY>` is used when it exists. When it does not, `SQL_USER` is the username. A complete saved login does not open the sign-in windows again.

Setup then builds the data model, one database at a time. After that, a question runs on the database and the answer comes back in the chat.

Queries use `SELECT` and `WITH` only. Every statement must start with `SELECT` or `WITH`. The only `SET` lines allowed are `SET NOCOUNT ON/OFF` and `SET TRANSACTION ISOLATION LEVEL READ UNCOMMITTED`, which the catalog scripts use. Put values directly in the query, for example `WHERE CustomerId = N'C-1001'`. If a value contains an apostrophe, write it twice, for example `N'O''Brien'`. Do not use `DECLARE` or `@variables`. dbvr runs each statement separately, so a declared variable is lost (SQL Error 137, verified 2026-10-16). The repo source writes queries the same way. The filter also refuses `NEXT VALUE FOR` and a statement that is only a bracketed or double-quoted name, because SQL Server runs a lone name at the start of a batch as a stored procedure.

After a new query runs, the skill quietly saves it to the saved-queries file. The next question of the same kind, with different values, reuses it, and the folded query says “(saved query)”. If you say an answer was wrong, that entry is removed. “Refresh the data model” marks that database's entries to be checked again. “Clear saved queries” deletes the file.

The skill cannot connect to DBeaver, and it does not read DBeaver’s saved passwords.

The repos are a secondary choice if dbvr is not available. You provide one repo link per database label, and read access. The skill reads migrations and entity models. It writes a query from the code. It does not run the query, because the code has no rows. This setup does not ask for passwords.

### Answers

An answer copies the script’s table exactly as printed, including the header, the separator, and every row, then states `<n> rows returned.` from the script’s `ROWS` line. The opening sentence quotes only names, numbers, dates, IDs, and statuses that appear in that table. A column is explained only when the data model or the user's notes file documents it. Before sending, the agent compares every value in its answer against the script output and fixes anything that does not match. The notes file is optional. Its path is `notes_path` in `setup.json`. The blank template is `.cursor/skills/sql-from-data-model-skill/notes.template.md`.

### Option B — manual

Pick Option B from the menu.

The skill reads a saved map of tables and columns, writes the question, and you run that question yourself in DBeaver.

You need DBeaver already open on the database. The skill writes the SQL. You paste it into DBeaver, run it, and paste the result back.

The model file is `model_path` in `setup.json` when that file exists. Otherwise the skill asks which file to use, or offers to build one by hand.

The query uses only tables and columns in that file. Each script is for one database. Column notes come from the data model or from `notes_path`. If `notes_path` is empty, a column that the data model does not explain is reported as `Meaning not documented.`

### Building the data model by hand

Option B uses it when you don't have a data model yet.

The skill gives you one SQL script. Run it in your database tool and paste the result back. It then gives you the next script. There are 7 scripts. They only read the list of tables, columns, and keys. They do not change data.

After the last result, the skill writes a markdown file. That file is the data model. Save it outside this repo. Do not commit it.

Do one database at a time. If you have two databases, finish the first before starting the second.

Option A, when it uses dbvr, runs those same 7 scripts itself. It does not change them.

## What has been verified

Verified on Windows 10 with dbvr 26.2.3 against SQL Server 2022 and Microsoft's AdventureWorksLT sample, on 2026-10-21. Details are in [examples/](examples/).

- The PowerShell sign-in window: it opens, Ctrl+V pastes, the password stays hidden, and a read-only login is saved.
- A wrong password and Cancel save nothing (tested with a stand-in for the window).
- A login that can change data: setup saves it and says so. 19 write and bypass attempts through `run` were refused before reaching the database, and the data was unchanged.
- All 7 catalog scripts through `run`, with a `db_datareader` login without `VIEW DEFINITION`. Every column came back (109 of 109), and the data model says what is hidden.
- Five questions, each checked against a separate admin query, including values with an apostrophe and a saved query reused for a second name.

Verified on Mac with dbvr 26.2.2 against Azure SQL: login, the read-only proof (reader 1, writer 0, owner 0), SELECT, JOIN, GROUP BY, an empty result, and an emoji value.

- The Mac sign-in window: an NSAlert with an Edit menu, so ⌘V paste works.
- The read-only role proof returned reader 1, writer 0, owner 0.
- This query style works: `dbvr -data=<workspace> sql --driver=microsoft --host= --port=1433 --database= --user= --password= --disable-status [-l=100000] [-format=csv -out=<file>] "<query>"`
- `-l` and `-format=csv -out=` worked on a large result.

Also verified on Mac through `.cursor/skills/sql-from-data-model-skill/scripts/sql_login.py run`:

- `run` works. That covers `-in=<file>` and `-l=100000`.
- `GROUP BY` and `SELECT … JOIN` returned rows.
- The same lookup with the value written in the query returned rows.
- An empty result. dbvr printed a header and a separator, and no data row. The script then printed `ROWS 0`. The shape looks like this:

```
|CustomerId|
|----------|
```

`run` sends the SQL file with `-in=<file>` and `-l=100000`. After the table, `run` prints `ROWS <n>`. `run` no longer checks the login's roles before each query; the query filter checks every query first. The role check in `setup` is one trailing `SELECT`.

Building the data model through dbvr was verified on 2026-10-19: all seven catalog scripts ran unchanged through `run`, with `--csv`, on four Azure SQL databases.

On Windows, dbvr's bundled Java writes the printed table in the Windows code page, so a character outside it, such as an emoji, came back as `?` (verified with dbvr 26.2.3). Setting `JAVA_TOOL_OPTIONS=-Dstdout.encoding=UTF-8` fixed it; `-Dfile.encoding=UTF-8` did not. The script sets that option for dbvr on Windows only, and keeps any `JAVA_TOOL_OPTIONS` already set. The CSV from `--csv` was always UTF-8.

## Known limits

`DECLARE` does not work. dbvr runs each statement separately, so a variable declared in one statement is missing in the next (SQL Error 137, verified 2026-10-16). Put the value directly in the query. If a value contains an apostrophe, write it twice, for example `N'O''Brien'`. The script refuses `DECLARE`.

A login without `VIEW DEFINITION` still sees every table and column, but SQL Server hides some metadata from it without an error. When that happens, the data model says so under Identity: “This login cannot view definitions, so check-constraint rules, column defaults and some procedures and functions are not shown. Ask the DBA for VIEW DEFINITION (read-only) for a complete model.” An empty check definition, or a default that exists but is hidden, is listed as `not visible to this login`. A column with no default stays blank. An empty index filter definition is listed as `filter definition not returned`. A column whose user-defined alias type is hidden is listed with its built-in base type.

The password goes to dbvr on its command line, because dbvr has no verified way to read it from an environment variable or a file. While a query runs, other programs on the same computer can see it in the process list. The script never puts it in a shell string and never prints it.

## What has not been verified

- Whether `SET NOCOUNT ON` and `SET TRANSACTION ISOLATION LEVEL READ UNCOMMITTED` carry over to the next statement. They are harmless either way. The catalog scripts stay unchanged.
- These Windows install paths, which are guesses: `%ProgramFiles%\dbvr\dbvr.exe` and `%LOCALAPPDATA%\Programs\dbvr\dbvr.exe`. The Windows test used the portable dbvr download with `--dbvr-path`.
- The Linux sign-in window.
- The Mac sign-in window with one username and one password per database. Windows was verified with one database.
- The “can change data” report covers database roles only, not permissions granted directly to the login.
- Answers from a fresh agent session in Cursor or Claude Code. On Windows, the questions were answered by following `SKILL.md` step by step.

## Verify on a new machine

Run this once on a real Mac or Windows machine, with a person at the computer. On Mac the Python command is `python3`. On Windows it is `py -3`. The script is `.cursor/skills/sql-from-data-model-skill/scripts/sql_login.py`.

1. Offline tests, from this repo:

```text
python3 -m unittest discover -s tests -v
py -3 -m unittest discover -s tests -v
```

Every test passes.

2. `paths` shows this machine’s settings folder. Mac and Linux: `~/.config/sql-from-data-model/`. Windows: `%APPDATA%\sql-from-data-model\`.

```text
python3 .cursor/skills/sql-from-data-model-skill/scripts/sql_login.py paths
py -3 .cursor/skills/sql-from-data-model-skill/scripts/sql_login.py paths
```

3. `check` prints `OK dbvr` and a version of 26.2 or newer. If it prints `STOP dbvr not found`, run it again with `--dbvr-path` set to the dbvr program.

4. Copy `.cursor/skills/sql-from-data-model-skill/scripts/databases.example.json`. Replace the placeholders with the servers and database names you use, and save that file outside this repo. Then load it and run `check` again. Every server prints `OK port`.

```text
python3 .cursor/skills/sql-from-data-model-skill/scripts/sql_login.py init-databases <file>
py -3 .cursor/skills/sql-from-data-model-skill/scripts/sql_login.py init-databases <file>
```

5. `setup`, with network access and someone at the computer:
   - The “Sign in to <environment>” window opens in front. Each database has a username field and a password field.
   - Paste works: ⌘V on Mac, Ctrl+V on Windows. Passwords stay hidden.
   - Cancel saves nothing.
   - After the last window, each database prints `OK … read-only` or `OK … can change data`, then `SAVED`.

6. Write a short `SELECT` from a table in one of your databases to a file and run it. `<database>` is a database name from your list. A table prints.

```text
python3 .cursor/skills/sql-from-data-model-skill/scripts/sql_login.py run <database> <file>
py -3 .cursor/skills/sql-from-data-model-skill/scripts/sql_login.py run <database> <file>
```

7. Write `SELECT N'📣 test' AS Sample;` to a file and run it on one database from your list. The emoji prints without an error. This is the Windows text check.

8. Run that same query with `--csv <path>`. Open the file. The emoji is intact.

9. Through the agent, build the data model for one database. The progress says “step N of 7”, and that database’s section is written. The file stays outside this repo.

10. Write down the results, including the real dbvr install path on Windows, and update the verified lists in this file, `AGENTS.md`, and `.cursor/skills/sql-from-data-model-skill/SKILL.md`.

## License

MIT. See [LICENSE](LICENSE).
