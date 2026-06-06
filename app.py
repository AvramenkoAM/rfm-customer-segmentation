import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from pathlib import Path

# ── Config ────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="RFM Customer Segmentation",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded",
)

ROOT     = Path(__file__).parent
SNAPSHOT = pd.Timestamp("2024-01-01")

COLORS = {
    "Champions":          "#2a9d8f",
    "Loyal Customers":    "#264653",
    "Potential Loyalists":"#e9c46a",
    "New Customers":      "#f4a261",
    "At Risk":            "#e76f51",
    "Cannot Lose Them":   "#c77dff",
    "Lost":               "#adb5bd",
}

ACTION = {
    "Champions":           "Reward · early access · ask for reviews",
    "Loyal Customers":     "Upsell · birthday voucher",
    "Potential Loyalists": "Limited-time offer for 2nd purchase",
    "New Customers":       "Onboarding email · 10% off next order",
    "At Risk":             "Win-back: £15 off · sense of urgency",
    "Cannot Lose Them":    "Personal outreach · high-value offer",
    "Lost":                "Last-chance email · accept churn if no reply",
}


# ── Data ──────────────────────────────────────────────────────────────────────
@st.cache_data
def load():
    df = pd.read_csv(
        ROOT / "data" / "retail_transactions.csv",
        parse_dates=["InvoiceDate"],
    )
    rfm = (
        df.groupby("CustomerID")
        .agg(
            last_purchase=("InvoiceDate", "max"),
            frequency    =("InvoiceNo",   "nunique"),
            monetary     =("Revenue",     "sum"),
        )
        .reset_index()
    )
    rfm["recency"] = (SNAPSHOT - rfm["last_purchase"]).dt.days
    rfm = rfm.drop(columns="last_purchase")

    rfm["R"] = pd.qcut(rfm["recency"],                       q=5, labels=[5,4,3,2,1]).astype(int)
    rfm["F"] = pd.qcut(rfm["frequency"].rank(method="first"),q=5, labels=[1,2,3,4,5]).astype(int)
    rfm["M"] = pd.qcut(rfm["monetary"],                      q=5, labels=[1,2,3,4,5]).astype(int)

    rfm["rfm_score"] = rfm["R"].astype(str)+rfm["F"].astype(str)+rfm["M"].astype(str)
    rfm["rfm_total"] = rfm["R"] + rfm["F"] + rfm["M"]

    def seg(row):
        r, f, m = row["R"], row["F"], row["M"]
        if r >= 4 and f >= 4:               return "Champions"
        if r >= 3 and f >= 3:               return "Loyal Customers"
        if r >= 4 and f <= 2:               return "New Customers"
        if r <= 2 and f >= 3:               return "At Risk"
        if r <= 2 and f <= 2 and m >= 3:    return "Cannot Lose Them"
        if r <= 2 and f <= 2:               return "Lost"
        return "Potential Loyalists"

    rfm["segment"] = rfm.apply(seg, axis=1)
    return df, rfm


df, rfm = load()

summary = (
    rfm.groupby("segment")
    .agg(customers=("CustomerID","count"), avg_recency=("recency","mean"),
         avg_frequency=("frequency","mean"), avg_monetary=("monetary","mean"),
         total_revenue=("monetary","sum"))
    .sort_values("total_revenue", ascending=False)
    .round(1)
)
summary["revenue_share"] = summary["total_revenue"] / summary["total_revenue"].sum()


# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🎯 RFM Analytics")
    st.caption("UK Retail · 2022–2023 · 2 500 customers")
    st.divider()
    page = st.radio(
        "Go to",
        ["Overview", "Segments", "Customer Explorer", "Action Plan"],
        label_visibility="collapsed",
    )
    st.divider()
    seg_filter = st.multiselect(
        "Filter segments",
        options=list(COLORS),
        default=list(COLORS),
    )
    st.caption("Stack: Python · SQL · Streamlit · Plotly")


rfm_f = rfm[rfm["segment"].isin(seg_filter)]


