import streamlit as st
import pandas as pd
import io
from issue_service import update_issue
from database import init_db
from Product_service import add_product, get_all_products, update_product, delete_product
from stock_service import update_stock, get_stock_history
from issue_service import issue_product, get_issue_logs
from auth_service import register_user, login_user
from reports_service import get_interconnected_data

import time

def safe_action_lock(key, cooldown=2):
    """
    Prevents double-click actions for 'cooldown' seconds.
    """
    now = time.time()

    if key not in st.session_state:
        st.session_state[key] = 0

    if now - st.session_state[key] < cooldown:
        return False  # blocked

    st.session_state[key] = now
    return True



# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="Priya engineering And Suppliers",
    page_icon="📦",
    layout="wide"
)

st.markdown("""
<h2 style="margin-bottom:0;">Priya Engineering And Supplier</h2>
<p style="color:gray; margin-top:0;">Internal Operations Dashboard</p>

<style>

/* FORCE override multiselect chip background */
span[data-baseweb="tag"] {
    background-color: #1f2933 !important;
    color: #e5e7eb !important;
    border: 1px solid #374151 !important;
}

/* Remove red close button */
span[data-baseweb="tag"] svg {
    fill: #9ca3af !important;
}

/* Hover effect */
span[data-baseweb="tag"]:hover {
    background-color: #374151 !important;
}

/* Dropdown list background */
div[role="listbox"] {
    background-color: #0f172a !important;
}

/* Selected multiselect input background */
div[data-baseweb="select"] > div {
    background-color: #020617 !important;
}

            
/* ===================== ODOO DARK BLUE → BLACK GRADIENT BACKGROUND ===================== */

/* Main App Gradient */
.stApp {
    background: linear-gradient(160deg, #020617 0%, #0f172a 45%, #020617 100%) !important;
    background-attachment: fixed !important;
}

/* Sidebar Gradient */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #020617 0%, #0b1220 100%) !important;
    border-right: 1px solid rgba(150,150,150,0.15);
}

/* ===================== MULTISELECT TAGS ===================== */

/* FORCE override multiselect chip background */
span[data-baseweb="tag"] {
    background-color: #1f2933 !important;
    color: #e5e7eb !important;
    border: 1px solid #374151 !important;
}

/* Remove red close button */
span[data-baseweb="tag"] svg {
    fill: #9ca3af !important;
}

/* Hover effect */
span[data-baseweb="tag"]:hover {
    background-color: #374151 !important;
}

/* Dropdown list background */
div[role="listbox"] {
    background-color: #0f172a !important;
}

/* Selected multiselect input background */
div[data-baseweb="select"] > div {
    background-color: #020617 !important;
}

/* ===================== TOP ERP HEADER BAR ===================== */
.block-container::before {
    content: "Internal Operations Dashboard";
    display: block;
    font-weight: 700;
    font-size: 18px;
    padding: 12px 18px;
    border-bottom: 1px solid rgba(150,150,150,0.15);
    margin-bottom: 12px;
}

/* ===================== SIDEBAR ERP MODULE CARDS ===================== */

section[data-testid="stSidebar"] .stRadio > div {
    display: flex;
    flex-direction: column;
    gap: 12px !important;
}

/* Force ALL sidebar module boxes equal height */
section[data-testid="stSidebar"] .stRadio label {
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;   /* centers text horizontally */
    text-align: center !important;
    height: 56px !important;             /* ✅ fixed equal height */
    min-height: 56px !important;
    padding: 0 14px !important;
    border-radius: 14px !important;
    border: 1px solid rgba(150,150,150,0.18);
    font-weight: 600 !important;
    transition: 0.18s ease;
    white-space: nowrap;                 /* prevents resizing */
    overflow: hidden;
    text-overflow: ellipsis;
}

/* Hover highlight */
section[data-testid="stSidebar"] .stRadio label:hover {
    background: rgba(150,150,150,0.08);
    transform: translateX(3px);
}

/* Active selection */
section[data-testid="stSidebar"] .stRadio input:checked + label {
    outline: 2px solid rgba(255,255,255,0.18);
}

/* ===================== FORM CARD LAYOUT ===================== */
form {
    border: 1px solid rgba(150,150,150,0.18);
    border-radius: 14px;
    padding: 18px;
}

/* Equal spacing between columns */
div[data-testid="column"] {
    padding: 0.6rem !important;
}

/* ===================== INPUT ALIGNMENT ===================== */
input, textarea, select {
    height: 42px !important;
    border-radius: 8px !important;
}

/* ===================== SECTION SPACING ===================== */
h1, h2, h3 {
    margin-bottom: 6px !important;
}

hr {
    margin-top: 18px !important;
    margin-bottom: 18px !important;
}
/* ===================== SELECTBOX + MULTISELECT FIX ===================== */

/* Selectbox main container */
div[data-baseweb="select"] > div {
    background-color: rgba(255,255,255,0.06) !important;
    border: 1px solid rgba(255,255,255,0.12) !important;
    border-radius: 10px !important;
}

/* Selectbox text */
div[data-baseweb="select"] span {
    color: #e5e7eb !important;
}

/* Dropdown arrow */
div[data-baseweb="select"] svg {
    fill: #e5e7eb !important;
}

/* Dropdown menu background */
div[role="listbox"] {
    background-color: #0b1220 !important;
    border: 1px solid rgba(255,255,255,0.12) !important;
    border-radius: 10px !important;
}

/* Dropdown options */
div[role="option"] {
    color: #e5e7eb !important;
}

/* Hover option */
div[role="option"]:hover {
    background-color: rgba(255,255,255,0.08) !important;
}



</style>
""", unsafe_allow_html=True)

