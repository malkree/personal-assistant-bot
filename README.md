# Personal Assistant Bot

A personal Telegram bot written in Python as a learning project. It keeps track of money, study time, tasks and workouts, and includes "Jurvis", a sarcastic AI assistant that remembers the recent conversation.

## Features

- **Money:** add income, record expenses, see the balance and the last 10 operations. Spending is checked and applied in a single SQL query, so the balance can never go negative.
- **Tasks:** add tasks, mark them as done, delete them.
- **Study:** log study sessions with the subject and hours spent.
- **Workouts:** log workouts with the name and duration.
- **Statistics:** one screen with the balance, completed tasks, study hours and workouts.
- **Jurvis (AI chat):** talks through the OpenRouter API and remembers the last 20 messages of the current dialogue.
- **Access control:** only the Telegram user IDs listed in `ALLOWED_USERS` can use the bot.

## Tech stack

- Python 3.9+
- [python-telegram-bot](https://python-telegram-bot.org/) (inline keyboards, conversation states)
- SQLite (built-in `sqlite3` module)
- OpenRouter API via the `openai` client
- `python-dotenv` for configuration

## Project structure

```
bot.py        # Telegram handlers, menus and dialogue states
jurvis.py     # AI assistant (OpenRouter API call)
storage.py    # SQLite connection and database schema
money.py      # balance and transactions
tasks.py      # task list
study.py      # study log
workouts.py   # workout log
stats.py      # statistics screen
```

## Setup

1. Clone the repository and install the dependencies:

   ```bash
   pip install -r requirements.txt
   ```

2. Create a bot with [@BotFather](https://t.me/BotFather) and get an API key from [OpenRouter](https://openrouter.ai/).

3. Copy `.env.example` to `.env` and fill in the values:

   ```
   BOT_TOKEN=your_telegram_bot_token
   OPENROUTER_API_KEY=your_openrouter_key
   ALLOWED_USERS=123456789
   ```

   `ALLOWED_USERS` is a comma-separated list of Telegram user IDs. You can find your ID with [@userinfobot](https://t.me/userinfobot). Optionally, set `JURVIS_MODEL` to choose another OpenRouter model.

4. Run the bot:

   ```bash
   python bot.py
   ```

   The database file `bot.db` is created automatically on the first start.

## Security notes

- Never commit your `.env` file. It is listed in `.gitignore`.
- The bot refuses to start if `ALLOWED_USERS` is empty, so it cannot be left open to everyone by accident.

## What I learned

Building this project, I practiced working with an asynchronous Telegram API, handling dialogue states, moving data from JSON files to a SQL database, and protecting secrets and access in a public repository.
