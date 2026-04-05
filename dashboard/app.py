import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
from streamlit_autorefresh import st_autorefresh

API_BASE = "http://api:8001"

# ─────────────────────────────────────────
# Page config
# ─────────────────────────────────────────
st.set_page_config(
    page_title="Real-Time E-commerce Dashboard",
    page_icon="🛒",
    layout="wide"
)

# Auto-refresh every 15 seconds
st_autorefresh(interval=15000, key="datarefresh")

# ─────────────────────────────────────────
# Color palette per category / region
# ─────────────────────────────────────────
CATEGORY_COLORS = {
    "Electronics": "#4F8EF7",
    "Fashion":     "#F76B6B",
    "Home":        "#F7B731",
    "Books":       "#2BCBBA",
    "Grocery":     "#A55EEA",
}

REGION_COLORS = {
    "North": "#4F8EF7",
    "South": "#F76B6B",
    "East":  "#2BCBBA",
    "West":  "#F7B731",
}

STATUS_COLORS = {
    "delivered":  "#2BCBBA",
    "shipped":    "#4F8EF7",
    "pending":    "#F7B731",
    "cancelled":  "#F76B6B",
}

# ─────────────────────────────────────────
# Sidebar — Filters
# ─────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🎛️ Filters")
    st.markdown("---")

    selected_region = st.selectbox(
        "🌍 Region",
        ["All", "North", "South", "East", "West"]
    )

    selected_category = st.selectbox(
        "📦 Category",
        ["All", "Electronics", "Fashion", "Home", "Books", "Grocery"]
    )

    st.markdown("---")
    st.markdown("## 📅 Time Range")

    granularity = st.radio(
        "Sales chart granularity",
        ["Daily", "Weekly", "Monthly"],
        index=1
    )

    st.markdown("---")
    st.caption(f"🔄 Last updated: {datetime.now().strftime('%H:%M:%S')}")
    st.caption("Auto-refreshes every 15s")

# ─────────────────────────────────────────
# Helper — fetch from API
# ─────────────────────────────────────────
@st.cache_data(ttl=15)
def safe_get(endpoint, region=None, category=None):
    try:
        params = {}
        if region and region != "All":
            params["region"] = region
        if category and category != "All":
            params["category"] = category
        r = requests.get(f"{API_BASE}{endpoint}", params=params, timeout=5)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        st.error(f"API error at {endpoint}: {e}")
        return None

# ─────────────────────────────────────────
# Header
# ─────────────────────────────────────────
st.markdown("# 🛒 Real-Time E-commerce Sales Dashboard")
st.markdown("---")

# ─────────────────────────────────────────
# KPI Section
# ─────────────────────────────────────────
st.markdown("### 📊 Key Performance Indicators")

kpis = safe_get("/metrics/kpis", selected_region, selected_category)

if kpis:
    col1, col2, col3, col4 = st.columns(4)

    col1.metric(
        label="🧾 Total Orders",
        value=f"{kpis['total_orders']:,}",
        delta="Live"
    )
    col2.metric(
        label="💰 Total Revenue",
        value=f"₹{kpis['total_revenue']:,.0f}",
        delta=f"Avg ₹{kpis['avg_order_value']:,.0f}/order"
    )
    col3.metric(
        label="🛍️ Avg Order Value",
        value=f"₹{kpis['avg_order_value']:,.2f}",
    )

    # Delivered rate from status data
    status_data = safe_get("/metrics/order-status", selected_region, selected_category)
    if status_data:
        df_status = pd.DataFrame(status_data)
        total = df_status["count"].sum()
        delivered = df_status[df_status["status"] == "delivered"]["count"].sum() if "delivered" in df_status["status"].values else 0
        rate = (delivered / total * 100) if total else 0
        col4.metric(
            label="✅ Delivery Rate",
            value=f"{rate:.1f}%",
            delta=f"{int(delivered)} delivered"
        )
    else:
        col4.metric(label="✅ Delivery Rate", value="—")
else:
    st.warning("⚠️ KPI data not available")

st.markdown("---")