st.divider()


# ---------------- SESSION INIT ----------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.user = None

# ---------------- LOGIN / REGISTER ----------------
if not st.session_state.logged_in:
    st.title("🔐 Login")

    tab1, tab2 = st.tabs(["Login", "Register"])

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

# ---------------- SIDEBAR ERP NAV ----------------
st.sidebar.markdown("## Navigation")

page = st.sidebar.radio(
    "Modules",
    [
        "Dashboard",
        "Products",
        "Stock Entry",
        "Issue Stock",
        "Inventory",
        "Logs",
        "Reports"
    ]
)

st.sidebar.divider()

st.sidebar.markdown("## User")
st.sidebar.write(st.session_state.user["username"])
st.sidebar.write(st.session_state.user["role"].upper())

if st.sidebar.button("Logout"):
    st.session_state.logged_in = False
    st.rerun()

# ---------------- DASHBOARD ----------------
if page == "Dashboard":
    st.subheader("Executive Summary")

    products = get_all_products()
    issues = get_issue_logs()

    total_products = len(products)
    low_stock = len([p for p in products if p["quantity"] <= p["min_stock"]])
    total_issues = len(issues)

    col1, col2, col3 = st.columns(3)
    col1.metric("Total Products", total_products)
    col2.metric("Low Stock Items", low_stock)
    col3.metric("Total Issues", total_issues)

