import asyncio
import os

from dotenv import load_dotenv
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.constants import ParseMode
from telegram.ext import (
    Application, ApplicationHandlerStop, CallbackQueryHandler, CommandHandler,
    ContextTypes, MessageHandler, TypeHandler, filters,
)

import money
import stats
from jurvis import ask_ai
from storage import init_db
from study import add_study, study_text
from tasks import add_task, complete_task, delete_task, load_tasks, task_text
from workouts import add_workout, workouts_text

load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")
MAX_HISTORY = 20
ALLOWED = {int(x) for x in os.getenv("ALLOWED_USERS", "").split(",") if x.strip()}


async def only_allowed(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if user is None or user.id not in ALLOWED:
        raise ApplicationHandlerStop


def kb(rows):
    return InlineKeyboardMarkup([[InlineKeyboardButton(text, callback_data=data) for text, data in row] for row in rows])


def main_kb():
    return kb([
        [("💰 Деньги", "money"), ("📚 Учёба", "study")],
        [("📝 Задачи", "tasks"), ("🏋️ Тренировки", "workouts")],
        [("📊 Статистика", "stats"), ("🤖 Джарвис", "jurvis")],
    ])


def back_kb(section):
    return kb([[("🔙 Назад", "main_menu")], [("↻ Обновить", section)]])


def section_kb(section):
    buttons = {
        "money": [("➕ Пополнить", "money_add"), ("➖ Потратить", "money_spend"), ("📜 История", "money_history")],
        "study": [("➕ Добавить занятие", "study_add")],
        "tasks": [("➕ Добавить задачу", "task_add")],
        "workouts": [("➕ Добавить тренировку", "workout_add")],
    }
    return kb([buttons.get(section, []), [("🔙 Назад", "main_menu")]])


def jurvis_kb():
    return kb([[("🔙 Завершить диалог", "main_menu")]])


async def send_menu(update: Update, text: str, markup=None):
    target = update.callback_query.message if update.callback_query else update.message
    await target.reply_text(text, reply_markup=markup, parse_mode=ParseMode.HTML)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    await update.message.reply_text("Привет! Я твой личный помощник. Выбери раздел:", reply_markup=main_kb())


async def button_click(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    action = query.data
    user_id = update.effective_user.id
    context.user_data.pop("state", None)

    if action == "main_menu":
        await query.edit_message_text("Главное меню:", reply_markup=main_kb())
    elif action == "money":
        await query.edit_message_text(money.money_text(user_id), reply_markup=section_kb("money"), parse_mode=ParseMode.HTML)
    elif action == "money_history":
        await query.edit_message_text(money.history_text(user_id), reply_markup=back_kb("money"), parse_mode=ParseMode.HTML)
    elif action in ("money_add", "money_spend"):
        context.user_data["state"] = action
        prompt = "Введите сумму для пополнения:" if action == "money_add" else "Введите сумму траты:"
        await query.edit_message_text(prompt, reply_markup=back_kb("money"))
    elif action == "study":
        await query.edit_message_text(study_text(user_id), reply_markup=section_kb("study"), parse_mode=ParseMode.HTML)
    elif action == "study_add":
        context.user_data["state"] = "study_subject"
        await query.edit_message_text("Введите предмет или название занятия:", reply_markup=back_kb("study"))
    elif action == "tasks":
        await query.edit_message_text(task_text(user_id), reply_markup=tasks_kb(user_id), parse_mode=ParseMode.HTML)
    elif action == "task_add":
        context.user_data["state"] = "task_add"
        await query.edit_message_text("Введите новую задачу:", reply_markup=back_kb("tasks"))
    elif action.startswith(("task_done:", "task_delete:")):
        kind, task_id = action.split(":")
        if kind == "task_done":
            complete_task(user_id, int(task_id))
        else:
            delete_task(user_id, int(task_id))
        await query.edit_message_text(task_text(user_id), reply_markup=tasks_kb(user_id), parse_mode=ParseMode.HTML)
    elif action == "workouts":
        await query.edit_message_text(workouts_text(user_id), reply_markup=section_kb("workouts"), parse_mode=ParseMode.HTML)
    elif action == "workout_add":
        context.user_data["state"] = "workout_name"
        await query.edit_message_text("Введите название тренировки:", reply_markup=back_kb("workouts"))
    elif action == "stats":
        await query.edit_message_text(stats.stats_text(user_id), reply_markup=back_kb("stats"), parse_mode=ParseMode.HTML)
    elif action == "jurvis":
        context.user_data["state"] = "jurvis"
        context.user_data["jurvis_history"] = []
        await query.edit_message_text(
            "🤖 Джарвис на связи. Напиши свой вопрос:",
            reply_markup=jurvis_kb(),
        )


def tasks_kb(user_id):
    rows = []
    for i, task in enumerate(load_tasks(user_id), 1):
        if not task["completed"]:
            rows.append([
                (f"✅ Выполнить {i}", f"task_done:{task['id']}"),
                (f"🗑️ Удалить {i}", f"task_delete:{task['id']}"),
            ])
    rows.append([("➕ Добавить", "task_add"), ("🔙 Назад", "main_menu")])
    return kb(rows)


async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    state = context.user_data.get("state")
    text = update.message.text.strip()
    user_id = update.effective_user.id
    if not state:
        await update.message.reply_text("Выбери действие кнопкой в меню.", reply_markup=main_kb())
        return
    if state == "jurvis":
        history = context.user_data.setdefault("jurvis_history", [])
        history.append({"role": "user", "content": text})
        del history[:-MAX_HISTORY]
        try:
            answer = await asyncio.to_thread(ask_ai, history)
        except Exception as exc:
            history.pop()
            await update.message.reply_text(f"Ошибка Джарвиса: {exc}", reply_markup=jurvis_kb())
            return
        history.append({"role": "assistant", "content": answer})
        await update.message.reply_text(answer, reply_markup=jurvis_kb())
        return

    if state in ("money_add", "money_spend"):
        try:
            amount = float(text.replace(",", "."))
            if amount <= 0: raise ValueError
        except ValueError:
            await update.message.reply_text("Введите положительное число, например 250.50:")
            return
        if state == "money_add":
            balance = money.add_money(user_id, amount)
            result = f"✅ Добавлено {amount:.2f} грн. Баланс: {balance:.2f} грн"
        else:
            ok, balance = money.spend_money(user_id, amount)
            if not ok:
                await update.message.reply_text(f"❌ Недостаточно средств. Баланс: {balance:.2f} грн")
                return
            result = f"✅ Потрачено {amount:.2f} грн. Баланс: {balance:.2f} грн"
        context.user_data.pop("state", None)
        await update.message.reply_text(result, reply_markup=section_kb("money"))
    elif state == "task_add":
        add_task(user_id, text); context.user_data.pop("state", None)
        await update.message.reply_text("✅ Задача добавлена.", reply_markup=tasks_kb(user_id))
    elif state == "study_subject":
        context.user_data["study_subject"] = text; context.user_data["state"] = "study_hours"
        await update.message.reply_text("Сколько часов заняло занятие?")
    elif state == "study_hours":
        try: hours = float(text.replace(",", ".")); assert hours > 0
        except (ValueError, AssertionError):
            await update.message.reply_text("Введите положительное число часов:"); return
        add_study(user_id, context.user_data.pop("study_subject"), hours); context.user_data.pop("state", None)
        await update.message.reply_text("✅ Занятие добавлено.", reply_markup=section_kb("study"))
    elif state == "workout_name":
        context.user_data["workout_name"] = text; context.user_data["state"] = "workout_duration"
        await update.message.reply_text("Введите длительность в часах:")
    elif state == "workout_duration":
        try: duration = float(text.replace(",", ".")); assert duration > 0
        except (ValueError, AssertionError):
            await update.message.reply_text("Введите положительное число часов:"); return
        add_workout(user_id, context.user_data.pop("workout_name"), duration); context.user_data.pop("state", None)
        await update.message.reply_text("✅ Тренировка добавлена.", reply_markup=section_kb("workouts"))


def main():
    if not TOKEN:
        raise RuntimeError("Не найден BOT_TOKEN в .env")
    if not ALLOWED:
        raise RuntimeError("Не задан ALLOWED_USERS в .env")
    init_db()
    app = Application.builder().token(TOKEN).build()
    app.add_handler(TypeHandler(Update, only_allowed), group=-1)
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", start))
    app.add_handler(CallbackQueryHandler(button_click))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler))
    print("Бот запущен!")
    app.run_polling()


if __name__ == "__main__":
    main()
