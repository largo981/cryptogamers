import logging
from flask import Flask, request, abort
from telegram import Update
from cryptogamers import application, TOKEN

app = Flask(__name__)

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.route(f"/{TOKEN}", methods=['POST'])
def webhook():
    logger.info("Запрос на веб-хук получен.")
    if request.headers.get('content-type') == 'application/json':
        json_str = request.get_data().decode('UTF-8')
        logger.info(f"Полученные данные: {json_str}")
        
        update = Update.de_json(json_str, application.bot)
        
        # Обработка обновления через приложение
        application.process_update(update)
        
        return '', 200
    else:
        logger.warning("Запрос отклонен: неверный content-type")
        abort(403)

if __name__ == "__main__":
    app.run(port=5000)