# ---------------- PRODUCTS MODULE ----------------
elif page == "Products":
    st.subheader("📦 Product Management")

    # ---------- PRODUCT TABLE ----------
    products = get_all_products()

    st.markdown("### 📋 Product List")

    if products:
        df = pd.DataFrame(products)
        df["Stock"] = df["quantity"].astype(str) + " " + df["unit_type"]
        st.dataframe(df, use_container_width=True)
    else:
        st.info("No products available")

    st.divider()

    # ---------- EXCEL IMPORT ----------
    st.markdown("### 📥 Import Products from Excel")

    with st.form("excel_import_form", clear_on_submit=False):
        uploaded_file = st.file_uploader(
            "Upload Excel File",
            type=["xlsx"],
            key="excel_upload"
        )

        submit_import = st.form_submit_button("Import Products from Excel")

        if submit_import:
            if not uploaded_file:
                st.error("Please upload an Excel file first.")
            else:
                try:
                    df_upload = pd.read_excel(uploaded_file)
                    st.dataframe(df_upload, use_container_width=True)

                    imported = 0
                    updated = 0
                    skipped = 0
                    errors = 0

                    existing = get_all_products()
                    existing_map = {
                        (p.get("item_code") or "").strip(): p["product_id"]
                        for p in existing
                        if p.get("item_code")
                    }

                    for _, row in df_upload.iterrows():
                        try:
                            # REQUIRED
                            name = str(row.get("Item Name", "")).strip()
                            category = str(row.get("PROJECT", "")).strip()
                            supplier = str(row.get("SUPPLIER", "")).strip()

                            if not name or not category or not supplier:
                                skipped += 1
                                continue

                            # OPTIONAL
                            raw_code = row.get("Material Code")

                            if pd.isna(raw_code) or str(raw_code).strip() == "":
                                item_code = None
                            else:
                                item_code = str(raw_code).strip()

                            contract_no = str(row.get("Contract no.", "")).strip()
                            unit_type = str(row.get("Unit", "Quantity")).strip()
                            date_added = str(row.get("Date", "")).strip()
                            cost_price = float(row.get("CP", 0) or 0)
                            quantity = int(row.get("Quantity", 0) or 0)

                            # --- Normalize UNIT ---
                            unit_type = unit_type.capitalize()
                            if unit_type not in ["Meter", "Quantity"]:
                                unit_type = "Quantity"   # safe default

                            # --- Normalize DATE ---
                            if isinstance(row.get("Date"), pd.Timestamp):
                                date_added = row["Date"].strftime("%Y-%m-%d")
                            elif date_added.lower() in ["none", "nan", ""]:
                                date_added = None

                            # --- Normalize ITEM CODE ---
                            if item_code.lower() in ["none", "nan", ""]:
                                item_code = None


                            # UPDATE
                            if item_code and item_code in existing_map:
                                update_product(
                                    existing_map[item_code],
                                    name,
                                    category,
                                    supplier,
                                    0,
                                    cost_price,
                                    0
                                )
                                updated += 1

                            # INSERT
                            else:
                                add_product(
                                    name=name,
                                    category=category,
                                    quantity=quantity or 0,
                                    unit_type=unit_type,
                                    supplier=supplier,
                                    date_added=date_added,
                                    cost_price=cost_price or 0,
                                    item_code=item_code,
                                    contract_no=contract_no,
                                    plant_name=row.get("Plant Name"),
                                    gate_pass_no=row.get("Gate Pass No."),
                                    gate_pass_date=row.get("Gate Pass Date")
                                )

                                imported += 1

                        except Exception as e:
                            errors += 1
                            st.error(f"Row failed ({name}): {e}")


                    st.success(f"✅ Imported {imported} new products")
                    st.info(f"🔁 Updated {updated} existing products")
                    st.warning(f"⚠️ Skipped {skipped} rows")
                    if errors:
                        st.error(f"❌ {errors} rows failed")

                except Exception as e:
                    st.error(f"Excel import failed: {e}")
        st.divider()
    # ---------- MANUAL ADD FORM ----------
    st.markdown("### ➕ Add New Product")

    with st.form("add_product_form"):
        col1, col2 = st.columns(2)

        # LEFT COLUMN
        with col1:
            name = st.text_input("Item Name")
            category = st.text_input("Project")
            supplier = st.text_input("Supplier")
            item_code = st.text_input("Item Code")
            contract_no = st.text_input("Contract No.")
            cost_price = st.number_input("Cost Price", min_value=0.0, step=0.1)

        # RIGHT COLUMN
        with col2:
            unit_type = st.selectbox("Unit Type", ["Meter", "Quantity"])
            quantity = st.number_input("Enter Value", min_value=0, step=1)
            date_added = st.date_input("Date Added")
            plant_name = st.text_input("Plant Name")
            gate_pass_no = st.text_input("Gate Pass No.")
            gate_pass_date = st.date_input("Gate Pass Date")

        # ✅ SUBMIT BUTTON MUST BE INSIDE FORM
        submitted = st.form_submit_button("Add Product")

        if submitted:
            if safe_action_lock("add_product_lock", cooldown=2):

                add_product(
                    name,
                    category,
                    quantity,
                    unit_type,
                    supplier,
                    str(date_added),
                    cost_price,
                    item_code,
                    contract_no,
                    plant_name,
                    gate_pass_no,
                    str(gate_pass_date)
                )

                st.success("✅ Product Added Successfully!")
                st.info("Saved ✔")
                st.rerun()

            else:
                st.warning("⚠️ Already submitted. Please wait 2 seconds.")


