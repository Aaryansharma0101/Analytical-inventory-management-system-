import pandas as pd
from database import get_connection

def load_data():
    conn = get_connection()
    products = pd.read_sql("SELECT * FROM products WHERE status = 'active'", conn)
    issues = pd.read_sql("SELECT * FROM issue_logs", conn)
    conn.close()
    return products, issues


def top_issued_products():
    products, issues = load_data()
    if issues.empty:
        return pd.DataFrame()

    usage = issues.groupby("product_id")["issued_qty"].sum().reset_index()

    merged = usage.merge(products, on="product_id")
    return merged.sort_values(by="issued_qty", ascending=False)


def slow_fast_products():
    products, issues = load_data()
    if issues.empty:
        products["issued_qty"] = 0
        return products

    usage = issues.groupby("product_id")["issued_qty"].sum().reset_index()

    merged = products.merge(usage, on="product_id", how="left").fillna(0)
    return merged.sort_values(by="issued_qty", ascending=False)


def dead_stock():
    products, issues = load_data()
    if issues.empty:
        return products

    used_ids = issues["product_id"].unique()
    return products[~products["product_id"].isin(used_ids)]
