import json
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import logging
from db_manager import DBManager
from screens_manager import show_welcome_screen, show_random_game_screen, show_balance_screen, invite_friends_screen

# Настраиваем логирование
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelень)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Создаем экземпляр DBManager
db_manager = DBManager()

# Загрузка конфигурации из bio.json
with open('bio.json', 'r') as config_file:
    config = json.load(config_file)
    bot_token = config['bot_token']

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Отправляем приветственное сообщение и регистрируем пользователя"""
    user = update.effective_user
    user_id = user.id
    user_name = user.username

    # Регистрируем пользователя в базе данных
    db_manager.register_user(user_id, user_name)

    # Отправляем сообщение пользователю с кнопками меню
    await show_welcome_screen(update, context)

async def menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Отправляем сообщение с меню"""
    await show_welcome_screen(update, context)

async def balance(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показываем текущий баланс пользователя"""
    user_id = update.effective_user.id
    user_info = db_manager.get_user_info(user_id)

    if user_info:
        balance = user_info[4]  # Предполагаем, что баланс находится в 5-м столбце
        await show_balance_screen(update, context, balance)
    else:
        await update.message.reply_text('Ошибка: Пользователь не найден.')

async def random_game(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Отправляем пользователю случайную игру"""
    game = db_manager.get_random_game()

    if game:
        await show_random_game_screen(update, context, game)
    else:
        await update.message.reply_text('На данный момент нет доступных игр.')

def main():
    """Запуск бота"""
    # Создаем объект Application и передаем ему токен бота из bio.json
    application = Application.builder().token(bot_token).build()

    # Регистрируем обработчики команд
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("menu", menu))
    application.add_handler(CommandHandler("balance", balance))
    application.add_handler(CommandHandler("random_game", random_game))

    # Запускаем бота
    application.run_polling()

if __name__ == '__main__':
    main()
