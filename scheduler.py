from apscheduler.schedulers.asyncio import AsyncIOScheduler
from aiogram import Bot
from database import get_all_birthdays
from datetime import datetime, timedelta
import logging

scheduler = AsyncIOScheduler()


async def check_birthdays(bot: Bot):
    today = datetime.now().date()
    tomorrow = today + timedelta(days=1)

    birthdays = get_all_birthdays()

    for bd in birthdays:
        # Извлекаем дату рождения из результата (она в формате datetime.date)
        birthdate = bd['birthdate']
        # Заменяем год на текущий для сравнения
        next_birthday = birthdate.replace(year=today.year)

        # Если в этом году день рождения уже прошел, берем следующий год
        if next_birthday < today:
            next_birthday = next_birthday.replace(year=today.year + 1)

        # Проверяем, завтра ли день рождения
        if next_birthday == tomorrow:
            message = (
                f"Завтра день рождения у {bd['full_name']}!\n"
                f"Контакт: {bd['contact_info']}\n"
                "Не забудьте поздравить!"
            )
            await bot.send_message(bd['user_id'], message)

        # Проверяем, сегодня ли день рождения
        elif next_birthday == today:
            message = (
                f"Сегодня день рождения у {bd['full_name']}!\n"
                f"Контакт: {bd['contact_info']}\n"
                "Поздравьте прямо сейчас!"
            )
            await bot.send_message(bd['user_id'], message)


def start_scheduler(bot: Bot):
    # Проверяем каждый день в 9:00 утра
    scheduler.add_job(check_birthdays, 'cron', hour=21, minute=51, args=[bot])
    scheduler.start()
    logging.info("Scheduler started")
