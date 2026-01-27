from database import get_connection
from stock_service import update_stock

def issue_product(product_id, quantity, issued_to, issued_by="Admin", remarks=""):
    conn = get_connection()
    cursor = conn.cursor()

    # Deduct stock
    update_stock(product_id, -quantity, "ISSUE", f"Issued to {issued_to}")

    # Log issue
    cursor.execute("""
        INSERT INTO issue_logs (product_id, quantity, issued_to, issued_by, remarks)
        VALUES (?, ?, ?, ?, ?)
    """, (product_id, quantity, issued_to, issued_by, remarks))

    conn.commit()
    conn.close()


def get_issue_logs():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT il.*, p.name
        FROM issue_logs il
        JOIN products p ON il.product_id = p.product_id
        ORDER BY il.date DESC
    """)

    rows = cursor.fetchall()
    conn.close()

    return [dict(row) for row in rows]