# ---------------- STOCK ENTRY ----------------
elif page == "Stock Entry":
    st.subheader("Stock Entry")

    products = get_all_products()

    if products:
        # ---------------- PROJECT FILTER ----------------
        project_list = sorted(list(set([p["category"] for p in products if p["category"]])))

        selected_project = st.selectbox(
            "Select Project",
            ["All Projects"] + project_list,
            key="stock_entry_project_filter"
        )

        # Filter products by selected project
        if selected_project != "All Projects":
            products = [p for p in products if p["category"] == selected_project]

        if products:
            product_map = {p["name"]: p["product_id"] for p in products}

            selected = st.selectbox(
                "Select Product",
                list(product_map.keys()),
                key="add_stock_product"
            )

            unit_type = st.selectbox(
                "Unit Type",
                ["Meter", "Quantity"],
                key="add_stock_unit"
            )

            qty = st.number_input(
                f"Enter {unit_type} Value",
                min_value=1,
                step=1,
                key="add_stock_qty"
            )

            notes = st.text_input("Notes (optional)", key="add_stock_notes")

            # Auto store unit info inside notes
            final_notes = f"[{unit_type}] {notes}".strip()

            if st.button("Add Stock", key="add_stock_btn"):
                if safe_action_lock("add_stock_lock", cooldown=2):
                    update_stock(product_map[selected], qty, "ADD", final_notes)
                    st.success("✅ Stock Added Successfully!")
                    st.info("Saved ✔")
                    st.rerun()
                else:
                    st.warning("⚠️ Already submitted. Please wait 2 seconds.")
        else:
            st.warning("No products found in this project.")

    else:
        st.info("No products available.")


