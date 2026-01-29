<<<<<<< HEAD
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
=======
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
>>>>>>> daab871577fd9f1ad5aa386bcb7b5c270b28f509
