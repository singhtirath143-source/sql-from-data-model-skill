---
title: "AdventureWorksLT Data Model"
date: 2026-10-21
source: AdventureWorksLT on 4f8e66111b25
note: Structural catalog from read-only sys.* scripts. Row counts are catalog estimates, not COUNT(*).
---

# AdventureWorksLT — Data Model

## Identity

generated_utc 2026-10-21 21:39:43.646 · server_name 4f8e66111b25 · collation_name SQL_Latin1_General_CP1_CI_AS · compatibility_level 160 · can_view_definitions 0

This login cannot view definitions, so check-constraint rules, column defaults and some procedures and functions are not shown. Ask the DBA for VIEW DEFINITION (read-only) for a complete model.

## Table inventory (12 tables)

| Schema | Table | Rows (estimate) | Created | Modified | Temporal |
|---|---|---|---|---|---|
| dbo | BuildVersion | 1 | 2018-03-04 | 2018-03-04 | NON_TEMPORAL_TABLE |
| dbo | ErrorLog | 0 | 2018-03-04 | 2018-03-04 | NON_TEMPORAL_TABLE |
| SalesLT | Address | 450 | 2018-03-04 | 2018-03-04 | NON_TEMPORAL_TABLE |
| SalesLT | Customer | 847 | 2018-03-04 | 2018-03-04 | NON_TEMPORAL_TABLE |
| SalesLT | CustomerAddress | 417 | 2018-03-04 | 2018-03-04 | NON_TEMPORAL_TABLE |
| SalesLT | Product | 295 | 2018-03-04 | 2018-03-04 | NON_TEMPORAL_TABLE |
| SalesLT | ProductCategory | 41 | 2018-03-04 | 2018-03-04 | NON_TEMPORAL_TABLE |
| SalesLT | ProductDescription | 762 | 2018-03-04 | 2018-03-04 | NON_TEMPORAL_TABLE |
| SalesLT | ProductModel | 128 | 2018-03-04 | 2018-03-04 | NON_TEMPORAL_TABLE |
| SalesLT | ProductModelProductDescription | 762 | 2018-03-04 | 2018-03-04 | NON_TEMPORAL_TABLE |
| SalesLT | SalesOrderDetail | 542 | 2018-03-04 | 2018-03-04 | NON_TEMPORAL_TABLE |
| SalesLT | SalesOrderHeader | 32 | 2018-03-04 | 2018-03-04 | NON_TEMPORAL_TABLE |

## [dbo].[BuildVersion]

**Rows (estimate):** 1  
**Primary key:** no primary key and no indexes  
**Unique:** none  
**Foreign keys:** no foreign keys  
**Check constraints:** none  
**Indexes:** none

| # | Column | Type | Nullable | Identity | Computed | Default |
|---|---|---|---|---|---|---|
| 1 | SystemInformationID | tinyint | NO | yes |  |  |
| 2 | Database Version | nvarchar(25) | NO |  |  |  |
| 3 | VersionDate | datetime | NO |  |  |  |
| 4 | ModifiedDate | datetime | NO |  |  | not visible to this login |

## [dbo].[ErrorLog]

**Rows (estimate):** 0  
**Primary key:** PK_ErrorLog_ErrorLogID (ErrorLogID)  
**Unique:** none  
**Foreign keys:** no foreign keys  
**Check constraints:** none  
**Indexes:** PK_ErrorLog_ErrorLogID clustered (ErrorLogID)

| # | Column | Type | Nullable | Identity | Computed | Default |
|---|---|---|---|---|---|---|
| 1 | ErrorLogID | int | NO | yes |  |  |
| 2 | ErrorTime | datetime | NO |  |  | not visible to this login |
| 3 | UserName | nvarchar(128) | NO |  |  |  |
| 4 | ErrorNumber | int | NO |  |  |  |
| 5 | ErrorSeverity | int | YES |  |  |  |
| 6 | ErrorState | int | YES |  |  |  |
| 7 | ErrorProcedure | nvarchar(126) | YES |  |  |  |
| 8 | ErrorLine | int | YES |  |  |  |
| 9 | ErrorMessage | nvarchar(4000) | NO |  |  |  |

## [SalesLT].[Address]