# ---------------- ISSUE STOCK ----------------
elif page == "Issue Stock":
    st.subheader("Issue Inventory")

    products = get_all_products()

    if not products:
        st.info("No products available.")
    else:
        df_all = pd.DataFrame(products)

        # PROJECT FILTER
        project_list = ["All Projects"] + sorted(
            df_all["category"].dropna().unique().tolist()
        )

        selected_project = st.selectbox("Select Project", project_list)

        # APPLY FILTER
        if selected_project != "All Projects":
            filtered_products = [p for p in products if p["category"] == selected_project]
        else:
            filtered_products = products

        # IF NO PRODUCTS AFTER FILTER
        if not filtered_products:
            st.warning("No products found in this project.")
        else:
            product_map = {p["name"]: p["product_id"] for p in filtered_products}

            selected = st.selectbox(
                "Select Product",
                list(product_map.keys()),
                key="issue_product"
            )

            issued_to = st.text_input("Issued To", key="issue_to")
            issued_qty = st.number_input("Issued Quantity", min_value=1, step=1, key="issue_qty")

            st.markdown("### Consumption (Optional)")
            used_qty = st.number_input("Used Quantity", min_value=0, step=1, key="used_qty")
            usage_purpose = st.text_input("What was it used for?", key="usage_purpose")

            remaining_qty = issued_qty - used_qty
            st.info(f"Remaining with user: {remaining_qty}")

            if st.button("📤 Submit Issue"):
                if safe_action_lock("issue_lock", cooldown=2):

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

                        st.success("✅ Issue Recorded Successfully!")
                        st.info("Saved ✔")
                        st.rerun()

                else:
                    st.warning("⚠️ Already submitted. Please wait 2 seconds.")

        st.divider()                 
        st.subheader("✏️ Edit Issued Records")

        issues = get_issue_logs()   

        if issues:
            df = pd.DataFrame(issues)

            products = get_all_products()

            # Map product_id → Item Name
            product_lookup = {p["product_id"]: p["name"] for p in products}

            # The following block should only run if issues exist
            issue_map = {}

            for index, i in enumerate(issues):
                product_name = product_lookup.get(i["product_id"], "Deleted Product")
                issued_to = i.get("issued_to", "")

                label = f"Issue #{index+1} — {product_name} → {issued_to}"
                issue_map[label] = i

            selected = st.selectbox("Select Issue to Edit", list(issue_map.keys()))

            issue = issue_map[selected]

            with st.form("edit_issue_form"):
                issued_to = st.text_input("Issued To", value=issue["issued_to"])
                issued_qty = st.number_input("Issued Quantity", value=int(issue["issued_qty"]), step=1)
                used_qty = st.number_input("Used Quantity", value=int(issue.get("used_qty", 0)), step=1)
                usage_purpose = st.text_input("Usage Purpose", value=issue.get("usage_purpose", ""))

                submitted = st.form_submit_button("Update Issue")

                if submitted:
                    issue_id = issue.get("issue_id") or issue.get("id")
                    success = update_issue(
                        issue_id,
                        issued_to,
                        issued_qty,
                        used_qty,
                        usage_purpose
                    )

                    if success:
                        st.success("Issue updated and stock adjusted!")
                        st.rerun()
                    else:
                        st.error("Failed to update issue.")
        else:
            st.info("No issue records available.")
# ---------------- LOGS ----------------
elif page == "Logs":
    st.subheader("Stock Movement History")

    history = get_stock_history()
    if history:
        st.dataframe(pd.DataFrame(history), use_container_width=True)
    else:
        st.info("No stock movements yet.")

    st.subheader("Issue Logs")

    issues = get_issue_logs()
    if issues:
        st.dataframe(pd.DataFrame(issues), use_container_width=True)
    else:
        st.info("No issued products yet.")

