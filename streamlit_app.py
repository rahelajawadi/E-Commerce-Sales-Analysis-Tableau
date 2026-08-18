import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(
    page_title="E-Commerce Sales Analysis",
    page_icon="📊",
    layout="wide"
)

st.title("E-Commerce Sales Analysis")
st.caption("Interactive sales analysis dashboard built with Python and Streamlit")

# Load Sample Superstore data
DATA_URL = (
    "https://raw.githubusercontent.com/plotly/datasets/master/"
    "superstore.csv"
)

@st.cache_data
def load_data():
    df = pd.read_csv(DATA_URL)

    df["Order Date"] = pd.to_datetime(df["Order Date"])
    df["Sales"] = pd.to_numeric(df["Sales"], errors="coerce")
    df["Profit"] = pd.to_numeric(df["Profit"], errors="coerce")
    df["Quantity"] = pd.to_numeric(df["Quantity"], errors="coerce")

    return df.dropna(subset=["Sales", "Profit", "Quantity"])


df = load_data()

# Sidebar filters
st.sidebar.header("Filters")

regions = st.sidebar.multiselect(
    "Region",
    sorted(df["Region"].dropna().unique()),
    default=sorted(df["Region"].dropna().unique())
)

categories = st.sidebar.multiselect(
    "Category",
    sorted(df["Category"].dropna().unique()),
    default=sorted(df["Category"].dropna().unique())
)

ship_modes = st.sidebar.multiselect(
    "Ship Mode",
    sorted(df["Ship Mode"].dropna().unique()),
    default=sorted(df["Ship Mode"].dropna().unique())
)

date_range = st.sidebar.date_input(
    "Order Date",
    value=(df["Order Date"].min().date(), df["Order Date"].max().date())
)

# Apply filters
filtered_df = df[
    df["Region"].isin(regions)
    & df["Category"].isin(categories)
    & df["Ship Mode"].isin(ship_modes)
    & (df["Order Date"].dt.date >= date_range[0])
    & (df["Order Date"].dt.date <= date_range[1])
]

# KPI cards
total_sales = filtered_df["Sales"].sum()
total_profit = filtered_df["Profit"].sum()
total_quantity = filtered_df["Quantity"].sum()

col1, col2, col3 = st.columns(3)

col1.metric("Total Sales", f"${total_sales:,.2f}")
col2.metric("Total Profit", f"${total_profit:,.2f}")
col3.metric("Total Quantity", f"{total_quantity:,.0f}")

st.divider()

# Sales over time
monthly_sales = (
    filtered_df
    .set_index("Order Date")
    .resample("ME")["Sales"]
    .sum()
    .reset_index()
)

fig_sales = px.line(
    monthly_sales,
    x="Order Date",
    y="Sales",
    markers=True,
    title="Sales Over Time"
)

st.plotly_chart(fig_sales, use_container_width=True)

# Sales by category and region
col1, col2 = st.columns(2)

with col1:
    category_sales = (
        filtered_df.groupby("Category", as_index=False)["Sales"]
        .sum()
        .sort_values("Sales", ascending=False)
    )

    fig_category = px.bar(
        category_sales,
        x="Category",
        y="Sales",
        title="Sales by Category",
        text_auto=".2s"
    )

    st.plotly_chart(fig_category, use_container_width=True)

with col2:
    region_sales = (
        filtered_df.groupby("Region", as_index=False)["Sales"]
        .sum()
        .sort_values("Sales", ascending=False)
    )

    fig_region = px.bar(
        region_sales,
        x="Region",
        y="Sales",
        title="Sales by Region",
        text_auto=".2s"
    )

    st.plotly_chart(fig_region, use_container_width=True)

# Profit by category
profit_category = (
    filtered_df.groupby("Category", as_index=False)["Profit"]
    .sum()
    .sort_values("Profit", ascending=False)
)

fig_profit = px.bar(
    profit_category,
    x="Category",
    y="Profit",
    title="Profit by Category",
    text_auto=".2s"
)

st.plotly_chart(fig_profit, use_container_width=True)

# Ship mode analysis
ship_mode_sales = (
    filtered_df.groupby("Ship Mode", as_index=False)["Sales"]
    .sum()
)

fig_ship = px.pie(
    ship_mode_sales,
    names="Ship Mode",
    values="Sales",
    title="Sales by Ship Mode"
)

st.plotly_chart(fig_ship, use_container_width=True)

# Top products
st.subheader("Top Products by Sales")

top_products = (
    filtered_df.groupby("Product Name", as_index=False)["Sales"]
    .sum()
    .sort_values("Sales", ascending=False)
    .head(10)
)

fig_products = px.bar(
    top_products.sort_values("Sales"),
    x="Sales",
    y="Product Name",
    orientation="h",
    title="Top 10 Products"
)

st.plotly_chart(fig_products, use_container_width=True)

# Filtered data
st.subheader("Filtered Sales Data")

st.dataframe(
    filtered_df,
    use_container_width=True,
    hide_index=True
)

# CSV download
csv = filtered_df.to_csv(index=False).encode("utf-8")

st.download_button(
    label="Download Filtered Data",
    data=csv,
    file_name="filtered_sales_data.csv",
    mime="text/csv"
)