**Rows (estimate):** 450  
**Primary key:** PK_Address_AddressID (AddressID)  
**Unique:** AK_Address_rowguid (rowguid)  
**Foreign keys:** no foreign keys  
**Check constraints:** none  
**Indexes:** PK_Address_AddressID clustered (AddressID); AK_Address_rowguid nonclustered (rowguid); IX_Address_AddressLine1_AddressLine2_City_StateProvince_PostalCode_CountryRegion nonclustered (AddressLine1, AddressLine2, City, StateProvince, PostalCode, CountryRegion); IX_Address_StateProvince nonclustered (StateProvince)

| # | Column | Type | Nullable | Identity | Computed | Default |
|---|---|---|---|---|---|---|
| 1 | AddressID | int | NO | yes |  |  |
| 2 | AddressLine1 | nvarchar(60) | NO |  |  |  |
| 3 | AddressLine2 | nvarchar(60) | YES |  |  |  |
| 4 | City | nvarchar(30) | NO |  |  |  |
| 5 | StateProvince | nvarchar(50) | NO |  |  |  |
| 6 | CountryRegion | nvarchar(50) | NO |  |  |  |
| 7 | PostalCode | nvarchar(15) | NO |  |  |  |
| 8 | rowguid | uniqueidentifier | NO |  |  | not visible to this login |
| 9 | ModifiedDate | datetime | NO |  |  | not visible to this login |

## [SalesLT].[Customer]

**Rows (estimate):** 847  
**Primary key:** PK_Customer_CustomerID (CustomerID)  
**Unique:** AK_Customer_rowguid (rowguid)  
**Foreign keys:** no foreign keys  
**Check constraints:** none  
**Indexes:** PK_Customer_CustomerID clustered (CustomerID); AK_Customer_rowguid nonclustered (rowguid); IX_Customer_EmailAddress nonclustered (EmailAddress)

| # | Column | Type | Nullable | Identity | Computed | Default |
|---|---|---|---|---|---|---|
| 1 | CustomerID | int | NO | yes |  |  |
| 2 | NameStyle | bit | NO |  |  | not visible to this login |
| 3 | Title | nvarchar(8) | YES |  |  |  |
| 4 | FirstName | nvarchar(50) | NO |  |  |  |
| 5 | MiddleName | nvarchar(50) | YES |  |  |  |
| 6 | LastName | nvarchar(50) | NO |  |  |  |
| 7 | Suffix | nvarchar(10) | YES |  |  |  |
| 8 | CompanyName | nvarchar(128) | YES |  |  |  |
| 9 | SalesPerson | nvarchar(256) | YES |  |  |  |
| 10 | EmailAddress | nvarchar(50) | YES |  |  |  |
| 11 | Phone | nvarchar(25) | YES |  |  |  |
| 12 | PasswordHash | varchar(128) | NO |  |  |  |
| 13 | PasswordSalt | varchar(10) | NO |  |  |  |
| 14 | rowguid | uniqueidentifier | NO |  |  | not visible to this login |
| 15 | ModifiedDate | datetime | NO |  |  | not visible to this login |

## [SalesLT].[CustomerAddress]

**Rows (estimate):** 417  
**Primary key:** PK_CustomerAddress_CustomerID_AddressID (CustomerID, AddressID)  
**Unique:** AK_CustomerAddress_rowguid (rowguid)  
**Foreign keys:** AddressID → SalesLT.Address.AddressID (FK_CustomerAddress_Address_AddressID); CustomerID → SalesLT.Customer.CustomerID (FK_CustomerAddress_Customer_CustomerID)  
**Check constraints:** none  
**Indexes:** PK_CustomerAddress_CustomerID_AddressID clustered (CustomerID, AddressID); AK_CustomerAddress_rowguid nonclustered (rowguid)

| # | Column | Type | Nullable | Identity | Computed | Default |
|---|---|---|---|---|---|---|
| 1 | CustomerID | int | NO |  |  |  |
| 2 | AddressID | int | NO |  |  |  |
| 3 | AddressType | nvarchar(50) | NO |  |  |  |
| 4 | rowguid | uniqueidentifier | NO |  |  | not visible to this login |
| 5 | ModifiedDate | datetime | NO |  |  | not visible to this login |

## [SalesLT].[Product]

