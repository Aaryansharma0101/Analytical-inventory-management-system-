"""
Custom HTML/CSS/JS component library for Streamlit.
Replaces default Streamlit widgets with custom modern UI.
All components use the CSS variables defined in app.py.
"""

import streamlit as st
import pandas as pd
import json
import base64
import html
from io import BytesIO

# ──────────────────────────────────────────────────────────────────
# JAVASCRIPT BRIDGE — syncs custom HTML widgets ⇄ hidden Streamlit widgets
# ──────────────────────────────────────────────────────────────────
JS_BRIDGE = """
<script>
// Global sync function — updates hidden Streamlit widget value
window.__sb_sync = function(key, value, type) {
    try {
        // Find the container with data-sk attribute
        var container = document.querySelector('[data-sk="' + key + '"]');
        if (!container) return;
        var el = container.querySelector('input, select, textarea');
        if (!el) return;
        
        // Use native value setter to trigger React/Streamlit
        var nativeSetter = Object.getOwnPropertyDescriptor(
            window.HTMLInputElement.prototype, 'value'
        );
        if (nativeSetter) {
            nativeSetter.set.call(el, value);
        } else {
            el.value = value;
        }
        el.dispatchEvent(new Event('input', { bubbles: true }));
        el.dispatchEvent(new Event('change', { bubbles: true }));
        
        // For select elements, also trigger the select change
        if (el.tagName === 'SELECT') {
            el.dispatchEvent(new Event('change', { bubbles: true }));
        }
    } catch(e) {}
};

// Toggle dropdown visibility
window.__sb_toggleDropdown = function(id) {
    var dd = document.getElementById('sb-dd-' + id);
    if (dd) dd.style.display = dd.style.display === 'block' ? 'none' : 'block';
};

// Close all dropdowns on outside click
document.addEventListener('click', function(e) {
    if (!e.target.closest('.sb-custom-select')) {
        document.querySelectorAll('.sb-dropdown-menu').forEach(function(el) {
            el.style.display = 'none';
        });
    }
});

// Select option in custom dropdown
window.__sb_selectOption = function(key, value, display, close) {
    __sb_sync(key, value, 'select');
    var trigger = document.querySelector('[data-sk-trigger="' + key + '"]');
    if (trigger) trigger.textContent = display;
    if (close !== false) {
        var dd = document.getElementById('sb-dd-' + key);
        if (dd) dd.style.display = 'none';
    }
};

// Toggle multiselect option
window.__sb_toggleMulti = function(key, value, display) {
    var container = document.querySelector('[data-sk="' + key + '"]');
    if (!container) return;
    var inp = container.querySelector('input');
    if (!inp) return;
    
    var current = inp.value ? inp.value.split(',') : [];
    var idx = current.indexOf(value);
    if (idx > -1) { current.splice(idx, 1); }
    else { current.push(value); }
    
    __sb_sync(key, current.join(','), 'text');
    
    // Update tags display
    var tagsEl = document.getElementById('sb-tags-' + key);
    if (tagsEl) {
        var selectedOptions = [];
        document.querySelectorAll('[data-multi-opt="' + key + '"]').forEach(function(opt) {
            var cb = opt.querySelector('input[type="checkbox"]');
            if (cb && cb.checked) selectedOptions.push(cb.value);
        });
        tagsEl.innerHTML = selectedOptions.map(function(v) {
            return '<span class="sb-tag">' + v + ' <span onclick="__sb_removeTag(\'' + key + '\',\'' + v.replace(/'/g,"\\'") + '\')" style="cursor:pointer;opacity:0.6">&#10005;</span></span>';
        }).join('');
    }
};

// Remove tag from multiselect
window.__sb_removeTag = function(key, value) {
    var cb = document.querySelector('[data-multi-opt="' + key + '"] input[value="' + value.replace(/"/g,'&quot;') + '"]');
    if (cb) { cb.checked = false; }
    __sb_toggleMulti(key, value, '');
};

// Toggle expander
window.__sb_toggleExpander = function(id) {
    var content = document.getElementById('sb-exp-' + id);
    var icon = document.getElementById('sb-exp-icon-' + id);
    if (content) {
        if (content.style.maxHeight && content.style.maxHeight !== '0px') {
            content.style.maxHeight = '0px';
            content.style.opacity = '0';
            if (icon) icon.style.transform = 'rotate(0deg)';
        } else {
            content.style.maxHeight = content.scrollHeight + 200 + 'px';
            content.style.opacity = '1';
            if (icon) icon.style.transform = 'rotate(90deg)';
        }
    }
};

// Toggle tab
window.__sb_switchTab = function(group, index) {
    document.querySelectorAll('[data-tab-btn="' + group + '"]').forEach(function(btn, i) {
        btn.classList.toggle('sb-tab-active', i === index);
    });
    document.querySelectorAll('[data-tab-content="' + group + '"]').forEach(function(content, i) {
        content.style.display = i === index ? 'block' : 'none';
    });
    // Update hidden Streamlit tabs if present
    __sb_sync(group + '_tab_idx', index.toString(), 'number');
};

// Sort table
window.__sb_sortTable = function(tableId, colIdx) {
    var table = document.getElementById(tableId);
    if (!table) return;
    var tbody = table.querySelector('tbody');
    if (!tbody) return;
    var rows = Array.from(tbody.querySelectorAll('tr'));
    var header = table.querySelectorAll('th')[colIdx];
    var asc = header.getAttribute('data-sort-asc') !== 'true';
    
    rows.sort(function(a, b) {
        var aVal = (a.children[colIdx] ? a.children[colIdx].textContent.trim() : '');
        var bVal = (b.children[colIdx] ? b.children[colIdx].textContent.trim() : '');
        var aNum = parseFloat(aVal.replace(/[^0-9.-]/g, ''));
        var bNum = parseFloat(bVal.replace(/[^0-9.-]/g, ''));
        if (!isNaN(aNum) && !isNaN(bNum)) {
            return asc ? aNum - bNum : bNum - aNum;
        }
        return asc ? aVal.localeCompare(bVal) : bVal.localeCompare(aVal);
    });
    
    rows.forEach(function(r) { tbody.appendChild(r); });
    header.setAttribute('data-sort-asc', asc ? 'true' : 'false');
    
    // Update sort icons
    table.querySelectorAll('th').forEach(function(th) {
        th.querySelector('.sb-sort-icon').textContent = th === header 
            ? (asc ? ' &#9650;' : ' &#9660;') 
            : ' &#9654;';
    });
};

// Search table
window.__sb_searchTable = function(tableId, inputId) {
    var input = document.getElementById(inputId);
    var table = document.getElementById(tableId);
    if (!input || !table) return;
    var q = input.value.toLowerCase();
    table.querySelectorAll('tbody tr').forEach(function(row) {
        row.style.display = row.textContent.toLowerCase().includes(q) ? '' : 'none';
    });
};
</script>
"""

