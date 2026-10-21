# Catalog scripts

Copy the script for the current step verbatim into the reply. Do not edit it. Each script is one result set, read-only, and safe to run on any SQL Server or Azure SQL database the user is connected to. The connection's current database is the one being described (`DB_NAME()`).

`database_firewall_rules` is excluded by name. On a database that has no such table, the filter matches nothing and the script still succeeds.

## Step 1 — Identity

```sql
/* Which database is this connection actually on? */
SET NOCOUNT ON;
SET TRANSACTION ISOLATION LEVEL READ UNCOMMITTED;

SELECT
  SYSUTCDATETIME() AS generated_utc,
  DB_NAME() AS database_name,
  @@SERVERNAME AS server_name,
  CAST(DATABASEPROPERTYEX(DB_NAME(), 'Collation') AS nvarchar(128)) AS collation_name,
  d.compatibility_level,
  HAS_PERMS_BY_NAME(DB_NAME(), 'DATABASE', 'VIEW DEFINITION') AS can_view_definitions
FROM sys.databases AS d
WHERE d.name = DB_NAME();
```

## Step 2 — Tables

```sql
/* Full table inventory with catalog row counts. */
SET NOCOUNT ON;
SET TRANSACTION ISOLATION LEVEL READ UNCOMMITTED;

SELECT
  s.name AS schema_name,
  t.name AS table_name,
  ISNULL(p.row_count, 0) AS row_count,
  (SELECT COUNT(*) FROM sys.columns AS c WHERE c.object_id = t.object_id) AS column_count,
  t.create_date,
  t.modify_date,
  t.temporal_type_desc
FROM sys.tables AS t
INNER JOIN sys.schemas AS s ON s.schema_id = t.schema_id
OUTER APPLY (
  SELECT SUM(sp.rows) AS row_count
  FROM sys.partitions AS sp
  WHERE sp.object_id = t.object_id
    AND sp.index_id IN (0, 1)
) AS p
WHERE t.is_ms_shipped = 0
  AND t.name <> N'database_firewall_rules'
ORDER BY s.name, t.name;
```

## Step 3 — Columns

```sql
/* Full column catalog: name, type, nullability, identity, default. */
SET NOCOUNT ON;
SET TRANSACTION ISOLATION LEVEL READ UNCOMMITTED;

SELECT
  s.name AS schema_name,
  t.name AS table_name,
  c.column_id,
  c.name AS column_name,
  COALESCE(ty.name, bt.name, N'unknown') AS type_name,
  CASE
    WHEN bt.name IN (N'varchar', N'char', N'binary', N'varbinary')
      THEN bt.name + N'(' + CASE WHEN c.max_length = -1 THEN N'max' ELSE CONVERT(nvarchar(10), c.max_length) END + N')'
    WHEN bt.name IN (N'nvarchar', N'nchar')
      THEN bt.name + N'(' + CASE WHEN c.max_length = -1 THEN N'max' ELSE CONVERT(nvarchar(10), c.max_length / 2) END + N')'
    WHEN bt.name IN (N'decimal', N'numeric')
      THEN bt.name + N'(' + CONVERT(nvarchar(10), c.precision) + N',' + CONVERT(nvarchar(10), c.scale) + N')'
    WHEN bt.name IN (N'datetime2', N'datetimeoffset', N'time')
      THEN bt.name + N'(' + CONVERT(nvarchar(10), c.scale) + N')'
    ELSE COALESCE(bt.name, ty.name, N'unknown')
  END AS type_display,
  CASE WHEN c.is_nullable = 1 THEN N'YES' ELSE N'NO' END AS is_nullable,
  c.is_identity,
  c.is_computed,
  CASE WHEN dc.object_id IS NULL THEN 0 ELSE 1 END AS has_default,
  LEFT(dc.definition, 400) AS default_definition
FROM sys.tables AS t
INNER JOIN sys.schemas AS s ON s.schema_id = t.schema_id
INNER JOIN sys.columns AS c ON c.object_id = t.object_id
LEFT JOIN sys.types AS ty ON ty.user_type_id = c.user_type_id
LEFT JOIN sys.types AS bt ON bt.user_type_id = c.system_type_id
LEFT JOIN sys.default_constraints AS dc
  ON dc.parent_object_id = c.object_id
 AND dc.parent_column_id = c.column_id
WHERE t.is_ms_shipped = 0
  AND t.name <> N'database_firewall_rules'
ORDER BY s.name, t.name, c.column_id;
```

## Step 4 — Indexes