**Rows (estimate):** 295  
**Primary key:** PK_Product_ProductID (ProductID)  
**Unique:** AK_Product_Name (Name); AK_Product_ProductNumber (ProductNumber); AK_Product_rowguid (rowguid)  
**Foreign keys:** ProductCategoryID → SalesLT.ProductCategory.ProductCategoryID (FK_Product_ProductCategory_ProductCategoryID); ProductModelID → SalesLT.ProductModel.ProductModelID (FK_Product_ProductModel_ProductModelID)  
**Check constraints:** CK_Product_ListPrice on ListPrice: not visible to this login; CK_Product_SellEndDate: not visible to this login; CK_Product_StandardCost on StandardCost: not visible to this login; CK_Product_Weight on Weight: not visible to this login  
**Indexes:** PK_Product_ProductID clustered (ProductID); AK_Product_Name nonclustered (Name); AK_Product_ProductNumber nonclustered (ProductNumber); AK_Product_rowguid nonclustered (rowguid)

| # | Column | Type | Nullable | Identity | Computed | Default |
|---|---|---|---|---|---|---|
| 1 | ProductID | int | NO | yes |  |  |
| 2 | Name | nvarchar(50) | NO |  |  |  |
| 3 | ProductNumber | nvarchar(25) | NO |  |  |  |
| 4 | Color | nvarchar(15) | YES |  |  |  |
| 5 | StandardCost | money | NO |  |  |  |
| 6 | ListPrice | money | NO |  |  |  |
| 7 | Size | nvarchar(5) | YES |  |  |  |
| 8 | Weight | decimal(8,2) | YES |  |  |  |
| 9 | ProductCategoryID | int | YES |  |  |  |
| 10 | ProductModelID | int | YES |  |  |  |
| 11 | SellStartDate | datetime | NO |  |  |  |
| 12 | SellEndDate | datetime | YES |  |  |  |
| 13 | DiscontinuedDate | datetime | YES |  |  |  |
| 14 | ThumbNailPhoto | varbinary(max) | YES |  |  |  |
| 15 | ThumbnailPhotoFileName | nvarchar(50) | YES |  |  |  |
| 16 | rowguid | uniqueidentifier | NO |  |  | not visible to this login |
| 17 | ModifiedDate | datetime | NO |  |  | not visible to this login |

## [SalesLT].[ProductCategory]

**Rows (estimate):** 41  
**Primary key:** PK_ProductCategory_ProductCategoryID (ProductCategoryID)  
**Unique:** AK_ProductCategory_Name (Name); AK_ProductCategory_rowguid (rowguid)  
**Foreign keys:** ParentProductCategoryID → SalesLT.ProductCategory.ProductCategoryID (FK_ProductCategory_ProductCategory_ParentProductCategoryID_ProductCategoryID)  
**Check constraints:** none  
**Indexes:** PK_ProductCategory_ProductCategoryID clustered (ProductCategoryID); AK_ProductCategory_Name nonclustered (Name); AK_ProductCategory_rowguid nonclustered (rowguid)

| # | Column | Type | Nullable | Identity | Computed | Default |
|---|---|---|---|---|---|---|
| 1 | ProductCategoryID | int | NO | yes |  |  |
| 2 | ParentProductCategoryID | int | YES |  |  |  |
| 3 | Name | nvarchar(50) | NO |  |  |  |
| 4 | rowguid | uniqueidentifier | NO |  |  | not visible to this login |
| 5 | ModifiedDate | datetime | NO |  |  | not visible to this login |

## [SalesLT].[ProductDescription]

**Rows (estimate):** 762  
**Primary key:** PK_ProductDescription_ProductDescriptionID (ProductDescriptionID)  
**Unique:** AK_ProductDescription_rowguid (rowguid)  
**Foreign keys:** no foreign keys  
**Check constraints:** none  
**Indexes:** PK_ProductDescription_ProductDescriptionID clustered (ProductDescriptionID); AK_ProductDescription_rowguid nonclustered (rowguid)

| # | Column | Type | Nullable | Identity | Computed | Default |
|---|---|---|---|---|---|---|
| 1 | ProductDescriptionID | int | NO | yes |  |  |
| 2 | Description | nvarchar(400) | NO |  |  |  |
| 3 | rowguid | uniqueidentifier | NO |  |  | not visible to this login |
| 4 | ModifiedDate | datetime | NO |  |  | not visible to this login |