# ──────────────────────────────────────────────────────────────────
# CSS COMPONENT STYLES (injected once)
# ──────────────────────────────────────────────────────────────────
COMPONENT_CSS = """
<style>
/* ── Custom Select ── */
.sb-custom-select {
    position: relative;
    width: 100%;
    cursor: pointer;
}
.sb-select-trigger {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 8px 12px;
    background: var(--input-bg, #fff) !important;
    border: 1px solid var(--input-border, #e2e8f0) !important;
    border-radius: 8px !important;
    color: var(--text-secondary, #475569) !important;
    font-size: 14px !important;
    transition: border-color 0.15s ease, box-shadow 0.15s ease;
    min-height: 36px;
}
.sb-select-trigger:hover { border-color: var(--accent, #3b82f6); }
.sb-select-trigger:focus-within,
.sb-select-trigger.sb-focused { border-color: var(--accent, #3b82f6); box-shadow: 0 0 0 3px var(--accent-light, rgba(59,130,246,0.1)); }
.sb-select-arrow { font-size: 10px; color: var(--text-muted, #94a3b8); margin-left: 8px; transition: transform 0.2s; }
.sb-dropdown-menu {
    position: absolute;
    top: calc(100% + 4px);
    left: 0;
    right: 0;
    z-index: 999;
    background: var(--card-bg, #fff);
    border: 1px solid var(--border-color, #e2e8f0);
    border-radius: 8px;
    box-shadow: var(--card-shadow-hover, 0 10px 25px -5px rgba(0,0,0,0.08));
    max-height: 220px;
    overflow-y: auto;
    display: none;
}
.sb-dropdown-option {
    padding: 8px 12px;
    cursor: pointer;
    color: var(--text-secondary, #475569) !important;
    font-size: 13px;
    transition: background 0.1s;
}
.sb-dropdown-option:hover { background: var(--option-hover, #f1f5f9); }
.sb-dropdown-option.sb-selected { 
    background: var(--accent-light, rgba(59,130,246,0.1)); 
    color: var(--accent, #3b82f6);
    font-weight: 600;
}
.sb-dropdown-search {
    padding: 6px 8px;
    border-bottom: 1px solid var(--border-color, #e2e8f0);
}
.sb-dropdown-search input {
    width: 100%;
    border: 1px solid var(--input-border, #e2e8f0);
    border-radius: 6px;
    padding: 6px 8px;
    font-size: 12px;
    background: var(--input-bg, #fff) !important;
    color: var(--text-secondary, #475569) !important;
    outline: none;
}
.sb-dropdown-search input:focus { border-color: var(--accent, #3b82f6); }

/* ── Custom Multi-select ── */
.sb-tags-container {
    display: flex;
    flex-wrap: wrap;
    gap: 4px;
    padding: 4px;
    min-height: 28px;
}
.sb-tag {
    display: inline-flex;
    align-items: center;
    gap: 4px;
    padding: 2px 8px;
    background: var(--accent-light, rgba(59,130,246,0.1));
    color: var(--accent, #3b82f6);
    border: 1px solid rgba(59,130,246,0.2);
    border-radius: 6px;
    font-size: 12px;
    font-weight: 500;
}
.sb-multi-option {
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 6px 12px;
    cursor: pointer;
    font-size: 13px;
    color: var(--text-secondary, #475569) !important;
    transition: background 0.1s;
}
.sb-multi-option:hover { background: var(--option-hover, #f1f5f9); }
.sb-multi-option input[type="checkbox"] { accent-color: var(--accent, #3b82f6); }

/* ── Custom Tabs ── */
.sb-tabs-bar {
    display: flex;
    gap: 0;
    border-bottom: 2px solid var(--border-color, #e2e8f0);
    margin-bottom: 16px;
}
.sb-tab-btn {
    padding: 10px 20px;
    cursor: pointer;
    color: var(--text-secondary, #475569);
    font-weight: 500;
    font-size: 14px;
    border-bottom: 2px solid transparent;
    margin-bottom: -2px;
    transition: all 0.2s;
    background: transparent;
    border-top: none;
    border-left: none;
    border-right: none;
    user-select: none;
}
.sb-tab-btn:hover { color: var(--text-primary, #1e293b); }
.sb-tab-btn.sb-tab-active {
    color: var(--accent, #3b82f6);
    border-bottom-color: var(--accent, #3b82f6);
    font-weight: 600;
}
.sb-tab-content { display: none; }
.sb-tab-content.sb-tab-active { display: block; }

/* ── Custom Expander ── */
.sb-expander {
    border: 1px solid var(--border-color, #e2e8f0);
    border-radius: 10px;
    background: var(--card-bg, #fff);
    box-shadow: var(--card-shadow, 0 1px 3px rgba(0,0,0,0.06));
    overflow: hidden;
    margin-bottom: 12px;
}
.sb-expander-header {
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 12px 16px;
    cursor: pointer;
    font-weight: 600;
    color: var(--text-primary, #1e293b);
    font-size: 14px;
    user-select: none;
    transition: background 0.15s;
}
.sb-expander-header:hover { background: var(--option-hover, #f1f5f9); }
.sb-expander-icon {
    font-size: 12px;
    color: var(--text-muted, #94a3b8);
    transition: transform 0.25s ease;
    flex-shrink: 0;
}
.sb-expander-content {
    max-height: 0;
    opacity: 0;
    overflow: hidden;
    transition: max-height 0.3s ease, opacity 0.25s ease, padding 0.25s ease;
    padding: 0 16px;
}
.sb-expander-content.sb-expanded {
    max-height: 2000px;
    opacity: 1;
    padding: 16px;
}

/* ── Custom Table ── */
.sb-table-wrapper {
    border: 1px solid var(--border-color, #e2e8f0);
    border-radius: 10px;
    overflow: hidden;
    box-shadow: var(--card-shadow, 0 1px 3px rgba(0,0,0,0.04));
    background: var(--card-bg, #fff);
}
.sb-table-search {
    padding: 8px 12px;
    border-bottom: 1px solid var(--border-color, #e2e8f0);
}
.sb-table-search input {
    width: 100%;
    border: 1px solid var(--input-border, #e2e8f0);
    border-radius: 6px;
    padding: 6px 10px;
    font-size: 13px;
    background: var(--input-bg, #fff);
    color: var(--text-secondary, #475569);
    outline: none;
    box-sizing: border-box;
}
.sb-table-search input:focus { border-color: var(--accent, #3b82f6); }
.sb-table {
    width: 100%;
    border-collapse: collapse;
    font-size: 13px;
}
.sb-table th {
    background: var(--accent-light, rgba(59,130,246,0.1));
    color: #64748b;
    padding: 10px 12px;
    text-align: left;
    font-weight: 600;
    font-size: 12px;
    cursor: pointer;
    user-select: none;
    white-space: nowrap;
    border-bottom: 1px solid var(--border-color, #e2e8f0);
}
.sb-table th:hover { background: rgba(59,130,246,0.15); }
.sb-sort-icon { font-size: 9px; opacity: 0.5; margin-left: 4px; }
.sb-table td {
    color: var(--text-secondary, #475569);
    padding: 8px 12px;
    border-bottom: 1px solid var(--border-color, #e2e8f0);
}
.sb-table tbody tr:hover { background: rgba(59,130,246,0.03); }
.sb-table tbody tr:nth-child(even) { background: rgba(0,0,0,0.012); }
.sb-table-empty {
    padding: 32px;
    text-align: center;
    color: var(--text-muted, #94a3b8);
    font-size: 14px;
}

/* ── Custom Alerts ── */
.sb-alert {
    display: flex;
    align-items: flex-start;
    gap: 8px;
    padding: 12px 16px;
    border-radius: 8px;
    font-size: 13px;
    border: 1px solid;
    margin-bottom: 8px;
}
.sb-alert-info { background: rgba(59,130,246,0.08); border-color: rgba(59,130,246,0.2); color: var(--text-secondary, #475569); }
.sb-alert-success { background: rgba(16,185,129,0.08); border-color: rgba(16,185,129,0.2); color: var(--text-secondary, #475569); }
.sb-alert-warning { background: rgba(245,158,11,0.08); border-color: rgba(245,158,11,0.2); color: var(--text-secondary, #475569); }
.sb-alert-error { background: rgba(239,68,68,0.08); border-color: rgba(239,68,68,0.2); color: var(--text-secondary, #475569); }
.sb-alert-icon { font-size: 16px; flex-shrink: 0; margin-top: 1px; }

/* ── Custom Metric ── */
.sb-metric-card {
    background: var(--card-bg, #fff);
    border: 1px solid var(--border-color, #e2e8f0);
    border-radius: 10px;
    padding: 16px 20px;
    box-shadow: var(--card-shadow, 0 1px 3px rgba(0,0,0,0.06));
}
.sb-metric-label {
    font-size: 11px;
    font-weight: 600;
    color: var(--text-muted, #94a3b8);
    text-transform: uppercase;
    letter-spacing: 0.05em;
    margin-bottom: 4px;
}
.sb-metric-value {
    font-size: 24px;
    font-weight: 700;
    color: var(--text-primary, #1e293b);
}

/* ── Form container ── */
.sb-form {
    background: var(--card-bg, #fff);
    border: 1px solid var(--border-color, #e2e8f0);
    border-radius: 12px;
    padding: 24px;
    box-shadow: var(--card-shadow, 0 1px 3px rgba(0,0,0,0.06));
}

/* ── Field label ── */
.sb-field-label {
    font-size: 13px;
    font-weight: 500;
    color: var(--text-secondary, #475569);
    margin-bottom: 6px;
    display: block;
}

/* ── Hidden widget wrapper ── */
.sb-hidden {
    position: absolute !important;
    width: 1px !important;
    height: 1px !important;
    padding: 0 !important;
    margin: -1px !important;
    overflow: hidden !important;
    clip: rect(0,0,0,0) !important;
    white-space: nowrap !important;
    border: 0 !important;
    opacity: 0 !important;
}
</style>
"""


