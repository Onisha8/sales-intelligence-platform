SELECT
  order_date,
  region,
  regional_manager,

  SUM(sales_amount)  AS total_sales,
  SUM(profit_amount) AS total_profit,
  SUM(cogs_amount)   AS total_cogs,
  SUM(quantity_sold) AS total_units,
  COUNT(DISTINCT order_id) AS orders,

  CASE
    WHEN SUM(sales_amount) = 0 THEN 0
    ELSE ROUND((SUM(profit_amount) / SUM(sales_amount))::numeric, 4)
  END AS profit_margin

FROM {{ ref('int_sales_line') }}
GROUP BY 1, 2, 3
ORDER BY 1, 2
