from fastapi import FastAPI, Query
from typing import Optional
import psycopg2
import psycopg2.pool
import os

app = FastAPI(title="E-commerce Analytics API")

# ─────────────────────────────────────────
# Connection pool — reads from environment
# ─────────────────────────────────────────
pool = psycopg2.pool.SimpleConnectionPool(
    minconn=1,
    maxconn=10,
    host=os.environ.get("POSTGRES_HOST", "db"),
    database=os.environ.get("POSTGRES_DB", "ecommerce"),
    user=os.environ.get("POSTGRES_USER", "admin"),
    password=os.environ.get("POSTGRES_PASSWORD", "admin123"),
    port=int(os.environ.get("POSTGRES_PORT", 5432))
)

def get_conn():
    return pool.getconn()

def release(conn):
    pool.putconn(conn)

# ─────────────────────────────────────────
# Health
# ─────────────────────────────────────────
@app.get("/")
def root():
    return {"status": "Analytics API running"}

# ─────────────────────────────────────────
# KPI Metrics
# ─────────────────────────────────────────
@app.get("/metrics/kpis")
def get_kpis(
    region:   Optional[str] = Query(None),
    category: Optional[str] = Query(None),
):
    conn = get_conn()
    cur = conn.cursor()

    filters, params = [], []
    if region and region != "All":
        filters.append("region = %s");   params.append(region)
    if category and category != "All":
        filters.append("product_category = %s"); params.append(category)

    where = ("WHERE " + " AND ".join(filters)) if filters else ""

    cur.execute(f"""
        SELECT
            COUNT(*)                            AS total_orders,
            COALESCE(SUM(price * quantity), 0)  AS total_revenue,
            COALESCE(AVG(price * quantity), 0)  AS avg_order_value
        FROM orders {where};
    """, params)

    row = cur.fetchone()
    cur.close(); release(conn)

    return {
        "total_orders":    row[0],
        "total_revenue":   float(row[1]),
        "avg_order_value": float(row[2])
    }

# ─────────────────────────────────────────
# Sales by Category
# ─────────────────────────────────────────
@app.get("/metrics/sales-by-category")
def sales_by_category(
    region:   Optional[str] = Query(None),
    category: Optional[str] = Query(None),
):
    conn = get_conn(); cur = conn.cursor()

    filters, params = [], []
    if region and region != "All":
        filters.append("region = %s"); params.append(region)
    if category and category != "All":
        filters.append("product_category = %s"); params.append(category)

    where = ("WHERE " + " AND ".join(filters)) if filters else ""

    cur.execute(f"""
        SELECT product_category, SUM(price * quantity) AS revenue
        FROM orders {where}
        GROUP BY product_category
        ORDER BY revenue DESC;
    """, params)

    rows = cur.fetchall()
    cur.close(); release(conn)
    return [{"category": r[0], "revenue": float(r[1])} for r in rows]

# ─────────────────────────────────────────
# Sales by Region
# ─────────────────────────────────────────
@app.get("/metrics/sales-by-region")
def sales_by_region(
    region:   Optional[str] = Query(None),
    category: Optional[str] = Query(None),
):
    conn = get_conn(); cur = conn.cursor()

    filters, params = [], []
    if region and region != "All":
        filters.append("region = %s"); params.append(region)
    if category and category != "All":
        filters.append("product_category = %s"); params.append(category)

    where = ("WHERE " + " AND ".join(filters)) if filters else ""

    cur.execute(f"""
        SELECT region, SUM(price * quantity) AS revenue, COUNT(*) AS orders
        FROM orders {where}
        GROUP BY region
        ORDER BY revenue DESC;
    """, params)

    rows = cur.fetchall()
    cur.close(); release(conn)
    return [{"region": r[0], "revenue": float(r[1]), "orders": r[2]} for r in rows]

# ─────────────────────────────────────────
# Sales Over Time
# ─────────────────────────────────────────
@app.get("/metrics/sales-over-time")
def sales_over_time(
    region:   Optional[str] = Query(None),
    category: Optional[str] = Query(None),
):
    conn = get_conn(); cur = conn.cursor()

    filters, params = [], []
    if region and region != "All":
        filters.append("region = %s"); params.append(region)
    if category and category != "All":
        filters.append("product_category = %s"); params.append(category)

    where = ("WHERE " + " AND ".join(filters)) if filters else ""

    cur.execute(f"""
        SELECT DATE(order_time) AS day, SUM(price * quantity) AS revenue
        FROM orders {where}
        GROUP BY day
        ORDER BY day;
    """, params)

    rows = cur.fetchall()
    cur.close(); release(conn)
    return [{"date": r[0].isoformat(), "revenue": float(r[1])} for r in rows]

# ─────────────────────────────────────────
# Order Status breakdown  ← NEW
# ─────────────────────────────────────────
@app.get("/metrics/order-status")
def order_status(
    region:   Optional[str] = Query(None),
    category: Optional[str] = Query(None),
):
    conn = get_conn(); cur = conn.cursor()

    filters, params = [], []
    if region and region != "All":
        filters.append("region = %s"); params.append(region)
    if category and category != "All":
        filters.append("product_category = %s"); params.append(category)

    where = ("WHERE " + " AND ".join(filters)) if filters else ""

    cur.execute(f"""
        SELECT status, COUNT(*) AS count
        FROM orders {where}
        GROUP BY status
        ORDER BY count DESC;
    """, params)

    rows = cur.fetchall()
    cur.close(); release(conn)
    return [{"status": r[0], "count": r[1]} for r in rows]

# ─────────────────────────────────────────
# Top Products  ← NEW
# ─────────────────────────────────────────
@app.get("/metrics/top-products")
def top_products(
    region:   Optional[str] = Query(None),
    category: Optional[str] = Query(None),
    limit:    int = Query(10),
):
    conn = get_conn(); cur = conn.cursor()

    filters, params = [], []
    if region and region != "All":
        filters.append("region = %s"); params.append(region)
    if category and category != "All":
        filters.append("product_category = %s"); params.append(category)

    where = ("WHERE " + " AND ".join(filters)) if filters else ""
    params.append(limit)

    cur.execute(f"""
        SELECT product, SUM(price * quantity) AS revenue
        FROM orders {where}
        GROUP BY product
        ORDER BY revenue DESC
        LIMIT %s;
    """, params)

    rows = cur.fetchall()
    cur.close(); release(conn)
    return [{"product": r[0], "revenue": float(r[1])} for r in rows]

# ─────────────────────────────────────────
# Recent Orders  ← ENHANCED
# ─────────────────────────────────────────
@app.get("/orders")
def get_orders(limit: int = Query(20)):
    conn = get_conn(); cur = conn.cursor()

    cur.execute("""
        SELECT id, product, product_category, region,
               price, quantity, status, order_time
        FROM orders
        ORDER BY order_time DESC
        LIMIT %s;
    """, (limit,))

    rows = cur.fetchall()
    cur.close(); release(conn)

    return [
        {
            "id":               r[0],
            "product":          r[1],
            "product_category": r[2],
            "region":           r[3],
            "price":            float(r[4]),
            "quantity":         r[5],
            "status":           r[6],
            "order_time":       r[7].isoformat()
        }
        for r in rows
    ]