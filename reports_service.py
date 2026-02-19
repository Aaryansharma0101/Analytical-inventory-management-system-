from database import get_connection

def get_interconnected_data():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            p.product_id,
            p.name AS product,
            p.category,
            p.supplier,
            p.item_code,
            p.contract_number,
            p.plant_name,
            p.gate_pass_no,
            p.gate_pass_date,
            p.unit_type,
            p.quantity AS current_stock,
            p.date_added,

            i.issued_to,
            i.issued_by,
            i.issued_qty,
            i.used_qty,
            i.usage_purpose,
            i.date AS issue_date

        FROM products p
        LEFT JOIN issue_logs i
        ON p.product_id = i.product_id

        ORDER BY p.name ASC
    """)

    rows = cursor.fetchall()
    conn.close()

    return [dict(r) for r in rows]
