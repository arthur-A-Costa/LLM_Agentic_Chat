from app.db.session_connection import get_connection

def search_products(product_type: str | None = None) -> list[dict]:
    conn = get_connection()

    try:
        with conn.cursor() as cur:
            if product_type:
                cur.execute(
                    """
                    SELECT
                        product_code,
                        product_name,
                        product_type,
                        description,
                        annual_fee,
                        monthly_interest_rate,
                        minimum_income,
                        max_term_months,
                        risk_level,
                        is_active
                    FROM banking_products
                    WHERE product_type = %s
                      AND is_active = TRUE
                    ORDER BY product_name
                    """,
                    {product_type,}
                )
            else:
                cur.execute(
                    """
                    SELECT
                        product_code,
                        product_name,
                        product_type,
                        description,
                        annual_fee,
                        monthly_interest_rate,
                        minimum_income,
                        max_term_months,
                        risk_level,
                        is_active
                    FROM banking_products
                    WHERE is_active = TRUE
                    ORDER BY product_name
                    """
                )

            columns = [desc[0] for desc in cur.description]
            rows = cur.fetchall()

            return [dict(zip(columns, row)) for row in rows]
        
    finally:
        conn.close()