# Saved queries

## Which customers work at company {company_name}?

- Database: `AdventureWorksLT`
- Tables: `SalesLT.Customer`
- Placeholders:
  - `{company_name}`: `SalesLT.Customer.CompanyName`, `nvarchar(128)`, text
- Column notes:
  - `CustomerID`, `FirstName`, `LastName`, `CompanyName`, `EmailAddress`: Meaning not documented.
- Saved: 2026-10-21
- Needs check: no

```sql
SELECT CustomerID, FirstName, LastName, CompanyName, EmailAddress
FROM SalesLT.Customer
WHERE CompanyName = N'{company_name}'
ORDER BY CustomerID;
```

## What are the top {top_n} products by revenue?

- Database: `AdventureWorksLT`
- Tables: `SalesLT.SalesOrderDetail`, `SalesLT.Product`
- Placeholders:
  - `{top_n}`: the number of products to return, `int`, number
- Column notes:
  - `Revenue`: the sum of `SalesOrderDetail.LineTotal`. Meaning not documented.
- Saved: 2026-10-21
- Needs check: no

```sql
SELECT TOP {top_n} p.ProductID, p.Name, SUM(d.LineTotal) AS Revenue
FROM SalesLT.SalesOrderDetail AS d
INNER JOIN SalesLT.Product AS p ON p.ProductID = d.ProductID
GROUP BY p.ProductID, p.Name
ORDER BY Revenue DESC;
```

## What phone number and email do we have for customer {last_name}?

- Database: `AdventureWorksLT`
- Tables: `SalesLT.Customer`
- Placeholders:
  - `{last_name}`: `SalesLT.Customer.LastName`, `nvarchar(50)`, text
- Column notes:
  - `Phone`, `EmailAddress`: Meaning not documented.
- Saved: 2026-10-21
- Needs check: no

```sql
SELECT CustomerID, FirstName, LastName, Phone, EmailAddress
FROM SalesLT.Customer
WHERE LastName = N'{last_name}'
ORDER BY CustomerID;
```

## How many products are in each top-level product category?

- Database: `AdventureWorksLT`
- Tables: `SalesLT.Product`, `SalesLT.ProductCategory` (joined to itself through `ParentProductCategoryID`)
- Placeholders: none
- Column notes:
  - `Category`, `Products`: Meaning not documented.
- Saved: 2026-10-21
- Needs check: no

```sql
SELECT parent.Name AS Category, COUNT(p.ProductID) AS Products
FROM SalesLT.Product AS p
INNER JOIN SalesLT.ProductCategory AS c ON c.ProductCategoryID = p.ProductCategoryID
INNER JOIN SalesLT.ProductCategory AS parent ON parent.ProductCategoryID = c.ParentProductCategoryID
GROUP BY parent.Name
ORDER BY Products DESC, Category;
```
