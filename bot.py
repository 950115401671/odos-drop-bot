import logging
import openai
import os

import os

if os.environ.get("RENDER") != "true" and not os.environ.get("RENDER_EXTERNAL_URL"):
    print("Бот работает только на Render. Локальный запуск заблокирован.")
    exit()
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
from dotenv import load_dotenv
import os

# Загружаем токены из .env файла
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Проверка на наличие токенов
if not BOT_TOKEN or not OPENAI_API_KEY:
    raise ValueError("BOT_TOKEN и OPENAI_API_KEY")

# Настройка OpenAI
openai.api_key = OPENAI_API_KEY

# Настройка логирования
logging.basicConfig(level=logging.INFO)

# Инициализация бота
bot = Bot(token="7002157950:AAEXRDYnAwfev4sDp44UYg0xpIudPskcA2Y")
dp = Dispatcher(bot)

# Стартовая команда
@dp.message_handler(commands=["start", "help"])
async def send_welcome(message: types.Message):
    await message.reply("Здравствуйте! Я — офтальмологический AI-ассистент. Задайте ваш вопрос о зрении 👁️")

# Обработка сообщений
@dp.message_handler()
async def handle_message(message: types.Message):
    try:
        system_prompt = (
            "Ты — опытный врач-офтальмолог, обладающий степенью PhD и специализацией в лечении синдрома сухого глаза. "
            "Ты работаешь как медицинский помощник в рамках проекта ODOS DROP. "
            "Твоя задача — давать предварительную информацию, обучать пациента, рассказывать про режим дня, гигиену глаз, увлажнение. "
            "Ты можешь рекомендовать безрецептурные капли: Systane, Hilo-Komod, Thealoz Duo, Artelac, ODOS DROP. "
            "В сложных случаях советуй обратиться к врачу. Укажи: «Напишите нашему офтальмологу в WhatsApp: https://wa.me/77077643442». "
            "Ты не ставишь диагнозы и не назначаешь рецептурные препараты — ты направляешь к специалисту."
        )

        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": message.text}
            ]
        )

        answer = response['choices'][0]['message']['content']
        await message.reply(answer)

    except Exception as e:
        await message.reply("Произошла ошибка при обращении к ИИ. Проверь настройки и API ключ.")
        logging.error(e)

# Запуск бота
if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)