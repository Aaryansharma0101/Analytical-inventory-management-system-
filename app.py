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
from components import (
    inject_components, render_table, render_select, render_multiselect,
    render_tabs, render_expander, render_alert, render_metric,
    render_download_button
)

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
    page_icon=None,
    layout="wide"
)

# Lock theme to light
st.session_state.theme = "light"

css_variables = """
:root {
    --bg-primary: #f8fafc;
    --bg-secondary: #f1f5f9;
    --bg-gradient: linear-gradient(160deg, #f0f4f8 0%, #e2e8f0 30%, #f8fafc 100%);
    --sidebar-gradient: linear-gradient(180deg, #ffffff 0%, #f8fafc 100%);
    --card-bg: #ffffff;
    --card-shadow: 0 1px 3px rgba(0,0,0,0.06), 0 1px 2px rgba(0,0,0,0.04);
    --card-shadow-hover: 0 10px 25px -5px rgba(0,0,0,0.08), 0 4px 10px -5px rgba(0,0,0,0.04);
    --border-color: #e2e8f0;
    --text-primary: #1e293b;
    --text-secondary: #475569;
    --text-muted: #94a3b8;
    --accent: #3b82f6;
    --accent-hover: #2563eb;
    --accent-light: rgba(59,130,246,0.1);
    --success: #10b981;
    --success-light: rgba(16,185,129,0.1);
    --warning: #f59e0b;
    --warning-light: rgba(245,158,11,0.1);
    --danger: #ef4444;
    --danger-light: rgba(239,68,68,0.1);
    --input-bg: #ffffff;
    --input-border: #e2e8f0;
    --input-focus-bg: #ffffff;
    --sidebar-tab-bg: #f8fafc;
    --sidebar-tab-hover: #f1f5f9;
    --user-card-bg: #f8fafc;
    --dataframe-shadow: 0 1px 3px rgba(0,0,0,0.04);
    --listbox-bg: #ffffff;
    --option-hover: #f1f5f9;
    --tab-border: #e2e8f0;
    --button-gradient: #3b82f6;
    --button-hover: #2563eb;
    --font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
}
"""

