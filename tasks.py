from storage import db


def load_tasks(user_id: int) -> list[dict]:
    with db() as conn:
        rows = conn.execute(
            "SELECT id, title, completed FROM tasks WHERE user_id = ? ORDER BY id",
            (user_id,),
        ).fetchall()
    return [dict(row) for row in rows]


def add_task(user_id: int, title: str) -> None:
    with db() as conn:
        conn.execute("INSERT INTO tasks (user_id, title) VALUES (?, ?)", (user_id, title))


def complete_task(user_id: int, task_id: int) -> None:
    with db() as conn:
        conn.execute("UPDATE tasks SET completed = 1 WHERE id = ? AND user_id = ?", (task_id, user_id))


def delete_task(user_id: int, task_id: int) -> None:
    with db() as conn:
        conn.execute("DELETE FROM tasks WHERE id = ? AND user_id = ?", (task_id, user_id))


def task_text(user_id: int) -> str:
    tasks = load_tasks(user_id)
    if not tasks:
        return "📝 Список задач пуст."
    return "📝 <b>Задачи:</b>\n" + "\n".join(
        f"{i}. {'✅' if task['completed'] else '⏳'} {task['title']}"
        for i, task in enumerate(tasks, 1)
    )
