import streamlit as st
import requests
import pandas as pd
from datetime import datetime
from streamlit_autorefresh import st_autorefresh

API_BASE = "http://127.0.0.1:8001"

st.set_page_config(
    page_title="Real-Time E-commerce Dashboard",
    layout="wide"
)

st_autorefresh(interval=10000, key="datarefresh")

st.title("🛒 Real-Time E-commerce Sales Dashboard")

# -------------------------
# FILTERS
# -------------------------
st.sidebar.header("Filters")

selected_region = st.sidebar.selectbox(
    "Select Region",
    ["All", "North", "South", "East", "West"]
)

selected_category = st.sidebar.selectbox(
    "Select Category",
    ["All", "Electronics", "Fashion", "Home", "Books", "Grocery"]
)

st.caption(f"Last updated: {datetime.now().strftime('%H:%M:%S')}")

# -------------------------
# Helper function
# -------------------------
def safe_get(endpoint):
    try:
        response = requests.get(f"{API_BASE}{endpoint}", timeout=5)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.error(f"Error fetching {endpoint}: {e}")
        return None

# -------------------------
# KPI SECTION
# -------------------------
st.subheader("📊 Key Performance Indicators")

kpis = safe_get("/metrics/kpis")

if kpis:
    col1, col2, col3 = st.columns(3)

    col1.metric("Total Orders", kpis["total_orders"])
    col2.metric("Total Revenue", f"₹ {kpis['total_revenue']:.2f}")
    col3.metric("Avg Order Value", f"₹ {kpis['avg_order_value']:.2f}")
else:
    st.warning("KPI data not available")

st.divider()

# -------------------------
# SALES BY CATEGORY
# -------------------------
st.subheader("📦 Revenue by Category")

cat_data = safe_get("/metrics/sales-by-category")

if isinstance(cat_data, list) and len(cat_data) > 0:
    df_cat = pd.DataFrame(cat_data)

    if selected_category != "All":
        df_cat = df_cat[df_cat["category"] == selected_category]

    st.bar_chart(df_cat.set_index("category")["revenue"])
else:
    st.info("No category data available")

st.divider()

# -------------------------
# SALES BY REGION
# -------------------------
st.subheader("🌍 Revenue by Region")

region_data = safe_get("/metrics/sales-by-region")

if isinstance(region_data, list) and len(region_data) > 0:
    df_region = pd.DataFrame(region_data)

    if selected_region != "All":
        df_region = df_region[df_region["region"] == selected_region]

    st.bar_chart(df_region.set_index("region")["revenue"])
else:
    st.info("No region data available")

st.divider()

# -------------------------
# SALES OVER TIME
# -------------------------
st.subheader("📈 Sales Over Time")

time_data = safe_get("/metrics/sales-over-time")

if isinstance(time_data, list) and len(time_data) > 0:
    df_time = pd.DataFrame(time_data)
    df_time["date"] = pd.to_datetime(df_time["date"])
    st.line_chart(df_time.set_index("date")["revenue"])
else:
    st.info("No time-series data available")
