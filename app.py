# -*- coding: utf-8 -*-
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
    page_title="Aaryan Techno Projects ERP",
    page_icon="📦",
    layout="wide"
)

# ---------------- THEME SELECTION ----------------
if "theme" not in st.session_state:
    st.session_state.theme = "dark"

# Render toggle in the sidebar so it's accessible globally
theme_toggle = st.sidebar.toggle(
    "☀️ Light Mode", 
    value=(st.session_state.theme == "light"),
    key="theme_toggle_widget"
)
st.session_state.theme = "light" if theme_toggle else "dark"

# Define dynamic CSS variables for theme modes
if st.session_state.theme == "light":
    css_variables = """
    :root {

        --bg-primary: #f8fafc;
        --bg-secondary: #eef2f7;

        --bg-gradient:
            linear-gradient(
                160deg,
                #f8fafc 0%,
                #e2e8f0 45%,
                #f8fafc 100%
            );

        --sidebar-gradient:
            linear-gradient(
                180deg,
                #ffffff 0%,
                #f1f5f9 100%
            );

        --card-bg: rgba(255,255,255,0.78);

        --border-color: rgba(15,23,42,0.08);

        --text-primary: #0f172a;
        --text-secondary: #475569;
        --text-muted: #64748b;

        --input-bg: #ffffff;
        --input-border: #cbd5e1;
        --input-focus-bg: #ffffff;

        --sidebar-tab-bg: rgba(15,23,42,0.03);
        --sidebar-tab-hover: rgba(15,23,42,0.06);

        --user-card-bg: rgba(15,23,42,0.03);

        --dataframe-shadow: rgba(15,23,42,0.06);

        --listbox-bg: #ffffff;

        --option-hover: rgba(15,23,42,0.04);

        --tab-border: rgba(15,23,42,0.08);

        --button-gradient:
            linear-gradient(
                135deg,
                #38bdf8 0%,
                #818cf8 100%
            );

        --button-hover:
            linear-gradient(
                135deg,
                #0ea5e9 0%,
                #6366f1 100%
            );
    }
    """

else:
    css_variables = """
    :root {
        --bg-primary: #020617;
        --bg-secondary: #0f172a;
        --bg-gradient: linear-gradient(160deg, #020617 0%, #0f172a 45%, #020617 100%);
        --sidebar-gradient: linear-gradient(180deg, #020617 0%, #0b1220 100%);
        --card-bg: rgba(15, 23, 42, 0.4) !important;
        --border-color: rgba(255, 255, 255, 0.05) !important;
        --text-primary: #f8fafc;
        --text-secondary: #94a3b8;
        --text-muted: #64748b;
        --input-bg: rgba(255, 255, 255, 0.02) !important;
        --input-border: rgba(255, 255, 255, 0.08) !important;
        --input-focus-bg: rgba(255, 255, 255, 0.04) !important;
        --sidebar-tab-bg: rgba(255, 255, 255, 0.02) !important;
        --sidebar-tab-hover: rgba(255, 255, 255, 0.07) !important;
        --user-card-bg: rgba(255, 255, 255, 0.03) !important;
        --dataframe-shadow: rgba(0, 0, 0, 0.2) !important;
        --listbox-bg: #0f172a !important;
        --option-hover: rgba(255, 255, 255, 0.06) !important;
        --tab-border: rgba(255, 255, 255, 0.08) !important;
    }
    """

