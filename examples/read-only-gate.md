# Read-only gate: write attempts with a login that can change data

Run on 2026-10-21 against the AdventureWorksLT sample, through the skill's `run` command, signed in with a login that
is in `db_datareader` **and** `db_datawriter`. Each line was a separate attempt. Line 19 is one file of three lines
(`SELECT 1 AS a`, `GO`, `DELETE …`), shown here joined with `·`.

**Result:** 19 of 19 write or bypass attempts were refused by the script before anything was sent
to the database. The 2 reads ran, including one that searches for the word `DELETE` as a value. A checksum of the data
taken by an admin login before and after was identical.

| # | Attempt | What happened |
|---|---|---|
| 1 | `UPDATE SalesLT.Customer SET LastName = N'X' WHERE CustomerID = 1` | refused: statement 1 starts with "UPDATE SalesLT.Customer SET LastName" |
| 2 | `DELETE FROM SalesLT.Customer WHERE CustomerID = 1` | refused: statement 1 starts with "DELETE FROM SalesLT.Customer WHERE" |
| 3 | `INSERT INTO SalesLT.ProductCategory (Name) VALUES (N'Hack')` | refused: statement 1 starts with "INSERT INTO SalesLT.ProductCategory (Name)" |
| 4 | `SELECT * INTO dbo.CustomerCopy FROM SalesLT.Customer` | refused: the query contains INTO |
| 5 | `SELECT 1; DELETE FROM SalesLT.Customer WHERE CustomerID = 1` | refused: statement 2 starts with "DELETE FROM SalesLT.Customer WHERE" |
| 6 | `WITH c AS (SELECT * FROM SalesLT.Customer) DELETE FROM c WHERE CustomerID = 1` | refused: the query contains DELETE |
| 7 | `EXEC sp_who` | refused: statement 1 starts with "EXEC sp_who" |
| 8 | `[sp_who]` | refused: statement 1 starts with "[name]" |
| 9 | `sp_who` | refused: statement 1 starts with "sp_who" |
| 10 | `DECLARE @x INT = 1; SELECT @x` | refused: the query uses DECLARE |
| 11 | `SELECT 1 /* comment */; DROP TABLE SalesLT.Address` | refused: statement 2 starts with "DROP TABLE SalesLT.Address" |
| 12 | `CREATE TABLE dbo.t (id INT)` | refused: statement 1 starts with "CREATE TABLE dbo.t (id" |
| 13 | `TRUNCATE TABLE SalesLT.CustomerAddress` | refused: statement 1 starts with "TRUNCATE TABLE SalesLT.CustomerAddress" |
| 14 | `MERGE SalesLT.ProductCategory AS t USING (SELECT 1 AS id) s ON 1=0 WHEN NOT MATCHED THEN INSERT (Name) VALUES (N'x');` | refused: statement 1 starts with "MERGE SalesLT.ProductCategory AS t" |
| 15 | `SELECT * FROM OPENROWSET('SQLNCLI','x','SELECT 1')` | refused: the query contains OPENROWSET |
| 16 | `WAITFOR DELAY '00:00:05'` | refused: statement 1 starts with "WAITFOR DELAY ''" |
| 17 | `SELECT NEXT VALUE FOR dbo.someseq` | refused: the query contains NEXT VALUE FOR |
| 18 | `GRANT SELECT ON SalesLT.Customer TO public` | refused: statement 1 starts with "GRANT SELECT ON SalesLT.Customer" |
| 19 | `SELECT 1 AS a · GO · DELETE FROM SalesLT.Customer WHERE CustomerID = 1` | refused: the query contains DELETE |
| 20 | `SELECT LastName FROM SalesLT.Customer WHERE LastName = N'DELETE'` | ran (a real read) |
| 21 | `SELECT TOP 2 FirstName, LastName FROM SalesLT.Customer ORDER BY CustomerID` | ran (a real read) |
