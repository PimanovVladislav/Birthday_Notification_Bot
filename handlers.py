import re

from aiogram import Bot, types
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.dispatcher.router import Router
from aiogram.filters import Command, CommandStart  # Импортируем фильтры команд

# Импортируйте ваши функции из базы данных
from database import add_user, add_birthday, get_birthdays_by_user, delete_birthday

# Создаем маршрутизатор
router = Router()

# Состояния для FSM
class BirthdayForm(StatesGroup):
    full_name = State()
    birthdate = State()
    contact_info = State()

# Обработчик команды /start с использованием CommandStart
@router.message(CommandStart())
async def start_command(message: types.Message, state: FSMContext):
    user = message.from_user
    add_user(user.id, user.username, user.first_name, user.last_name)
    await message.answer(
        f"Привет, {user.first_name}! Я бот для напоминания о днях рождения.\n"
        "Используй команды:\n"
        "/add_birthday - добавить день рождения\n"
        "/list_birthdays - посмотреть свои записи\n"
        "/delete_birthday - удалить запись"
    )

# Начало добавления дня рождения
@router.message(Command(commands=["add_birthday"]))
async def add_birthday_start(message: types.Message, state: FSMContext):
    await state.set_state(BirthdayForm.full_name)
    await message.answer("Введите ФИО именинника:")

# Обработка ФИО
@router.message(BirthdayForm.full_name)
async def process_full_name(message: types.Message, state: FSMContext):
    await state.update_data(full_name=message.text)
    await state.set_state(BirthdayForm.birthdate)
    await message.answer("Введите дату рождения в формате ГГГГ-ММ-ДД:")

# Обработка даты рождения
@router.message(BirthdayForm.birthdate)
async def process_birthdate(message: types.Message, state: FSMContext):
    if not re.match(r'\d{4}-\d{2}-\d{2}', message.text):
        await message.answer("Неверный формат. Введите дату в формате ГГГГ-ММ-ДД:")
        return

    await state.update_data(birthdate=message.text)
    await state.set_state(BirthdayForm.contact_info)
    await message.answer("Введите контакт для связи (телефон, Telegram и т.д.):")

# Обработка контакта и сохранение данных
@router.message(BirthdayForm.contact_info)
async def process_contact_info(message: types.Message, state: FSMContext):
    data = await state.get_data()
    full_name = data['full_name']
    birthdate = data['birthdate']
    contact_info = message.text

    user_id = message.from_user.id

    # Сохраняем в базу данных
    add_birthday(user_id, full_name, birthdate, contact_info)

    await message.answer(f"День рождения {full_name} добавлен!")
    await state.clear()

# Просмотр списка дней рождений с использованием команды /list_birthdays
@router.message(Command(commands=["list_birthdays"]))
async def list_birthdays(message: types.Message):
    user_id = message.from_user.id
    birthdays = get_birthdays_by_user(user_id)

    if not birthdays:
        await message.answer("У вас пока нет сохраненных дней рождений.")
        return

    response = "Ваши дни рождения:\n\n"
    for bd in birthdays:
        response += (
            f"🔹 {bd['full_name']}\n"
            f"Дата: {bd['birthdate']}\n"
            f"Контакт: {bd['contact_info']}\n"
            f"ID: {bd['id']}\n\n"
        )

    await message.answer(response)

# Удаление дня рождения (начало) с использованием команды /delete_birthday
class DeleteBirthday(StatesGroup):
    birthday_id = State()

@router.message(Command(commands=["delete_birthday"]))
async def delete_birthday_start(message: types.Message, state: FSMContext):
    await state.set_state(DeleteBirthday.birthday_id)
    await message.answer("Введите ID дня рождения для удаления:")

@router.message(DeleteBirthday.birthday_id)
async def process_birthday_id(message: types.Message, state: FSMContext):
    try:
        birthday_id = int(message.text)
    except ValueError:
        await message.answer("Пожалуйста, введите число (ID).")
        return

    user_id = message.from_user.id
    birthdays = get_birthdays_by_user(user_id)
    ids = [bd['id'] for bd in birthdays]

    if birthday_id not in ids:
        await message.answer("У вас нет записи с таким ID.")
        await state.clear()
        return

    delete_birthday(birthday_id)
    await message.answer("Запись удалена!")
    await state.clear()