# ──────────────────────────────────────────────────────────────────
# UTILITY: Render a hidden Streamlit widget + mark it for JS sync
# ──────────────────────────────────────────────────────────────────
def _hidden_widget(key, widget_fn):
    """Wrap a Streamlit widget in a hidden container with data-sk attribute."""
    st.markdown(f'<div data-sk="{key}" class="sb-hidden">', unsafe_allow_html=True)
    result = widget_fn()
    st.markdown('</div>', unsafe_allow_html=True)
    return result


# ──────────────────────────────────────────────────────────────────
# COMPONENT: Inject global JS + CSS (call once at top of app)
# ──────────────────────────────────────────────────────────────────
def inject_components():
    """Call this once at the top of app.py to inject JS bridge and component CSS."""
    st.markdown(COMPONENT_CSS, unsafe_allow_html=True)
    st.markdown(JS_BRIDGE, unsafe_allow_html=True)


# ──────────────────────────────────────────────────────────────────
# COMPONENT: Custom Rich Table
# ──────────────────────────────────────────────────────────────────
def render_table(df, columns=None, key="table", search=True, height=None):
    """
    Render a pandas DataFrame as a custom HTML table with sorting and search.
    Returns the DataFrame (pass-through for chaining).
    """
    if df is None or df.empty:
        st.markdown('<div class="sb-table-empty">No data to display.</div>', unsafe_allow_html=True)
        return df
    
    display_df = df.copy()
    if columns:
        display_df = display_df[[c for c in columns if c in display_df.columns]]
    
    # Sanitize column names for HTML id
    safe_key = key.replace(" ", "_")
    table_id = f"sb-tbl-{safe_key}"
    search_id = f"sb-src-{safe_key}"
    
    cols = list(display_df.columns)
    headers_html = "".join(
        f'<th onclick="__sb_sortTable(\'{table_id}\',{i})">'
        f'{col}<span class="sb-sort-icon"> &#9654;</span></th>'
        for i, col in enumerate(cols)
    )
    
    rows_html = ""
    for _, row in display_df.iterrows():
        cells_html = "".join(
            f"<td>{str(row[col]) if pd.notna(row[col]) else ''}</td>"
            for col in cols
        )
        rows_html += f"<tr>{cells_html}</tr>"
    
    search_html = (
        f'<div class="sb-table-search">'
        f'<input type="text" id="{search_id}" placeholder="Search table..." '
        f'oninput="__sb_searchTable(\'{table_id}\',\'{search_id}\')" />'
        f'</div>'
    ) if search else ""
    
    style = f"max-height:{height}px;overflow-y:auto;" if height else ""
    
    html_content = f"""
    <div class="sb-table-wrapper" style="{style}">
        {search_html}
        <table class="sb-table" id="{table_id}">
            <thead><tr>{headers_html}</tr></thead>
            <tbody>{rows_html}</tbody>
        </table>
    </div>
    """
    st.markdown(html_content, unsafe_allow_html=True)
    return df


