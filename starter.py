import subprocess
import os
import sys
import shutil

# Определяем пути к файлам
db_checker_script = os.path.join(os.getcwd(), 'dbchecker.py')
bot_script = os.path.join(os.getcwd(), 'cryptogamers.py')
webhook_script = os.path.join(os.getcwd(), 'webhook.py')
messages_file = os.path.join(os.getcwd(), 'messages.json')

# Функция для запуска процесса
def run_script(script_path):
    return subprocess.Popen([sys.executable, script_path], stdout=sys.stdout, stderr=sys.stderr)

def check_messages_file():
    if not os.path.exists(messages_file):
        print(f"Файл {messages_file} не найден. Пожалуйста, создайте его перед запуском.")
        sys.exit(1)
    else:
        print(f"Файл {messages_file} найден.")

if __name__ == "__main__":
    try:
        # Проверка наличия файла messages.json
        check_messages_file()

        # Запуск проверки и создания баз данных
        db_checker_process = run_script(db_checker_script)
        db_checker_process.wait()  # Ждем завершения dbchecker.py перед запуском остальных скриптов
        print(f"Проверка баз данных завершена: PID {db_checker_process.pid}")

        # Запуск основного бота
        bot_process = run_script(bot_script)
        print(f"Запущен основной бот: PID {bot_process.pid}")
        
        # Запуск сервера webhook
        webhook_process = run_script(webhook_script)
        print(f"Запущен сервер webhook: PID {webhook_process.pid}")

        # Ожидание завершения процессов
        bot_process.wait()
        webhook_process.wait()

    except KeyboardInterrupt:
        print("Остановка процессов...")
        bot_process.terminate()
        webhook_process.terminate()

    except Exception as e:
        print(f"Произошла ошибка: {e}")
        bot_process.terminate()
        webhook_process.terminate()
