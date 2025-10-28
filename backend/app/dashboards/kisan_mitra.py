import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from datetime import datetime
import streamlit_shadcn_ui as ui
from utilities import (
    initialize_page,
    create_sidebar,
    read_date_data,
    read_category_data,
    read_department_data,
    read_issue_data,
)


# 1. Page setup
initialize_page()


st.title("Kisan Mitra Helpline Dashboard v1.2")

# 2. Load data
df_date = read_date_data()
df_category = read_category_data()
df_dept = read_department_data()
(
    df_issues,
    na_opening_dates,
    na_resolution_dates,
    all_records,
    min_date_raw,
    max_date_raw,
) = read_issue_data(df_date)

(
    current_start,
    current_end,
    prev_start,
    prev_end,
    comparison_label,
    prev_custom_start,
) = create_sidebar(df_issues, df_date, min_date_raw, max_date_raw)


df_filtered_issues = df_issues[
    (df_issues["Opening Date"] >= current_start)
    & (df_issues["Opening Date"] <= current_end)
].copy()

df_prev_filtered = (
    df_issues[
        (df_issues["Opening Date"] >= prev_start)
        & (df_issues["Opening Date"] <= prev_end)
    ].copy()
    if prev_start and prev_end
    else pd.DataFrame()
)


############################################
# Metrics, Charts and Other Computations
############################################


total_cases = df_filtered_issues["Case No"].nunique()

# Filter only resolved issues to calculate resolution days
resolved_issues = df_filtered_issues[df_filtered_issues["Status"] == "Resolved"].copy(
)

resolved_issues = df_filtered_issues[df_filtered_issues["Status"] == "Resolved"].copy(
)
resolved_issues["resolution days"] = (
    resolved_issues["Resolution Date Time"] -
    resolved_issues["Opening Date Time"]
).dt.days

avg_resolution_days = round(resolved_issues["resolution days"].mean(), 2)

closed_issues_count = len(
    df_filtered_issues[df_filtered_issues["Status"] == "Closed"])

pending_issues = df_filtered_issues[
    ~df_filtered_issues["Status"].isin(["Resolved", "Closed"])
].copy()


# Calculate resolution rate
resolution_rate = round(
    df_filtered_issues[df_filtered_issues["Status"]
                       == "Resolved"]["Case No"].nunique()
    / total_cases
    * 100,
    2,
)

# Calculate Aging of Pending Issues
pending_issues["Aging Days"] = (
    pd.Timestamp.today().normalize() - pending_issues["Opening Date"]
).dt.days


def categorize_aging(days):
    if days < 7:
        return "< 7 days"
    elif 7 <= days <= 30:
        return "7–30 days"
    else:
        return "> 30 days"


pending_issues["Aging Category"] = pending_issues["Aging Days"].apply(
    categorize_aging)

aging_order = ["< 7 days", "7–30 days", "> 30 days"]
aging_counts = (
    pending_issues["Aging Category"].value_counts().reindex(
        aging_order, fill_value=0)
)

# Create a bar chart for Aging of Pending Issues
aging_bar = go.Figure(
    go.Bar(
        x=aging_counts.values,
        y=aging_counts.index,
        orientation="h",
        marker=dict(color="indianred"),
        text=aging_counts.values,
        textposition="auto",
    )
)

aging_bar.update_layout(
    xaxis_title="Number of Cases",
    yaxis_title="Aging Category",
    yaxis=dict(
        categoryorder="array", categoryarray=["< 7 days", "7–30 days", "> 30 days"]
    ),
    height=400,
    margin=dict(l=80, r=20, t=60, b=40),
)


priority_counts = df_filtered_issues["Priority"].value_counts()
priority_percentage = (priority_counts / priority_counts.sum() * 100).round(2)

# Create plotly table for more insights to bar chart

min_aging = pending_issues["Aging Days"].min()
max_aging = pending_issues["Aging Days"].max()
aging_over_360 = pending_issues[pending_issues["Aging Days"] > 360].shape[0]

