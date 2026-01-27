import streamlit as st
import pandas as pd

from database import init_db
from Product_service import add_product, get_all_products, update_product
from stock_service import update_stock, get_stock_history
from issue_service import issue_product, get_issue_logs
from Product_service import add_product, get_all_products, update_product, delete_product
from Stockout_prediction import predict_stockout_days
from Usage_analytics import top_issued_products, slow_fast_products, dead_stock




st.set_page_config(page_title="Smart Inventory System", layout="wide")
init_db()

st.title("📦 Smart Inventory Management System")

tabs = st.tabs([
    "➕ Products",
    "📥 Add Stock",
    "📤 Issue Stock",
    "📋 Inventory (Edit)",
    "📜 Logs",
    "🧠 Smart Alerts",
    "📊 Analytics Dashboard"
])

# ---------------- TAB 1 — ADD PRODUCTS ----------------
with tabs[0]:
    st.header("➕ Add New Product")

    with st.form("add_product_form"):
        col1, col2 = st.columns(2)

        with col1:
            name = st.text_input("Product Name")
            category = st.text_input("Category")
            supplier = st.text_input("Supplier")

        with col2:
            quantity = st.number_input("Initial Quantity", min_value=0, step=1)
            min_stock = st.number_input("Min Stock Alert Level", min_value=0, step=1, value=5)
            cost_price = st.number_input("Cost Price", min_value=0.0, step=0.1)
            sell_price = st.number_input("Sell Price", min_value=0.0, step=0.1)

        submitted = st.form_submit_button("Add Product")

        if submitted:
            if name.strip() == "":
                st.error("Product name is required")
            else:
                add_product(name, category, quantity, min_stock, supplier, cost_price, sell_price)
                st.success(f"Product '{name}' added successfully!")

# ---------------- TAB 2 — ADD STOCK ----------------
with tabs[1]:
    st.header("📥 Add Stock")

    products = get_all_products()

    if products:
        product_map = {p["name"]: p["product_id"] for p in products}

        selected = st.selectbox(
            "Select Product",
            list(product_map.keys()),
            key="add_stock_product"
        )

        qty = st.number_input("Quantity to Add", min_value=1, step=1, key="add_stock_qty")
        notes = st.text_input("Notes (optional)", key="add_stock_notes")

        if st.button("Add Stock", key="add_stock_button"):
            update_stock(product_map[selected], qty, "ADD", notes)
            st.success("Stock updated successfully!")
            st.rerun()
    else:
        st.info("No products available.")

# ---------------- TAB 3 — ISSUE STOCK ----------------
with tabs[2]:
    st.header("📤 Issue Stock")

    products = get_all_products()

    if products:
        product_map = {p["name"]: p for p in products}

        selected = st.selectbox(
            "Select Product",
            list(product_map.keys()),
            key="issue_stock_product"
        )

        product = product_map[selected]
        available = product["quantity"]

        st.write(f"Available Stock: **{available}**")

        qty = st.number_input("Quantity to Issue", min_value=1, step=1, key="issue_qty")
        issued_to = st.text_input("Issued To (Person / Dept)", key="issue_to")
        remarks = st.text_input("Remarks", key="issue_remarks")

        if st.button("Issue Product", key="issue_button"):
            if qty > available:
                st.error("Not enough stock available!")
            elif issued_to.strip() == "":
                st.error("Please enter who the item is issued to.")
            else:
                issue_product(product["product_id"], qty, issued_to, "Admin", remarks)
                st.success("Product issued successfully!")
                st.rerun()
    else:
        st.info("No products available.")

