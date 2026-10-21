# Column notes

This file is a blank template. It is not a data model, and it does not describe a real database.

The skill does not need a notes file. `notes_path` in `setup.json` starts empty, and setup can finish while it is empty.

To use notes:

1. Copy this file to a path outside this repo. Do not commit the copy.
2. Save that path as `notes_path` in `setup.json`.
3. Fill in only the meanings you want an answer to quote.

Write one section per database label. Use the `database_name` from that database's section in the data model. Do not put passwords, connection strings, or rows of data in this file.

An answer may quote a column meaning, a status value, or a join rule only when it is written here or in the data model. If this file and the data model disagree, the data model wins.

The automatic path reads a notes file only to explain a column or a value. It does not use these notes to choose a table or to write a query. The manual path may use a join rule written here. The data model still wins if they disagree.

## <Label>

**Database:** <database_name>

### Column meanings

| Schema | Table | Column | Meaning |
|---|---|---|---|
| | | | |

### Status values

| Schema | Table | Column | Value | Meaning |
|---|---|---|---|---|
| | | | | |

### Join rules

| From | To | Join | Note |
|---|---|---|---|
| | | | |