# ──────────────────────────────────────────────────────────────────
# COMPONENT: Custom Select (Dropdown)
# ──────────────────────────────────────────────────────────────────
def render_select(label, options, key="select", default=None, searchable=True):
    """
    Render a custom dropdown selector with hidden Streamlit selectbox.
    Returns the currently selected value.
    """
    # Determine default index
    if default is not None and default in options:
        default_idx = options.index(default)
    else:
        default_idx = 0
    
    # Hidden Streamlit widget
    _hidden_widget(key, lambda: st.selectbox(
        "", options=options, index=default_idx,
        key=f"_sb_{key}", label_visibility="collapsed"
    ))
    
    # Get current value from session state
    current_val = st.session_state.get(f"_sb_{key}", options[default_idx] if options else "")
    current_display = current_val if current_val in options else (options[0] if options else "")
    
    # Build options HTML
    opts_html = ""
    if searchable:
        opts_html += ('<div class="sb-dropdown-search">'
            '<input type="text" placeholder="Search..." '
            'oninput="var dd=this.closest(\'.sb-dropdown-menu\');'
            'dd.querySelectorAll(\'.sb-dropdown-option\').forEach(function(o){'
            'o.style.display=o.textContent.toLowerCase().includes(this.value.toLowerCase())?\'\':\'none\';'
            '})" /></div>')
    for opt in options:
        opt_str = str(opt)
        js_safe_opt = json.dumps(opt_str)  # Returns properly JS-escaped string with quotes
        selected_class = " sb-selected" if opt == current_display else ""
        opts_html += '<div class="sb-dropdown-option{}" onclick="__sb_selectOption(\'{}\',{},{})">{}</div>'.format(
            selected_class, key, js_safe_opt, js_safe_opt, html.escape(opt_str)
        )
    
    html_content = f"""
    <div class="sb-custom-select">
        <label class="sb-field-label">{html.escape(str(label))}</label>
        <div class="sb-select-trigger" onclick="__sb_toggleDropdown('{key}')" data-sk-trigger="{key}">
            <span>{html.escape(str(current_display))}</span>
            <span class="sb-select-arrow">&#9660;</span>
        </div>
        <div class="sb-dropdown-menu" id="sb-dd-{key}">
            {opts_html}
        </div>
    </div>
    """
    st.markdown(html_content, unsafe_allow_html=True)
    return current_val


