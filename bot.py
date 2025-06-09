import logging
import openai
import os
from aiogram import Bot, Dispatcher, types
from aiogram.utils.executor import start_webhook
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
WEBHOOK_HOST = os.getenv("WEBHOOK_HOST")  # Например: https://dashboard.render.com/worker/srv-d10llv15pdvs73a9r27g
WEBHOOK_PATH = f"/webhook/{BOT_TOKEN}"
WEBHOOK_URL = f"{WEBHOOK_HOST}{WEBHOOK_PATH}"

# Проверка окружения Render для защиты от локального запуска
if os.environ.get("RENDER") != "true" and not os.environ.get("RENDER_EXTERNAL_URL"):
    print("Бот работает только на Render. Локальный запуск заблокирован.")
    exit()

if not BOT_TOKEN or not OPENAI_API_KEY or not WEBHOOK_HOST:
    raise ValueError("Не заданы BOT_TOKEN, OPENAI_API_KEY или WEBHOOK_HOST")

openai.api_key = OPENAI_API_KEY

logging.basicConfig(level=logging.INFO)

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)

@dp.message_handler(commands=["start", "help"])
async def send_welcome(message: types.Message):
    await message.reply("Здравствуйте! Я — офтальмологический AI-ассистент. Задайте ваш вопрос о зрении 👁️")

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

async def on_startup(dp):
    await bot.set_webhook(WEBHOOK_URL)
    logging.info(f"Установлен webhook: {WEBHOOK_URL}")

async def on_shutdown(dp):
    logging.warning("Shutting down..")
    await bot.delete_webhook()
    logging.warning("Webhook удалён")
    await dp.storage.close()
    await dp.storage.wait_closed()
    logging.warning("Бот остановлен")

if _name_ == "_main_":
    start_webhook(
        dispatcher=dp,
        webhook_path=WEBHOOK_PATH,
        on_startup=on_startup,
        on_shutdown=on_shutdown,
        skip_updates=True,
        host="0.0.0.0",
        port=int(os.getenv("PORT", 5000))
    )