SELECT
  CAST("Region" AS text) AS region,
  CAST("Person" AS text) AS regional_manager
FROM {{ source('raw', 'regional_mgr') }}