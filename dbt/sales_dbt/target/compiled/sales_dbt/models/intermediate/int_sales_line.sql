WITH s AS (
  SELECT *
  FROM "sales_dw"."analytics"."stg_sales_data"
),
z AS (
  SELECT *
  FROM "sales_dw"."analytics"."stg_zip_code"
),
m AS (
  SELECT *
  FROM "sales_dw"."analytics"."stg_regional_mgr"
)

SELECT
  s.order_id,
  s.order_date,
  s.segment,
  s.postal_code,

  z.city,
  z.state,
  z.country,
  z.region,
  m.regional_manager,

  s.product_id,
  s.category,
  s.sub_category,
  s.product_name,

  s.quantity_sold,

  (s.sales_price_per_item * s.quantity_sold)::numeric(14,2)  AS sales_amount,
  (s.profit_per_item * s.quantity_sold)::numeric(14,2)       AS profit_amount,
  (s.cogs_per_item * s.quantity_sold)::numeric(14,2)         AS cogs_amount,

  CASE
    WHEN (s.sales_price_per_item * s.quantity_sold) = 0 THEN 0
    ELSE ROUND(
      ((s.profit_per_item * s.quantity_sold) / (s.sales_price_per_item * s.quantity_sold))::numeric
    , 4)
  END AS profit_margin

FROM s
LEFT JOIN z ON s.postal_code = z.postal_code
LEFT JOIN m ON z.region = m.region