# ──────────────────────────────────────────────────────────────────
# COMPONENT: Custom Multi-Select
# ──────────────────────────────────────────────────────────────────
def render_multiselect(label, options, key="multi", default=None):
    """
    Render a custom multi-select with tags and hidden Streamlit widget.
    Returns list of selected values.
    """
    if default is None:
        default = []
    default_str = ",".join(default)
    
    _hidden_widget(key, lambda: st.text_input(
        "", value=default_str,
        key=f"_sb_{key}", label_visibility="collapsed"
    ))
    
    raw_val = st.session_state.get(f"_sb_{key}", default_str)
    current_val = [v.strip() for v in raw_val.split(",") if v.strip()]
    
    # Build tags HTML
    tags_html = "".join(
        f'<span class="sb-tag">{v} <span onclick="__sb_removeTag(\'{key}\',\'{v}\')" style="cursor:pointer;opacity:0.6">&#10005;</span></span>'
        for v in current_val
    )
    
    opts_html = ""
    for opt in options:
        checked = "checked" if opt in current_val else ""
        opts_html += f"""
        <label class="sb-multi-option" data-multi-opt="{key}">
            <input type="checkbox" value="{opt}" {checked} onchange="__sb_toggleMulti('{key}','{opt}','{opt}')" />
            <span>{opt}</span>
        </label>
        """
    
    html_content = f"""
    <div class="sb-custom-select">
        <label class="sb-field-label">{label}</label>
        <div class="sb-select-trigger" onclick="__sb_toggleDropdown('{key}')">
            <div class="sb-tags-container" id="sb-tags-{key}">{tags_html}</div>
            <span class="sb-select-arrow">&#9660;</span>
        </div>
        <div class="sb-dropdown-menu" id="sb-dd-{key}" style="padding:4px 0;">
            {opts_html}
        </div>
    </div>
    """
    st.markdown(html_content, unsafe_allow_html=True)
    return current_val