## [SalesLT].[ProductModel]

**Rows (estimate):** 128  
**Primary key:** PK_ProductModel_ProductModelID (ProductModelID)  
**Unique:** AK_ProductModel_Name (Name); AK_ProductModel_rowguid (rowguid)  
**Foreign keys:** no foreign keys  
**Check constraints:** none  
**Indexes:** PK_ProductModel_ProductModelID clustered (ProductModelID); AK_ProductModel_Name nonclustered (Name); AK_ProductModel_rowguid nonclustered (rowguid); PXML_ProductModel_CatalogDescription xml (CatalogDescription)

| # | Column | Type | Nullable | Identity | Computed | Default |
|---|---|---|---|---|---|---|
| 1 | ProductModelID | int | NO | yes |  |  |
| 2 | Name | nvarchar(50) | NO |  |  |  |
| 3 | CatalogDescription | xml | YES |  |  |  |
| 4 | rowguid | uniqueidentifier | NO |  |  | not visible to this login |
| 5 | ModifiedDate | datetime | NO |  |  | not visible to this login |

## [SalesLT].[ProductModelProductDescription]

**Rows (estimate):** 762  
**Primary key:** PK_ProductModelProductDescription_ProductModelID_ProductDescriptionID_Culture (ProductModelID, ProductDescriptionID, Culture)  
**Unique:** AK_ProductModelProductDescription_rowguid (rowguid)  
**Foreign keys:** ProductDescriptionID → SalesLT.ProductDescription.ProductDescriptionID (FK_ProductModelProductDescription_ProductDescription_ProductDescriptionID); ProductModelID → SalesLT.ProductModel.ProductModelID (FK_ProductModelProductDescription_ProductModel_ProductModelID)  
**Check constraints:** none  
**Indexes:** PK_ProductModelProductDescription_ProductModelID_ProductDescriptionID_Culture clustered (ProductModelID, ProductDescriptionID, Culture); AK_ProductModelProductDescription_rowguid nonclustered (rowguid)

| # | Column | Type | Nullable | Identity | Computed | Default |
|---|---|---|---|---|---|---|
| 1 | ProductModelID | int | NO |  |  |  |
| 2 | ProductDescriptionID | int | NO |  |  |  |
| 3 | Culture | nchar(6) | NO |  |  |  |
| 4 | rowguid | uniqueidentifier | NO |  |  | not visible to this login |
| 5 | ModifiedDate | datetime | NO |  |  | not visible to this login |

## [SalesLT].[SalesOrderDetail]

**Rows (estimate):** 542  
**Primary key:** PK_SalesOrderDetail_SalesOrderID_SalesOrderDetailID (SalesOrderID, SalesOrderDetailID)  
**Unique:** AK_SalesOrderDetail_rowguid (rowguid)  
**Foreign keys:** ProductID → SalesLT.Product.ProductID (FK_SalesOrderDetail_Product_ProductID); SalesOrderID → SalesLT.SalesOrderHeader.SalesOrderID (FK_SalesOrderDetail_SalesOrderHeader_SalesOrderID)  
**Check constraints:** CK_SalesOrderDetail_OrderQty on OrderQty: not visible to this login; CK_SalesOrderDetail_UnitPrice on UnitPrice: not visible to this login; CK_SalesOrderDetail_UnitPriceDiscount on UnitPriceDiscount: not visible to this login  
**Indexes:** PK_SalesOrderDetail_SalesOrderID_SalesOrderDetailID clustered (SalesOrderID, SalesOrderDetailID); AK_SalesOrderDetail_rowguid nonclustered (rowguid); IX_SalesOrderDetail_ProductID nonclustered (ProductID)

| # | Column | Type | Nullable | Identity | Computed | Default |
|---|---|---|---|---|---|---|
| 1 | SalesOrderID | int | NO |  |  |  |
| 2 | SalesOrderDetailID | int | NO | yes |  |  |
| 3 | OrderQty | smallint | NO |  |  |  |
| 4 | ProductID | int | NO |  |  |  |
| 5 | UnitPrice | money | NO |  |  |  |
| 6 | UnitPriceDiscount | money | NO |  |  | not visible to this login |
| 7 | LineTotal | numeric(38,6) | NO |  | yes |  |
| 8 | rowguid | uniqueidentifier | NO |  |  | not visible to this login |
| 9 | ModifiedDate | datetime | NO |  |  | not visible to this login |

