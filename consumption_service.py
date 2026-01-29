from database import get_connection

def log_consumption(product_id, issued_to, consumed_qty, purpose, consumed_by):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO consumption_logs 
        (product_id, issued_to, consumed_qty, purpose, consumed_by)
        VALUES (?, ?, ?, ?, ?)
    """, (product_id, issued_to, consumed_qty, purpose, consumed_by))

    conn.commit()
    conn.close()


def get_consumption_logs():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT c.*, p.name
        FROM consumption_logs c
        JOIN products p ON c.product_id = p.product_id
        ORDER BY c.date DESC
    """)

    rows = cursor.fetchall()
    conn.close()

    return [dict(row) for row in rows]
