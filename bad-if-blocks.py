"""
BAD EXAMPLE  –  Nested-if policy hell
======================================
All business rules are crammed into a single function.
Adding or disabling one rule means touching (and re-testing)
the entire block.  Welcome to maintenance nightmare.
"""

import psycopg2

DB = dict(host="localhost", dbname="postgres", user="postgres", password="turtlecode", port=5432)


def process_order(order_id: int) -> str:
    conn = psycopg2.connect(**DB)
    cur  = conn.cursor()

    cur.execute(
        """
        SELECT u.id, u.role, u.is_active, u.age, u.country,
               o.amount, o.status
        FROM   orders o
        JOIN   users  u ON u.id = o.user_id
        WHERE  o.id = %s
        """,
        (order_id,),
    )
    row = cur.fetchone()

    if row is None:
        cur.close(); conn.close()
        return f"Order {order_id}: NOT FOUND"

    user_id, role, is_active, age, country, amount, status = row

    # ------------------------------------------------------------------ #
    #  ALL POLICIES JAMMED INTO ONE GIANT IF-CHAIN                        #
    #  Try disabling just the "age" check… good luck not breaking others. #
    # ------------------------------------------------------------------ #
    if status != "pending":
        result = "REJECTED – order is not pending"
    else:
        if not is_active:
            result = "REJECTED – user account is inactive"
        else:
            if age < 18:
                result = "REJECTED – user is under 18"
            else:
                if country in ("KP", "IR", "SY"):
                    result = "REJECTED – country is sanctioned"
                else:
                    if role not in ("admin", "editor"):
                        result = "REJECTED – insufficient role"
                    else:
                        if amount > 5000:
                            result = "REJECTED – amount exceeds limit"
                        else:
                            # finally approve
                            cur.execute(
                                "UPDATE orders SET status='approved' WHERE id=%s",
                                (order_id,),
                            )
                            conn.commit()
                            result = "APPROVED"

    cur.close()
    conn.close()
    return f"Order {order_id}: {result}"


# ── demo ──────────────────────────────────────────────────────────────── #
if __name__ == "__main__":
    for oid in range(1, 6):
        print(process_order(oid))