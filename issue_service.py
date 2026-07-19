from database import get_connection
from stock_service import update_stock

def issue_product(product_id, issued_to, issued_by, issued_qty, used_qty, usage_purpose):
    remaining_qty = issued_qty - used_qty

    conn = get_connection()
    cursor = conn.cursor()

    # Insert Issue Record
    cursor.execute("""
        INSERT INTO issue_logs 
        (product_id, issued_to, issued_by, issued_qty, used_qty, usage_purpose, remaining_qty)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (product_id, issued_to, issued_by, issued_qty, used_qty, usage_purpose, remaining_qty))

    # Reduce stock
    cursor.execute("""
        UPDATE products 
        SET quantity = quantity - ? 
        WHERE product_id = ?
    """, (issued_qty, product_id))

    conn.commit()
    conn.close()


def get_issue_logs():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT i.*, p.name AS product_name, p.category
        FROM issue_logs i
        JOIN products p ON i.product_id = p.product_id
        ORDER BY i.date DESC
    """)

    rows = cursor.fetchall()
    conn.close()

    return [dict(row) for row in rows]

def update_issue(issue_id, new_issued_to, new_qty, new_used_qty, new_purpose):
    conn = get_connection()
    cursor = conn.cursor()

    # Get old issue record
    cursor.execute("SELECT product_id, issued_qty FROM issue_logs WHERE id = ?", (issue_id,))
    old = cursor.fetchone()

    if not old:
        conn.close()
        return False

    product_id, old_qty = old

    # Calculate stock adjustment
    difference = new_qty - old_qty

    # Update stock (reverse or deduct)
    cursor.execute("""
        UPDATE products 
        SET quantity = quantity - ? 
        WHERE product_id = ?
    """, (difference, product_id))

    # Update issue log
    cursor.execute("""
        UPDATE issue_logs
        SET issued_to = ?, issued_qty = ?, used_qty = ?, usage_purpose = ?
        WHERE id = ?
    """, (new_issued_to, new_qty, new_used_qty, new_purpose, issue_id))

    conn.commit()
    conn.close()
    return True