# Inject Dynamic CSS and top bar layout
css_styles = """
@import url('https://fonts.googleapis.com/css2?family=Inter:opsz,wght@14..32,300..700&display=swap');

/* ---------- GLOBAL FONT & TEXT ---------- */
* { font-family: var(--font-family) !important; }
html, body, [class*="css"], .stApp, p, span, label, input, select,
textarea, button, h1, h2, h3, h4, h5, h6, li, ul, div {
    font-family: var(--font-family) !important;
}
h1, h2, h3, h4, h5, h6, .stMarkdown, li, ul {
    color: var(--text-primary) !important;
}
p, span, label, .st-cb, .st-da, .st-dv, .st-ea, .st-el {
    color: var(--text-secondary) !important;
}
.block-container::before { display: none !important; }

/* ---------- MAIN APP ---------- */
.stApp {
    background: var(--bg-gradient) !important;
    background-attachment: fixed !important;
}
[data-testid="stMain"] { background: transparent !important; }
[data-testid="stBlockContainer"] { padding: 1.5rem 2rem !important; }
[data-testid="stVerticalBlock"] { gap: 12px !important; }

/* ---------- SIDEBAR ---------- */
section[data-testid="stSidebar"] {
    background: var(--sidebar-gradient) !important;
    border-right: 1px solid var(--border-color) !important;
}
section[data-testid="stSidebar"] * { color: var(--text-primary) !important; }

/* ---------- TOP NAV BAR ---------- */
.top-nav-bar {
    display: flex !important;
    align-items: center !important;
    justify-content: space-between !important;
    padding: 16px 24px !important;
    background: var(--card-bg) !important;
    border: 1px solid var(--border-color) !important;
    border-radius: 12px !important;
    margin-bottom: 24px !important;
    box-shadow: var(--card-shadow) !important;
    transition: box-shadow 0.2s ease !important;
}
.top-nav-bar:hover { box-shadow: var(--card-shadow-hover) !important; }
.app-title { font-size: 22px !important; font-weight: 700 !important; color: var(--text-primary) !important; margin: 0 !important; letter-spacing: -0.02em !important; }
.app-subtitle { font-size: 11px !important; color: var(--text-muted) !important; margin: 2px 0 0 0 !important; font-weight: 600 !important; text-transform: uppercase !important; letter-spacing: 0.08em !important; }

/* ---------- STOCK BADGES ---------- */
.stock-badge { display: inline-flex !important; align-items: center !important; gap: 4px !important; padding: 4px 10px !important; border-radius: 20px !important; font-size: 12px !important; font-weight: 600 !important; line-height: 1 !important; }
.stock-badge-safe { background: var(--success-light) !important; color: var(--success) !important; }
.stock-badge-warning { background: var(--warning-light) !important; color: var(--warning) !important; }
.stock-badge-danger { background: var(--danger-light) !important; color: var(--danger) !important; }

/* ---------- SIDEBAR NAV RADIO ---------- */
.sidebar-section-header { font-size: 11px !important; text-transform: uppercase !important; letter-spacing: 0.1em !important; color: var(--text-muted) !important; font-weight: 700 !important; margin-top: 1.5rem !important; margin-bottom: 0.5rem !important; padding-left: 8px !important; border-bottom: 1px solid var(--border-color) !important; padding-bottom: 4px !important; }
section[data-testid="stSidebar"] .stRadio div[role="radiogroup"] label > div:first-child { display: none !important; }
section[data-testid="stSidebar"] .stRadio div[role="radiogroup"] { display: flex !important; flex-direction: column !important; gap: 6px !important; padding: 0 !important; }
section[data-testid="stSidebar"] .stRadio div[role="radiogroup"] label { display: flex !important; align-items: center !important; justify-content: flex-start !important; width: 100% !important; min-height: 44px !important; padding: 10px 14px !important; margin: 0 !important; border-radius: 10px !important; background: var(--sidebar-tab-bg) !important; border: 1px solid transparent !important; color: var(--text-secondary) !important; font-weight: 500 !important; font-size: 14px !important; transition: all 0.2s cubic-bezier(0.4,0,0.2,1) !important; cursor: pointer !important; }
section[data-testid="stSidebar"] .stRadio div[role="radiogroup"] label:hover { background: var(--sidebar-tab-hover) !important; border-color: var(--border-color) !important; color: var(--text-primary) !important; transform: translateX(3px) !important; }
section[data-testid="stSidebar"] .stRadio div[role="radiogroup"] label:has(input:checked) { background: var(--accent-light) !important; border: 1px solid rgba(59,130,246,0.3) !important; color: var(--accent) !important; font-weight: 600 !important; }
section[data-testid="stSidebar"] .stRadio div[role="radiogroup"] label p { margin: 0 !important; padding: 0 !important; color: inherit !important; }

/* ---------- USER CARD ---------- */
.user-card { display: flex !important; align-items: center !important; gap: 12px !important; padding: 12px !important; border-radius: 10px !important; background: var(--user-card-bg) !important; border: 1px solid var(--border-color) !important; margin-top: 0.5rem !important; margin-bottom: 1rem !important; }
.user-avatar { width: 38px !important; height: 38px !important; border-radius: 50% !important; background: var(--accent-light) !important; color: var(--accent) !important; display: flex !important; align-items: center !important; justify-content: center !important; font-weight: 700 !important; font-size: 15px !important; }
.user-details { display: flex !important; flex-direction: column !important; }
.user-name { font-weight: 600 !important; font-size: 14px !important; color: var(--text-primary) !important; }
.user-role { font-size: 10px !important; font-weight: 600 !important; color: var(--accent) !important; letter-spacing: 0.05em !important; }

/* ---------- SIDEBAR LOGOUT BUTTON ---------- */
div[data-testid="stSidebar"] button { width: 100% !important; border-radius: 8px !important; background-color: transparent !important; border: 1px solid rgba(239,68,68,0.2) !important; color: var(--danger) !important; transition: all 0.2s ease !important; font-size: 13px !important; font-weight: 600 !important; }
div[data-testid="stSidebar"] button:hover { background-color: var(--danger-light) !important; border-color: var(--danger) !important; }

/* ---------- METRICS CARDS ---------- */
.metrics-grid { display: grid !important; gap: 20px !important; margin-bottom: 25px !important; margin-top: 10px !important; }
.metric-card { background: var(--card-bg) !important; border: 1px solid var(--border-color) !important; border-radius: 12px !important; padding: 20px 22px !important; display: flex !important; align-items: center !important; gap: 16px !important; transition: all 0.25s cubic-bezier(0.4,0,0.2,1) !important; box-shadow: var(--card-shadow) !important; }
.metric-card:hover { transform: translateY(-2px) !important; box-shadow: var(--card-shadow-hover) !important; border-color: var(--accent) !important; }
.metric-icon { width: 46px !important; height: 46px !important; border-radius: 10px !important; display: flex !important; align-items: center !important; justify-content: center !important; font-size: 20px !important; flex-shrink: 0 !important; }
.metric-info { display: flex !important; flex-direction: column !important; }
.metric-value { font-size: 26px !important; font-weight: 700 !important; color: var(--text-primary) !important; line-height: 1.1 !important; }
.metric-label { font-size: 12px !important; color: var(--text-muted) !important; font-weight: 500 !important; margin-top: 2px !important; }

/* ---------- FORMS ---------- */
form { background: var(--card-bg) !important; border: 1px solid var(--border-color) !important; border-radius: 12px !important; padding: 24px !important; box-shadow: var(--card-shadow) !important; }

/* ---------- INPUTS / TEXTAREA / SELECT ---------- */
input, textarea, select {
    background-color: var(--input-bg) !important;
    border: 1px solid var(--input-border) !important;
    color: var(--text-secondary) !important;
    border-radius: 8px !important;
    padding: 8px 12px !important;
    transition: all 0.15s ease !important;
    font-size: 14px !important;
}
input:focus, textarea:focus, select:focus {
    border-color: var(--accent) !important;
    box-shadow: 0 0 0 3px var(--accent-light) !important;
}

/* ---------- SIHLECT / DROPDOWN ---------- */
div[data-baseweb="select"] > div { background-color: var(--input-bg) !important; border: 1px solid var(--input-border) !important; border-radius: 8px !important; }
div[data-baseweb="select"] span { color: var(--text-secondary) !important; }
div[data-baseweb="select"] svg { fill: var(--text-muted) !important; }
div[role="listbox"] { background-color: var(--listbox-bg) !important; border: 1px solid var(--border-color) !important; border-radius: 8px !important; }
div[role="option"] { color: var(--text-secondary) !important; }
div[role="option"]:hover { background-color: var(--option-hover) !important; }
[data-baseweb="select"] * { color: var(--text-secondary) !important; }
[data-baseweb="select"] > div { background: var(--input-bg) !important; border: 1px solid var(--input-border) !important; }

/* ---------- TAG (Multiselect chips) ---------- */
span[data-baseweb="tag"] { background-color: var(--accent-light) !important; color: var(--accent) !important; border: 1px solid rgba(59,130,246,0.2) !important; border-radius: 6px !important; }
span[data-baseweb="tag"] svg { fill: var(--accent) !important; }
span[data-baseweb="tag"]:hover { background-color: var(--sidebar-tab-hover) !important; }

/* ---------- TABS ---------- */
button[data-baseweb="tab"] { color: var(--text-secondary) !important; font-weight: 500 !important; padding: 8px 16px !important; transition: all 0.2s ease !important; font-size: 14px !important; background: transparent !important; }
button[data-baseweb="tab"][aria-selected="true"] { color: var(--accent) !important; border-bottom-color: var(--accent) !important; font-weight: 600 !important; }
button[data-baseweb="tab"]:hover { color: var(--text-primary) !important; }

/* ---------- BUTTONS ---------- */
div.stButton > button, div.stFormSubmitButton > button, .stDownloadButton button {
    background: var(--accent) !important;
    color: #ffffff !important;
    border: none !important;
    border-radius: 8px !important;
    padding: 8px 16px !important;
    font-weight: 500 !important;
    font-size: 14px !important;
    transition: all 0.2s ease !important;
    box-shadow: var(--card-shadow) !important;
    width: 100% !important;
}
div.stButton > button:hover, div.stFormSubmitButton > button:hover, .stDownloadButton button:hover {
    background: var(--accent-hover) !important;
    box-shadow: var(--card-shadow-hover) !important;
    transform: translateY(-1px) !important;
}
div.stButton > button:active, div.stFormSubmitButton > button:active { transform: translateY(0px) !important; }

/* ---------- DATAFRAME / TABLE ---------- */
div[data-testid="stDataFrame"] { border: 1px solid var(--border-color) !important; border-radius: 10px !important; overflow: hidden !important; box-shadow: var(--card-shadow) !important; background: var(--card-bg) !important; }
[data-testid="stDataFrame"] * { color: var(--text-secondary) !important; }
[data-testid="stDataFrame"] thead th { color: #64748b !important; font-weight: 600 !important; }
[data-testid="stDataFrame"] tbody td { color: var(--text-secondary) !important; }
[data-testid="stDataFrame"] tr:nth-child(even) { background: rgba(0,0,0,0.015) !important; }
hr { border-color: var(--border-color) !important; }
table { width: 100% !important; border-collapse: collapse !important; background: var(--card-bg) !important; border-radius: 10px !important; overflow: hidden !important; box-shadow: var(--card-shadow) !important; }
table thead tr { background: var(--accent-light) !important; }
table th { color: #64748b !important; padding: 12px !important; text-align: left !important; border-bottom: 1px solid var(--border-color) !important; font-weight: 600 !important; font-size: 13px !important; }
table td { color: var(--text-secondary) !important; padding: 10px 12px !important; border-bottom: 1px solid var(--border-color) !important; font-size: 13px !important; }
table tbody tr:hover { background: rgba(59,130,246,0.03) !important; }

/* ---------- NUMBER INPUT ---------- */
[data-testid="stNumberInput"] input { color: var(--text-secondary) !important; }
[data-testid="stNumberInput"] button {
    background: var(--bg-secondary) !important;
    border: 1px solid var(--border-color) !important;
    color: var(--text-secondary) !important;
    border-radius: 4px !important;
    min-width: 28px !important;
    min-height: 28px !important;
}
[data-testid="stNumberInput"] button:hover { background: var(--option-hover) !important; border-color: var(--accent) !important; }
[data-testid="stNumberInput"] button svg { fill: var(--text-secondary) !important; }

/* ---------- DATE INPUT ---------- */
[data-testid="stDateInput"] input { color: var(--text-secondary) !important; }
[data-testid="stDateInput"] button { color: var(--text-secondary) !important; background: transparent !important; border: none !important; }
[data-testid="stDateInput"] button svg { fill: var(--text-muted) !important; }
[data-testid="stDateInput"] div[data-baseweb="calendar"] { background: var(--card-bg) !important; border: 1px solid var(--border-color) !important; border-radius: 10px !important; box-shadow: var(--card-shadow-hover) !important; }
[data-testid="stDateInput"] div[data-baseweb="calendar"] * { color: var(--text-secondary) !important; }
[data-testid="stDateInput"] div[data-baseweb="calendar"] div[aria-selected="true"] { background: var(--accent-light) !important; color: var(--accent) !important; font-weight: 600 !important; border-radius: 50% !important; }
[data-testid="stDateInput"] div[data-baseweb="calendar"] div:hover { background: var(--option-hover) !important; border-radius: 50% !important; }

/* ---------- MULTISELECT ---------- */
[data-testid="stMultiSelect"] * { color: var(--text-secondary) !important; }
[data-testid="stMultiSelect"] div[data-baseweb="select"] > div { background: var(--input-bg) !important; border: 1px solid var(--input-border) !important; border-radius: 8px !important; }
[data-testid="stMultiSelect"] div[role="listbox"] { background: var(--listbox-bg) !important; border: 1px solid var(--border-color) !important; border-radius: 8px !important; }
[data-testid="stMultiSelect"] div[role="option"] { color: var(--text-secondary) !important; }
[data-testid="stMultiSelect"] div[role="option"]:hover { background: var(--option-hover) !important; }
[data-testid="stMultiSelect"] span[data-baseweb="tag"] { background: var(--accent-light) !important; color: var(--accent) !important; border: 1px solid rgba(59,130,246,0.2) !important; border-radius: 6px !important; }
[data-testid="stMultiSelect"] span[data-baseweb="tag"] svg { fill: var(--accent) !important; }

/* ---------- CHECKBOX ---------- */
[data-testid="stCheckbox"] label { color: var(--text-secondary) !important; }
[data-testid="stCheckbox"] input[type="checkbox"] { accent-color: var(--accent) !important; }
[data-testid="stCheckbox"] label:hover { color: var(--text-primary) !important; }
[data-testid="stCheckbox"] svg { fill: var(--accent) !important; }

/* ---------- RADIO BUTTONS ---------- */
[data-testid="stRadio"] label { color: var(--text-secondary) !important; }
[data-testid="stRadio"] input[type="radio"] { accent-color: var(--accent) !important; }
[data-testid="stRadio"] label:hover { color: var(--text-primary) !important; }
[data-testid="stRadio"] div[role="radiogroup"] label { padding: 6px 10px !important; border-radius: 8px !important; transition: background 0.15s ease !important; }
[data-testid="stRadio"] div[role="radiogroup"] label:hover { background: var(--option-hover) !important; }

/* ---------- SEUGER ---------- */
[data-testid="stSlider"] * { color: var(--text-secondary) !important; }
[data-testid="stSlider"] div[data-baseweb="slider"] { background: var(--border-color) !important; }
[data-testid="stSlider"] div[data-baseweb="slider"] > div { background: var(--accent) !important; }
[data-testid="stSlider"] div[role="slider"] { background: var(--accent) !important; border: 2px solid var(--card-bg) !important; box-shadow: var(--card-shadow) !important; }
[data-testid="stSlider"] div[role="slider"]:hover { box-shadow: var(--card-shadow-hover) !important; }
[data-testid="stSlider"] .st-dv { color: var(--text-muted) !important; }
[data-testid="stSlider"] [data-testid="stTickBar"] { color: var(--text-muted) !important; }

/* ---------- METRIC ---------- */
[data-testid="stMetric"] { background: var(--card-bg) !important; border: 1px solid var(--border-color) !important; border-radius: 10px !important; padding: 16px 20px !important; box-shadow: var(--card-shadow) !important; }
[data-testid="stMetric"] label { color: var(--text-muted) !important; font-size: 12px !important; font-weight: 500 !important; text-transform: uppercase !important; letter-spacing: 0.05em !important; }
[data-testid="stMetric"] [data-testid="stMetricValue"] { color: var(--text-primary) !important; font-size: 24px !important; font-weight: 700 !important; }
[data-testid="stMetric"] [data-testid="stMetricDelta"] { color: var(--text-secondary) !important; }
[data-testid="stMetric"] [data-testid="stMetricDelta"] svg { fill: var(--text-muted) !important; }

/* ---------- EXPANDER ---------- */
[data-testid="stExpander"] { border: 1px solid var(--border-color) !important; border-radius: 10px !important; background: var(--card-bg) !important; box-shadow: var(--card-shadow) !important; overflow: hidden !important; }
[data-testid="stExpander"] summary { font-weight: 600 !important; color: var(--text-primary) !important; padding: 12px 16px !important; }
[data-testid="stExpander"] summary:hover { background: var(--option-hover) !important; }
[data-testid="stExpander"] summary svg { fill: var(--text-muted) !important; }
[data-testid="stExpander"] [role="button"] { color: var(--text-primary) !important; }
[data-testid="stExpander"] .stAlert { border-radius: 0 !important; }

/* ---------- ALERTS (Info, Success, Warning, Error) ---------- */
.stAlert { border-radius: 8px !important; font-size: 13px !important; }
[data-testid="stAlert"] * { color: var(--text-secondary) !important; }
[data-testid="stAlert"] svg { flex-shrink: 0 !important; }
[data-testid="stInfo"] * { color: var(--text-secondary) !important; }
[data-testid="stSuccess"] * { color: var(--text-secondary) !important; }
[data-testid="stWarning"] * { color: var(--text-secondary) !important; }
[data-testid="stError"] * { color: var(--text-secondary) !important; }

/* ---------- PROGRESS ---------- */
[data-testid="stProgress"] * { color: var(--text-secondary) !important; }
[data-testid="stProgress"] div[role="progressbar"] { background: var(--border-color) !important; border-radius: 999px !important; }
[data-testid="stProgress"] div[role="progressbar"] > div { background: var(--accent) !important; border-radius: 999px !important; }

/* ---------- SPINNER ---------- */
[data-testid="stSpinner"] * { color: var(--text-secondary) !important; }
[data-testid="stSpinner"] svg { fill: var(--accent) !important; }

/* ---------- CODE BLOCK ---------- */
[data-testid="stCode"] { background: var(--bg-secondary) !important; border: 1px solid var(--border-color) !important; border-radius: 8px !important; }
[data-testid="stCode"] * { color: var(--text-secondary) !important; }
[data-testid="stCode"] code { color: var(--text-secondary) !important; background: transparent !important; }

/* ---------- CAPTION ---------- */
[data-testid="stCaption"] * { color: var(--text-muted) !important; font-size: 12px !important; }

/* ---------- TOGGLE ---------- */
[data-testid="stToggle"] label { color: var(--text-secondary) !important; }
[data-testid="stToggle"] div[role="switch"] { background: var(--border-color) !important; }
[data-testid="stToggle"] div[role="switch"][aria-checked="true"] { background: var(--accent) !important; }
[data-testid="stToggle"] div[role="switch"] div { background: white !important; }

/* ---------- STATUS ---------- */
[data-testid="stStatus"] * { color: var(--text-secondary) !important; }
[data-testid="stStatus"] svg { fill: var(--accent) !important; }

/* ---------- FILE UPLOADER ---------- */
[data-testid="stFileUploader"] * { color: var(--text-secondary) !important; }
[data-testid="stFileUploader"] button { background: var(--accent) !important; color: white !important; }

/* ---------- COLUMNS ---------- */
[data-testid="column"] { gap: 16px !important; }
.st-cb { color: transparent !important; }

/* ---------- DIVIDER ---------- */
.stDivider { border-color: var(--border-color) !important; }

/* ---------- DOWNLOAD BUTTON ---------- */
.stDownloadButton button { width: 100% !important; }

/* ---------- INFO CARD (Custom) ---------- */
.info-card { background: var(--card-bg) !important; border: 1px solid var(--border-color) !important; border-radius: 10px !important; padding: 16px 20px !important; box-shadow: var(--card-shadow) !important; margin-bottom: 16px !important; }
.info-card-title { font-size: 13px !important; font-weight: 600 !important; color: var(--text-muted) !important; text-transform: uppercase !important; letter-spacing: 0.05em !important; margin-bottom: 6px !important; }
.info-card-value { font-size: 24px !important; font-weight: 700 !important; color: var(--text-primary) !important; }

/* ---------- ACTIVITY FEED ---------- */
.activity-item { display: flex !important; align-items: flex-start !important; gap: 12px !important; padding: 12px 0 !important; border-bottom: 1px solid var(--border-color) !important; }
.activity-item:last-child { border-bottom: none !important; }
.activity-dot { width: 8px !important; height: 8px !important; border-radius: 50% !important; margin-top: 6px !important; flex-shrink: 0 !important; }
.activity-content { flex: 1 !important; }
.activity-text { font-size: 13px !important; color: var(--text-primary) !important; line-height: 1.4 !important; }
.activity-time { font-size: 11px !important; color: var(--text-muted) !important; margin-top: 2px !important; }

/* ---------- MISC ---------- */
.search-box { position: relative !important; margin-bottom: 16px !important; }
.health-safe { color: var(--success) !important; }
.health-warning { color: var(--warning) !important; }
.health-danger { color: var(--danger) !important; }
"""