# ---------------- TAB 4 — INVENTORY VIEW & EDIT ----------------
# --- TAB 4: VIEW & EDIT INVENTORY ---
# ---------------- TAB 4 — INVENTORY VIEW, EDIT & DELETE ----------------
with tabs[3]:
    st.header("📋 Product Inventory")

    products = get_all_products()

    if products:
        df = pd.DataFrame(products)
        st.dataframe(df, use_container_width=True)

        st.subheader("✏️ Edit Product")

        product_map = {f"{p['name']} (ID {p['product_id']})": p for p in products}
        selected = st.selectbox(
            "Select Product to Edit or Delete",
            list(product_map.keys()),
            key="edit_product_select"
        )

        product = product_map[selected]

        col1, col2 = st.columns([3, 1])

        # ---- EDIT FORM ----
        with col1:
            with st.form("edit_product_form"):
                colA, colB = st.columns(2)

                with colA:
                    name = st.text_input("Product Name", value=product["name"])
                    category = st.text_input("Category", value=product["category"])
                    supplier = st.text_input("Supplier", value=product["supplier"])

                with colB:
                    min_stock = st.number_input("Min Stock", value=int(product["min_stock"]), step=1)
                    cost_price = st.number_input("Cost Price", value=float(product["cost_price"] or 0))
                    sell_price = st.number_input("Sell Price", value=float(product["sell_price"] or 0))

                updated = st.form_submit_button("Update Product")

                if updated:
                    update_product(
                        product["product_id"],
                        name,
                        category,
                        supplier,
                        min_stock,
                        cost_price,
                        sell_price
                    )
                    st.success("Product updated successfully!")
                    st.rerun()

        # ---- DELETE BUTTON ----
        with col2:
            st.subheader("🗑️ Delete Product")

            if st.button("Delete Product", key="delete_product_button"):
                delete_product(product["product_id"])
                st.warning("Product deleted (archived)!")
                st.rerun()

    else:
        st.info("No products available.")


# ---------------- TAB 5 — LOGS ----------------
with tabs[4]:
    st.header("📜 Stock Movement History")

    history = get_stock_history()
    if history:
        st.dataframe(pd.DataFrame(history), use_container_width=True)
    else:
        st.info("No stock movements yet.")

    st.header("📤 Issue Logs")

    issues = get_issue_logs()
    if issues:
        st.dataframe(pd.DataFrame(issues), use_container_width=True)
    else:
        st.info("No issued products yet.")

# ---------------- TAB 6 — SMART LOW STOCK PREDICTION ----------------
with tabs[5]:
    st.header("🧠 Smart Low Stock Prediction")

    predictions = predict_stockout_days()

    if predictions:
        df = pd.DataFrame(predictions)

        def highlight_risk(row):
            if row["risk"] == "HIGH":
                return ["background-color: #ff4d4d"] * len(row)
            elif row["risk"] == "MEDIUM":
                return ["background-color: #fff3cd"] * len(row)
            elif row["risk"] == "LOW":
                return ["background-color: #d4edda"] * len(row)
            return [""] * len(row)

        st.dataframe(df.style.apply(highlight_risk, axis=1), use_container_width=True)

        st.caption("HIGH = urgent restock | MEDIUM = monitor | LOW = safe")
    else:
        st.info("No prediction data available yet.")

# ---------------- TAB 7 — ANALYTICS DASHBOARD ----------------
with tabs[6]:
    st.header("📊 Inventory Analytics Dashboard")

    top_products = top_issued_products()
    fast_slow = slow_fast_products()
    dead = dead_stock()

    # ---- KPI Metrics ----
    st.subheader("📌 Key Stats")

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Products", len(get_all_products()))
    with col2:
        st.metric("Total Issued Items", int(top_products["issued_qty"].sum()) if not top_products.empty else 0)
    with col3:
        st.metric("Dead Stock Items", len(dead))

    # ---- Top Issued Products Chart ----
    st.subheader("🏆 Top Issued Products")

    if not top_products.empty:
        chart_data = top_products[["name", "issued_qty"]].set_index("name")
        st.bar_chart(chart_data)
    else:
        st.info("No issue data yet.")

    # ---- Fast vs Slow Moving ----
    st.subheader("🔥 Fast vs Slow Moving Products")

    if not fast_slow.empty:
        st.dataframe(fast_slow[["name", "issued_qty", "quantity"]])
    else:
        st.info("No usage trend data yet.")

    # ---- Dead Stock ----
    st.subheader("🧊 Dead Stock (Unused Items)")

    if not dead.empty:
        st.dataframe(dead[["name", "quantity"]], use_container_width=True)
    else:
        st.success("No dead stock — all products are moving!")
