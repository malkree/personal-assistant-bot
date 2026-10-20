from money import money_text
from storage import db


def stats_text(user_id: int) -> str:
    # Считаем прямо в SQL, не вытаскивая все строки в Python
    with db() as conn:
        tasks = conn.execute(
            "SELECT COUNT(*) AS total, COALESCE(SUM(completed), 0) AS done FROM tasks WHERE user_id = ?",
            (user_id,),
        ).fetchone()
        study_hours = conn.execute(
            "SELECT COALESCE(SUM(hours), 0) AS s FROM study WHERE user_id = ?", (user_id,)
        ).fetchone()["s"]
        workouts = conn.execute(
            "SELECT COUNT(*) AS n, COALESCE(SUM(duration), 0) AS s FROM workouts WHERE user_id = ?",
            (user_id,),
        ).fetchone()
    total, completed = tasks["total"], tasks["done"]
    progress = completed / total * 100 if total else 0
    return (
        "📊 <b>Статистика</b>\n\n"
        f"{money_text(user_id)}\n"
        f"📝 Задачи: {completed}/{total} выполнено ({progress:.0f}%)\n"
        f"📚 Учёба: {study_hours:.1f} ч.\n"
        f"🏋️ Тренировок: {workouts['n']} ({workouts['s']:.1f} ч.)"
    )
