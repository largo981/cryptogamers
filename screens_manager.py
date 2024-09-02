import json
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import ContextTypes

# Загрузка сообщений из messages.json с явной указкой кодировки
with open('messages.json', 'r', encoding='utf-8') as file:
    messages = json.load(file)

def get_message(lang, key):
    return messages.get(lang, {}).get(key, "")

async def show_welcome_screen(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Отправляет приветственное сообщение с меню."""
    user_language = update.effective_user.language_code or 'en'
    welcome_text = get_message(user_language, 'start_message')
    
    # Кнопки меню
    keyboard = [
        [KeyboardButton(get_message(user_language, 'random_game_button'))],
        [KeyboardButton(get_message(user_language, 'balance_button'))],
        [KeyboardButton(get_message(user_language, 'Меню'))]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=False)
    
    await update.message.reply_text(welcome_text, reply_markup=reply_markup)

async def show_random_game_screen(update: Update, context: ContextTypes.DEFAULT_TYPE, game):
    """Отправляет информацию о случайной игре."""
    user_language = update.effective_user.language_code or 'en'
    if game:
        game_text = (
            f"**{game['name']}**\n"
            f"#Категория: {game['category']}\n"
            f"#Тэги: {game['tags']}\n"
            f"{game['description']}\n"
        )
        await update.message.reply_text(game_text)
    else:
        no_games_text = get_message(user_language, 'no_games_available')
        await update.message.reply_text(no_games_text)

async def show_balance_screen(update: Update, context: ContextTypes.DEFAULT_TYPE, balance):
    """Отправляет информацию о текущем балансе пользователя."""
    user_language = update.effective_user.language_code or 'en'
    balance_text = get_message(user_language, 'balance_message').format(balance=balance)
    await update.message.reply_text(balance_text)

async def invite_friends_screen(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Отправляет сообщение с предложением пригласить друзей."""
    user_language = update.effective_user.language_code or 'en'
    invite_text = get_message(user_language, 'referral_message')
    await update.message.reply_text(invite_text)
