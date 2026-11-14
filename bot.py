
import asyncio
import logging

from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder

from config import BOT_TOKEN, ADMIN_ID, BOT_NAME
from database import (
    init_db,
    add_user,
    use_request,
    get_stats,
    set_unlimited,
    set_limit,
    get_user
)
from search import format_results

logging.basicConfig(level=logging.INFO)

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()


def is_admin(user_id):
    return user_id == ADMIN_ID and ADMIN_ID != 0


def menu():
    kb = InlineKeyboardBuilder()
    kb.button(text="🔎 Поиск по нику", callback_data="search")
    kb.button(text="👤 Мой профиль", callback_data="profile")
    kb.adjust(1)
    return kb.as_markup()


@dp.message(Command("start"))
async def start(message: Message):
    add_user(message.from_user.id, message.from_user.username)

    if is_admin(message.from_user.id):
        set_unlimited(message.from_user.id)

    await message.answer(
        f"🕵️ <b>{BOT_NAME}</b>\n\n"
        "Добро пожаловать!\n"
        "Выбери действие:",
        reply_markup=menu()
    )


@dp.callback_query(F.data == "search")
async def search_button(call: CallbackQuery):
    await call.message.answer(
        "🔎 Отправь публичный username."
    )
    await call.answer()


@dp.callback_query(F.data == "profile")
async def profile_button(call: CallbackQuery):
    user = get_user(call.from_user.id)

    if not user:
        await call.answer("Сначала нажми /start", show_alert=True)
        return

    unlimited = user[5]
    used = user[3]
    limit = user[6]

    status = "♾️ Безлимит" if unlimited else f"{used}/{limit}"

    await call.message.answer(
        f"👤 ID: <code>{call.from_user.id}</code>\n"
        f"📊 Запросы сегодня: {status}"
    )
    await call.answer()


@dp.message(F.text.startswith("@"))
async def username_search(message: Message):
    user_id = message.from_user.id

    add_user(user_id, message.from_user.username)

    if not use_request(user_id):
        await message.answer("⛔ Дневной лимит исчерпан.")
        return

    result = format_results(message.text)

    await message.answer(
        result or "❌ Некорректный username."
    )


@dp.message(Command("admin"))
async def admin(message: Message):
    if not is_admin(message.from_user.id):
        return

    users, requests = get_stats()

    await message.answer(
        "⚙️ <b>DEPANOV SHERLOCK</b>\n\n"
        f"👥 Пользователей: {users}\n"
        f"🔎 Всего запросов: {requests}\n\n"
        "Команды:\n"
        "/unlimited ID\n"
        "/limit ID ЧИСЛО"
    )


@dp.message(Command("unlimited"))
async def unlimited_command(message: Message):
    if not is_admin(message.from_user.id):
        return

    parts = message.text.split()

    if len(parts) != 2 or not parts[1].isdigit():
        await message.answer("Использование: /unlimited ID")
        return

    user_id = int(parts[1])
    add_user(user_id)
    set_unlimited(user_id, True)

    await message.answer(
        f"♾️ Безлимит выдан пользователю {user_id}."
    )


@dp.message(Command("limit"))
async def limit_command(message: Message):
    if not is_admin(message.from_user.id):
        return

    parts = message.text.split()

    if len(parts) != 3 or not all(
        part.isdigit() for part in parts[1:]
    ):
        await message.answer("Использование: /limit ID ЧИСЛО")
        return

    user_id = int(parts[1])
    amount = int(parts[2])

    if amount > 10000:
        await message.answer("Максимум 10000.")
        return

    add_user(user_id)
    set_limit(user_id, amount)

    await message.answer("✅ Лимит успешно установлен.")


async def main():
    if not BOT_TOKEN:
        raise RuntimeError("BOT_TOKEN не задан!")

    init_db()
    print("DEPANOV SHERLOCK запущен!")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
    
