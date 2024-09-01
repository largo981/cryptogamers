from pyrogram import Client, filters
import json
import sqlite3

# Загрузка конфигурации из файла bio.json
with open('bio.json', 'r') as file:
    config = json.load(file)

import sqlite3

# Подключение к базе данных
conn = sqlite3.connect('user.db')
cursor = conn.cursor()

# Создание таблицы для пользователей
cursor.execute('''
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY,
    user_id INTEGER NOT NULL UNIQUE,
    balance REAL DEFAULT 0.0,
    referral_id INTEGER
)
''')

conn.commit()
conn.close()


# Инициализация клиента Pyrogram
app = Client(
    "cryptogamers_bot",
    bot_token=config["bot_token"]
)

# Команда /start
@app.on_message(filters.command("start"))
async def start(client, message):
    await message.reply(
        "Привет! Добро пожаловать в Cryptogamers! 🎮\n"
        "Используй команду /menu для начала."
    )

# Команда /menu
@app.on_message(filters.command("menu"))
async def menu(client, message):
    await message.reply(
        "Вот что ты можешь сделать:\n"
        "/randomgame - Сыграть в случайную игру\n"
        "/balance - Проверить свой баланс"
    )

# Запуск бота
app.run()
