"""
GOOD EXAMPLE  –  Simple Policy Registry
"""

import psycopg2

DB = dict(host="localhost", dbname="postgres", user="postgres", password="turtlecode", port=5432)


# ── 1. Toggle policies here ───────────────────────────────────────────── #
POLICIES = {
    "order_pending"     : True,
    "user_active"       : True,
    "minimum_age"       : True,
    "sanctioned_country": True,
    "role_permission"   : True,
    "amount_limit"      : True,
}


# ── 2. One function per policy ────────────────────────────────────────── #
def policy_order_pending(order: dict) -> str | None:
    if order["status"] != "pending":
        return "order is not pending"

def policy_user_active(order: dict) -> str | None:
    if not order["is_active"]:
        return "user account is inactive"

def policy_minimum_age(order: dict) -> str | None:
    if order["age"] < 18:
        return "user is under 18"

def policy_sanctioned_country(order: dict) -> str | None:
    if order["country"] in {"KP", "IR", "SY"}:
        return "country is sanctioned"

def policy_role_permission(order: dict) -> str | None:
    if order["role"] not in {"admin", "editor"}:
        return "insufficient role"

def policy_amount_limit(order: dict) -> str | None:
    if order["amount"] > 5000:
        return f"amount {order['amount']} exceeds limit 5000"


# ── 3. Registry maps name → function ─────────────────────────────────── #
REGISTRY = {
    "order_pending"     : policy_order_pending,
    "user_active"       : policy_user_active,
    "minimum_age"       : policy_minimum_age,
    "sanctioned_country": policy_sanctioned_country,
    "role_permission"   : policy_role_permission,
    "amount_limit"      : policy_amount_limit,
}


# ── 4. Run all active policies ────────────────────────────────────────── #
def evaluate(order: dict) -> tuple[bool, str]:
    for name, fn in REGISTRY.items():
        if not POLICIES[name]:          # skip if disabled
            continue
        error = fn(order)
        if error:
            return False, f"[{name}] {error}"
    return True, "all policies passed"


# ── 5. Process order ──────────────────────────────────────────────────── #
def process_order(order_id: int) -> str:
    conn = psycopg2.connect(**DB)
    cur  = conn.cursor()

    cur.execute(
        """
        SELECT u.role, u.is_active, u.age, u.country, o.amount, o.status
        FROM   orders o
        JOIN   users  u ON u.id = o.user_id
        WHERE  o.id = %s
        """,
        (order_id,),
    )
    row = cur.fetchone()
    if not row:
        return f"Order {order_id}: NOT FOUND"

    order = dict(zip(["role", "is_active", "age", "country", "amount", "status"], row))

    passed, reason = evaluate(order)

    if passed:
        cur.execute("UPDATE orders SET status='approved' WHERE id=%s", (order_id,))
        conn.commit()

    cur.close()
    conn.close()
    return f"Order {order_id}: {'APPROVED' if passed else f'REJECTED – {reason}'}"


# ── Demo ──────────────────────────────────────────────────────────────── #
if __name__ == "__main__":

    print("--- Round 1: All policies ON ---")
    for oid in range(1, 6):
        print(process_order(oid))