# ══════════════════════════════════════════════════════════════════════════════
# OVERVIEW
# ══════════════════════════════════════════════════════════════════════════════
if page == "Overview":
    st.header("Customer Overview")

    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Customers",       f"{len(rfm):,}")
    c2.metric("Total Revenue",   f"£{df['Revenue'].sum():,.0f}")
    c3.metric("Avg Order Value", f"£{df.groupby('InvoiceNo')['Revenue'].sum().mean():.2f}")
    c4.metric("Avg Purchases",   f"{rfm['frequency'].mean():.1f}")
    c5.metric("Avg Recency",     f"{rfm['recency'].mean():.0f} days")

    st.divider()
    l, r = st.columns([1, 1])

    with l:
        st.subheader("Customers per Segment")
        seg_n = rfm_f["segment"].value_counts().reset_index()
        seg_n.columns = ["segment", "count"]
        fig = px.bar(
            seg_n.sort_values("count"),
            x="count", y="segment", orientation="h",
            color="segment", color_discrete_map=COLORS,
            labels={"count": "Customers", "segment": ""},
        )
        fig.update_layout(showlegend=False, margin=dict(l=0,r=0,t=20,b=0))
        st.plotly_chart(fig, use_container_width=True)

    with r:
        st.subheader("Revenue Share by Segment")
        rev_share = summary.reset_index()[["segment","revenue_share"]].copy()
        rev_share = rev_share[rev_share["segment"].isin(seg_filter)]
        fig = px.pie(
            rev_share, names="segment", values="revenue_share",
            hole=0.5, color="segment", color_discrete_map=COLORS,
        )
        fig.update_traces(textposition="inside", textinfo="percent+label")
        fig.update_layout(showlegend=False, margin=dict(l=0,r=0,t=20,b=0))
        st.plotly_chart(fig, use_container_width=True)

    st.divider()
    st.subheader("Monthly Revenue")
    monthly = df.groupby(df["InvoiceDate"].dt.to_period("M"))["Revenue"].sum().reset_index()
    monthly["InvoiceDate"] = monthly["InvoiceDate"].dt.to_timestamp()
    fig = px.area(monthly, x="InvoiceDate", y="Revenue",
                  labels={"InvoiceDate":"","Revenue":"Revenue (£)"},
                  color_discrete_sequence=["#2a9d8f"])
    fig.update_traces(line_width=2, fillcolor="rgba(42,157,143,0.15)")
    fig.update_layout(margin=dict(l=0,r=0,t=20,b=0))
    st.plotly_chart(fig, use_container_width=True)


# ══════════════════════════════════════════════════════════════════════════════
# SEGMENTS
# ══════════════════════════════════════════════════════════════════════════════
elif page == "Segments":
    st.header("Segment Analysis")

    disp = summary.loc[summary.index.isin(seg_filter)].copy()
    disp["revenue_share"] = (disp["revenue_share"] * 100).round(1).astype(str) + "%"
    disp.columns = ["Customers","Avg Recency (days)","Avg Frequency",
                    "Avg Spend (£)","Total Revenue (£)","Revenue Share"]
    st.dataframe(disp, use_container_width=True)

    st.divider()
    l, r = st.columns(2)

    with l:
        st.subheader("Avg Recency by Segment (days)")
        avg_r = rfm_f.groupby("segment")["recency"].mean().sort_values()
        fig = px.bar(avg_r.reset_index(), x="recency", y="segment",
                     orientation="h", color="segment", color_discrete_map=COLORS,
                     labels={"recency":"Avg Recency (days)","segment":""})
        fig.update_layout(showlegend=False, margin=dict(l=0,r=0,t=20,b=0))
        st.plotly_chart(fig, use_container_width=True)

    with r:
        st.subheader("Avg Monetary by Segment (£)")
        avg_m = rfm_f.groupby("segment")["monetary"].mean().sort_values()
        fig = px.bar(avg_m.reset_index(), x="monetary", y="segment",
                     orientation="h", color="segment", color_discrete_map=COLORS,
                     labels={"monetary":"Avg Total Spend (£)","segment":""})
        fig.update_layout(showlegend=False, margin=dict(l=0,r=0,t=20,b=0))
        st.plotly_chart(fig, use_container_width=True)

    st.divider()
    st.subheader("R × F Heatmap — Average Spend (£)")
    heat = rfm_f.pivot_table(index="R", columns="F", values="monetary", aggfunc="mean")
    fig = px.imshow(
        heat, text_auto=".0f", color_continuous_scale="YlGn",
        labels={"x":"Frequency Score","y":"Recency Score","color":"Avg Spend (£)"},
        aspect="auto",
    )
    fig.update_layout(margin=dict(l=0,r=0,t=30,b=0))
    st.plotly_chart(fig, use_container_width=True)


