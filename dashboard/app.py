
from pathlib import Path
import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

# ---------------- PAGE CONFIG ----------------

st.set_page_config(
    page_title="RetailIQ | Sales Intelligence",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------------- CUSTOM CSS ----------------

st.markdown("""
<style>
.stApp {
    background: #0B1020;
    color: #F1F5F9;
}
[data-testid="stSidebar"] {
    background: #11182B;
    border-right: 1px solid #29334D;
}
[data-testid="stMetric"] {
    background: linear-gradient(135deg,#17233D,#202A49);
    border: 1px solid #354263;
    padding: 20px;
    border-radius: 15px;
}
[data-testid="stMetricLabel"] {
    color: #AAB7D0 !important;
}
[data-testid="stMetricValue"] {
    color: #FFFFFF !important;
}
h1, h2, h3 {
    color: #FFFFFF !important;
}
p, label {
    color: #B8C3D9;
}
.block-container {
    padding-top: 2rem;
    padding-bottom: 2rem;
}
hr {
    border-color: #29334D;
}
</style>
""", unsafe_allow_html=True)

# ---------------- LOAD DATA ----------------

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_PATH = BASE_DIR / "data" / "cleaned_superstore.csv"

@st.cache_data
def load_data(path):
    data = pd.read_csv(path)

    for col in data.columns:
        if "date" in col.lower():
            data[col] = pd.to_datetime(
                data[col], errors="coerce"
            )

    return data

if not DATA_PATH.exists():
    st.error(f"Dataset not found: {DATA_PATH}")
    st.stop()

df = load_data(str(DATA_PATH))

# ---------------- HEADER ----------------

st.markdown("""
# 📊 RetailIQ
### Sales Intelligence & Business Analytics
""")

st.caption("Explore business performance, discover trends and understand profitability.")

st.divider()

# ---------------- SIDEBAR ----------------

st.sidebar.markdown("# RetailIQ")
st.sidebar.caption("BUSINESS INTELLIGENCE")

st.sidebar.markdown("---")
st.sidebar.subheader("⚙️ Dashboard Filters")

filtered_df = df.copy()

if "Region" in df.columns:
    regions = sorted(df["Region"].dropna().unique())

    selected_regions = st.sidebar.multiselect(
        "Region",
        regions,
        default=regions
    )

    filtered_df = filtered_df[
        filtered_df["Region"].isin(selected_regions)
    ]

if "Category" in df.columns:
    categories = sorted(df["Category"].dropna().unique())

    selected_categories = st.sidebar.multiselect(
        "Category",
        categories,
        default=categories
    )

    filtered_df = filtered_df[
        filtered_df["Category"].isin(selected_categories)
    ]

if "Segment" in df.columns:
    segments = sorted(df["Segment"].dropna().unique())

    selected_segments = st.sidebar.multiselect(
        "Customer Segment",
        segments,
        default=segments
    )

    filtered_df = filtered_df[
        filtered_df["Segment"].isin(selected_segments)
    ]

st.sidebar.markdown("---")
st.sidebar.caption("RetailIQ | Data Analytics Project")

# ---------------- KPI CARDS ----------------

st.markdown("## 📈 Business Overview")

sales = filtered_df["Sales"].sum()
profit = filtered_df["Profit"].sum()
quantity = filtered_df["Quantity"].sum()

orders = (
    filtered_df["Order ID"].nunique()
    if "Order ID" in filtered_df.columns
    else len(filtered_df)
)

margin = profit / sales * 100 if sales else 0

c1, c2, c3, c4 = st.columns(4)

c1.metric("💰 Total Revenue", f"${sales:,.0f}")
c2.metric("📊 Net Profit", f"${profit:,.0f}")
c3.metric("🛒 Total Orders", f"{orders:,}")
c4.metric("📦 Quantity Sold", f"{quantity:,.0f}")

st.caption(f"Overall profit margin: {margin:.2f}%")

st.divider()

# ---------------- SALES ANALYSIS ----------------

st.markdown("## 📊 Sales Performance")

left, right = st.columns(2)

if "Category" in filtered_df.columns:
    with left:
        category_sales = (
            filtered_df.groupby("Category", as_index=False)
            ["Sales"].sum()
        )

        fig = px.bar(
            category_sales,
            x="Category",
            y="Sales",
            color="Category",
            title="Revenue by Category",
            template="plotly_dark"
        )

        fig.update_layout(
            paper_bgcolor="#0B1020",
            plot_bgcolor="#11182B",
            showlegend=False
        )

        st.plotly_chart(fig, use_container_width=True)

if "Region" in filtered_df.columns:
    with right:
        region_profit = (
            filtered_df.groupby("Region", as_index=False)
            ["Profit"].sum()
        )

        fig = px.bar(
            region_profit,
            x="Region",
            y="Profit",
            color="Profit",
            color_continuous_scale="Purples",
            title="Profit by Region",
            template="plotly_dark"
        )

        fig.update_layout(
            paper_bgcolor="#0B1020",
            plot_bgcolor="#11182B"
        )

        st.plotly_chart(fig, use_container_width=True)

st.divider()

# ---------------- CUSTOMER ANALYSIS ----------------

st.markdown("## 👥 Customer Insights")

left, right = st.columns(2)

if "Segment" in filtered_df.columns:
    with left:
        segment_sales = (
            filtered_df.groupby("Segment", as_index=False)
            ["Sales"].sum()
        )

        fig = px.pie(
            segment_sales,
            names="Segment",
            values="Sales",
            hole=0.55,
            title="Sales by Customer Segment",
            template="plotly_dark"
        )

        fig.update_layout(
            paper_bgcolor="#0B1020"
        )

        st.plotly_chart(fig, use_container_width=True)

if "City" in filtered_df.columns:
    with right:
        city_sales = (
            filtered_df.groupby("City", as_index=False)
            ["Sales"].sum()
            .sort_values("Sales", ascending=False)
            .head(10)
        )

        fig = px.bar(
            city_sales.sort_values("Sales"),
            x="Sales",
            y="City",
            orientation="h",
            title="Top 10 Cities by Revenue",
            template="plotly_dark"
        )

        fig.update_layout(
            paper_bgcolor="#0B1020",
            plot_bgcolor="#11182B"
        )

        st.plotly_chart(fig, use_container_width=True)

st.divider()

# ---------------- PRODUCT ANALYSIS ----------------

st.markdown("## 🏆 Product Performance")

if "Product Name" in filtered_df.columns:

    product_profit = (
        filtered_df.groupby("Product Name", as_index=False)
        ["Profit"].sum()
        .sort_values("Profit", ascending=False)
        .head(10)
    )

    fig = px.bar(
        product_profit.sort_values("Profit"),
        x="Profit",
        y="Product Name",
        orientation="h",
        title="Top 10 Profitable Products",
        template="plotly_dark"
    )

    fig.update_layout(
        paper_bgcolor="#0B1020",
        plot_bgcolor="#11182B"
    )

    st.plotly_chart(fig, use_container_width=True)

# ---------------- MONTHLY TRENDS ----------------

date_columns = [
    col for col in filtered_df.columns
    if "date" in col.lower()
]

if date_columns:
    date_col = date_columns[0]

    trend_data = filtered_df.dropna(subset=[date_col]).copy()

    if not trend_data.empty:
        trend_data["Month"] = (
            trend_data[date_col].dt.to_period("M").astype(str)
        )

        monthly_sales = (
            trend_data.groupby("Month", as_index=False)
            ["Sales"].sum()
        )

        st.markdown("## 📅 Monthly Sales Trend")

        fig = px.line(
            monthly_sales,
            x="Month",
            y="Sales",
            markers=True,
            title="Monthly Revenue",
            template="plotly_dark"
        )

        fig.update_layout(
            paper_bgcolor="#0B1020",
            plot_bgcolor="#11182B"
        )

        st.plotly_chart(fig, use_container_width=True)

# ---------------- DATA TABLE ----------------

st.divider()
st.markdown("## 📋 Detailed Sales Records")

st.caption(f"Showing {len(filtered_df):,} records")

st.dataframe(
    filtered_df,
    use_container_width=True,
    hide_index=True
)

# ---------------- DOWNLOAD ----------------

st.download_button(
    "⬇️ Download Filtered Data",
    data=filtered_df.to_csv(index=False).encode("utf-8"),
    file_name="retail_sales_report.csv",
    mime="text/csv"
)

# ---------------- FOOTER ----------------

st.divider()

st.markdown("""
<center>
<h3>RetailIQ</h3>
<p>Built with Python | Pandas | Plotly | Streamlit</p>
<p>Retail Sales Analytics Portfolio Project</p>
</center>
""", unsafe_allow_html=True)
