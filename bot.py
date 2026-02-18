import asyncio
import os
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from dotenv import load_dotenv
from aiohttp import web

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Загружаем токен из файла .env (для локальной разработки)
load_dotenv()
BOT_TOKEN = os.getenv('BOT_TOKEN')
if not BOT_TOKEN:
    logger.error("BOT_TOKEN не найден в переменных окружения!")
    exit(1)

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
    logger.info(f"User {message.from_user.id} started the bot")

# Middleware для логирования HTTP-запросов
@web.middleware
async def logger_middleware(request, handler):
    logger.info(f"HTTP {request.method} {request.path} from {request.remote}")
    return await handler(request)

# Обработчик корневого пути
async def handle_root(request):
    logger.info("Root endpoint accessed")
    return web.Response(text="I'm alive! Bot is running.")

# Обработчик для проверки здоровья
async def handle_health(request):
    return web.json_response({"status": "ok", "bot": "running"})

# Запуск веб-сервера
async def run_web_server():
    app = web.Application(middlewares=[logger_middleware])
    app.router.add_get('/', handle_root)
    app.router.add_get('/health', handle_health)
    runner = web.AppRunner(app)
    await runner.setup()
    port = int(os.environ.get('PORT', 10000))
    site = web.TCPSite(runner, '0.0.0.0', port)
    await site.start()
    logger.info(f"Web server started on port {port}")

# Запуск бота (поллинг)
async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    logger.info("Bot started polling")
    await dp.start_polling(bot)

# Обёртка для запуска обоих сервисов
async def main_wrapper():
    # Запускаем веб-сервер как фоновую задачу
    web_task = asyncio.create_task(run_web_server())
    # Запускаем бота
    try:
        await main()
    finally:
        # Если бот завершился, отменяем веб-сервер
        web_task.cancel()
        try:
            await web_task
        except asyncio.CancelledError:
            logger.info("Web server stopped")

if __name__ == "__main__":
    try:
        asyncio.run(main_wrapper())
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.exception(f"Unhandled exception: {e}")