# ══════════════════════════════════════════════════════════════════════════════
# CUSTOMER EXPLORER
# ══════════════════════════════════════════════════════════════════════════════
elif page == "Customer Explorer":
    st.header("Customer Explorer")

    sample = rfm_f.sample(min(2000, len(rfm_f)), random_state=42)
    fig = px.scatter(
        sample,
        x="recency", y="monetary",
        color="segment", size="frequency",
        size_max=20, opacity=0.65,
        color_discrete_map=COLORS,
        hover_data=["CustomerID","frequency","rfm_score"],
        labels={"recency":"Recency (days)","monetary":"Total Spend (£)"},
        title="Recency vs Total Spend — bubble size = purchase frequency",
    )
    fig.update_layout(height=520, margin=dict(l=0,r=0,t=40,b=0))
    st.plotly_chart(fig, use_container_width=True)

    st.divider()
    st.subheader("Customer Search")
    cid = st.number_input("Customer ID", min_value=int(rfm["CustomerID"].min()),
                          max_value=int(rfm["CustomerID"].max()),
                          value=int(rfm["CustomerID"].iloc[0]))
    row = rfm[rfm["CustomerID"] == cid]
    if len(row):
        r = row.iloc[0]
        c1,c2,c3,c4,c5 = st.columns(5)
        c1.metric("Segment",   r["segment"])
        c2.metric("Recency",   f"{r['recency']} days")
        c3.metric("Frequency", f"{r['frequency']} orders")
        c4.metric("Monetary",  f"£{r['monetary']:.2f}")
        c5.metric("RFM Score", r["rfm_score"])

        hist = df[df["CustomerID"]==cid].groupby(
            df[df["CustomerID"]==cid]["InvoiceDate"].dt.to_period("M")
        )["Revenue"].sum().reset_index()
        hist["InvoiceDate"] = hist["InvoiceDate"].dt.to_timestamp()
        fig2 = px.bar(hist, x="InvoiceDate", y="Revenue",
                      labels={"InvoiceDate":"","Revenue":"Revenue (£)"},
                      title=f"Purchase history — Customer {cid}",
                      color_discrete_sequence=["#2a9d8f"])
        st.plotly_chart(fig2, use_container_width=True)


# ══════════════════════════════════════════════════════════════════════════════
# ACTION PLAN
# ══════════════════════════════════════════════════════════════════════════════
elif page == "Action Plan":
    st.header("Marketing Action Plan")

    rows = []
    for seg, row in summary.iterrows():
        if seg not in seg_filter:
            continue
        rows.append({
            "Segment":       seg,
            "Customers":     int(row["customers"]),
            "Revenue Share": f"{row['revenue_share']*100:.1f}%",
            "Avg Spend (£)": f"£{row['avg_monetary']:.2f}",
            "Avg Recency":   f"{row['avg_recency']:.0f} days",
            "Action":        ACTION.get(seg, "—"),
        })
    st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

    st.divider()
    st.subheader("Priority Matrix")
    fig = px.scatter(
        summary.reset_index(),
        x="avg_recency", y="avg_monetary",
        size="customers", color="segment",
        size_max=50, color_discrete_map=COLORS,
        text="segment",
        labels={"avg_recency":"Avg Recency (days)","avg_monetary":"Avg Spend (£)"},
        title="Segment Priority: Recency vs Spend  (bubble = customers)",
    )
    fig.update_traces(textposition="top center")
    fig.update_layout(showlegend=False, height=500, margin=dict(l=0,r=0,t=40,b=0))
    st.plotly_chart(fig, use_container_width=True)

    st.info(
        "**Re-score monthly.** Segment movement is the key signal: "
        "Champions moving toward At Risk need immediate attention before they are lost."
    )