aging_table = go.Figure(
    data=[
        go.Table(
            header=dict(
                values=["<b>Metric</b>", "<b>Value</b>"],
                fill_color="#f8f9fa",
                align="center",
                height=40,
                font=dict(color="#333333", size=14),
                line=dict(width=1, color="#f0f0f0"),
            ),
            cells=dict(
                values=[
                    [
                        "Lowest aging (days)",
                        "Highest aging (days)",
                        "Cases with aging > 360 days",
                    ],
                    [min_aging, max_aging, aging_over_360],
                ],
                fill_color="white",
                align="center",
                height=36,
                font=dict(color="#333333", size=14),
                line=dict(width=1, color="#f0f0f0"),
            ),
        )
    ]
)

aging_table.update_layout(
    margin=dict(l=10, r=10, t=50, b=50),
    plot_bgcolor="white",
    paper_bgcolor="white",
    height=500,
)

# Temp dataframe for Pie Chart
chart_data = pd.DataFrame(
    {
        "priority": priority_counts.index,
        "count": priority_counts.values,
        "percent": priority_percentage.values,
    }
)

priority_pie = px.pie(
    chart_data,
    names="priority",
    values="count",
    hover_data=["count", "percent"],
    color_discrete_sequence=px.colors.qualitative.Pastel,
)
priority_pie.update_traces(
    texttemplate="%{percent:.2%}",  # ensures consistent display like 10.0%
    customdata=chart_data[["count"]].to_numpy(),
    hovertemplate="<b>%{label}</b><br>Cases: %{customdata[0]}",
)

# Create line chart for Resolved cases vs Cases Registered over time

registered_monthly = (
    df_filtered_issues.groupby(
        df_filtered_issues["Opening Date Time"].dt.to_period("M")
    )["Case No"]
    .nunique()
    .reset_index(name="Registered Cases")
)
registered_monthly["Month"] = registered_monthly["Opening Date Time"].dt.to_timestamp()

resolved_monthly = (
    resolved_issues.groupby(resolved_issues["Resolution Date Time"].dt.to_period("M"))[
        "Case No"
    ]
    .nunique()
    .reset_index(name="Resolved Cases")
)
resolved_monthly["Month"] = resolved_monthly["Resolution Date Time"].dt.to_timestamp()

monthly_summary = (
    pd.merge(
        registered_monthly[["Month", "Registered Cases"]],
        resolved_monthly[["Month", "Resolved Cases"]],
        on="Month",
        how="outer",
    )
    .fillna(0)
    .sort_values("Month")
)
monthly_summary["Registered Cases"] = monthly_summary["Registered Cases"].astype(
    int)
monthly_summary["Resolved Cases"] = monthly_summary["Resolved Cases"].astype(
    int)

monthly_melted = monthly_summary.melt(
    id_vars="Month",
    value_vars=["Registered Cases", "Resolved Cases"],
    var_name="Type",
    value_name="Number of Cases",
)

trend_line = px.line(
    monthly_melted,
    x="Month",
    y="Number of Cases",
    color="Type",
    markers=True,
)
trend_line.update_layout(
    xaxis_title="Month",
    yaxis_title="Number of Cases",
    xaxis=dict(range=[monthly_melted["Month"].min(),
               monthly_melted["Month"].max()]),
)

# Creating a distress summary table

distress_cases = df_filtered_issues[df_filtered_issues["Priority"] == "Distress"]

distress_with_categories = pd.merge(
    distress_cases[["Case No"]],
    df_category[["Case No", "Category Name"]],
    on="Case No",
    how="left",
)

distress_summary = (
    distress_with_categories["Category Name"]
    .value_counts()
    .reset_index()
    .rename(columns={"index": "Category", "count": "Frequency of Occurance"})
    .head(10)
)

# Creating tabs for different analyses
tab1, tab2, tab3 = st.tabs(
    ["Overview", "District-wise Analysis", "Department-wise Analysis"]
)

