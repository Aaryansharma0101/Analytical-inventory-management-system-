from database import get_connection

def update_stock(product_id, change_qty, movement_type, notes=""):
    conn = get_connection()
    cursor = conn.cursor()

    # Update product quantity
    cursor.execute("""
        UPDATE products
        SET quantity = quantity + ?
        WHERE product_id = ?
    """, (change_qty, product_id))

    # Log stock movement
    cursor.execute("""
        INSERT INTO stock_movements (product_id, change_qty, movement_type, notes)
        VALUES (?, ?, ?, ?)
    """, (product_id, change_qty, movement_type, notes))

    conn.commit()
    conn.close()


def get_stock_history():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT sm.*, p.name
        FROM stock_movements sm
        JOIN products p ON sm.product_id = p.product_id
        ORDER BY sm.date DESC
    """)

    rows = cursor.fetchall()
    conn.close()

    return [dict(row) for row in rows]
