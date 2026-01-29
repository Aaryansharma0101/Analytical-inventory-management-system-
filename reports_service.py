from database import get_connection

def get_interconnected_data():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT 
            p.name AS product,
            p.category AS category,
            i.issued_by,
            i.issued_to,
            i.issued_qty,
            i.used_qty,
            i.remaining_qty,
            i.usage_purpose,
            i.date
        FROM issue_logs i
        LEFT JOIN products p 
            ON i.product_id = p.product_id
        ORDER BY i.date DESC
    """)

    rows = cursor.fetchall()
    conn.close()

    return [dict(row) for row in rows]
