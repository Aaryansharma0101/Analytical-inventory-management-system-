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
            i.date AS issue_date,

            -- Totals per product
            (p.quantity + COALESCE(sub.total_issued, 0)) AS total_stock_had,
            COALESCE(sub.total_issued, 0) AS total_issued,
            p.quantity AS stock_left

        FROM products p
        LEFT JOIN issue_logs i ON p.product_id = i.product_id
        LEFT JOIN (
            SELECT product_id, SUM(issued_qty) AS total_issued
            FROM issue_logs
            GROUP BY product_id
        ) sub ON p.product_id = sub.product_id

        ORDER BY p.name ASC
    """)

    rows = cursor.fetchall()
    conn.close()

    return [dict(r) for r in rows]

