"""
Synthetic retail dataset generator.
Produces a CSV that mirrors Online Retail II structure.
Run once: python data/generate_retail_data.py
"""
import numpy as np
import pandas as pd
from pathlib import Path

np.random.seed(42)

# ── Parameters ────────────────────────────────────────────────────────────────
N_CUSTOMERS  = 2_500
N_PRODUCTS   = 400
START        = pd.Timestamp("2022-01-01")
END          = pd.Timestamp("2023-12-31")
DAYS_TOTAL   = (END - START).days

CATEGORIES = [
    "Home & Garden", "Electronics", "Clothing", "Books",
    "Sports & Outdoors", "Beauty", "Toys", "Food & Grocery",
    "Automotive", "Office", "Health", "Music",
    "Pet Supplies", "Jewelry", "Tools", "Baby",
]

COUNTRIES = {
    "United Kingdom": 0.58,
    "Germany":        0.14,
    "France":         0.12,
    "Spain":          0.08,
    "Netherlands":    0.08,
}

# ── Product catalogue ─────────────────────────────────────────────────────────
products = pd.DataFrame({
    "ProductID": [f"P{i:04d}" for i in range(N_PRODUCTS)],
    "Category":  np.random.choice(CATEGORIES, N_PRODUCTS),
    "UnitPrice": np.clip(
        np.random.lognormal(mean=2.9, sigma=0.85, size=N_PRODUCTS).round(2),
        0.49, 849.99,
    ),
})

# ── Customer activity weights (Pareto 80/20) ──────────────────────────────────
raw_weights = np.random.pareto(a=1.5, size=N_CUSTOMERS)
activity    = (raw_weights / raw_weights.max()).clip(0.01, 1.0)
customer_ids = np.arange(10001, 10001 + N_CUSTOMERS)

# ── Generate transactions ─────────────────────────────────────────────────────
records = []
invoice_counter = 500000

for idx, cid in enumerate(customer_ids):
    # Customers acquired randomly during the first 18 months
    acq_offset = int(np.random.randint(0, min(540, DAYS_TOTAL)))
    n_invoices = max(2, int(activity[idx] * 80) + np.random.poisson(3))
    country    = np.random.choice(list(COUNTRIES), p=list(COUNTRIES.values()))

    for _ in range(n_invoices):
        inv_offset = acq_offset + int(np.random.randint(0, max(1, DAYS_TOTAL - acq_offset)))
        if inv_offset > DAYS_TOTAL:
            continue
        inv_date = START + pd.Timedelta(days=inv_offset)

        # Seasonal multiplier: Q4 boost, summer dip
        month = inv_date.month
        seasonal = 1.35 if month in (11, 12) else 0.85 if month in (7, 8) else 1.0

        invoice_no = f"C{invoice_counter}"
        invoice_counter += 1
        n_items = int(np.clip(np.random.lognormal(0.7, 0.6), 1, 15))
        chosen  = products.sample(n=min(n_items, N_PRODUCTS))

        for _, prod in chosen.iterrows():
            qty   = int(np.random.randint(1, 7))
            price = round(prod["UnitPrice"] * seasonal + np.random.uniform(-0.5, 0.5), 2)
            price = max(0.49, price)
            records.append({
                "InvoiceNo":   invoice_no,
                "InvoiceDate": inv_date.strftime("%Y-%m-%d"),
                "CustomerID":  cid,
                "Country":     country,
                "StockCode":   prod["ProductID"],
                "Category":    prod["Category"],
                "Quantity":    qty,
                "UnitPrice":   price,
            })

# ── Save ──────────────────────────────────────────────────────────────────────
df = (
    pd.DataFrame(records)
    .sort_values("InvoiceDate")
    .reset_index(drop=True)
)
df["Revenue"] = (df["Quantity"] * df["UnitPrice"]).round(2)

out = Path(__file__).parent / "retail_transactions.csv"
df.to_csv(out, index=False)
print(f"Saved {len(df):,} rows · {df['CustomerID'].nunique():,} customers · {df['InvoiceNo'].nunique():,} invoices")
print(f"→ {out}")
