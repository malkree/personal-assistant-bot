from storage import db


def load_workouts(user_id: int) -> list[dict]:
    with db() as conn:
        rows = conn.execute(
            "SELECT name, duration FROM workouts WHERE user_id = ? ORDER BY id",
            (user_id,),
        ).fetchall()
    return [dict(row) for row in rows]


def add_workout(user_id: int, name: str, duration: float) -> None:
    with db() as conn:
        conn.execute("INSERT INTO workouts (user_id, name, duration) VALUES (?, ?, ?)", (user_id, name, duration))


def workouts_text(user_id: int) -> str:
    items = load_workouts(user_id)
    if not items:
        return "🏋️ Тренировок пока нет."
    total = sum(item["duration"] for item in items)
    lines = ["🏋️ <b>Тренировки:</b>"]
    lines += [f"{i}. {item['name']} — {item['duration']:.1f} ч." for i, item in enumerate(items, 1)]
    lines.append(f"\n⏱️ Всего: {total:.1f} ч.")
    return "\n".join(lines)
