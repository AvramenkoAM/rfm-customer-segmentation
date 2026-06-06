-- ─────────────────────────────────────────────────────────────────────────────
-- 03_at_risk_customers.sql
-- Identifies customers who need immediate attention:
--   At Risk, Cannot Lose Them, and high-value customers with declining recency.
-- ─────────────────────────────────────────────────────────────────────────────

-- At Risk customers sorted by revenue (prioritise high-value first)
SELECT
    CustomerID,
    recency_days,
    frequency,
    ROUND(monetary, 2) AS total_spend,
    segment
FROM rfm_scored
WHERE segment IN ('At Risk', 'Cannot Lose Them')
ORDER BY monetary DESC
LIMIT 50;


-- Champions with rising recency (at risk of dropping to Loyal or lower)
-- Defines "rising recency" as > 90 days since last purchase
SELECT
    CustomerID,
    recency_days,
    frequency,
    ROUND(monetary, 2) AS total_spend,
    R, F, M,
    rfm_score
FROM rfm_scored
WHERE segment = 'Champions'
  AND recency_days > 90
ORDER BY recency_days DESC;


-- Win-back priority list: lost customers with historically high spend
SELECT
    CustomerID,
    recency_days,
    frequency,
    ROUND(monetary, 2) AS total_spend,
    segment
FROM rfm_scored
WHERE segment = 'Lost'
  AND monetary > (SELECT AVG(monetary) FROM rfm_scored)
ORDER BY monetary DESC
LIMIT 30;


-- Segment migration risk summary
-- Shows how many customers are within 1 score point of dropping to a worse segment
SELECT
    segment,
    COUNT(*) AS total_customers,
    SUM(CASE WHEN R = 3 AND segment = 'Champions' THEN 1 ELSE 0 END) AS champions_at_r3,
    SUM(CASE WHEN R = 2 THEN 1 ELSE 0 END)                          AS low_recency_count
FROM rfm_scored
GROUP BY segment
ORDER BY low_recency_count DESC;
