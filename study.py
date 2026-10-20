from storage import db


def load_study(user_id: int) -> list[dict]:
    with db() as conn:
        rows = conn.execute(
            "SELECT subject, hours FROM study WHERE user_id = ? ORDER BY id",
            (user_id,),
        ).fetchall()
    return [dict(row) for row in rows]


def add_study(user_id: int, subject: str, hours: float) -> None:
    with db() as conn:
        conn.execute("INSERT INTO study (user_id, subject, hours) VALUES (?, ?, ?)", (user_id, subject, hours))


def study_text(user_id: int) -> str:
    items = load_study(user_id)
    if not items:
        return "📚 Занятий пока нет."
    total = sum(item["hours"] for item in items)
    lines = ["📚 <b>Учёба:</b>"]
    lines += [f"{i}. {item['subject']} — {item['hours']:.1f} ч." for i, item in enumerate(items, 1)]
    lines.append(f"\n⏱️ Всего: {total:.1f} ч.")
    return "\n".join(lines)
