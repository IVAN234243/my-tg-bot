import asyncio
import os
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from dotenv import load_dotenv
from aiohttp import web  # для маленького веб-сервера

# Загружаем токен из файла .env (для локальной разработки)
load_dotenv()
BOT_TOKEN = os.getenv('BOT_TOKEN')

# Создаем объекты бота и диспетчера
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# Команда /start
@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    # Ссылка на вашу игру (замените на актуальную)
    web_app_info = types.WebAppInfo(url="https://ivan234243.github.io/face-runner-game/")
    keyboard = types.ReplyKeyboardMarkup(
        keyboard=[
            [types.KeyboardButton(text="Открыть приложение", web_app=web_app_info)]
        ],
        resize_keyboard=True
    )
    await message.answer("Привет! Нажми кнопку, чтобы открыть мини-приложение.", reply_markup=keyboard)

# Запуск бота (поллинг)
async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

# Маленький веб-сервер, чтобы Render не ругался
async def handle(request):
    return web.Response(text="I'm alive!")

async def run_web_server():
    app = web.Application()
    app.router.add_get('/', handle)
    runner = web.AppRunner(app)
    await runner.setup()
    port = int(os.environ.get('PORT', 10000))  # Render передаёт порт в переменной PORT
    site = web.TCPSite(runner, '0.0.0.0', port)
    await site.start()
    print(f"Web server started on port {port}")

if __name__ == "__main__":
    # Запускаем веб-сервер в фоне
    loop = asyncio.get_event_loop()
    loop.create_task(run_web_server())
    # Запускаем бота
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Bot stopped")