# Inject Dynamic CSS and top bar layout
st.markdown(f"""
<div class="top-nav-bar">
    <span class="app-logo">🏭</span>
    <div>
        <h1 class="app-title">Aaryan Techno Projects ERP</h1>
        <p class="app-subtitle">Internal Operations & Inventory Control Center</p>
    </div>
</div>

<style>
{css_variables}

@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700&display=swap');

/* Force Outfit Font & Text Adaptability Everywhere */
html, body, [class*="css"], .stApp,
p, span, label, input, select,
textarea, button,
h1, h2, h3, h4, h5, h6,
li, ul {{

    font-family: 'Outfit', sans-serif !important;
}}

/* Dynamic Heading and Text Colors */
h1, h2, h3, h4, h5, h6,
label,
.stMarkdown,
p,
li,
ul,
span:not(.app-logo):not(.app-title):not(.app-subtitle) {{

    color: var(--text-primary) !important;
}}

/* Hide Streamlit default header bar content injection */
.block-container::before {{
    display: none !important;
}}

/* Main App Gradient Background */
.stApp {{

    background: var(--bg-gradient) !important;

    background-attachment: fixed !important;
}}

/* Sidebar Gradient Background */
section[data-testid="stSidebar"] {{

    background: var(--sidebar-gradient) !important;

    border-right:
        1px solid var(--border-color) !important;
}}

/* FIX SIDEBAR TEXT */
section[data-testid="stSidebar"] * {{

    color: var(--text-primary) !important;
}}

/* Custom Top Navigation / Header Bar */
.top-nav-bar {{

    display: flex !important;

    align-items: center !important;

    gap: 18px !important;

    padding: 18px 24px !important;

    background: var(--card-bg) !important;

    border:
        1px solid var(--border-color) !important;

    border-radius: 16px !important;

    margin-bottom: 24px !important;

    backdrop-filter: blur(12px) !important;

    box-shadow:
        0 4px 30px var(--dataframe-shadow) !important;
}}

.app-logo {{
    font-size: 36px !important;
}}

.app-title {{

    font-size: 26px !important;

    font-weight: 700 !important;

    background:
        linear-gradient(
            135deg,
            #38bdf8,
            #818cf8
        ) !important;

    -webkit-background-clip: text !important;

    -webkit-text-fill-color: transparent !important;

    margin: 0 !important;

    letter-spacing: -0.02em !important;
}}

.app-subtitle {{

    font-size: 11px !important;

    color: var(--text-muted) !important;

    margin: 2px 0 0 0 !important;

    font-weight: 600 !important;

    text-transform: uppercase !important;

    letter-spacing: 0.1em !important;
}}

/* Sidebar Section Headers */
.sidebar-section-header {{

    font-size: 11px !important;

    text-transform: uppercase !important;

    letter-spacing: 0.1em !important;

    color: var(--text-muted) !important;

    font-weight: 700 !important;

    margin-top: 1.5rem !important;

    margin-bottom: 0.5rem !important;

    padding-left: 8px !important;

    border-bottom:
        1px solid var(--border-color) !important;

    padding-bottom: 4px !important;
}}

/* ================= INPUTS ================= */

input,
textarea,
select {{

    background:
        var(--input-bg) !important;

    border:
        1px solid var(--input-border) !important;

    color:
        var(--text-primary) !important;

    border-radius: 10px !important;
}}

/* ================= SELECTBOX ================= */

div[data-baseweb="select"] > div {{

    background:
        var(--input-bg) !important;

    border:
        1px solid var(--input-border) !important;

    border-radius: 10px !important;
}}

div[data-baseweb="select"] span {{

    color:
        var(--text-primary) !important;
}}

div[data-baseweb="select"] input {{

    color:
        var(--text-primary) !important;
}}

/* ================= DROPDOWNS ================= */

div[role="listbox"] {{

    background:
        var(--listbox-bg) !important;
}}

div[role="option"] {{

    color:
        var(--text-primary) !important;
}}

div[role="option"]:hover {{

    background:
        var(--option-hover) !important;
}}

/* ================= FILE UPLOADER ================= */

[data-testid="stFileUploader"] * {{

    color:
        var(--text-primary) !important;
}}

/* ================= DATAFRAME ================= */

div[data-testid="stDataFrame"] {{

    border:
        1px solid var(--border-color) !important;

    border-radius: 12px !important;

    overflow: hidden !important;

    box-shadow:
        0 4px 20px var(--dataframe-shadow) !important;
}}

[data-testid="stDataFrame"] * {{

    color:
        var(--text-primary) !important;
}}

/* ================= BUTTONS ================= */

div.stButton > button,
div.stFormSubmitButton > button {{

    background:
        var(--button-gradient) !important;

    color: white !important;

    border: none !important;

    border-radius: 10px !important;

    font-weight: 600 !important;

    transition: 0.2s ease !important;
}}

div.stButton > button:hover,
div.stFormSubmitButton > button:hover {{

    background:
        var(--button-hover) !important;

    transform: translateY(-1px) !important;
}}

/* ================= DIVIDERS ================= */

hr {{

    border-color:
        var(--border-color) !important;
}}

/* ===================== SIDEBAR NAVIGATION CARDS ===================== */

/* Hide radio circles */
section[data-testid="stSidebar"] .stRadio div[role="radiogroup"] label > div:first-child {{
    display: none !important;
}}

/* Sidebar radio button list layout */
section[data-testid="stSidebar"] .stRadio div[role="radiogroup"] {{
    display: flex !important;
    flex-direction: column !important;
    gap: 8px !important;
    padding: 0 !important;
}}

/* Style labels to look like premium buttons */
section[data-testid="stSidebar"] .stRadio div[role="radiogroup"] label {{
    display: flex !important;
    align-items: center !important;
    justify-content: flex-start !important;
    width: 100% !important;
    height: auto !important;
    min-height: 46px !important;
    padding: 10px 16px !important;
    margin: 0 !important;
    border-radius: 12px !important;
    background: var(--sidebar-tab-bg) !important;
    border: 1px solid var(--border-color) !important;
    color: var(--text-secondary) !important;
    font-weight: 500 !important;
    font-size: 14px !important;
    transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1) !important;
    cursor: pointer !important;
}}

/* Hover state */
section[data-testid="stSidebar"] .stRadio div[role="radiogroup"] label:hover {{
    background: var(--sidebar-tab-hover) !important;
    border-color: var(--text-muted) !important;
    color: var(--text-primary) !important;
    transform: translateX(4px) !important;
}}

/* Checked state */
section[data-testid="stSidebar"] .stRadio div[role="radiogroup"] label:has(input:checked) {{
    background: linear-gradient(135deg, rgba(56, 189, 248, 0.15) 0%, rgba(129, 140, 248, 0.15) 100%) !important;
    border: 1px solid rgba(56, 189, 248, 0.4) !important;
    color: var(--text-primary) !important;
    box-shadow: 0 4px 20px -5px rgba(56, 189, 248, 0.25) !important;
    font-weight: 600 !important;
}}

section[data-testid="stSidebar"] .stRadio div[role="radiogroup"] label p {{
    margin: 0 !important;
    padding: 0 !important;
    color: inherit !important;
}}

/* ===================== USER CARD & SIDEBAR LOGOUT ===================== */
.user-card {{
    display: flex !important;
    align-items: center !important;
    gap: 12px !important;
    padding: 12px !important;
    border-radius: 12px !important;
    background: var(--user-card-bg) !important;
    border: 1px solid var(--border-color) !important;
    margin-top: 0.5rem !important;
    margin-bottom: 1rem !important;
}}
.user-avatar {{
    width: 36px !important;
    height: 36px !important;
    border-radius: 50% !important;
    background: linear-gradient(135deg, #38bdf8, #818cf8) !important;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    font-weight: 700 !important;
    color: white !important;
    font-size: 14px !important;
}}
.user-details {{
    display: flex !important;
    flex-direction: column !important;
}}
.user-name {{
    font-weight: 600 !important;
    font-size: 14px !important;
    color: var(--text-primary) !important;
}}
.user-role {{
    font-size: 10px !important;
    font-weight: 600 !important;
    color: #38bdf8 !important;
    letter-spacing: 0.05em !important;
}}

/* Logout Button */
div[data-testid="stSidebar"] button {{
    width: 100% !important;
    border-radius: 10px !important;
    background-color: transparent !important;
    border: 1px solid rgba(239, 68, 68, 0.2) !important;
    color: #ef4444 !important;
    transition: all 0.2s ease !important;
    font-size: 13px !important;
    font-weight: 600 !important;
}}
div[data-testid="stSidebar"] button:hover {{
    background-color: rgba(239, 68, 68, 0.1) !important;
    border-color: #ef4444 !important;
    color: #ef4444 !important;
}}

/* ===================== DASHBOARD CUSTOM METRIC CARDS ===================== */
.metrics-grid {{
    display: grid !important;
    grid-template-columns: repeat(3, 1fr) !important;
    gap: 20px !important;
    margin-bottom: 25px !important;
    margin-top: 10px !important;
}}
.metric-card {{
    background: var(--card-bg) !important;
    border: 1px solid var(--border-color) !important;
    border-radius: 16px !important;
    padding: 22px 24px !important;
    display: flex !important;
    align-items: center !important;
    gap: 18px !important;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
    box-shadow: 0 4px 30px var(--dataframe-shadow) !important;
    backdrop-filter: blur(12px) !important;
}}
.metric-card:hover {{
    transform: translateY(-4px) !important;
    border-color: rgba(56, 189, 248, 0.25) !important;
    box-shadow: 0 10px 30px -10px rgba(56, 189, 248, 0.25) !important;
}}
.metric-icon {{
    width: 48px !important;
    height: 48px !important;
    border-radius: 12px !important;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    font-size: 22px !important;
}}
.metric-info {{
    display: flex !important;
    flex-direction: column !important;
}}
.metric-value {{
    font-size: 28px !important;
    font-weight: 700 !important;
    color: var(--text-primary) !important;
    line-height: 1.1 !important;
}}
.metric-label {{
    font-size: 13px !important;
    color: var(--text-secondary) !important;
    font-weight: 500 !important;
    margin-top: 2px !important;
}}

/* ===================== FORM CARDS & INPUT CONTROLS ===================== */
form {{
    background: var(--card-bg) !important;
    border: 1px solid var(--border-color) !important;
    border-radius: 16px !important;
    padding: 24px !important;
    box-shadow: 0 4px 30px var(--dataframe-shadow) !important;
    backdrop-filter: blur(8px) !important;
}}

input, textarea, select {{
    background-color: var(--input-bg) !important;
    border: 1px solid var(--input-border) !important;
    color: var(--text-primary) !important;
    border-radius: 10px !important;
    padding: 10px 14px !important;
    transition: all 0.2s ease !important;
    font-size: 14px !important;
}}
input:focus, textarea:focus, select:focus {{
    border-color: #38bdf8 !important;
    box-shadow: 0 0 0 2px rgba(56, 189, 248, 0.2) !important;
    background-color: var(--input-focus-bg) !important;
}}

/* Selectbox Overrides */
div[data-baseweb="select"] > div {{
    background-color: var(--input-bg) !important;
    border: 1px solid var(--input-border) !important;
    border-radius: 10px !important;
}}
div[data-baseweb="select"] span {{
    color: var(--text-primary) !important;
}}
div[data-baseweb="select"] svg {{
    fill: var(--text-primary) !important;
}}
div[role="listbox"] {{
    background-color: var(--listbox-bg) !important;
    border: 1px solid var(--border-color) !important;
    border-radius: 10px !important;
}}
div[role="option"] {{
    color: var(--text-secondary) !important;
}}
div[role="option"]:hover {{
    background-color: var(--option-hover) !important;
}}

/* Multiselect Tag Overrides */
span[data-baseweb="tag"] {{
    background-color: var(--input-bg) !important;
    color: var(--text-primary) !important;
    border: 1px solid var(--input-border) !important;
    border-radius: 6px !important;
}}
span[data-baseweb="tag"] svg {{
    fill: var(--text-secondary) !important;
}}
span[data-baseweb="tag"]:hover {{
    background-color: var(--sidebar-tab-hover) !important;
}}

/* Styled Streamlit Tabs */
button[data-baseweb="tab"] {{
    color: var(--text-secondary) !important;
    font-weight: 500 !important;
    padding: 10px 20px !important;
    transition: all 0.2s ease !important;
    font-size: 14px !important;
}}
button[data-baseweb="tab"][aria-selected="true"] {{
    color: #38bdf8 !important;
    border-bottom-color: #38bdf8 !important;
    font-weight: 600 !important;
}}
button[data-baseweb="tab"]:hover {{
    color: var(--text-primary) !important;
}}

/* Button & Form Submit Styling */
div.stButton > button, div.stFormSubmitButton > button {{
    background: linear-gradient(135deg, #38bdf8 0%, #818cf8 100%) !important;
    color: #ffffff !important;
    border: none !important;
    border-radius: 10px !important;
    padding: 10px 24px !important;
    font-weight: 600 !important;
    font-size: 14px !important;
    transition: all 0.2s ease-in-out !important;
    box-shadow: 0 4px 15px rgba(56, 189, 248, 0.2) !important;
    width: 100% !important;
}}
div.stButton > button:hover, div.stFormSubmitButton > button:hover {{
    transform: translateY(-1px) !important;
    box-shadow: 0 6px 20px rgba(56, 189, 248, 0.35) !important;
    color: #ffffff !important;
}}
div.stButton > button:active, div.stFormSubmitButton > button:active {{
    transform: translateY(1px) !important;
}}

/* Dataframe & Table Aesthetics */
div[data-testid="stDataFrame"] {{
    border: 1px solid var(--border-color) !important;
    border-radius: 12px !important;
    overflow: hidden !important;
    box-shadow: 0 4px 20px var(--dataframe-shadow) !important;
}}

/* Helper Divider Override */
hr {{
    border-color: var(--border-color) !important;
}}

/* ================= CUSTOM HTML TABLE ================= */

table {{

    width: 100% !important;

    border-collapse: collapse !important;

    background: var(--card-bg) !important;

    border-radius: 14px !important;

    overflow: hidden !important;

    backdrop-filter: blur(12px) !important;
}}

/* Header */
table thead tr {{

    background:
        rgba(59,130,246,0.08) !important;
}}

/* Header cells */
table th {{

    color:
        var(--text-primary) !important;

    padding: 14px !important;

    text-align: left !important;

    border-bottom:
        1px solid var(--border-color) !important;
}}

/* Table rows */
table td {{

    color:
        var(--text-primary) !important;

    padding: 12px !important;

    border-bottom:
        1px solid var(--border-color) !important;
}}

/* Hover */
table tbody tr:hover {{

    background:
        rgba(255,255,255,0.03) !important;
}}
/* FORCE SELECTBOX COLORS */

[data-baseweb="select"] * {{
    color: var(--text-primary) !important;
}}

[data-baseweb="select"] > div {{
    background: var(--input-bg) !important;
    border: 1px solid var(--input-border) !important;
}}

div[role="listbox"] {{
    background: var(--listbox-bg) !important;
}}

div[role="option"] {{
    color: var(--text-primary) !important;
    background: transparent !important;
}}

div[role="option"]:hover {{
    background: var(--option-hover) !important;
}}
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
st.sidebar.markdown('<p class="sidebar-section-header">Navigation</p>', unsafe_allow_html=True)

page_icons_map = {
    "📊 Dashboard": "Dashboard",
    "📦 Products": "Products",
    "📥 Stock Entry": "Stock Entry",
    "📤 Issue Stock": "Issue Stock",
    "📋 Inventory": "Inventory",
    "📜 Logs": "Logs",
    "📈 Reports": "Reports"
}

selected_page_with_icon = st.sidebar.radio(
    "Modules",
    list(page_icons_map.keys()),
    label_visibility="collapsed"
)

page = page_icons_map[selected_page_with_icon]

st.sidebar.markdown('<p class="sidebar-section-header">Session</p>', unsafe_allow_html=True)

username = st.session_state.user["username"]
role_display = st.session_state.user["role"].upper()
initial = username[0].upper() if username else "U"

st.sidebar.markdown(f"""
<div class="user-card">
    <div class="user-avatar">{initial}</div>
    <div class="user-details">
        <div class="user-name">{username}</div>
        <div class="user-role">{role_display}</div>
    </div>
</div>
""", unsafe_allow_html=True)

if st.sidebar.button("Logout"):
    st.session_state.logged_in = False
    st.rerun()


# ---------------- DASHBOARD ----------------
if page == "Dashboard":
    st.subheader("Executive Summary")

    products = get_all_products()
    issues = get_issue_logs()

    total_products = len(products)
    low_stock = len([p for p in products if p.get("quantity", 0) <= p.get("min_stock", float('inf'))])
    total_issues = len(issues)

    st.markdown(f"""
    <div class="metrics-grid">
        <div class="metric-card">
            <div class="metric-icon" style="background: rgba(56, 189, 248, 0.1); color: #38bdf8;">📦</div>
            <div class="metric-info">
                <div class="metric-value">{total_products}</div>
                <div class="metric-label">Total Products</div>
            </div>
        </div>
        <div class="metric-card">
            <div class="metric-icon" style="background: rgba(239, 68, 68, 0.1); color: #ef4444;">⚠️</div>
            <div class="metric-info">
                <div class="metric-value">{low_stock}</div>
                <div class="metric-label">Low Stock Items</div>
            </div>
        </div>
        <div class="metric-card">
            <div class="metric-icon" style="background: rgba(168, 85, 247, 0.1); color: #a855f7;">📋</div>
            <div class="metric-info">
                <div class="metric-value">{total_issues}</div>
                <div class="metric-label">Total Issues</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)


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
                            if item_code:
                                if isinstance(item_code, str) and item_code.lower() in ["none", "nan", ""]:
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
                            st.error(f"Row failed: {e}")


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
                issued_to = st.text_input("Issued To", value=issue.get("issued_to", ""))
                issued_qty = st.number_input("Issued Quantity", value=int(issue.get("issued_qty", 0)), step=1)
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
elif page == "Reports":
    st.subheader("📊 Master Reports (Inventory + Logs)")

    data = get_interconnected_data()

    if not data:
        st.info("No records available.")
    else:
        df = pd.DataFrame(data)

        # ---------------- FILTER SECTION ----------------
        st.markdown("### 🔎 Filters")

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            person_filter = st.selectbox(
                "Person",
                ["All"] + sorted(df["issued_to"].dropna().unique().tolist())
            )

        with col2:
            product_filter = st.selectbox(
                "Product",
                ["All"] + sorted(df["product"].dropna().unique().tolist())
            )

        with col3:
            category_filter = st.selectbox(
                "Project",
                ["All"] + sorted(df["category"].dropna().unique().tolist())
            )

        with col4:
            issuer_filter = st.selectbox(
                "Issuer",
                ["All"] + sorted(df["issued_by"].dropna().unique().tolist())
            )
        show_issued_only = st.toggle("Show Issued Items Only", value=False)

        # ---------------- APPLY FILTERS ----------------
        filtered = df.copy()
        if show_issued_only:
            filtered = filtered[filtered["issued_to"].notna()]

        if person_filter != "All":
            filtered = filtered[filtered["issued_to"] == person_filter]

        if product_filter != "All":
            filtered = filtered[filtered["product"] == product_filter]

        if category_filter != "All":
            filtered = filtered[filtered["category"] == category_filter]

        if issuer_filter != "All":
            filtered = filtered[filtered["issued_by"] == issuer_filter]

        # ---------------- COLUMN VISIBILITY ----------------
        st.markdown("### 🧩 Column Visibility")

        all_columns = list(filtered.columns)

        if "visible_master_report_columns" not in st.session_state:
            st.session_state.visible_master_report_columns = all_columns

        selected_columns = st.multiselect(
            "Select columns to display",
            all_columns,
            default=st.session_state.visible_master_report_columns,
            key="master_report_column_selector"
        )

        st.session_state.visible_master_report_columns = selected_columns

        # ---------------- MASTER TABLE ----------------
        st.markdown("### 📋 Complete Report")

        valid_columns = [col for col in selected_columns if col in filtered.columns]
        st.dataframe(
            filtered[valid_columns],
            use_container_width=True,
            height=600
        )

        # ---------------- EXPORT ----------------
        buffer = io.BytesIO()

        with pd.ExcelWriter(buffer, engine="xlsxwriter") as writer:
            filtered[valid_columns].to_excel(writer, sheet_name="Master Report", index=False)

        buffer.seek(0)
        st.download_button(
            label="⬇ Download Excel",
            data=buffer.getvalue(),
            file_name="master_inventory_report.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
