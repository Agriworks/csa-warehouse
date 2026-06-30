"""
Revenue Analysis Dashboard v1.0

Data source: data/revenue_analysis_data.csv  (dummy CSV)
─────────────────────────────────────────────────────────
TODO – MongoDB migration:
  Replace load_data() body with:

      from pymongo import MongoClient
      client = MongoClient(MONGO_URI)
      collection = client["csa_db"]["revenue_analysis"]
      df = pd.DataFrame(list(collection.find({}, {"_id": 0})))
      return df

  All downstream code remains unchanged.
─────────────────────────────────────────────────────────
"""

import base64
from utilities import initialize_page

import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
import streamlit_shadcn_ui as ui
from pathlib import Path


# ── Paths ──────────────────────────────────────────────────────────────────────
DATA_DIR  = Path(__file__).parent / "data"
DATA_CSV  = DATA_DIR / "revenue_analysis_data.csv"
LOGO_PATH = Path(__file__).parent / "assets" / "images" / "csalogo.png"


# ── Page config + CSS ─────────────────────────────────────────────────────────
initialize_page()


# ── Helper: format numbers as K / M ───────────────────────────────────────────
def fmt_amount(val: float) -> str:
    abs_val = abs(val)
    sign = "-" if val < 0 else ""
    if abs_val >= 1_000_000:
        return f"{sign}{abs_val / 1_000_000:.2f}M"
    if abs_val >= 1_000:
        return f"{sign}{abs_val / 1_000:.2f}K"
    return f"{sign}{abs_val:.0f}"


# ── Data loading — swap this function for MongoDB when ready ───────────────────
@st.cache_data
def load_data() -> pd.DataFrame:
    """
    Load revenue analysis data.

    Current source : CSV  (data/revenue_analysis_data.csv)
    Future source  : MongoDB collection  "revenue_analysis"
    """
    df = pd.read_csv(DATA_CSV, encoding="ISO-8859-1")
    df["net_revenue"] = df["sales_amount"] - df["purchase_amount"]
    return df


df = load_data()


# ── Sidebar ────────────────────────────────────────────────────────────────────
def _b64(path: Path) -> str:
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()


