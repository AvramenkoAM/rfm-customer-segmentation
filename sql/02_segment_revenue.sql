-- ─────────────────────────────────────────────────────────────────────────────
-- 02_segment_revenue.sql
-- Segment-level KPIs and revenue share analysis.
-- Run after 01_rfm_calculation.sql or against rfm_scored view.
-- ─────────────────────────────────────────────────────────────────────────────

-- Segment summary: size, average metrics, revenue share
WITH rfm AS (/* paste output of 01_rfm_calculation.sql or use a view */
    SELECT CustomerID, recency_days, frequency, monetary, segment
    FROM rfm_scored   -- replace with actual table/view name
),
totals AS (
    SELECT SUM(monetary) AS total_revenue FROM rfm
)
SELECT
    segment,
    COUNT(*)                                                AS customers,
    ROUND(AVG(recency_days), 1)                            AS avg_recency_days,
    ROUND(AVG(frequency), 2)                               AS avg_frequency,
    ROUND(AVG(monetary), 2)                                AS avg_monetary,
    ROUND(SUM(monetary), 2)                                AS total_revenue,
    ROUND(100.0 * SUM(monetary) / (SELECT total_revenue FROM totals), 2) AS revenue_share_pct
FROM rfm
GROUP BY segment
ORDER BY total_revenue DESC;


-- Top 20 customers by total spend (for VIP list)
SELECT
    CustomerID,
    recency_days,
    frequency,
    ROUND(monetary, 2) AS total_spend,
    segment
FROM rfm_scored
ORDER BY monetary DESC
LIMIT 20;


-- Pareto check: cumulative revenue share by customer decile
WITH ranked AS (
    SELECT
        CustomerID,
        monetary,
        NTILE(10) OVER (ORDER BY monetary DESC) AS decile
    FROM rfm_scored
)
SELECT
    decile,
    COUNT(*)                                                   AS customers,
    ROUND(SUM(monetary), 2)                                    AS decile_revenue,
    ROUND(100.0 * SUM(monetary) / SUM(SUM(monetary)) OVER (), 2) AS share_pct,
    ROUND(100.0 * SUM(SUM(monetary)) OVER (ORDER BY decile)
          / SUM(SUM(monetary)) OVER (), 2)                     AS cumulative_pct
FROM ranked
GROUP BY decile
ORDER BY decile;
