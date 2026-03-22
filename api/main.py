from fastapi import FastAPI
import psycopg2

app = FastAPI(title="E-commerce Analytics API")

# -----------------------------
# Database Connection Utility
# -----------------------------
def get_db_connection():
    return psycopg2.connect(
        host="localhost",
        database="ecommerce",
        user="admin",
        password="admin123",
        port=5432
    )

# -----------------------------
# Root Health Check
# -----------------------------
@app.get("/")
def root():
    return {"status": "Analytics API running"}

# -----------------------------
# KPI Metrics
# -----------------------------
@app.get("/metrics/kpis")
def get_kpis():
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT
            COUNT(*) AS total_orders,
            COALESCE(SUM(price * quantity), 0) AS total_revenue,
            COALESCE(AVG(price * quantity), 0) AS avg_order_value
        FROM orders;
    """)

    result = cur.fetchone()

    cur.close()
    conn.close()

    return {
        "total_orders": result[0],
        "total_revenue": float(result[1]),
        "avg_order_value": float(result[2])
    }

# -----------------------------
# Sales by Category
# -----------------------------
@app.get("/metrics/sales-by-category")
def sales_by_category():
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT
            product_category,
            SUM(price * quantity) AS revenue
        FROM orders
        GROUP BY product_category
        ORDER BY revenue DESC;
    """)

    rows = cur.fetchall()

    cur.close()
    conn.close()

    return [
        {
            "category": row[0],
            "revenue": float(row[1])
        }
        for row in rows
    ]

# -----------------------------
# Sales by Region
# -----------------------------
@app.get("/metrics/sales-by-region")
def sales_by_region():
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT
            region,
            SUM(price * quantity) AS revenue,
            COUNT(*) AS orders
        FROM orders
        GROUP BY region
        ORDER BY revenue DESC;
    """)

    rows = cur.fetchall()

    cur.close()
    conn.close()

    return [
        {
            "region": row[0],
            "revenue": float(row[1]),
            "orders": row[2]
        }
        for row in rows
    ]

# -----------------------------
# Sales Over Time
# -----------------------------
@app.get("/metrics/sales-over-time")
def sales_over_time():
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT
            DATE(order_time) AS day,
            SUM(price * quantity) AS revenue
        FROM orders
        GROUP BY day
        ORDER BY day;
    """)

    rows = cur.fetchall()

    cur.close()
    conn.close()

    return [
        {
            "date": row[0].isoformat(),
            "revenue": float(row[1])
        }
        for row in rows
    ]
