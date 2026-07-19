import pandas as pd
from database import get_connection

def predict_stockout_days():
    conn = get_connection()

    # Get products
    products = pd.read_sql("SELECT * FROM products WHERE status = 'active'", conn)

    # Get issue logs
    issues = pd.read_sql("SELECT * FROM issue_logs", conn)

    conn.close()

    if products.empty:
        return []

    predictions = []

    for _, product in products.iterrows():
        product_id = product["product_id"]
        current_stock = product["quantity"]

        product_issues = issues[issues["product_id"] == product_id]

        if product_issues.empty:
            predictions.append({
                "product": product["name"],
                "days_left": None,
                "risk": "NO DATA",
                "stock": current_stock
            })
            continue

        product_issues["date"] = pd.to_datetime(product_issues["date"])

        total_issued = product_issues["issued_qty"].sum()
        days_active = (product_issues["date"].max() - product_issues["date"].min()).days + 1

        avg_daily_usage = total_issued / max(days_active, 1)

        if avg_daily_usage == 0:
            days_left = None
        else:
            days_left = round(current_stock / avg_daily_usage, 1)

        # Risk labeling
        if days_left is None:
            risk = "NO DATA"
        elif days_left < 5:
            risk = "HIGH"
        elif days_left < 15:
            risk = "MEDIUM"
        else:
            risk = "LOW"

        predictions.append({
            "product": product["name"],
            "stock": current_stock,
            "avg_daily_usage": round(avg_daily_usage, 2),
            "days_left": days_left,
            "risk": risk
        })

    return predictions
