import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import WebAppInfo
import os
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("BOT_TOKEN")
WEB_APP_URL = os.getenv("NGROK_URL")

bot = Bot(token=TOKEN)
dp = Dispatcher()

@dp.message(Command("start"))
async def start(message: types.Message):
    # Создаем клавиатуру с кнопкой запуска
    markup = types.ReplyKeyboardMarkup(
        keyboard=[
            [types.KeyboardButton(text="♻️ Открыть CleanBurabay", web_app=WebAppInfo(url=WEB_APP_URL))]
        ],
        resize_keyboard=True
    )
    
    await message.answer(
        "Привет! 👋\nЯ помогу сделать Бурабай чище.\nНажми кнопку ниже, чтобы сообщить о мусоре!",
        reply_markup=markup
    )

async def main():
    print("Бот запущен...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())