"""
Stock Inventory Dashboard v1.0

Data source: data/stock_inventory_data.csv  (dummy CSV)
─────────────────────────────────────────────────────────
TODO – MongoDB migration:
  Replace load_data() body with:

      from pymongo import MongoClient
      client = MongoClient(MONGO_URI)
      collection = client["csa_db"]["stock_inventory"]
      df = pd.DataFrame(list(collection.find({}, {"_id": 0})))
      return df

  All downstream code remains unchanged.
─────────────────────────────────────────────────────────
"""

import base64
from utilities import initialize_page

import pandas as pd
import plotly.express as px
import streamlit as st
import streamlit_shadcn_ui as ui
from pathlib import Path


# ── Paths ──────────────────────────────────────────────────────────────────────
DATA_DIR  = Path(__file__).parent / "data"
DATA_CSV  = DATA_DIR / "stock_inventory_data.csv"
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
    Load stock inventory data.

    Current source : CSV  (data/stock_inventory_data.csv)
    Future source  : MongoDB collection  "stock_inventory"
    """
    df = pd.read_csv(DATA_CSV, encoding="ISO-8859-1")
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
    """<div class="sidebar-header">Stock Inventory Dashboard</div>""",
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
all_companies = sorted(df["company"].dropna().unique())
sel_companies = st.sidebar.multiselect(
    "Company:",
    options=all_companies,
    default=[],
    placeholder="All Companies",
)

all_warehouses = sorted(df["warehouse"].dropna().unique())
sel_warehouses = st.sidebar.multiselect(
    "Warehouse:",
    options=all_warehouses,
    default=[],
    placeholder="All Warehouses",
)

all_groups = sorted(df["item_group"].dropna().unique())
sel_groups = st.sidebar.multiselect(
    "Item Group:",
    options=all_groups,
    default=[],
    placeholder="All Groups",
)

st.sidebar.markdown(
    "<hr style='margin-top:45px;margin-bottom:50px;'>",
    unsafe_allow_html=True,
)


# ── Apply filters ──────────────────────────────────────────────────────────────
df_f = df.copy()
if sel_companies:
    df_f = df_f[df_f["company"].isin(sel_companies)]
if sel_warehouses:
    df_f = df_f[df_f["warehouse"].isin(sel_warehouses)]
if sel_groups:
    df_f = df_f[df_f["item_group"].isin(sel_groups)]


# ── Metrics ────────────────────────────────────────────────────────────────────
total_stock_qty = df_f["stock_qty"].sum()
total_stock_value = df_f["stock_value"].sum()
items_in_stock = df_f["item_name"].nunique()
warehouses_count = df_f["warehouse"].nunique()
avg_stock_value = total_stock_value / items_in_stock if items_in_stock > 0 else 0


# ── Aggregations ───────────────────────────────────────────────────────────────
item_summary = (
    df_f.groupby("item_name", as_index=False)["stock_value"]
    .sum()
    .sort_values("stock_value", ascending=True) # Ascending for horizontal bar bottom-up display
)

warehouse_summary = (
    df_f.groupby("warehouse", as_index=False)["stock_qty"]
    .sum()
    .sort_values("stock_qty", ascending=False)
)

group_summary = (
    df_f.groupby("item_group", as_index=False)["stock_value"]
    .sum()
    .sort_values("stock_value", ascending=True) # Ascending for horizontal bar bottom-up display
)


############################################
#  LAYOUT
############################################

st.title("Stock Inventory Dashboard v1.0")

# ── KPI cards ──────────────────────────────────────────────────────────────────
st.markdown("""<h3 class="sub">KPIs</h3>""", unsafe_allow_html=True)
c1, c2, c3, c4, c5 = st.columns(5)
with c1:
    ui.metric_card("Total Stock Qty", fmt_amount(total_stock_qty))
with c2:
    ui.metric_card("Total Stock Value", fmt_amount(total_stock_value))
with c3:
    ui.metric_card("Items in Stock", f"{items_in_stock}")
with c4:
    ui.metric_card("Warehouses", f"{warehouses_count}")
with c5:
    ui.metric_card("Avg Stock Value per Item", fmt_amount(avg_stock_value))

st.divider()

# ── Charts ─────────────────────────────────────────────────────────────────────
col_left, col_right = st.columns(2, gap="large")

with col_left:
    st.markdown(
        """<h3 class="sub">Total Stock Value by Item Name</h3>""",
        unsafe_allow_html=True,
    )
    if not item_summary.empty:
        fig_item = px.bar(
            item_summary,
            x="stock_value",
            y="item_name",
            orientation="h",
            text=item_summary["stock_value"].apply(fmt_amount),
            color_discrete_sequence=["#0096ff"],
        )
        fig_item.update_traces(textposition="outside")
        fig_item.update_layout(
            xaxis_title="Total Stock Value",
            yaxis_title="Item Name",
            height=650,
            showlegend=False,
            margin=dict(l=150, r=20, t=40, b=40),
            xaxis=dict(tickformat=".2s"),
        )
        st.plotly_chart(fig_item, use_container_width=True)
    else:
        st.info("No data available.")

with col_right:
    st.markdown(
        """<h3 class="sub">Total Stock Qty by Warehouse</h3>""",
        unsafe_allow_html=True,
    )
    if not warehouse_summary.empty:
        fig_wh = px.bar(
            warehouse_summary,
            x="warehouse",
            y="stock_qty",
            text=warehouse_summary["stock_qty"].apply(fmt_amount),
            color_discrete_sequence=["#0096ff"],
        )
        fig_wh.update_traces(textposition="outside")
        fig_wh.update_layout(
            xaxis_title="Warehouse",
            yaxis_title="Total Stock Qty",
            height=300,
            showlegend=False,
            margin=dict(l=50, r=20, t=40, b=80),
            yaxis=dict(tickformat=".2s"),
        )
        st.plotly_chart(fig_wh, use_container_width=True)
    else:
        st.info("No data available.")

    st.divider()

    st.markdown(
        """<h3 class="sub">Total Stock Value by Item Group</h3>""",
        unsafe_allow_html=True,
    )
    if not group_summary.empty:
        fig_gp = px.bar(
            group_summary,
            x="stock_value",
            y="item_group",
            orientation="h",
            text=group_summary["stock_value"].apply(fmt_amount),
            color_discrete_sequence=["#0096ff"],
        )
        fig_gp.update_traces(textposition="outside")
        fig_gp.update_layout(
            xaxis_title="Total Stock Value",
            yaxis_title="Item Group",
            height=300,
            showlegend=False,
            margin=dict(l=100, r=20, t=20, b=40),
            xaxis=dict(tickformat=".2s"),
        )
        st.plotly_chart(fig_gp, use_container_width=True)
    else:
        st.info("No data available.")

st.divider()

# ── Data expanders ─────────────────────────────────────────────────────────────
with st.expander("📋 Full Stock Inventory Data (filtered)"):
    st.write(f"Showing {len(df_f):,} records.")
    st.dataframe(df_f, use_container_width=True)
