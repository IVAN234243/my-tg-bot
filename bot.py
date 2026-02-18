import asyncio
import os
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from dotenv import load_dotenv
from aiohttp import web

# Загружаем токен из файла .env (для локальной разработки)
load_dotenv()
BOT_TOKEN = os.getenv('BOT_TOKEN')

# Создаем объекты бота и диспетчера
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# Команда /start
@dp.message(Command("start"))
async def cmd_start(message: types.Message):
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

# Обёртка для запуска обоих сервисов одновременно
async def main_wrapper():
    # Запускаем веб-сервер как фоновую задачу
    web_task = asyncio.create_task(run_web_server())
    # Запускаем бота
    await main()
    # Если бот завершится (например, из-за ошибки), отменяем веб-сервер
    web_task.cancel()

if __name__ == "__main__":
    try:
        asyncio.run(main_wrapper())
    except KeyboardInterrupt:
        print("Bot stopped")
