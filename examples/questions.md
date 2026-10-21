# Five questions, answered by the skill

Each question was asked in plain English. The skill picked the tables from [data-model.md](data-model.md), wrote a `SELECT`, ran it through `run` with a read-only login, and answered in the format `SKILL.md` sets: a one-line answer, the table exactly as returned, the row count, column notes, the database, and the query.

After each new query ran, it was saved to [data-model.saved-queries.md](data-model.saved-queries.md). Question 5 asks the same kind of thing as question 3 with a different name, so it reused that saved query.

Each answer was then checked against a separate query run with an admin login. Those checks were written differently on purpose, so the same mistake couldn't pass twice:
- apostrophes matched with a wildcard and a character-code check instead of a doubled `''`
- revenue recomputed from quantity × price × (1 − discount), ranked to catch ties at 5th place
- category counts through subqueries instead of joins

All five matched.

---

## 1. Which customers work at Family's Favorite Bike Shop?

The company name has an apostrophe, which the query writes twice.

**Answer:** CustomerID 570 and 29,503 work at Family's Favorite Bike Shop. Both rows are Gregory Alderson.

|CustomerID|FirstName|LastName|CompanyName                |EmailAddress                |
|----------|---------|--------|---------------------------|----------------------------|
|570       |Gregory  |Alderson|Family's Favorite Bike Shop|gregory0@adventure-works.com|
|29,503    |Gregory  |Alderson|Family's Favorite Bike Shop|gregory0@adventure-works.com|

2 rows returned.

Column notes: Meaning not documented.

From the Test Sample database.

<details><summary>The query it ran</summary>

```sql
SELECT CustomerID, FirstName, LastName, CompanyName, EmailAddress
FROM SalesLT.Customer
WHERE CompanyName = N'Family''s Favorite Bike Shop'
ORDER BY CustomerID;
```

</details>

## 2. What are the top 5 products by revenue?

**Answer:** Touring-1000 Blue, 60 (ProductID 969) has the most revenue, 37,191.492.

|ProductID|Name                   |Revenue      |
|---------|-----------------------|-------------|
|969      |Touring-1000 Blue, 60  |37,191.492   |
|783      |Mountain-200 Black, 42 |37,178.838   |
|976      |Road-350-W Yellow, 48  |36,486.2355  |
|782      |Mountain-200 Black, 38 |35,801.844   |
|957      |Touring-1000 Yellow, 60|23,413.474656|

5 rows returned.

Column notes: Revenue is the sum of SalesOrderDetail.LineTotal. Meaning not documented.

From the Test Sample database.

<details><summary>The query it ran</summary>

```sql
SELECT TOP 5 p.ProductID, p.Name, SUM(d.LineTotal) AS Revenue
FROM SalesLT.SalesOrderDetail AS d
INNER JOIN SalesLT.Product AS p ON p.ProductID = d.ProductID
GROUP BY p.ProductID, p.Name
ORDER BY Revenue DESC;
```

</details>

## 3. What phone number and email do we have for customer D'Hers?

**Answer:** Thierry D'Hers (CustomerID 299 and 29,692) has phone 680-555-0192 and email thierry1@adventure-works.com.

|CustomerID|FirstName|LastName|Phone       |EmailAddress                |
|----------|---------|--------|------------|----------------------------|
|299       |Thierry  |D'Hers  |680-555-0192|thierry1@adventure-works.com|
|29,692    |Thierry  |D'Hers  |680-555-0192|thierry1@adventure-works.com|

2 rows returned.

Column notes: Meaning not documented.

From the Test Sample database.

<details><summary>The query it ran</summary>

```sql
SELECT CustomerID, FirstName, LastName, Phone, EmailAddress
FROM SalesLT.Customer
WHERE LastName = N'D''Hers'
ORDER BY CustomerID;
```

</details>

## 4. How many products are in each top-level product category?

Products belong to subcategories, so the query joins the category table to itself through `ParentProductCategoryID`, a foreign key the data model lists.

**Answer:** Components has the most products, 134.

|Category   |Products|
|-----------|--------|
|Components |134     |
|Bikes      |97      |
|Clothing   |35      |
|Accessories|29      |

4 rows returned.

Column notes: Meaning not documented.

From the Test Sample database.

<details><summary>The query it ran</summary>

```sql
SELECT parent.Name AS Category, COUNT(p.ProductID) AS Products
FROM SalesLT.Product AS p
INNER JOIN SalesLT.ProductCategory AS c ON c.ProductCategoryID = p.ProductCategoryID
INNER JOIN SalesLT.ProductCategory AS parent ON parent.ProductCategoryID = c.ParentProductCategoryID
GROUP BY parent.Name
ORDER BY Products DESC, Category;
```

</details>

## 5. What phone number and email do we have for customer Harris?

This is the same kind of question as question 3, with a different name. The skill found the saved entry *What phone number and email do we have for customer {last_name}?*, filled in `{last_name}`, and did not read the data model again.

**Answer:** Keith Harris (CustomerID 2 and 29,816) has phone 170-555-0127 and email keith0@adventure-works.com.

|CustomerID|FirstName|LastName|Phone       |EmailAddress              |
|----------|---------|--------|------------|--------------------------|
|2         |Keith    |Harris  |170-555-0127|keith0@adventure-works.com|
|29,816    |Keith    |Harris  |170-555-0127|keith0@adventure-works.com|

2 rows returned.

Column notes: Meaning not documented.

From the Test Sample database.

<details><summary>The query it ran (saved query)</summary>

```sql
SELECT CustomerID, FirstName, LastName, Phone, EmailAddress
FROM SalesLT.Customer
WHERE LastName = N'Harris'
ORDER BY CustomerID;
```

</details>
