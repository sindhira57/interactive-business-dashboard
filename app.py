import streamlit as st
import pandas as pd
import plotly.express as px

# --------------------------------------------------
# PAGE CONFIGURATION
# --------------------------------------------------

st.set_page_config(
    page_title="Interactive Business Dashboard",
    page_icon="📊",
    layout="wide"
)

# --------------------------------------------------
# LOAD DATA
# --------------------------------------------------

@st.cache_data
def load_data():
    data = pd.read_csv("interactive_business_dashboard_cleaned.csv")
    data["Date"] = pd.to_datetime(data["Date"], errors="coerce")

    # Calculate churn percentage
    data["Churn_%"] = (
        data["Churned_Users"] / data["Active_Users"] * 100
    ).fillna(0)

    return data


df = load_data()

# --------------------------------------------------
# TITLE
# --------------------------------------------------

st.title("📊 Interactive Business Dashboard")
st.markdown(
    "### Business Performance Analysis"
)

st.divider()

# --------------------------------------------------
# SIDEBAR FILTERS
# --------------------------------------------------

st.sidebar.header("🔎 Dashboard Filters")

# Date filter
min_date = df["Date"].min().date()
max_date = df["Date"].max().date()

selected_dates = st.sidebar.date_input(
    "Select Date Range",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date
)

# Region filter
regions = sorted(df["Region"].unique())

selected_regions = st.sidebar.multiselect(
    "Select Region",
    options=regions,
    default=regions
)

# Category filter
categories = sorted(df["Category"].unique())

selected_categories = st.sidebar.multiselect(
    "Select Category",
    options=categories,
    default=categories
)

# --------------------------------------------------
# APPLY FILTERS
# --------------------------------------------------

filtered_df = df.copy()

# Date filtering
if isinstance(selected_dates, tuple) and len(selected_dates) == 2:
    start_date = pd.Timestamp(selected_dates[0])
    end_date = pd.Timestamp(selected_dates[1])

    filtered_df = filtered_df[
        (filtered_df["Date"] >= start_date)
        & (filtered_df["Date"] <= end_date)
    ]

# Region filtering
if selected_regions:
    filtered_df = filtered_df[
        filtered_df["Region"].isin(selected_regions)
    ]

# Category filtering
if selected_categories:
    filtered_df = filtered_df[
        filtered_df["Category"].isin(selected_categories)
    ]

# --------------------------------------------------
# KPI CALCULATIONS
# --------------------------------------------------

total_revenue = filtered_df["Revenue"].sum()

active_users = filtered_df["Active_Users"].sum()

churned_users = filtered_df["Churned_Users"].sum()

churn_percentage = (
    churned_users / active_users * 100
    if active_users > 0
    else 0
)

total_transactions = filtered_df["Transactions"].sum()

average_ticket = (
    total_revenue / total_transactions
    if total_transactions > 0
    else 0
)

# --------------------------------------------------
# KPI CARDS
# --------------------------------------------------

st.subheader("📌 Key Performance Indicators")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "💰 Total Revenue",
        f"${total_revenue:,.2f}"
    )

with col2:
    st.metric(
        "👥 Active Users",
        f"{active_users:,.0f}"
    )

with col3:
    st.metric(
        "📉 Churn %",
        f"{churn_percentage:.2f}%"
    )

with col4:
    st.metric(
        "🧾 Average Ticket Size",
        f"${average_ticket:,.2f}"
    )

st.divider()

# --------------------------------------------------
# CHECK FILTERED DATA
# --------------------------------------------------

if filtered_df.empty:

    st.warning(
        "No data available for the selected filters."
    )