with tab1:
    # st.subheader("KPIs")
    st.markdown("""<h3 class="sub">KPIs</h3>""", unsafe_allow_html=True)
    cols = st.columns(5)

    with cols[0]:
        ui.metric_card("Total Cases Registered", total_cases)

    with cols[1]:
        ui.metric_card(
            "Total Cases Resolved",
            df_filtered_issues[df_filtered_issues["Status"] == "Resolved"][
                "Case No"
            ].nunique(),
        )
    with cols[2]:
        ui.metric_card("Average Resolution Days",
                       f"{avg_resolution_days} days")

    with cols[3]:
        ui.metric_card("Resolution Rate", f"{resolution_rate}%")

    with cols[4]:
        ui.metric_card("Non-Resolved Closed Cases", closed_issues_count)

    st.divider()

    # st.subheader("Monthly Trend: Registered vs Resolved Cases")
    st.markdown(
        """<h3 class="sub">Monthly Trend: Registered vs Resolved Cases</h3>""",
        unsafe_allow_html=True,
    )
    st.plotly_chart(trend_line, use_container_width=True)

    st.divider()

    col1, col2 = st.columns(2, gap="large")
    col1.subheader("Distribution of Registered Cases by Priority")
    col1.plotly_chart(priority_pie, use_container_width=True)

    # col2.subheader("Top 10 Distress Categories by Frequency")
    st.markdown(
        """<h3 class="sub">Top 10 Distress Categories by Frequency</h3>""",
        unsafe_allow_html=True,
    )

    col2.dataframe(distress_summary, use_container_width=True)

    st.divider()

    # st.subheader("Aging Distribution of Pending Cases")
    st.markdown(
        """<h3 class="sub">Aging Distribution of Pending Cases</h3>""",
        unsafe_allow_html=True,
    )

    col1, col2 = st.columns([2, 1], gap="large")

    col1.plotly_chart(aging_bar, use_container_width=True)
    col2.plotly_chart(aging_table, use_container_width=True)

    st.divider()


with tab2:
    st.subheader("District-wise Analysis")

    st.subheader("Dummy Text for Demo")

    st.write(
        "Lorem Ipsum is simply dummy text of the printing and typesetting industry. Lorem Ipsum has been the industry's standard dummy text ever since the 1500s, when an unknown printer took a galley of type and scrambled it to make a type specimen book. It has survived not only five centuries, but also the leap into electronic typesetting, remaining essentially unchanged. It was popularised in the 1960s with the release of Letraset sheets containing Lorem Ipsum passages, and more recently with desktop publishing software like Aldus PageMaker including versions of Lorem Ipsum."
    )

    st.divider()


with tab3:
    st.subheader("Department-wise Analysis")

    st.subheader("Dummy Text for Demo")

    st.write(
        "Lorem Ipsum is simply dummy text of the printing and typesetting industry. Lorem Ipsum has been the industry's standard dummy text ever since the 1500s, when an unknown printer took a galley of type and scrambled it to make a type specimen book. It has survived not only five centuries, but also the leap into electronic typesetting, remaining essentially unchanged. It was popularised in the 1960s with the release of Letraset sheets containing Lorem Ipsum passages, and more recently with desktop publishing software like Aldus PageMaker including versions of Lorem Ipsum."
    )

    st.divider()


# 3. Display data
with st.expander("🗂️ Category Mapping DataFrame"):
    st.dataframe(df_category)

with st.expander("🏢 Department Mapping DataFrame"):
    st.dataframe(df_dept)

with st.expander("📋 Issue Data (Merged with Date Info)"):
    st.write(f"This dataframe contains {len(df_filtered_issues)} records.")
    st.dataframe(df_filtered_issues)

st.caption(
    f"‼️Out of {all_records} total entries, {na_opening_dates} entries were dropped because the issue registration date ('Opening Date') was not recorded and {na_resolution_dates} were dropped becasue issue resolution date was not recorded for resolved issues."
)
