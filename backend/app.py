from flask import Flask, request, jsonify
from collections import defaultdict
from datetime import datetime

app = Flask(__name__)

# In-memory store
orders = []

# -------------------------
# Health
# -------------------------
@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"}), 200


# -------------------------
# Orders
# -------------------------
@app.route("/orders", methods=["POST"])
def create_order():
    data = request.get_json()

    if not data or "amount" not in data:
        return jsonify({"error": "Invalid order data"}), 400

    # enrich order with mock fields
    order = {
        "amount": data["amount"],
        "category": data.get("category", "General"),
        "region": data.get("region", "India"),
        "date": datetime.now().strftime("%Y-%m-%d")
    }

    orders.append(order)
    return jsonify({"message": "Order created", "order": order}), 201


@app.route("/orders", methods=["GET"])
def get_orders():
    return jsonify(orders), 200


# -------------------------
# Metrics (Dashboard needs these)
# -------------------------
@app.route("/metrics/kpis", methods=["GET"])
def kpis():
    total_orders = len(orders)
    total_revenue = sum(o["amount"] for o in orders)
    avg_order_value = total_revenue / total_orders if total_orders else 0

    return jsonify({
        "total_orders": total_orders,
        "total_revenue": total_revenue,
        "avg_order_value": avg_order_value
    })


@app.route("/metrics/sales-by-category", methods=["GET"])
def sales_by_category():
    result = defaultdict(float)
    for o in orders:
        result[o["category"]] += o["amount"]

    return jsonify([
        {"category": k, "revenue": v} for k, v in result.items()
    ])


@app.route("/metrics/sales-by-region", methods=["GET"])
def sales_by_region():
    result = defaultdict(float)
    for o in orders:
        result[o["region"]] += o["amount"]

    return jsonify([
        {"region": k, "revenue": v} for k, v in result.items()
    ])


@app.route("/metrics/sales-over-time", methods=["GET"])
def sales_over_time():
    result = defaultdict(float)
    for o in orders:
        result[o["date"]] += o["amount"]

    return jsonify([
        {"date": k, "revenue": v} for k, v in sorted(result.items())
    ])


# -------------------------
# Run
# -------------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8001)
