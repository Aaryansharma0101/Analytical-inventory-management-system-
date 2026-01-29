import streamlit as st
import pandas as pd
from database import init_db
from Product_service import add_product, get_all_products, update_product
from stock_service import update_stock, get_stock_history
from issue_service import issue_product, get_issue_logs
from Product_service import add_product, get_all_products, update_product, delete_product
from auth_service import register_user, login_user
from database import init_db
import io 

init_db()

st.set_page_config(
    page_title="Priya engineering And Supplier",
    page_icon="📦",
    layout="wide"
)





# SESSION INIT
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.user = None


# LOGIN / REGISTER SCREEN
if not st.session_state.logged_in:
    st.title("🔐 Login")

    tab1, tab2 = st.tabs(["Login", "Register"])

    # LOGIN TAB
    with tab1:
        login_identifier = st.text_input("Username or Email", key="login_identifier_input")
        login_password = st.text_input("Password", type="password", key="login_password_input")

        if st.button("Login", key="login_btn"):
            success, msg, user = login_user(login_identifier, login_password)

            if success:
                st.session_state.logged_in = True
                st.session_state.user = user
                st.success("Login successful!")
                st.rerun()
            else:
                st.error(msg)

    # REGISTER TAB
    with tab2:
        reg_username = st.text_input("Choose Username", key="register_username_input")
        reg_email = st.text_input("Email", key="register_email_input")
        reg_password = st.text_input("Password", type="password", key="register_password_input")

        if st.button("Register", key="register_btn"):
            success, msg = register_user(reg_username, reg_email, reg_password)

            if success:
                st.success(msg)
            else:
                st.error(msg)

    st.stop()

role = st.session_state.user["role"]
st.sidebar.markdown("## 👤 User Panel")
st.sidebar.write(f"**Username:** {st.session_state.user['username']}")
st.sidebar.write(f"**Role:** {role.upper()}")
st.sidebar.divider()

if st.sidebar.button("🚪 Logout"):
    st.session_state.logged_in = False
    st.session_state.user = None
    st.rerun()

if role == "admin":
    # existing add product UI here
    pass
else:
    st.warning("Only Admin can add products.")

if role == "admin":
    if st.button("Delete Product"):
        delete_product(products["product_id"])
else:
    st.info("Delete restricted to Admin.")

if role == "admin":
    # show logs
    pass
else:
    st.warning("Logs are Admin-only.")

st.set_page_config(page_title="Smart Inventory System", layout="wide")
init_db()

st.title("Priya engineering And Suppliers")

tabs = st.tabs([
    "➕ Products",
    "📥 Add Stock",
    "📤 Issue Stock",
    "📋 Inventory (Edit)",
    "📜 Logs",
    "📊 Interconnected Reports"
])

# ---------------- TAB 1 — ADD PRODUCTS ----------------
with tabs[0]:
    st.header("➕ Add New Product")

    with st.form("add_product_form"):
        col1, col2 = st.columns(2)

        with col1:
            name = st.text_input("item")
            category = st.text_input("Project")
            supplier = st.text_input("Supplier")
            item_code = st.text_input("Item Code")
            contract_no = st.text_input("Contract No.")


        with col2:
            unit_type = st.selectbox("Unit Type", ["Meter", "Quantity"])
            quantity = st.number_input("Enter Value", min_value=0, step=1)
            min_stock = st.number_input("Min Stock Alert Level", min_value=0, step=1, value=5)
            cost_price = st.number_input("Cost Price", min_value=0.0, step=0.1)
            sell_price = st.number_input("Sell Price", min_value=0.0, step=0.1)

        submitted = st.form_submit_button("Add Product")

        if submitted:
            if name.strip() == "":
                st.error("Product name is required")
            else:
                add_product(name, category, quantity, unit_type, min_stock, supplier, cost_price, sell_price)
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
    st.header("📤 Issue Product")

    products = get_all_products()

    if products:
        product_map = {p["name"]: p["product_id"] for p in products}
        selected = st.selectbox("Select Product", list(product_map.keys()), key="issue_product")

        issued_to = st.text_input("Issued To", key="issue_to")
        issued_qty = st.number_input("Issued Quantity", min_value=1, step=1, key="issue_qty")

        st.subheader("🔥 Consumption (Optional)")
        used_qty = st.number_input("Used Quantity", min_value=0, step=1, key="used_qty")
        usage_purpose = st.text_input("What was it used for?", key="usage_purpose")

        remaining_qty = issued_qty - used_qty
        st.info(f"Remaining with user: {remaining_qty}")

        if st.button("📤 Submit Issue"):
            if used_qty > issued_qty:
                st.error("Used quantity cannot exceed issued quantity")
            else:
                issue_product(
                    product_map[selected],
                    issued_to,
                    st.session_state.user["username"],
                    issued_qty,
                    used_qty,
                    usage_purpose
                )
                st.success("Issue recorded successfully!")
                st.rerun()

    else:
        st.info("No products available.")

