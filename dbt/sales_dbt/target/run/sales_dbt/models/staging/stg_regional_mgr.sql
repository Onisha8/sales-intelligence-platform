
  create view "sales_dw"."analytics"."stg_regional_mgr__dbt_tmp"
    
    
  as (
    SELECT
  CAST("Region" AS text) AS region,
  CAST("Person" AS text) AS regional_manager
FROM "sales_dw"."raw"."regional_mgr"
  );