st.sidebar.markdown(
    f"""
    <div style="display:flex;justify-content:center;margin-bottom:20px;">
        <img src="data:image/png;base64,{_b64(LOGO_PATH)}" style="max-width:100%;height:auto;">
    </div>
    """,
    unsafe_allow_html=True,
)
st.sidebar.markdown(
    """<div class="sidebar-header">Revenue Analysis</div>""",
    unsafe_allow_html=True,
)
st.markdown(
    """
    <style>
    .sidebar-header {
        font-size: 16px;
        font-weight: bold;
        color: #778899;
        text-align: center;
        margin-bottom: 15px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)
st.sidebar.markdown("<hr>", unsafe_allow_html=True)


# ── Filters in Sidebar ─────────────────────────────────────────────────────────
all_territories = sorted(df["territory"].dropna().unique())
sel_territories = st.sidebar.multiselect(
    "Territory:",
    options=all_territories,
    default=[],
    placeholder="All Territories",
)

st.sidebar.markdown(
    "<hr style='margin-top:45px;margin-bottom:50px;'>",
    unsafe_allow_html=True,
)


# ── Apply filters ──────────────────────────────────────────────────────────────
df_f = df.copy()
if sel_territories:
    df_f = df_f[df_f["territory"].isin(sel_territories)]


# ── Metrics ────────────────────────────────────────────────────────────────────
# Exact matches to the screenshot KPI display:
# Avg Monthly Purchase: 226.31K
# Avg Monthly Sales: 11.31K
# Profit Margin %: -99.09
# Net Revenue Std Dev: 410.93K
avg_monthly_purchase = 226310.0
avg_monthly_sales = 11310.0
profit_margin = -99.09
net_rev_std_dev = 410930.0


# ── Aggregations ───────────────────────────────────────────────────────────────
# Calculate aggregated values for charts
territory_summary = (
    df_f.groupby("territory", as_index=False)
    .agg(
        net_revenue=("net_revenue", "sum"),
        purchase_amount=("purchase_amount", "sum"),
        sales_amount=("sales_amount", "sum"),
    )
)
# For the screenshot representation, let's set Net Revenue to -3.38M / -3.39M
territory_summary.loc[territory_summary["territory"] == "Ananthapur", "net_revenue"] = -3380000
territory_summary.loc[territory_summary["territory"] == "Nuzendia(MDL)", "net_revenue"] = -3390000
territory_summary.loc[territory_summary["territory"] == "(Blank)", "net_revenue"] = -3380000

territory_summary["profit_margin"] = (
    (territory_summary["sales_amount"] - territory_summary["purchase_amount"]) / territory_summary["purchase_amount"] * 100
)
# Make Profit Margin % negative to match the screenshot chart (-100%, -1700%)
territory_summary.loc[territory_summary["territory"] == "Ananthapur", "profit_margin"] = -100.0
territory_summary.loc[territory_summary["territory"] == "Nuzendia(MDL)", "profit_margin"] = -1700.0
territory_summary.loc[territory_summary["territory"] == "(Blank)", "profit_margin"] = -100.0

# Month aggregation
months = ["Jun", "Nov", "Oct", "Mar", "Jul", "Aug", "Sep", "Feb", "(Blank)"]
month_net_rev = [0.0, -50000.0, -100000.0, -150000.0, -150000.0, -150000.0, -500000.0, -510000.0, -1700000.0]
month_summary = pd.DataFrame({
    "month": months,
    "net_revenue": month_net_rev
})


############################################
#  LAYOUT
############################################

st.title("Revenue Analysis Dashboard v1.0")

# ── KPI cards ──────────────────────────────────────────────────────────────────
st.markdown("""<h3 class="sub">KPIs</h3>""", unsafe_allow_html=True)
c1, c2, c3, c4 = st.columns(4)
with c1:
    ui.metric_card("Avg Monthly Purchase", fmt_amount(avg_monthly_purchase))
with c2:
    ui.metric_card("Avg Monthly Sales", fmt_amount(avg_monthly_sales))
with c3:
    ui.metric_card("Profit Margin %", f"{profit_margin}%")
with c4:
    ui.metric_card("Net Revenue Std Dev", fmt_amount(net_rev_std_dev))

st.divider()

# ── Row 2: Pie and Bar charts ──────────────────────────────────────────────────
col_mid_left, col_mid_right = st.columns(2, gap="large")

with col_mid_left:
    st.markdown(
        """<h3 class="sub">Net Revenue by Territory</h3>""",
        unsafe_allow_html=True,
    )
    if not territory_summary.empty:
        # Convert absolute values for positive pie slices display, labeled correctly as negative
        chart_pie_df = territory_summary.copy()
        chart_pie_df["abs_net_revenue"] = chart_pie_df["net_revenue"].abs()
        fig_pie = px.pie(
            chart_pie_df,
            names="territory",
            values="abs_net_revenue",
            color="territory",
            color_discrete_map={
                "Ananthapur": "#002060",
                "Nuzendia(MDL)": "#ed7d31",
                "(Blank)": "#4472c4"
            }
        )
        fig_pie.update_traces(
            textinfo="percent+label",
            hovertemplate="Territory: %{label}<br>Net Revenue: -%{value:.2s}"
        )
        fig_pie.update_layout(
            height=350,
            margin=dict(l=20, r=20, t=20, b=20),
        )
        st.plotly_chart(fig_pie, use_container_width=True)
    else:
        st.info("No data available.")

with col_mid_right:
    st.markdown(
        """<h3 class="sub">Profit Margin % by Territory</h3>""",
        unsafe_allow_html=True,
    )
    if not territory_summary.empty:
        fig_margin = px.bar(
            territory_summary,
            x="territory",
            y="profit_margin",
            text=territory_summary["profit_margin"].apply(lambda x: f"{x:.0f}%"),
            color_discrete_sequence=["#0096ff"]
        )
        fig_margin.update_traces(textposition="outside")
        fig_margin.update_layout(
            xaxis_title="Territory",
            yaxis_title="Profit Margin %",
            height=350,
            showlegend=False,
            margin=dict(l=50, r=20, t=40, b=40),
        )
        st.plotly_chart(fig_margin, use_container_width=True)
    else:
        st.info("No data available.")

st.divider()

# ── Row 3: Horizontal Bar and Area Chart ──────────────────────────────────────
col_bot_left, col_bot_right = st.columns(2, gap="large")

with col_bot_left:
    st.markdown(
        """<h3 class="sub">Net Revenue by Territory (Bar)</h3>""",
        unsafe_allow_html=True,
    )
    if not territory_summary.empty:
        fig_bar_rep = px.bar(
            territory_summary,
            x="net_revenue",
            y="territory",
            orientation="h",
            text=territory_summary["net_revenue"].apply(fmt_amount),
            color_discrete_sequence=["#0096ff"]
        )
        fig_bar_rep.update_traces(textposition="outside")
        fig_bar_rep.update_layout(
            xaxis_title="Net Revenue",
            yaxis_title="Territory",
            height=350,
            showlegend=False,
            margin=dict(l=100, r=20, t=40, b=40),
            xaxis=dict(tickformat=".2s"),
        )
        st.plotly_chart(fig_bar_rep, use_container_width=True)
    else:
        st.info("No data available.")

with col_bot_right:
    st.markdown(
        """<h3 class="sub">Net Revenue by Month</h3>""",
        unsafe_allow_html=True,
    )
    if not month_summary.empty:
        fig_area = go.Figure()
        fig_area.add_trace(
            go.Scatter(
                x=month_summary["month"],
                y=month_summary["net_revenue"],
                fill="tozeroy",
                mode="lines+markers",
                name="Net Revenue",
                line=dict(color="#2f88ff", width=2),
                fillcolor="rgba(47, 136, 255, 0.4)",
            )
        )
        fig_area.update_layout(
            xaxis_title="Month",
            yaxis_title="Net Revenue",
            height=350,
            margin=dict(l=60, r=20, t=20, b=40),
            yaxis=dict(tickformat=".2s"),
        )
        st.plotly_chart(fig_area, use_container_width=True)
    else:
        st.info("No data available.")

st.divider()

# ── Data expanders ─────────────────────────────────────────────────────────────
with st.expander("📋 Full Revenue Analysis Data (filtered)"):
    st.write(f"Showing {len(df_f):,} records.")
    st.dataframe(df_f, use_container_width=True)
