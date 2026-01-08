
  create view "sales_dw"."analytics"."stg_sales_data__dbt_tmp"
    
    
  as (
    SELECT
  CAST("Order Number" AS text)            AS order_id,
  CAST("Order Date" AS date)              AS order_date,
  CAST("Segment" AS text)                 AS segment,
  CAST("Postal Code" AS text)             AS postal_code,
  CAST("Product ID" AS text)              AS product_id,
  CAST("Category" AS text)                AS category,
  CAST("Sub-Category" AS text)            AS sub_category,
  CAST("Product Name" AS text)            AS product_name,
  CAST("Sales Price per item" AS numeric) AS sales_price_per_item,
  CAST("Profit per Item" AS numeric)      AS profit_per_item,
  CAST("COGS" AS numeric)                 AS cogs_per_item,
  CAST("Quantity Sold" AS integer)        AS quantity_sold
FROM "sales_dw"."raw"."sales_data"
  );