```sql
/* Every index column, including primary keys, unique constraints, and filtered indexes. */
SET NOCOUNT ON;
SET TRANSACTION ISOLATION LEVEL READ UNCOMMITTED;

SELECT
  SCHEMA_NAME(t.schema_id) AS schema_name,
  t.name AS table_name,
  i.name AS index_name,
  i.type_desc,
  i.is_primary_key,
  i.is_unique,
  i.is_unique_constraint,
  i.has_filter,
  i.filter_definition,
  ic.key_ordinal,
  COL_NAME(ic.object_id, ic.column_id) AS column_name,
  ic.is_included_column,
  ic.is_descending_key
FROM sys.tables AS t
INNER JOIN sys.indexes AS i
  ON i.object_id = t.object_id
 AND i.index_id > 0
INNER JOIN sys.index_columns AS ic
  ON ic.object_id = i.object_id
 AND ic.index_id = i.index_id
WHERE t.is_ms_shipped = 0
  AND t.name <> N'database_firewall_rules'
ORDER BY schema_name, table_name, i.is_primary_key DESC, i.name, ic.is_included_column, ic.key_ordinal;
```

## Step 5 — Foreign keys

```sql
/* Every foreign key column. */
SET NOCOUNT ON;
SET TRANSACTION ISOLATION LEVEL READ UNCOMMITTED;

SELECT
  OBJECT_SCHEMA_NAME(fk.parent_object_id) AS parent_schema,
  OBJECT_NAME(fk.parent_object_id) AS parent_table,
  COL_NAME(fkc.parent_object_id, fkc.parent_column_id) AS parent_column,
  OBJECT_SCHEMA_NAME(fk.referenced_object_id) AS referenced_schema,
  OBJECT_NAME(fk.referenced_object_id) AS referenced_table,
  COL_NAME(fkc.referenced_object_id, fkc.referenced_column_id) AS referenced_column,
  fk.name AS foreign_key_name,
  fkc.constraint_column_id,
  fk.delete_referential_action_desc,
  fk.update_referential_action_desc,
  fk.is_disabled
FROM sys.foreign_keys AS fk
INNER JOIN sys.foreign_key_columns AS fkc
  ON fkc.constraint_object_id = fk.object_id
ORDER BY parent_schema, parent_table, foreign_key_name, fkc.constraint_column_id;
```

## Step 6 — Check constraints

```sql
/* Check constraints. */
SET NOCOUNT ON;
SET TRANSACTION ISOLATION LEVEL READ UNCOMMITTED;

SELECT
  OBJECT_SCHEMA_NAME(cc.parent_object_id) AS schema_name,
  OBJECT_NAME(cc.parent_object_id) AS table_name,
  cc.name AS constraint_name,
  COL_NAME(cc.parent_object_id, cc.parent_column_id) AS column_name,
  cc.definition,
  cc.is_disabled
FROM sys.check_constraints AS cc
ORDER BY schema_name, table_name, constraint_name;
```

## Step 7 — Views, procedures, functions, and triggers

```sql
/* Views, procedures, functions, and triggers. */
SET NOCOUNT ON;
SET TRANSACTION ISOLATION LEVEL READ UNCOMMITTED;

SELECT
  object_kind,
  schema_name,
  object_name,
  detail,
  modify_date
FROM (
  SELECT
    N'view' AS object_kind,
    s.name AS schema_name,
    v.name AS object_name,
    CAST(NULL AS nvarchar(400)) AS detail,
    v.modify_date
  FROM sys.views AS v
  INNER JOIN sys.schemas AS s ON s.schema_id = v.schema_id
  WHERE v.is_ms_shipped = 0
    AND v.name <> N'database_firewall_rules'

  UNION ALL

  SELECT
    o.type_desc,
    SCHEMA_NAME(o.schema_id),
    o.name,
    CAST(NULL AS nvarchar(400)),
    o.modify_date
  FROM sys.objects AS o
  WHERE o.type IN ('P', 'FN', 'IF', 'TF', 'AF')
    AND o.is_ms_shipped = 0

  UNION ALL

  SELECT
    N'trigger',
    OBJECT_SCHEMA_NAME(tr.parent_id),
    tr.name,
    OBJECT_SCHEMA_NAME(tr.parent_id) + N'.' + OBJECT_NAME(tr.parent_id),
    tr.modify_date
  FROM sys.triggers AS tr
  WHERE tr.parent_class_desc = N'OBJECT_OR_COLUMN'
    AND tr.is_ms_shipped = 0
) AS catalog_objects
ORDER BY object_kind, schema_name, object_name;
```
