from storage import db


def _ensure_user(conn, user_id: int) -> None:
    conn.execute("INSERT OR IGNORE INTO users (user_id) VALUES (?)", (user_id,))


def _balance(conn, user_id: int) -> float:
    return conn.execute("SELECT balance FROM users WHERE user_id = ?", (user_id,)).fetchone()["balance"]


def get_balance(user_id: int) -> float:
    with db() as conn:
        _ensure_user(conn, user_id)
        return _balance(conn, user_id)


def add_money(user_id: int, amount: float) -> float:
    """Пополняет баланс и возвращает новый баланс."""
    with db() as conn:
        _ensure_user(conn, user_id)
        conn.execute("UPDATE users SET balance = balance + ? WHERE user_id = ?", (amount, user_id))
        conn.execute("INSERT INTO transactions (user_id, type, amount) VALUES (?, 'add', ?)", (user_id, amount))
        return _balance(conn, user_id)


def spend_money(user_id: int, amount: float) -> tuple[bool, float]:
    """Списывает сумму, если хватает денег. Возвращает (успех, баланс)."""
    with db() as conn:
        _ensure_user(conn, user_id)
        # Проверка и списание одним запросом, чтобы два одновременных списания не ушли в минус
        cur = conn.execute(
            "UPDATE users SET balance = balance - ? WHERE user_id = ? AND balance >= ?",
            (amount, user_id, amount),
        )
        if cur.rowcount == 0:
            return False, _balance(conn, user_id)
        conn.execute("INSERT INTO transactions (user_id, type, amount) VALUES (?, 'spend', ?)", (user_id, amount))
        return True, _balance(conn, user_id)


def money_text(user_id: int) -> str:
    return f"💰 Баланс: <b>{get_balance(user_id):.2f} грн</b>"


def history_text(user_id: int) -> str:
    with db() as conn:
        rows = conn.execute(
            "SELECT type, amount FROM transactions WHERE user_id = ? ORDER BY id DESC LIMIT 10",
            (user_id,),
        ).fetchall()
    if not rows:
        return "📜 История операций пока пуста."
    lines = ["📜 <b>Последние операции:</b>"]
    for row in rows:
        sign = "+" if row["type"] == "add" else "−"
        lines.append(f"{sign} {row['amount']:.2f} грн")
    return "\n".join(lines)