# ─────────────────────────────────────────
# Row 1 — Category bar + Donut
# ─────────────────────────────────────────
col_left, col_right = st.columns([2, 1])

with col_left:
    st.markdown("### 📦 Revenue by Category")
    cat_data = safe_get("/metrics/sales-by-category", selected_region, selected_category)

    if cat_data:
        df_cat = pd.DataFrame(cat_data)
        df_cat.columns = ["category", "revenue"]

        if selected_category != "All":
            df_cat = df_cat[df_cat["category"] == selected_category]

        df_cat = df_cat.sort_values("revenue", ascending=True)
        df_cat["color"] = df_cat["category"].map(CATEGORY_COLORS)

        fig_cat = px.bar(
            df_cat,
            x="revenue",
            y="category",
            orientation="h",
            color="category",
            color_discrete_map=CATEGORY_COLORS,
            text=df_cat["revenue"].apply(lambda x: f"₹{x:,.0f}"),
            labels={"revenue": "Revenue (₹)", "category": ""},
        )
        fig_cat.update_traces(textposition="outside")
        fig_cat.update_layout(
            showlegend=False,
            height=300,
            margin=dict(l=0, r=40, t=10, b=10),
            xaxis_tickprefix="₹",
            xaxis_tickformat=",",
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
        )
        st.plotly_chart(fig_cat, use_container_width=True)
    else:
        st.info("No category data available")

with col_right:
    st.markdown("### 🍩 Revenue Mix")
    if cat_data:
        df_donut = pd.DataFrame(cat_data)
        df_donut.columns = ["category", "revenue"]

        fig_donut = px.pie(
            df_donut,
            names="category",
            values="revenue",
            color="category",
            color_discrete_map=CATEGORY_COLORS,
            hole=0.55,
        )
        fig_donut.update_traces(
            textposition="inside",
            textinfo="percent",
            hovertemplate="<b>%{label}</b><br>₹%{value:,.0f}<extra></extra>"
        )
        fig_donut.update_layout(
            showlegend=True,
            height=300,
            margin=dict(l=0, r=0, t=10, b=10),
            legend=dict(orientation="v", x=1, y=0.5),
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
        )
        st.plotly_chart(fig_donut, use_container_width=True)

st.markdown("---")

# ─────────────────────────────────────────
# Row 2 — Region bar + Order status donut
# ─────────────────────────────────────────
col_left2, col_right2 = st.columns([2, 1])

with col_left2:
    st.markdown("### 🌍 Revenue by Region")
    region_data = safe_get("/metrics/sales-by-region", selected_region, selected_category)

    if region_data:
        df_region = pd.DataFrame(region_data)

        if selected_region != "All":
            df_region = df_region[df_region["region"] == selected_region]

        df_region = df_region.sort_values("revenue", ascending=True)

        fig_region = px.bar(
            df_region,
            x="revenue",
            y="region",
            orientation="h",
            color="region",
            color_discrete_map=REGION_COLORS,
            text=df_region["revenue"].apply(lambda x: f"₹{x:,.0f}"),
            labels={"revenue": "Revenue (₹)", "region": ""},
        )
        fig_region.update_traces(textposition="outside")
        fig_region.update_layout(
            showlegend=False,
            height=280,
            margin=dict(l=0, r=40, t=10, b=10),
            xaxis_tickprefix="₹",
            xaxis_tickformat=",",
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
        )
        st.plotly_chart(fig_region, use_container_width=True)
    else:
        st.info("No region data available")

with col_right2:
    st.markdown("### 📋 Order Status")
    if status_data:
        df_s = pd.DataFrame(status_data)
        fig_status = px.pie(
            df_s,
            names="status",
            values="count",
            color="status",
            color_discrete_map=STATUS_COLORS,
            hole=0.55,
        )
        fig_status.update_traces(
            textposition="inside",
            textinfo="percent+label",
            hovertemplate="<b>%{label}</b><br>%{value} orders<extra></extra>"
        )
        fig_status.update_layout(
            showlegend=False,
            height=280,
            margin=dict(l=0, r=0, t=10, b=10),
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
        )
        st.plotly_chart(fig_status, use_container_width=True)
    else:
        st.info("No status data")

