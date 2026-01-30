import sqlite3
import os

DB_FOLDER = "data"
DB_NAME = "inventory.db"
DB_PATH = os.path.join(DB_FOLDER, DB_NAME)

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    os.makedirs(DB_FOLDER, exist_ok=True)
    conn = get_connection()
    cursor = conn.cursor()

    # Products Table
    cursor.execute("""
CREATE TABLE IF NOT EXISTS products (
    product_id INTEGER PRIMARY KEY AUTOINCREMENT,
    unit_type TEXT DEFAULT 'Quantity',
    name TEXT,
    category TEXT,
    quantity INTEGER DEFAULT 0,
    min_stock INTEGER DEFAULT 5,
    item_code TEXT UNIQUE,
    contract_number TEXT,
    supplier TEXT,
    plant_name TEXT,
    gate_pass_no TEXT,
    gate_pass_date TEXT,
    date_added TEXT,
    cost_price REAL,
    sell_price REAL,
    status TEXT DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
""")


    # Stock Movements Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS stock_movements (
        movement_id INTEGER PRIMARY KEY AUTOINCREMENT,
        product_id INTEGER,
        change_qty INTEGER,
        movement_type TEXT,
        notes TEXT,
        date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(product_id) REFERENCES products(product_id)
    )
    """)

    # Issue Logs Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS issue_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        product_id INTEGER,
        issued_to TEXT,
        issued_by TEXT,
        issued_qty INTEGER,
        used_qty INTEGER DEFAULT 0,
        usage_purpose TEXT,
        remaining_qty INTEGER,
        date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)


    # Users Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        role TEXT DEFAULT 'user',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        status TEXT DEFAULT 'active'
    )
    """)
    # CONSUMPTION LOGS TABLE
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS consumption_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        product_id INTEGER,
        issued_to TEXT,
        consumed_qty INTEGER,
        purpose TEXT,
        consumed_by TEXT,
        date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    conn.commit()
    conn.close()