st.markdown(f"""
<div class="top-nav-bar">
    <div>
        <h1 class="app-title">Aaryan Techno Projects ERP</h1>
        <p class="app-subtitle">Internal Operations & Inventory Control Center</p>
    </div>
</div>

<style>
{css_variables}
{css_styles}
</style>
""", unsafe_allow_html=True)

# Inject custom components JS + CSS
inject_components()

st.divider()


# ---------------- SESSION INIT ----------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.user = None

# ---------------- LOGIN / REGISTER ----------------
if not st.session_state.logged_in:
    st.title("Login")

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

role = st.session_state.user["role"] if st.session_state.user else "user"

# ---------------- SIDEBAR ERP NAV ----------------
st.sidebar.markdown('<p class="sidebar-section-header">Navigation</p>', unsafe_allow_html=True)

page_icons_map = {
    "Dashboard": "Dashboard",
    "Products": "Products",
    "Stock Entry": "Stock Entry",
    "Issue Stock": "Issue Stock",
    "Inventory": "Inventory",
    "Logs": "Logs",
    "Reports": "Reports"
}

selected_page_with_icon = st.sidebar.radio(
    "Modules",
    list(page_icons_map.keys()),
    label_visibility="collapsed"
)

# Handle quick-action navigation from dashboard
if "dash_nav_to" in st.session_state and st.session_state.dash_nav_to:
    nav_target = st.session_state.dash_nav_to
    st.session_state.dash_nav_to = None
    # Find matching page icon
    for icon_key, page_val in page_icons_map.items():
        if page_val == nav_target:
            selected_page_with_icon = icon_key
            break