st.markdown("---")

# ─────────────────────────────────────────
# Sales Over Time
# ─────────────────────────────────────────
st.markdown("### 📈 Sales Over Time")

time_data = safe_get("/metrics/sales-over-time", selected_region, selected_category)

if time_data:
    df_time = pd.DataFrame(time_data)
    df_time["date"] = pd.to_datetime(df_time["date"])
    df_time = df_time.sort_values("date")

    # Apply granularity
    if granularity == "Weekly":
        df_time = df_time.resample("W", on="date").sum().reset_index()
    elif granularity == "Monthly":
        df_time = df_time.resample("ME", on="date").sum().reset_index()

    fig_time = go.Figure()
    fig_time.add_trace(go.Scatter(
        x=df_time["date"],
        y=df_time["revenue"],
        mode="lines+markers",
        line=dict(color="#4F8EF7", width=2.5),
        marker=dict(size=5),
        fill="tozeroy",
        fillcolor="rgba(79,142,247,0.08)",
        hovertemplate="<b>%{x|%d %b %Y}</b><br>₹%{y:,.0f}<extra></extra>"
    ))
    fig_time.update_layout(
        height=350,
        margin=dict(l=0, r=0, t=10, b=10),
        xaxis_title="Date",
        yaxis_title="Revenue (₹)",
        yaxis_tickprefix="₹",
        yaxis_tickformat=",",
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        hovermode="x unified",
    )
    st.plotly_chart(fig_time, use_container_width=True)
else:
    st.info("No time-series data available")

st.markdown("---")

# ─────────────────────────────────────────
# Top Products + Recent Orders
# ─────────────────────────────────────────
col_top, col_orders = st.columns([1, 2])

with col_top:
    st.markdown("### 🏆 Top 10 Products")
    top_data = safe_get("/metrics/top-products", selected_region, selected_category)

    if top_data:
        df_top = pd.DataFrame(top_data)
        df_top.columns = ["product", "revenue"]
        df_top = df_top.sort_values("revenue", ascending=True)

        fig_top = px.bar(
            df_top,
            x="revenue",
            y="product",
            orientation="h",
            text=df_top["revenue"].apply(lambda x: f"₹{x:,.0f}"),
            color_discrete_sequence=["#4F8EF7"],
            labels={"revenue": "Revenue (₹)", "product": ""},
        )
        fig_top.update_traces(textposition="outside", marker_color="#4F8EF7")
        fig_top.update_layout(
            showlegend=False,
            height=400,
            margin=dict(l=0, r=60, t=10, b=10),
            xaxis_tickprefix="₹",
            xaxis_tickformat=",",
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
        )
        st.plotly_chart(fig_top, use_container_width=True)
    else:
        st.info("No product data available")

with col_orders:
    st.markdown("### 🧾 Recent Orders")
    orders_data = safe_get("/orders?limit=20")

    if orders_data:
        df_orders = pd.DataFrame(orders_data)
        if not df_orders.empty:
            # Format for display
            if "price" in df_orders.columns and "quantity" in df_orders.columns:
                df_orders["revenue"] = (df_orders["price"] * df_orders["quantity"]).apply(lambda x: f"₹{x:,.0f}")
            if "order_time" in df_orders.columns:
                df_orders["order_time"] = pd.to_datetime(df_orders["order_time"]).dt.strftime("%d %b %Y %H:%M")

            display_cols = [c for c in ["id", "product", "product_category", "region", "revenue", "status", "order_time"] if c in df_orders.columns]

            st.dataframe(
                df_orders[display_cols].rename(columns={
                    "id": "ID",
                    "product": "Product",
                    "product_category": "Category",
                    "region": "Region",
                    "revenue": "Revenue",
                    "status": "Status",
                    "order_time": "Time"
                }),
                use_container_width=True,
                height=400,
                hide_index=True,
            )
    else:
        st.info("No recent orders available")