else:

    # --------------------------------------------------
    # REVENUE TREND
    # --------------------------------------------------

    st.subheader("📈 Revenue Trend")

    revenue_trend = (
        filtered_df
        .groupby("Date", as_index=False)["Revenue"]
        .sum()
    )

    fig_revenue = px.line(
        revenue_trend,
        x="Date",
        y="Revenue",
        markers=True,
        title="Revenue Over Time"
    )

    fig_revenue.update_layout(
        template="plotly_white",
        xaxis_title="Date",
        yaxis_title="Revenue"
    )

    st.plotly_chart(
        fig_revenue,
        use_container_width=True
    )

    # --------------------------------------------------
    # REGION & CATEGORY CHARTS
    # --------------------------------------------------

    col1, col2 = st.columns(2)

    # Revenue by Region
    with col1:

        region_data = (
            filtered_df
            .groupby("Region", as_index=False)["Revenue"]
            .sum()
            .sort_values("Revenue", ascending=False)
        )

        fig_region = px.bar(
            region_data,
            x="Region",
            y="Revenue",
            text_auto=".2s",
            title="💰 Revenue by Region"
        )

        fig_region.update_layout(
            template="plotly_white"
        )

        st.plotly_chart(
            fig_region,
            use_container_width=True
        )

    # Revenue by Category
    with col2:

        category_data = (
            filtered_df
            .groupby("Category", as_index=False)["Revenue"]
            .sum()
            .sort_values("Revenue", ascending=False)
        )

        fig_category = px.bar(
            category_data,
            x="Category",
            y="Revenue",
            text_auto=".2s",
            title="🛍️ Revenue by Category"
        )

        fig_category.update_layout(
            template="plotly_white"
        )

        st.plotly_chart(
            fig_category,
            use_container_width=True
        )

    # --------------------------------------------------
    # ACTIVE USERS & CHURN
    # --------------------------------------------------

    col1, col2 = st.columns(2)

    # Active users by region
    with col1:

        users_region = (
            filtered_df
            .groupby("Region", as_index=False)["Active_Users"]
            .sum()
        )

        fig_users = px.pie(
            users_region,
            names="Region",
            values="Active_Users",
            hole=0.4,
            title="👥 Active Users by Region"
        )

        st.plotly_chart(
            fig_users,
            use_container_width=True
        )

    # Churn by region
    with col2:

        churn_region = (
            filtered_df
            .groupby("Region", as_index=False)
            .agg(
                Active_Users=("Active_Users", "sum"),
                Churned_Users=("Churned_Users", "sum")
            )
        )

        churn_region["Churn_%"] = (
            churn_region["Churned_Users"]
            / churn_region["Active_Users"]
            * 100
        )

        fig_churn = px.bar(
            churn_region,
            x="Region",
            y="Churn_%",
            text_auto=".2f",
            title="📉 Churn Rate by Region"
        )

        fig_churn.update_layout(
            template="plotly_white",
            yaxis_title="Churn %"
        )

        st.plotly_chart(
            fig_churn,
            use_container_width=True
        )

    # --------------------------------------------------
    # CATEGORY PERFORMANCE TABLE
    # --------------------------------------------------

    st.subheader("📊 Category Performance")

    category_performance = (
        filtered_df
        .groupby("Category", as_index=False)
        .agg(
            Revenue=("Revenue", "sum"),
            Transactions=("Transactions", "sum"),
            Active_Users=("Active_Users", "sum")
        )
    )

    category_performance["Average Ticket Size"] = (
        category_performance["Revenue"]
        / category_performance["Transactions"]
    )

    st.dataframe(
        category_performance.style.format({
            "Revenue": "${:,.2f}",
            "Average Ticket Size": "${:,.2f}",
            "Transactions": "{:,.0f}",
            "Active_Users": "{:,.0f}"
        }),
        use_container_width=True,
        hide_index=True
    )

    # --------------------------------------------------
    # BUSINESS INSIGHTS
    # --------------------------------------------------

    st.subheader("💡 Business Insights")

    top_region = (
        filtered_df.groupby("Region")["Revenue"]
        .sum()
        .idxmax()
    )

    top_category = (
        filtered_df.groupby("Category")["Revenue"]
        .sum()
        .idxmax()
    )

    highest_churn = (
        churn_region
        .sort_values("Churn_%", ascending=False)
        .iloc[0]["Region"]
    )

    st.success(
        f"🏆 **Top Revenue Region:** {top_region}"
    )

    st.info(
        f"🛍️ **Top Revenue Category:** {top_category}"
    )

    st.warning(
        f"📉 **Highest Churn Region:** {highest_churn}"
    )

# --------------------------------------------------
# FOOTER
# --------------------------------------------------

st.divider()

st.caption(
    "Interactive Business Dashboard | "
    "Built with Python, Streamlit, Pandas and Plotly"
)