-- ─────────────────────────────────────────────────────────────────────────────
-- 01_rfm_calculation.sql
-- Calculates R, F, M scores and assigns segments in pure SQL (SQLite).
-- Assumes table: transactions(InvoiceNo, InvoiceDate, CustomerID,
--                              Quantity, UnitPrice, Revenue)
-- ─────────────────────────────────────────────────────────────────────────────

-- Step 1: Raw RFM metrics per customer
WITH snapshot AS (
    SELECT DATE('2024-01-01') AS today
),
raw_rfm AS (
    SELECT
        t.CustomerID,
        CAST(julianday((SELECT today FROM snapshot))
             - julianday(MAX(t.InvoiceDate)) AS INTEGER)  AS recency_days,
        COUNT(DISTINCT t.InvoiceNo)                       AS frequency,
        ROUND(SUM(t.Revenue), 2)                          AS monetary
    FROM transactions t
    GROUP BY t.CustomerID
),

-- Step 2: Quintile boundaries using percentile approximation
--         SQLite lacks PERCENTILE_CONT, so we rank and bucket manually
ranked AS (
    SELECT
        CustomerID,
        recency_days,
        frequency,
        monetary,
        NTILE(5) OVER (ORDER BY recency_days DESC) AS r_tile,  -- DESC: lower = better
        NTILE(5) OVER (ORDER BY frequency ASC)     AS f_tile,
        NTILE(5) OVER (ORDER BY monetary ASC)      AS m_tile
    FROM raw_rfm
),

-- Step 3: Assign 1–5 scores (5 = best)
scored AS (
    SELECT
        CustomerID,
        recency_days,
        frequency,
        monetary,
        (6 - r_tile) AS R,   -- invert: tile 1 (highest recency) → score 5
        f_tile        AS F,
        m_tile        AS M,
        CAST((6 - r_tile) AS TEXT)
            || CAST(f_tile AS TEXT)
            || CAST(m_tile AS TEXT)  AS rfm_score,
        (6 - r_tile) + f_tile + m_tile AS rfm_total
    FROM ranked
),

-- Step 4: Segment assignment
segmented AS (
    SELECT
        *,
        CASE
            WHEN R >= 4 AND F >= 4                      THEN 'Champions'
            WHEN R >= 3 AND F >= 3                      THEN 'Loyal Customers'
            WHEN R >= 4 AND F <= 2                      THEN 'New Customers'
            WHEN R <= 2 AND F >= 3                      THEN 'At Risk'
            WHEN R <= 2 AND F <= 2 AND M >= 3           THEN 'Cannot Lose Them'
            WHEN R <= 2 AND F <= 2                      THEN 'Lost'
            ELSE                                             'Potential Loyalists'
        END AS segment
    FROM scored
)

SELECT * FROM segmented ORDER BY rfm_total DESC;
