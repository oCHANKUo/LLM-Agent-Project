# db_schema.py

TABLE_SCHEMAS = {
    "DimCustomer": [
        "CustomerKey INT",
        "FirstName NVARCHAR(50)",
        "LastName NVARCHAR(50)",
        "Email NVARCHAR(100)"
    ],
    "DimProduct": [
        "ProductKey INT",
        "ProductName NVARCHAR(100)",
        "CategoryName NVARCHAR(50)"
    ],
    "DimSalesPerson": [
        "SalesPersonKey INT",
        "FirstName NVARCHAR(50)",
        "LastName NVARCHAR(50)",
        "Email NVARCHAR(100)"
    ],
    "DimDate": [
        "DateKey INT",
        "Date NVARCHAR(10)",
        "Month NVARCHAR(20)",
        "Year INT"
    ],
    "DimTerritory": [
        "TerritoryKey INT",
        "Region NVARCHAR(50)",
        "Country NVARCHAR(50)"
    ],
    "FactSalesOrderDetail": [
        "SalesOrderDetailKey INT",
        "SalesOrderKey INT",
        "ProductKey INT",
        "OrderQty INT",
        "UnitPrice DECIMAL(10,2)"
    ]
}