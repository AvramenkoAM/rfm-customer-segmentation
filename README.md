# RFM Customer Segmentation

Portfolio data analytics project demonstrating customer segmentation using the RFM framework on a synthetic UK-style retail dataset.

## Business Problem

Marketing budget is limited. The business needs to know which customers deserve a loyalty reward, which are about to churn, and where not to spend money. RFM answers this with three measurable metrics — no ML required.

| Metric | Definition | Higher = |
| --- | --- | --- |
| **R**ecency | Days since last purchase | More engaged |
| **F**requency | Unique invoice count | More loyal |
| **M**onetary | Total spend (£) | More valuable |

## Executive Snapshot

| Metric | Value |
| --- | ---: |
| Customers | 2,500 |
| Transactions | 19,600+ |
| Date range | Jan 2022 – Dec 2023 |
| Avg purchases per customer | ~3.8 |
| Top 20% customers → revenue | ~80% |

## Live Dashboard

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

Deploy to [Streamlit Cloud](https://streamlit.io/cloud): connect this repo, set `app.py` as entry point.

## Repository Structure

```text
.
├── app.py                          # Streamlit dashboard (4 pages)
├── data/
│   ├── retail_transactions.csv     # Synthetic dataset (committed)
│   └── generate_retail_data.py     # Reproduces the dataset from scratch
├── notebooks/
│   ├── 01_data_exploration.ipynb   # EDA: distributions, seasonality, Pareto
│   └── 02_rfm_analysis.ipynb       # RFM scoring, segments, action plan
├── sql/
│   ├── 01_rfm_calculation.sql      # RFM scoring in pure SQL (NTILE + CASE)
│   ├── 02_segment_revenue.sql      # Segment KPIs + Pareto analysis
│   └── 03_at_risk_customers.sql    # Win-back + VIP-at-risk lists
├── images/                         # Exported charts
├── .streamlit/config.toml          # Dashboard theme
├── README.md
└── requirements.txt
```

## Portfolio Deliverables

| Deliverable | Description |
| --- | --- |
| [Streamlit dashboard](app.py) | 4 pages: Overview, Segments, Customer Explorer, Action Plan |
| [EDA notebook](notebooks/01_data_exploration.ipynb) | Distributions, seasonality, Pareto check |
| [RFM analysis notebook](notebooks/02_rfm_analysis.ipynb) | Full scoring pipeline, heatmaps, segment action plan |
| [SQL: RFM calculation](sql/01_rfm_calculation.sql) | NTILE-based quintile scoring with segment CASE logic |
| [SQL: segment revenue](sql/02_segment_revenue.sql) | Revenue share + Pareto by decile |
| [SQL: at-risk customers](sql/03_at_risk_customers.sql) | Win-back priority lists, migration risk |
| [Data generator](data/generate_retail_data.py) | Reproducible synthetic dataset with Pareto activity distribution |

## RFM Segments & Actions

| Segment | R | F | Marketing Action |
| --- | --- | --- | --- |
| Champions | ≥4 | ≥4 | Reward, early access, ask for reviews |
| Loyal Customers | ≥3 | ≥3 | Upsell premium, birthday voucher |
| Potential Loyalists | 3–4 | 1–2 | Limited-time offer for 2nd purchase |
| New Customers | ≥4 | ≤2 | Onboarding flow, 10% off next order |
| At Risk | ≤2 | ≥3 | Win-back: £15 off, urgency messaging |
| Cannot Lose Them | ≤2 | ≤2 | High M | Personal outreach, high-value offer |
| Lost | ≤2 | ≤2 | Low M | Last-chance email, accept churn |

## Key Insights

- Top 20% of customers generate ~80% of revenue — confirms Pareto distribution
- Strong Q4 seasonality: Nov–Dec revenue is 35% above monthly average
- "At Risk" segment represents recovered revenue if win-back campaign converts 20–25%
- Champions have disproportionately high AOV — protecting them is the highest-ROI action

## How to Run

```bash
# 1. Create environment
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# 2. (Optional) Regenerate the dataset
python data/generate_retail_data.py

# 3. Run notebooks in order
jupyter notebook

# 4. Launch dashboard
streamlit run app.py
```

## Skills Demonstrated

- RFM framework and customer lifecycle analysis
- Quintile-based scoring with pandas `qcut` and SQL `NTILE`
- Customer segmentation with business-driven segment rules
- Interactive dashboard development (Streamlit + Plotly)
- Synthetic data generation with realistic statistical distributions
- SQL window functions for ranking and revenue share analysis
- Translating segment data into prioritised marketing actions