## [SalesLT].[SalesOrderHeader]

**Rows (estimate):** 32  
**Primary key:** PK_SalesOrderHeader_SalesOrderID (SalesOrderID)  
**Unique:** AK_SalesOrderHeader_rowguid (rowguid); AK_SalesOrderHeader_SalesOrderNumber (SalesOrderNumber)  
**Foreign keys:** BillToAddressID → SalesLT.Address.AddressID (FK_SalesOrderHeader_Address_BillTo_AddressID); ShipToAddressID → SalesLT.Address.AddressID (FK_SalesOrderHeader_Address_ShipTo_AddressID); CustomerID → SalesLT.Customer.CustomerID (FK_SalesOrderHeader_Customer_CustomerID)  
**Check constraints:** CK_SalesOrderHeader_DueDate: not visible to this login; CK_SalesOrderHeader_Freight on Freight: not visible to this login; CK_SalesOrderHeader_ShipDate: not visible to this login; CK_SalesOrderHeader_Status on Status: not visible to this login; CK_SalesOrderHeader_SubTotal on SubTotal: not visible to this login; CK_SalesOrderHeader_TaxAmt on TaxAmt: not visible to this login  
**Indexes:** PK_SalesOrderHeader_SalesOrderID clustered (SalesOrderID); AK_SalesOrderHeader_rowguid nonclustered (rowguid); AK_SalesOrderHeader_SalesOrderNumber nonclustered (SalesOrderNumber); IX_SalesOrderHeader_CustomerID nonclustered (CustomerID)

| # | Column | Type | Nullable | Identity | Computed | Default |
|---|---|---|---|---|---|---|
| 1 | SalesOrderID | int | NO | yes |  |  |
| 2 | RevisionNumber | tinyint | NO |  |  | not visible to this login |
| 3 | OrderDate | datetime | NO |  |  | not visible to this login |
| 4 | DueDate | datetime | NO |  |  |  |
| 5 | ShipDate | datetime | YES |  |  |  |
| 6 | Status | tinyint | NO |  |  | not visible to this login |
| 7 | OnlineOrderFlag | bit | NO |  |  | not visible to this login |
| 8 | SalesOrderNumber | nvarchar(25) | NO |  | yes |  |
| 9 | PurchaseOrderNumber | nvarchar(25) | YES |  |  |  |
| 10 | AccountNumber | nvarchar(15) | YES |  |  |  |
| 11 | CustomerID | int | NO |  |  |  |
| 12 | ShipToAddressID | int | YES |  |  |  |
| 13 | BillToAddressID | int | YES |  |  |  |
| 14 | ShipMethod | nvarchar(50) | NO |  |  |  |
| 15 | CreditCardApprovalCode | varchar(15) | YES |  |  |  |
| 16 | SubTotal | money | NO |  |  | not visible to this login |
| 17 | TaxAmt | money | NO |  |  | not visible to this login |
| 18 | Freight | money | NO |  |  | not visible to this login |
| 19 | TotalDue | money | NO |  | yes |  |
| 20 | Comment | nvarchar(max) | YES |  |  |  |
| 21 | rowguid | uniqueidentifier | NO |  |  | not visible to this login |
| 22 | ModifiedDate | datetime | NO |  |  | not visible to this login |

## Other objects

| Kind | Schema | Name | Detail |
|---|---|---|---|
| SQL_INLINE_TABLE_VALUED_FUNCTION | dbo | ufnGetCustomerInformation |  |
| SQL_TABLE_VALUED_FUNCTION | dbo | ufnGetAllCategories |  |
| trigger | SalesLT | iduSalesOrderDetail | SalesLT.SalesOrderDetail |
| trigger | SalesLT | uSalesOrderHeader | SalesLT.SalesOrderHeader |
| view | SalesLT | vGetAllCategories |  |
| view | SalesLT | vProductAndDescription |  |
| view | SalesLT | vProductModelCatalogDescription |  |
