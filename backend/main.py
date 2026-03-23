from fastapi import FastAPI
from pydantic import BaseModel
import psycopg2

app = FastAPI(title="Backend Order API")

# -----------------------------
# DB Connection
# -----------------------------
def get_db_connection():
    return psycopg2.connect(
        host="db",
        database="ecommerce",
        user="admin",
        password="admin123",
        port=5432
    )

# -----------------------------
# Model
# -----------------------------
class Order(BaseModel):
    product: str
    category: str
    region: str
    amount: float

# -----------------------------
# Create Order API
# -----------------------------
@app.post("/create-order")
def create_order(order: Order):
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute(
        """
        INSERT INTO orders (product, category, region, amount)
        VALUES (%s, %s, %s, %s)
        """,
        (order.product, order.category, order.region, order.amount)
    )

    conn.commit()
    cur.close()
    conn.close()

    return {"message": "Order created successfully"}

# -----------------------------
# Get Orders API
# -----------------------------
@app.get("/orders")
def get_orders():
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("SELECT * FROM orders ORDER BY id DESC LIMIT 20")
    rows = cur.fetchall()

    cur.close()
    conn.close()

    return {"orders": rows}