# ---------------- TAB 4 — INVENTORY VIEW & EDIT ----------------
# --- TAB 4: VIEW & EDIT INVENTORY ---
# ---------------- TAB 4 — INVENTORY VIEW, EDIT & DELETE ----------------
with tabs[3]:
    st.header("📋 Product Inventory")

    products = get_all_products()
    total_products = len(products)
    low_stock = len([p for p in products if p["quantity"] <= p["min_stock"]])

    col1, col2, col3 = st.columns(3)

    col1.metric("📦 Total Products", total_products)
    col2.metric("⚠️ Low Stock Items", low_stock)
    col3.metric("📤 Total Issues", len(get_issue_logs()))

    if products:
        df = pd.DataFrame(products)

        # Combine quantity + unit type
        df["Stock"] = df["quantity"].astype(str) + " " + df["unit_type"]

        # Optional stock warning label
        df["Stock Status"] = df.apply(
            lambda x: "⚠️ LOW" if x["quantity"] <= x["min_stock"] else "✅ OK",
            axis=1
        )

        # Hide raw columns if you want
        df_display = df.drop(columns=["quantity", "unit_type"])

        st.dataframe(df_display, use_container_width=True)
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


# ---------------- TAB 7 — INTERCONNECTED REPORTS ----------------

with tabs[5]:
    st.header("📊 Interconnected Reports")
    st.caption("Filter usage by Person, Product, Category, or Issuer")

    from reports_service import get_interconnected_data

    data = get_interconnected_data()

    if not data:
        st.info("No issue or consumption records found yet.")
    else:
        df = pd.DataFrame(data)

        mode = st.selectbox(
            "View By",
            ["Person", "Product", "Category", "Issuer"],
            key="report_mode"
        )

        if mode == "Person":
            options = sorted(df["issued_to"].dropna().unique())
            selected = st.selectbox("Select Person", options)
            filtered = df[df["issued_to"] == selected]

        elif mode == "Product":
            options = sorted(df["product"].dropna().unique())
            selected = st.selectbox("Select Product", options)
            filtered = df[df["product"] == selected]

        elif mode == "Category":
            options = sorted(df["category"].dropna().unique())
            selected = st.selectbox("Select Category", options)
            filtered = df[df["category"] == selected]

        elif mode == "Issuer":
            options = sorted(df["issued_by"].dropna().unique())
            selected = st.selectbox("Select Issuer", options)
            filtered = df[df["issued_by"] == selected]

        st.subheader("📋 Filtered Results")

        display_cols = [
            "issued_to", "product", "category",
            "issued_by", "issued_qty",
            "used_qty", "remaining_qty",
            "usage_purpose", "date"
        ]

        filtered_display = filtered[display_cols]

        st.dataframe(filtered_display, use_container_width=True)

        # -------- EXPORT TO EXCEL --------
        st.subheader("📤 Export Report")

        buffer = io.BytesIO()

        with pd.ExcelWriter(buffer, engine="xlsxwriter") as writer:
            filtered_display.to_excel(writer, sheet_name="Report", index=False)

        st.download_button(
            label="📥 Download Excel Report",
            data=buffer.getvalue(),
            file_name="interconnected_report.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
