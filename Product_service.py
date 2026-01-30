from database import get_connection

def add_product(name, category, quantity, unit_type, supplier, date_added, cost_price, item_code, contract_no, plant_name, gate_pass_no, gate_pass_date):


    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
INSERT INTO products (
    name, category, quantity, unit_type, supplier,
    date_added, cost_price, item_code, contract_number,
    plant_name, gate_pass_no, gate_pass_date
)
VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
""", (
    name, category, quantity, unit_type, supplier,
    date_added, cost_price, item_code, contract_no,
    plant_name, gate_pass_no, gate_pass_date
))


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

def update_product(product_id, name, category, supplier, date_added, cost_price, sell_price):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE products
        SET name = ?, category = ?, supplier = ?, min_stock = ?, cost_price = ?, sell_price = ?
        WHERE product_id = ?
    """, (name, category, supplier,str(date_added), cost_price, sell_price, product_id))

    conn.commit()
    conn.close()

def delete_product(product_id):
    conn = get_connection()
    cursor = conn.cursor()

    # Delete issue logs linked to this product
    cursor.execute("""
        DELETE FROM issue_logs 
        WHERE product_id = ?
    """, (product_id,))

    # Delete stock history linked to this product
    cursor.execute("""
        DELETE FROM stock_history 
        WHERE product_id = ?
    """, (product_id,))

    # Delete the product itself
    cursor.execute("""
        DELETE FROM products 
        WHERE product_id = ?
    """, (product_id,))

    conn.commit()
    conn.close()
