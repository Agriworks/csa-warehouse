"""
Farmer Income & Visits Dashboard v1.0

Data source: data/farmer_income_data.csv  (dummy CSV)
─────────────────────────────────────────────────────────
TODO – MongoDB migration:
  Replace load_data() body with:

      from pymongo import MongoClient
      client = MongoClient(MONGO_URI)
      collection = client["csa_db"]["farmer_income_visits"]
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
DATA_CSV  = DATA_DIR / "farmer_income_data.csv"
LOGO_PATH = Path(__file__).parent / "assets" / "images" / "csalogo.png"


# ── Page config + CSS ─────────────────────────────────────────────────────────
initialize_page()


# ── Data loading — swap this function for MongoDB when ready ───────────────────
@st.cache_data
def load_data() -> pd.DataFrame:
    """
    Load farmer income & visits data.

    Current source : CSV  (data/farmer_income_data.csv)
    Future source  : MongoDB collection  "farmer_income_visits"
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
    """<div class="sidebar-header">Farmer Income Dashboard</div>""",
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
all_coordinators = sorted(df["coordinator_name"].dropna().unique())
sel_coordinators = st.sidebar.multiselect(
    "Name of NF Coordinator:",
    options=all_coordinators,
    default=[],
    placeholder="All Coordinators",
)

all_months = sorted(df["month"].dropna().unique())
sel_months = st.sidebar.multiselect(
    "Month:",
    options=all_months,
    default=[],
    placeholder="All Months",
)

st.sidebar.markdown(
    "<hr style='margin-top:45px;margin-bottom:50px;'>",
    unsafe_allow_html=True,
)


# ── Apply filters ──────────────────────────────────────────────────────────────
df_f = df.copy()
if sel_coordinators:
    df_f = df_f[df_f["coordinator_name"].isin(sel_coordinators)]
if sel_months:
    df_f = df_f[df_f["month"].isin(sel_months)]


# ── Metrics ────────────────────────────────────────────────────────────────────
total_farmers_met = int(df_f["farmers_met"].sum())
total_visits = int(df_f["visits"].sum())


# ── Aggregations ───────────────────────────────────────────────────────────────
coord_summary = (
    df_f.groupby("coordinator_name", as_index=False)["score"]
    .sum()
    .sort_values("score", ascending=False)
)

village_summary = (
    df_f.groupby("village", as_index=False)["farmers_met"]
    .sum()
    .sort_values("farmers_met", ascending=False)
)


############################################
#  LAYOUT
############################################

st.title("Farmer Income & Visits Dashboard v1.0")

# ── KPI cards ──────────────────────────────────────────────────────────────────
st.markdown("""<h3 class="sub">KPIs</h3>""", unsafe_allow_html=True)
c1, c2, c3, c4, c5 = st.columns(5)
with c1:
    ui.metric_card("Total Income Display", "Awaiting data")
with c2:
    ui.metric_card("Total Farmers Met", f"{total_farmers_met:,}")
with c3:
    ui.metric_card("Net Income", "Awaiting data")
with c4:
    ui.metric_card("Total Visits", f"{total_visits:,}")
with c5:
    ui.metric_card("Total Yield", "Awaiting data")

st.divider()

# ── Charts ─────────────────────────────────────────────────────────────────────
col_left, col_right = st.columns([3, 2], gap="large")

with col_left:
    st.markdown(
        """<h3 class="sub">Total Score Sum by Name of NF Coordinator</h3>""",
        unsafe_allow_html=True,
    )
    if not coord_summary.empty:
        fig_score = px.bar(
            coord_summary,
            x="coordinator_name",
            y="score",
            text="score",
            color_discrete_sequence=["#1f77b4"],
        )
        fig_score.update_traces(textposition="outside")
        fig_score.update_layout(
            xaxis_title="Name of NF Coordinator",
            yaxis_title="Total Score Sum",
            height=450,
            showlegend=False,
            margin=dict(l=50, r=20, t=40, b=120),
            xaxis=dict(tickangle=-45),
        )
        st.plotly_chart(fig_score, use_container_width=True)
    else:
        st.info("No data available for selected filters.")

with col_right:
    st.markdown(
        """<h3 class="sub">Total Farmers Met by Village (Demo Details)</h3>""",
        unsafe_allow_html=True,
    )
    if not village_summary.empty:
        fig_village = px.bar(
            village_summary,
            x="village",
            y="farmers_met",
            text="farmers_met",
            color_discrete_sequence=["#1f77b4"],
        )
        fig_village.update_traces(textposition="outside")
        fig_village.update_layout(
            xaxis_title="Village (Demo Details)",
            yaxis_title="Total Farmers Met",
            height=450,
            showlegend=False,
            margin=dict(l=50, r=20, t=40, b=120),
            xaxis=dict(tickangle=-45),
        )
        st.plotly_chart(fig_village, use_container_width=True)
    else:
        st.info("No data available for selected filters.")

st.divider()

# ── Data expanders ─────────────────────────────────────────────────────────────
with st.expander("📋 Full Coordinator & Farmer Data (filtered)"):
    st.write(f"Showing {len(df_f):,} records.")
    st.dataframe(df_f, use_container_width=True)
