import sqlite3
from contextlib import closing

class DBManager:
    def __init__(self, user_db_path='user.db', game_db_path='game.db'):
        self.user_db_path = user_db_path
        self.game_db_path = game_db_path

    def _connect(self, db_path):
        # Подключение к базе данных по указанному пути
        return sqlite3.connect(db_path)

    # Функции, связанные с пользователями
    def register_user(self, user_id, user_name, referal_id=None):
        # Проверяем, существует ли пользователь с таким user_id
        with closing(self._connect(self.user_db_path)) as conn, conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
            existing_user = cursor.fetchone()

            if existing_user:
                # Если пользователь уже существует, обновляем его имя и реферальный ID
                cursor.execute(
                    "UPDATE users SET user_name = ?, referal_id = ? WHERE user_id = ?",
                    (user_name, referal_id, user_id)
                )
            else:
                # Если пользователя не существует, добавляем новую запись
                cursor.execute(
                    "INSERT INTO users (user_id, user_name, referal_id) VALUES (?, ?, ?)",
                    (user_id, user_name, referal_id)
                )
            conn.commit()

    def update_user_balance(self, user_id, balance):
        # Обновление баланса пользователя
        with closing(self._connect(self.user_db_path)) as conn, conn:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE users SET user_balance = ? WHERE user_id = ?",
                (balance, user_id)
            )
            conn.commit()

    def get_user_info(self, user_id):
        # Получение информации о пользователе по его ID
        with closing(self._connect(self.user_db_path)) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
            return cursor.fetchone()

    # Функции, связанные с играми
    def get_random_game(self):
        # Получение случайной игры из базы данных
        with closing(self._connect(self.game_db_path)) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM games ORDER BY RANDOM() LIMIT 1")
            return cursor.fetchone()

    def get_game_by_id(self, game_id):
        # Получение информации об игре по её ID
        with closing(self._connect(self.game_db_path)) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM games WHERE game_id = ?", (game_id,))
            return cursor.fetchone()