# ──────────────────────────────────────────────────────────────────
# COMPONENT: Custom Tabs
# ──────────────────────────────────────────────────────────────────
def render_tabs(tabs, key="tabs"):
    """
    Render custom tab navigation. Returns the index of the active tab (0-based).
    Usage:
        active = render_tabs(["Tab 1", "Tab 2"], key="my_tabs")
        if active == 0: ...
        elif active == 1: ...
    """
    # Hidden widget for active tab tracking
    _hidden_widget(f"{key}_tab_idx", lambda: st.number_input(
        "", value=0, min_value=0, max_value=len(tabs)-1, step=1,
        key=f"_sb_{key}_tab", label_visibility="collapsed"
    ))
    
    active_idx = int(st.session_state.get(f"_sb_{key}_tab", 0))
    
    btns_html = "".join(
        f'<button class="sb-tab-btn{" sb-tab-active" if i == active_idx else ""}" '
        f'onclick="__sb_switchTab(\'{key}\',{i})">{tab}</button>'
        for i, tab in enumerate(tabs)
    )
    
    html_content = f'<div class="sb-tabs-bar">{btns_html}</div>'
    st.markdown(html_content, unsafe_allow_html=True)
    return active_idx


# ──────────────────────────────────────────────────────────────────
# COMPONENT: Custom Expander
# ──────────────────────────────────────────────────────────────────
def render_expander(title, key="exp", expanded=False):
    """
    Render a custom collapsible expander section.
    Use as a context manager:
        with render_expander("Filters"):
            st.markdown("...")
    Returns a context manager.
    """
    class ExpanderContext:
        def __init__(self, title, key, expanded):
            self.title = title
            self.key = key
            self.expanded = expanded
        
        def __enter__(self):
            state_key = f"_sb_exp_{self.key}"
            is_expanded = st.session_state.get(state_key, self.expanded)
            
            html_content = f"""
            <div class="sb-expander">
                <div class="sb-expander-header" onclick="__sb_toggleExpander('{self.key}')">
                    <span class="sb-expander-icon" id="sb-exp-icon-{self.key}" 
                          style="transform: rotate({'90deg' if is_expanded else '0deg'})">&#9654;</span>
                    <span>{self.title}</span>
                </div>
                <div class="sb-expander-content" id="sb-exp-{self.key}"
                     style="max-height: {'2000px' if is_expanded else '0px'}; opacity: {'1' if is_expanded else '0'}; padding: {'16px' if is_expanded else '0 16px'};">
            """
            st.markdown(html_content, unsafe_allow_html=True)
            return self
        
        def __exit__(self, *args):
            st.markdown('</div></div>', unsafe_allow_html=True)
    
    return ExpanderContext(title, key, expanded)


