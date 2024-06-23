import json
from queue import Queue

from loguru import logger
from telegram import Update, InputFile
from telegram.ext import Updater, CommandHandler, MessageHandler, CallbackContext, Application
import requests
import os

import settings

# Файл для хранения пользователей
USERS_FILE = 'users.json'


# Функция для загрузки пользователей из файла
# Функция для загрузки пользователей из файла
def load_users():
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, 'r') as file:
            return json.load(file)
    return {}

# Функция для сохранения пользователей в файл
def save_users(users):
    with open(USERS_FILE, 'w') as file:
        json.dump(users, file)

# Функция для начала работы с ботом
async def start(update: Update, context: CallbackContext) -> None:
    user = update.message.from_user
    users = load_users()
    if user.username not in users:
        users[user.username] = user.id
        save_users(users)
    await update.message.reply_text('Привет! Я бот для уведомлений. Отправьте /notify для получения уведомлений.')

# Функция для отправки уведомлений
async def notify_user(application: Application, username, image_path) -> bool:
    users = load_users()
    if username in users:
        chat_id = users[username]
        if os.path.exists(image_path):
            with open(image_path, 'rb') as image_file:
                await application.bot.send_photo(chat_id=chat_id, photo=InputFile(image_file), caption='Обнаружен объект!')
                return True
        else:
            logger.error(f"Изображение по пути {image_path} не найдено.")
            return False
    else:
        logger.error(f"Пользователь {username} не найден.")
        return False

# Обработчик команды /notify (для тестирования)
async def notify(update: Update, context: CallbackContext) -> None:
    user = update.message.from_user
    # Путь к изображению, которое нужно отправить
    image_path = 'path_to_image.jpg'  # Замените на путь к вашему изображению
    await notify_user(context, user.username, image_path)

def main() -> None:
    # Создание приложения и передача ему токена вашего бота
    application = Application.builder().token(settings.TELEGRAM_TOKEN).build()

    # Обработчики команд
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("notify", notify))

    # Запуск бота
    application.run_polling()

if __name__ == '__main__':
    main()