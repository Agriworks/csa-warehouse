"""
Stock Movement Dashboard v1.0

Data source: data/stock_movement_data.csv  (dummy CSV)
─────────────────────────────────────────────────────────
TODO – MongoDB migration:
  Replace load_data() body with:

      from pymongo import MongoClient
      client = MongoClient(MONGO_URI)
      collection = client["csa_db"]["stock_movement"]
      df = pd.DataFrame(list(collection.find({}, {"_id": 0})))
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
DATA_CSV  = DATA_DIR / "stock_movement_data.csv"
LOGO_PATH = Path(__file__).parent / "assets" / "images" / "csalogo.png"


# ── Page config + CSS ─────────────────────────────────────────────────────────
initialize_page()


# ── Helper: format numbers as K / M ───────────────────────────────────────────
def fmt_amount(val: float) -> str:
    abs_val = abs(val)
    sign = "-" if val < 0 else ""
    if abs_val >= 1_000_000:
        return f"{sign}{abs_val / 1_000_000:.1f}M"
    if abs_val >= 1_000:
        return f"{sign}{abs_val / 1_000:.1f}K"
    return f"{sign}{abs_val:.0f}"


# ── Data loading — swap this function for MongoDB when ready ───────────────────
@st.cache_data
def load_data() -> pd.DataFrame:
    """
    Load stock movement data.

    Current source : CSV  (data/stock_movement_data.csv)
    Future source  : MongoDB collection  "stock_movement"
    """
    df = pd.read_csv(DATA_CSV, encoding="ISO-8859-1")
    df["date"] = pd.to_datetime(df["date"], format="%d-%m-%Y", errors="coerce")
    df["year"] = df["date"].dt.year.astype(str)
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
    """<div class="sidebar-header">Stock Movement Dashboard</div>""",
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


# ── Filter: Date/Year in Sidebar ───────────────────────────────────────────────
all_years = sorted(df["year"].dropna().unique())
sel_years = st.sidebar.multiselect(
    "Date (Year):",
    options=all_years,
    default=[],
    placeholder="All Years",
)

st.sidebar.markdown(
    "<hr style='margin-top:45px;margin-bottom:50px;'>",
    unsafe_allow_html=True,
)


# ── Apply filters ──────────────────────────────────────────────────────────────
df_f = df.copy()
if sel_years:
    df_f = df_f[df_f["year"].isin(sel_years)]


# ── Metrics ────────────────────────────────────────────────────────────────────
total_in = df_f["in_qty"].sum()
total_out = df_f["out_qty"].sum()
net_stock_movement = total_in - total_out


# ── Year aggregation ───────────────────────────────────────────────────────────
year_summary = (
    df_f.groupby("year", as_index=False)
    .agg(
        in_qty=("in_qty", "sum"),
        out_qty=("out_qty", "sum"),
        balance_value=("balance_value", "sum"),
    )
    .sort_values("year")
)


############################################
#  LAYOUT
############################################

st.title("Stock Movement Dashboard v1.0")

col_left, col_right = st.columns([1, 3], gap="large")

with col_left:
    st.markdown("""<h3 class="sub">KPI</h3>""", unsafe_allow_html=True)
    ui.metric_card("Net Stock Movement", f"{net_stock_movement:,}")
    
    st.write("")
    st.write("")
    
    # Let's put a local selector just like the screenshot or keep it in the sidebar
    st.write("**Quick filter:**")
    sel_year_local = st.selectbox("Date", ["All"] + all_years)
    
    if sel_year_local != "All":
        df_f_local = df[df["year"] == sel_year_local]
        net_local = df_f_local["in_qty"].sum() - df_f_local["out_qty"].sum()
        year_summary_local = df_f_local.groupby("year", as_index=False).agg(
            in_qty=("in_qty", "sum"),
            out_qty=("out_qty", "sum"),
            balance_value=("balance_value", "sum"),
        )
    else:
        df_f_local = df_f
        net_local = net_stock_movement
        year_summary_local = year_summary

with col_right:
    # Top Chart: Sum of In Qty and Sum of Out Qty by Year
    st.markdown(
        """<h3 class="sub">Sum of In Qty and Sum of Out Qty by Year</h3>""",
        unsafe_allow_html=True,
    )
    
    if not year_summary_local.empty:
        fig_line = go.Figure()
        fig_line.add_trace(
            go.Scatter(
                x=year_summary_local["year"],
                y=year_summary_local["in_qty"],
                mode="lines+markers+text",
                name="Sum of In Qty",
                text=year_summary_local["in_qty"].apply(fmt_amount),
                textposition="top center",
                line=dict(color="#1f77b4", width=3),
            )
        )
        fig_line.add_trace(
            go.Scatter(
                x=year_summary_local["year"],
                y=year_summary_local["out_qty"],
                mode="lines+markers+text",
                name="Sum of Out Qty",
                text=year_summary_local["out_qty"].apply(fmt_amount),
                textposition="bottom center",
                line=dict(color="#000080", width=3),
            )
        )
        fig_line.update_layout(
            xaxis_title="Year",
            yaxis_title="Sum of In Qty and Sum of Out Qty",
            height=300,
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="left",
                x=0,
                title=None,
            ),
            margin=dict(l=50, r=20, t=55, b=40),
            yaxis=dict(tickformat=".2s"),
        )
        st.plotly_chart(fig_line, use_container_width=True)
    else:
        st.info("No data available.")

    st.divider()

    # Bottom Chart: Sum of Balance Value by Year (Area Chart)
    st.markdown(
        """<h3 class="sub">Sum of Balance Value by Year</h3>""",
        unsafe_allow_html=True,
    )
    
    if not year_summary_local.empty:
        fig_area = go.Figure()
        fig_area.add_trace(
            go.Scatter(
                x=year_summary_local["year"],
                y=year_summary_local["balance_value"],
                fill="tozeroy",
                mode="lines+markers+text",
                name="Sum of Balance Value",
                text=year_summary_local["balance_value"].apply(fmt_amount),
                textposition="top center",
                line=dict(color="#2f88ff", width=2),
                fillcolor="rgba(47, 136, 255, 0.4)",
            )
        )
        fig_area.update_layout(
            xaxis_title="Year",
            yaxis_title="Sum of Balance Value",
            height=300,
            margin=dict(l=50, r=20, t=20, b=40),
            yaxis=dict(tickformat=".2s"),
        )
        st.plotly_chart(fig_area, use_container_width=True)
    else:
        st.info("No data available.")

st.divider()

# ── Data expanders ─────────────────────────────────────────────────────────────
with st.expander("📋 Full Stock Movement Data (filtered)"):
    st.write(f"Showing {len(df_f_local):,} records.")
    st.dataframe(df_f_local, use_container_width=True)
