import sqlite3
import os

# Функция для проверки и создания базы данных игр
def check_or_create_game_db():
    if not os.path.exists('game.db'):
        conn = sqlite3.connect('game.db')
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS games (
                game_id INTEGER PRIMARY KEY AUTOINCREMENT,
                game_name TEXT NOT NULL,
                game_url TEXT NOT NULL,
                game_category TEXT,
                game_tag TEXT,
                game_description TEXT,
                game_image_base64 TEXT
            )
        ''')
        conn.commit()
        conn.close()
        print("game.db создана.")
    else:
        print("game.db уже существует.")

# Функция для проверки и создания базы данных пользователей
def check_or_create_user_db():
    if not os.path.exists('user.db'):
        conn = sqlite3.connect('user.db')
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                user_name TEXT NOT NULL,
                user_referal INTEGER DEFAULT 0,
                user_balance REAL DEFAULT 0.0,
                user_device TEXT,
                user_install TEXT DEFAULT 'no'
            )
        ''')
        conn.commit()
        conn.close()
        print("user.db создана.")
    else:
        print("user.db уже существует.")

if __name__ == "__main__":
    check_or_create_game_db()
    check_or_create_user_db()
