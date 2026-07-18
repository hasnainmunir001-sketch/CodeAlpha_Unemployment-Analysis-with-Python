"""
Unemployment in India — Interactive Analysis Dashboard
=======================================================
A Streamlit app for exploring unemployment trends across Indian states,
with a special focus on the impact of COVID-19.

Run locally:
    streamlit run app.py

Author : (add your name here before publishing)
Dataset: Unemployment in India — Kaggle (gokulrajkmv/unemployment-in-india)
"""

import io
import os
import numpy as np
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px

from utils.data_processing import load_and_clean, summary_stats, covid_impact_table

# Absolute path to the sample CSV, based on this file's location — works no
# matter which directory the app is launched from.
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SAMPLE_DATA_PATH = os.path.join(BASE_DIR, "data", "sample_unemployment_data.csv")

# --------------------------------------------------------------------------------------
# PAGE CONFIG & GLOBAL STYLE
# --------------------------------------------------------------------------------------
st.set_page_config(
    page_title="Unemployment in India | Analysis Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

sns.set_theme(style="whitegrid")

CUSTOM_CSS = """
<style>
    .main-header {
        font-size: 2.2rem;
        font-weight: 700;
        color: #1F2937;
        padding-bottom: 0.2rem;
    }
    .sub-header {
        font-size: 1.05rem;
        color: #4B5563;
        margin-bottom: 1.5rem;
    }
    .metric-card {
        background-color: #F9FAFB;
        border: 1px solid #E5E7EB;
        border-radius: 10px;
        padding: 1rem;
    }
    .insight-box {
        background-color: #EFF6FF;
        border-left: 5px solid #2563EB;
        padding: 0.9rem 1.1rem;
        border-radius: 6px;
        margin-bottom: 0.8rem;
    }
    footer {visibility: hidden;}
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# --------------------------------------------------------------------------------------
# SIDEBAR — DATA SOURCE
# --------------------------------------------------------------------------------------
st.sidebar.title("⚙️ Data Source")
st.sidebar.markdown(
    "Upload the **Unemployment in India** CSV (Kaggle) or use the "
    "bundled sample dataset to explore the dashboard."
)

uploaded_file = st.sidebar.file_uploader("Upload CSV file", type=["csv"])
use_sample = st.sidebar.checkbox("Use sample dataset instead", value=uploaded_file is None)

st.sidebar.markdown("---")
st.sidebar.info(
    "**Dataset source:** [Kaggle — Unemployment in India]"
    "(https://www.kaggle.com/datasets/gokulrajkmv/unemployment-in-india)"
)


@st.cache_data(show_spinner=False)
def get_dataframe(file_bytes: bytes | None, sample: bool) -> pd.DataFrame:
    if sample or file_bytes is None:
        return load_and_clean(SAMPLE_DATA_PATH)
    return load_and_clean(io.BytesIO(file_bytes))


if uploaded_file is not None and not use_sample:
    file_bytes = uploaded_file.getvalue()
    df = get_dataframe(file_bytes, sample=False)
    data_label = f"Uploaded file: `{uploaded_file.name}`"
else:
    df = get_dataframe(None, sample=True)
    data_label = "Sample dataset (bundled with app)"

if df.empty:
    st.error("The dataset could not be loaded or is empty. Please check the CSV format.")
    st.stop()

# --------------------------------------------------------------------------------------
# HEADER
# --------------------------------------------------------------------------------------
st.markdown('<div class="main-header">📊 Unemployment in India — Analysis Dashboard</div>', unsafe_allow_html=True)
st.markdown(
    f'<div class="sub-header">Data cleaning, exploratory analysis, and COVID-19 impact '
    f'assessment of unemployment trends. Currently using: {data_label}</div>',
    unsafe_allow_html=True,
)

# --------------------------------------------------------------------------------------
# SIDEBAR — FILTERS
# --------------------------------------------------------------------------------------
st.sidebar.markdown("---")
st.sidebar.title("🔎 Filters")

regions = sorted(df["region"].dropna().unique()) if "region" in df.columns else []
selected_regions = st.sidebar.multiselect("Region / State", options=regions, default=regions)

areas = sorted(df["area"].dropna().unique()) if "area" in df.columns else []
selected_areas = st.sidebar.multiselect("Area", options=areas, default=areas)

if "date" in df.columns and not df["date"].isna().all():
    min_date, max_date = df["date"].min(), df["date"].max()
    date_range = st.sidebar.slider(
        "Date range",
        min_value=min_date.to_pydatetime(),
        max_value=max_date.to_pydatetime(),
        value=(min_date.to_pydatetime(), max_date.to_pydatetime()),
    )
else:
    date_range = None

filtered = df.copy()
if selected_regions:
    filtered = filtered[filtered["region"].isin(selected_regions)]
if selected_areas:
    filtered = filtered[filtered["area"].isin(selected_areas)]
if date_range:
    filtered = filtered[(filtered["date"] >= date_range[0]) & (filtered["date"] <= date_range[1])]

if filtered.empty:
    st.warning("No data matches the selected filters. Please broaden your selection.")
    st.stop()

# --------------------------------------------------------------------------------------
# TOP-LEVEL KPIs
# --------------------------------------------------------------------------------------
k1, k2, k3, k4 = st.columns(4)
k1.metric("Avg. Unemployment Rate", f"{filtered['unemployment_rate'].mean():.2f}%")
k2.metric("Peak Unemployment Rate", f"{filtered['unemployment_rate'].max():.2f}%")
if "labour_participation_rate" in filtered.columns:
    k3.metric("Avg. Labour Participation", f"{filtered['labour_participation_rate'].mean():.2f}%")
if "employed" in filtered.columns:
    k4.metric("Avg. Estimated Employed", f"{filtered['employed'].mean():,.0f}")

st.markdown("---")

# --------------------------------------------------------------------------------------
# TABS
# --------------------------------------------------------------------------------------
tab_overview, tab_trends, tab_covid, tab_seasonality, tab_insights, tab_data = st.tabs(
    ["🏠 Overview", "📈 Trends", "🦠 COVID-19 Impact", "📅 Seasonality", "💡 Insights", "🗂️ Raw Data"]
)

# ---------------- OVERVIEW ----------------
with tab_overview:
    st.subheader("Dataset Overview")
    c1, c2 = st.columns([2, 1])
    with c1:
        st.dataframe(filtered.head(20), use_container_width=True)
    with c2:
        st.write("**Descriptive statistics**")
        st.dataframe(summary_stats(filtered), use_container_width=True)

    st.write("**Missing values (post-cleaning)**")
    st.dataframe(filtered.isna().sum().rename("missing_count").to_frame(), use_container_width=True)

    if "area" in filtered.columns:
        fig = px.pie(
            filtered, names="area", title="Record Distribution by Area (Rural vs Urban)", hole=0.45
        )
        st.plotly_chart(fig, use_container_width=True)

# ---------------- TRENDS ----------------
with tab_trends:
    st.subheader("Unemployment Rate Over Time")
    ts = filtered.groupby("date", as_index=False)["unemployment_rate"].mean()
    fig = px.line(ts, x="date", y="unemployment_rate", title="National Average Unemployment Rate Over Time")
    fig.update_traces(line=dict(width=2.5))
    st.plotly_chart(fig, use_container_width=True)

    if "region" in filtered.columns:
        st.subheader("Top / Bottom Regions by Average Unemployment Rate")
        region_avg = (
            filtered.groupby("region")["unemployment_rate"].mean().sort_values(ascending=False).reset_index()
        )
        colA, colB = st.columns(2)
        with colA:
            fig_top = px.bar(
                region_avg.head(10), x="unemployment_rate", y="region", orientation="h",
                title="Top 10 Regions — Highest Avg. Unemployment", color="unemployment_rate",
                color_continuous_scale="Reds",
            )
            fig_top.update_layout(yaxis={"categoryorder": "total ascending"})
            st.plotly_chart(fig_top, use_container_width=True)
        with colB:
            fig_bottom = px.bar(
                region_avg.tail(10), x="unemployment_rate", y="region", orientation="h",
                title="Bottom 10 Regions — Lowest Avg. Unemployment", color="unemployment_rate",
                color_continuous_scale="Greens",
            )
            fig_bottom.update_layout(yaxis={"categoryorder": "total descending"})
            st.plotly_chart(fig_bottom, use_container_width=True)

    if "area" in filtered.columns:
        st.subheader("Rural vs Urban Unemployment Trend")
        area_ts = filtered.groupby(["date", "area"], as_index=False)["unemployment_rate"].mean()
        fig_area = px.line(area_ts, x="date", y="unemployment_rate", color="area",
                            title="Rural vs Urban Unemployment Rate Over Time")
        st.plotly_chart(fig_area, use_container_width=True)

    if {"unemployment_rate", "employed", "labour_participation_rate"}.issubset(filtered.columns):
        st.subheader("Correlation Between Key Indicators")
        corr = filtered[["unemployment_rate", "employed", "labour_participation_rate"]].corr()
        fig_corr, ax = plt.subplots(figsize=(5, 4))
        sns.heatmap(corr, annot=True, cmap="coolwarm", fmt=".2f", ax=ax)
        st.pyplot(fig_corr)

# ---------------- COVID IMPACT ----------------
with tab_covid:
    st.subheader("Impact of COVID-19 on Unemployment")
    st.caption("India's nationwide lockdown began on 25 March 2020 — used as the COVID cut-off date.")

    covid_table = covid_impact_table(filtered)
    if not covid_table.empty:
        c1, c2 = st.columns([1, 2])
        with c1:
            st.dataframe(covid_table, use_container_width=True)
            pre = covid_table.loc[covid_table["covid_period"] == "Pre-COVID", "avg_unemployment_rate"]
            post = covid_table.loc[covid_table["covid_period"] == "COVID / Post-COVID", "avg_unemployment_rate"]
            if len(pre) and len(post):
                delta = post.values[0] - pre.values[0]
                st.metric("Change in Avg. Unemployment Rate", f"{delta:+.2f} pts")
        with c2:
            fig = px.bar(
                covid_table, x="covid_period", y="avg_unemployment_rate", color="covid_period",
                title="Average Unemployment Rate: Pre-COVID vs COVID/Post-COVID",
                color_discrete_sequence=["#10B981", "#EF4444"],
            )
            st.plotly_chart(fig, use_container_width=True)

    st.subheader("Monthly Trend Highlighting the COVID Spike")
    ts = filtered.groupby("date", as_index=False)["unemployment_rate"].mean()
    fig2 = px.line(ts, x="date", y="unemployment_rate", title="Unemployment Rate Timeline")
    fig2.add_vline(x="2020-03-25", line_dash="dash", line_color="red",
                    annotation_text="Lockdown begins", annotation_position="top")
    st.plotly_chart(fig2, use_container_width=True)

    if "area" in filtered.columns:
        st.subheader("COVID Impact by Area (Rural vs Urban)")
        area_covid = filtered.groupby(["area", "covid_period"])["unemployment_rate"].mean().reset_index()
        fig3 = px.bar(area_covid, x="area", y="unemployment_rate", color="covid_period", barmode="group",
                      title="Rural vs Urban — Pre vs Post COVID Unemployment Rate")
        st.plotly_chart(fig3, use_container_width=True)

# ---------------- SEASONALITY ----------------
with tab_seasonality:
    st.subheader("Monthly / Seasonal Patterns")
    if "month_name" in filtered.columns:
        month_order = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
        monthly = filtered.groupby("month_name")["unemployment_rate"].mean().reindex(month_order).reset_index()
        fig = px.line(monthly, x="month_name", y="unemployment_rate", markers=True,
                      title="Average Unemployment Rate by Month (Seasonality)")
        st.plotly_chart(fig, use_container_width=True)

        fig_box = px.box(filtered, x="month_name", y="unemployment_rate", category_orders={"month_name": month_order},
                          title="Distribution of Unemployment Rate by Month")
        st.plotly_chart(fig_box, use_container_width=True)

    if "year" in filtered.columns:
        st.subheader("Year-over-Year Comparison")
        yearly = filtered.groupby("year")["unemployment_rate"].mean().reset_index()
        fig_year = px.bar(yearly, x="year", y="unemployment_rate", title="Average Unemployment Rate by Year")
        st.plotly_chart(fig_year, use_container_width=True)

# ---------------- INSIGHTS ----------------
with tab_insights:
    st.subheader("💡 Key Insights & Policy Recommendations")

    pre_avg = filtered.loc[filtered["covid_period"] == "Pre-COVID", "unemployment_rate"].mean() \
        if "covid_period" in filtered.columns else np.nan
    post_avg = filtered.loc[filtered["covid_period"] == "COVID / Post-COVID", "unemployment_rate"].mean() \
        if "covid_period" in filtered.columns else np.nan

    insights = []
    if not np.isnan(pre_avg) and not np.isnan(post_avg):
        change_pct = ((post_avg - pre_avg) / pre_avg) * 100 if pre_avg else np.nan
        insights.append(
            f"Average unemployment rate moved from **{pre_avg:.2f}%** (pre-COVID) to "
            f"**{post_avg:.2f}%** (COVID/post-COVID) — a change of **{change_pct:+.1f}%**, "
            f"highlighting the scale of labour-market disruption caused by the pandemic and lockdowns."
        )
    if "area" in filtered.columns:
        area_avg = filtered.groupby("area")["unemployment_rate"].mean()
        if len(area_avg) > 1:
            higher_area = area_avg.idxmax()
            insights.append(
                f"**{higher_area}** areas show a consistently higher average unemployment rate "
                f"than other areas, suggesting targeted employment schemes may be more impactful there."
            )
    if "region" in filtered.columns:
        region_avg = filtered.groupby("region")["unemployment_rate"].mean().sort_values(ascending=False)
        if len(region_avg) > 0:
            insights.append(
                f"**{region_avg.index[0]}** recorded the highest average unemployment rate "
                f"({region_avg.iloc[0]:.2f}%) among all regions in the filtered data — a candidate "
                f"for priority policy intervention (skill development, MSME support, rural employment schemes)."
            )
    if "month_name" in filtered.columns:
        month_order = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
        monthly = filtered.groupby("month_name")["unemployment_rate"].mean().reindex(month_order)
        if monthly.notna().any():
            peak_month = monthly.idxmax()
            insights.append(
                f"Unemployment tends to peak around **{peak_month}**, indicating a possible seasonal "
                f"pattern that policymakers could anticipate with temporary employment or relief programs."
            )

    if not insights:
        st.info("Add more data or broaden filters to generate detailed insights.")
    for i, ins in enumerate(insights, start=1):
        st.markdown(f'<div class="insight-box">**{i}.** {ins}</div>', unsafe_allow_html=True)

    st.markdown("### Suggested Policy Directions")
    st.markdown(
        """
        - **Targeted relief for high-unemployment regions**: prioritize states/regions with
          persistently elevated rates for skill-building and job-guarantee schemes.
        - **Rural vs urban strategy**: rural and urban labour markets often respond differently
          to shocks — schemes such as MGNREGA-style rural employment guarantees vs urban
          job-matching platforms should be tailored accordingly.
        - **Pandemic-preparedness buffer**: the sharp COVID-19 spike shows the value of a
          rapid-response unemployment insurance / wage-subsidy mechanism for future shocks.
        - **Seasonal workforce planning**: where clear seasonal peaks exist, temporary public
          works or seasonal credit support can smooth household income volatility.
        """
    )

# ---------------- RAW DATA ----------------
with tab_data:
    st.subheader("Cleaned Dataset")
    st.dataframe(filtered, use_container_width=True)
    csv_bytes = filtered.to_csv(index=False).encode("utf-8")
    st.download_button(
        "⬇️ Download filtered data as CSV",
        data=csv_bytes,
        file_name="cleaned_unemployment_data.csv",
        mime="text/csv",
    )

st.markdown("---")
st.caption(
    "Built with Streamlit • Data: Unemployment in India (Kaggle) • "
    "For educational / portfolio purposes."
)
