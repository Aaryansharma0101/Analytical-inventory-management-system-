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
        name TEXT NOT NULL,
        category TEXT,
        quantity INTEGER DEFAULT 0,
        min_stock INTEGER DEFAULT 5,
        supplier TEXT,
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
        issue_id INTEGER PRIMARY KEY AUTOINCREMENT,
        product_id INTEGER,
        quantity INTEGER,
        issued_to TEXT,
        issued_by TEXT,
        remarks TEXT,
        date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(product_id) REFERENCES products(product_id)
    )
    """)

    conn.commit()
    conn.close()