page = page_icons_map[selected_page_with_icon]

st.sidebar.markdown('<p class="sidebar-section-header">Session</p>', unsafe_allow_html=True)

username = st.session_state.user["username"] if st.session_state.user else "guest"
role_display = st.session_state.user["role"].upper() if st.session_state.user else "USER"
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
    st.markdown(f"""<div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:8px;">
        <h2 style="margin:0;font-weight:700;">Executive Summary</h2>
    </div>""", unsafe_allow_html=True)

    products = get_all_products()
    issues = get_issue_logs()

    total_products = len(products)
    total_issues = len(issues)
    low_stock = len([p for p in products if p.get("quantity", 0) <= 5])
    healthy_stock = total_products - low_stock

    # Recent activity
    recent_issues = sorted(issues, key=lambda x: x.get("date", ""), reverse=True)[:5] if issues else []

    st.markdown(f"""
    <div class="metrics-grid">
        <div class="metric-card">
            <div class="metric-icon" style="background: var(--accent-light); color: var(--accent);"> </div>
            <div class="metric-info">
                <div class="metric-value">{total_products}</div>
                <div class="metric-label">Total Products</div>
            </div>
        </div>
        <div class="metric-card">
            <div class="metric-icon" style="background: var(--success-light); color: var(--success);"> </div>
            <div class="metric-info">
                <div class="metric-value">{healthy_stock}</div>
                <div class="metric-label">Healthy Stock</div>
            </div>
        </div>
        <div class="metric-card">
            <div class="metric-icon" style="background: var(--danger-light); color: var(--danger);"> </div>
            <div class="metric-info">
                <div class="metric-value">{low_stock}</div>
                <div class="metric-label">Low Stock Items</div>
            </div>
        </div>
        <div class="metric-card">
            <div class="metric-icon" style="background: var(--warning-light); color: var(--warning);"> </div>
            <div class="metric-info">
                <div class="metric-value">{total_issues}</div>
                <div class="metric-label">Total Issues</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ---- Quick Actions ----
    st.markdown("### Quick Actions")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        if st.button("Add Product", use_container_width=True, key="dash_add_product"):
            st.session_state.dash_nav_to = "Products"
            st.rerun()
    with col2:
        if st.button("Add Stock", use_container_width=True, key="dash_add_stock"):
            st.session_state.dash_nav_to = "Stock Entry"
            st.rerun()
    with col3:
        if st.button("Issue Stock", use_container_width=True, key="dash_issue_stock"):
            st.session_state.dash_nav_to = "Issue Stock"
            st.rerun()
    with col4:
        if st.button("View Reports", use_container_width=True, key="dash_reports"):
            st.session_state.dash_nav_to = "Reports"
            st.rerun()

    # ---- Recent Activity ----
    st.markdown("### Recent Activity")
    if recent_issues:
        activity_html = ""
        for iss in recent_issues:
            activity_html += f"""
            <div class="activity-item">
                <div class="activity-dot" style="background: var(--accent);"></div>
                <div class="activity-content">
                    <div class="activity-text"><strong>{iss.get('product_name', 'Unknown')}</strong> issued {iss.get('issued_qty', 0)} to <strong>{iss.get('issued_to', 'N/A')}</strong></div>
                    <div class="activity-time">{iss.get('date', '')} &middot; by {iss.get('issued_by', '')}</div>
                </div>
            </div>
            """
        st.markdown(f"""
        <div style="background:var(--card-bg);border:1px solid var(--border-color);border-radius:12px;padding:16px 20px;box-shadow:var(--card-shadow);">
            {activity_html}
        </div>
        """, unsafe_allow_html=True)
    else:
        st.info("No recent activity yet.")


# ---------------- PRODUCTS MODULE ----------------
elif page == "Products":
    st.markdown("<h2 style='margin-bottom:4px;font-weight:700;'>Product Management</h2>", unsafe_allow_html=True)

    products = get_all_products()

    # ---------- SEARCH & FILTER ----------
    if products:
        df = pd.DataFrame(products)
        search_term = st.text_input("Search products by name, code, or supplier...", key="product_search").strip().lower()
        
        # Filter
        if search_term:
            mask = (
                df["name"].str.lower().str.contains(search_term, na=False) |
                df["category"].str.lower().str.contains(search_term, na=False) |
                df["supplier"].str.lower().str.contains(search_term, na=False) |
                df["item_code"].astype(str).str.lower().str.contains(search_term, na=False)
            )
            df_filtered = df[mask]
        else:
            df_filtered = df

        st.markdown(f"<p style='color:var(--text-muted);font-size:13px;margin-bottom:12px;'>Showing {len(df_filtered)} of {len(products)} products</p>", unsafe_allow_html=True)

        if not df_filtered.empty:
            df_display = df_filtered.copy()
            df_display["Stock"] = df_display["quantity"].astype(str) + " " + df_display["unit_type"]
            df_display["Health"] = df_display["quantity"].apply(lambda q: " Good" if q > 15 else (" Medium" if q > 5 else " Low"))
            
            col1, col2 = st.columns([3, 1])
            with col1:
                render_table(df_display[["name","category","supplier","Stock","Health"]], key="products_table")
            with col2:
                st.markdown('<div style="background:var(--card-bg);border:1px solid var(--border-color);border-radius:10px;padding:16px;box-shadow:var(--card-shadow);">', unsafe_allow_html=True)
                st.markdown("##### Stock Health")
                low_count = len(df_filtered[df_filtered["quantity"] <= 5])
                med_count = len(df_filtered[(df_filtered["quantity"] > 5) & (df_filtered["quantity"] <= 15)])
                safe_count = len(df_filtered[df_filtered["quantity"] > 15])
                st.markdown(f"<p style='color:var(--danger);font-size:14px;'>Low: <strong>{low_count}</strong></p>", unsafe_allow_html=True)
                st.markdown(f"<p style='color:var(--warning);font-size:14px;'>Medium: <strong>{med_count}</strong></p>", unsafe_allow_html=True)
                st.markdown(f"<p style='color:var(--success);font-size:14px;'>Good: <strong>{safe_count}</strong></p>", unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)
        else:
            render_alert("No products match your search.", "info")
    else:
        render_alert("No products available. Add your first product below!", "info")

    st.divider()

    # ---------- EXCEL IMPORT ----------
    st.markdown("### Import Products from Excel")

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
                                    0,  # date_added placeholder
                                    cost_price,
                                    None,  # plant_name placeholder
                                    None,  # gate_pass_no placeholder
                                    None,  # gate_pass_date placeholder
                                    0  # sell_price placeholder
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


                    st.success(f"Imported {imported} new products")
                    st.info(f"Updated {updated} existing products")
                    st.warning(f"Skipped {skipped} rows")
                    if errors:
                        st.error(f"{errors} rows failed")

                except Exception as e:
                    st.error(f"Excel import failed: {e}")

    st.divider()

    # ---------- MANUAL ADD FORM ----------
    st.markdown("### Add New Product")

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

        #  SUBMIT BUTTON MUST BE INSIDE FORM
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

                st.success("Product Added Successfully!")
                st.info("Saved")
                st.rerun()

            else:
                st.warning("Already submitted. Please wait 2 seconds.")

    # ---------- DELETE PRODUCT (ADMIN ONLY) ----------
    if role == "admin":
        st.divider()
        st.markdown("### Delete Product (Admin Only)")
        with st.form("delete_product_form"):
            product_options = {
                f"{p['name']} (Code: {p['item_code'] or 'N/A'})": p['product_id']
                for p in products
            }
            if product_options:
                selected_prod_to_delete = st.selectbox(
                    "Select Product to Delete",
                    options=list(product_options.keys())
                )
                
                confirm_delete = st.checkbox(
                    "I confirm that I want to permanently delete this product and all associated issue/movement logs.",
                    key="confirm_delete_checkbox"
                )
                
                submitted_delete = st.form_submit_button("Delete Product")
                
                if submitted_delete:
                    if not confirm_delete:
                        st.error("Please confirm deletion by checking the confirmation box.")
                    else:
                        prod_id = product_options[selected_prod_to_delete]
                        delete_product(prod_id)
                        st.success(" Product and its associated logs deleted successfully!")
                        st.rerun()
            else:
                render_alert("No products available to delete.", "info")


# ---------------- STOCK ENTRY ----------------

elif page == "Stock Entry":
    st.markdown("<h2 style='margin-bottom:4px;font-weight:700;'>Stock Entry</h2>", unsafe_allow_html=True)

    products = get_all_products()

    if products:
        df_products = pd.DataFrame(products)

        col_filter, col_info = st.columns([1, 1])

        with col_filter:
            project_list = sorted(list(set([p["category"] for p in products if p["category"]])))
            selected_project = st.selectbox(
                "Select Project",
                ["All Projects"] + project_list,
                key="stock_entry_project_filter"
            )

            if selected_project != "All Projects":
                products_filtered = [p for p in products if p["category"] == selected_project]
            else:
                products_filtered = products

        if products_filtered:
            product_map = {p["name"]: p for p in products_filtered}

            with col_filter:
                selected_name = st.selectbox(
                    "Select Product",
                    list(product_map.keys()),
                    key="add_stock_product"
                )
                selected_product = product_map[selected_name]

            # Show current stock info card
            with col_info:
                current_qty = selected_product["quantity"]
                unit = selected_product.get("unit_type", "Units")
                health_class = "stock-badge-danger" if current_qty <= 5 else ("stock-badge-warning" if current_qty <= 15 else "stock-badge-safe")
                health_text = "Low" if current_qty <= 5 else ("Medium" if current_qty <= 15 else "Good")
                st.markdown(f"""
                <div style="background:var(--card-bg);border:1px solid var(--border-color);border-radius:10px;padding:16px;box-shadow:var(--card-shadow);height:100%;">
                    <div style="font-size:13px;font-weight:600;color:var(--text-muted);text-transform:uppercase;letter-spacing:0.05em;margin-bottom:8px;">Current Stock</div>
                    <div style="font-size:28px;font-weight:700;color:var(--text-primary);">{current_qty} <span style="font-size:14px;font-weight:400;color:var(--text-muted);">{unit}</span></div>
                    <div style="margin-top:8px;"><span class="stock-badge {health_class}">&#8226; {health_text}</span></div>
                </div>
                """, unsafe_allow_html=True)

            # Stock addition form
            with st.form("add_stock_form"):
                st.markdown("##### + Add Stock")
                col1, col2 = st.columns(2)
                with col1:
                    unit_type = st.selectbox("Unit Type", ["Meter", "Quantity"], key="add_stock_unit")
                    qty = st.number_input(f"Quantity to Add ({unit_type})", min_value=1, step=1, key="add_stock_qty")
                with col2:
                    notes = st.text_input("Notes / Reference", key="add_stock_notes", placeholder="e.g. Supplier delivery #123")
                    st.markdown("<br>", unsafe_allow_html=True)
                    submitted = st.form_submit_button("+ Add Stock", use_container_width=True)

                if submitted:
                    if safe_action_lock("add_stock_lock", cooldown=2):
                        final_notes = f"[{unit_type}] {notes}".strip()
                        update_stock(selected_product["product_id"], qty, "ADD", final_notes)
                        st.success(f"Successfully added {qty} {unit_type} to {selected_name}!")
                        st.rerun()
                    else:
                        st.warning("Already submitted. Please wait 2 seconds.")
        else:
            st.warning("No products found in this project.")
    else:
        render_alert("No products available. Add products first!", "info")


# ---------------- ISSUE STOCK ----------------
elif page == "Issue Stock":
    st.markdown("<h2 style='margin-bottom:4px;font-weight:700;'>Issue Inventory</h2>", unsafe_allow_html=True)

    products = get_all_products()

    if not products:
        st.info("No products available.")
    else:
        df_all = pd.DataFrame(products)

        project_list = ["All Projects"] + sorted(df_all["category"].dropna().unique().tolist())
        col_filter, col_info = st.columns([1, 1])

        with col_filter:
            selected_project = st.selectbox("Select Project", project_list)

        if selected_project != "All Projects":
            filtered_products = [p for p in products if p["category"] == selected_project]
        else:
            filtered_products = products

        if not filtered_products:
            st.warning("No products found in this project.")
        else:
            product_map = {p["name"]: p for p in filtered_products}

            with col_filter:
                selected_name = st.selectbox("Select Product", list(product_map.keys()), key="issue_product")

            selected_product = product_map[selected_name]
            current_qty = selected_product["quantity"]
            unit_type = selected_product.get("unit_type", "Units")

            # Product info card
            with col_info:
                health_class = "stock-badge-danger" if current_qty <= 5 else ("stock-badge-warning" if current_qty <= 15 else "stock-badge-safe")
                health_text = "Low" if current_qty <= 5 else ("Medium" if current_qty <= 15 else "Good")
                st.markdown(f"""
                <div style="background:var(--card-bg);border:1px solid var(--border-color);border-radius:10px;padding:16px;box-shadow:var(--card-shadow);height:100%;">
                    <div style="font-size:13px;font-weight:600;color:var(--text-muted);text-transform:uppercase;letter-spacing:0.05em;margin-bottom:4px;">{selected_name}</div>
                    <div style="font-size:11px;color:var(--text-muted);margin-bottom:8px;">{selected_product.get('category', '')} &middot; {selected_product.get('supplier', '')}</div>
                    <div style="font-size:28px;font-weight:700;color:var(--text-primary);">{current_qty} <span style="font-size:14px;font-weight:400;color:var(--text-muted);">{unit_type}</span></div>
                    <div style="margin-top:8px;"><span class="stock-badge {health_class}">&#8226; Available: {health_text}</span></div>
                </div>
                """, unsafe_allow_html=True)

            with st.form("issue_stock_form"):
                st.markdown("##### Issue Details")
                col1, col2 = st.columns(2)
                with col1:
                    issued_to = st.text_input("Issue To", key="issue_to", placeholder="Person name")
                    issued_qty = st.number_input(f"Quantity to Issue ({unit_type})", min_value=1, max_value=current_qty, step=1, key="issue_qty")
                with col2:
                    used_qty = st.number_input("Used Quantity", min_value=0, max_value=current_qty, step=1, key="used_qty")
                    usage_purpose = st.text_input("Usage Purpose", key="usage_purpose", placeholder="What is it for?")

                remaining_qty = issued_qty - used_qty
                if issued_qty > 0:
                    st.info(f"Remaining with user: **{remaining_qty}** {unit_type}")

                if current_qty <= 5:
                    st.warning(f"Only {current_qty} {unit_type} in stock! Consider restocking.")

                submitted = st.form_submit_button("Submit Issue", use_container_width=True)

                if submitted:
                    if safe_action_lock("issue_lock", cooldown=2):
                        if not issued_to.strip():
                            st.error("Please enter who the item is issued to.")
                        elif used_qty > issued_qty:
                            st.error("Used quantity cannot exceed issued quantity.")
                        elif issued_qty > current_qty:
                            st.error(f"Not enough stock! Only {current_qty} {unit_type} available.")
                        else:
                            issue_product(
                                selected_product["product_id"],
                                issued_to,
                                st.session_state.user["username"],
                                issued_qty,
                                used_qty,
                                usage_purpose
                            )
                            st.success(f"Issued {issued_qty} {unit_type} of {selected_name} to {issued_to}!")
                            st.rerun()
                    else:
                        st.warning("Already submitted. Please wait 2 seconds.")

        st.divider()
        st.markdown("<h3>Edit Issued Records</h3>", unsafe_allow_html=True)

        issues = get_issue_logs()
        if issues:
            product_lookup = {p["product_id"]: p["name"] for p in products}
            issue_map = {}
            for idx, i_val in enumerate(issues):
                pname = product_lookup.get(i_val["product_id"], "Deleted Product")
                issue_map[f"#{idx+1} {pname} → {i_val.get('issued_to','')}"] = i_val

            selected_issue_label = st.selectbox("Select Issue to Edit", list(issue_map.keys()))
            issue = issue_map[selected_issue_label]

            with st.form("edit_issue_form"):
                col1, col2 = st.columns(2)
                with col1:
                    e_issued_to = st.text_input("Issued To", value=issue.get("issued_to", ""))
                    e_qty = st.number_input("Issued Quantity", value=int(issue.get("issued_qty", 0)), step=1)
                with col2:
                    e_used = st.number_input("Used Qty", value=int(issue.get("used_qty", 0)), step=1)
                    e_purpose = st.text_input("Purpose", value=issue.get("usage_purpose", ""))

                if st.form_submit_button("Update Issue"):
                    issue_id = issue.get("issue_id") or issue.get("id")
                    if update_issue(issue_id, e_issued_to, e_qty, e_used, e_purpose):
                        st.success("Issue updated and stock adjusted!")
                        st.rerun()
                    else:
                        st.error("Failed to update issue.")
        else:
            st.info("No issue records available.")

# ---------------- INVENTORY (Stock Health) ----------------
elif page == "Inventory":
    st.markdown("<h2 style='margin-bottom:4px;font-weight:700;'>Inventory & Stock Health</h2>", unsafe_allow_html=True)

    products = get_all_products()
    if not products:            render_alert("No products in inventory.", "info")
    else:
        df = pd.DataFrame(products)

        # Filters
        col1, col2 = st.columns(2)
        with col1:
            project_filter = render_select("Filter by Project", ["All"] + sorted(df["category"].dropna().unique().tolist()), key="inv_project")
        with col2:
            health_filter = render_select("Filter by Health", ["All", "Good", "Medium", "Low"], key="inv_health")

        filtered_df = df.copy()
        if project_filter != "All":
            filtered_df = filtered_df[filtered_df["category"] == project_filter]
        if health_filter != "All":
            if health_filter == "Low":
                filtered_df = filtered_df[filtered_df["quantity"] <= 5]
            elif health_filter == "Medium":
                filtered_df = filtered_df[(filtered_df["quantity"] > 5) & (filtered_df["quantity"] <= 15)]
            elif health_filter == "Good":
                filtered_df = filtered_df[filtered_df["quantity"] > 15]

        # Summary cards
        total_val = len(filtered_df)
        low_val = len(filtered_df[filtered_df["quantity"] <= 5])
        med_val = len(filtered_df[(filtered_df["quantity"] > 5) & (filtered_df["quantity"] <= 15)])
        safe_val = len(filtered_df[filtered_df["quantity"] > 15])

        st.markdown(f"""
        <div class="metrics-grid" style="grid-template-columns:repeat(4,1fr)!important">
            <div class="metric-card"><div class="metric-icon" style="background:var(--accent-light);color:var(--accent);">&#128230;</div><div class="metric-info"><div class="metric-value">{total_val}</div><div class="metric-label">Total Items</div></div></div>
            <div class="metric-card"><div class="metric-icon" style="background:var(--success-light);color:var(--success);">&#9989;</div><div class="metric-info"><div class="metric-value">{safe_val}</div><div class="metric-label">Good Stock</div></div></div>
            <div class="metric-card"><div class="metric-icon" style="background:var(--warning-light);color:var(--warning);">&#128202;</div><div class="metric-info"><div class="metric-value">{med_val}</div><div class="metric-label">Medium Stock</div></div></div>
            <div class="metric-card"><div class="metric-icon" style="background:var(--danger-light);color:var(--danger);">&#9888;&#65039;</div><div class="metric-info"><div class="metric-value">{low_val}</div><div class="metric-label">Low Stock</div></div></div>
        </div>
        """, unsafe_allow_html=True)

        # Table
        if not filtered_df.empty:
            display = filtered_df[["name","category","supplier","quantity","unit_type","item_code"]].copy()
            display.columns = ["Product","Project","Supplier","Qty","Unit","Code"]
            display["Health"] = display["Qty"].apply(
                lambda q: "✅ Good" if q > 15 
                else ("⚠️ Medium" if q > 5 
                else "🔴 Low")
            )
            render_table(display, key="inventory_table")
        else:
            st.info("No products match the selected filters.")# ---------------- LOGS ----------------

elif page == "Logs":
    st.markdown("<h2 style='margin-bottom:4px;font-weight:700;'>Activity Logs</h2>", unsafe_allow_html=True)

    active_tab = render_tabs(["Stock Movements", "Issue Logs"], key="logs_tabs")

    if active_tab == 0:
        history = get_stock_history()
        if history:
            df = pd.DataFrame(history)
            cols = ["date","name","movement_type","change_qty","notes"]
            cols = [c for c in cols if c in df.columns]
            render_table(df[cols], key="stock_movements")
        else:
            render_alert("No stock movements yet.", "info")

    elif active_tab == 1:
        issues = get_issue_logs()
        if issues:
            df = pd.DataFrame(issues)
            cols = ["date","product_name","issued_to","issued_by","issued_qty","used_qty","remaining_qty","usage_purpose"]
            cols = [c for c in cols if c in df.columns]
            render_table(df[cols], key="issue_logs")
        else:
            render_alert("No issued products yet.", "info")

# ---------------- REPORTS ----------------
elif page == "Reports":
    st.markdown("<h2 style='margin-bottom:4px;font-weight:700;'>Master Reports</h2>", unsafe_allow_html=True)

    data = get_interconnected_data()

    if not data:
        render_alert("No records available.", "info")
    else:
        df = pd.DataFrame(data)

        # ---------------- FILTER SECTION ----------------
        with render_expander("Filters", key="report_filters", expanded=True):
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                person_filter = render_select("Person", ["All"] + sorted(df["issued_to"].dropna().unique().tolist()), key="report_person")
            with col2:
                product_filter = render_select("Product", ["All"] + sorted(df["product"].dropna().unique().tolist()), key="report_product")
            with col3:
                category_filter = render_select("Project", ["All"] + sorted(df["category"].dropna().unique().tolist()), key="report_category")
            with col4:
                issuer_filter = render_select("Issuer", ["All"] + sorted(df["issued_by"].dropna().unique().tolist()), key="report_issuer")
        
        # Show issued only toggle
        show_issued_only = st.toggle("Show Issued Items Only", value=False, key="report_show_issued")
        
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

        # ---------------- SUMMARY METRICS ----------------
        unique_products = filtered.drop_duplicates(subset=["product_id"])
        total_stock_had_sum = unique_products["total_stock_had"].sum() if not unique_products.empty else 0
        total_issued_sum = unique_products["total_issued"].sum() if not unique_products.empty else 0
        total_stock_left_sum = unique_products["stock_left"].sum() if not unique_products.empty else 0

        st.markdown("### Stock Summary")
        col_m1, col_m2, col_m3 = st.columns(3)
        with col_m1:
            render_metric("Total Stock I Had", f"{total_stock_had_sum:,}", key="total_had")
        with col_m2:
            render_metric("Stock Issued", f"{total_issued_sum:,}", key="total_issued")
        with col_m3:
            render_metric("Stock Left", f"{total_stock_left_sum:,}", key="total_left")

        # Rename columns
        filtered_disp = filtered.rename(columns={
            "product_id": "Product ID",
            "product": "Product Name",
            "category": "Project",
            "supplier": "Supplier",
            "item_code": "Item Code",
            "contract_number": "Contract Number",
            "plant_name": "Plant Name",
            "gate_pass_no": "Gate Pass No",
            "gate_pass_date": "Gate Pass Date",
            "unit_type": "Unit",
            "current_stock": "Current Stock",
            "date_added": "Date Added",
            "issued_to": "Issued To",
            "issued_by": "Issued By",
            "issued_qty": "Issued Qty",
            "used_qty": "Used Qty",
            "usage_purpose": "Usage Purpose",
            "issue_date": "Issue Date",
            "total_stock_had": "Total Stock I Had",
            "total_issued": "Stock Issued",
            "stock_left": "Stock Left"
        })

        # ---------------- COLUMN VISIBILITY ----------------
        all_columns = list(filtered_disp.columns)
        default_cols = ["Product Name", "Project", "Supplier", "Total Stock I Had", "Stock Issued", "Stock Left", "Issued To", "Issued Qty", "Issue Date"]
        default_selection = [c for c in default_cols if c in all_columns]

        if "visible_master_report_columns" not in st.session_state:
            st.session_state.visible_master_report_columns = default_selection
        else:
            st.session_state.visible_master_report_columns = [c for c in st.session_state.visible_master_report_columns if c in all_columns]
            if not st.session_state.visible_master_report_columns:
                st.session_state.visible_master_report_columns = default_selection

        selected_columns = render_multiselect("Select columns to display", all_columns, key="report_column_selector", default=st.session_state.visible_master_report_columns)
        st.session_state.visible_master_report_columns = selected_columns if selected_columns else default_selection

        # ---------------- MASTER TABLE ----------------
        valid_columns = [c for c in selected_columns if c in filtered_disp.columns] if selected_columns else [c for c in default_selection if c in filtered_disp.columns]
        render_table(filtered_disp[valid_columns], key="master_report_table", height=500)

        # ---------------- EXPORT ----------------
        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine="xlsxwriter") as writer:
            filtered_disp[valid_columns].to_excel(writer, sheet_name="Master Report", index=False)
        buffer.seek(0)
        render_download_button(
            "Download Excel Report",
            filtered_disp[valid_columns],
            "master_inventory_report.xlsx",
            key="report_download"
        )

