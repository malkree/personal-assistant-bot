import os

from openai import OpenAI

SYSTEM_PROMPT = (
    "Ты — Джарвис, грубый и дерзкий персональный ассистент. "
    "Отвечай по-русски, кратко и по делу. "
    "Допускаются мат, сарказм и резкие формулировки. "
    "Главное — сначала дать полезный ответ, а потом добавить характер."
)


def ask_ai(history: list[dict]) -> str:
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        raise RuntimeError("не задан OPENROUTER_API_KEY в .env")
    client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key=api_key)
    response = client.chat.completions.create(
        model=os.getenv("JURVIS_MODEL", "openai/gpt-4o-mini"),
        messages=[{"role": "system", "content": SYSTEM_PROMPT}, *history],
    )
    return response.choices[0].message.content or "Не удалось получить ответ."
