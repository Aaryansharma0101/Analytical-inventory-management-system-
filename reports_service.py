from database import get_connection

def get_interconnected_data():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            i.id AS issue_id,
            p.name AS product,
            p.category AS category,
            p.supplier AS supplier,
            p.item_code AS item_code,
            p.contract_number AS contract_number,
            p.plant_name AS plant_name,
            p.gate_pass_no AS gate_pass_no,
            p.gate_pass_date AS gate_pass_date,
            p.unit_type AS unit_type,
            p.quantity AS total_stock,

            i.issued_to,
            i.issued_by,
            i.issued_qty,
            i.used_qty,
            i.usage_purpose,
            (p.quantity - i.issued_qty) AS remaining_qty,
            i.date

        FROM issue_logs i
        JOIN products p ON i.product_id = p.product_id
        ORDER BY i.date DESC
    """)

    rows = cursor.fetchall()
    conn.close()

    return [dict(r) for r in rows]

