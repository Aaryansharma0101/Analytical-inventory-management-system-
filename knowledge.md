# Project knowledge

This file gives Freebuff context about your project: goals, commands, conventions, and gotchas.

## Quickstart
- **Install:** `pip install -r requirements.txt`
- **Run:** `streamlit run app.py`
- **Test:** No test framework detected
- **Admin first user:** The first registered user automatically gets the `admin` role (see `auth_service.py`).
- **Make existing user admin:** Run `python make_admin.py` (hardcoded to username "Dipesh" — edit file first).

## Architecture
- **Framework:** Streamlit (v1.53.1), runs on port **8501**
- **Database:** SQLite stored at `data/inventory.db` (see `database.py`)
- **Auth:** bcrypt password hashing via `auth_service.py`
- **Custom UI:** `components.py` provides custom HTML/CSS/JS components (tables, selects, tabs, expanders, alerts, metrics, buttons, forms)
- **Key files:**
  - `app.py` — Main entry point; all Streamlit UI lives here (dashboard, products, stock entry, issue stock, logs, reports)
  - `database.py` — Schema init, connection helper, migration logic for `min_stock`→`initial_quantity`
  - `Product_service.py` — Product CRUD (add, get_all, update, delete)
  - `stock_service.py` — Stock movements (add/remove stock, get history)
  - `issue_service.py` — Issue/release stock to people (create, get logs, update)
  - `reports_service.py` — Interconnected report query (products + issues + summary totals)
  - `consumption_service.py` — Consumption logging
  - `Stockout_prediction.py` — ML-based stockout risk prediction (scikit-learn)
  - `Usage_analytics.py` — Usage analytics (top products, slow/fast, dead stock)
  - `components.py` — Custom UI component library (replaces default Streamlit widgets)
- **Data flow:** app.py imports all service modules → services call database.py → SQLite DB

## Conventions
- **Imports:** All service modules are flat (no packages), imported directly in `app.py`
- **Double-click guard:** Use `safe_action_lock(key, cooldown=2)` before submitting forms to prevent double-submits
- **Forms:** All add/edit forms use `st.form()` with `st.form_submit_button()` (Streamlit best practice)
- **DB schema:** `products`, `stock_movements`, `issue_logs`, `users`, `consumption_logs` tables
- **Theme:** Locked to light mode (`st.session_state.theme = "light"`)
- **Columns:** Product table uses `initial_quantity` (not `min_stock`); migration auto-removes old `min_stock` column
- **CSS injection:** All CSS must be wrapped in `<style>` tags when using `st.markdown()` with `unsafe_allow_html=True`
- **Component injection:** Use `inject_components()` at top of `app.py` to inject custom JS/CSS

## Custom Components (`components.py`)
- **`inject_components()`** — Call once at top of app to inject global CSS and JS bridge
- **`render_table(df, key)`** — Custom sortable/searchable HTML table
- **`render_select(label, options, key)`** — Custom dropdown with search
- **`render_multiselect(label, options, key)`** — Custom multi-select with tags
- **`render_tabs(tabs, key)`** — Custom tab navigation (returns active index)
- **`render_expander(title, key, expanded)`** — Custom collapsible section (context manager)
- **`render_alert(message, type)`** — Custom alert boxes (info/success/warning/error)
- **`render_metric(label, value, key)`** — Custom metric card
- **`render_button(label, key, type)`** — Custom button (primary/secondary/danger)
- **`render_download_button(label, data, file_name, key)`** — Custom download button

## Known Gotchas / Bugs
1. **`issue_service.update_issue`** uses `issue_id` in SQL WHERE clause, but `issue_logs` table PK column is `id`, not `issue_id` → update will never match a row
2. **Devcontainer:** Config references `README.md` which does not exist in the repo
3. **No `.env` support:** All config is hardcoded (database path, admin promotion script has hardcoded username)
4. **Windows paths:** Many file paths use backslashes; use raw strings or forward slashes for cross-platform compatibility

## Recent Changes
- Fixed `Stockout_prediction.py` to use `issued_qty` instead of `quantity` (was causing KeyError)
- Fixed `Usage_analytics.py` to use `issued_qty` instead of `quantity` (was causing KeyError)
- Fixed CSS injection in `components.py` to wrap `COMPONENT_CSS` in `<style>` tags (was rendering as plain text)
- Added `components.py` with custom UI component library
- Updated `app.py` to use custom components throughout