# ──────────────────────────────────────────────────────────────────
# COMPONENT: Custom Alert
# ──────────────────────────────────────────────────────────────────
def render_alert(message, type="info"):
    """Render a custom alert box. Types: info, success, warning, error."""
    icons = {"info": "&#8505;", "success": "&#10003;", "warning": "&#9888;", "error": "&#10007;"}
    icon = icons.get(type, "&#8505;")
    html_content = f'<div class="sb-alert sb-alert-{type}"><span class="sb-alert-icon">{icon}</span><span>{message}</span></div>'
    st.markdown(html_content, unsafe_allow_html=True)


# ──────────────────────────────────────────────────────────────────
# COMPONENT: Custom Metric Card
# ──────────────────────────────────────────────────────────────────
def render_metric(label, value, key="metric"):
    """Render a custom metric card."""
    html_content = f"""
    <div class="sb-metric-card">
        <div class="sb-metric-label">{label}</div>
        <div class="sb-metric-value">{value}</div>
    </div>
    """
    st.markdown(html_content, unsafe_allow_html=True)


# ──────────────────────────────────────────────────────────────────
# COMPONENT: Custom Form Container
# ──────────────────────────────────────────────────────────────────
def render_form(key="form"):
    """Context manager for custom form container."""
    class FormContext:
        def __enter__(self):
            st.markdown(f'<div class="sb-form" id="sb-form-{key}">', unsafe_allow_html=True)
            return self
        def __exit__(self, *args):
            st.markdown('</div>', unsafe_allow_html=True)
    return FormContext()


# ──────────────────────────────────────────────────────────────────
# COMPONENT: Custom Input Field
# ──────────────────────────────────────────────────────────────────
def render_input(label, key="input", placeholder="", type="text", default=""):
    """Render a custom text input with hidden Streamlit widget."""
    _hidden_widget(key, lambda: st.text_input(
        "", value=default, placeholder=placeholder,
        key=f"_sb_{key}", label_visibility="collapsed"
    ))
    current = st.session_state.get(f"_sb_{key}", default)
    
    html_content = f"""
    <div style="margin-bottom:4px;">
        <label class="sb-field-label">{label}</label>
        <input type="{type}" value="{current}" placeholder="{placeholder}"
               oninput="__sb_sync('{key}', this.value, 'text')"
               style="width:100%;background:var(--input-bg,#fff);border:1px solid var(--input-border,#e2e8f0);
                      border-radius:8px;padding:8px 12px;color:var(--text-secondary,#475569);
                      font-size:14px;outline:none;box-sizing:border-box;"
               onfocus="this.style.borderColor='var(--accent,#3b82f6)';this.style.boxShadow='0 0 0 3px rgba(59,130,246,0.1)'"
               onblur="this.style.borderColor='var(--input-border,#e2e8f0)';this.style.boxShadow='none'" />
    </div>
    """
    st.markdown(html_content, unsafe_allow_html=True)
    return current


# ──────────────────────────────────────────────────────────────────
# COMPONENT: Custom Number Input
# ──────────────────────────────────────────────────────────────────
def render_number_input(label, key="num", min_value=0, max_value=None, step=1, default=0):
    """Render a custom number input with hidden Streamlit widget."""
    _hidden_widget(key, lambda: st.number_input(
        "", value=default, min_value=min_value, max_value=max_value or 999999999,
        step=step, key=f"_sb_{key}", label_visibility="collapsed"
    ))
    current = st.session_state.get(f"_sb_{key}", default)
    
    html_content = f"""
    <div style="margin-bottom:4px;">
        <label class="sb-field-label">{label}</label>
        <input type="number" value="{current}" min="{min_value}" 
               {"max=" + str(max_value) if max_value else ""} step="{step}"
               oninput="__sb_sync('{key}', this.value, 'number')"
               style="width:100%;background:var(--input-bg,#fff);border:1px solid var(--input-border,#e2e8f0);
                      border-radius:8px;padding:8px 12px;color:var(--text-secondary,#475569);
                      font-size:14px;outline:none;box-sizing:border-box;"
               onfocus="this.style.borderColor='var(--accent,#3b82f6)';this.style.boxShadow='0 0 0 3px rgba(59,130,246,0.1)'"
               onblur="this.style.borderColor='var(--input-border,#e2e8f0)';this.style.boxShadow='none'" />
    </div>
    """
    st.markdown(html_content, unsafe_allow_html=True)
    return current


