"""
Purchase & Sales Territory Dashboard v1.0

Data source: data/purchase_sales_data.csv  (dummy CSV)
─────────────────────────────────────────────────────────
TODO – MongoDB migration:
  Replace load_data() body with:

      from pymongo import MongoClient
      client = MongoClient(MONGO_URI)
      collection = client["csa_db"]["territory_transactions"]
      df = pd.DataFrame(list(collection.find({}, {"_id": 0})))
      df["date"] = pd.to_datetime(df["date"], format="%d-%m-%Y", errors="coerce")
      return df

  All downstream code remains unchanged.
─────────────────────────────────────────────────────────
"""

import base64
from utilities import initialize_page

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
import streamlit_shadcn_ui as ui
from pathlib import Path


# ── Paths ──────────────────────────────────────────────────────────────────────
DATA_DIR  = Path(__file__).parent / "data"
DATA_CSV  = DATA_DIR / "purchase_sales_data.csv"
LOGO_PATH = Path(__file__).parent / "assets" / "images" / "csalogo.png"


# ── Page config + CSS — same as kisan_mitra.py ────────────────────────────────
initialize_page()


# ── Helper: format numbers as K / M ───────────────────────────────────────────
def fmt_amount(val: float) -> str:
    """Display large numbers as 33.92K or 3.39M."""
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
    Load territory purchase & sales data.

    Current source : CSV  (data/purchase_sales_data.csv)
    Future source  : MongoDB collection  "territory_transactions"
    """
    df = pd.read_csv(DATA_CSV, encoding="ISO-8859-1")
    df["date"]         = pd.to_datetime(df["date"], format="%d-%m-%Y", errors="coerce")
    df["month_year"]   = df["date"].dt.strftime("%b %Y")      # "Sep 2024"
    df["month_period"] = df["date"].dt.to_period("M")         # for sorting
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
    """<div class="sidebar-header">Purchase & Sales Dashboard</div>""",
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

# ── Filter: Month Year ─────────────────────────────────────────────────────────
months_ordered = (
    df[["month_year", "month_period"]]
    .drop_duplicates()
    .sort_values("month_period")["month_year"]
    .tolist()
)
sel_months = st.sidebar.multiselect(
    "Month Year:",
    options=months_ordered,
    default=[],
    placeholder="All",
)

# ── Filter: Territory ──────────────────────────────────────────────────────────
all_territories = sorted(df["territory"].unique())
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
if sel_months:
    df_f = df_f[df_f["month_year"].isin(sel_months)]
if sel_territories:
    df_f = df_f[df_f["territory"].isin(sel_territories)]


# ── Metrics ────────────────────────────────────────────────────────────────────
total_sales    = df_f["sales_amount"].sum()
total_purchase = df_f["purchase_amount"].sum()
net_position   = total_sales - total_purchase


# ── Territory aggregation ──────────────────────────────────────────────────────
territory_summary = (
    df_f.groupby("territory", as_index=False)
    .agg(
        purchase_amount=("purchase_amount", "sum"),
        sales_amount=("sales_amount", "sum"),
    )
    .sort_values("purchase_amount", ascending=False)
)

# ── Monthly aggregation ────────────────────────────────────────────────────────
monthly_summary = (
    df_f.groupby(["month_period", "month_year"], as_index=False)
    .agg(
        purchase_amount=("purchase_amount", "sum"),
        sales_amount=("sales_amount", "sum"),
    )
    .sort_values("month_period")
)


############################################
#  LAYOUT
############################################

st.title("Purchase & Sales Territory Dashboard v1.0")

# ── KPI cards ──────────────────────────────────────────────────────────────────
st.markdown("""<h3 class="sub">KPIs</h3>""", unsafe_allow_html=True)
c1, c2, c3 = st.columns(3)
with c1:
    ui.metric_card("Total Sales", fmt_amount(total_sales))
    st.caption("Total Sales Amount")
with c2:
    ui.metric_card("Total Purchases", fmt_amount(total_purchase))
    st.caption("Total Purchase Amount")
with c3:
    ui.metric_card("Net Position", fmt_amount(net_position))
    st.caption("Net Revenue")

st.divider()

# ── Territory bar charts ───────────────────────────────────────────────────────
col_left, col_right = st.columns(2, gap="large")

with col_left:
    st.markdown(
        """<h3 class="sub">Total Purchase Amount by Territory</h3>""",
        unsafe_allow_html=True,
    )
    if not territory_summary.empty:
        fig_pur = px.bar(
            territory_summary,
            x="territory",
            y="purchase_amount",
            text=territory_summary["purchase_amount"].apply(fmt_amount),
            color_discrete_sequence=["#1f77b4"],
        )
        fig_pur.update_traces(textposition="outside")
        fig_pur.update_layout(
            xaxis_title="Territory",
            yaxis_title="Total Purchase Amount",
            height=400,
            showlegend=False,
            margin=dict(l=50, r=20, t=40, b=60),
            yaxis=dict(tickformat=".2s"),
        )
        st.plotly_chart(fig_pur, use_container_width=True)
    else:
        st.info("No data for selected filters.")

with col_right:
    st.markdown(
        """<h3 class="sub">Total Sales Amount by Territory</h3>""",
        unsafe_allow_html=True,
    )
    if not territory_summary.empty:
        fig_sal = px.bar(
            territory_summary,
            x="territory",
            y="sales_amount",
            text=territory_summary["sales_amount"].apply(fmt_amount),
            color_discrete_sequence=["#1f77b4"],
        )
        fig_sal.update_traces(textposition="outside")
        fig_sal.update_layout(
            xaxis_title="Territory",
            yaxis_title="Total Sales Amount",
            height=400,
            showlegend=False,
            margin=dict(l=50, r=20, t=40, b=60),
            yaxis=dict(tickformat=".2s"),
        )
        st.plotly_chart(fig_sal, use_container_width=True)
    else:
        st.info("No data for selected filters.")

st.divider()

# ── Monthly dual line chart ────────────────────────────────────────────────────
st.markdown(
    """<h3 class="sub">Total Purchase Amount and Total Sales Amount by Month</h3>""",
    unsafe_allow_html=True,
)

if not monthly_summary.empty:
    monthly_melted = monthly_summary.melt(
        id_vars=["month_period", "month_year"],
        value_vars=["purchase_amount", "sales_amount"],
        var_name="Type",
        value_name="Amount",
    )
    monthly_melted["Type"] = monthly_melted["Type"].map(
        {
            "purchase_amount": "Total Purchase Amount",
            "sales_amount":    "Total Sales Amount",
        }
    )

    fig_monthly = px.line(
        monthly_melted,
        x="month_year",
        y="Amount",
        color="Type",
        markers=True,
        text="Amount",
        color_discrete_map={
            "Total Purchase Amount": "#1f77b4",
            "Total Sales Amount":    "#17becf",
        },
    )
    fig_monthly.update_traces(
        texttemplate="%{y:.2s}",
        textposition="top center",
    )
    fig_monthly.update_layout(
        xaxis_title="Month",
        yaxis_title="Total Purchase Amount and Total Sales Amount",
        height=440,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="left",
            x=0,
            title=None,
        ),
        margin=dict(l=60, r=20, t=60, b=60),
        yaxis=dict(tickformat=".2s"),
    )
    st.plotly_chart(fig_monthly, use_container_width=True)
else:
    st.info("No data available for the selected filters.")

st.divider()

# ── Data expanders ─────────────────────────────────────────────────────────────
with st.expander("📋 Full Transaction Data (filtered)"):
    st.write(f"Showing {len(df_f):,} records.")
    st.dataframe(df_f, use_container_width=True)

with st.expander("📊 Territory Summary"):
    st.dataframe(territory_summary, use_container_width=True, hide_index=True)
