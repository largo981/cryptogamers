import sqlite3
import json
import logging
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Application, CommandHandler, CallbackContext, MessageHandler, filters

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Загрузка конфигурации из bio.json
with open('bio.json', 'r', encoding='utf-8') as file:
    config = json.load(file)

# Загрузка сообщений из messages.json
with open('messages.json', 'r', encoding='utf-8') as file:
    messages = json.load(file)

TOKEN = config.get('bot_token')

# Создаем приложение
application = Application.builder().token(TOKEN).build()

# Подключение к базам данных
conn_user = sqlite3.connect('user.db', check_same_thread=False)
cursor_user = conn_user.cursor()

conn_game = sqlite3.connect('game.db', check_same_thread=False)
cursor_game = conn_game.cursor()

# Функция для регистрации пользователя
def register_user(user_id, user_name, user_referal=0):
    try:
        cursor_user.execute('SELECT * FROM users WHERE user_id=?', (user_id,))
        user = cursor_user.fetchone()

        if user is None:
            logger.info(f"Добавляем нового пользователя: {user_name} с ID: {user_id}")
            cursor_user.execute('''
                INSERT INTO users (user_id, user_name, user_referal, user_balance, user_device, user_install)
                VALUES (?, ?, ?, 0.0, '', 'no')
            ''', (user_id, user_name, user_referal))
            conn_user.commit()
            logger.info(f"Пользователь {user_name} с ID: {user_id} успешно добавлен.")
        else:
            logger.info(f"Пользователь уже существует: {user_name} с ID: {user_id}")
    except Exception as e:
        logger.error(f"Ошибка при добавлении пользователя: {e}")

# Обработчик команды /start
async def start(update: Update, context: CallbackContext):
    user = update.message.from_user
    language = user.language_code if user.language_code in messages else 'en'
    start_message = messages[language]['start_message']
    
    register_user(user.id, user.username or user.first_name)

    # Кнопки меню
    keyboard = [
        [KeyboardButton(messages[language]['random_game_button'])],
        [KeyboardButton(messages[language]['balance_button'])]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    
    await update.message.reply_text(start_message, reply_markup=reply_markup)

# Обработчик команды /balance
async def balance(update: Update, context: CallbackContext):
    user = update.message.from_user
    language = user.language_code if user.language_code in messages else 'en'
    
    cursor_user.execute('SELECT user_balance FROM users WHERE user_id=?', (user.id,))
    user_balance = cursor_user.fetchone()[0]

    balance_message = messages[language]['balance_message'].format(balance=user_balance)
    await update.message.reply_text(balance_message)

# Обработчик кнопки "Случайная игра"
async def random_game(update: Update, context: CallbackContext):
    user = update.message.from_user
    language = user.language_code if user.language_code in messages else 'en'
    
    cursor_game.execute('SELECT * FROM games ORDER BY RANDOM() LIMIT 1')
    game = cursor_game.fetchone()
    
    if game:
        game_name = f"*{game[1]}*"
        game_category = f"#{game[3]}"
        game_tag = f"#{game[4]}"
        game_description = f"_{game[5]}_"
        game_image = game[6]  # Декодирование base64 не требуется, т.к. это строка для Telegram

        random_game_message = (
            f"{game_name}\n{game_category} {game_tag}\n"
            f"{game_description}\n{game_image}"
        )
        await update.message.reply_text(random_game_message, parse_mode="Markdown")
    else:
        await update.message.reply_text(messages[language]['no_games_available'])

# Обработчик текстовых сообщений
async def handle_message(update: Update, context: CallbackContext):
    user_message = update.message.text
    user = update.message.from_user
    language = user.language_code if user.language_code in messages else 'en'
    
    if user_message == messages[language]['random_game_button']:
        await random_game(update, context)
    elif user_message == messages[language]['balance_button']:
        await balance(update, context)

# Добавляем обработчики команд и сообщений
application.add_handler(CommandHandler('start', start))
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

# Запуск бота
if __name__ == '__main__':
    try:
        application.run_polling()
    finally:
        conn_user.close()
        conn_game.close()
        logger.info("Соединения с базой данных закрыты.")