# ──────────────────────────────────────────────────────────────────
# COMPONENT: Custom Date Input
# ──────────────────────────────────────────────────────────────────
def render_date_input(label, key="date", default=None):
    """Render a custom date input with hidden Streamlit widget."""
    from datetime import date, datetime
    
    if default is None:
        default = date.today()
    if isinstance(default, datetime):
        default = default.date()
    
    default_str = default.isoformat() if hasattr(default, 'isoformat') else str(default)
    
    _hidden_widget(key, lambda: st.date_input(
        "", value=default, key=f"_sb_{key}", label_visibility="collapsed"
    ))
    current = st.session_state.get(f"_sb_{key}", default)
    current_str = current.isoformat() if hasattr(current, 'isoformat') else str(current)
    
    html_content = f"""
    <div style="margin-bottom:4px;">
        <label class="sb-field-label">{label}</label>
        <input type="date" value="{current_str}" 
               onchange="__sb_sync('{key}', this.value, 'date')"
               style="width:100%;background:var(--input-bg,#fff);border:1px solid var(--input-border,#e2e8f0);
                      border-radius:8px;padding:8px 12px;color:var(--text-secondary,#475569);
                      font-size:14px;outline:none;box-sizing:border-box;"
               onfocus="this.style.borderColor='var(--accent,#3b82f6)';this.style.boxShadow='0 0 0 3px rgba(59,130,246,0.1)'"
               onblur="this.style.borderColor='var(--input-border,#e2e8f0)';this.style.boxShadow='none'" />
    </div>
    """
    st.markdown(html_content, unsafe_allow_html=True)
    return current


# ──────────────────────────────────────────────────────────────────
# COMPONENT: Custom Button
# ──────────────────────────────────────────────────────────────────
def render_button(label, key="btn", type="primary"):
    """
    Render a custom button. Uses a hidden Streamlit button for state.
    Returns True when clicked.
    """
    clicked = st.button(f"__{label}", key=f"_sb_btn_{key}", label_visibility="collapsed")
    
    bg = "var(--accent,#3b82f6)" if type == "primary" else ("transparent" if type == "secondary" else "var(--danger,#ef4444)")
    color = "white" if type != "secondary" else "var(--text-secondary,#475569)"
    border = "none" if type != "secondary" else "1px solid var(--border-color,#e2e8f0)"
    
    # Hide the real button
    st.markdown(f"""
    <style>
        div[data-testid="stButton"]:has(button[key="_sb_btn_{key}"]),
        button[key="_sb_btn_{key}"] {{ display: none !important; }}
    </style>
    """, unsafe_allow_html=True)
    
    html_content = f"""
    <button onclick="var b=document.querySelector('button[key=\"_sb_btn_{key}\"]');if(b){{b.click();}}"
            style="width:100%;background:{bg};color:{color};border:{border};border-radius:8px;
                   padding:8px 16px;font-weight:500;font-size:14px;cursor:pointer;
                   transition:all 0.2s ease;box-shadow:var(--card-shadow,0 1px 3px rgba(0,0,0,0.06));
                   font-family:var(--font-family,'Inter');"
            onmouseover="this.style.opacity='0.9'"
            onmouseout="this.style.opacity='1'">
        {label}
    </button>
    """
    st.markdown(html_content, unsafe_allow_html=True)
    return clicked


# ──────────────────────────────────────────────────────────────────
# COMPONENT: Custom Download Button
# ──────────────────────────────────────────────────────────────────
def render_download_button(label, data, file_name, mime_type="application/octet-stream", key="dwn"):
    """Render a custom download button."""
    if isinstance(data, pd.DataFrame):
        buffer = BytesIO()
        with pd.ExcelWriter(buffer, engine="xlsxwriter") as writer:
            data.to_excel(writer, sheet_name="Sheet1", index=False)
        buffer.seek(0)
        data = buffer.getvalue()
        if not file_name.endswith('.xlsx'):
            file_name += '.xlsx'
        mime_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    
    b64 = base64.b64encode(data).decode()
    href = f'data:{mime_type};base64,{b64}'
    
    html_content = f"""
    <a href="{href}" download="{file_name}"
       style="display:inline-block;width:100%;background:var(--accent,#3b82f6);color:white;
              border:none;border-radius:8px;padding:8px 16px;font-weight:500;font-size:14px;
              text-align:center;text-decoration:none;cursor:pointer;
              box-shadow:var(--card-shadow,0 1px 3px rgba(0,0,0,0.06));
              font-family:var(--font-family,'Inter');box-sizing:border-box;"
       onmouseover="this.style.opacity='0.9'" onmouseout="this.style.opacity='1'">
        {label}
    </a>
    """
    st.markdown(html_content, unsafe_allow_html=True)
