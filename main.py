import asyncio
import logging
from aiogram import Bot, Dispatcher
from config import BOT_TOKEN
from database import create_tables
from handlers import router
from scheduler import start_scheduler, scheduler

# Настройка логирования
logging.basicConfig(level=logging.INFO)




async def main():
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()

    create_tables()

    dp.include_router(router)
    start_scheduler(bot)
    await dp.start_polling(bot)


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print('\nBye!')
