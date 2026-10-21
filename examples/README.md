# Example: Microsoft's AdventureWorksLT sample

Everything in this folder came from one real run of the skill. The database was [AdventureWorksLT](https://learn.microsoft.com/en-us/sql/samples/adventureworks-install-configure), Microsoft's public sample, restored into SQL Server 2022 in Docker. It has 12 tables, 109 columns and 847 customers.

| File | What it shows |
|---|---|
| [data-model.md](data-model.md) | The data model the skill wrote from its 7 catalog scripts |
| [questions.md](questions.md) | Five plain-English questions: the answer, the exact table, and the query, each checked against a separate admin query |
| [data-model.saved-queries.md](data-model.saved-queries.md) | The saved queries those questions left behind: placeholders only, no searched values and no returned data |
| [read-only-gate.md](read-only-gate.md) | 19 write and bypass attempts with a login that **can** change data, all refused before reaching the database |

## How it was run

- **Machine:** Windows 10, dbvr 26.2.3, Python 3.
- **Login for the data model and the questions:** in `db_datareader` only, without `VIEW DEFINITION`. That's the usual read-only login, so the model shows what most users will see:
  - every table and column
  - the note at the top saying definitions are hidden
  - check-constraint rules and column defaults marked "not visible to this login"
  - 7 of the database's 10 views, procedures, functions and triggers (the other 3 are a procedure and two functions this login can't run, and without `VIEW DEFINITION` it can't see them)
- **Login for the write attempts:** in `db_datareader` and `db_datawriter`.
- **Sign-in:** the sign-in window was used for real. The repeated runs used a stand-in that typed the same login.

## Reading the results

- **Server name:** `source:` at the top of the data model is the Docker container's host name, as SQL Server reported it.
- **Two rows per customer:** questions 1, 3 and 5 return two rows for the same person, with different `CustomerID`s. That's what this sample database holds, and the answer shows both rows rather than picking one.