# ---------------- REPORTS ----------------
if page == "Reports":
    st.subheader("📊 Reports & Master Dashboard")
    st.caption("Unified inventory + logs + interconnected issue reports in one place")

    report_type = st.selectbox(
        "Select Report Type",
        [
            "📦 Inventory Report",
            "📥 Stock Movement Logs",
            "📤 Issue & Consumption Report"
        ],
        key="report_type_select"
    )

    st.divider()

    # ================================
    # REPORT 1: INVENTORY REPORT
    # ================================
    if report_type == "📦 Inventory Report":
        st.markdown("## 📦 Inventory Report")

        products = get_all_products()

        if not products:
            st.info("No products available.")
        else:
            df = pd.DataFrame(products)

            # Create Stock column if quantity + unit exists
            if "quantity" in df.columns and "unit_type" in df.columns:
                df["Stock"] = df["quantity"].astype(str) + " " + df["unit_type"]

            st.markdown("### 🧩 Column Visibility")

            all_columns = list(df.columns)

            if "visible_inventory_report_cols" not in st.session_state:
                st.session_state.visible_inventory_report_cols = all_columns

            selected_cols = st.multiselect(
                "Select columns to display",
                all_columns,
                default=st.session_state.visible_inventory_report_cols,
                key="inventory_report_col_selector"
            )

            st.session_state.visible_inventory_report_cols = selected_cols

            st.dataframe(df[selected_cols], use_container_width=True)

            # Export Excel
            buffer = io.BytesIO()
            with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
                df[selected_cols].to_excel(writer, sheet_name="Inventory", index=False)

            st.download_button(
                label="📥 Download Inventory Excel",
                data=buffer.getvalue(),
                file_name="inventory_report.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

    # ================================
    # REPORT 2: STOCK MOVEMENT LOGS
    # ================================
    elif report_type == "📥 Stock Movement Logs":
        st.markdown("## 📥 Stock Movement Logs")
        st.caption("Tracks all ADD / REMOVE movements for stock")

        stock_logs = get_stock_history()

        if not stock_logs:
            st.info("No stock movements found.")
        else:
            df = pd.DataFrame(stock_logs)

            st.markdown("### 🧩 Column Visibility")

            all_columns = list(df.columns)

            if "visible_stock_report_cols" not in st.session_state:
                st.session_state.visible_stock_report_cols = all_columns

            selected_cols = st.multiselect(
                "Select columns to display",
                all_columns,
                default=st.session_state.visible_stock_report_cols,
                key="stock_report_col_selector"
            )

            st.session_state.visible_stock_report_cols = selected_cols

            st.dataframe(df[selected_cols], use_container_width=True)

            buffer = io.BytesIO()
            with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
                df[selected_cols].to_excel(writer, sheet_name="Stock Movements", index=False)

            st.download_button(
                label="📥 Download Stock Logs Excel",
                data=buffer.getvalue(),
                file_name="stock_movements_report.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

    # ================================
    # REPORT 3: ISSUE + CONSUMPTION REPORT
    # ================================
    elif report_type == "📤 Issue & Consumption Report":
        st.markdown("## 📤 Issue & Consumption Report")
        st.caption("Tracks who issued what to whom, consumption, remaining stock, and purpose")

        data = get_interconnected_data()

        if not data:
            st.info("No issue or consumption records found yet.")
        else:
            df = pd.DataFrame(data)

            col1, col2 = st.columns([1, 3])

            with col1:
                mode = st.selectbox(
                    "View By",
                    ["Person", "Product", "Category", "Issuer"],
                    key="issue_report_mode"
                )

                if mode == "Person":
                    selected = st.selectbox(
                        "Select Person",
                        sorted(df["issued_to"].dropna().unique()),
                        key="issue_report_person"
                    )
                    filtered = df[df["issued_to"] == selected]

                elif mode == "Product":
                    selected = st.selectbox(
                        "Select Product",
                        sorted(df["product"].dropna().unique()),
                        key="issue_report_product"
                    )
                    filtered = df[df["product"] == selected]

                elif mode == "Category":
                    selected = st.selectbox(
                        "Select Category",
                        sorted(df["category"].dropna().unique()),
                        key="issue_report_category"
                    )
                    filtered = df[df["category"] == selected]

                elif mode == "Issuer":
                    selected = st.selectbox(
                        "Select Issuer",
                        sorted(df["issued_by"].dropna().unique()),
                        key="issue_report_issuer"
                    )
                    filtered = df[df["issued_by"] == selected]

            with col2:
                st.markdown("### 📋 Results")

                all_columns = list(filtered.columns)

                st.markdown("### 🧩 Column Visibility")

                if "visible_issue_report_cols" not in st.session_state:
                    st.session_state.visible_issue_report_cols = all_columns

                selected_cols = st.multiselect(
                    "Select columns to display",
                    all_columns,
                    default=st.session_state.visible_issue_report_cols,
                    key="issue_report_col_selector"
                )

                st.session_state.visible_issue_report_cols = selected_cols

                st.dataframe(filtered[selected_cols], use_container_width=True)

                # Export Excel
                buffer = io.BytesIO()
                with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
                    filtered[selected_cols].to_excel(writer, sheet_name="Issue Report", index=False)

                st.download_button(
                    label="📥 Download Issue Report Excel",
                    data=buffer.getvalue(),
                    file_name="issue_consumption_report.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )

