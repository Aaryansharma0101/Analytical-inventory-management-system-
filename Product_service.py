<<<<<<< HEAD
from database import get_connection

def add_product(name, category, quantity, unit_type, min_stock, supplier, cost_price, sell_price):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO products (name, category, quantity, unit_type, min_stock, supplier, cost_price, sell_price)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (name, category, quantity, unit_type, min_stock, supplier, cost_price, sell_price))

    conn.commit()
    conn.close()

def get_all_products():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT * FROM products WHERE status = 'active'
        ORDER BY created_at DESC
    """)

    rows = cursor.fetchall()
    conn.close()

    return [dict(row) for row in rows]

def update_product(product_id, name, category, supplier, min_stock, cost_price, sell_price):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE products
        SET name = ?, category = ?, supplier = ?, min_stock = ?, cost_price = ?, sell_price = ?
        WHERE product_id = ?
    """, (name, category, supplier, min_stock, cost_price, sell_price, product_id))

    conn.commit()
    conn.close()

def delete_product(product_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE products
        SET status = 'inactive'
        WHERE product_id = ?
    """, (product_id,))

    conn.commit()
    conn.close()
=======
from database import get_connection

def add_product(name, category, quantity, min_stock, supplier, cost_price, sell_price):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO products (name, category, quantity, min_stock, supplier, cost_price, sell_price)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (name, category, quantity, min_stock, supplier, cost_price, sell_price))

    conn.commit()
    conn.close()


def get_all_products():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT * FROM products WHERE status = 'active'
        ORDER BY created_at DESC
    """)

    rows = cursor.fetchall()
    conn.close()

    return [dict(row) for row in rows]

def update_product(product_id, name, category, supplier, min_stock, cost_price, sell_price):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE products
        SET name = ?, category = ?, supplier = ?, min_stock = ?, cost_price = ?, sell_price = ?
        WHERE product_id = ?
    """, (name, category, supplier, min_stock, cost_price, sell_price, product_id))

    conn.commit()
    conn.close()

def delete_product(product_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE products
        SET status = 'inactive'
        WHERE product_id = ?
    """, (product_id,))

    conn.commit()
    conn.close()
>>>>>>> daab871577fd9f1ad5aa386bcb7b5c270b28f509
