WITH z AS (
  SELECT
    CAST("Postal Code" AS text) AS postal_code,
    CAST("City" AS text)        AS city,
    CAST("State" AS text)       AS state,
    CAST("Country" AS text)     AS country,
    CAST("Region" AS text)      AS region
  FROM {{ source('raw', 'zip_code') }}
  WHERE "Postal Code" IS NOT NULL
),
ranked AS (
  SELECT
    *,
    ROW_NUMBER() OVER (
      PARTITION BY postal_code
      ORDER BY
        region NULLS LAST,
        state NULLS LAST,
        city NULLS LAST
    ) AS rn
  FROM z
)
SELECT
  postal_code,
  city,
  state,
  country,
  region
FROM ranked
WHERE rn = 1
